# -*- coding: utf-8 -*-

import sqlite3
from db_init import *

db_allow = sqlite3.connect( ALLOW_DB_NAME )

c_allow = db_allow.cursor()

def query_allow(id):
    c_allow.execute('SELECT * FROM allow WHERE id=?', (str(id),))
    if len(c_allow.fetchall()) > 0:
        return True
    else:
        return False

