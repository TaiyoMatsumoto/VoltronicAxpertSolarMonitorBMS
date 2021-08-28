#! /usr/bin/python
import struct
from binascii import unhexlify
import urllib2
import serial
import time, sys, string
import sqlite3
import json
import urllib
import httplib
import datetime
import calendar
import os
import re
import crcmod
import usb.core
import usb.util
import signal
import MySQLdb

MaxBatAh = 280            # BAT Ah
k1       =-0.063157894
k2       =-k1*100

# List of Daly's BMS commands
C9 = 'a58098080000000000000000c5'
C8 = 'a58097080000000000000000c4'
C7 = 'a58096080000000000000000c3'
C6 = 'a58095080000000000000000c2'
C5 = 'a58094080000000000000000c1'
C4 = 'a58093080000000000000000c0'
C3 = 'a58092080000000000000000bf'
C2 = 'a58091080000000000000000be'
C1 = 'a58090080000000000000000bd'

def crc_string(str1):
    sum_crc = 0
    for x in str1:
            z = int(x.encode('hex'),16)
            sum_crc = sum_crc + z
    return hex(sum_crc) [-2:]

def main():

    ser = serial.Serial(
       port='/dev/bms',
       baudrate = 9600,
       parity=serial.PARITY_NONE,
       stopbits=serial.STOPBITS_ONE,
       bytesize=serial.EIGHTBITS,
       timeout = 2)

    conn = MySQLdb.connect(host="localhost",user="admin",passwd="<admin passoword>",db="axpert")
    cursor = conn.cursor()
    ignoreSQL=0

    command=C1
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var1=float(int((response [(2*2):(3*2)].encode('hex')),16))/10
    var2=float(int((response [(3*2):(4*2)].encode('hex')),16))/10
    var3=(30000-float(int((response [(4*2):(5*2)].encode('hex')),16)))/10
    SOC=float(int((response [(5*2):(6*2)].encode('hex')),16))/10
    var4=SOC*(1+k1)+k2                                                            #linear compensation

    command=C2
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var5=float(int((response [(2*2):(3*2)].encode('hex')),16))/1000
    var6=int((response [(3*2):(4*2-1)].encode('hex')),16)
    var7=float(int((response [(4*2-1):(5*2-1)].encode('hex')),16))/1000
    var8=int((response [(5*2-1):(6*2-2)].encode('hex')),16)

    command=C3
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var9=int(response [4:5].encode('hex'),16)-40
    var10=int(response [5:6].encode('hex'),16)
    var11=int(response [6:7].encode('hex'),16)-40
    var12=int(response [7:8].encode('hex'),16)

    command=C4
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var13=int(response [(2*2):(2*2+1)].encode('hex'),16)
    var14=int(response [(2*2+1):(2*2+2)].encode('hex'),16)
    var15=int(response [(2*2+2):(2*2+3)].encode('hex'),16)
    var16=int(response [(2*2+3):(2*2+4)].encode('hex'),16)
    BatAh=float(int(response [(2*2+4):(2*2+8)].encode('hex'),16))/1000
    var17=((100*BatAh/MaxBatAh)*(1+k1)+k2)*MaxBatAh/100

    command=C5
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var18=int(response [4:5].encode('hex'),16)
    var19=int(response [5:6].encode('hex'),16)
    var20=int(response [6:7].encode('hex'),16)
    var21=int(response [7:8].encode('hex'),16)
    var22=format(int(response [8:9].encode('hex'),16),'08b')
    var23=int(response [9:11].encode('hex'),16)

    command=C6
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
        ignoreSQL=+1
    var24=float(int(response [(2*2+1):(3*2+1)].encode('hex'),16))/1000
    var25=float(int(response [(3*2+1):(4*2+1)].encode('hex'),16))/1000
    var26=float(int(response [(4*2+1):(5*2+1)].encode('hex'),16))/1000
    crc=response [(13+6*2):(13+7*2-1)].encode('hex')
    if crc != crc_string(response [(13+0*2):(13+6*2)]):
         ignoreSQL=+1
    var27=float(int(response [(13+2*2+1):(13+3*2+1)].encode('hex'),16))/1000
    var28=float(int(response [(13+3*2+1):(13+4*2+1)].encode('hex'),16))/1000
    var29=float(int(response [(13+4*2+1):(13+5*2+1)].encode('hex'),16))/1000
    crc=response [(26+6*2):(26+7*2-1)].encode('hex')
    if crc != crc_string(response [(26+0*2):(26+6*2)]):
         ignoreSQL=+1
    var30=float(int(response [(26+2*2+1):(26+3*2+1)].encode('hex'),16))/1000
    var31=float(int(response [(26+3*2+1):(26+4*2+1)].encode('hex'),16))/1000
    var32=float(int(response [(26+4*2+1):(26+5*2+1)].encode('hex'),16))/1000
    crc=response [(39+6*2):(39+7*2-1)].encode('hex')
    if crc != crc_string(response [(39+0*2):(39+6*2)]):
         ignoreSQL=+1
    var33=float(int(response [(39+2*2+1):(39+3*2+1)].encode('hex'),16))/1000
    var34=float(int(response [(39+3*2+1):(39+4*2+1)].encode('hex'),16))/1000
    var35=float(int(response [(39+4*2+1):(39+5*2+1)].encode('hex'),16))/1000
    crc=response [(52+6*2):(52+7*2-1)].encode('hex')
    if crc != crc_string(response [(52+0*2):(52+6*2)]):
         ignoreSQL=+1
    var36=float(int(response [(52+2*2+1):(52+3*2+1)].encode('hex'),16))/1000
    var37=float(int(response [(52+3*2+1):(52+4*2+1)].encode('hex'),16))/1000
    var38=float(int(response [(52+4*2+1):(52+5*2+1)].encode('hex'),16))/1000
    crc=response [(65+6*2):(65+7*2-1)].encode('hex')
    if crc != crc_string(response [(65+0*2):(65+6*2)]):
         ignoreSQL=+1
    var39=float(int(response [(65+2*2+1):(65+3*2+1)].encode('hex'),16))/1000

    if var24<2 or var25<2 or var26<2 or var27<2 or var28<2 or var29<2 or var30<2 or var31<2 or var32<2 or var33<2 or var34<2 or var35<2 or var36<2 or var37<2 or var38<2 or var39<2:
       ignoreSQL=+1
    if var24>4 or var25>4 or var26>4 or var27>4 or var28>4 or var29>4 or var30>4 or var31>4 or var32>4 or var33>4 or var34>4 or var35>4 or var36>4 or var37>4 or var38>4 or var39>4:
       ignoreSQL=+1

    command=C7
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var40=int((response [(5):(6)].encode('hex')),16)-40
    if var40<5 or var40>60:
       ignoreSQL=+1

    command=C8
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var41=format(int(response [(2*2):(6*2)].encode('hex'),16),'064b')

    command=C9
    ser.write (command.decode('hex'))
    time.sleep(0.15)
    response = ser.read(1024)
    crc=response [(6*2):(7*2-1)].encode('hex')
    if crc != crc_string(response [(0*2):(6*2)]):
       ignoreSQL=+1
    var42=format(int(response [(4):(5)].encode('hex'),16),'08b')
    var43=format(int(response [(5):(6)].encode('hex'),16),'08b')
    var44=format(int(response [(6):(7)].encode('hex'),16),'08b')
    var45=format(int(response [(7):(8)].encode('hex'),16),'08b')
    var46=format(int(response [(8):(9)].encode('hex'),16),'08b')
    var47=format(int(response [(9):(10)].encode('hex'),16),'08b')
    var48=format(int(response [(10):(11)].encode('hex'),16),'08b')
    var49=int(response [(11):(12)].encode('hex'),16)

    if ignoreSQL == 0:
        SQL_statement = ( "INSERT INTO BMS(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16,var17,var18,var19,var20,var21,var22,var23,var24,var25,var26,var27,var28,var29,var30,var31,var32,var33,var34,var35,var36,var37,var38,var39,var40,var41,var42,var43,var44,var45,var46,var47,var48,var49) VALUES ('%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%s','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%s','%s','%s','%s','%s','%s','%s','%s','%f')" % ( var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16,var17,var18,var19,var20,var21,var22,var23,var24,var25,var26,var27,var28,var29,var30,var31,var32,var33,var34,var35,var36,var37,var38,var39,var40,var41,var42,var43,var44,var45,var46,var47,var48,var49 ))
        try:
            cursor.execute(SQL_statement)
            conn.commit()
        except:
            conn.rollback()
    cursor.close()
    conn.close()
    ser.close()


if __name__ == '__main__':
    main()

