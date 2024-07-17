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
from controller_mqtt_client import ControllerMQTTClient

logger = setup_logger()

#CONSTANTS
port = '/dev/ttyUSB0'
curr_dir = os.path.dirname(__file__)
json_file_path = os.path.join(curr_dir, "resources","constants.json")
baudrate = 460800
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
pumps = eval(get_loop_constant(loop_id="server_consts", const="pumps_connected"))

def create_controller(loop_id):
    """
    Creates a controller instance based on the specified loop ID.

    Args:
        loop_id (str): The loop identifier used to determine the type of controller to create.

    Returns:
        tuple: A tuple containing the controller instance and its associated device manager.

    Depending on the loop ID, this function initializes either a ConcentrationController or FermentationController along with their respective device managers.
    """

    if loop_id == "concentration_loop":
        controller = ConcentrationController()
    elif loop_id == "fermentation_loop":
        controller = FermentationController()

    return controller

class Controller:
    """
    A base class for controllers that manage operations related to device control and data handling.

    Handles initialization of serial connections to Arduino devices, controls pumps based on provided states, and manages data collection and control processes.
    """

    def __init__(self):
        """
        Initializes the Controller instance, attempting to establish a serial connection to an Arduino.

        Raises:
            AttributeError: If the connection to the Arduino cannot be established, typically due to the serial monitor being open in the Arduino IDE.
        """
        # try:
        if pumps:
            self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)
            time.sleep(2)
            
                
        # except Exception as e:
        #     print(f"failed to intialize arduino: \n{e}")
        #     logger.error(f"Error in controller super class constructor: {e}\n{traceback.format_exc()}")
        #     raise AttributeError("Unable to connect to Arduino; serial monitor in Arduino IDE may be open")
        pass

    def pump_control(self, state: str):
        """
        Sends a control command to the Arduino to manage pump states.

        Args:
            state (str): The desired state ('on' or 'off') to which the pump should be set.

        Logs the command sent to the Arduino and handles any exceptions that occur during the process.
        """
        try:
            command = state + self.pcu_id + '\n'
            print(f"Sending command: {command.encode()}")
            logger.info(f"Sending command: {command.encode()}")
            if pumps:
                print("sending command to esp")
                self.arduino.write(command.encode())
                time.sleep(1)
                if self.arduino.in_waiting > 0:
                    response = self.arduino.read(self.arduino.in_waiting).decode('utf-8')
                    print(f"Response from ESP32: {response}")

        except Exception as e:
            print(f"failed to control pump: \n state: {state}, \n{e}")
            logger.error(f"Error in pump_control: \n state: {state}, \n{e}\n{traceback.format_exc()}")

        time.sleep(1)
        
    def start_control(self):
        """
        Begins the control process by identifying and invoking the control method specified by the controller's current configuration.

        Raises:
            AttributeError: If the specified control method does not exist.
            ValueError: If no control method is configured for the current loop.
        """
        try:
            self.load_control_constants()
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
        """
        Starts or continues data collection based on the control status.

        Args:
            control_status (bool): Indicates whether the collection is starting as part of an ongoing control process.

        Returns:
            dict: The current status of the collection process, possibly along with collected data if control_status is False.
        """
        try:
            self.load_control_constants()
            self.status.update({
                "data_collection_status": "data_collection_on"
            })

            if control_status:
                return self.status
            else:
                data = self.get_data()
                self.save_data_sheets(data)
                return self.status, data
        except Exception as e:
            print(f"failed to start_collection: \n control_status: {control_status} \n{e}")
            logger.error(f"Error in start_collection: \n control_status: {control_status}, \n{e}\n{traceback.format_exc()}")

    def reset_controller_consts(self, testing: bool=False):
        """
        Resets control constants to default values based on testing requirements.

        Args:
            testing (bool): Indicates whether the reset is being performed under testing conditions, which may require different defaults.
        """
        if testing:
            reset_consts = get_control_constant(self.loop_id, self.control_id, "reset_consts")
            update_control_constant(self.loop_id, self.control_id, "start_time", 0)
            update_control_constant(self.loop_id, self.control_id, "test_data_index", 0)
            self.update_controller_consts(reset_consts)

    def stop_control(self, data_col_is_on: bool = True):
        """
        Stops all control activities and updates the system status accordingly.

        Args:
            data_col_is_on (bool): Indicates whether data collection should also be stopped.

        Returns:
            dict: The updated status after stopping the control processes.
        """
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
        """
        Toggles the operational state of a specified pump.

        Args:
            pump_name (str): The name of the pump whose state is to be toggled.

        Updates the status to reflect the new state of the pump after the toggle.
        """
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
        """
        Initializes the pumps based on the configuration stored in the control constants.

        Returns:
            dict: A dictionary of Pump objects indexed by their names.

        Creates and stores Pump instances for each configured pump, ready for operational control.
        """
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
        """
        Initializes the status dictionary for the controller with default values and current pump states.

        Returns:
            dict: The initial status dictionary containing control and collection states as well as initial pump states.
        """
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
        """
        Updates the control status based on specified parameters.

        Args:
            control_is_on (bool): Indicates whether the control loop is active.
            data_col_is_on (bool): Indicates whether data collection is active.

        Returns:
            tuple: A tuple containing new values for control and data collection status.
        """
        control = "control_on" if control_is_on else "control_off"
        data_col = "data_collection_on" if data_col_is_on else "data_collection_off"
        return control, data_col
    
    def update_status(self, control_is_on: bool=True, data_col_is_on: bool=True):
        """
        Updates the comprehensive status of the controller, including static and dynamic states.

        Args:
            control_is_on (bool): Indicates whether the control loop should be marked as active.
            data_col_is_on (bool): Indicates whether data collection should be marked as active.

        Updates both static and dynamic components of the controller's status based on current operational states.
        """
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

    def get_data(self):
        """
        Fetches measurement data from the device manager based on the current testing configuration.

        Args:
            test_data (str): Identifier for the type of test data to fetch.

        Returns:
            dict: The measurement data retrieved from the device manager or the test configuration.
        """
        try:
            if testing:
                    data = self.mqtt_client.request_data(testing=testing)
                    print(f"test data: {data}")
                    logger.info(f"test data: {data}")
                    return data
            else:
                data = self.mqtt_client.request_data()
                return data
        except Exception as e:
            print(f"failed to get data: {e}")
            logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")
      
    def save_data_sheets(self, data):
        """
        Saves collected data into a designated data sheet for record-keeping and analysis.

        Args:
            data (dict): The data to be saved.

        Processes and formats the data appropriately before saving it to an external data sheet.
        """
        try:
            status = self.status.copy()
            status.pop("type", None)  # Remove the "type" key if it exists in the status data
            status.pop("data_collection_status", None)
            status.pop("loopID", None)
            status = {k: self.__convert_even_odd(v) for k, v in status.items()}
            combined_data = data.copy()  # Create a copy of the original data
            combined_data.pop("type", None)
            combined_data.update(status)
            save_dict_to_sheet(combined_data, self.csv_name)
            print("added data to sheets")
            logger.info("added data to sheets")
        except Exception as e:
            print(f"failed to add data to sheets: {data}, \n{e}")
            logger.error(f"Error in save_data_sheets: \n{data}, \n{e}\n{traceback.format_exc()}")

    def load_control_constants(self):
        """
        Loads and caches control constants for the controller from an external configuration source.

        Loads control constants specific to the controller's loop and configuration, storing them for operational use.
        """
        try:
            constants = get_control_constant(self.loop_id, self.control_id, "control_consts")  # Fetch constants for the given control
            # Store constants in a dictionary
            self.control_consts = constants
            print(f"Loaded control constants for {self.control_id}: {self.control_consts}")
            logger.info(f"Loaded control constants for {self.control_id}: {self.control_consts}")

            # Store configuration in a dictionary
            constants = get_control_constant(self.loop_id, self.control_id, "control_config")  # Fetch constants for the given control
            # Store constants in a dictionary
            self.control_config = constants
            print(f"Loaded control configuration for {self.control_id}: {self.control_config}")
            logger.info(f"Loaded control configuration for {self.control_id}: {self.control_config}")
        except Exception as e:
            print(f"Failed to load control constants: {e}")
            logger.error(f"Error in load_control_constants: {e}\n{traceback.format_exc()}")
            self.control_consts = {}  # Default to an empty dict if loading fails
            self.control_config = {}  # Default to an empty dict if loading fails
    
    def update_controller_consts(self, toUpdate, *args, **kwargs):
        """
        Updates specific control constants within the controller's configuration.

        Args:
            *args: Additional positional arguments specifying which constants to update.
            **kwargs: Key-value pairs specifying the values to which the constants should be updated.

        Updates are performed directly in the configuration file and are immediately reflected in the controller's operational parameters.
        """
         
        # Load the existing data from the JSON file
        with open(json_file_path, "r") as file:
            data = json.load(file)

        # Find the correct loop and controller to update
        loop_found = next((item for item in data["loop"] if item["loop_id"] == self.loop_id), None)
        if loop_found:
            controller_found = next((controller for controller in loop_found["controllers"] if controller["controller_id"] == self.control_id), None)
            if controller_found and toUpdate in controller_found:
                updated_dict = update_dict(controller_found[toUpdate], *args, **kwargs)
                controller_found[toUpdate] = updated_dict
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

    def __convert_even_odd(self, value):
        """
        Converts numeric values to 'ON' or 'OFF' based on their even or odd status.

        Args:
            value (str): The numeric value to be converted, as a string.

        Returns:
            str: 'ON' if the number is odd, 'OFF' if even.
        """
        if isinstance(value, str) and value.isdigit():
            num = int(value)
            return "OFF" if num % 2 == 0 else "ON"
        return value
    
    def __get_loop_devices(self) -> list:
        """
        Gets the devices in the specified loop.
        """
           
        devices = get_control_constant(self.loop_id, self.control_id, "devices")
        devices = list(filter(lambda dev: dev != "temp_sensor", devices))

        return devices
    
    def __get_loop_data_type(self) -> list:
        """
        Gets the data type for the specified loop.
        """

        return list(get_control_constant(self.loop_id, self.control_id, "data_type"))
    
    def init_device_manager(self):
        init_data = {
            "loop_id": self.loop_id,
            "control_id": self.control_id,
            "data_types": self.__get_loop_data_type(),
            "loop_devices": self.__get_loop_devices(),
            "csv_name": get_control_constant(self.loop_id, self.control_id, "csv_name"),
            "test_name": get_control_constant(self.loop_id, self.control_id, "test_name"),
            "devices": eval(get_loop_constant(loop_id="server_consts", const="devices_connected"))

        }
        self.mqtt_client.init_device_manager(init_data)
