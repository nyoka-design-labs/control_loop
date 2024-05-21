"""
Script used for testing of only the scale and pump control loop.
"""

import sys
import time
import time

sys.path.append("../src")
from devices.scale import Scale
from devices.pump import Pump
from utils import add_to_csv, extract_specific_cells

INTERVAL = 60 # time in between readings

m_0 = 10000

scale = Scale(0x0922, 0x8003)
pump = Pump()

def loop():
    start_time = time.time()
    i = 0
    last_weight = m_0
    weight_drops_by_min = extract_specific_cells('feed_data_v0-2_u-0.1_m0-1000.csv', 6, 1217, 4) * 1000
    while i in range(0, len(weight_drops_by_min)): 
        pump.arduino.write('2'.encode()) # Switch units on the scale to keep it on

        current_time = time.time()
        elapsed_time = current_time - start_time

        current_weight = scale.get_weight()
        # expected_weight = get_expected_weight(elapsed_time)
        expected_weight = last_weight - float(weight_drops_by_min[i])

        print(f"Elapsed time: {elapsed_time:.2f}s, Current weight: {current_weight}, Expected weight: {expected_weight:.2f}")
        add_to_csv([current_weight, round(expected_weight, 2)])

        if current_weight >= expected_weight:
            pump.control(True)  # Turn on the pump
        elif current_weight < expected_weight:
            pump.control(False)  # Turn off the pump

        last_weight = expected_weight # Update the last weight

        # Wait for the next interval before the next iteration
        i += 1
        time.sleep(INTERVAL)
    
    pump.control(True)  # Turn off the pump

if __name__ == "__main__":
    try:
        loop()
    except KeyboardInterrupt:
        # control_pump(False)
        print("Program terminated")
