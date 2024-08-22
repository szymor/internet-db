#!/bin/env python3

import ipaddress as ia
import sqlite3
import sys
import os

if len(sys.argv) != 3:
	print("Syntax: {} <db file> <ip list file>".format(sys.argv[0]))
	exit(1)

if not os.path.exists(sys.argv[1]):
	print("Database {} does not exist.".format(sys.argv[1]))
	exit(2)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

count = 0
with open(sys.argv[2]) as f:
	for line in f:
		line = line[:-1] # remove eol character
		ip = ia.ip_address(line)
		try:
			cur.execute("insert into mqtt(ip) values({});".format(int(ip)))
			count = count + 1
		except sqlite3.IntegrityError:
			print("Duplicate IP: {}.".format(ip))

con.commit()

print("Inserted", count, "entries.")

con.close()
