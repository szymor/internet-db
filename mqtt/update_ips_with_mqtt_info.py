#!/bin/env python3

import ipaddress as ia
import sqlite3
import sys
import os
import time

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print(f"Connected with result code {rc}.")
	client.disconnect()
	ip = int(userdata)
	cur.execute(f"update mqtt set plain={rc} where ip={ip};")
	con.commit()

def on_connect_fail(client, userdata):
	print("Not connected.")
	ip = int(userdata)
	cur.execute(f"update mqtt set plain=-3 where ip={ip};")
	con.commit()

def check_single_ip(cur, ip):
	mqttc = mqtt.Client(userdata=ip)
	mqttc.on_connect = on_connect
	try:
		mqttc.connect(str(ip), 1883)
	except:
		print("Unexpected connection error.")
		cur.execute(f"update mqtt set plain=-1 where ip={int(ip)};")
		con.commit()
		return
	mqttc.loop(5.0)
	print("Timeout error.")
	cur.execute(f"update mqtt set plain=-2 where ip={int(ip)};")
	con.commit()
	mqttc.disconnect()

if len(sys.argv) != 2:
	print("Syntax: {} <db file>".format(sys.argv[0]))
	exit(1)

if not os.path.exists(sys.argv[1]):
	print("Database {} does not exist.".format(sys.argv[1]))
	exit(2)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

# modify the SQL statement if you want to update other records
res = cur.execute("select ip from mqtt where plain is null;")
for r in res.fetchall():
	ip = ia.ip_address(r[0])
	print(ip, "...", sep='')
	check_single_ip(cur, ip)

print("Update finished.")
con.close()
