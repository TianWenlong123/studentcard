# -*- coding: utf-8 -*-
from card import Card
from myserial import MySerial, MAC_PORT

class Controller:
    def __init__(self, portname=None):
        #初始化
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
            for cmd in cmds:
                response = self.ser.sendCmd(cmd)
                if not response or len(response) < 4 or response[0:4] != 'OKAY':
                    print 'Error!', response
                    # return False
                else:
                    print response

    def sendCmd(self, cmd):
        response = self.ser.sendCmd(cmd)
        return response


    #def cancelCard(self):

    #def accesscrl(self):

    #def register(self):

    #def consume(self):

    #def store(self):
