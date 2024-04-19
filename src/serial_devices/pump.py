import serial
import time

class Pump:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, type: str):

        if (type != "main" and type != "ph"):
            raise ValueError("Invalid pump mode")

        if (type == "main"):
            self.state = 0 # 0=OFF, 1=ON
        elif (type == "ph"):
            self.state = 2 # 2=OFF, 3=ON

        self.mode = type

    def control(self, turn_on: bool) -> str:
        """
        Sends command to Arduino to control the pump.
        """

        command = 1 if turn_on else 0
        self.state = self.state ^ command # XOR the provided state
        return str(self.state) # XOR the provided state
    
    def toggle(self) -> str:
        """
        Changes state of pump
        """
        self.state = self.state ^ 1 # XOR to toggle state
        return str(self.state)

if __name__ == "__main__":
    # example usage of Pump class
    pump = Pump(type="main")

    try:
        while True:
            pump.toggle()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Program terminated")