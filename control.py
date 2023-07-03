#!/usr/bin/env python
import time
import datetime
import os
import RPi.GPIO as GPIO
import math
import sqlite3
import re
import set_shutter
from influxdb import InfluxDBClient


class control:

    def readAperture(self):
        str = open(self.path+'/web/formdata','r').read()
        match = re.search('\"apertureset\":\"(\d+)',str)

        choke = int(match.group(1))
        if (self.DEBUG == 1):
            print choke
            
        measurement = 'choke'
        fields = {'value': choke}

        # Create an InfluxDB measurement
        data = [
            {
                'measurement': measurement,
                'fields': fields
            }
        ]

        # Write the data to InfluxDB
        self.client.write_points(data)
     
        return choke

    def readSetPoint(self):
        str = open(self.path+'/web/formdata','r').read()
        match = re.search('\"sensorset\":\"(\d+)',str)
        setpoint = int(match.group(1))

        measurement = 'setpoint'
        fields = {'value': setpoint}

        # Create an InfluxDB measurement
        data = [
            {
                'measurement': measurement,
                'fields': fields
            }
        ]

        # Write the data to InfluxDB
        self.client.write_points(data)

        return setpoint

    # Set PWM of fan output port based on current steady state and target temp F
    def setFan(self, temp, target):
        if (self.DEBUG == 1):
            print temp, target

        fan_enable = temp < target

        GPIO.output(self.PWMPIN, fan_enable)

        measurement = 'fan_enable'
        fields = {'value': fan_enable}

        # Create an InfluxDB measurement
        data = [
            {
                'measurement': measurement,
                'fields': fields
            }
        ]

        # Write the data to InfluxDB
        self.client.write_points(data)


    # Get steady state reading of the smokebox temp
    def readTemp(self):
        
        conn=sqlite3.connect(self.path+'/templog.db')
        curs=conn.cursor()
        curs.execute("SELECT max(timestamp), sensnum, temp FROM (SELECT * FROM temps WHERE sensnum = 0)")
        temp = curs.fetchone()[2]
        if (self.DEBUG == 1):
            print "db", temp

        conn.close()
        self.setFan(temp,self.readSetPoint())
        set_shutter.setAperture(self.readAperture())

    def testloop(self):
        while True:
            self.readTemp()
            GPIO.output(self.PWMPIN,True)
            time.sleep(1)
            GPIO.output(self.PWMPIN,False)
            time.sleep(1)

    def __init__(self):
        self.client = InfluxDBClient(host='localhost', port=8086)
        self.db_name = 'tempcontroler'
        self.client.create_database(self.db_name)
        self.client.switch_database(self.db_name)

        GPIO.setmode(GPIO.BCM)
        self.DEBUG = 1

        #targettemp = 240
        self.PWMPIN = 13

        self.path='/home/pi/Smoker-Controller'

        GPIO.setup(self.PWMPIN,GPIO.OUT)
        #testloop()
        self.readTemp()
        self.readAperture()
        #GPIO.cleanup()

if __name__ == "__main__":
    control()
