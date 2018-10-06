# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import sys
import json

def grafico(parsed_response):
    parsed_size = len(parsed_response)
    d = {}

    for i in range(0,parsed_size):    
        categories = parsed_response[i]['categories']
        for cat in categories:
            if cat in d:
                d[cat] += 1
            else:
                d[cat] = 1

    labels = list(d.keys())
    sizes  = list(d.values())

    plt.pie(sizes,labels=labels,autopct='%1.1f%%')
    plt.axis('equal')
    plt.savefig('/path/fig.png')#path to fig.
    plt.clf()#overwrite graph.


# This function prints out the response from an endpoint in a consistent way.
def pretty_print_response(response):
    print(response.code)
    parsed_response = json.loads(response.read().decode('utf-8'))
    print(type(parsed_response))
    print(json.dumps(parsed_response, indent=4))
    grafico(parsed_response)
    return len(parsed_response)


# this function prints out information about a request that will be made
# to the API.
def pretty_print_request(client, path, method, headers=None):
    ip = client.get_server_ip()
    base_uri = client.get_base_uri()

    header_copy = client.get_headers().copy()
    if headers is not None:
        header_copy.update(headers)

    url = 'https://' + ip + base_uri + path
    print('Sending a ' + method + ' request to:')
    print(url)
    print('with these headers:')
    print(header_copy)
    print()


# this function sets up data to be used by a sample. If the data already exists
# it prefers to use the existing data.
def data_setup(client, path, method, params=[]):
    response = client.call_api(path, method, params=params)
    if (response.code == 409):
        print("Data already exists, using existing data")
    elif(response.code >= 400):
        print("An error occurred setting up sample data:")
        pretty_print_response(response)
        sys.exit(1)
    return response