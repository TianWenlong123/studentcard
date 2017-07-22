# -*- coding: utf-8 -*-

import sqlite3
from db_init import *

db_allow = sqlite3.connect( ALLOW_DB_NAME )
db_student = sqlite3.connect( STUDENTS_DB_NAME )

c_allow = db_allow.cursor()
c_stu   = db_student.cursor()

def query_allow(id):
    c_allow.execute('SELECT * FROM allow WHERE id=?', (str(id),))
    if len(c_allow.fetchall()) > 0:
        return True
    else:
        return False

def exist_student(id):
    c_stu.execute('SELECT * FROM info WHERE id=?', (str(id),))
    if len(c_stu.fetchall()) > 0:
        return True
    else:
        return False

def insert_student(student):
    c_stu.execute('INSERT into info values (?, ?, ?, ?, ?, ?, ?)', student)
    db_student.commit()

