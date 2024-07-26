import serial
import time

class Valve:
    """
    Controls the valves connected to an ESP32.
    """

    def __init__(self, name: str):
        # Map each pump type to its off state code

        # Updated command code assignment to avoid conflicts:
        self.valve_names = {
            "heat_valve": (16, 17), 
            "cool_valve": (18, 19)
        }

        if name not in self.valve_names:
            raise ValueError("Invalid valve mode")

        self.state = self.valve_names[name][0]
        self.name = name

    def control(self, turn_on: bool) -> str:
        """
        Adjusts the valve state based on the command to turn on or off,
        and returns the appropriate command code.
        """
        state = self.valve_names[self.name][1 if turn_on else 0]
        return str(state)
    
    def return_on_off_states(self, needed_state: bool):
        if needed_state:
            return self.valve_names[self.name][1]
        else:
            return self.valve_names[self.name][0]

    def is_on(self) -> bool:
        """
        Checks if the pump is currently on.

        Returns:
        bool: True if the pump is on, False otherwise.
        """
        return self.state == self.valve_names[self.name][1]
    
    def set_state(self, state: int):
        if state in self.valve_names[self.name]:
            self.state = state
        else:
            raise ValueError(f"Invalid pump state {state}, for pump {self.name}")

if __name__ == "__main__":
    # example usage of Pump class
    pass
