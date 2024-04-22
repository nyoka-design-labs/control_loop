import serial
import time

class Pump:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, type: str):

        if (type != "feed" and type != "ph"):
            raise ValueError("Invalid pump mode")

        # feed: 0=OFF, 1=ON ph: 2=OFF, 3=ON
        self.state = 0 if type == "feed" else 2

        self.mode = type

    def control(self, turn_on: bool) -> str:
        """
        Adjusts the pump state based on the desired command to turn on or off.
        Handles state transitions.
        """
        if turn_on:
            if self.state in [0, 2]:  # If the pump is off in either mode, turn it on
                self.state += 1
        else:
            if self.state in [1, 3]:  # If the pump is on in either mode, turn it off
                self.state -= 1

        # Return the new state as a string for any potential debugging/logging
        return str(self.state)
    
    def toggle(self) -> str:
        """
        Changes state of pump
        """
        self.state = self.state ^ 1 # XOR to toggle state
        return str(self.state)

if __name__ == "__main__":
    # example usage of Pump class
    pump = Pump(type="feed")

    try:
        while True:
            pump.toggle()
            time.sleep(5)
    except KeyboardInterrupt:
        print("Program terminated")
