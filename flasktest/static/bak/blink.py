#!/usr/bin/env python
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime



GPIO.setmode(GPIO.BCM)
current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
str_current_datetime = str(current_datetime)
with open('logled.txt', 'a') as file:
	file.write(str_current_datetime + 'led on moisture >22728')



valve = 17
GPIO.setup(valve, GPIO.OUT)
GPIO.output(valve, True)
sleep(3600)
GPIO.output(valve, False)

GPIO.cleanup()

current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
str_current_datetime = str(current_datetime)
with open('logled.txt', 'a') as file:
        file.write(str_current_datetime + ' led off\n')
