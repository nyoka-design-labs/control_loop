from serial_devices.pump import Pump
from devices import get_measurement
from utils import *
import time

INTERVAL = 60 # time in between readings

m_0 = 10000

class Controller:
    """
    Represents a controller in the control loop.
    """

    def __init__(self):
        self.pump = Pump()
    
    def loop(self):
        """
        Main control loop for the controller. Loops indefinitely.
        """

        start_time = time.time()
        i = 0
        last_weight = m_0
        weight_drops_by_min = extract_specific_cells('feed_data_v0-2_u-0.1_m0-1000.csv', 6, 1217, 4) * 1000
        while i in range(0, len(weight_drops_by_min)):
            self.pump.arduino.write('2'.encode()) # Switch units on the scale to keep it on

            data = get_measurement()

            elapsed_time = data['time'] - start_time

            expected_weight = last_weight - float(weight_drops_by_min[i])

            print(f"Elapsed time: {elapsed_time:.2f}s, Current weight: {data['weight']}, Expected weight: {expected_weight:.2f}")
            add_to_csv([data['weight'], round(expected_weight, 2)])

            if data['weight'] >= expected_weight:
                self.pump.control(True) # Turn on the pump
            else:
                self.pump.control(False) # Turn off the pump

            # Wait for the next interval before the next iteration
            i += 1
            time.sleep(INTERVAL)
        