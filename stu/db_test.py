# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('allow.db')

c = conn.cursor()

id = 2014011423

c.execute('SELECT * FROM allow WHERE id=?', (str(id),))

print c.fetchall()