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
import logging

FILE_PATH1   = "/home/pi/axpert.json"


def main():
            logging.basicConfig(filename='/run/axpert.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
            ser = serial.Serial('/dev/axpert', 2400, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)#
	    ser.port = "/dev/axpert"
	    ser.baudrate = 2400
            ser.bytesize = serial.EIGHTBITS     #number of bits per bytes
            ser.parity = serial.PARITY_NONE     #set parity check: no parity
            ser.stopbits = serial.STOPBITS_ONE  #number of stop bits
            ser.timeout = 1                     #non-block #ser.xonxoff = False #disable software flow control
            ser.rtscts = False                  #disable hardware (RTS/CTS) flow control
            ser.dsrdtr = False                  #disable hardware (DSR/DTR) flow control
            ser.writeTimeout = 2                #timeout for write

            response=""
            tempfile = open(FILE_PATH1)
            data = tempfile.read()
            tempfile.close()
            commands = data.split(';', 99)
            if len(commands) > 0:
               for command in commands:
                   xmodem_crc_func = crcmod.predefined.mkCrcFun('xmodem')
                   command_crc = command + unhexlify(hex(xmodem_crc_func(command)).replace('0x','',1)) + "\r"
                   logging.debug("command sent:"+str(command_crc))
                   ser.write(command_crc)
                   time.sleep (0.15)
                   while True:
                      r = ser.read(1024)
                      response += r
                      if '\r' in r: break
                   logging.debug("response received:"+str(response))
                   time.sleep (1)

if __name__ == '__main__':
    main()
