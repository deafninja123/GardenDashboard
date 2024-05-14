#!/usr/bin/env python
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime



GPIO.setmode(GPIO.BCM)
current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
str_current_datetime = str(current_datetime)
with open('log.txt', 'a') as file:
	file.write(str_current_datetime + ' 30sec\n')



valve = 17
GPIO.setup(valve, GPIO.OUT)
GPIO.output(valve, True)
sleep(30)
GPIO.output(valve, False)

GPIO.cleanup()

current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
str_current_datetime = str(current_datetime)
with open('log.txt', 'a') as file:
	file.write(str_current_datetime + ' 30sec ended\n')









