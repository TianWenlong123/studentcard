# -*- coding: utf-8 -*-
from data_type import *

class Controller:
    def __init__(self):
        #初始化
        self.ser = Ser()
        self.state=''

    def createNew(self,filename):
        card = NewCard()

        if(card.getInfo(filename)):
            card.writeInfo(self.ser)

    #def cancelCard(self):

    #def accesscrl(self):

    #def register(self):

    #def consume(self):

    #def store(self):
