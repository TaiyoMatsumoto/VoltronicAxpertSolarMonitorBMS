#! /usr/bin/python

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
import sys
import signal
import time
import MySQLdb
from binascii import unhexlify

# List of AXPERT/Voltronic commands 
Q1    = "\x51\x31\x1B\xFC\x0D"
QPIGS = "\x51\x50\x49\x47\x53\xB7\xA9\x0D"
QPIWS = "\x51\x50\x49\x57\x53\xB4\xDA\x0D"
QMOD  = "\x51\x4D\x4F\x44\x49\xC1\x0D"
QPIRI = "\x51\x50\x49\x52\x49\xF8\x54\x0D"

POP02 = "\x50\x4F\x50\x30\x32\xE2\x0A\x0D"  # SBU
POP01 = "\x50\x4F\x50\x30\x31\xD2\x69\x0D"  # SUB
POP00 = "\x50\x4F\x50\x30\x30\xC2\x48\x0D"  # USB
PCP00 = "\x50\x43\x50\x30\x30\x8D\x7A\x0D"  # Utility First
PCP01 = "\x50\x43\x50\x30\x31\x9D\x5B\x0D"  # Solar First
PCP02 = "\x50\x43\x50\x30\x32\xAD\x38\x0D"  # Solar + Utility
PCP03 = "\x50\x43\x50\x30\x33\xBD\x19\x0D"  # Only Solar
MCHGC010 = ""  # Setting max charging Current
MCHGC020 = ""  # Setting max charging Current
MCHGC030 = ""  # Setting max charging Current
MCHGC040 = ""  # Setting max charging Current
MCHGC050 = ""  # Setting max charging Current

PCVVXX_X = ""  # Setting battery C.V. charging voltage
PBFTXX_X = ""  # Setting battery float charging voltage
PBCVXX_X = ""  # Set battery re-charge voltage
PBDVXX_X = ""  # Set battery re-discharge voltage

def main():

            ser = serial.Serial('/dev/axpert', 2400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)
	    ser.port = "/dev/axpert"
	    ser.baudrate = 2400
	    ser.bytesize = serial.EIGHTBITS     #number of bits per bytes
	    ser.parity = serial.PARITY_NONE     #set parity check: no parity
            ser.stopbits = serial.STOPBITS_ONE  #number of stop bits
            ser.timeout = 1                     #non-block #ser.xonxoff = False #disable software flow control
            ser.rtscts = False                  #disable hardware (RTS/CTS) flow control
            ser.dsrdtr = False                  #disable hardware (DSR/DTR) flow control
            ser.writeTimeout = 2                #timeout for write

            conn = MySQLdb.connect(host="localhost",user="admin",passwd="<admin password>",db="axpert")
            cursor = conn.cursor()

            response=""
            command  =  "QPIGS"
            xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
            command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + "\r"
	    ser.write(command_crc)
	    time.sleep (0.15)
            while True:
	        r = ser.read(1024)
                response += r
                if '\r' in r: break
            response_var = re.sub ('[^0-9. ]','',response)
       	    response_var.rstrip()
       	    vars = response_var.split(' ', 99)
            SQL_statement = ( "INSERT INTO QPIGS(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16) VALUES ('%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f')" % (float(vars[0]),float(vars[1]),float(vars[2]),float(vars[3]),float(vars[4]),float(vars[5]),float(vars[6]),float(vars[7]),float(vars[8]),float(vars[9]),float(vars[10]),float(vars[11]),float(vars[12]),float(vars[13]),float(vars[14]),float(vars[15])))
            if (float(vars[15])*float(vars[8]))>(float(vars[5])*2) or float(vars[9])>(40*1.25) or float(vars[3])<45 or float(vars[3])>55 or float(vars[5])>15000 or float(vars[4])>15000 or (float(vars[12])*float(vars[13]))>3000  or (float(vars[8])*float(vars[9]))>5000 or (float(vars[8])*float(vars[15]))>10000 or (float(vars[11]))<10 or (float(vars[11]))>60 or (float(vars[13]))>500 or (float(vars[6])>0 and float(vars[2])<150) or (float(vars[2])>0 and float(vars[3])<30) or (float(vars[8]))<40 or (float(vars[8]))>60 or (float(vars[2]))>260 or (float(vars[2]))<200 or (float(vars[12])>1 and float(vars[13])<100):   #Ignore the noise, store only valid data
                     ignore_data=1
            else:
                     ignore_data=0
                     try:
                        cursor.execute(SQL_statement)
                        conn.commit()
                     except:
                        conn.rollback()

            response=""
            command  =  "QMOD"
            xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
            command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + "\r"
            ser.write(command_crc)
            time.sleep (0.15)
            while True:
                r = ser.read(1024)
                response += r
                if '\r' in r: break
            response_var = re.sub ('[^a-zA-Z_ ]','',response)
            response_var.rstrip()
            vars = response_var.split(' ', 99)
            SQL_statement = ( "INSERT INTO QMOD(var1) VALUES ('%s')" % (str(vars[0])))
            try:
               cursor.execute(SQL_statement)
               conn.commit()
            except:
               conn.rollback()

            response=""
            command  =  "QPIWS"
            xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
            command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + "\r"
            ser.write(command_crc)
            time.sleep (0.15)
            while True:
                r = ser.read(1024)
                response += r
                if '\r' in r: break

