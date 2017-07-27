# -*- coding: utf-8 -*-

import os
import sqlite3

ALLOW_DB_NAME = 'allow.db'
STUDENTS_DB_NAME = 'students.db'

ALLOW_TABLE_NAME = 'allow'
STUDENTS_TABLE_NAME = 'info'

ALLOW_START_ID = 2014011300
ALLOW_END_ID = 2014011500

def init_allow():    
    db_allow = sqlite3.connect('allow.db')
    c_allow = db_allow.cursor()

    # Create table
    c_allow.execute('''CREATE TABLE allow
                (id int)''')

    # Insert data
    for id in range(ALLOW_START_ID, ALLOW_END_ID):
        c_allow.execute("INSERT INTO allow VALUES (%d)" % id)

    # Save (commit) the changes
    db_allow.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    db_allow.close()

def init_students():
    db_stu = sqlite3.connect('students.db')
    c_stu = db_stu.cursor()
    c_stu.execute('''CREATE TABLE info
        (id int,
        name text,
        sex text,
        department text,
        begin_time date,
        end_time date,
        money real)
        ''')
    db_stu.commit()
    db_stu.close()

def main():
    if not os.path.exists(ALLOW_DB_NAME):
        init_allow()
    else:
        print ALLOW_DB_NAME, 'already exists.'
    
    if not os.path.exists(STUDENTS_DB_NAME):
        init_students()
    else:
        print STUDENTS_DB_NAME, 'already exists.'
    

if __name__ == '__main__':
    main()
