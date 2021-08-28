#! /usr/bin/python

import urllib2
import string
import sqlite3
import json
import urllib
import httplib
import calendar
import sys
import signal
import MySQLdb
import time
import datetime as dt
import logging
import math
import requests
import statistics

FILE_PATH1     = "/home/pi/controller.json"
DEBUG_FLAG     = True
BAT_TO_USB    = 50.6                    # switch to USB mode
BAT_GRID_ON   = BAT_TO_USB + 0.6        # activate public grid
BAT_GRID_OFF  = BAT_GRID_ON + 0.6       # deactivate public grid
BAT_FULL      = 54.5
BAT_FLT_LOW   = BAT_FULL - 0.8
BAT_CVV_LOW   = BAT_FLT_LOW + 0.1
BAT_FLT_HIGH  = BAT_FULL + 0.6
BAT_CVV_HIGH  = BAT_FLT_HIGH + 0.1
SOC_CHRG_LOW  = 14
SOC_CHRG_HIGH = SOC_CHRG_LOW + 10
BAT_CELL_MAX  = 3.53

def main():

    if DEBUG_FLAG:
       logging.basicConfig(filename='/var/log/controller.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    tempfile = open(FILE_PATH1)
    command = tempfile.read()
    tempfile.close()
    if command == "ON":
       conn = MySQLdb.connect(host="localhost",user="admin",passwd="<admin password>",db="axpert")
       cursor = conn.cursor()

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=10)
       cursor.execute("select count(*) from axpert.QPIRI where created >= %s and created < %s and var17 = 0 and var18 = 3", (range2, range1))
       i = cursor.fetchone()[0]
       cursor.execute("select count(*) from axpert.BMS where created >= %s and created < %s and var4 <= %s", (range2, range1, SOC_CHRG_LOW))
       j = cursor.fetchone()[0]
       if i >= 9 and j >= 9:
          logging.debug("SoC is very low, switching to mode: solar first ...")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"PCP01")

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=10)
       cursor.execute("select count(*) from axpert.QPIRI where created >= %s and created < %s and var17 = 0 and var18 = 1", (range2, range1))
       i = cursor.fetchone()[0]
       cursor.execute("select count(*) from axpert.BMS where created >= %s and created < %s and var4 >= %s", (range2, range1, SOC_CHRG_HIGH))
       j = cursor.fetchone()[0]
       if i >= 9 and j >= 9:
          logging.debug("SoC is optimal, switching to mode: only solar ...")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"PCP03")


       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=10)
       cursor.execute("select count(*) from axpert.QPIRI where created >= %s and created < %s and var17 = 2", (range2, range1))
       i = cursor.fetchone()[0]
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var1 > 0 and var9 >= %s", (range2, range1, BAT_GRID_OFF))
       j = cursor.fetchone()[0]
       if i >= 9 and j >= 9 and dt.datetime.now().hour <= 13 and dt.datetime.now().hour >= 7 :  # fix - invertor FW bug
          logging.debug("Battery voltage is within limits, grid switch deactivated ...")
          r = requests.post('http://rpi3/switch.json',"OFF")

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=4)
       cursor.execute("SELECT var17 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       i = statistics.median(sum(map(list,cursor.fetchall()), []))
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var1 > 0 and var9 <= %s", (range2, range1, BAT_TO_USB))
       j = cursor.fetchone()[0]
       if i == 2 and j >= 3 :
          logging.debug("Battery voltage critical, switching to USB mode ...")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"POP00")

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=4)
       cursor.execute("SELECT var17 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       i = statistics.median(sum(map(list,cursor.fetchall()), []))
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var1 = 0 and var9 <= %s", (range2, range1, BAT_GRID_ON))
       j = cursor.fetchone()[0]
       if i == 2 and j >= 3 :
          logging.debug("Battery voltage is reaching low levels, grid switch activated ...")
          r = requests.post('http://rpi3:48211/switch.json',"ON")

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=16)
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var1 > 0 and var9 > %s", (range2, range1, BAT_GRID_OFF))
       i = cursor.fetchone()[0]
       cursor.execute("select count(*) from axpert.QPIRI where created >= %s and created < %s and var17 = 2", (range2, range1))
       j = cursor.fetchone()[0]
       if i >= 15 and j >= 15 :
          logging.debug("SBU mode is detected and grid is on, switching to USB mode ...")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"POP00")
       else:
             range1 = dt.datetime.now()
             range2 = range1 - dt.timedelta(hours=0, minutes=16)
             cursor.execute("select count(*) from axpert.QMOD where created >= %s and created < %s and var1 = %s", (range2, range1, "L"))
             i = cursor.fetchone()[0]
             cursor.execute("select count(*) from axpert.QPIRI where created >= %s and created < %s and var17 = 2", (range2, range1))
             j = cursor.fetchone()[0]
             if i >= 15 and j >= 15 :
                  logging.debug("SBU line mode is detected, switching to USB mode ...")
                  r = requests.post('http://127.0.0.1:48211/axpert.json',"POP00")



