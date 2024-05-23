import serial
from devices.pump import Pump
from DeviceManager import DeviceManager
import time
from resources.utils import calculate_derivative, isDerPositive, get_loop_constant, get_control_constant

#CONSTANTS
port = '/dev/ttyACM0'
baudrate = 9600
testing = True


def create_controller(loop_id, control_id):
    
    dm = DeviceManager(loop_id, control_id)

    if loop_id == "concentration_loop":
        controller = ConcentrationController(dm)
    elif loop_id == "fermentation_loop":
        controller = FermentationController(dm)

    return controller, dm

class Controller:

    def __init__(self):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        # time.sleep(1)
        # self.arduino.flush()

    def pump_control(self, state: str):
        print(f"sent arduino: {state.encode()}")
        self.arduino.write((state + '\n').encode())
        # self.arduino.flush()

        time.sleep(1)

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
        self.lactose_pump = Pump(name="blackPump3")

        self.device_manager = dm
        self.loop_id = "fermentation_loop"

        self.start_feed = False
        self.start_feed_2 = False
        self.first_time = True
        self.refil = False
        self.rpm_volts = 0.06
        self.increment_counter = 0
        self.test_data = None

        
        self.control_name = get_loop_constant(self.loop_id, "chosen_control")

        self.status = {
            "type": "status",
            "loopID": "fermentation_loop",
            "control_loop_status": "control_off",
            "data_collection_status": "data_collection_off",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state),
        }

        self.pump_control(self.feed_pump.control(False))
        self.pump_control(self.lactose_pump.control(False))
        self.pump_control(self.base_pump.control(False))

    def start_control(self):
        control_name = self.control_name

        if control_name:
            control_method = getattr(self, f"_{self.__class__.__name__}__{control_name}", None)
            if control_method:
                return control_method()
            else:
                raise AttributeError(f"Method {control_name} not found in class.")
        else:
            raise ValueError(f"No control method found for loop_id: {self.loop_id}")

    # def start_control(self):
    #     value_for_func_2_run = get_loop_constant(self.loop_id, "chosen_control")

    #     return self.__ph_mixed_feed_control()
    
    def stop_control(self):
        self.pump_control(self.feed_pump.control(False))
        self.pump_control(self.base_pump.control(False))
        self.pump_control(self.lactose_pump.control(False))

        self.status.update({
            "control_loop_status": "control_off",
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state)
        })

        return self.status
    
    def start_collection(self):
        data = self.__get_data(data_col=True)
        
        self.status.update({
            "data_collection_status": "data_collection_on"
        })

        return self.status, data
    
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
        
    def toggle_lactose(self):
        self.pump_control(self.lactose_pump.toggle())
        self.status.update({
            "lactose_pump_status": str(self.lactose_pump.state)
        })

    def __ph_mixed_feed_control(self):
        '''
        control_id = ph_mixed_feed_loop
        '''
        data = self.__get_data()
        refill_mass = get_control_constant(self.loop_id, self.control_id, "refill_mass")
        feed_ph_sp = get_control_constant(self.loop_id, self.control_id, "feed_ph_sp")
        refill_count = get_control_constant(self.loop_id, self.control_id, "refill_count")

        # gets the intial weight of the feed
        if self.first_time:
            self.feedweightinitial = data["feed_weight"]
            print(self.feedweightinitial)
            self.first_time = False

        if not self.start_feed:
            if data["ph"] >= 7:
                self.pump_control(self.base_pump.control(False))
                self.start_feed = True
            else:
                self.pump_control(self.base_pump.control(True))

        if self.start_feed:
            if data['ph'] >= feed_ph_sp:
                self.pump_control(self.feed_pump.control(True)) # turn on the pump

            elif data['ph'] < feed_ph_sp:
                self.pump_control(self.feed_pump.control(False)) # turn on the pump
            
            if not self.refil:
                if self.feedweightinitial - data["feed_weight"] >= refill_mass:
                    self.refil = True

            if self.refil:
                if self.increment_counter < refill_count: # interval size of 15s
                    self.pump_control(self.lactose_pump.control(True))
                    self.increment_counter += 1
                else:
                    self.pump_control(self.lactose_pump.control(False))
                    self.refil = False
                    self.increment_counter = 0
                    self.feedweightinitial = data["feed_weight"]

        self.__update_status(True)

        return self.status
    
    def __do_der_control(self):
        '''
        control_id = do_der_loop
        '''
        data = self.__get_data()

        deriv_window = get_control_constant(self.loop_id, control_id="do_der_loop", const="deriv_window")
        derivs = calculate_derivative("do", self.loop_id, deriv_window)

        if isDerPositive(derivs):
            self.pump_control(self.feed_pump.control(True))
        else:
            self.pump_control(self.feed_pump.control(False))

        self.__pH_balance(data["ph"], "do_der_loop")
    
    def __new_control(self):
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
        self.__update_status(True)
         
        return self.status

    def __do_feed_control(self):
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

        self.__update_status(True)

        return self.status

    def __pH_balance(self, ph: float, control_id: str):
        """
        Main control loop for the pH controller.
        """
        
        ph_sp = get_control_constant(self.loop_id, control_id, "ph_balance_sp")
        print(f"ph being balanced at {ph_sp}")
        if (ph < ph_sp):
            # turn on pump
            self.pump_control(self.base_pump.control(True))

        else:
            # turn off pump
            self.pump_control(self.base_pump.control(False))
    
    def __get_data(self, data_col=False):
        if data_col:
            if testing:
                data = self.test_data
                return data
            else:
                data = self.device_manager.get_measurement()
                return data
        else:
            if testing:
                data = self.device_manager.test_get_measurement("test_data_7")
                self.test_data = data
                print(f"test data: {data}")
                return data
            else:
                data = self.device_manager.get_measurement()
                return data
            
    def __update_control_status(self, is_on: bool):
        """Update the control status based on the boolean value provided."""
        control = "control_on" if is_on else "control_off"
        return control

    def __update_status(self, control: bool):

        self.status.update({
            "control_loop_status": self.__update_control_status(control),
            "feed_pump_status": str(self.feed_pump.state),
            "base_pump_status": str(self.base_pump.state),
            "lactose_pump_status": str(self.lactose_pump.state)
        })

if __name__ == "__main__":
    d = DeviceManager("fermentation_loop", "ph_mixed_feed_loop")
    c = FermentationController(d)
    stat = 2
    while True:
        stat = stat ^ 1
        # print(c.pump_control(str(stat)))
        # print(c.pump_control(str(1)))
        print(c.start_control())

        time.sleep(5)
