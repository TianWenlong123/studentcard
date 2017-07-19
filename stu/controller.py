# -*- coding: utf-8 -*-
from card import Card
from myserial import MySerial, MAC_PORT

class Controller:
    def __init__(self,position,posnum, portname=None):
        #初始化

        self.position = position
        self.posnum =posnum

        if portname == None:
            self.ser = MySerial()
        else:
            self.ser = MySerial(portname)
        self.state=''
        self.card = Card()

    def available(self):
        return self.ser.isOpen()

    def createNew(self, filename):
        if(self.card.getInfo(filename)):
            cmds = self.card.newCardInitCommands()
            self.sendCmd(cmds)

    def sendCmd(self, cmds):
        for cmd in cmds:
            # print cmd
            response = self.ser.sendCmd(cmd)
            if not response or len(response) < 4 or response[0:4] != 'OKAY':
                print 'Error!', response
                # return False
            else:
                print response

    def register(self,begint,endt):
        cmds = self.card.updateTimeCommands(begint,endt)
        self.sendCmd(cmds)

    #def accesscrl(self):

    def changeRecord(self,consume_type,money):
        #修改头指针
        cmd = self.card.readConsumeHeadCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        str = '0x' + response[index:index+8]
        old_head = int(str, 16)
        new_head = old_head + 1
        if new_head > 5:
            new_head = new_head-5
        cmd = self.card.updateConsumeHeadCmd(new_head)
        respnose = self.ser.sendCmd(cmd)
        #修改数量
        cmd = self.card.readConsumeNumCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        str = '0x' + response[index:index+8]
        num = int(str,16)
        if num < 5:
            num = num + 1
            cmd = self.card.updateConsumeNumCmd(num)
            response = self.ser.sendCmd(cmd)
        #修改记录
        cmds = self.card.updateRecordCmd(new_head,self.position,self.posnum,consume_type,money)
        self.sendCmd(cmds)

    def consume(self,money):
        #读取金额
        cmd = self.card.readMoneyCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        #print index
        str = '0x' + response[index:index + 8]
        old_money = int(str, 16)
        new_money = float(old_money - money * 100) / 100
        cmd = self.card.updateMoneyCmd(new_money)
        response = self.ser.sendCmd(cmd)
        #print response
        #修改记录
        self.changeRecord(1,money)

    def save(self,money):
        #需要增加验证
        cmd = self.card.readMoneyCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        #print index
        str = '0x'+response[index:index + 8]
        #print str
        old_money = int(str, 16)
        #print old_money
        new_money = float(old_money + money*100)/100
        #print new_money
        cmd = self.card.updateMoneyCmd(new_money)
        response = self.ser.sendCmd(cmd)

        #修改记录
        self.changeRecord(2, money)

    def showInfo(self):
        self.card.showInfo()

    def waitCard(self):
        text = ''
        text = self.ser.port.readline()
        while text == '':
            text = self.ser.port.readline()

        while text:
            print text
            text = self.ser.port.readline()




