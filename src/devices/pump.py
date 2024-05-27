import serial
import time

class Pump:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, name: str):
        # Map each pump type to its off state code

        # Updated command code assignment to avoid conflicts:
        self.pump_names = {
            "blackPump1": (0, 1), 
            "blackPump2": (2, 3),
            "blackPump3": (4, 5),
            "blackPump4": (6, 7),
            "blackPump5": (8, 9),
            "whitePump1": (10, 11),
            "whitePump2": (12, 13),
            "whitePump3": (14, 15),
        }

        if name not in self.pump_names:
            raise ValueError("Invalid pump mode")

        self.state = self.pump_names[name][0]
        self.name = name

    def control(self, turn_on: bool) -> str:
        """
        Adjusts the pump state based on the command to turn on or off,
        and returns the appropriate command code.
        """
        self.state = self.pump_names[self.name][1 if turn_on else 0]
        return str(self.state)
    
    def toggle(self) -> str:
        """
        Toggles the pump state.
        """
        current_state = self.state % 2  # Get current state (0 or 1)
        self.state = self.pump_names[self.name][1 - current_state]  # Toggle state
        return str(self.state)

    def set_rpm(self, rpm: float) -> str:
        """
        Special method for blackPump1 to control RPM, returns the command string.
        """
        if self.name == "blackPump1":
            return f"R{rpm}"
        else:
            raise NotImplementedError("RPM control is only implemented for blackPump1")
    def return_on_off_states(self, needed_state: bool):
        if needed_state:
            return self.pump_names[self.name][1]
        else:
            return self.pump_names[self.name][0]



if __name__ == "__main__":
    # example usage of Pump class
    pump = Pump(name="blackPump3")

    try:
        while True:
            print(pump.toggle())
            time.sleep(2)
    except KeyboardInterrupt:
        print("Program terminated")
