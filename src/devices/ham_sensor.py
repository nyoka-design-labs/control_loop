import pymodbus.client as ModbusClient
import struct
import time
import os
import sys

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..")
sys.path.append(SRC_DIR)
from resources.logging_config import setup_logger
import traceback
from datetime import datetime, timedelta
from resources.utils import *
from resources.error_notification import send_notification
logger = setup_logger()
class _Sensor:
    """
    Class representing the Hamilton sensors.
    """

    def __init__(self, port: str):
        """
        Initialize the sensor.
        """

        # initialie the Modbus client configuration
        self.client = ModbusClient.ModbusSerialClient(method='rtu', port=port, baudrate=19200, stopbits=2, bytesize=8, parity='N')
        self.callibration_func = lambda x: x # default callibration function (ie. no callibration)
        self.port = port

        self.client.connect()
    
    def get_temp(self) -> float:
        """
        Read temperature data from the sensor.
        """
        try:
            # Read holding registers from the sensor
            res = self.client.read_holding_registers(address=2409, count=10, slave=1)

            # Combine the two registers to form a hex value
            hex_value = hex(res.registers[3]) + hex(res.registers[2])[2:].zfill(4)

            # Convert the hex value to a float value
            data = self.convert_raw_value(str(hex_value))

            return round(data, 3)
        except Exception as e:
            print(f"Failed to get temp: \n{e}")
            logger.error(f"Error in get_temp: {e}\n{traceback.format_exc()}")
            # send_notification(f"sensors not connected")
            return -1

    def close(self):
        self.client.close()

    def convert_raw_value(self, value: str) -> float:
        """
        Convert raw hex value to float using IEEE 754 standard.
        """
        try:
            # Convert hex to binary string, remove '0b' prefix, and pad to 32 bits
            binary_str = format(int(value, 16), '032b')
            # Convert binary string to bytes
            bytes_value = int(binary_str, 2).to_bytes(4, byteorder='big', signed=True)
            # Unpack the bytes to a float
            float_value = struct.unpack('>f', bytes_value)[0]
            return float_value
        except Exception as e:
            print(f"Failed to convert raw hex to float: \n{e}")
            logger.error(f"Error in convert_raw_value: {e}\n{traceback.format_exc()}")
            return -1
class DO(_Sensor):
    """
    Class representing the dissolved oxygen sensor.
    """

    def __init__(self, port):
        """
        Initialize the sensor.
        """

        super().__init__(port)
        self.port = port
        self.callibration_func = lambda x: x

        DO_setpoint = get_loop_constant("calibration_constants", "DO_probe")
        print(DO_setpoint)
        self.callibrate(DO_setpoint)

    def __call__(self, *args, **kwds) -> float:
        try:
            # Attempt to get DO and handle disconnection transparently
            do_value = self.get_do()
            if do_value == -1:
                self.reconnect()  # Attempt to reconnect if reading fails
                do_value = self.get_do()  # Try to get DO again after reconnecting
            return do_value
        except Exception as e:
            print(f"Failed to get DO: \n{e}")
            logger.error(f"Error in __call__ for DO probe:\n port: {self.port}, \n {e}\n{traceback.format_exc()}")
            send_notification(f"sensors not connected")
            return -1
    

    def get_do(self) -> float:
        """
        Read DO from the sensor, handling disconnections.
        """
        if self.client:
            try:
                return round(self.callibration_func(self.__get_raw_do()), 3)  # Example adjustment factor
            except Exception as e:
                print(f"Failed to get DO: {e}")
                send_notification(f"sensors not connected")
                logger.error(f"Error in get_do: {e}\n{traceback.format_exc()}")
        return -1  # Return error value if disconnected or read fails
    
    
    def callibrate(self, do) -> None:
        """
        Calibrate DO sensor by adding a constant offset to be at 100%.
        """

        diff = 100 - do
        print(diff)
        self.callibration_func = lambda x: x + diff

    def __get_raw_do(self) -> float:
        """
        Returns the raw DO value, handle disconnections.
        """
        if self.client:
            response = self.client.read_holding_registers(address=2089, count=10, slave=1)
            if response.isError():
                raise ValueError("Error reading DO")
            hex_value = hex(response.registers[3]) + hex(response.registers[2])[2:].zfill(4)
            return self.convert_raw_value(hex_value)
        raise ConnectionError("DO sensor is disconnected")
            

        
    def reconnect(self):
        """
        Reattempt to connect to the sensor.
        """
        try:
            if not self.client:
                self.client = ModbusClient(method='rtu', port=self.port, baudrate=19200, stopbits=2, bytesize=8, parity='N')
                if not self.client.connect():
                    print(f"Failed to reconnect sensor on port {self.port}")
                    self.client = None
        except Exception as e:
            send_notification(f"sensors not connected")
            print(f"Failed to reconnect DO probe: \n{e}")
            logger.error(f"Error in reconnect DO: {e}\n{traceback.format_exc()}")
    def do_calibration(self, dur):
        """
        Calibrate the DO sensor by averaging measurements after a stabilization period.
        Dur is the stabilization duration in minutes.
        """
        input("Ensure the DO probe is in the standard solution and press Enter to start calibration.")
        start_time = datetime.now()
        stabilization_end = start_time + timedelta(minutes=dur)

        # Stabilization phase
        while datetime.now() < stabilization_end:
            current_do = self.__get_raw_do()
            elapsed_time = datetime.now() - start_time
            time_remaining = stabilization_end - datetime.now()
            print(f"Current DO: {current_do}, Time Started: {start_time.strftime('%H:%M:%S')}, Time Remaining: {time_remaining}")
            time.sleep(3)

        # Measurement phase
        measurements = []
        print("Starting measurement phase for DO calibration...")
        for _ in range(20):
            current_do = self.__get_raw_do()
            measurements.append(current_do)
            print(f"Measured DO: {current_do}")
            time.sleep(3)

        # Calculate average DO and adjust calibration
        average_do = sum(measurements) / len(measurements)
        print(f"DO Calibration complete. Average measured DO: {average_do:.3f}")
        update_loop_constant("calibration_constants", "DO_probe", average_do)
    
