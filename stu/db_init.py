# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect('allow.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE allow
             (id int, name text)''')
# (id int, name text, sex text, department text, begin_time date, end_time date, money real)

# Insert a row of data
c.execute("INSERT INTO allow VALUES (2014011423, '陈雅正')")

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
