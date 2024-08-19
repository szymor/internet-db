#!/bin/env python3

import ipaddress as ia
import sqlite3
import sys
import os

from datetime import datetime

if len(sys.argv) != 3:
	print("Syntax: {} <db file> <out dir>".format(sys.argv[0]))
	exit(1)

if not os.path.exists(sys.argv[1]):
	print("Database {} does not exist.".format(sys.argv[1]))
	exit(2)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

os.mkdir(sys.argv[2])

res = cur.execute("select * from ftp where anon >= 0 order by ip;")
records = res.fetchall()

dt = datetime.now().ctime()

pagesize = 250
pages = [records[i*pagesize : (i+1)*pagesize] for i in range((len(records) + pagesize - 1) // pagesize)]
ep = enumerate(pages)
for p in ep:
	with open("{}/ftp_{}.html".format(sys.argv[2], p[0]), "w") as f:
		f.write('<!DOCTYPE html><html lang="en-US"><head><title>FTP Server List {}/{}</title><meta charset="utf-8"><link rel="stylesheet" href="style.css"></head>'.format(p[0] + 1, len(pages)))
		f.write('<body>')

		if p[0] > 0:
			left = '<a href="ftp_{}.html">&lt;&lt;</a>'.format(p[0] - 1)
		else:
			left = '&lt;&lt;'
		if p[0] < len(pages) - 1:
			right = '<a href="ftp_{}.html">&gt;&gt;</a>'.format(p[0] + 1)
		else:
			right = '&gt;&gt;'

		f.write('<table><caption>{} FTP Server List, page {}/{} {}</caption>'.format(left, p[0] + 1, len(pages), right))
		f.write('<tr><th>No.</th><th>IP address</th><th>Anonymous access</th><th>Root directory listing</th></tr>')
		for e in enumerate(p[1]):
			ip = ia.ip_address(e[1][0])
			anon = e[1][1]
			f.write('<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="listing/listing_{}.txt">TXT</a></td></tr>'.format(
				e[0] + 1 + p[0] * pagesize,
				str(ip),
				"yes" if anon == 1 else "no",
				str(ip)))
		f.write('</table>')

		f.write('<p>')
		epp = enumerate(pages)
		for pp in epp:
			if p[0] != pp[0]:
				f.write('<a href="ftp_{}.html">{}</a> '.format(pp[0], pp[0] + 1))
			else:
				f.write('{} '.format(pp[0] + 1))
		f.write('</p>')

		f.write('<footer><p>Generated at {}</p></footer>'.format(dt))

		f.write('</body></html>')

con.close()
