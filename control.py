#!/usr/bin/env python
import time
import datetime
import os
import RPi.GPIO as GPIO
import math
import sqlite3

GPIO.setmode(GPIO.BCM)
DEBUG = 0

targettemp = 240
PWMPIN = 13

# Set PWM of fan output port based on current steady state and target temp F
def setFan(temp, target):
	if (temp < target):
		GPIO.output(PWMPIN, True)
	else:
		GPIO.output(PWMPIN, False)


# Get steady state reading of the smokebox temp
def readTemp():
	
    conn=sqlite3.connect('/home/pi/templog.db')
    curs=conn.cursor()
    #curs.execute("INSERT INTO temps (sensnum,temp) values((?), (?))", (sensnum,temp,))
    curs.execute("SELECT max(timestamp), sensnum, temp FROM (SELECT * FROM temps WHERE sensnum = 0)")
    temp = curs.fetchone()[2]
    if (DEBUG == 1):
      print curs.fetchone()

    conn.close()
    setFan(temp,targettemp)

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
