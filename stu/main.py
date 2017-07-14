# -*- coding: utf-8 -*-
from controller import *
from data_type import MAC_PORT

ctrl = Controller(MAC_PORT)

def main():
    while not ctrl.available():
        continue
    
    ctrl.createNew('NewCardInfo.txt')


if __name__ == '__main__':
    main()
