# -*- coding: utf-8 -*-
import Queue
import serial

MAC_PORT = "/dev/cu.usbmodem1411"

class Ser(object):
    def __init__(self):
        #打开端口
        #self.port = serial.Serial(port='COM3', baudrate=9600, bytesize=8, parity='E', stopbits=1, timeout=5)
        self.port = serial.Serial(port='COM3', baudrate=9600, bytesize=8, timeout=5)

    def send_cmd(self,cmd):
        self.port.write(cmd)
        response = self.port.readall()
        return response

    def fillcmd(self,cmd):
        length = len(cmd)
        if length<54 :
            for i in range(length,54):
                cmd += '0'
        return cmd

class NewCard:
    def __init__(self):
        self.id = '2014011111'
        self.id_len = 10
        self.begin_time = '20170827'
        self.end_time = '20180827'
        self.time_len = 8
        self.money = 0
        self.consume_head = 0
        self.consume_num = 0
        self.consume_queue = Queue.Queue(maxsize=5)
        self.passwd = "******"
        self.passwd_len = 6

    def getInfo(self,filename):
        file = open(filename)
        #考虑增加验证
        index = 0

        #id
        line = file.readline()
        index = line.index('=')+ 2
        self.id = line[index:index+self.id_len]

        #time begin and end
        line = file.readline()
        index = line.index('=') + 2
        self.begin_time = line[index:index+self.time_len]
        line = file.readline()
        index = line.index('=') + 2
        self.end_time = line[index:index + self.time_len]

        #passwd
        line = file.readline()
        index = line.index('=') + 2
        self.passwd = line[index:index + self.passwd_len]
        return 1

    def writeInfo(self,ser):
        #写ID 54
        cmd = 'WRTE'+'0004'+'16'+'FFFFFFFFFFFF'+ self.id.encode('utf8').encode('hex')
        cmd = ser.fillcmd(cmd)
        print cmd
        response = ser.send_cmd(cmd)
        print response
        #判断response是否正确...

        #写起始时间和终止时间
        cmd = 'WRTE'+'0005'+'16'+'FFFFFFFFFFFF'+ self.begin_time.encode('utf8').encode('hex')
        cmd = ser.fillcmd(cmd)
        response = ser.send_cmd(cmd)
        print response
        cmd = 'WRTE' + '0006' + '16' + 'FFFFFFFFFFFF' + self.end_time.encode('utf8').encode('hex')
        cmd = ser.fillcmd(cmd)
        response = ser.send_cmd(cmd)
        print response
        #写passwd
        response = ser.send_cmd(self.passwd)
        cmd = 'WRTE' + '0044' + '16' + 'FFFFFFFFFFFF' + self.passwd.encode('utf8').encode('hex')
        cmd = ser.fillcmd(cmd)
        response = ser.send_cmd(cmd)
        print response






