#!/usr/bin/env python
import time
import datetime
import os
import RPi.GPIO as GPIO
import math
import sqlite3
import statistics

GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
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
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def temp_calc(value):
    volts = (value * 3.3) / 1024 #calculate the voltage
    ohms = ((1/volts)*3300)-1000 #calculate the ohms of the thermististor

    lnohm = math.log1p(ohms) #take ln(ohms)

    #a, b, & c values from http://www.thermistor.com/calculators.php
    #using curve R (-6.2%/C @ 25C) Mil Ratio X
    #a =  0.002197222470870
    #b =  0.000161097632222
    #c =  0.000000125008328

    a =  0.000570569668444 
    b =  0.000239344111326 
    c =  0.000000047282773 

    #Steinhart Hart Equation
    # T = 1/(a + b[ln(ohm)] + c[ln(ohm)]^3)

    t1 = (b*lnohm) # b[ln(ohm)]

    c2 = c*lnohm # c[ln(ohm)]

    t2 = math.pow(c2,3) # c[ln(ohm)]^3

    temp = 1/(a + t1 + t2) #calcualte temperature

    tempc = temp - 273.15 - 4 #K to C

    tempf = tempc*9/5 + 32
    # the -4 is error correction for bad python math

    #print out info
    #print ("%4d/1023 => %5.3f V => %4.1f ohms  => %4.1f K => %4.1f C  => %4.1f F" % (value, volts, ohms, temp, tempc, tempf))

    return tempf
    
def log_temperature(sensnum,temp):

    conn=sqlite3.connect('/home/pi/Smoker-Controller/templog.db')
    curs=conn.cursor()
    curs.execute("INSERT INTO temps (sensnum,temp) values((?), (?))", (sensnum,temp,))

    # commit the changes
    conn.commit()

    conn.close()


# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25


# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

for sensor in xrange(0,3):
                samples = []
		value = 0
		temp = 0 
                for x in range(5):
                    value = readadc(sensor, SPICLK, SPIMOSI, SPIMISO, SPICS)
                    time.sleep(0.2)
                    if value != 0:
                        samples.append(int(temp_calc(value)))
                std=99
                print "samples:", samples
                if len(samples) == 5:
                    mean = statistics.mean(samples)

                    std=statistics.stdev(samples)
                
                if std < 2.0:    
                    if DEBUG:
		        print "mean:", mean, sensor
		    log_temperature(sensor, mean)
                else:
                    if DEBUG:
                        print "invalid. L,std,sensor,samples:",len(samples), std, sensor, samples
		    log_temperature(sensor, 0)

GPIO.cleanup()
