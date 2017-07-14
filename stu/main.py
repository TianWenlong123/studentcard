# -*- coding: utf-8 -*-
from controller import *
from data_type import MAC_PORT

ctrl = Controller()

def main():
    ctrl.waitCard()
    ctrl.createNew('NewCardInfo.txt')


if __name__ == '__main__':
    main()
