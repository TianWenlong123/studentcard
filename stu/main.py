# -*- coding: utf-8 -*-
from controller import *
from data_type import MAC_PORT

ctrl = Controller()

def main():
    ctrl.waitCard()
    print "1 : 制作新卡\n"
    print "2 : 注销旧卡\n"
    print "3 : 学生注册\n"
    choice = input("Please input your chioce:\n")
    if choice==1:
        a =''
        a = input("fill in the file(NewCardInfo.txt) with student's information and input ok :\n")
        ctrl.createNew('NewCardInfo.txt')

    if choice==3:
        begin_time = input("Please input begin time")
        end_time = input("Please input end time")
        ctrl.register(begin_time,end_time)


if __name__ == '__main__':
    main()
