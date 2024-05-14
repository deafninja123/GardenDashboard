import os
import re
import serial
import time
import subprocess
from datetime import datetime

ser = serial.Serial('/dev/ttyS0', baudrate=115200, timeout=1)

def send_command(command):
    ser.write(command.encode())
    time.sleep(0.1)
    response = ser.readline().decode().strip()
    return response

# Example: Send AT command
response = send_command('AT\r\n')
print(f'Response: {response}')

response = send_command('AT+NETWORKID?\r\n')
print(f'Response: {response}')

response = send_command('AT+ADDRESS=2\r\n')
print(f'Response: {response}')

response = send_command('AT+PARAMETER?\r\n')
print(f'Response: {response}')
while True:
	ser.reset_input_buffer()
	recieved1 = ""
	time.sleep(5)
	recieved1 = ser.readline().decode().strip()
	print(f'Response: {recieved1}')
#recieved1 = ser.write(ser.readline().decode().strip())
#print(b'recieved1')
	if recieved1:
		match = re.search(r'zz(\d+),', recieved1)
	# Check if a match is found
		if match:
			isolated_part = match.group(1)
			print("Isolated Part:", isolated_part)
			current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
			str_current_datetime = str(current_datetime)
			print(str_current_datetime + " " + isolated_part)
			print("Current Working Directory:", os.getcwd())
			with open('/home/mike/flasktest/static/logled.txt', 'a') as file:
				file.write(str_current_datetime + " " + isolated_part +"\n")
				file.write(os.getcwd() + "\n")
			if (int(isolated_part) > 16000):
			# Specify the Python script you want to run
				script_to_run = "/home/mike/flasktest/static/ValveOn60min.py"
				# Run the script if ground is dry
				try:
				    print("ground is dry")
				    print("running ValveOn60min.py")
				    subprocess.run(["python", script_to_run], check=True)
				except subprocess.CalledProcessError as e:
				    print(f"Error: {e}")
			elif ((int(isolated_part) <= 16000) and (int(isolated_part) >= 12000)):
				script_to_run = "/home/mike/flasktest/static/ValveOn10min.py"
                                # Run the script if the ground is a little dry
                                try:
                                    print("ground is a little dry")
                                    print("running ValveOn10min.py")
                                    subprocess.run(["python", script_to_run], check=True)
                                except subprocess.CalledProcessError as e:
                                    print(f"Error: {e}")
			else:
			       print(f"ground is wet")
		else:
	            print("Pattern not found in the string.")

ser.close()
