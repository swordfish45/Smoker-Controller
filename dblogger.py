#!/usr/bin/env python3
import time
import datetime
import os
import RPi.GPIO as GPIO
import math
import sqlite3
from influxdb import InfluxDBClient
import thermistor
import logging


class dblogger:
    def log_temperature_sqlite(self, sensnum, temp):

        conn = sqlite3.connect("/home/pi/Smoker-Controller/templog.db")
        curs = conn.cursor()
        curs.execute(
            "INSERT INTO temps (sensnum,temp) values((?), (?))", (sensnum, temp)
        )

        # commit the changes
        conn.commit()

        conn.close()

    def log_temperature_influx(self, sensnum, temp):
        # Define the temperature data
        measurement = "temperature"
        tags = {"sensor": sensnum}
        fields = {"value": temp}

        # Create an InfluxDB measurement
        data = [{"measurement": measurement, "tags": tags, "fields": fields}]

        # Write the data to InfluxDB
        self.client.write_points(data)

    def __init__(self):
        logging.getLogger("control")

        self.therm = thermistor.thermistor()

        logging.info(f"InfluxDBClient localhost 8086 db tempcontroler")

        self.client = InfluxDBClient(host="localhost", port=8086)
        self.db_name = "tempcontroler"
        self.client.create_database(self.db_name)
        self.client.switch_database(self.db_name)

    def log_temps(self):
        for sensor in range(0, 3):
            temp = self.therm.get_temp_deg_f(sensor)
            self.log_temperature_sqlite(sensor, int(temp))
            self.log_temperature_influx(sensor, float(temp))


if __name__ == "__main__":
    lgr = logger()
    lgr.log_temps()
