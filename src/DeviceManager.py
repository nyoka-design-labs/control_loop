from usb_devices.scale import Scale, USS_Scale
from usb_devices.ham_sensor import PH, DO
import time
from utils import add_to_csv
import json
import os
import serial.tools.list_ports
from exceptions import SerialPortNotFoundException

DEV_CONTRUCTORS = {
    "uss_scale": USS_Scale,
    "dymo_scale": Scale,
    "do_sensor": DO,
    "ph_sensor": PH
}

curr_directory = os.path.dirname(__file__)
CONSTANTS_DIR = f"{curr_directory}/constants.json"

class DeviceManager:
    """
    Represents a device manager.
    """

    def __init__(self, loop_id: str) -> None:
        self.delete()
        self.loop_id = loop_id
        names = self.__get_loop_devices()

        try:
            # finds the serial port for each device and creates dict
            dev2port = {name: self.__find_usb_serial_port(name) for name in names}
        except SerialPortNotFoundException as e:
            print(e)
            return

        self.devices = []
        for name, port in dev2port.items():
            # calling all device constructors
            self.devices.append(DEV_CONTRUCTORS[name](port))

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

    def get_measurement(self, save_data=False) -> dict:
        """
        Get the current measurement from all the devices.
        """

        # collect data from each device
        devices_data = list(map(lambda dev: dev(), self.devices))
        data_headers = self.__get_loop_data_type()

        if save_data:
            add_to_csv(devices_data, "data.csv", data_headers)

        return dict(zip(data_headers, devices_data))

    
    def __find_usb_serial_port(self, device_name: str) -> str | SerialPortNotFoundException:
        """
        Returns the serial port to use for the device.
        """

        func = lambda x: str(hex(x))[2:].zfill(4)

        ports = serial.tools.list_ports.comports()

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
                    chosen_port = (ser_ports - occ_ports).pop()
                except:
                    raise SerialPortNotFoundException(f"Serial port for {device_name} not found.")
                
                # update the current device port
                self.__update_device_port(chosen_port, idx)
                return chosen_port

        raise SerialPortNotFoundException(f"Serial port for {device_name} not found.")

    def __get_loop_devices(self) -> list:
        """
        Gets the devices in the specified loop.
        """

        f = open(CONSTANTS_DIR)
        loops = json.load(f)['loop']
        f.close()

        return list(filter(lambda x: x['name'] == self.loop_id, loops))[0]['devices']
    
    def __get_loop_data_type(self) -> list:
        """
        Gets the data type for the specified loop.
        """

        f = open(CONSTANTS_DIR)
        loops = json.load(f)['loop']
        f.close()

        return list(filter(lambda x: x['name'] == self.loop_id, loops))[0]['data_type']

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
    
    def __update_device_port(self, port: str, idx: int) -> None:
        with open(CONSTANTS_DIR, "r+") as f:
            file_data = json.load(f)
            file_data["devices"][idx]["port"] = port
            f.seek(0)
            json.dump(file_data, f, indent = 4)
            f.close()

if __name__ == "__main__":
    dm = DeviceManager("fermentation_loop")
    print(dm.get_measurement())
