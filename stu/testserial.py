# -*- coding: utf-8 -*-
import serial

ser = serial.Serial('com3',9600)
ser.timeout=10
ser.write("2222222222\n")   # 每个命令以 \n 结尾
#ser.close()

#import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())

#if len(plist) <= 0:
#    print("没有发现端口!")
#else:
#    plist_0 = list(plist[0])
#    serialName = plist_0[0]
#    serialFd = serial.Serial(serialName, 9600, timeout=60)
#    print("可用端口名>>>", serialFd.name)
#    ser.write("0000000000\n")
#    ser.close()