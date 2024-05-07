import serial
from serial_devices.pump import Pump
from DeviceManager import DeviceManager
import time

#CONSTANTS
port = '/dev/ttyACM0'
baudrate = 9600


def create_controller(loop_id):
    
    dm = DeviceManager(loop_id)

    if loop_id == "concentration_loop":
        controller = ConcentrationController(dm)
    elif loop_id == "fermentation_loop":
        controller = FermentationController(dm)

    return controller, dm

class Controller:

    def __init__(self):
        # self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        pass


    def pump_control(self, state: float):
        print(f"sent arduino: {state}")
        # self.arduino.write(state.encode())



class ConcentrationController(Controller):
    """
    The concentration control loop controller
    """

    def __init__(self, dm: DeviceManager):
        super.__init__()
        self.buffer_pump = Pump(type="3")
        self.lysate_pump = Pump(type="4")
        self.device_manager = dm

        self.status = {
            "type": "status",
            "loopID": "concentration_loop",
            "control_loop_status": "control_off",
            "data_collection_status": "data_collection_off",
            "buffer_pump_status": "4",
            "lysate_pump_status": "6"
        }


    def start_control(self):
       return self.concentration_loop(self)
    

    def concentration_loop(self):
        data = self.device_manager.get_measurement()
        self.__buffer_control(data['weight_buff'])
        self.__lysate_control(data['weight_lys'])

        self.status.update({
            "control_loop_status": "control_on",
            "data_collection_status": "data_collection_on",
            "buffer_pump_status": str(self.buffer_pump.state),
            "lysate_pump_status": str(self.lysate_pump.state)
        })

        return self.status, data

    

    def __buffer_control(self, weight: float):
        if (weight < 1200):
            self.pump_control(self.buffer_pump.control(True))
        else:
            self.pump_control(self.buffer_pump.control(False))

    def __lysate_control(self, weight: float):
        if (weight < 250):
            self.pump_control(self.lysate_pump.control(False))
        else:
            self.pump_control(self.lysate_pump.control(True))

    def start_collection(self):
        data = self.device_manager.get_measurement()
        self.status.update({
            "data_collection_status": "data_collection_on"
        })

        return self.status, data

class FermentationController(Controller):
    """
    The fermentation control loop controller
    """

    def __init__(self, dm: DeviceManager):
        super().__init__()
        self.feed_pump = Pump(type="feed")
        self.base_pump = Pump(type="base")
        self.device_manager = dm
        self.start_feed = False

        self.status = {
            "type": "status",
            "loopID": "fermentation_loop",
            "control_loop_status": "control_off",
            "data_collection_status": "data_collection_off",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state),
        }

    def start_control(self):
        return self.test_loop()

    def test_loop(self):
        data = self.device_manager.get_measurement()

        if data['feed_weight'] >= 50:
            self.pump_control(self.feed_pump.control(True)) # turn on the pump
        elif data['feed_weight'] < 50:
            self.pump_control(self.feed_pump.control(False)) # turn on the pump




        self.status.update({
            "control_loop_status": "control_on",
            "data_collection_status": "data_collection_on",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state)
        })

        return self.status, data


    def do_feed_loop(self):
        """
        DO only control loop for the controller. Loops indefinitely.
        """
        data = self.device_manager.get_measurement()

        if (data["do"] >= 60):
                self.pump_control(self.feed_pump.control(True)) # turn on the pump

        elif (data["do"] < 20):
                self.pump_control(self.feed_pump.control(False)) # turn off the pump
        
        self.__pH_balance(data['ph']) # balances the pH

        self.status.update({
            "control_loop_status": "control_on",
            "data_collection_status": "data_collection_on",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state)
        })

        self.__pH_balance(data['ph']) # balances the pH


        return self.status, data

    
    def __pH_balance(self, ph: float):
        """
        Main control loop for the pH controller.
        """
    
        if (ph < 6.7):
            # turn on pump
            self.pump_control(self.base_pump.control(True))

        else:
            # turn off pump
            self.pump_control(self.base_pump.control(False))


    def start_collection(self):
        data = self.device_manager.get_measurement()
        self.status.update({
            "data_collection_status": "data_collection_on"
        })

        return self.status, data


if __name__ == "__main__":
    d = DeviceManager("fermentation_loop")
    c = FermentationController(d)
    while True:
        print(c.start_control())
        time.sleep(3)