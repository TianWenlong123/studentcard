# -*- coding: utf-8 -*-
from card import Card
from myserial import MySerial, MAC_PORT

PRIME1 = 39089
PRIME2 = 40883

class Controller:
    def __init__(self,position,posnum, portname=None):
        #初始化

        self.position = position
        self.posnum =posnum
        self.portname=portname

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
            print 'Completed!'
            
    def setInvalid(self):
        cmd = self.card.updateValidCmd('nvalid')
        response = self.ser.sendCmd(cmd)
        
        cmd = self.card.updateMoneyCmd(0.0)
        response = self.ser.sendCmd(cmd)
        
        cmd = self.card.updateMoneyCmdBak(0.0)
        response = self.ser.sendCmd(cmd)
        
        print 'Set invalid successfully!'
        
    def sendCmd(self, cmds):
        for cmd in cmds:
            # print cmd
            response = self.ser.sendCmd(cmd)
            if not response or len(response) < 4 or (response[0:4] != 'OKAY' and response[0:4] != 'CLSE'):
                print 'Error!', response
                # return False

    def register(self,begint,endt):
        cmds = self.card.updateTimeCommands(begint,endt)
        self.sendCmd(cmds)
        
        print 'Log in successfully!'
    #def accesscrl(self):

    def changeRecord(self,consume_type,money):
        #修改头指针
        cmd = self.card.readConsumeHeadCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        str = '0x' + response[index:index+8]
        old_head = int(str, 16)
        new_head = old_head + 1
        print new_head
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
        print num
        if num < 5:
            num = num + 1
            cmd = self.card.updateConsumeNumCmd(num)
            response = self.ser.sendCmd(cmd)
        #修改记录
        cmds = self.card.updateRecordCmd(new_head,self.position,self.posnum,consume_type,money)
        self.sendCmd(cmds)

    def consume(self,money):
        #读取金额
        cmd = self.card.readValidCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        print index

        str = response[index:index + 12]
        valid = str.decode('hex')
        if valid != 'yvalid':
            print 'InValid!'
            return
        
        cmd = self.card.readMoneyCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        #print index
        str = '0x' + response[index:index + 8]
        old_money = int(str, 16)

        cmd_bak = self.card.readMoneyCmdBak()
        response = self.ser.sendCmd(cmd_bak)
        index = response.index(':')+1
        #print index
        str = '0x' + response[index:index + 8]
        old_money_bak = int(str, 16)

        check = old_money * PRIME1 % PRIME2

        if check != old_money_bak:
            print 'Money Error!'
            return
        
        print 'old money = ' + str(old_money)
        
        varify = 1
        if money >= 50:
            varify = self.varify()
        if varify == 1:
            new_money = float(old_money - money * 100) / 100
            if new_money >= 0:
                cmd = self.card.updateMoneyCmd(new_money)
                response = self.ser.sendCmd(cmd)
                #print response
                check = new_money * PRIME1 % PRIME2
                cmd_bak = self.card.updateMoneyCmdBak(check)

                response = self.ser.sendCmd(cmd_bak)
                # 修改记录
                self.changeRecord(1, money)
                print 'new money = ' + str(new_money)
            else:
                print 'insufficient funds'
                return
        else:
            print 'Password error'
            return

    def save(self,money):
        #需要增加验证
        cmd = self.card.readValidCmd()
        response = self.ser.sendCmd(cmd)

        index = response.index(':')+1
        str=response[index:index + 12]

        valid = str.decode('hex')
        if valid != 'yvalid':
            print 'InValid!'
            return
        
        cmd = self.card.readMoneyCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        #print index
        str = '0x'+response[index:index + 8]
        #print str
        old_money = int(str, 16)
        
        cmd_bak = self.card.readMoneyCmdBak()
        response = self.ser.sendCmd(cmd_bak)
        index = response.index(':')+1
        #print index
        str = '0x' + response[index:index + 8]
        old_money_bak = int(str, 16)

        check = old_money * PRIME1 % PRIME2

        if check != old_money_bak :
            print 'Money Error!'
            return

        print 'old money = ' + str(old_money)
        
        new_money = float(old_money + money*100)/100
        #print new_money
        cmd = self.card.updateMoneyCmd(new_money)
        response = self.ser.sendCmd(cmd)
        check = new_money * PRIME1 % PRIME2
        cmd_bak = self.card.updateMoneyCmdBak(check)
        response = self.ser.sendCmd(cmd_bak)
        
        print 'new money = ' + str(new_money)
        #修改记录
        self.changeRecord(2, money)

    def varify(self):
        password = raw_input("输入密码：\n")
        cmd = self.card.readPasswdCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        #print index
        str = response[index:index + 12]
        passwd = str.decode('hex')
        if password==passwd:
            #print "money : %d\n" %self.money
            return 1
        else:
            return 0
        
    def showInfo(self):
        cmd = self.card.readValidCmd()
        response = self.ser.sendCmd(cmd)
        print response
        index = response.index(':') + 1
        #print index
        str = response[index:index + 12]
        valid = str.decode('hex')
        if valid != 'yvalid':
            print 'InValid!'
            return
        #read name
        cmd = self.card.readNameCmd()
        response = self.ser.sendCmd(cmd)
        print response
        index = response.index(':')+1
        length = int('0x'+response[index:index + 2],16)
        name = response[index+2:index+2+length].decode('hex')
        print 'name: %s' % name
        #read department
        cmd = self.card.readDepartmentCmd()
        response = self.ser.sendCmd(cmd)
        #print response
        index = response.index(':')+1
        length = int('0x'+response[index:index + 2],16)
        department = response[index+2:index+2+length].decode('hex')
        print 'department: %s' % department

        # read student id number
        cmd = self.card.readIDCmd()
        response = self.ser.sendCmd(cmd)
        #print response
        index = response.index(':')+1
        str = '0x' + response[index:index + 8]
        ID = int(str,16)
        print 'ID: %d' % ID

        # read begin time and end time
        cmd = self.card.readBeginTimeCmd()
        response = self.ser.sendCmd(cmd)
        #print response
        index = response.index(':')+1
        year = int('0x'+ response[index:index+8],16)
        month = int('0x'+ response[index+8:index+12],16)
        day = int('0x' + response[index + 12:index + 16], 16)
        print "beginTime: %d:%d:%d" %(year,month,day)

        cmd = self.card.readEndTimeCmd()
        response = self.ser.sendCmd(cmd)
        #print response
        index = response.index(':')+1
        year = int('0x'+ response[index:index+8],16)
        month = int('0x'+ response[index+8:index+12],16)
        day = int('0x' + response[index + 12:index + 16], 16)
        print "EndTime: %d:%d:%d" %(year,month,day)

        # read money
        cmd = self.card.readMoneyCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        #print index
        str = '0x' + response[index:index + 8]
        money = int(str, 16)
        money = float(money)/100
        print 'Money: %d' % money

        # read record
        # 读头指针
        cmd = self.card.readConsumeHeadCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        str = '0x' + response[index:index+8]
        head = int(str, 16)
        #print head
        # 读数量
        cmd = self.card.readConsumeNumCmd()
        response = self.ser.sendCmd(cmd)
        index = response.index(':')+1
        str = '0x' + response[index:index+8]
        num = int(str,16)
        #print num

        #读记录
        i=0
        while i < num :
            temp_head = head-i
            if temp_head < 1:
                temp_head = temp_head+5

            cmd = self.card.readRecordCmd(temp_head)
            response = self.ser.sendCmd(cmd)
            index = response.index(':')+1
            year = int('0x' + response[index:index + 8], 16)
            month = int('0x' + response[index + 8:index + 12], 16)
            day = int('0x' + response[index + 12:index + 16], 16)
            consume_type = int('0x' + response[index + 16:index + 18], 16)
            con_money = int('0x' + response[index + 18:index + 26], 16)
            posnum = int('0x' + response[index + 26:index + 30], 16)
            length = int('0x' + response[index + 30:index + 32], 16)

            print '%d:%d:%d -- ' %(year,month,day),
            if consume_type==1:
                print '消费 -- ',
            else:
                print '储值 -- ',
            print '%d 元 -- 终端号 %d ' %(con_money,posnum),

            cmd = self.card.readRecordPosCmd(temp_head)
            response = self.ser.sendCmd(cmd)
            index = response.index(':')+1
            #print response
            #print response[index:index+length]
            str=response[index:index+length].decode('hex')
            print str

            i = i+1

    def waitCard(self):
        text = ''
        text = self.ser.port.readline()
        while text == '':
            text = self.ser.port.readline()

        while text:
            print text
            text = self.ser.port.readline()




