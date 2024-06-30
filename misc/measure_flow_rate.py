import time
import os
import sys

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from devices.scale import USS_Scale
import numpy as np
from scipy.stats import linregress
from List_All_coms import serial_ports


ports = serial_ports()
print(ports)
# Initialize the scale
chosen_port = ports[-1]
print(chosen_port)
# chosen_port = '/dev/tty.usbserial-1130'
scale = USS_Scale(chosen_port)

def measure_pump_rate(measurement_interval=2, total_duration=60):
    print("Starting the pump rate measurement...")
    start_time = time.time()
    times = []
    weights = []

    while time.time() - start_time < total_duration:
        current_time = time.time() - start_time
        current_weight = scale.get_weight()
        print(f"weight: {current_weight} time: {current_time} time left {total_duration - current_time}")
        times.append(current_time)
        weights.append(current_weight)
        time.sleep(measurement_interval)  # wait for 2 seconds before the next measurement

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(times, weights)

    transfer_rate = slope * 60  # Convert the slope from g/s to ml/min (assuming 1g = 1ml)

    print(f"Slope: {slope} grams/second")
    print(f"Intercept: {intercept} grams")
    print(f"R-squared: {r_value**2}")
    print(f"Transfer rate: {transfer_rate:.2f} ml/min")

    return transfer_rate

# Run the measurement function
if __name__ == "__main__":
    measure_pump_rate()


