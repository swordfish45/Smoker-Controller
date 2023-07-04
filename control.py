#!/usr/bin/env python3
import time
import datetime
import os
import RPi.GPIO as GPIO
import math
import sqlite3
import re
import shutter
import dblogger
import logging
import sys
from influxdb import InfluxDBClient


class control:
    def readAperture(self):
        str = open(self.path + "/web/formdata", "r").read()
        match = re.search('"apertureset":"(\d+)', str)

        choke = int(match.group(1))

        logging.info(f"readAperture choke {choke}")

        measurement = "choke"
        fields = {"value": choke}

        # Create an InfluxDB measurement
        data = [{"measurement": measurement, "fields": fields}]

        # Write the data to InfluxDB
        self.client.write_points(data)

        return choke

    def readSetPoint(self):
        setpt = open(self.path + "/web/formdata", "r").read()
        match = re.search('"sensorset":"(\d+)', setpt)
        setpoint = int(match.group(1))

        measurement = "setpoint"
        fields = {"value": setpoint}

        # Create an InfluxDB measurement
        data = [{"measurement": measurement, "fields": fields}]

        # Write the data to InfluxDB
        self.client.write_points(data)

        return setpoint

    # Set PWM of fan output port based on current steady state and target temp F
    def setFan(self, temp, target):

        logging.info(f"setFan temp {temp},  target {target}")

        fan_enable = temp < target

        GPIO.output(self.PWMPIN, fan_enable)

        measurement = "fan_enable"
        fields = {"value": fan_enable}

        # Create an InfluxDB measurement
        data = [{"measurement": measurement, "fields": fields}]

        # Write the data to InfluxDB
        self.client.write_points(data)

    # Get steady state reading of the smokebox temp
    def contol_temps(self):

        conn = sqlite3.connect(self.path + "/templog.db")
        curs = conn.cursor()
        curs.execute(
            "SELECT max(timestamp), sensnum, temp FROM (SELECT * FROM temps WHERE sensnum = 0)"
        )
        temp = curs.fetchone()[2]

        logging.info(f"Latest smoke temp {temp}")

        conn.close()
        self.setFan(temp, self.readSetPoint())
        self.shutter.setAperture(self.readAperture())

    def testloop(self):
        while(True):
            self.contol_temps()
            GPIO.output(self.PWMPIN, True)
            time.sleep(1)
            GPIO.output(self.PWMPIN, False)
            time.sleep(1)

    def main_loop(self):
        while(True):
            self.dblogger.log_temps()
            self.contol_temps()
            time.sleep(10)
        # todo /home/pi/Smoker-Controller/dbcleanup.sh

    def __init__(self):
        logging.getLogger("control")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("/home/pi/Smoker-Controller/control.log"),
                logging.StreamHandler()
            ]
)

        self.shutter = shutter.shutter()
        self.dblogger = dblogger.dblogger()

        self.client = InfluxDBClient(host="localhost", port=8086)
        self.db_name = "tempcontroler"
        self.client.create_database(self.db_name)
        self.client.switch_database(self.db_name)

        GPIO.setmode(GPIO.BCM)
        self.DEBUG = 1

        # targettemp = 240
        self.PWMPIN = 13

        self.path = "/home/pi/Smoker-Controller"

        GPIO.setup(self.PWMPIN, GPIO.OUT)
        # testloop()

        # GPIO.cleanup()


if __name__ == "__main__":
    contr = control()
    contr.main_loop()
