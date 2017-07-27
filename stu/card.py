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
import datetime

BLOCK_SIZE = 16

ID_SIZE           = 4
MAX_RECORD        = 5

NAME_BLOCK        =9
DEPARTMENT_BLOCK  =10
ID_BLOCK          = 4
BEGIN_TIME_BLOCK  = 5
END_TIME_BLOCK    = 6
MONEY_BLOCK       = 8
MONEY_BLOCK_BAK   = 12
RECORD_INFO_HEAD_BLOCK = 16
RECORD_INFO_NUM_BLOCK = 17
RECORD_POS_SECTOR = 4

VALID_BLOCK       = 40
PASSWD_BLOCK      = 44

keys = ['FF' * 6 for i in range(16)]
#keys[MONEY_BLOCK_BAK/4] = 'DECFAB1D52B7'

class Card:
    def __init__(self):
        self.name          = '王小明'
        self.department    = '计算机'
        self.id            = '2014011111'
        self.id_len        = 10
        self.begin_time    = '20170827'
        self.end_time      = '20180827'
        self.time_len      = 8
        self.money         = 0 # cent
        self.money_bak     = 0
        self.consume_head  = 0
        self.consume_num   = 0
        self.consume_queue = Queue.Queue(maxsize = 5)
        self.passwd        = "******"
        self.passwd_len    = 6
        self.valid         = "nvalid"
        
    def getInfo(self, filename):
        file = open(filename)
        #考虑增加验证
        index = 0

        #name
        line = file.readline()
        index = line.index('=')+2
        self.name = line[index:len(line)-1]

        #department
        line = file.readline()
        index = line.index('=')+2
        self.department = line[index:len(line)-1]

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

    def closeCmd(self):
        return 'CLSE'

    def updateIDCmd(self, id=None):
        if id != None:
            self.id = id
        id = int(self.id)
        data = hex(id)[2:] + '00' * (BLOCK_SIZE - ID_SIZE)
        return self.writeCmd(ID_BLOCK, BLOCK_SIZE, data)

    def readIDCmd(self):
        return self.readCmd(ID_BLOCK, BLOCK_SIZE)

    def readBeginTimeCmd(self):
        return self.readCmd(BEGIN_TIME_BLOCK, BLOCK_SIZE)

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
    
    def readValidCmd(self):
        return self.readCmd(VALID_BLOCK, BLOCK_SIZE)
    
    def updateValidCmd(self,valid):
        if valid != None:
            self.valid = valid
        data = self.valid.encode('hex')
        assert len(data) == 12
        data += '0' * (BLOCK_SIZE * 2 - 12)
        return self.writeCmd(VALID_BLOCK, BLOCK_SIZE, data)          

    def readMoneyCmd(self):
        return self.readCmd(MONEY_BLOCK, BLOCK_SIZE)

    def readMoneyCmdBak(self):
        return self.readCmd(MONEY_BLOCK_BAK, BLOCK_SIZE)
    
    def updateMoneyCmd(self, money):
        'money min value is 1 cent, so multiply by 100 to convert to int operation'
        self.money = money
        cent = int(round(self.money, 2) * 100)
        data = ('%08X' % cent) + '00' * (BLOCK_SIZE - 4)
        return self.writeCmd(MONEY_BLOCK, BLOCK_SIZE, data)
    
    def updateMoneyCmdBak(self, money):
        'money min value is 1 cent, so multiply by 100 to convert to int operation'
        self.money_bak = money
        cent = int(round(self.money_bak, 2) * 100)
        data = ('%08X' % cent) + '00' * (BLOCK_SIZE - 4)
        return self.writeCmd(MONEY_BLOCK_BAK, BLOCK_SIZE, data)

    def readNameCmd(self):
        return self.readCmd(NAME_BLOCK,BLOCK_SIZE)

    def updateNameCmd(self):
        name_data = self.name.encode('hex')
        length = len(name_data)
        #print self.name
        #print length
        data = ('%02x'%length)+name_data
        while len(data) < 32:
            data += '0'
        return self.writeCmd(NAME_BLOCK,BLOCK_SIZE,data)

    def readDepartmentCmd(self):
        return self.readCmd(DEPARTMENT_BLOCK, BLOCK_SIZE)

    def updateDepartmentCmd(self):
        depart_data = self.department.encode('hex')
        length = len(depart_data)
        #print self.department
        #print length
        data = ('%02x' % length) + depart_data
        while len(data) < 32:
            data += '0'
        return self.writeCmd(DEPARTMENT_BLOCK, BLOCK_SIZE, data)

    def readConsumeHeadCmd(self):
        return self.readCmd(RECORD_INFO_HEAD_BLOCK,BLOCK_SIZE)

    def updateConsumeHeadCmd(self,head=None):
        if head != None:
            self.consume_head = head
        data = ('%08X' % self.consume_head) + '00' *  (BLOCK_SIZE - 4)
        return self.writeCmd(RECORD_INFO_HEAD_BLOCK,BLOCK_SIZE,data)

    def readConsumeNumCmd(self):
        return self.readCmd(RECORD_INFO_NUM_BLOCK,BLOCK_SIZE)

    def updateConsumeNumCmd(self,num=None):
        if num != None:
            self.consume_num = num
        data = ('%08X' % self.consume_num) + '00' *  (BLOCK_SIZE - 4)
        return self.writeCmd(RECORD_INFO_NUM_BLOCK,BLOCK_SIZE,data)

    def updateRecordCmd(self,head,position,posnum,consume_type,money):
        BLOCK = 4*(RECORD_POS_SECTOR+head)
        cmds=[]
        #print position
        data = position.encode('hex')
        #print data
        length = len(data)
        while len(data) < 32:
            data += '0'
        cmds.append( self.writeCmd(BLOCK, BLOCK_SIZE, data) )

        now_time = datetime.datetime.now()
        year = now_time.year
        month = now_time.month
        day = now_time.day
        data = '%08x%04x%04x%02x%08x%04x%02x' % (year, month, day, consume_type, money*100, posnum, length)
        cmds.append(self.writeCmd(BLOCK+1, BLOCK_SIZE, data))
        return cmds


    def readRecordPosCmd(self,head):
        BLOCK = 4 * (RECORD_POS_SECTOR + head)
        return self.readCmd(BLOCK,BLOCK_SIZE)

    def readRecordCmd(self,head):
        BLOCK = 4 * (RECORD_POS_SECTOR + head)
        return self.readCmd(BLOCK+1,BLOCK_SIZE)

    def newCardInitCommands(self):
        cmds = []

        #write name
        cmd = self.updateNameCmd()
        cmds.append(cmd)

        # write department
        cmd = self.updateDepartmentCmd()
        cmds.append(cmd)

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

        # write money
        cmd = self.updateMoneyCmd(0.0)
        cmds.append(cmd)

        cmd = self.updateMoneyCmdBak(0.0)
        cmds.append(cmd)

        # write record
        cmd = self.updateConsumeHeadCmd(0)
        cmds.append(cmd)

        cmd = self.updateConsumeNumCmd(0)
        cmds.append(cmd)
        
        cmd = self.updateValidCmd('yvalid')
        cmds.append(cmd)

        cmd = self.updateValidCmd('yvalid')
        cmds.append(cmd)

        #cmd = self.closeCmd()
        #cmds.append(cmd)

        return cmds

    def updateTimeCommands(self,begint,endt):
        cmds = []
        # write begin time and end time
        cmd = self.updateBeginTimeCmd(begint)
        cmds.append(cmd)
        cmd = self.updateEndTimeCmd(endt)
        cmds.append(cmd)

        return cmds

    def varify(self):
        password = raw_input("输入密码：\n")
        ppasswd = 0
        if password==ppasswd:
            #print "money : %d\n" %self.money
            return 1
        else:
            return 0
            #print "密码错误"