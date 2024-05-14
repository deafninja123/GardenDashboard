import re
import serial
import time
import subprocess
from datetime import datetime
while True:
	recieved1 = ""
	time.sleep(1)
	recieved1 = input()
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
			with open('static/logled.txt', 'a+') as file:
				file.write(str_current_datetime + " " + isolated_part +"\n")
			if (int(isolated_part) > 22728):
			# Specify the Python script you want to run
				#script_to_run = "static/ValveOn60min.py"
				# Run the script
				try:
				    print("ground is dry")
				    print("running ValveOn60min.py")
				    #subprocess.run(["python", script_to_run], check=True)
				except subprocess.CalledProcessError as e:
				    print(f"Error: {e}")
			else:
			       print(f"ground is wet")
		else:
	            print("Pattern not found in the string.")

ser.close()
