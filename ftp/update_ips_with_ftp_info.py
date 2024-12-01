#!/bin/env python3

import ipaddress as ia
import datetime
import sqlite3
import time
import sys
import os

from ftplib import FTP
from ftplib import error_perm

def opt_quit(ftp):
    try:
        ftp.quit()
    except:
        print("Quit error.")

list = ""
def list_callback(line):
	global list
	list += line + "\n"

def check_single_ip(cur, ip):
	i = int(ip)
	dt = datetime.datetime.now()
	t = time.mktime(dt.timetuple())
	ti = int(t)
	try:
		ftp = FTP(str(ip), timeout=5)
	except:
		cur.execute(f"update ftp set anon=-1, timestamp={ti} where ip={i};")
		print("Connection failed unexpectedly.")
		return
	try:
		ret = ftp.login()
	except error_perm:
		cur.execute(f"update ftp set anon=0, timestamp={ti}, welcome=? where ip={i};", (ftp.welcome, ))
		print("No anonymous login.")
		opt_quit(ftp)
		return
	except:
		cur.execute(f"update ftp set anon=-2, timestamp={ti}, welcome=? where ip={i};", (ftp.welcome, ))
		print("Login failed unexpectedly.")
		opt_quit(ftp)
		return
	# positive response for anonymous credentials
	if ret[0] == '2':
		global list
		list = ""
		try:
			ftp.retrlines("LIST", callback=list_callback)
		except:
			cur.execute(f"update ftp set anon=1, timestamp={ti}, welcome=?, listing='<error>' where ip={i};", (ftp.welcome, ))
			print("Cannot retrieve root directory listing.")
			opt_quit(ftp)
			return
		cur.execute(f"update ftp set anon=1, timestamp={ti}, welcome=?, listing=? where ip={i};", (ftp.welcome, list))
		print("Anonymous access available.")
	else:
		cur.execute(f"update ftp set anon=0, timestamp={ti}, welcome=?, listing='<rsp_error>' where ip={i};", (ftp.welcome, ))
		print("Unexpected response.")
	opt_quit(ftp)

if len(sys.argv) < 2:
	print("Syntax: {} <db file>".format(sys.argv[0]))
	exit(1)

if not os.path.exists(sys.argv[1]):
	print("Database {} does not exist.".format(sys.argv[1]))
	exit(2)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

resstr = "select ip from ftp where anon is null;"
if len(sys.argv) == 4:
	resstr = f"select ip from (select ip, row_number() over() as rn from ftp where anon is null) where rn >= {sys.argv[2]} and rn <= {sys.argv[3]};"

print(resstr)
res = cur.execute(resstr)
for r in res.fetchall():
	ip = ia.ip_address(r[0])
	print(ip, "...", sep='')
	check_single_ip(cur, ip)
	con.commit()

print("Update finished.")
con.close()
