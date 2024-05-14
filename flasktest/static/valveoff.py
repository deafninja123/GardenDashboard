#!/usr/bin/env python
import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)

valve = 17
GPIO.setup(valve, GPIO.OUT)
GPIO.output(valve, False)













