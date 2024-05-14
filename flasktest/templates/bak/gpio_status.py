#!/usr/bin/env python3

from gpiozero import DigitalInputDevice
from time import sleep

# Define the GPIO pin number
PIN_NUMBER = 17

# Create a DigitalInputDevice object
pin = DigitalInputDevice(PIN_NUMBER)

# Read and print the status of the pin every second
while True:
    print("GPIO Pin {} status: {}".format(PIN_NUMBER, pin.value))
    sleep(1)
