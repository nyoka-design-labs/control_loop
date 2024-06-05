from resources.logging_config import logger
import serial
from devices.pump import Pump
from DeviceManager import DeviceManager
import time
from resources.utils import calculate_derivative, isDerPositive, get_loop_constant, get_control_constant, update_control_constant
from resources.google_api.sheets import save_dict_to_sheet
from datetime import datetime, timedelta
import traceback

#CONSTANTS
port = '/dev/ttyACM0'
baudrate = 9600
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
devices = eval(get_loop_constant(loop_id="server_consts", const="devices_connected"))
def create_controller(loop_id, control_id, testing: bool=False):
    
    dm = DeviceManager(loop_id, control_id, testing)

    if loop_id == "concentration_loop":
        controller = ConcentrationController(dm)
    elif loop_id == "fermentation_loop":
        controller = FermentationController(dm)

    return controller, dm

class Controller:

    def __init__(self):
        try:
            if devices:
                self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        except Exception as e:
            print(f"failed to intialize arduino: \n{e}")
            logger.error(f"Error in controller super class constructor: {e}\n{traceback.format_exc()}")
            raise AttributeError("Unable to connect to Arduino; serial monitor in Arduino IDE may be open")

    def pump_control(self, state: str):
        try:
            print(f"sent arduino: {state.encode()}")
            if devices:
                self.arduino.write((state + '\n').encode())
        except Exception as e:
            print(f"failed to control pump: \n state: {state}, \n{e}")
            logger.error(f"Error in pump_control: {e}\n{traceback.format_exc()}")

        time.sleep(1)

    def start_control(self):
        try:
            control_name = self.control_name

            if control_name:
                control_method = getattr(self, f"_{self.__class__.__name__}__{control_name}", None)
                if control_method:
                    return control_method()
                else:
                    raise AttributeError(f"Method {control_name} not found in class.")
            else:
                raise ValueError(f"No control method found for loop_id: {self.loop_id}")
        except Exception as e:
            print(f"failed to start control: \n{e}")
            logger.error(f"Error in start_control: {e}\n{traceback.format_exc()}")
        
    def start_collection(self, control_status: bool):
        try:
            self.status.update({
                "data_collection_status": "data_collection_on"
            })

            if control_status:
                return self.status
            else:
                data = self.get_data(test_data=self.test_data)
                # take out type field before adding to csv
                status = self.status.copy()
                status.pop("type", None)  # Remove the "type" key if it exists in the status data
                combined_data = data.copy()  # Create a copy of the original data
                combined_data.update(status)

                save_dict_to_sheet(combined_data, self.csv_name)
                
                return self.status, data
        except Exception as e:
            print(f"failed to start_collection: \n control_status: {control_status} \n{e}")
            logger.error(f"Error in start_collection: {e}\n{traceback.format_exc()}")
        
    def stop_control(self, data_col_is_on: bool = True):
        try:
            for pump in self.pumps.values():
                self.pump_control(pump.control(False))

            self.update_status(control_is_on=False, data_col_is_on=data_col_is_on)

            return self.status
        except Exception as e:
            print(f"failed to stop_control: \n data_col_is_on: {data_col_is_on} \n{e}")
            logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")
    
    def toggle_pump(self, pump_name):
        try:
            if pump_name in self.pumps:
                self.pump_control(self.pumps[pump_name].toggle())
                self.status.update({
                    f"{pump_name}_status": str(self.pumps[pump_name].state)
                })
        except Exception as e:
            print(f"failed to toggle_pump: \n{pump_name}, \n{e}")
            logger.error(f"Error in toggle_pump: {e}\n{traceback.format_exc()}")

            
    def initialize_pumps(self):
        try:
            pumps_info = get_control_constant(self.loop_id, self.control_name, "pumps")
            pumps = {}
            for pump_name, pump_value in pumps_info.items():
                pumps[pump_name] = Pump(name=pump_value)
            return pumps
        except Exception as e:
            print(f"failed to initialize_pumps: \n{e}")
            logger.error(f"Error in initialize_pumps: {e}\n{traceback.format_exc()}")

    
    def initialize_status(self):
        try:
            status = {
                "type": "status",
                "loopID": self.loop_id,
                "control_loop_status": "control_off",
                "data_collection_status": "data_collection_off",
                "feed_media": get_control_constant(self.loop_id, self.control_name, "feed_media")
            }
        
            # Add initial pump statuses to the status dictionary
            for pump_name in self.pumps:
                status[f"{pump_name}_status"] = str(self.pumps[pump_name].state)

            return status
        except Exception as e:
            print(f"failed to initialize_status: \n{e}")
            logger.error(f"Error in initialize_status: {e}\n{traceback.format_exc()}")
    
    def update_control_status(self, control_is_on: bool=False, data_col_is_on: bool=True):
        """Update the control status based on the boolean value provided."""
        control = "control_on" if control_is_on else "control_off"
        data_col = "data_collection_on" if data_col_is_on else "data_collection_off"
        return control, data_col
    
    def update_status(self, control_is_on: bool=True, data_col_is_on: bool=True):
        try:
            control, data_col = self.update_control_status(control_is_on, data_col_is_on)
            
            # Update static statuses
            self.status.update({
                "control_loop_status": control,
                "data_collection_status": data_col,
                "feed_media": get_control_constant(self.loop_id, self.control_name, "feed_media")
            })
            
            # Update dynamic pump statuses
            for pump_name in self.pumps:
                self.status[f"{pump_name}_status"] = str(self.pumps[pump_name].state)
        except Exception as e:
            print(f"failed to update_status: \n control_is_on: {control_is_on} \n data_col_is_on: {data_col_is_on} \n {e}")
            logger.error(f"Error in update_status: {e}\n{traceback.format_exc()}")

    
    def get_data(self, test_data: str):
        try:
            if testing:
                    data = self.device_manager.test_get_measurement(test_data)
                    print(f"test data: {data}")
                    return data
            else:
                data = self.device_manager.get_measurement()
                return data
        except Exception as e:
            print(f"failed to get data: {e}")
            logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")
        
    def save_data_sheets(self, data):
        try:
            status = self.status.copy()
            status.pop("type", None)  # Remove the "type" key if it exists in the status data
            combined_data = data.copy()  # Create a copy of the original data
            combined_data.update(status)
            save_dict_to_sheet(combined_data, self.csv_name)
            print("added data to sheets")
        except Exception as e:
            print(f"failed to add data to sheets: {data}, \n{e}")
            logger.error(f"Error in save_data_sheets: {e}\n{traceback.format_exc()}")

