# -*- coding: utf-8 -*-
from data_type import *

class Controller:
    def __init__(self):
        #初始化
        self.ser = Ser()
        self.state=''
        self.card = NewCard()

    def createNew(self,filename):
        if(self.card.getInfo(filename)):
            self.card.writeInfo(self.ser)

    def cancelCard(self):
        self.ser.send_cmd('Cancel')

    def register(self,begint,endt):
        self.ser.send_cmd(begint)
        self.ser.send_cmd(endt)

    #def accesscrl(self):

    #def consume(self):

    #def store(self):

    def waitCard(self):
        text = ''
        text = self.ser.port.readline()
        while text == '':
            text = self.ser.port.readline()

        while text:
            print text
            text = self.ser.port.readline()




