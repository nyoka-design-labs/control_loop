import pymodbus.client as ModbusClient
import struct
import time

class Sensor:
    """
    Class representing the Hamilton sensors.
    """

    def __init__(self, type: str):
        """
        Initialize the sensor.
        """

        if (type != "do" and type != "ph"):
            raise ValueError("Invalid sensor type")

        # initialie the Modbus client configuration
        self.client = ModbusClient.ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=19200, stopbits=2, bytesize=8, parity='N')
        self.mode = type

        self.client.connect()

    def get_data(self) -> float:
        """
        Read data from the sensor. DO sensor updates reading every 3s
        """

        if (self.mode == 'do'):
            # Read holding registers from the sensor
            res = self.client.read_holding_registers(address=2089, count=10, slave=1)

            # Combine the two registers to form a hex value
            hex_value = hex(res.registers[3]) + hex(res.registers[2])[2:].zfill(4)

            # Convert the hex value to a float value
            data = self.__calibrate_raw_values(str(hex_value))
        elif (self.mode == 'ph'):
            # Placeholder for pH sensor implementation
            pass

        # Round the data to 3 decimal places and return it
        return round(data, 3)

    def close(self):
        self.client.close()

    def __calibrate_raw_values(self, value: str) -> float:
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

if __name__ == "__main__":
    # example usage of Sensor class
    sensor = Sensor(type="do")
    sensor.client.connect()

    try:
        while True:
            print(sensor.get_data())
            time.sleep(1)
    except KeyboardInterrupt:
        sensor.close()
        print("\nProgram terminated")