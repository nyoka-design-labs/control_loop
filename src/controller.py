from serial_devices.pump import Pump
from usb_devices.scale import Scale
import time

class Controller:
    """
    """

    def __init__(self, pump: Pump, scale: Scale):
        self.pump = pump
        self.scale = scale

    def run(self, func: function, mode: str='continuous') -> None | ValueError:
        """
        """

        if mode == 'continuous':
            self.__continuous(func)
        elif mode == 'discrete':
            self.__discrete(func)
        else:
            raise ValueError("Invalid mode")
    
    def __continuous(self, func: function):
        """
        """

        start_time = time.time()
        try:
            while True:
                current_time = time.time()
                elapsed_time = current_time - start_time
                weight = self.scale.get_weight()

                if weight > func(elapsed_time):
                    self.pump.control(True)
                else:
                    self.pump.control(False)
        except KeyboardInterrupt:
            self.pump.control(False)
            print("Program terminated")