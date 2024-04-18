import pymodbus.client as ModbusClient
import struct

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

        self.client.connect()
    
    def get_temp(self) -> float:
        """
        Read temperature data from the sensor.
        """

        # Read holding registers from the sensor
        res = self.client.read_holding_registers(address=2409, count=10, slave=1)

        # Combine the two registers to form a hex value
        hex_value = hex(res.registers[3]) + hex(res.registers[2])[2:].zfill(4)

        # Convert the hex value to a float value
        data = self.__convert_raw_value(str(hex_value))

        return round(data, 3)

    def close(self):
        self.client.close()

    def __convert_raw_value(self, value: str) -> float:
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

    def get_do(self) -> float:
        """
        Read DO from the sensor.
        """

        return round(self.callibration_func(self.__get_raw_do()), 3)
    
    def callibrate(self) -> None:
        """
        Calibrate DO sensor by adding a constant offset to be at 100%.
        """

        diff = 100 - self.__get_raw_do()

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
            data = self.__convert_raw_value(str(hex_value))
        except AttributeError:
            data = 0

        # Convert the hex value to a float value
        return data
    
class PH(_Sensor):
    """
    Class representing the pH sensor.
    """

    def __init__(self, port):
        """
        Initialize the sensor.
        """

        super().__init__(port)
        self.tare_constant = 0

    def get_ph(self) -> float:
        """
        Read data from the sensor.
        """

        return round(self.callibration_func(self.__get_raw_ph()), 3)
    
    def get_tared_ph(self) -> float:
        """
        Returns adjusted reading for tare.
        """

        data = self.callibration_func(self.__get_raw_ph() + self.tare_constant)

        return round(data, 3)
    
    def update_tare_constant(self, tare: float) -> None:
        """
        Updates the tare constant.
        """

        curr_reading = self.__get_raw_ph()
        self.tare_constant = tare - curr_reading
    
    def callibrate(self, setpoint4: int, setpoint7: int) -> None:
        """
        Calibrate the sensor using a linear function (y = b0 + b1*x).
        """

        b1 = (7 - 4) / (setpoint7 - setpoint4) # slope paramater

        b0 = 4 - b1*setpoint4 # intercept parameter

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
        data = self.__convert_raw_value(str(hex_value))

        return data

if __name__ == "__main__":
    # example usage of Sensor class
    # sensor = Sensor(type="ph")
    # sensor.client.connect()

    # try:
    #     while True:
    #         print(f"Data: {sensor.get_data()}, Temperature: {sensor.get_temp()}")
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     sensor.close()
    #     print("\nProgram terminated")
    pass