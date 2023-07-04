#!/usr/bin/env python3
import time
import datetime
import os
import RPi.GPIO as GPIO
import math


class thermistor:

    #  read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(self, adcnum, clockpin, mosipin, misopin, cspin):
        if (adcnum > 7) or (adcnum < 0):
            return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)  # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3  # we only need to send 5 bits here
        for i in range(5):
            if commandout & 0x80:
                GPIO.output(mosipin, True)
            else:
                GPIO.output(mosipin, False)
            commandout <<= 1
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(clockpin, True)
            GPIO.output(clockpin, False)
            adcout <<= 1
            if GPIO.input(misopin):
                adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1  # first bit is 'null' so drop it
        return adcout

    def adc_to_deg_f(self, value):
        volts = (value * 3.3) / 1024  # calculate the voltage
        ohms = ((1 / volts) * 3300) - 1000  # calculate the ohms of the thermististor

        lnohm = math.log1p(ohms)  # take ln(ohms)

        # a, b, & c values from http://www.thermistor.com/calculators.php
        # using curve R (-6.2%/C @ 25C) Mil Ratio X
        # a =  0.002197222470870
        # b =  0.000161097632222
        # c =  0.000000125008328

        a = 0.000570569668444
        b = 0.000239344111326
        c = 0.000000047282773

        # Steinhart Hart Equation
        # T = 1/(a + b[ln(ohm)] + c[ln(ohm)]^3)

        t1 = b * lnohm  # b[ln(ohm)]

        c2 = c * lnohm  # c[ln(ohm)]

        t2 = math.pow(c2, 3)  # c[ln(ohm)]^3

        temp = 1 / (a + t1 + t2)  # calcualte temperature

        tempc = temp - 273.15 - 4  # K to C

        tempf = tempc * 9 / 5 + 32
        # the -4 is error correction for bad python math

        # print out info
        # print ("%4d/1023 => %5.3f V => %4.1f ohms  => %4.1f K => %4.1f C  => %4.1f F" % (value, volts, ohms, temp, tempc, tempf))

        return tempf

    def get_temp_deg_f(self, sensor):
        value = self.readadc(
            sensor, self.SPICLK, self.SPIMOSI, self.SPIMISO, self.SPICS
        )
        if value != 0:
            return self.adc_to_deg_f(value)
        else:
            return 0

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # change these as desired - they're the pins connected from the
        # SPI port on the ADC to the Cobbler
        self.SPICLK = 18
        self.SPIMISO = 23
        self.SPIMOSI = 24
        self.SPICS = 25

        # set up the SPI interface pins
        GPIO.setup(self.SPIMOSI, GPIO.OUT)
        GPIO.setup(self.SPIMISO, GPIO.IN)
        GPIO.setup(self.SPICLK, GPIO.OUT)
        GPIO.setup(self.SPICS, GPIO.OUT)

    def __del__(self):
        GPIO.cleanup()


if __name__ == "__main__":
    therm = thermistor()
    print("Sensor 1, ", therm.get_temp_deg_f(0), "f")
    print("Sensor 2, ", therm.get_temp_deg_f(1), "f")
