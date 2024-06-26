import serial
from devices.pump import Pump
from DeviceManager import DeviceManager
import time
from resources.utils import *
from resources.google_api.sheets import save_dict_to_sheet
from datetime import datetime, timedelta
import traceback
import json
import os
import inspect
from resources.logging_config import setup_logger
logger = setup_logger()
#CONSTANTS
port = '/dev/ttyACM0'
curr_dir = os.path.dirname(__file__)
json_file_path = os.path.join(curr_dir, "resources","constants.json")
baudrate = 9600
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
pumps = eval(get_loop_constant(loop_id="server_consts", const="pumps_connected"))

def create_controller(loop_id):

    if loop_id == "concentration_loop":
        controller = ConcentrationController()
    elif loop_id == "fermentation_loop":
        controller = FermentationController()

    return controller, controller.device_manager

class Controller:

    def __init__(self):
        try:
            if pumps:
                self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
        except Exception as e:
            print(f"failed to intialize arduino: \n{e}")
            logger.error(f"Error in controller super class constructor: {e}\n{traceback.format_exc()}")
            raise AttributeError("Unable to connect to Arduino; serial monitor in Arduino IDE may be open")

    def pump_control(self, state: str):
        try:
            print(f"sent arduino: {state.encode()}")
            logger.info(f"sent arduino: {state.encode()}")
            if pumps:
                self.arduino.write((state + '\n').encode())
        except Exception as e:
            print(f"failed to control pump: \n state: {state}, \n{e}")
            logger.error(f"Error in pump_control: \n state: {state}, \n{e}\n{traceback.format_exc()}")

        time.sleep(1)
        
    def start_control(self):
        try:
            control_id = self.control_id

            if control_id:
                control_method = getattr(self, f"_{self.__class__.__name__}__{control_id}", None)
                if control_method:
                    return control_method()
                else:
                    raise AttributeError(f"Method {control_id} not found in class.")
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
                data = self.get_data(test_data=self.control_consts["test_data"])
                self.save_data_sheets(data)
                return self.status, data
        except Exception as e:
            print(f"failed to start_collection: \n control_status: {control_status} \n{e}")
            logger.error(f"Error in start_collection: \n control_status: {control_status}, \n{e}\n{traceback.format_exc()}")

    def reset_controller_consts(self, testing: bool=False):
        if testing:
            reset_consts = get_control_constant(self.loop_id, self.control_id, "reset_consts")
            update_control_constant(self.loop_id, self.control_id, "start_time", 0)
            update_control_constant(self.loop_id, self.control_id, "test_data_index", 0)
            self.update_controller_consts(reset_consts)

    def stop_control(self, data_col_is_on: bool = True):
        print("stopping pumps")
        
        try:
            for pump in self.pumps.values():
                self.pump_control(pump.control(False))

            self.update_status(control_is_on=False, data_col_is_on=data_col_is_on)

            return self.status
        except Exception as e:
            print(f"failed to stop_control: \n data_col_is_on: {data_col_is_on} \n{e}")
            logger.error(f"Error in get_data: \n data_col_is_on: {data_col_is_on}, \n{e}\n{traceback.format_exc()}")
    
    def toggle_pump(self, pump_name):
        try:
            if pump_name in self.pumps:
                self.pump_control(self.pumps[pump_name].toggle())
                self.status.update({
                    f"{pump_name}_status": str(self.pumps[pump_name].state)
                })
        except Exception as e:
            print(f"failed to toggle_pump: \n{pump_name}, \n{e}")
            logger.error(f"Error in toggle_pump: \n{pump_name}, \n{e}\n{traceback.format_exc()}")
         
    def initialize_pumps(self):
        try:
            pumps_info = get_control_constant(self.loop_id, self.control_id, "pumps")
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
            })
            
            # Update dynamic pump statuses
            for pump_name in self.pumps:
                self.status[f"{pump_name}_status"] = str(self.pumps[pump_name].state)
        except Exception as e:
            print(f"failed to update_status: \n control_is_on: {control_is_on} \n data_col_is_on: {data_col_is_on} \n {e}")
            logger.error(f"Error in update_status: control_is_on: {control_is_on} \n data_col_is_on: {data_col_is_on}, \n{e}\n{traceback.format_exc()}")

    def get_data(self, test_data: str):
        try:
            if testing:
                    data = self.device_manager.test_get_measurement(test_data)
                    print(f"test data: {data}")
                    logger.info(f"test data: {data}")
                    return data
            else:
                data = self.device_manager.get_measurement()
                return data
        except Exception as e:
            print(f"failed to get data: {e}")
            logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")
    
    def __convert_even_odd(self, value):
            if isinstance(value, str) and value.isdigit():
                num = int(value)
                return "OFF" if num % 2 == 0 else "ON"
            return value
    
    def save_data_sheets(self, data):
        try:
            status = self.status.copy()
            status.pop("type", None)  # Remove the "type" key if it exists in the status data
            status.pop("data_collection_status", None)
            status.pop("loopID", None)
            status = {k: self.__convert_even_odd(v) for k, v in status.items()}
            combined_data = data.copy()  # Create a copy of the original data
            combined_data.pop("type", None)
            combined_data.update(status)
            save_dict_to_sheet(combined_data, self.control_consts["csv_name"])
            print("added data to sheets")
            logger.info("added data to sheets")
        except Exception as e:
            print(f"failed to add data to sheets: {data}, \n{e}")
            logger.error(f"Error in save_data_sheets: \n{data}, \n{e}\n{traceback.format_exc()}")

    def load_control_constants(self):
        """
        Load and store control constants for the chosen control in self.control_constants.
        """
        try:
            constants = get_control_constant(self.loop_id, self.control_id, "control_consts")  # Fetch constants for the given control
            # Store constants in a dictionary
            self.control_consts = constants
            print(f"Loaded control constants for {self.control_id}: {self.control_consts}")
            logger.info(f"Loaded control constants for {self.control_id}: {self.control_consts}")
        except Exception as e:
            print(f"Failed to load control constants: {e}")
            logger.error(f"Error in load_control_constants: {e}\n{traceback.format_exc()}")
            self.control_consts = {}  # Default to an empty dict if loading fails
    
    def update_controller_consts(self, *args, **kwargs):
        """
        Update a specific control constant in the control_const dict in the JSON file.

        Args:
            loop_id (str): The identifier for the loop.
            controller_id (str): The identifier for the specific controller within the loop.
            key (str): The key of the constant to update.
            value: The new value to set for the constant.
        """
         
        # Load the existing data from the JSON file
        with open(json_file_path, "r") as file:
            data = json.load(file)

        # Find the correct loop and controller to update
        loop_found = next((item for item in data["loop"] if item["loop_id"] == self.loop_id), None)
        if loop_found:
            controller_found = next((controller for controller in loop_found["controllers"] if controller["controller_id"] == self.control_id), None)
            if controller_found and "control_consts" in controller_found:
                updated_dict = update_dict(controller_found["control_consts"], *args, **kwargs)
                controller_found["control_consts"] = updated_dict
                # Save the updated data back to the JSON file
                with open(json_file_path, "w") as file:
                    json.dump(data, file, indent=4)
                print(f"Updated {args, kwargs} in controller {self.control_id} of loop {self.loop_id}")
                logger.info(f"Updated {args, kwargs} in controller {self.control_id} of loop {self.loop_id}")
                self.load_control_constants()
                print("Updated control_consts for controller")
            else:
                print(f"Controller {self.control_id} not found in loop {self.loop_id}")
        else:
            print(f"Loop {self.loop_id} not found")

