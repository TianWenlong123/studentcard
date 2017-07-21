# -*- coding: utf-8 -*-

import sqlite3

db_allow = sqlite3.connect('allow.db')

c_allow = db_allow.cursor()

id = 2014011423

c_allow.execute('SELECT * FROM allow WHERE id=?', (str(id),))

print c_allow.fetchall()