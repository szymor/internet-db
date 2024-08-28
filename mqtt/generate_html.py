#!/bin/env python3

import ipaddress as ia
import sqlite3
import sys
import os

from datetime import datetime

header_template = """
<!DOCTYPE HTML>
<html lang="en-US">
<head>
<meta charset="utf-8">
<title>Not a Miyoo site - {title}</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<h1 style="text-align: center;">{title}</h1>
<hr>
<nav style="text-align: center;">
{left} |
<a href="/">Back to Home</a> |
{right}
</nav>
<hr>
"""

footer_template = """
<hr>
<footer>
<p style="text-align: center;">by vamastah, generated on {dt}</p>
</footer>
</body>
</html>
"""

if len(sys.argv) != 3:
	print("Syntax: {} <db file> <out dir>".format(sys.argv[0]))
	exit(1)

if not os.path.exists(sys.argv[1]):
	print("Database {} does not exist.".format(sys.argv[1]))
	exit(2)

con = sqlite3.connect(sys.argv[1])
cur = con.cursor()

res = cur.execute("select * from mqtt where plain >= 0 order by ip;")
records = res.fetchall()

os.mkdir(sys.argv[2])

dt = datetime.now().ctime()

pagesize = 250
pages = [records[i*pagesize : (i+1)*pagesize] for i in range((len(records) + pagesize - 1) // pagesize)]
ep = enumerate(pages)
for p in ep:
	with open("{}/mqtt_{}.html".format(sys.argv[2], p[0]), "w") as f:
		title = "MQTT Server List {}/{}".format(p[0] + 1, len(pages))

		if p[0] > 0:
			left = '<a href="mqtt_{}.html">&lt;&lt;</a>'.format(p[0] - 1)
		else:
			left = '&lt;&lt;'
		if p[0] < len(pages) - 1:
			right = '<a href="mqtt_{}.html">&gt;&gt;</a>'.format(p[0] + 1)
		else:
			right = '&gt;&gt;'

		f.write(header_template.format(title=title, left=left, right=right))

		f.write('<table>')
		f.write('<tr><th>No.</th><th>IP address</th><th>Plain text (port 1883)</th></tr>')
		for e in enumerate(p[1]):
			ip = ia.ip_address(e[1][0])
			rc = e[1][1]
			rc_table = [
				"full access",
				"wrong protocol version",
				"identifier rejected",
				"server unavailable",
				"bad username or password",
				"not authorized"
			]
			if rc >= 0 and rc <= 5:
				text = rc_table[rc]
			else:
				text = "???"
			style = ""
			if rc == 0:
				style = ' style="background-color: #c0ffc0;"'
			elif rc == 4 or rc == 5:
				style = ' style="background-color: #ffc0c0;"'
			f.write('<tr><td>{}</td><td>{}</td><td{}>{}</td></tr>'.format(
				e[0] + 1 + p[0] * pagesize,
				str(ip),
				style,
				text))
		f.write('</table>')

		f.write('<p style="text-align: center;">')
		epp = enumerate(pages)
		for pp in epp:
			if p[0] != pp[0]:
				f.write('<a href="mqtt_{}.html">{}</a> '.format(pp[0], pp[0] + 1))
			else:
				f.write('{} '.format(pp[0] + 1))
		f.write('</p>')

		f.write(footer_template.format(dt=dt))

con.close()
