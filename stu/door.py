# -*- coding: utf-8 -*-

import serial
from myserial import MySerial, MAC_PORT
import sqlite3

myserial = MySerial(MAC_PORT, timeout=1)

conn = sqlite3.connect('allow.db')
cursor = conn.cursor()

def main():
    myserial.port.readall()
    while myserial.isOpen():
        n = myserial.port.inWaiting()
        if n:
            cmd = myserial.port.readall()
            cmds = cmd.split('\n')
            for cmd in cmds:
                if cmd[0:4] == "REQU":
                    istr = '0x'+cmd[4:12]
                    print istr
                    id = int(istr, 16)
                    print 'ID:', id, 'request to pass'
                    response = myserial.sendCmd('PASS')
                    if response[0:3] == 'LOG':
                        print 'log:', response[3:]
                    else:
                        print response
                elif cmd[0:4] == 'CLSE':
                    break
                elif cmd[0:3] == 'LOG':
                    print 'log:', cmd[3:]
                else:
                    print cmd
        else:
            continue
    print 'Serial closed. Exit.'
    

if __name__ == '__main__':
    main()
