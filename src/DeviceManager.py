from devices.scale import Scale, USS_Scale
from devices.ham_sensor import PH, DO
import time
from resources.utils import add_to_csv, load_test_data
import json
import os
import serial.tools.list_ports
from resources.exceptions import SerialPortNotFoundException
from resources.google_api.sheets import save_to_sheet
from datetime import datetime

DEV_CONTRUCTORS = {
    "uss_scale": USS_Scale,
    "dymo_scale": Scale,
    "do_sensor": DO,
    "ph_sensor": PH
}

curr_directory = os.path.dirname(__file__)
# CONSTANTS_DIR = f"{curr_directory}/resources/constants.json"
CONSTANTS_DIR = os.path.join(curr_directory, "resources", "constants.json")
TEST_DATA_DIR = os.path.join(curr_directory, "resources", "test_data.json")
test_data = load_test_data(TEST_DATA_DIR)

class DeviceManager:
    """
    Represents a device manager.
    """

    def __init__(self, loop_id: str) -> None:
        self.test_data = test_data
        self.index = 0
        self.start_time = None
        self.delete()
        self.loop_id = loop_id
        names = self.__get_loop_devices()
        dev2port = []
        data_types = self.__get_loop_data_type()
        idt = 0
        try:
            # finds the serial port for each device and creates dict
            for name in names:
                if data_types[idt] == "temp":
                    idt += 1
                port = self.__find_usb_serial_port(name, data_types[idt])
                dev2port.append((name, port))
                idt += 1
        except SerialPortNotFoundException as e:
            print(e)
            return

        self.devices = []
        for name, port in dev2port:
            # calling all device constructors
            if name == "dymo_scale":
                self.devices.append(DEV_CONTRUCTORS[name](0x0922, 0x8003))
            else:
                self.devices.append(DEV_CONTRUCTORS[name](port))

        # self.devices = [USS_Scale(port="/dev/ttyUSB0"), Scale(0x0922, 0x8003)]

    def delete(self) -> None:
        """
        Closes all the devices.
        """

        with open(CONSTANTS_DIR, "r+") as f:
            file_data = json.load(f)

            for idx in range(len(file_data["devices"])):
                file_data["devices"][idx]["port"] = ""
                
            f.close()

        with open(CONSTANTS_DIR, "w") as f:
            json.dump(file_data, f, indent=4)
            f.close()

    def get_measurement(self, save_data=True) -> dict:
        

        # Collect data from each device
        devices_data = []
        for dev in self.devices:
            result = dev()

            if isinstance(result, tuple):
                devices_data.extend(result)  # This handles multiple return values
            else:
                devices_data.append(result)

        data_headers = self.__get_loop_data_type()

        # elapsed time
        if self.start_time is None:
            self.start_time = time.time()
            elapsed_time = 0
        else:
            elapsed_time = (time.time() - self.start_time) / 3600

        data_headers.append("time")
        devices_data.append(round(elapsed_time, 6))
        
        # date
        data_headers.append("date")
        devices_data.append(datetime.now().strftime('%d-%m-%Y'))
        
        # time of day
        data_headers.append("time_of_day")
        devices_data.append(datetime.now().strftime('%H:%M:%S'))
        
        # start time
        data_headers.append("start_time")
        devices_data.append(self.start_time)

        # type of information being sent to frontend
        data_headers.append("type")
        devices_data.append("data")



        csv_name = "fermentation_05-21-2024"

        if save_data:
            add_to_csv(devices_data, f"{csv_name}.csv", data_headers)
            save_to_sheet(devices_data, data_headers, csv_name) ## WILL BE USED HERE

        # print(data_headers)
        # print(devices_data)

        return dict(zip(data_headers, devices_data))

    def test_get_measurement(self, test_name):
        measurement = self.test_data[test_name][self.index]
        self.index += 1
        return measurement


    def __find_usb_serial_port(self, device_name: str, data_type: str) -> str | SerialPortNotFoundException:
        """
        Returns the serial port to use for the device.
        """

        if device_name == "dymo_scale":
            return ""

        func = lambda x: str(hex(x))[2:].zfill(4)

        ports = serial.tools.list_ports.comports()
        ports = list(filter(lambda x: x.vid is not None and x.pid is not None, ports))

        f = open(CONSTANTS_DIR)
        devs = json.load(f)['devices']
        for idx, dev in enumerate(devs):
            if dev['name'] == device_name and dev["port"] == "":
                # find active serial ports
                ser_ports = list(filter(lambda x: func(x.vid) == dev['vendor_id'] and func(x.pid) == dev['product_id'], ports))
                ser_ports = set(map(lambda x: x.device, ser_ports))
                # find occupied ports
                occ_ports = self.__get_occupied_ports()

                try:
                    # choose port that is not being used
                    avail_ports = (ser_ports - occ_ports)
                    sorted_avail_ports = sorted(avail_ports, key=lambda x: int(x.split('USB')[1]))
                    chosen_port = sorted_avail_ports[0]
                except:
                    raise SerialPortNotFoundException(f"Serial port for {device_name} not found.")
                
                # update the current device port
                self.__update_device_port(chosen_port, data_type, idx)

                return chosen_port

        raise SerialPortNotFoundException(f"Serial port for {device_name} not found.")

        # if device_name == "uss_scale":
        #     chosen_port = "/dev/ttyUSB0"
        #     self.__update_device_port(chosen_port, 0)
        #     return chosen_port
        # elif device_name == "do_probe":
        #     chosen_port = "/dev/ttyUSB1"
        #     self.__update_device_port(chosen_port, 5)
        #     return chosen_port
        # elif device_name == "ph_probe":
        #     chosen_port = "/dev/ttyUSB2"
        #     self.__update_device_port(chosen_port, 6)
        #     return chosen_port

    def __get_loop_devices(self) -> list:
        """
        Gets the devices in the specified loop.
        """

        f = open(CONSTANTS_DIR)
        loops = json.load(f)['loop']
        f.close()
        devices = list(filter(lambda x: x['loop_id'] == self.loop_id, loops))[0]['devices']
        devices = list(filter(lambda dev: dev != "temp_sensor", devices))
        # print(devices)
        return devices
    
    def __get_loop_data_type(self) -> list:
        """
        Gets the data type for the specified loop.
        """

        f = open(CONSTANTS_DIR)
        loops = json.load(f)['loop']
        f.close()

        return list(filter(lambda x: x['loop_id'] == self.loop_id, loops))[0]['data_type']

    def __get_all_device_names(self) -> set:
        """
        Gets all the device names from the constants file.
        """

        f = open(CONSTANTS_DIR)
        devs = json.load(f)['devices']
        f.close()

        return [devs[i]['name'] for i in range(len(devs))]
    
    def __get_occupied_ports(self) -> set:
        """
        Gets all the occupied ports from the constants file.
        """

        f = open(CONSTANTS_DIR)
        devs = json.load(f)['devices']
        f.close()

        return set(map(lambda x: x['port'], filter(lambda x: x['port'] != "", devs)))
    
    def __update_device_port(self, port: str, data_type: str, idx: int) -> None:
        with open(CONSTANTS_DIR, "r+") as f:
            file_data = json.load(f)
            file_data["devices"][idx]["port"] = port
            file_data["devices"][idx]["data_type"] = data_type
            f.seek(0)
            json.dump(file_data, f, indent = 4)
            f.close()

if __name__ == "__main__":
    dm = DeviceManager("fermentation_loop")
    while True:
        # print(dm.test_get_measurement("test_data_1"))
        print(dm.get_measurement())
        time.sleep(3)
