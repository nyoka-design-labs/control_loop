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
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        pass

    def pump_control(self, state: str):
        print(f"sent arduino: {state}")
        self.arduino.write(state.encode())

class ConcentrationController(Controller):
    """
    The concentration control loop controller
    """

    def __init__(self, dm: DeviceManager):
        super().__init__()
        self.buffer_pump = Pump(name="whitePump1")
        self.lysate_pump = Pump(name="whitePump2")
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
       return self.concentration_loop()
    

    def concentration_loop(self):
        data = self.device_manager.get_measurement()
        self.__buffer_control(data['buffer_weight'])
        self.__lysate_control(data['lysate_weight'])

        self.status.update({
            "control_loop_status": "control_on",
            "data_collection_status": "data_collection_on",
            "buffer_pump_status": str(self.buffer_pump.state),
            "lysate_pump_status": str(self.lysate_pump.state)
        })

        return self.status

    def __buffer_control(self, weight: float):
        if (weight < 800):
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
    
    def stop_control(self):
        self.pump_control(self.buffer_pump.control(False))
        self.pump_control(self.lysate_pump.control(False))

        self.status.update({
            "control_loop_status": "control_off",
            "buffer_pump_status": str(self.buffer_pump.state),
            "lysate_pump_status": str(self.lysate_pump.state)
        })

        return self.status
    
    def toggle_buffer(self):
        self.pump_control(self.buffer_pump.toggle())
        self.status.update({
            "buffer_pump_status": str(self.buffer_pump.state)
        })

    def toggle_lysate(self):
        self.pump_control(self.lysate_pump.toggle())
        self.status.update({
            "lysate_pump_status": str(self.lysate_pump.state)
        })

class FermentationController(Controller):
    """
    The fermentation control loop controller
    """

    def __init__(self, dm: DeviceManager):
        super().__init__()
        self.feed_pump = Pump(name="blackPump1")
        self.base_pump = Pump(name="blackPump2")
        self.device_manager = dm
        self.start_feed = False
        self.start_feed_2 = False
        self.first_time = True
        self.rpm_volts = 0.06
        self.increment_counter = 0

        self.status = {
            "type": "status",
            "loopID": "fermentation_loop",
            "control_loop_status": "control_off",
            "data_collection_status": "data_collection_off",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state),
        }

    def start_control(self):
        return self.do_feed_loop()

    
    def new_loop(self):
        data = self.device_manager.get_measurement()

        if self.first_time:
            self.pump_control(f"9 {round(self.rpm_volts, 2)}")
            self.pump_control(self.feed_pump.control(False))
            self.first_time = False


        # if data['do'] < 50:
        # # if True:
        #     self.start_feed = True
        

        # if self.start_feed:
        if True:
            if True: # change later

                self.start_feed_2 = True
            

            if self.start_feed_2:
                print("went into main loop")
                self.pump_control(self.feed_pump.control(True))
                time.sleep(1)
                if self.increment_counter == 10:
                    if data['do'] >= 20:
                        print("incremented rpm")
                        self.rpm_volts += 0.01
                        
                    else:
                        print("decremented rpm")
                        self.rpm_volts -= 0.01

        
                    self.pump_control(f"9 {round(self.rpm_volts, 2)}")
                    

                    self.increment_counter = 0
                

                self.increment_counter += 1

        self.__pH_balance(data['ph'])

        self.status.update({
            "control_loop_status": "control_on",
            "data_collection_status": "data_collection_on",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state)
        })
         
        return self.status



    def do_feed_loop(self):
        """
        DO only control loop for the controller. Loops indefinitely.
        """
        data = self.device_manager.get_measurement()
        # if data['do'] > 70:
        print(f"increment counter:{self.increment_counter}")

        if self.increment_counter == 4:
            print("4th increment")
           
            if (data["do"] >= 20):
                    self.pump_control(self.feed_pump.control(True)) # turn on the pump

            elif (data["do"] < 20):
                    self.pump_control(self.feed_pump.control(False)) # turn off the pump
            self.increment_counter = 0
        self.increment_counter += 1
        
        self.__pH_balance(data['ph']) # balances the pH

        self.status.update({
            "control_loop_status": "control_on",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state)
        })
        return self.status

    
    def __pH_balance(self, ph: float):
        """
        Main control loop for the pH controller.
        """
        print("ph being balanced")
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
    
    def stop_control(self):
        self.pump_control(self.feed_pump.control(False))
        self.pump_control(self.base_pump.control(False))

        self.status.update({
            "control_loop_status": "control_off",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state)
        })

        return self.status
    def toggle_base(self):
        self.pump_control(self.base_pump.toggle())
        self.status.update({
            "base_pump_status": str(self.base_pump.state)
        })
    def toggle_feed(self):
        self.pump_control(self.feed_pump.toggle())
        self.status.update({
            "feed_pump_status": str(self.feed_pump.state)
        })
        


if __name__ == "__main__":
    d = DeviceManager("concentration_loop")
    c = FermentationController(d)
    while True:
        print(c.start_collection())
        time.sleep(3)