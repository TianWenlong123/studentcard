# -*- coding: utf-8 -*-
from controller import *
from data_type import MAC_PORT
import platform

portname = 'COM3'
if not 'windows' in platform.platform().lower():
    portname = MAC_PORT
ctrl = Controller('饮食中心',1,portname=portname)

def main():
    ctrl.waitCard()
    while 1:
        print "1 : 制作新卡\n"
        print "2 : 注销旧卡\n"
        print "3 : 学生注册\n"
        print "4 : 消费\n"
        print "5 : 存钱\n"
        print "6 : 查看信息\n"
        print "7 : 退出\n"
        print "\n"
        choice = input("Please input your chioce:\n")

        if choice==1:
            a = raw_input("fill in the file(NewCardInfo.txt) with student's information and input ok :\n")
            ctrl.createNew('NewCardInfo.txt')

        if choice==2:
            a=1

        if choice==3:
            begin_time = raw_input("Please input begin time\n")
            end_time = raw_input("Please input end time\n")
            ctrl.register(begin_time,end_time)

        if choice==4:
            #money = input("Please input consume amount\n")
            money = 10.50
            ctrl.consume(money)

        if choice==5:
            # money = input("Please input save amount\n")
            money = 10.50
            ctrl.save(money)

        if choice==6:
            ctrl.showInfo()

        if choice==7:
            break

if __name__ == '__main__':

    main()
