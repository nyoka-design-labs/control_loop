from serial_devices.pump import Pump
from devices import get_measurement
from utils import *
import time

INTERVAL = 60 # time in between readings

# commands correspons to the arduino control sketch
commands = {"switch_units": "2",
            "speed_control": "3"}

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

        while True:
            self.pump.arduino.write(commands["switch_units"].encode()) # Switch units on the scale to keep it on

            data = get_measurement()

            elapsed_time = data['time'] - start_time

            expected_weight = exponential_func(elapsed_time+INTERVAL, 0) # weight at the next interval
            weight_difference = expected_weight - data['weight']

            if data['weight'] >= expected_weight:
                self.pump.control(True) # Turn on the pump
            else:
                self.pump.control(False) # Turn off the pump

            # Wait for the next interval before the next iteration
            time.sleep(INTERVAL)

    def pH_loop(self, ph: float):
        """
        Main control loop for the pH controller. Loops indefinitely.
        """
    

        if (ph < 6.7):
            # turn on pump
            self.pump.control(True)
        else:
            # turn off pump
            self.pump.control(False)
        