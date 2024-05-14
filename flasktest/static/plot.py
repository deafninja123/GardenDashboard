import matplotlib.pyplot as plt
import pandas as pd

# Read data from file
with open('CompostTempLog.txt', 'r') as file:
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

# Save or display the plot
plt.savefig('temperature_plot.png')
plt.show()
