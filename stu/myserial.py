# -*- coding: utf-8 -*-
import serial

MAC_PORT = "/dev/cu.usbmodem1411"

class MySerial(object):
    def __init__(self, portname=None, timeout=None, baudrate=9600):
        #self.port = serial.Serial(port='COM3', baudrate=9600, bytesize=8, parity='E', stopbits=1, timeout=5)
        if timeout == None:
            timeout = 1.2
        if portname == None:
            self.port = serial.Serial(port='COM3', baudrate=baudrate, bytesize=8, timeout=timeout)
        else:
            self.port = serial.Serial(port=portname, baudrate=baudrate, timeout=timeout)

    def sendCmd(self, cmd):
        cmd = cmd.upper()
        #print 'Send:',cmd
        self.port.write(cmd)
        response = self.port.readall()
        return response

    def isOpen(self):
        return self.port.isOpen()
