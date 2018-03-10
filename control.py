#!/usr/bin/env python
import time
import datetime
import os
import RPi.GPIO as GPIO
import math
import sqlite3
import re

GPIO.setmode(GPIO.BCM)
DEBUG = 1

#targettemp = 240
PWMPIN = 13

path='/home/pi/Smoker-Controller'

def readSetPoint():
    str = open(path+'/web/formdata','r').read()
    match = re.search('\"sensorset\":\"(\d+)',str)
    return int(match.group(1))

# Set PWM of fan output port based on current steady state and target temp F
def setFan(temp, target):
    if (DEBUG == 1):
        print temp, target
    if (temp < target):
        GPIO.output(PWMPIN, True)
    else:
        GPIO.output(PWMPIN, False)


# Get steady state reading of the smokebox temp
def readTemp():
	
    conn=sqlite3.connect(path+'/templog.db')
    curs=conn.cursor()
    curs.execute("SELECT max(timestamp), sensnum, temp FROM (SELECT * FROM temps WHERE sensnum = 0)")
    temp = curs.fetchone()[2]
    if (DEBUG == 1):
      print "db", temp

    conn.close()
    setFan(temp,readSetPoint())

def testloop():
	while True:
		readTemp()
	        GPIO.output(PWMPIN,True)
	        time.sleep(1)
	        GPIO.output(PWMPIN,False)
        	time.sleep(1)

GPIO.setup(PWMPIN,GPIO.OUT)
#testloop()
readTemp()
#GPIO.cleanup()
