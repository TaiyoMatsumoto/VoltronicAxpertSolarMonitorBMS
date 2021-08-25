#!/usr/bin/python

import json
import requests
import MySQLdb
import time, sys, string
import sqlite3
import datetime
import signal
import MySQLdb
import logging
import os
from pathlib import Path

DEBUG_FLAG     = True
FILE_PATH1   = "/run/SDM230.lock"

def main():

        IsReachable=True
        try:
            r = requests.get('http://<MBMD_server_ip>:8080/api/avg')
            r.json()
            data = json.loads(r.text)
        except:
            IsReachable=False

        conn = MySQLdb.connect(host="<SQL_server_ip>",user="<admin>",passwd="<password>",db="axpert")
        cursor = conn.cursor()

        if IsReachable:
               SQL_statement = ( "INSERT INTO SDM230(var1,var2,var3,var4,var5,var6,var7,var8,var9,var10,var11,var12,var13) VALUES ('%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f','%f')" % ( float(data['SDM2301.1']['ApparentPower']), float(data['SDM2301.1']['Cosphi']), float(data['SDM2301.1']['Current']), float(data['SDM2301.1']['Export']), float(data['SDM2301.1']['Frequency']), float(data['SDM2301.1']['Import']), float(data['SDM2301.1']['PhaseAngle']), float(data['SDM2301.1']['Power']), float(data['SDM2301.1']['ReactiveExport']), float(data['SDM2301.1']['ReactiveImport']), float(data['SDM2301.1']['ReactivePower']), float(data['SDM2301.1']['Sum']), float(data['SDM2301.1']['Voltage']) ))
               try:
                    cursor.execute(SQL_statement)
                    conn.commit()
                    os.remove(FILE_PATH1)
               except:
                    conn.rollback()
        else:
               fileExist = Path(FILE_PATH1)
               if not fileExist.is_file():
                       open(FILE_PATH1, 'w+')
                       if DEBUG_FLAG:
                          logging.basicConfig(filename='/var/log/SDM230.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
                          logging.debug("SDM230 meter is not reachable")


        cursor.close()
        conn.close()

if __name__ == '__main__':
    main()
