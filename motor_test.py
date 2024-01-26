#######################################
# Copyright (c) 2021 Maker Portal LLC
# Author: Joshua Hrisko
#######################################
#
# NEMA 17 (17HS4023) Raspberry Pi Tests
# --- rotating the NEMA 17 to test
# --- wiring and motor functionality
#
#
#######################################
#
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
import time

################################
# RPi and Motor Pre-allocations
################################
#
#define GPIO pins
direction= 22 # Direction (DIR) GPIO Pin
step = 23 # Step GPIO Pin
EN_pin = 24 # enable pin (LOW to enable)

dir2 = 25
step2 = 8
EN_pin2 = 7

# Declare a instance of class pass GPIO pins numbers and the motor type
mymotortest = RpiMotorLib.A4988Nema(direction, step, (21,21,21), "DRV8825")
mot2 = RpiMotorLib.A4988Nema(dir2, step2, (21, 21, 21), "DRV8825")
GPIO.setup(EN_pin,GPIO.OUT) # set enable pin as output
GPIO.setup(EN_pin2,GPIO.OUT)

###########################
# Actual motor control
###########################
#
GPIO.output(EN_pin,GPIO.LOW) # pull enable to low to enable motor
GPIO.output(EN_pin2,GPIO.LOW)
while (True):
    mot2.motor_go(False, # True=Clockwise, False=Counter-Clockwise
                    "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
                    200, # number of steps
                    .0005, # step delay [sec]
                    False, # True = print verbose output 
                    .05) # initial delay [sec]
    mymotortest.motor_go(False, # True=Clockwise, False=Counter-Clockwise
                        "Full" , # Step type (Full,Half,1/4,1/8,1/16,1/32)
                        200, # number of steps
                        .0005, # step delay [sec]
                        False, # True = print verbose output 
                        .05) # initial delay [sec]
    time.sleep(1)

GPIO.cleanup() # clear GPIO allocations after run