class ConcentrationController(Controller):
    """
    The concentration control loop controller
    """

    def __init__(self, dm: DeviceManager):
        super().__init__()
        self.buffer_pump = Pump(name="whitePump1")
        self.lysate_pump = Pump(name="whitePump2")

        self.device_manager = dm
        self.loop_id = "concentration_loop"
        self.test_data = "concentration_test_data_1"

        self.control_name = get_loop_constant(self.loop_id, "chosen_control")
        self.csv_name = get_control_constant(self.loop_id, self.control_name, "csv_name")

        # Initialize pumps from JSON configuration
        self.pumps = self.initialize_pumps()

        self.status = self.initialize_status()
        self.stop_control(data_col_is_on=False)
        
    def __concentration_loop(self):
        data = self.get_data(test_data="concentration_test_data_1")

        self.__buffer_control(data['buffer_weight'])
        self.__lysate_control(data['lysate_weight'])

        self.update_status()   
   
        # take out type field before adding to csv
        status = self.status.copy()
        status.pop("type", None)  # Remove the "type" key if it exists in the status data
        combined_data = data.copy()  # Create a copy of the original data
        combined_data.update(status)

        save_dict_to_sheet(combined_data, self.csv_name)

        return data, self.status

    def __buffer_control(self, weight: float):
        '''
        Turns on pump if LESS than set point. Re-fills reservoir.
        '''
        buffer_sp = get_control_constant(self.loop_id, self.control_name, "buffer_sp")
        if (weight < buffer_sp):
            self.pump_control(self.pumps["buffer_pump"].control(True))
        else:
            self.pump_control(self.pumps["buffer_pump"].control(False))

    def __lysate_control(self, weight: float):
        '''
        Turns on pump if GREATER than set point. Empties reservoir.
        '''
        lysate_sp = get_control_constant(self.loop_id, self.control_name, "lysate_sp")
        if (weight > lysate_sp):
            self.pump_control(self.pumps["lysate_pump"].control(True))
        else:
            self.pump_control(self.pumps["lysate_pump"].control(False))

