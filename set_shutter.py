#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import sys
 


class shutter:

    # get the corresponding value from range 0 ~ 180 degrees to min ~ max duty cycle
    def mapValue( self, value, fromLow, fromHigh, toLow, toHigh):
        return (toHigh-toLow)*(value-fromLow) / (fromHigh - fromLow) + toLow
        
    # rotate the servo to a specific angle
    def servoWrite(self, angle):
        # make sure it doesn't go beyond the angle the servo motor can rotate
        if (angle < self.MIN_ANGLE):
            angle = self.MIN_ANGLE
        elif (angle > self.MAX_ANGLE):
            angle = self.MAX_ANGLE
        self.pwmChannel.ChangeDutyCycle(self.mapValue(angle, 0, 180, self.SERVO_MIN_DUTY, self.SERVO_MAX_DUTY))
        
    def loop(self):
        while True:
            # rotate from 0 ~ 180 degrees
            for dc in range(0, 181, 1):
                self.servoWrite(dc)
                time.sleep(0.01)
            time.sleep(0.5)
            # rotate from 180 ~ 0 degrees
            for dc in range(180, -1, -1):
                self.servoWrite(dc)
                time.sleep(0.01)
            time.sleep(0.5)
            
        
    def setAperture(self, percent):
        
        angle = int(float(percent) * 0.01 * 180)
        print(angle)
        
        # Silently ignored if above some angle for some reason
        if(angle > 170):
            angle = 170
            
        self.servoWrite(angle)
        time.sleep(1)
        self.pwmChannel.stop()

    def __init__(self):

        self.ERROR_OFFSET = 0.5
        self.SERVO_MIN_DUTY = 2.5 + self.ERROR_OFFSET # duty cycle for 0 degrees
        self.SERVO_MAX_DUTY = 12.5 + self.ERROR_OFFSET # duty cycle for 180 degrees
        self.MIN_ANGLE = 0 # degrees
        self.MAX_ANGLE = 180 # degrees
        self.servoPin = 12

        #initialize GPIO Pin
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(self.servoPin, GPIO.OUT)
        GPIO.output(self.servoPin, GPIO.LOW)
        
        # initialize PWM in defined GPIO Pin
        self.pwmChannel = GPIO.PWM(self.servoPin, 50)
        self.pwmChannel.start(0)

    def __del__(self):
        self.pwmChannel.stop()
        GPIO.cleanup()

     
if __name__ == '__main__':
    if (not (len(sys.argv) == 2 and int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 100)):
        print("Must provide integer percent closed 0-100")
        exit()

    shutter = shutter()

    shutter.setAperture(sys.argv[1])