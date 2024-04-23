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
        self.feed_pump = Pump(type="feed")
        self.pH_pump = Pump(type="ph")
        self.buffer_pump = Pump(type="buffer")
        self.lysate_pump = Pump(type="lysate_pump")
        self.start_feed = False
        self.pause_feed = False

        t = extract_specific_cells('/Users/mba_sam/Github/Nyoka Design Labs/control_loop/tests/feed_data_v0-2_u-0.1_m0-1000.csv', 6, 1217, 4)
        
        self.target = list(map(lambda x: float(x)*1000, t))
        self.index = 0
    
    def loop(self, data: dict):
        """
        Main control loop for the controller. Loops indefinitely.
        """

        # self.arduino.write(commands["switch_units"].encode()) # keeps scale on

        if (data["ph"] > 6.75):
            self.start_feed = True

        if (self.start_feed): # starts only when pH reaches target
            current_weight = data["weight"]
            last_weight = last_weight - self.__get_target_weight()
            print(last_weight)

            if (current_weight >= last_weight):
                self.arduino.write(self.feed_pump.control(True).encode()) # turn on the pump
            elif (current_weight < last_weight):
                self.arduino.write(self.feed_pump.control(False).encode()) # turn off the pump

        self.__pH_balance(data['ph']) # balances the pH

    def ph_do_feed_loop(self, data: dict):
        """
        Main control loop for the controller. Loops indefinitely.
        """

        # self.arduino.write(commands["switch_units"].encode()) # keeps scale on
        
        if (data["ph"] > 6.75):
            self.start_feed = True
            
        if (data["do"] >= 60):
            self.start_feed = True
        elif (data["do"] < 20):
            self.start_feed = False

        if (self.start_feed): # starts only when pH reaches target and Do is above 60
            last_weight = self.__get_target_weight()
            current_weight = data["weight"]
            print(f"target_weight: {last_weight})")

            if (current_weight >= last_weight):
                # print(f"sent arduino keep feed on: {self.feed_pump.control(True).encode()}")
                self.arduino.write(self.control_pump.control(True).encode()) # turn on the pump
            elif (current_weight < last_weight):
                # print(f"sent arduino keep feed off: {self.feed_pump.control(False).encode()}")
                self.arduino.write(self.control_pump.control(False).encode()) # turn off the pump

        self.__pH_balance(data['ph']) # balances the pH
        return last_weight
    
    def stop_loop(self):
        # self.feed_pump.control(False)
        # self.pH_pump.control(False)
        self.arduino.write(self.feed_pump.control(False).encode()) # turn OFF the feed pump
        self.arduino.write(self.pH_pump.control(False).encode()) # turn OFF the base pump

    def toggle_feed(self):
        # status = self.feed_pump.toggle()
        # print(f"sent arduino: {status}")
        self.arduino.write(self.control_pump.toggle().encode())
    
    def toggle_base(self):
        # status = self.pH_pump.toggle()
        # print(f"sent arduino: {status}")
        self.arduino.write(self.pH_pump.toggle().encode())

    def toggle_buffer(self):
        # status = self.pH_pump.toggle()
        # print(f"sent arduino: {status}")
        self.arduino.write(self.buffer_pump.toggle().encode())

    def toggle_lysate(self):
        # status = self.pH_pump.toggle()
        # print(f"sent arduino: {status}")
        self.arduino.write(self.lysate_pump.toggle().encode())
            
    def __get_target_weight(self) -> float:
        """
        Returns the target weight for the current iteration.
        """
        t = self.target[self.index]
        self.index += 1
        return t
        # return 1000

    def __mass_control(self, weight: float):
        pass

    def __pH_balance(self, ph: float):
        """
        Main control loop for the pH controller.
        """
    
        if (ph < 6.7):
            # turn on pump
            # print(f"sent arduino: {self.pH_pump.control(True).encode()}")
            self.arduino.write(self.pH_pump.control(True).encode())

        else:
            # turn off pump
            # print(f"sent arduino: {self.pH_pump.control(False).encode()}")
            self.arduino.write(self.pH_pump.control(False).encode())