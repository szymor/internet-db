#!/bin/env python3

import ipaddress as ia
import sqlite3
import sys
import os

from ftplib import FTP

list = ""
def list_callback(line):
	global list
	list += line + "\n"

def check_single_ip(cur, ip):
	try:
		ftp = FTP(str(ip), timeout=30)
	except:
		cur.execute("update ftp set anon=-1 where ip={};".format(int(ip)))
		con.commit()
		print("Connection failed unexpectedly.")
		return
	try:
		ret = ftp.login()
	except:
		cur.execute("update ftp set anon=-2 where ip={};".format(int(ip)))
		con.commit()
		print("Login failed unexpectedly.")
		ftp.quit()
		return
	# positive response for anonymous credentials
	if ret[0] == '2':
		global list
		list = ""
		ftp.retrlines("LIST", callback=list_callback)
		with open("listing_" + str(ip) + ".txt", "w") as f:
			f.write(list)
		cur.execute("update ftp set anon=1 where ip={};".format(int(ip)))
		con.commit()
		print("Anonymous access available.")
	else:
		cur.execute("update ftp set anon=0 where ip={};".format(int(ip)))
		con.commit()
		print("No anonymous access.")
	ftp.quit()

if len(sys.argv) != 2:
	print("Syntax: {} <db file>".format(sys.argv[0]))
	exit(1)

if not os.path.exists(sys.argv[1]):
	print("Database {} does not exist.".format(sys.argv[1]))
	exit(2)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

# modify the SQL statement if you want to update other records
res = cur.execute("select ip from ftp where anon is null;")
for r in res.fetchall():
	ip = ia.ip_address(r[0])
	print(ip, "...", sep='')
	check_single_ip(cur, ip)

print("Update finished.")
con.close()
