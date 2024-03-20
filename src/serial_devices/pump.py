import serial
import time

class PumpController:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, port='/dev/ttyACM0', baudrate=57600):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)

    def control_pump(self, turn_on):
        """
        Sends command to Arduino to control the pump.
        """
        command = '1' if turn_on else '0'
        self.arduino.write(command.encode())
    def control_refill_pump(self):
        """
        Sends command to Arduino to control the refil pump.
        """
        command = '2'
        self.arduino.write(command.encode())
        time.sleep(122)
        command = '3'
        self.arduino.write(command.encode())