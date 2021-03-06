#!/usr/bin/env python3
# This is the typical way to query to the ArielAPI, and receive
# the results. ArielAPI searches are asynchronous.
# Endpoints are used to determine if the search has completed.
# After determining that the search is complete, call
# GET /searches/{search_id}/results for search results.
# The results are saved through the POST /searches/{search_id} endpoint.
# script modified to fetch events of interest. 

import sys
import os
import importlib
sys.path.append(os.path.realpath('../modules'))
import json
from arielapiclient import APIClient
from datetime import datetime,timedelta,date

client_module   = importlib.import_module('RestApiClient')
SampleUtilities = importlib.import_module('SampleUtilities')

# This function is used for set initial time for search offenses in milliseconds.
# The parameter day is used as a time range factor. How many days from now the search start.
# today format: 'dd/mm/yyyy'
def get_date(day):
    today = date.today().strftime("%d/%m/%Y")
    today_mili = int( datetime.strptime(today,"%d/%m/%Y").strftime('%s') )*1000

    a_time_ago = ( datetime.strptime(today,"%d/%m/%Y") - timedelta(days=day) ).strftime('%d/%m/%Y')
    a_time_ago_mili = int(datetime.strptime(a_time_ago,'%d/%m/%Y').strftime('%s') )*1000
    
    return str(a_time_ago_mili)

# This function return the number of offenses queried by the specified user.
def get_offenses(day,client_id):
	# First we have to create our client
    # Update your version.
    client = client_module.RestApiClient(version='9.0')
   
    time_search = get_date(day)
    # Call the endpoint so that we can find how many OPEN offenses there are.
    response = client.call_api('siem/offenses?filter=status=OPEN', 'GET')
    num_of_open_offenses = len(json.loads(response.read().decode('utf-8')))

    # Copy the headers into our own variable
    range_header = client.get_headers().copy()

    # Set the starting point (indexing starts at 0)
    page_position = 0
    # and choose how many offenses you want to display at a time.
    offenses_per_page = 500

    # Looping here in order to repeatedly show 500 offenses at a time until we've
    # seen all of the OPEN offenses or exit character q is pressed
    input_string = ""
    fields = '''id,description,assigned_to,categories,category_count,policy_category_count,security_category_count,close_time,closing_user,closing_reason_id,credibility,relevance,severity,magnitude,destination_networks,source_network,device_count,\
event_count,flow_count,inactive,last_updated_time,local_destination_count,offense_source,offense_type,protected,follow_up,remote_destination_count,source_count,start_time,status,username_count,source_address_ids,local_destination_address_ids,domain_id'''

        # Change the value for Range in the header in the format item=x-y
    range_header['Range'] = ('items=' + str(page_position) + '-' +
                             str(page_position + offenses_per_page - 1))

    
    response = client.call_api(
            'siem/offenses?fields=' + fields + '&filter=start_time>'+time_search+'%20and%20domain_id='+client_id, 'GET',
            headers=range_header)
        # As usual, check the response code
    if (response.code != 200):
        print('Failed to retrieve list of offenses')
        SampleUtilities.pretty_print_response(response)
        sys.exit(1)

    # pretty_print_response return the number of offenses queried by the user.
    qtd_offenses = SampleUtilities.pretty_print_response(response)
    return '[+] quantidade de ofensas ultimo(s) {} dia(s): {} ofensa(s)'.format(day, qtd_offenses)

def evento_interesse():
    api_client = APIClient()
    # This is the AQL expression to send for the search. 
    query_expression = """SELECT domainid,LOGSOURCENAME(logsourceid) as "Log Source",\
SUM(eventcount) as "Event Count (SUM)", MIN(magnitude) as "Magnitude (MIN)",\
MIN(severity) as "Severity (MIN)" FROM events WHERE domainid=1 and severity > 6 and magnitude > 5 GROUP BY\
domainid ORDER BY "Event Count (SUM)" DESC LAST 1 DAYS"""

    # Use the query parameters above to call a method. This will call
    # POST /searches on the Ariel API. (look at arielapiclient for more
    # detail).  A response object is returned. It contains
    # successful or not successful search information.
    # The search_id corresponding to this search is contained in
    # the JSON object.
    response = api_client.create_search(query_expression)

    # Each response contains an HTTP response code.
    #  - Response codes in the 200 range indicate that your request succeeded.
    #  - Response codes in the 400 range indicate that your request failed due
    #    to incorrect input.
    #  - Response codes in the 500 range indicate that there was an error on
    #    the server side.
    #print(response.code)

    # The search is asynchronous, so the response will not be the results of
    # the search.

    # The 2 lines below parse the body of the response (a JSON object)
    # into a dictionary, so we can discern information, such as the search_id.
    response_json = json.loads(response.read().decode('utf-8'))

    # Prints the contents of the dictionary.
    #print(response_json)

    # Retrieves the search_id of the query from the dictionary.
    search_id = response_json['search_id']
    #print("search id: "+search_id)
    # This block of code calls GET /searches/{search_id} on the Ariel API
    # to determine if the search is complete. This block of code will repeat
    # until the status of the search is 'COMPLETE' or there is an error.
    response = api_client.get_search(search_id)
    error = False
    while (response_json['status'] != 'COMPLETED') and not error:
        if (response_json['status'] == 'EXECUTE') | \
                (response_json['status'] == 'SORTING') | \
                (response_json['status'] == 'WAIT'):
            response = api_client.get_search(search_id)
            response_json = json.loads(response.read().decode('utf-8'))
        else:
            print(response_json['status'])
            error = True

    # After the search is complete, call the GET /searches/{search_id} to
    # obtain the result of the search.
    # Depending on whether the "application/json" or "application/csv"
    # method is given, return search results will be in JSON form or CSV form.
    response = api_client.get_search_results(
        search_id, 'application/json', '1', '11')

    body = response.read().decode('utf-8')
    body_json = json.loads(body)

    # This is for pretty printing the JSON object.
    #print(json.dumps(body_json, indent=2, separators=(',', ':')))

    # This is the same call as before, but asks for a CSV object in return.
    response = api_client.get_search_results(search_id, "application/csv")
    evento_interesse_count = response.read().decode('utf-8').split(',')[2].split(':')[1].replace('"','')
    #print(evento_interesse_count)
    return float(evento_interesse_count)

def main():
    get_offenses()

if __name__ == "__main__":
    main()
