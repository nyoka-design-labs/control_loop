import pymodbus.client as ModbusClient
import struct
import time
import os
import sys

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..")
sys.path.append(SRC_DIR)
from resources.logging_config import logger
import traceback
from datetime import datetime, timedelta
from resources.utils import *
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
            print(f"failed to get temp: \n{e}")
            logger.error(f"Error in get_temp: {e}\n{traceback.format_exc()}")
            return -1

    def close(self):
        self.client.close()

    def convert_raw_value(self, value: str) -> float:
        """
        Convert raw hex value to float using IEEE 754 standard.
        """

        # Convert hex to binary string, remove '0b' prefix, and pad to 32 bits
        binary_str = format(int(value, 16), '032b')
        # Convert binary string to bytes
        bytes_value = int(binary_str, 2).to_bytes(4, byteorder='big', signed=True)
        # Unpack the bytes to a float
        float_value = struct.unpack('>f', bytes_value)[0]
        return float_value
    
class DO(_Sensor):
    """
    Class representing the dissolved oxygen sensor.
    """

    def __init__(self, port):
        """
        Initialize the sensor.
        """

        super().__init__(port)
        self.callibration_func = lambda x: x

    def __call__(self, *args, **kwds) -> float:
        return self.get_do()

    def get_do(self) -> float:
        """
        Read DO from the sensor.
        """
        try:
            return round(self.__get_raw_do() - 5.233, 3)
            # return round(self.callibration_func(self.__get_raw_do() - 4.098 + 0.96), 3)
        except Exception as e:
            print(f"failed to get data: \n{e}")
            logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")
    
    def callibrate(self, do) -> None:
        """
        Calibrate DO sensor by adding a constant offset to be at 100%.
        """

        diff = 100 - do

        self.callibration_func = lambda x: x + diff
    
    def __get_raw_do(self) -> float:
        """
        Returns the raw DO value.
        """

        data = None

        # Read holding registers from the sensor
        res = self.client.read_holding_registers(address=2089, count=10, slave=1)

        try: # checks if probe is connected
            # Combine the two registers to form a hex value
            hex_value = hex(res.registers[3]) + hex(res.registers[2])[2:].zfill(4)
            data = self.convert_raw_value(str(hex_value))
        except AttributeError:
            data = 0

        # Convert the hex value to a float value
        return data
    
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
        self.callibrate(average_do)
        print(f"DO Calibration complete. Average measured DO: {average_do:.3f}")
    
class PH(_Sensor):
    """
    Class representing the pH sensor.
    """

    def __init__(self, port):
        """
        Initialize the sensor.
        """

        super().__init__(port)
        self.callibrate(4.068, 7.056)

    def __call__(self, *args, **kwds) -> float:
        return (self.get_ph(), self.get_temp())
        
    def get_ph(self) -> float:
        """
        Read data from the sensor.
        """
        try:
            # return round(self.__get_raw_ph(), 5)
            return round(self.callibration_func(self.__get_raw_ph()), 3)
        except Exception as e:
            print(f"failed to get ph: \n{e}")
            logger.error(f"Error in get_ph: {e}\n{traceback.format_exc()}")
            return -1
    
    def callibrate(self, setpoint4: int, setpoint7: int) -> None:
        """
        Calibrate the sensor using a linear function (y = b0 + b1*x).
        """

        b1 = (7 - 4) / (setpoint7 - setpoint4) # slope paramater

        b0 = 4 - b1*setpoint4 + 0.131# intercept parameter

        self.callibration_func = lambda x: b0 + b1*x

    def __get_raw_ph(self) -> float:
        """
        Returns the raw pH value.
        """

        # Read holding registers from the sensor
        res = self.client.read_holding_registers(address=2089, count=10, slave=1)

        # Combine the two registers to form a hex value
        hex_value = hex(res.registers[3]) + hex(res.registers[2])[2:].zfill(4)

        # Convert the hex value to a float value
        data = self.convert_raw_value(str(hex_value))

        return data
    def ph_calibration_values(self, dur):
        """
        Calibrate the pH sensor at pH 4 and pH 7.
        Dur is the stabilization duration in minutes.
        """
        calibration_points = {4: None, 7: None}
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

        # Apply new calibration using the averages obtained
        self.callibrate(calibration_points[4], calibration_points[7])

if __name__ == "__main__":
    # example usage of Sensor class
    # ph = PH("/dev/ttyUSB1")
    # ph.client.connect()
    # do = DO("/dev/ttyUSB0")
    # do.client.connect()
    update_control_constant("calibration_constant", "pH_probe", f"4", 44)

    # try:
    #     while True:
    #         print(f"do: {do.get_do()}  ph: {ph.get_ph()}")
    #         time.sleep(3)
    # except KeyboardInterrupt:
    #     do.close()
    #     ph.close()
    #     print("\nProgram terminated")
