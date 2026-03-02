# test connection from pico to uart lora module and try to send messages.
from machine import UART, Pin
import time
import sys

uart = UART(0,baudrate=115200,tx=Pin(0),rx=Pin(1))
led = Pin('LED', Pin.OUT)
SoilCapSensor = machine.ADC(0)
destination = 0
localaddress = 9
msg=""
msgtype=""
msgid=0

def send_at_command(command):
    uart.write(command + b'\r\n')
    time.sleep(2)  # Adjust delay based on your module's response time

def read_response():
    response = b''
    while uart.any():
        response += uart.read(1)
    return response.decode('utf-8')

#response = UART.readline()
#print(f'Response: {UART.readline()}')
'''


send_at_command(b'AT+SEND=00')
response = read_response()
print(f'Response: {response}')
response = read_response()
print(f'Response: {response}')
#response = uart.readline()
#print(f'Response: {response}')
# Example: Send AT commands and read responses
send_at_command(b'AT')
response = read_response()
print(f'Response: {response}')

    
send_at_command(b'AT+PARAMETER=12,7,1,4')
response = read_response()
print(f'Response: {response}')

send_at_command(b'+RCV')
response = read_response()
print(f'Response: {response}')

send_at_command(b'AT+PARAMETER?')
response = read_response()
print(f'Response: {response}')

send_at_command(b'AT+ADDRESS?')
response = read_response()
print(f'Response: {response}')

send_at_command(b'AT+ADDRESS?')
response = read_response()
print(f'Response: {response}')

send_at_command(b'AT+NETWORKID?')
response = read_response()
print(f'Response: {response}')
  
'''
send_at_command(b'AT+NETWORKID=0')  #network must be set to 0 to work with sx1276


send_at_command(b'AT+PARAMETER?')
response = read_response()
print(f'Response: {response}')

send_at_command(b'AT+SEND=00,10,HELLO')
response = read_response()
print(f'Response: {response}')
while True:
    CapVal = SoilCapSensor.read_u16()
    destination = 2
    msgtype="zz" #soilMoistureSensor reading
    msg=str(destination)+ str(localaddress) + str(msgid) + str(msgtype) + str(CapVal)
    at_command = "AT+SEND=" + str(destination) + "," + str(len(msg)) + "," + str(msg)
    at_command_bytes = at_command.encode()
    #sys.getsizeof(str(msg))
    send_at_command(at_command_bytes)
    
    response = read_response()
    print(f'Response1: {response}')
    
    print(f'strmsg: {str(len(msg))}')
    print(f'Response: {str(CapVal)}')
    
    
    print(f'msg: {at_command_bytes}')
    #time.sleep(300)
    time.sleep(2) #1hour

#machine.reset()

'''
led.on()
uart.write("AT+SEND=50,5,HtELLO\r")
led.off()

led.on()
utime.sleep_ms(1000)
led.off()

uart.write("AT\r")

if uart.any() == True:
        buf=uart.read(3)
        print(buf)
        led.on()
        utime.sleep_ms(1000)
        led.off()
     
while True:
    if uart.any() == True:
        buf=uart.read(3)
        print(buf)

'''










