class FermentationController(Controller):
    """
    The fermentation control loop controller
    """

    def __init__(self, dm: DeviceManager):
        super().__init__()

        self.device_manager = dm
        self.loop_id = "fermentation_loop"
        self.test_data = "3_phase_control_test_data"

        self.control_name = get_loop_constant(self.loop_id, "chosen_control")
        self.csv_name = get_control_constant(self.loop_id, self.control_name, "csv_name")
        
        self.start_feed = eval(get_control_constant(self.loop_id, self.control_name, "start_feed"))
        self.start_feed_2 = False
        self.first_time = True
        self.refill = False
        self.switch_feeds = False
        self.refill_increment = 0
        self.rpm_volts = 0.06
        self.increment_counter = 0
        self.last_base_addition = None
        self.ready_to_start_feed = False
        self.phase2_start_time = None

        # Initialize pumps from JSON configuration
        self.pumps = self.initialize_pumps()

        self.status = self.initialize_status()
        self.stop_control(data_col_is_on=False)


    def __ph_mixed_feed_control(self):
        '''
        control_id = ph_mixed_feed_control
        '''
        data = self.get_data()
        refill_mass = get_control_constant(self.loop_id, self.control_name, "refill_mass")
        feed_ph_sp = get_control_constant(self.loop_id, self.control_name, "feed_ph_sp")
        refill_count = get_control_constant(self.loop_id, self.control_name, "refill_count")

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
            
            if not self.refill and self.has_refilled:
                if self.feedweightinitial - data["feed_weight"] >= refill_mass:
                    self.refill = True

            if self.refill:
                if self.increment_counter < refill_count: # interval size of 15s
                    self.pump_control(self.lactose_pump.control(True))
                    self.increment_counter += 1
                else:
                    self.pump_control(self.lactose_pump.control(False))
                    self.increment_counter = 0
                    self.feedweightinitial = data["feed_weight"]

        self.update_status()

        return self.status
    
    def __do_der_control(self):
        '''
        control_id = do_der_control
        '''
        # gets the intial weight of the feed
        data = self.get_data()
        if self.first_time:
            self.feedweightinitial = data["feed_weight"]
            print(self.feedweightinitial)
            self.first_time = False

        self.__pH_balance(data["ph"], self.control_name)

        if not hasattr(self, 'derivs'):
            self.derivs = []
                
        if not self.start_feed:
            deriv_window = get_control_constant(self.loop_id, control_id=self.control_name, const="deriv_window")
            self.increment_counter += 1
            if self.increment_counter < deriv_window:
                print("not enough points", self.increment_counter)
                pass
            else:
                self.derivs.append(calculate_derivative("do", self.loop_id, deriv_window)) 
                print(self.derivs)
                self.increment_counter = 0

            if isDerPositive(self.derivs):
                    print("the last 5 derivatives were positive feed started",isDerPositive(self.derivs))
                    self.feedweightinitial = data["feed_weight"]
                    self.start_feed = True
            
        if self.start_feed:

            # self.pump_control(self.feed_pump.control(True))

            refill_mass = get_control_constant(self.loop_id, self.control_name, "refill_mass")

            if not self.switch_feeds:
                if self.feedweightinitial - data["feed_weight"] >= refill_mass:
                    self.switch_feeds = True

            if self.switch_feeds:
                self.pump_control(self.feed_pump.control(False))
                self.pump_control(self.lactose_pump.control(True))
            else:
                self.pump_control(self.feed_pump.control(True))

        else:
            self.pump_control(self.feed_pump.control(False))
        
        self.update_status()

        return self.status
    
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
        self.update_status()
         
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

        self.update_status()

        return self.status

    def __feed_control(self):
        data = self.get_data(self.test_data)
        self.__pH_balance(data["ph"])
        
        current_time = time.time()  # Get the current time

        if not self.start_feed:
            if not self.ready_to_start_feed:
                no_base_window = get_control_constant(self.loop_id, self.control_name, "no_base_window")

                if self.status["base_pump_status"] == str(self.pumps["base_pump"].return_on_off_states(True)):
                    print(f"updated last base addition time {current_time}")
                    self.last_base_addition = current_time  # Update the last base addition time

                if self.last_base_addition and (current_time - self.last_base_addition) >= no_base_window:
                    # 10 minutes (600 seconds) have passed since the last base addition
                    print(f"ready to feed set to true {(current_time - self.last_base_addition)}")
                    self.ready_to_start_feed = True

            if self.ready_to_start_feed and self.status["base_pump_status"] == str(self.pumps["base_pump"].return_on_off_states(True)):
                # Feed starts when base is added for the first time after the 10-minute period
                print("start feed set to true")
                self.start_feed = True

        switch_feed = True if get_control_constant(self.loop_id, self.control_name, "feed_media") == "Lactose" else False

        if self.start_feed:
            if not switch_feed: 
                self.pump_control(self.pumps["feed_pump"].control(True))
                self.pump_control(self.pumps["lactose_pump"].control(False))
            else:
                self.pump_control(self.pumps["lactose_pump"].control(True))
                self.pump_control(self.pumps["feed_pump"].control(False))
        else:
            self.pump_control(self.pumps["lactose_pump"].control(False))
            self.pump_control(self.pumps["feed_pump"].control(False))

        self.update_status()

        
        # take out type field before adding to csv
        status = self.status.copy()
        status.pop("type", None)  # Remove the "type" key if it exists in the status data
        combined_data = data.copy()  # Create a copy of the original data
        combined_data.update(status)

        save_dict_to_sheet(combined_data, self.csv_name)

        return data, self.status

    def __3_phase_feed_control(self):

        data = self.get_data(self.test_data)

        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        phase3_start_time = datetime(2024, 5, 30, 5, 0, 0)  # 5:00 AM May 30, 2024

        # Phase 1: Maintain pH using only base
        if not self.start_feed:
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            print("in phase 1")
            if data["ph"] >= 7.02:
                self.start_feed = True
                update_control_constant(self.loop_id, self.control_name, "start_feed", "True")
                print("Transition to Phase 2")

        # Phase 2: Acid and base control, turn on feed pump
        if self.start_feed and current_datetime < phase3_start_time:
            self.__pH_balance(data["ph"], base_control=True, acid_control=True)
            self.pump_control(self.pumps["feed_pump"].control(True))
            self.pump_control(self.pumps["lactose_pump"].control(False))
            print("Phase 2: Feed pump on")

        # Phase 3: turn off acid and base control, turn off feed pump and start using lactose pump
        if self.start_feed and current_datetime >= phase3_start_time:
            self.__pH_balance(data["ph"], base_control=False, acid_control=False)
            self.pump_control(self.pumps["feed_pump"].control(False))
            print("Transition to Phase 3: Feed pump off, lactose pump control")
            if data["ph"] >= 7:
                self.pump_control(self.pumps["lactose_pump"].control(True))
                print("Lactose pump on")
            else:
                self.pump_control(self.pumps["lactose_pump"].control(False))
                print("Lactose pump off")

        self.update_status()

        status = self.status.copy()
        status.pop("type", None)  # Remove the "type" key if it exists in the status data
        combined_data = data.copy()  # Create a copy of the original data
        combined_data.update(status)
        try:
            save_dict_to_sheet(combined_data, self.csv_name)
        except Exception as e:
            print(f"error in save_dict_to_sheet: {e}")

        return data, self.status
    
    def switch_feed_media(self):
        """
        Switch the feed media between 'Glucose' and 'Lactose'.
        """
        control_name = self.control_name
        current_value = get_control_constant(self.loop_id, control_name, "feed_media")
        new_value = 'Lactose' if current_value == 'Glucose' else 'Glucose'
        update_control_constant(self.loop_id, control_name, "feed_media", new_value)
        self.status.update({
            "feed_media": get_control_constant(self.loop_id, self.control_name, "feed_media")
        })
    
    def __pH_balance(self, ph: float, base_control: bool=True, acid_control: bool=True):
        """
        Main control loop for the pH controller.
        """
        
        ph_base_sp = get_control_constant(self.loop_id, self.control_name, "ph_balance_base_sp")
        ph_acid_sp = get_control_constant(self.loop_id, self.control_name, "ph_balance_acid_sp")
        print(f"ph being balanced at base: {ph_base_sp} and acid: {ph_acid_sp}")

        if base_control and (ph <= ph_base_sp):
            # turn on base pump
            self.pump_control(self.pumps["base_pump"].control(True))
            # turn off acid pump if acid_control is True
            if acid_control:
                self.pump_control(self.pumps["acid_pump"].control(False))

        elif acid_control and (ph > ph_acid_sp):
            # turn on acid pump
            self.pump_control(self.pumps["acid_pump"].control(True))
            # turn off base pump if base_control is True
            if base_control:
                self.pump_control(self.pumps["base_pump"].control(False))

        elif (not acid_control) and (not base_control):
            self.pump_control(self.pumps["base_pump"].control(False))
            self.pump_control(self.pumps["acid_pump"].control(False))

        else:
            # turn off both pumps if their respective control is True
            if base_control:
                self.pump_control(self.pumps["base_pump"].control(False))
            if acid_control:
                self.pump_control(self.pumps["acid_pump"].control(False))

        self.update_status()

if __name__ == "__main__":
    d = DeviceManager("fermentation_loop", "feed_control", testing)
    c = FermentationController(d)
    # d = DeviceManager("concentration_loop", "concentration_loop", testing)
    # c = ConcentrationController(d)
    stat = 2
    while True:
        stat = stat ^ 1
        # print(c.pump_control(str(stat)))
        # print(c.pump_control(str(1)))
        # print(c.start_control())
        c.start_control()

        time.sleep(5)
