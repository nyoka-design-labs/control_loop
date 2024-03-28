import pymodbus.client as ModbusClient

class Sensor:
    """
    Class for reading from the Hamilton sensor.
    """

    def __init__(self, type: str):
        """
        Initialize the sensor.
        """

        if (type == "do"):
            self.mode = "do"
            self.client = ModbusClient.ModbusSerialClient(port='/dev/ttyUSB0', baudrate=19200,
                                                       stopbits=2, bytesize=8, parity='N')
        elif (type == "ph"):
            self.mode = "ph"
            pass
        else:
            raise ValueError("Invalid sensor type")
        
        self.client.connect()

    def read(self) -> tuple:
        """
        Read from the sensor.
        """

        res = self.client.read_holding_registers(method='rtu', address=1928, count=4, unit=1)
        return (res.registers)

    def close(self):
        self.client.close()

if __name__ == "__main__":
    sensor = Sensor(type="do")
    print(sensor.read(2409, 10))
    sensor.close()

# client = ModbusClient.ModbusSerialClient(port='/dev/ttyUSB0', baudrate=19200, stopbits=2, bytesize=8, parity='N')
# client.connect()

# res = client.read_holding_registers(method='rtu', address=2409, count=10, unit=1)

# print(res)
# print(res.registers)
# print(res.decode)