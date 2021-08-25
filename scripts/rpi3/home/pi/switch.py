#!/usr/bin/python
import smbus
import time
import datetime as dt
import RPi.GPIO as GPIO
import logging
import math

FILE_PATH1   = "/home/pi/switch.json"
SWITCH_PORT   = 26
DEBUG_FLAG    = False

def main():

 try:
    if DEBUG_FLAG:
          logging.basicConfig(filename='/run/switch.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SWITCH_PORT, GPIO.OUT)

    while True:
          time.sleep(30)
          tempfile = open(FILE_PATH1)
          command = tempfile.read()
          tempfile.close()
          if command == "OFF":
             logging.debug("Switch off grid...")
             GPIO.output(SWITCH_PORT, GPIO.HIGH)
          else:
             logging.debug("Switch on grid...")
             GPIO.output(SWITCH_PORT, GPIO.LOW)

 finally:
       GPIO.cleanup()

if __name__=="__main__":
   main()