#############################

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=4)
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var9 >= %s", (range2, range1, BAT_FULL))
       i = cursor.fetchone()[0]
       cursor.execute("SELECT var15 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       j = statistics.median(sum(map(list,cursor.fetchall()), []))
       cursor.execute("SELECT var17 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       k = statistics.median(sum(map(list,cursor.fetchall()), []))
       if i >= 3 and j > 10 :
          r = requests.post('http://rpi3:48211/switch.json',"OFF")
          if k == 0 :
               logging.debug("Battery is almost fully charged, switching to SBU mode ...")
               r = requests.post('http://127.0.0.1:48211/axpert.json',"POP02")
          else:
               logging.debug("Battery is almost fully charged, max. charging current set to 10A ...")
               r = requests.post('http://127.0.0.1:48211/axpert.json',"MCHGC010;POP02")

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=6)
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var10 = 0 and var16 = 0 and var9 >= %s", (range2, range1, BAT_FULL))
       i = cursor.fetchone()[0]
       cursor.execute("SELECT var11 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       j = statistics.median(sum(map(list,cursor.fetchall()), []))
       if i >= 5 and j > BAT_CVV_LOW :
          logging.debug("Battery is fully charged, bulk and floating voltage set to safe values ...")
          r = requests.post('http://rpi3:48211/switch.json',"OFF")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"MCHGC010"+";PBFT"+str(BAT_FLT_LOW)+";PCVV"+str(BAT_CVV_LOW)+";PBDV"+str(math.floor(BAT_FLT_LOW)))

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=4)
       cursor.execute("select count(*) from axpert.BMS where created >= %s and created < %s and var14 = 0", (range2, range1))
       i = cursor.fetchone()[0]
       cursor.execute("SELECT var11 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       j = statistics.median(sum(map(list,cursor.fetchall()), []))
       if i >= 3 and j > BAT_CVV_LOW :
          logging.debug("Battery is fully charged, bulk and floating voltage set to safe values ....")
          r = requests.post('http://rpi3:48211/switch.json',"OFF")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"MCHGC010"+";PBFT"+str(BAT_FLT_LOW)+";PCVV"+str(BAT_CVV_LOW)+";PBDV"+str(math.floor(BAT_FLT_LOW)))

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=4)
       cursor.execute("select avg(var24),avg(var25),avg(var26),avg(var27),avg(var28),avg(var29),avg(var30),avg(var31),avg(var32),avg(var33),avg(var34),avg(var35),avg(var36),avg(var37),avg(var38),avg(var39) from axpert.BMS where created >= %s and created < %s", (range2, range1))
       i = cursor.fetchone()
       cursor.execute("SELECT var11 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       j = statistics.median(sum(map(list,cursor.fetchall()), []))
       if not i[0] == None :
          if max(i) >= BAT_CELL_MAX :
             if j > BAT_CVV_LOW :
                     a = BAT_CVV_LOW
                     b = BAT_FLT_LOW
             else:
                     a = j - 0.1            # Find safe value if default value is not optimal and BMS protection fails
                     b = a - 0.1
             logging.debug("Maximum voltage of battery cell is going to be exceeded, bulk and floating voltage set to safe values ...")
             r = requests.post('http://rpi3:48211/switch.json',"OFF")
             r = requests.post('http://127.0.0.1:48211/axpert.json',"MCHGC010"+";PBFT"+str(b)+";PCVV"+str(a)+";PBDV"+str(math.floor(b)))

       cursor.execute("SELECT var15 FROM axpert.QPIRI ORDER BY created DESC LIMIT 3")
       i = statistics.median(sum(map(list,cursor.fetchall()), []))
       if dt.datetime.now().hour == 3 and i < 40 :
          logging.debug("Bulk, floating voltage and max. charging current set to optimal values ...")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"PCVV"+str(BAT_CVV_HIGH)+";PBFT"+str(BAT_FLT_HIGH)+";MCHGC040"+";PBDV"+str(math.floor(BAT_FLT_HIGH)))

       range1 = dt.datetime.now()
       range2 = range1 - dt.timedelta(hours=0, minutes=6)
       cursor.execute("SELECT var23 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       i = statistics.median(sum(map(list,cursor.fetchall()), []))
       cursor.execute("select count(*) from axpert.QPIGS where created >= %s and created < %s and var9 >= %s", (range2, range1, str(i)))
       j = cursor.fetchone()[0]
       cursor.execute("SELECT var17 FROM axpert.QPIRI ORDER BY created DESC LIMIT 6")
       k = statistics.median(sum(map(list,cursor.fetchall()), []))
       if j >= 5 and k == 0 :
          logging.debug("Optimal voltage reached switching from USB to SBU mode ...")
          r = requests.post('http://rpi3:48211/switch.json',"OFF")
          r = requests.post('http://127.0.0.1:48211/axpert.json',"POP02")

       cursor.close()
       conn.close()

if __name__ == '__main__':
    main()
