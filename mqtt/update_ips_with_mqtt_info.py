#!/bin/env python3

import ipaddress as ia
import sqlite3
import sys
import os
import time
import datetime

import paho.mqtt.client as mqtt

def get_timestamp():
	dt = datetime.datetime.now()
	t = time.mktime(dt.timetuple())
	ti = int(t)
	return ti

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print(f"Connected with result code {rc}.")
	client.disconnect()
	ip = int(userdata)
	ti = get_timestamp()
	cur.execute(f"update mqtt set rc={rc}, timestamp={ti} where ip={ip};")
	con.commit()

def on_connect_fail(client, userdata):
	print("Not connected.")
	ip = int(userdata)
	ti = get_timestamp()
	cur.execute(f"update mqtt set rc=-3, timestamp={ti} where ip={ip};")
	con.commit()

def check_single_ip(cur, ip):
	mqttc = mqtt.Client(userdata=ip)
	mqttc.on_connect = on_connect
	try:
		mqttc.connect(str(ip), 1883)
	except:
		print("Unexpected connection error.")
		ti = get_timestamp()
		cur.execute(f"update mqtt set rc=-1, timestamp={ti} where ip={int(ip)};")
		con.commit()
		return
	try:
		mqttc.loop(1.0)
	except TimeoutError:
		pass
	ti = get_timestamp()
	cur.execute(f"update mqtt set rc=-2, timestamp={ti} where ip={int(ip)} and rc is null;")
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

res = cur.execute("select ip from mqtt where rc is null;")
for r in res.fetchall():
	ip = ia.ip_address(r[0])
	print(ip, "...", sep='')
	check_single_ip(cur, ip)

print("Update finished.")
con.close()
