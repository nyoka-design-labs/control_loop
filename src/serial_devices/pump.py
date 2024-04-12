import serial
import time

class Pump:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, type = 'ph', port: str='/dev/ttyACM1', baudrate: int=57600):

        # if (type != "do" and type != "ph"):
        #     raise ValueError("Invalid sensor type")
        

        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        self.state = 0 # 0=OFF, 1=ON
        # self.mode = type

    def control(self, turn_on):
        """
        Sends command to Arduino to control the pump.
        """
        self.state = turn_on
        command = '1' if turn_on else '0'
        self.arduino.write(command.encode())
        # if self.mode == 'do':
           
        # if self.mode == 'ph':
        #     self.state = turn_on
        #     command = '3' if turn_on else '4'
        #     self.arduino.write(command.encode())
    
    def toggle(self) -> None:
        """
        Changes state of pump
        """

        self.arduino.write(str(not self.state).encode())

if __name__ == "__main__":
    # example usage of Pump class
    pump = Pump()

    try:
        while True:
            pump.toggle()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Program terminated")