class ConcentrationController(Controller):
    """
    The concentration control loop controller
    """

    def __init__(self):
        super().__init__()
        self.buffer_pump = Pump(name="whitePump1")
        self.lysate_pump = Pump(name="whitePump2")

        self.loop_id = "concentration_loop"
        self.control_id = get_loop_constant(self.loop_id, "chosen_control")
        self.device_manager = DeviceManager(self.loop_id, self.control_id, testing)

        self.initial_buffer_mass = None
        self.initial_lysate_mass = None

        self.control_consts = {}
        self.load_control_constants()

        # Initialize pumps from JSON configuration
        self.pumps = self.initialize_pumps()

        self.status = self.initialize_status()
        self.stop_control(data_col_is_on=False)
        
    def __concentration_loop(self):
        data = self.get_data(test_data=self.control_consts["test_data"])

        self.__buffer_control(data['buffer_weight'])
        # self.__lysate_control(data['lysate_weight'])

        self.update_status()   
   
        self.save_data_sheets(data)

        return data, self.status
    
    def __concentration_buffer_loop(self):
        data = self.get_data(test_data=self.control_consts["test_data"])

        self.__buffer_control(data['buffer_weight'])

        self.update_status()   
   
        self.save_data_sheets(data)

        return data, self.status
    
    def __buffer_control(self, weight: float):
        '''
        Turns on pump if LESS than set point. Re-fills reservoir.
        '''
        if self.control_consts["buffer_sp"] == 0:
            self.update_controller_consts("buffer_sp", weight)
        buffer_sp = self.control_consts["buffer_sp"]
        if (weight < buffer_sp):
            self.pump_control(self.pumps["buffer_pump"].control(True))
        else:
            self.pump_control(self.pumps["buffer_pump"].control(False))

    def __lysate_control(self, weight: float):
        '''
        Turns on pump if GREATER than set point. Empties reservoir.
        '''
        
        lysate_upper_sp = self.control_consts["lysate_upper_sp"]
        lysate_lower_sp = self.control_consts["lysate_lower_sp"]
        if (weight > lysate_upper_sp):
            self.pump_control(self.pumps["lysate_pump"].control(True))
        elif (weight < lysate_lower_sp):
            self.pump_control(self.pumps["lysate_pump"].control(False))

