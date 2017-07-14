# -*- coding: utf-8 -*-
import serial

MAC_PORT = "/dev/cu.usbmodem1411"

class MySerial(object):
    def __init__(self, portname=None, baudrate=9600):
        #self.port = serial.Serial(port='COM3', baudrate=9600, bytesize=8, parity='E', stopbits=1, timeout=5)
        if portname == None:
            self.port = serial.Serial(port='COM3', baudrate=baudrate, bytesize=8, timeout=1)
        else:
            self.port = serial.Serial(port=portname, baudrate=baudrate)

    def sendCmd(self, cmd):
        print 'Send:',cmd
        self.port.write(cmd)
        #n = self.port.inWaiting()
        #response = self.port.read(n)
        response = self.port.readall()
        print 'Recv:', response
        return response

    def isOpen(self):
        return self.port.isOpen()