class ConcentrationController(Controller):
    """
    The concentration control loop controller
    """

    def __init__(self):
        super().__init__()

        self.loop_id = "fermentation_loop"
        self.control_id = get_loop_constant(self.loop_id, "chosen_control")
        self.csv_name = get_control_constant(self.loop_id, self.control_id, "csv_name")
        self.pcu_id = get_loop_constant(self.loop_id, "pcu_id")
        self.load_control_constants()
        
        self.mqtt_client = ControllerMQTTClient(broker_address="192.168.0.25")
        self.init_device_manager()

        self.initial_buffer_mass = None
        self.initial_lysate_mass = None  

        # Initialize pumps from JSON configuration
        self.pumps = self.initialize_pumps()

        self.status = self.initialize_status()
        self.stop_control(data_col_is_on=False)
        
    def __concentration_loop(self):
        data = self.get_data()

        self.__buffer_control(data['buffer_weight'])
        # self.__lysate_control(data['lysate_weight'])

        self.update_status()   
   
        self.save_data_sheets(data)

        return data, self.status
    
    def __concentration_buffer_loop(self):
        data = self.get_data()

        self.__buffer_control(data['buffer_weight'])

        self.update_status()   
   
        self.save_data_sheets(data)

        return data, self.status
    
    def __buffer_control(self, weight: float):
        '''
        Turns on pump if LESS than set point. Re-fills reservoir.
        '''
        
        if self.control_config["buffer_sp"] == 0:
            self.update_controller_consts("control_config", "buffer_sp", weight)
        buffer_sp = self.control_config["buffer_sp"]
        if (weight < buffer_sp):
            self.pump_control(self.pumps["buffer_pump"].control(True))
        else:
            self.pump_control(self.pumps["buffer_pump"].control(False))

    def __lysate_control(self, weight: float):
        '''
        Turns on pump if GREATER than set point. Empties reservoir.
        '''
        
        lysate_upper_sp = self.control_config["lysate_upper_sp"]
        lysate_lower_sp = self.control_config["lysate_lower_sp"]
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
        self.csv_name = get_control_constant(self.loop_id, self.control_id, "csv_name")
        self.pcu_id = get_loop_constant(self.loop_id, "pcu_id")
        self.load_control_constants()

        self.mqtt_client = ControllerMQTTClient(broker_address="192.168.0.25")
        self.init_device_manager()
        
        # Initialize pumps from JSON configuration
        self.pumps = self.initialize_pumps()

        self.status = self.initialize_status()
        self.stop_control(data_col_is_on=False)


    def __3_phase_feed_control(self):
        """
        Manages a three-phase feed control process involving pH adjustments and selective pump activation.

        This method manages the control process through the following:
        - Loads control constants.
        - Retrieves and uses the latest data to monitor and adjust system behavior.
        - Manages the feeding process in three phases:
        1. Initial pH maintenance using only a base solution.
        2. Activation of a glycerol feed pump based on time and pH levels before a specific datetime.
        3. Transition to a lactose feed pump after the specified datetime.

        Each phase uses pH data to control pumps and adjust the feed type, ensuring that the process parameters are within specified limits. The method also handles data collection and status updates.

        Returns:
            tuple: Contains the data collected during the control process and the updated status of the controller.
        """

        data = self.get_data()

        start_feed = eval(self.control_consts["start_feed"])

        pre_feed_trigger_type = 'ph'
        feed_trigger_type = 'ph'
        feed_trigger_sp = self.control_config["feed_trigger_sp"]

        start_feed_trig_value = self.control_config.get("start_feed_trig_value")
        required_readings = self.control_config.get("required_readings")
        feed_counter = self.control_consts.get("feed_counter", 0)

        
        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        phase3_start_time = datetime(2024, 7, 4, 11, 0, 0)  # 8:30 PM Jun 20, 2024
        

        # Phase 1: Maintain pH using only base
        if not start_feed:
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            start_feed = self.__start_feed_check_bool(data, pre_feed_trigger_type, start_feed_trig_value, required_readings, feed_counter)

        # Phase 2: Start feeding with glycerol pump
        if start_feed and current_datetime < phase3_start_time:
            print("Phase 2: Glycerol Feed")
            logger.info("Phase 2: Glucose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            self.__control_pump_activation(data, 'feed_pump', feed_trigger_type, feed_trigger_upper_sp=feed_trigger_sp, feed_trigger_lower_sp=feed_trigger_sp)

        # Phase 3: Start feeding with lactose pump
        if start_feed and current_datetime >= phase3_start_time:
            print("Phase 3: Lactose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            self.__control_pump_activation(data, 'lactose_pump', feed_trigger_type, feed_trigger_upper_sp=feed_trigger_sp, feed_trigger_lower_sp=feed_trigger_sp)

        self.update_status()

        self.save_data_sheets(data)

        return data, self.status
    
    def __2_phase_do_trig_ph_feed_control(self):
        """
        Controls a two-phase feeding process that initiates based on dissolved oxygen (DO) and controls pH levels.

        This method performs the following:
        - Loads control constants.
        - Retrieves and uses the latest data to monitor and adjust system behavior.
        - Manages the feeding process in two phases:
        1. pH maintenance based on predefined settings.
        2. Activation of feeding pumps when conditions meet specific triggers.

        Pre-feed conditions and feed initiation are controlled by evaluating the dissolved oxygen levels,
        followed by pH maintenance. The process aims to transition smoothly from the first phase (maintenance)
        to the second phase (active feeding), which is controlled through continuous monitoring and adjustments
        based on the current pH levels.

        Returns:
            tuple: Contains the data collected during the process and the updated status of the controller.
        """


        data = self.get_data()

        pre_feed_trigger_type = 'do'
        feed_trigger_type = 'ph'

        feed_trigger_sp = self.control_config["feed_trigger_sp"]

        start_feed_trig_value = self.control_config.get("start_feed_trig_value")
        start_trig_value = self.control_config.get("start_trig_value")
        start_counter = self.control_consts.get("start_counter", 0)
        feed_counter = self.control_consts.get("feed_counter", 0)

        required_readings = self.control_config.get("required_readings")

        start_phase_1 = eval(self.control_consts["start_phase_1"])
        start_feed = eval(self.control_consts["start_feed"])

        if not start_feed:
            self.__pH_balance(data['ph'], base_control=True, acid_control=False)
            start_phase_1 = self.__pre_phase_check(data, pre_feed_trigger_type, start_trig_value, required_readings, start_counter, start_phase_1)
            start_feed = self.__start_feed_check_bool(data, pre_feed_trigger_type, start_feed_trig_value, required_readings, feed_counter, start_phase_1)
            if start_feed:
                self.__pH_balance(data['ph'], base_control=False, acid_control=False)
        

        if start_feed:
            self.__control_pump_activation(data, 'feed_pump', feed_trigger_type, feed_trigger_upper_sp=feed_trigger_sp, feed_trigger_lower_sp=feed_trigger_sp)
            self.__activate_antifoam_pump()
            
        self.update_status()

        self.save_data_sheets(data)

        return data, self.status
    
    def __3_phase_do_feed_control(self):
        """
        Manages a three-phase feeding process based on pH and dissolved oxygen (DO) levels, integrating derivative checks.

        This method performs the following:
        - Loads control constants and fetches the latest data.
        - Retrieves and uses the latest data to monitor and adjust system behavior.
        - Manages the feeding process through three phases:
        1. pH maintenance using only the base solution before any feed starts.
        2. Glycerol feed activation prior to a specific datetime using DO triggers.
        3. Lactose feed activation post a specific datetime, continuing DO-based control.

        The control logic includes starting the feed based on the DO levels and adjusting the feed type over time.
        The method also involves advanced control techniques such as derivative checking of the sensor readings
        to decide on feed initiation and adjustment, providing precise control over the feeding process.

        Returns:
            tuple: Contains the latest data and the controller's updated status, detailing the operational state
                and any changes enacted during the control process.
        """
        data = self.get_data()
        
        start_feed = eval(self.control_consts["start_feed"])

        pre_feed_trigger_type = 'ph'
        feed_trigger_type = 'do'


        required_readings = self.control_config.get("required_readings")
        deriv_window = self.control_config["deriv_window"]
        derivs  = self.control_config["derivs"]
        feed_counter = self.control_config.get("feed_counter", 0)
        
        feed_trigger_upper_sp = self.control_config["feed_trigger_upper_sp"]
        feed_trigger_lower_sp = self.control_config["feed_trigger_lower_sp"]

        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        phase3_start_time = datetime(2024, 6, 20, 20, 30, 0)  # 8:30 PM Jun 20, 2024


        # Phase 1: Maintain pH using only base
        if not start_feed:
            self.__pH_balance(data["ph"], base_control=True, acid_control=False)
            self.__start_feed_check_der(self, pre_feed_trigger_type, feed_counter, derivs, self.csv_name, required_readings=required_readings, deriv_window=deriv_window)

        # Phase 2: Start feeding with glycerol pump
        if start_feed and current_datetime < phase3_start_time:
            print("Phase 2: Glycerol Feed")
            logger.info("Phase 2: Glucose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=True)
            self.pump_control(self.pumps["lactose_pump"].control(False))
            self.pump_control(self.pumps["lactose_const_pump"].control(False))
            self.pump_control(self.pumps["feed_const_pump"].control(True))
            self.__control_pump_activation(data, 'feed_pump', feed_trigger_type, feed_trigger_upper_sp=feed_trigger_upper_sp, feed_trigger_lower_sp=feed_trigger_lower_sp)

        # Phase 3: Start feeding with lactose pump
        if start_feed and current_datetime >= phase3_start_time:
            print("Phase 3: Lactose Feed")
            self.__pH_balance(data["ph"], base_control=True, acid_control=True)
            self.pump_control(self.pumps["feed_pump"].control(False))
            self.pump_control(self.pumps["feed_const_pump"].control(False))
            self.pump_control(self.pumps["lactose_const_pump"].control(True))
            self.__control_pump_activation(data, 'lactose_pump', feed_trigger_type, feed_trigger_upper_sp=feed_trigger_upper_sp, feed_trigger_lower_sp=feed_trigger_lower_sp)

        self.update_status()

        self.save_data_sheets(data)

        return data, self.status
    
    def __test_loop(self):
        data = self.get_data()
        cyc = self.control_config["cycles"]
        self.pump_control(self.pumps["feed_pump"].toggle())
        self.pump_control(self.pumps["base_pump"].toggle())

        cyc += 1

        self.update_controller_consts("control_config", "cycles", cyc)

        self.update_status()

        return data, self.status
    
    def __switch_feed_media(self):
        """
        Switch the feed media between 'Glycerol' and 'Lactose'.
        """
        # control_id = self.control_id
        # current_value = get_control_constant(self.loop_id, control_id, "feed_media")
        current_value = self.control_config["feed_media"]
        new_value = 'Lactose' if current_value == 'Glucose' else 'Glucose'
        self.update_controller_consts("control_config", "feed_media", new_value)
        self.status.update({
            "feed_media": self.control_config["feed_media"]
        })
    
    def __pH_balance(self, ph: float, base_control: bool=True, acid_control: bool=True):
        """
        Controls the activation of base and acid pumps to maintain the pH within a specified range.

        Args:
            ph (float): The current pH reading from the sensor.
            base_control (bool): If True, allows the base pump to be activated to increase pH.
            acid_control (bool): If True, allows the acid pump to be activated to decrease pH.

        Behavior:
            - If `base_control` is True and the pH is below the set point for base addition (`base_sp`),
            the base pump is activated and the acid pump is deactivated.
            - If `acid_control` is True and the pH is above the set point for acid addition (`acid_sp`),
            the acid pump is activated and the base pump is deactivated.
            - If both controls are False, both pumps are deactivated.
            - The function also logs the current pH balancing status and updates the system's status.
        """
        
        ph_base_sp = self.control_config["base_sp"]
        ph_acid_sp = self.control_config["acid_sp"]

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

    def __pre_phase_check(self, data: dict, trigger_type: str, start_trig_value: float, required_readings: float, start_counter: int, start_phase_1: bool, trigger_below = True):
        """
        Checks and activates pre-phase based on the specified trigger value conditions.

        Args:
            data (dict): Dictionary containing the current readings of sensors.
            trigger_type (str): Specifies which sensor's data ('ph' or 'do') to use as a trigger.
            start_trig_value (float): The value that the trigger must meet to consider starting the pre-phase.
            required_readings (int): Number of consecutive readings required to meet the condition before activating pre-phase.
            start_counter (int): The current count of consecutive readings meeting the pre-phase condition.
            start_phase_1 (bool): Indicates whether phase 1 has already been activated.
            trigger_below (bool): Determines if the trigger should be below (True) or above (False) the start_trig_value to start phase 1.

        Returns:
            bool: True if phase 1 can be activated, False otherwise.
        """
        curr_value = data[trigger_type]

        if (not start_phase_1):
            if (trigger_below and curr_value < start_trig_value) or (not trigger_below and curr_value > start_trig_value):
                start_counter += 1
                if start_counter >= required_readings - 1:
                    self.update_controller_consts("control_consts", "start_phase_1", "True")
                    start_phase_1 = True
                    print(f"Phase 1 activated by {trigger_type} {'below' if trigger_below else 'above'} {start_trig_value} for {required_readings} readings.")
                    logger.info(f"Phase 1 activated by {trigger_type} {'below' if trigger_below else 'above'} {start_trig_value} for {required_readings} readings.")
            else:
                start_counter = 0  # Reset counter if condition not met
            self.update_controller_consts("control_consts", "start_counter", start_counter)

        self.update_status()

        return start_phase_1
    
    def test_pre_phase_check(self, data: dict, trigger_type: str, start_trig_value: float, required_readings: float, start_counter: int, start_phase_1: bool, trigger_below = True):
        return self.__pre_phase_check(data, trigger_type, start_trig_value, required_readings, start_counter, start_phase_1, trigger_below)

    def __start_feed_check_bool(self, data: dict, trigger_type: str, start_feed_trig_value: float, required_readings: float, feed_counter: int, start_phase_1=True, trigger_below=False, start_feed=False):
        """
        Checks and determines if feeding should start based on sensor data exceeding/subceeding a set threshold.

        Args:
            data (dict): Dictionary containing the current readings of sensors.
            trigger_type (str): Specifies which sensor's data ('ph' or 'do') to use as a trigger for feeding.
            start_feed_trig_value (float): The value that the trigger must exceed or fall below to consider starting feed, depending on the logic of 'trigger_below'.
            required_readings (int): Number of consecutive readings required above (or below, if trigger_below is True) the threshold to start feeding.
            feed_counter (int): The current count of consecutive readings meeting the feed start condition.
            start_phase_1 (bool): Indicates whether phase 1 has been activated and feed checking should proceed.
            trigger_below (bool): Determines the logic for triggering feed; True means feeding starts when readings are below the threshold.

        Returns:
            bool: True if feed conditions are met and feeding can start, False otherwise.
        """
        curr_value = data[trigger_type]
        # Phase 1: check feed start conditions
        if start_phase_1 and (not start_feed):
            if (not trigger_below and curr_value >= start_feed_trig_value) or (trigger_below and curr_value <= start_feed_trig_value):
                feed_counter += 1
                if feed_counter >= required_readings:
                    self.update_controller_consts("control_consts", "start_feed", "True")
                    start_feed = True
                    print(f"Feed started by {trigger_type} {'above' if not trigger_below else 'below'} {start_feed_trig_value} for {required_readings} readings.")
                    logger.info(f"Feed started by {trigger_type} {'above' if not trigger_below else 'below'} {start_feed_trig_value} for {required_readings} readings.")
            else:
                feed_counter = 0  # Reset counter if condition not met
            self.update_controller_consts("control_consts", "feed_counter", feed_counter)

        self.update_status()

        return start_feed
    
    def test_start_feed_check_bool(self, data: dict, trigger_type: str, start_feed_trig_value: float, required_readings: float, feed_counter: int, start_phase_1=True, trigger_below = False, start_feed = False):
        return self.__start_feed_check_bool(data, trigger_type, start_feed_trig_value, required_readings, feed_counter, start_phase_1, trigger_below, start_feed)

    def __start_feed_check_der(self, trigger_type: str, feed_counter: float, derivs: list, csv_name: str, required_readings: int=5, deriv_window: int=5, der_positive=True, start_phase_1=True, start_feed=False):
        """
        Determines whether to initiate feed based on the derivative of sensor data, considering either positive or negative trends as specified.

        Args:
            trigger_type (str): Specifies which sensor's data ('ph' or 'do') to use for derivative calculation.
            required_readings (int): Number of consecutive readings required where the derivative matches the expected sign (positive or negative).
            feed_counter (int): Current count of consecutive readings matching the expected derivative condition.
            derivs (list): List of recently calculated derivatives.
            der_positive (bool): True if feed should start when the derivative is positive; False if it should start when the derivative is negative.
            deriv_window (int): Number of data points to use for calculating the derivative.
            start_phase_1 (bool): Indicates if phase 1 is active and derivative check can proceed.
            start_feed (bool): Current state of feeding, whether it has started or not.

        Returns:
            bool: True if feed should be started based on derivative criteria, False otherwise.
        """
        if start_phase_1 and not start_feed:
            feed_counter += 1
            if feed_counter >= deriv_window:
                # Calculate the derivative and adjust the sign if necessary
                new_derivative = calculate_derivative(trigger_type, csv_name, deriv_window)
                derivs.append(new_derivative)
                if not der_positive:
                    # Invert the derivatives to check for negative trends using the existing positive check logic
                    derivs = [-x for x in derivs]

                # Check if the derivatives meet the criteria for starting feed
                if isDerPositive(derivs, required_readings):
                    start_feed = True
                    self.update_controller_consts("control_consts", "start_feed", "True")
                    print("Derivative conditions met. Transitioning to Phase 2")
                    logger.info("Derivative conditions met. Transitioning to Phase 2")
                # Reset the counter and derivatives list after checking
                
            # Update the current state of the derivative checks
            self.update_controller_consts("control_consts", "feed_counter", feed_counter)
            self.update_controller_consts("control_consts", "derivs", derivs)

        self.update_status()
        return start_feed
    
    def test_start_feed_check_der(self, trigger_type: str, feed_counter: float, derivs: list, csv_name: str, required_readings: int=5, deriv_window: int=5, der_positive=True, start_phase_1=True, start_feed=False):
        return self.__start_feed_check_der(trigger_type, feed_counter, derivs, csv_name, required_readings, deriv_window, der_positive, start_phase_1, start_feed)

    def __control_pump_activation(self, data: dict, pump_name: str, feed_trigger_type: str, feed_trigger_upper_sp: float, feed_trigger_lower_sp: float,trigger_above = True):
        """
        Controls the activation of a specified pump based on the sensor data thresholds.

        Args:
            data (dict): Dictionary containing the current readings from sensors.
            pump_name (str): The name of the pump to be controlled.
            feed_trigger_type (str): Specifies which sensor's data ('ph' or 'do') is used as a trigger for the pump.
            feed_trigger_upper_sp (float): The upper setpoint that, if exceeded, may trigger the pump to activate or deactivate.
            feed_trigger_lower_sp (float): The lower setpoint that, if dropped below, may trigger the pump to activate or deactivate.
            trigger_above (bool): Determines the direction of triggering:
                - If True, the pump activates when the data exceeds the upper setpoint and deactivates below the lower setpoint.
                - If False, the pump activates when the data drops below the lower setpoint and deactivates above the upper setpoint.

        This method checks if the current sensor value meets the conditions set by `feed_trigger_upper_sp` and `feed_trigger_lower_sp`
        to control the specified pump. It activates the pump if the conditions are met and deactivates it otherwise, providing
        immediate feedback via logging.
        """

        current_value = data[feed_trigger_type]

        if (trigger_above and current_value >= feed_trigger_upper_sp) or (not trigger_above and current_value <= feed_trigger_lower_sp):
            self.pump_control(self.pumps[pump_name].control(True))
            print(f"{pump_name} pump on")
            logger.info(f"{pump_name} pump on")
        elif (trigger_above and current_value < feed_trigger_lower_sp) or (not trigger_above and current_value > feed_trigger_upper_sp):
            self.pump_control(self.pumps[pump_name].control(False))
            print(f"{pump_name} pump off")
            logger.info(f"{pump_name} pump off")

        self.update_status()

    def test_control_pump_activation(self, data: dict, pump_name: str, feed_trigger_type: str, feed_trigger_upper_sp: float, feed_trigger_lower_sp: float,trigger_above = True):
        self.__control_pump_activation(data, pump_name, feed_trigger_type, feed_trigger_upper_sp, feed_trigger_lower_sp, trigger_above)
   
    def __activate_antifoam_pump(self):
        """
        Activates the antifoam pump for one cycle every 2 hours from the start time in data.

        Parameters:
        data (dict): Dictionary containing the current readings of sensors.
        """
        start_time = get_control_constant(self.loop_id, self.control_id, "start_time")
        last_antifoam_edition = self.control_consts.get("last_antifoam_edition", 0)
        antifoam_edition_rate = self.control_config.get("antifoam_edition_rate", 2)
        current_time = time.time()

        # Check if the antifoam pump is on
        if self.pumps["antifoam_pump"].is_on():
            # Turn off the antifoam pump and update last_antifoam_edition with current_time
            self.pump_control(self.pumps["antifoam_pump"].control(False))
            self.update_controller_consts("control_consts", "last_antifoam_edition", current_time)
            print("Antifoam pump deactivated")
            logger.info("Antifoam pump deactivated")
        else:
            if last_antifoam_edition == 0:
                # Initialize last_antifoam_edition with start_time
                self.update_controller_consts("control_consts", "last_antifoam_edition", current_time)
            last_antifoam_edition = self.control_consts.get("last_antifoam_edition")

            elapsed_time = (current_time - last_antifoam_edition) / 3600  # Convert elapsed time to hours

            # Check if specified hours have passed since the last antifoam edition
            if elapsed_time >= antifoam_edition_rate:
                self.pump_control(self.pumps["antifoam_pump"].control(True))
                print("Antifoam pump activated")
                logger.info("Antifoam pump activated")
    
if __name__ == "__main__":
   
    c = FermentationController()
    
    while True:
        status, data = c.start_collection(control_status=False)
        print(data)
        time.sleep(3)

       
