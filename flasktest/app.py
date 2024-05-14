from flask import Flask, render_template
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime


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
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        str_current_datetime = str(current_datetime)
        with open('/home/mike/flasktest/static/log.txt', 'a') as file:
                file.write(str_current_datetime + ' 10min ended\n')
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
	current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
	str_current_datetime = str(current_datetime)
	with open('/home/mike/flasktest/static/log.txt', 'a') as file:
	        file.write(str_current_datetime + ' 60min ended\n')
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
	current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
	str_current_datetime = str(current_datetime)
	with open('/home/mike/flasktest/static/log.txt', 'a') as file:
		file.write(str_current_datetime + ' 30sec ended\n')
	return "ok"

@app.route('/run_clearlog')
def clearlog():
	with open('/home/mike/flasktest/static/log.txt', 'w') as file:
		file.write('')



def get_pin_status():
    # Execute your Python script here
    # For example:
    # result = some_function_from_your_script()
    # return result
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
