from flask import Flask, render_template
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


app = Flask(__name__, static_url_path='/static')

# Set up GPIO


# Route to read GPIO pin status
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_ValveOff')
def valve_off():
	GPIO.setmode(GPIO.BCM)
	valve = 17
	GPIO.setup(valve, GPIO.OUT)
	GPIO.output(valve, False)
	return "Valve has been turned off"


@app.route('/run_ValveOn10min')
def ValveOn10min():
        GPIO.setmode(GPIO.BCM)
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        str_current_datetime = str(current_datetime)
        with open('/home/mike/flasktest/static/log.txt', 'a') as file:
                file.write(str_current_datetime + ' 10min\n')
        valve = 17
        GPIO.setup(valve, GPIO.OUT)
        GPIO.output(valve, True)
        sleep(600)
        GPIO.output(valve, False)
        GPIO.cleanup()
        return "Valve is on for 10 min"


@app.route('/run_ValveOn60min')
def ValveOn60min():
	GPIO.setmode(GPIO.BCM)
	current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
	str_current_datetime = str(current_datetime)
	with open('/home/mike/flasktest/static/log.txt', 'a') as file:
		file.write(str_current_datetime + ' 60min\n')
	valve = 17
	GPIO.setup(valve, GPIO.OUT)
	GPIO.output(valve, True)
	sleep(3600)
	GPIO.output(valve, False)
	GPIO.cleanup()
	return "Valve is on for 1 hour"

@app.route('/run_ValveOn')
def ValveOn():
	GPIO.setmode(GPIO.BCM)
	current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
	str_current_datetime = str(current_datetime)
	with open('/home/mike/flasktest/static/log.txt', 'a') as file:
		file.write(str_current_datetime + ' 30sec\n')
	valve = 17
	GPIO.setup(valve, GPIO.OUT)
	GPIO.output(valve, True)
	sleep(30)
	GPIO.output(valve, False)
	GPIO.cleanup()
	return "ok"

@app.route('/run_clearlog')
def clearlog():
	with open('/home/mike/flasktest/static/log.txt', 'r') as file:
	# Read all lines from the file
		line = file.readline().strip()
	# Discard the first entry (i.e., the first line)
	#lines.pop(0)
	# Open the file for writing (which clears the file)
	with open('/home/mike/flasktest/static/logs/log.txt', 'a') as dest:
	# Write the remaining lines back to the file
		dest.write(line + '\n')
	with open('/home/mike/flasktest/static/log.txt', 'r') as file:
		lines = file.readlines()
	if lines:
		lines.pop(0)
	with open('/home/mike/flasktest/static/log.txt', 'w') as dest:
	# Write the remaining lines back to the file
		dest.writelines(lines)
	return "ok"


@app.route('/run_clearmoisturelog')
def clearmoisturelog():
        with open('/home/mike/flasktest/static/logled.txt', 'r') as file:
        # Read all lines from the file
                line = file.readline().strip()
        # Open the file for writing (which clears the file)
        with open('/home/mike/flasktest/static/logs/logled.txt', 'a') as dest:
        # Write the remaining lines back to the file
                dest.write(line + '\n')
        with open('/home/mike/flasktest/static/logled.txt', 'r') as file:
                lines = file.readlines()
        if lines:
                lines.pop(0)
        with open('/home/mike/flasktest/static/logled.txt', 'w') as dest:
        # Write the remaining lines back to the file
                dest.writelines(lines)
        return "ok"

@app.route('/run_cleartemplog')
def cleartemplog():
	with open('/home/mike/flasktest/static/CompostTempLog.txt', 'r') as file:
        # Read all lines from the file
		line = file.readline().strip()
        # Open the file for writing (which clears the file)
	with open('/home/mike/flasktest/static/logs/CompostTempLog.txt', 'a') as dest:
        # Write the remaining lines back to the file
		dest.write(line + '\n')
	with open('/home/mike/flasktest/static/CompostTempLog.txt', 'r') as file:
		lines = file.readlines()
	if lines:
		lines.pop(0)
	with open('/home/mike/flasktest/static/CompostTempLog.txt', 'w') as dest:
        # Write the remaining lines back to the file
		dest.writelines(lines)
	return "ok"


@app.route('/get_Temp_Graph')
def TempGraph():
	# Read data from file
	with open('/home/mike/flasktest/static/CompostTempLog.txt', 'r') as file:
		lines = file.readlines()
	# Extract date and temperature from each line
	dates = []
	temperatures = []
	for line in lines:
		parts = line.strip().split()
		date = parts[0] + ' ' + parts[1]  # Combine date and time parts
		temperature = int(parts[2])  # Assuming temperature is an integer
		dates.append(date)
		temperatures.append(temperature)
	# Create DataFrame
	data = pd.DataFrame({'Date': dates, 'Temperature': temperatures})
	# Convert 'Date' column to datetime format
	data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d %H-%M-%S')
	# Plotting
	plt.plot(data['Date'], data['Temperature'])
	# Customization
	plt.xlabel('Date', fontsize=20)
	plt.ylabel('Temperature', fontsize=20)
	plt.title('Temperature Variation Over Time', fontsize=20)
	plt.grid(True)
	plt.xticks(data['Date'], rotation=45)
	plt.subplots_adjust(bottom=0.15)
	# Save or display the plot
	plt.savefig('/home/mike/flasktest/static/temperature_plot.png')
	#plt.show()
	return "ok"

@app.route('/TotalWater')
def TotalWaterLog():
	# Initialize variables to store total durations for each duration type
	total = 0
# Open the file for reading
	with open('/home/mike/flasktest/static/log.txt', 'r') as file:
    # Read each line from the file
		for line in file:
        # Split the line by whitespace
			parts = line.split()
        # Extract the duration from the last part of the line
			duration = int(parts[-1][:-3])  # Remove 'min' and convert to int
        # Check if the duration is 60min or 10min and add to the corresponding total
			if '60min' in line:
				total += 60
			elif '10min' in line:
				total += 10
	total = total/60
	formatted_number = "{:.1f}".format(total)
	return str(formatted_number)



def get_pin_status():
    # Execute your Python script here For example: result = some_function_from_your_script() return result
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17,GPIO.OUT)
	pin_status = GPIO.input(17)
	if pin_status:
		return "on"
	else:
		return "off"

@app.route('/get_pin_status')
def fetch_pin_status():
    status = get_pin_status()
    return status


if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.238', port=80)
