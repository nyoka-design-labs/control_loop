import serial
from serial_devices.pump import Pump
from devices import get_measurement
from utils import *
import time

INTERVAL = 60 # time in between readings

# commands correspons to the arduino control sketch
commands = {"switch_units": "5",
            "speed_control": "3"}

class Controller:
    """
    Represents a controller in the control loop.
    """

    def __init__(self, port: str='/dev/ttyACM0', baudrate: int=57600):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.control_pump = Pump(type="main")
        self.pH_pump = Pump(type="ph")
        self.start_main = False

        t = extract_specific_cells('../tests/feed_data_v0-2_u-0.1_m0-1000.csv', 6, 1217, 4)
        self.target = list(map(lambda x: float(x)*1000, t))
        self.index = 0
    
    def loop(self, data: dict):
        """
        Main control loop for the controller. Loops indefinitely.
        """

        self.arduino.write(commands["switch_units"].encode()) # keeps scale on

        if (data["ph"] > 6.75):
            self.start_main = True

        if (self.start_main): # starts only when pH reaches target
            current_weight = data["weight"]
            last_weight = self.__get_target_weight()

            if (current_weight >= last_weight):
                self.control_pump.control(True) # turn on the pump
            elif (current_weight < last_weight):
                self.control_pump.control(False) # turn off the pump

        self.__pH_balance(data['ph']) # balances the pH
            
    def __get_target_weight(self) -> float:
        """
        Returns the target weight for the current iteration.
        """
        t = self.target[self.index]
        self.index += 1
        return t

    def __pH_balance(self, ph: float):
        """
        Main control loop for the pH controller. Loops indefinitely.
        """
    
        if (ph < 6.7):
            # turn on pump
            self.pH_pump.control(True)
        else:
            # turn off pump
            self.pH_pump.control(False)
        