#                     012345678901234567890123456789012345
#F          response="011110011000000000111111100000000000"
#W          response="000001100111101111000000011111000000"

            response_var = re.sub ('[^0-9. ]','',response)
            response_var.rstrip()
            vars = response_var.split(' ', 99)
            x=str(vars[0])
            warning=int(x[5])+int(x[6])+int(x[9])+int(x[10])+int(x[11])+int(x[12])+int(x[14])+int(x[15])+int(x[16])+int(x[17])+int(x[25])+int(x[26])+int(x[27])+int(x[28])+int(x[29])
            fault=int(x[1])+int(x[2])+int(x[3])+int(x[4])+int(x[7])+int(x[8])+int(x[18])+int(x[19])+int(x[20])+int(x[21])+int(x[22])+int(x[23])+int(x[24])
            message="OK"
            if (fault > 0):
                   message="FAULT!!!"
            elif (warning > 0):
                   message="WARNING!"
            SQL_statement = ( "INSERT INTO QPIWS(var1,var2) VALUES ('%s','%s')" % (str(vars[0]),message ))
            try:
               cursor.execute(SQL_statement)
               conn.commit()
            except:
               conn.rollback()

            response=""
            command  =  "Q1"
            xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
            command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + "\r"
            ser.write(command_crc)
            time.sleep (0.15)
            while True:
                r = ser.read(1024)
                response += r
                if '\r' in r: break
            response_var = re.sub ('[^0-9. ]','',response)
            response_var.rstrip()
            vars = response_var.split(' ', 99)
            SQL_statement = ( "INSERT INTO Q1(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16,var17,var18,var19,var20,var21,var22,var23,var24,var25,var26,var27) VALUES ('%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f')" % ( float(vars[0]),float(vars[1]),float(vars[2]),float(vars[3]),float(vars[4]),float(vars[5]),float(vars[6]),float(vars[7]),float(vars[8]),float(vars[9]),float(vars[10]),float(vars[11]),float(vars[12]),float(vars[13]),float(vars[14]),float(vars[15]),float(vars[16]),float(vars[17]),float(vars[18]),float(vars[19]),float(vars[20]),float(vars[21]),float(vars[22]),float(vars[23]),float(vars[24]),float(vars[25]),float(vars[26]) ))
            try:
               cursor.execute(SQL_statement)
               conn.commit()
            except:
               conn.rollback()

            response=""
            command  =  "QPIRI"
            xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
            command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + "\r"
            ser.write(command_crc)
            time.sleep (0.15)
            while True:
                r = ser.read(1024)
                response += r
                if '\r' in r: break
            response_var = re.sub ('[^0-9. ]','',response)
            response_var.rstrip()
            vars = response_var.split(' ', 99)
            SQL_statement = ( "INSERT INTO QPIRI(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13,var14,var15,var16,var17,var18,var19,var20,var21,var22,var23,var24,var25,var26) VALUES ('%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f')" % ( float(vars[0]),float(vars[1]),float(vars[2]),float(vars[3]),float(vars[4]),float(vars[5]),float(vars[6]),float(vars[7]),float(vars[8]),float(vars[9]),float(vars[10]),float(vars[11]),float(vars[12]),float(vars[13]),float(vars[14]),float(vars[15]),float(vars[16]),float(vars[17]),float(vars[18]),float(vars[19]),float(vars[20]),float(vars[21]),float(vars[22]),float(vars[23]),float(vars[24]),float(vars[25])))

            try:
               cursor.execute(SQL_statement)
               conn.commit()
            except:
               conn.rollback()


            cursor.close()
            conn.close()

if __name__ == '__main__':
    main()
