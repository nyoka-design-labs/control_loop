import serial
import time

class Pump:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, type: str):
        # Map each pump type to its off state code
        state_codes = {
            "feed": 0,   # 0=OFF, 1=ON
            "base": 2,     # 2=OFF, 3=ON
            "buffer": 4, # 4=OFF, 5=ON
            "lysate": 6  # 6=OFF, 7=ON
        }
        if type not in state_codes:
            raise ValueError("Invalid pump mode")

        self.state = state_codes[type]
        self.mode = type

    def control(self, turn_on: bool) -> str:
        """
        Adjusts the pump state based on the command to turn on or off.
        """

        if turn_on and self.state % 2 == 0:  # Check if current state is even (OFF), then turn ON
            self.state += 1
        elif not turn_on and self.state % 2 != 0:  # Check if current state is odd (ON), then turn OFF
            self.state -= 1
        print(f"state from pump: {self.state}")
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