class FermentationController(Controller):
    """
    The fermentation control loop controller
    """

    def __init__(self):
        super().__init__()

        self.loop_id = "fermentation_loop"
        self.control_id = get_loop_constant(self.loop_id, "chosen_control")

        self.device_manager = DeviceManager(self.loop_id, self.control_id, testing)

        self.control_consts = {}
        self.load_control_constants()
        
        # Initialize pumps from JSON configuration
        self.pumps = self.initialize_pumps()

        self.status = self.initialize_status()
        self.stop_control(data_col_is_on=False)


    def __3_phase_feed_control(self):

        data = self.get_data(self.control_consts["test_data"])

        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        phase3_start_time = datetime(2024, 6, 20, 20, 30, 0)  # 8:30 PM Jun 20, 2024
        print(f"Lactose Start Time: {phase3_start_time.strftime('%d-%m-%Y_%H:%M:%S')}")
        logger.info(f"Lactose Start Time: {phase3_start_time.strftime('%d-%m-%Y_%H:%M:%S')}")
        start_feed = eval(self.control_consts["start_feed"])

        # Phase 1: Maintain pH using only base
        
        ph_maintained_time = self.control_consts.get("ph_maintained_time", 0)
        ph_window = self.control_consts["ph_window"]
        feed_trigger_ph = self.control_consts["feed_trigger_ph"]

        if not start_feed:
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            print("In phase 1")
            logger.info("In Phase 1")
            if data["ph"] >= feed_trigger_ph:
                if ph_maintained_time == 0:
                    # Start timing when pH first reaches feed_trigger_ph
                    ph_maintained_time = current_time
                    self.update_controller_consts("ph_maintained_time", ph_maintained_time)
                elif current_time - ph_maintained_time >= ph_window:  # Check if pH has been maintained
                    start_feed = True
                    self.update_controller_consts("start_feed", "True")
                    print("Transitioning to Phase 2")
                    logger.info("Transitioning to Phase 2")
            else:
                # Reset the timer if pH drops below feed_trigger_ph
                if ph_maintained_time != 0:
                    self.update_controller_consts("ph_maintained_time", 0)

        # Phase 2: Acid and base control OFF, turn on feed pump
        if start_feed and current_datetime < phase3_start_time:
            print("Phase 2: Glucose Feed")
            logger.info("Phase 2: Glucose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            self.pump_control(self.pumps["lactose_pump"].control(False))
            if data["ph"] >= feed_trigger_ph:
                self.pump_control(self.pumps["feed_pump"].control(True))
                print("Feed pump on")
                logger.info("Feed pump on")
            else:
                self.pump_control(self.pumps["feed_pump"].control(False))
                print("Feed pump off")
                logger.info("Feed pump off")

        # Phase 3: turn off acid and base control, turn off feed pump and start using lactose pump
        if start_feed and current_datetime >= phase3_start_time:
            print("Phase 3: Lactose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            self.pump_control(self.pumps["feed_pump"].control(False))
            if data["ph"] >= feed_trigger_ph:
                self.pump_control(self.pumps["lactose_pump"].control(True))
                print("Lactose pump on")
                logger.info("Lactose pump on")
            else:
                self.pump_control(self.pumps["lactose_pump"].control(False))
                print("Lactose pump off")
                logger.info("Lactose pump off")

        self.update_status()

        self.save_data_sheets(data)

        return data, self.status
    
    def __2_phase_do_trig_ph_feed_control(self):

        data = self.get_data(self.control_consts["test_data"])
        start_feed = eval(self.control_consts["start_feed"])

        # Phase 1: Maintain pH using only base
        
        do_maintained_counter = self.control_consts.get("do_maintained_counter", 0)
        do_window = self.control_consts["do_window"] - 1
        feed_trigger_ph = self.control_consts["feed_trigger_ph"]
        feed_trigger_do = self.control_consts["feed_trigger_do"]
        do_below_50_counter = self.control_consts["do_below_50_counter"]
        start_phase_1 = eval(self.control_consts["start_phase_1"])
        required_consecutive_readings = 2

        if not start_feed:
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            if not start_phase_1:
                if data["do"] < 50:
                    do_below_50_counter += 1
                    self.update_controller_consts("do_below_50_counter", do_below_50_counter)
                else:
                    do_below_50_counter = 0  # Reset counter if DO is not below 50
                    self.update_controller_consts("do_below_50_counter", do_below_50_counter)
            if do_below_50_counter >= required_consecutive_readings:
                self.update_controller_consts("start_phase_1", "True")
                if data["do"] >= feed_trigger_do:
                    print("In phase 1")
                    logger.info("In phase 1")
                    if do_maintained_counter >= do_window:  # Check if DO has been maintained
                        self.__pH_balance(data["ph"], base_control=False, acid_control=False)
                        start_feed = True
                        self.update_controller_consts("start_feed", "True")
                        print("Transitioning to Phase 2")
                        logger.info("Transitioning to Phase 2")
                    else:
                        do_maintained_counter += 1
                        self.update_controller_consts("do_maintained_counter", do_maintained_counter)
                else:
                    # Reset the counter if DO drops below feed_trigger_do
                    if do_maintained_counter != 0:
                        self.update_controller_consts("do_maintained_counter", 0)

        # Phase 2: Base control OFF, turn on feed pump
        if start_feed:
            print("Phase 2: Glucose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            if data["ph"] >= feed_trigger_ph:
                self.pump_control(self.pumps["feed_pump"].control(True))
                print("Feed pump on")
                logger.info("Feed pump on")
            else:
                self.pump_control(self.pumps["feed_pump"].control(False))
                print("Feed pump off")
                logger.info("Feed pump off")

        self.update_status()

        self.save_data_sheets(data)

        return data, self.status
    
    def __3_phase_do_feed_control(self):

        data = self.get_data(self.control_consts["test_data"])

        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        phase3_start_time = datetime(2024, 6, 20, 20, 30, 0)  # 8:30 PM Jun 20, 2024


        # Phase 1: Maintain pH using only base
        start_feed = eval(self.control_consts["start_feed"])
        do_upper_sp = self.control_consts["do_upper_sp"]
        do_lower_sp = self.control_consts["do_lower_sp"]
        deriv_window = self.control_consts["deriv_window"]
        derivs  = self.control_consts["derivs"]
        increment_counter = self.control_consts["increment_counter"]

        if not start_feed:
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            increment_counter += 1
            self.update_controller_consts("increment_counter", increment_counter)
            if increment_counter < deriv_window:
                print("not enough points", increment_counter)
                logger.info("not enough points", increment_counter)
                pass
            else:
                derivs.append(calculate_derivative("do", self.control_consts["csv_name"], deriv_window))
                self.update_controller_consts("derivs", derivs)
                print(derivs)
                logger.info(derivs)
                self.update_controller_consts("increment_counter", 0)

            if isDerPositive(derivs):
                    print("the last 5 derivatives were positive Phase 2 started started")
                    start_feed = True
                    self.update_controller_consts("start_feed", "True")
                    print("Transitioning to Phase 2")
                    logger.info("Transitioning to Phase 2")

        # Phase 2: Acid and base control OFF, turn on feed pump
        if start_feed and current_datetime < phase3_start_time:
            print("Phase 2: Glycerol Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=True)
            self.pump_control(self.pumps["lactose_pump"].control(False))
            self.pump_control(self.pumps["lactose_const_pump"].control(False))
            self.pump_control(self.pumps["feed_const_pump"].control(True))
            if data["do"] >= do_upper_sp:
                self.pump_control(self.pumps["feed_pump"].control(True))
                print("Glycerol pump on")
                logger.info("Glycerol pump on")
            elif data["do"] <= do_lower_sp:
                self.pump_control(self.pumps["feed_pump"].control(False))
                print("Glycerol pump off")
                logger.info("Glycerol pump off")

        # Phase 3: turn off acid and base control, turn off feed pump and start using lactose pump
        if start_feed and current_datetime >= phase3_start_time:
            print("Phase 3: Lactose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=True)
            self.pump_control(self.pumps["feed_pump"].control(False))
            self.pump_control(self.pumps["feed_const_pump"].control(False))
            self.pump_control(self.pumps["lactose_const_pump"].control(True))
            if data["do"] >= do_upper_sp:
                self.pump_control(self.pumps["lactose_pump"].control(True))
                print("Lactose pump on")
                logger.info("Lactose pump on")
            elif data["do"] <= do_lower_sp:
                self.pump_control(self.pumps["lactose_pump"].control(False))
                print("Lactose pump off")
                logger.info("Lactose pump off")

        self.update_status()

        self.save_data_sheets(data)

        return data, self.status
    
    def __test_loop(self):
        data, status = self.__3_phase_feed_control()

        return data, status
    
    def switch_feed_media(self):
        """
        Switch the feed media between 'Glucose' and 'Lactose'.
        """
        # control_id = self.control_id
        # current_value = get_control_constant(self.loop_id, control_id, "feed_media")
        current_value = self.control_consts["feed_media"]
        new_value = 'Lactose' if current_value == 'Glucose' else 'Glucose'
        self.update_controller_consts("feed_media", new_value)
        self.status.update({
            "feed_media": self.control_consts["feed_media"]
        })
    
    def __pH_balance(self, ph: float, base_control: bool=True, acid_control: bool=True):
        """
        Main control loop for the pH controller.
        """
        
        # ph_base_sp = get_control_constant(self.loop_id, self.control_id, "ph_balance_base_sp")
        # ph_acid_sp = get_control_constant(self.loop_id, self.control_id, "ph_balance_acid_sp")
        ph_base_sp = self.control_consts["ph_balance_base_sp"]
        ph_acid_sp = self.control_consts["ph_balance_acid_sp"]
        print(f"ph being balanced at base: {ph_base_sp} and acid: {ph_acid_sp}")
        logger.info(f"ph being balanced at base: {ph_base_sp} and acid: {ph_acid_sp}")

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
   
    c = FermentationController()
    # c = ConcentrationController()

    while True:
        c.start_control()
        time.sleep(2)
   

       
