#!/bin/env python3

import sqlite3
import sys

if len(sys.argv) != 2:
	print("Syntax: {} <db file>".format(sys.argv[0]))
	exit(1)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

cur.execute("create table mqtt(ip primary key, rc, timestamp, comments text);")

con.close()