class PH(_Sensor):
    """
    Class representing the pH sensor.
    """

    def __init__(self, port):
        """
        Initialize the sensor.
        """

        super().__init__(port)
        self.port = port
        calibration_points = get_loop_constant("calibration_constants", "pH_probe")
        print(calibration_points)
        self.callibrate(calibration_points["4"], calibration_points["7"])
        
    def __call__(self) -> tuple:
        try:
            ph, temp = self.get_ph(), self.get_temp()
            if ph == -1 or temp == -1:
                self.reconnect()  # Attempt to reconnect if either value fails
                ph, temp = self.get_ph(), self.get_temp()
            return (ph, temp)
        except Exception as e:
            print(f"Failed to get ph and temp: \n{e}")
            send_notification(f"sensors not connected")
            logger.error(f"Error in __call__ for pH probe:\n port: {self.port}, \n {e}\n{traceback.format_exc()}")
            return (-1, -1)
    def get_ph(self) -> float:
        """
        Read pH from the sensor, handle disconnection.
        """
        if self.client:
            ph_offset = get_loop_constant("calibration_constants", "pH_probe").get("ph_offset", 0)
            try:
                return round(self.callibration_func(self.__get_raw_ph() + ph_offset), 3)
            except Exception as e:
                send_notification(f"sensors not connected")
                print(f"Failed to get ph: \n{e}")
                logger.error(f"Error in get_ph: {e}\n{traceback.format_exc()}")
        return -1  # Return error value if disconnected or read fails
        
    
    def callibrate(self, setpoint4: int, setpoint7: int) -> None:
        """
        Calibrate the sensor using a linear function (y = b0 + b1*x).
        """

        b1 = (7 - 4) / (setpoint7 - setpoint4) # slope paramater

        b0 = 4 - b1*setpoint4 + 0.168# intercept parameter

        self.callibration_func = lambda x: b0 + b1*x + 0.03

    def __get_raw_ph(self) -> float:
        """
        Read raw pH value from the sensor.
        """
        if self.client:
            response = self.client.read_holding_registers(address=2089, count=10, slave=1)
            if response.isError():
                raise ValueError("Error reading pH")
            hex_value = hex(response.registers[3]) + hex(response.registers[2])[2:].zfill(4)
            return self.convert_raw_value(hex_value)
        raise ConnectionError("PH sensor is disconnected")

    def reconnect(self):
        """
        Reattempt to connect to the sensor.
        """
        try:

            if not self.client:
                self.client = ModbusClient(method='rtu', port=self.port, baudrate=19200, stopbits=2, bytesize=8, parity='N')
                if not self.client.connect():
                    print(f"Failed to reconnect sensor on port {self.port}")
                    self.client = None
        except Exception as e:
            print(f"Failed to reconnect pH probe: \n{e}")
            logger.error(f"Error in reconnect pH: {e}\n{traceback.format_exc()}")

    def ph_calibration_values(self, dur):
        """
        Calibrate the pH sensor at pH 4 and pH 7.
        Dur is the stabilization duration in minutes.
        """
        calibration_points = {4: None, 7: None, "ph_offset": 0}
        for point in [4, 7]:  # Calibration points
            input(f"Place the probe in the {point} pH solution and press Enter to start calibration.")
            start_time = datetime.now()
            stabilization_end = start_time + timedelta(minutes=dur)

            # Stabilization phase
            while datetime.now() < stabilization_end:
                current_ph = self.__get_raw_ph()
                elapsed_time = datetime.now() - start_time
                time_remaining = stabilization_end - datetime.now()
                print(f"Current pH: {current_ph}, Time Started: {start_time.strftime('%H:%M:%S')}, Time Remaining: {time_remaining}")
                time.sleep(3)

            # Measurement phase
            measurements = []
            print(f"Starting measurement phase for calibration at pH {point}...")
            for _ in range(20):
                current_ph = self.__get_raw_ph()
                measurements.append(current_ph)
                print(f"Measured pH: {current_ph}")
                time.sleep(3)

            average_ph = sum(measurements) / len(measurements)
            calibration_points[point] = average_ph
            print(f"Calibration complete at pH {point}. Average measured pH: {average_ph:.3f}")

        update_loop_constant("calibration_constants", "pH_probe", calibration_points)
        

if __name__ == "__main__":
    # example usage of Sensor class
    # ph = PH("/dev/ttyUSB0")
    # ph.client.connect()
    do = DO("/dev/ttyUSB0")
    # do.client.connect()
    
    # # ph.ph_calibration_values(10)
    # do.do_calibration(5)
    # print(ph())
    # try:
    #     while True:
    #         print(f"do: {do()}  ph: {ph()}")
    #         time.sleep(3)
    # except KeyboardInterrupt:
    #     do.close()
    #     ph.close()
    #     print("\nProgram terminated")
