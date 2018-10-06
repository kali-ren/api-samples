#!/usr/bin/python3

import mysql.connector

mydb = mysql.connector.connect(
	host   = "localhost",
	user   = "YOUR_USE",
	passwd = "YOUR_PASS",
	database = "YOUR_DB"
)

def fetch(id_telegram):
	mycursor = mydb.cursor()
	sql = "select * from users where id_telegram="+id_telegram#try me :)
	try:
		mycursor.execute(sql)
		myresult = mycursor.fetchone()
		return myresult[0]
	except Exception as e:
		return(e)

def get_domain_id(id_telegram):
    mycursor = mydb.cursor()
    sql = "select domain_id from users where id_telegram="+id_telegram#try me :)
    try:
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        return myresult[0]    	
    except Exception as e:
        return(e)

