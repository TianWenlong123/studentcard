# -*- coding: utf-8 -*-

# Card operate commands
# Write:
# |0--3|4--7|89|ab|12--------23|24----------------------------55|
# |WRTE|BlkA|SZ|TA|FFF--KEY--FF|----DATA------------DATA--------|
# |READ|BlkA|SZ|TA|FFF--KEY--FF|
# |CLSE|
# 
# note:
# BlkA: block address
# SZ: size
# TA: trailer block address
# 

import Queue

BLOCK_SIZE = 16

ID_SIZE           = 4
MAX_RECORD        = 5

ID_BLOCK          = 4
BEGIN_TIME_BLOCK  = 5
END_TIME_BLOCK    = 6
MONEY_BLOCK       = 8
MONEY_BLOCK_BAK   = 12
RECORD_INFO_BLOCK = 16
VALID_BLOCK       = 40
PASSWD_BLOCK      = 44

keys = ['FF' * 6 for i in range(16)]

class Card:
    def __init__(self):
        self.id            = '2014011111'
        self.id_len        = 10
        self.begin_time    = '20170827'
        self.end_time      = '20180827'
        self.time_len      = 8
        self.money         = 0 # cent
        self.consume_head  = 0
        self.consume_num   = 0
        self.consume_queue = Queue.Queue(maxsize = 5)
        self.passwd        = "******"
        self.passwd_len    = 6

    def getInfo(self, filename):
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

    def writeCmd(self, blockAddr, size, data):
        'construct a write command'
        # |WRTE|BlkA|SZ|TA|FFF--KEY--FF|----DATA------------DATA--------|
        # 'WRTE00041607FFFFFFFFFFFF11223344000000000000000000000000'
        cmd = 'WRTE%04d%02d%02d%s' % (blockAddr, size, blockAddr/4*4+3, keys[blockAddr/4])
        cmd += data
        return cmd

    def readCmd(self, blockAddr, size):
        'construct a read command'
        cmd = 'READ%04d%02d%02d%s' % (blockAddr, size, blockAddr/4*4+3, keys[blockAddr/4])
        return cmd

    def updateIDCmd(self, id=None):
        if id != None:
            self.id = id
        id = int(self.id)
        data = hex(id)[2:] + '00' * (BLOCK_SIZE - ID_SIZE)
        return self.writeCmd(ID_BLOCK, BLOCK_SIZE, data)

    def updateBeginTimeCmd(self, begin_time=None):
        if begin_time != None:
            self.begin_time = begin_time
        
        year  = int(self.begin_time[0: 4])
        month = int(self.begin_time[5: 6])
        day   = int(self.begin_time[7: 8])
        data = '%08x%04x%04x%16s' % (year, month, day, '0' * 16)
        return self.writeCmd(BEGIN_TIME_BLOCK, BLOCK_SIZE, data)

    def readEndTimeCmd(self):
        return self.readCmd(END_TIME_BLOCK, BLOCK_SIZE)

    def updateEndTimeCmd(self, end_time=None):
        if end_time != None:
            self.end_time = end_time
        
        year  = int(self.end_time[0: 4])
        month = int(self.end_time[5: 6])
        day   = int(self.end_time[7: 8])
        data = '%08x%04x%04x%16s' % (year, month, day, '0' * 16)
        return self.writeCmd(END_TIME_BLOCK, BLOCK_SIZE, data)

    def readPasswdCmd(self):
        return self.readCmd(PASSWD_BLOCK, BLOCK_SIZE)

    def updatePasswdCmd(self, passwd=None):
        if passwd != None:
            self.passwd = passwd
        data = self.passwd.encode('hex')
        assert len(data) == 12
        data += '0' * (BLOCK_SIZE * 2 - 12)
        return self.writeCmd(PASSWD_BLOCK, BLOCK_SIZE, data)

    def readMoneyCmd(self):
        return self.readCmd(MONEY_BLOCK, BLOCK_SIZE)

    def updateMoneyCmd(self, money):
        'money min value is 1 cent, so multiply by 100 to convert to int operation'
        self.money = money
        cent = int(round(self.money, 2) * 100)
        data = ('%08X' % cent) + '00' * (BLOCK_SIZE - 4)
        return self.writeCmd(MONEY_BLOCK, BLOCK_SIZE, data)

    def newCardInitCommands(self):
        cmds = []
        # write student id number
        cmd = self.updateIDCmd()
        cmds.append(cmd)

        # write begin time and end time
        cmd = self.updateBeginTimeCmd()
        cmds.append(cmd)
        cmd = self.updateEndTimeCmd()
        cmds.append(cmd)

        # write passwd
        cmd = self.updatePasswdCmd('011423')
        cmds.append(cmd)

        cmd = self.updateMoneyCmd(0.0)
        cmds.append(cmd)

        return cmds

    def updateTimeCommands(self,begint,endt):
        cmds = []
        # write begin time and end time
        cmd = self.updateBeginTimeCmd(begint)
        cmds.append(cmd)
        cmd = self.updateEndTimeCmd(endt)
        cmds.append(cmd)

        return cmds