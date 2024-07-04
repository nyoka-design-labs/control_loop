from devices.scale import Scale, USS_Scale
from devices.ham_sensor import PH, DO
import time
from resources.utils import *
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

class DeviceManager:
    """
    Represents a device manager.
    """

    def __init__(self, loop_id: str, control_id: str, data_types: list, loop_devices: list, csv_name: str) -> None:
        self.loop_id = loop_id
        self.control_id = control_id
        self.data_types = data_types + ["time", "date", "time_of_day", "type"]
        self.csv_name = csv_name
        self.start_time = 0
        self.index = 0

        # Load all devices information
        curr_directory = os.path.dirname(__file__)
        self.ALL_DEVICES_DIR = os.path.join(curr_directory, "resources", "all_devices.json")
        self.__delete()
        with open(self.ALL_DEVICES_DIR, "r") as f:
            self.all_devices = json.load(f)['devices']

        self.devices = self.__init_devices(loop_devices)

        self.loop_control_file = f"{self.loop_id}-{self.control_id}-{datetime.now().strftime('%Y%m%d')}.json"
        self.__init_loop_control_file()

    def __delete(self) -> None:
        """
        Closes all the devices.
        """

        with open(self.ALL_DEVICES_DIR, "r+") as f:
            file_data = json.load(f)

            for idx in range(len(file_data["devices"])):
                file_data["devices"][idx]["port"] = ""
                
            f.close()

        with open(self.ALL_DEVICES_DIR, "w") as f:
            json.dump(file_data, f, indent=4)
            f.close()

    def __init_devices(self, loop_devices):
        dev2port = []
        idt = 0
        if loop_devices:
            try:
                for name in loop_devices:
                    if self.data_types[idt] == "temp":
                        idt += 1
                    port = self.__find_usb_serial_port(name, self.data_types[idt])
                    dev2port.append((name, port))
                    idt += 1
            except SerialPortNotFoundException as e:
                print(e)

            devices = []
            for name, port in dev2port:
                if name == "dymo_scale":
                    devices.append(DEV_CONTRUCTORS[name](0x0922, 0x8003))
                else:
                    devices.append(DEV_CONTRUCTORS[name](port))
            return devices

    def __init_loop_control_file(self):
        if not os.path.exists(self.loop_control_file):
            with open(self.loop_control_file, "w") as f:
                json.dump({"start_time": self.start_time, "test_data_index": self.index}, f)

    def update_loop_control_file(self, key, value):
        with open(self.loop_control_file, "r+") as f:
            data = json.load(f)
            data[key] = value
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

    def get_loop_control_value(self, key):
        with open(self.loop_control_file, "r") as f:
            data = json.load(f)
            return data[key]

    def get_measurement(self, save_data=True) -> dict:
        devices_data = []
        for dev in self.devices:
            result = dev()
            if isinstance(result, tuple):
                devices_data.extend(result)
            else:
                devices_data.append(result)

        if self.start_time <= 0:
            self.start_time = time.time()
            self.update_loop_control_file("start_time", self.start_time)
            elapsed_time = 0
        else:
            elapsed_time = (time.time() - self.start_time) / 3600

        devices_data.append(round(elapsed_time, 8))
        devices_data.append(datetime.now().strftime('%d-%m-%Y'))
        devices_data.append(datetime.now().strftime('%H:%M:%S'))
        devices_data.append("data")

        if save_data:
            add_to_csv(devices_data, f"{self.csv_name}.csv", self.data_types)

        return dict(zip(self.data_types, devices_data))

    def test_get_measurement(self, test_name):
        measurement = self.test_data[test_name][self.index]
        if self.start_time <= 0:
            self.start_time = time.time()
            self.update_loop_control_file("start_time", self.start_time)
            elapsed_time = 0
        else:
            elapsed_time = (time.time() - self.start_time) / 3600

        measurement["time"] = elapsed_time
        self.index += 1
        self.update_loop_control_file("test_data_index", self.index)
        current_time = time.time()
        current_datetime = datetime.fromtimestamp(current_time)
        measurement['time_of_day'] = current_datetime.strftime('%H:%M:%S')
        measurement['date'] = current_datetime.strftime('%Y-%m-%d')

        add_test_data_to_csv(measurement, f"{self.csv_name}.csv")
        return measurement

    def __find_usb_serial_port(self, device_name: str, data_type: str) -> str | SerialPortNotFoundException:
        if device_name == "dymo_scale":
            return ""

        func = lambda x: str(hex(x))[2:].zfill(4)
        ports = serial.tools.list_ports.comports()
        ports = list(filter(lambda x: x.vid is not None and x.pid is not None, ports))

        for idx, dev in enumerate(self.all_devices):
            if dev['name'] == device_name and dev["port"] == "":
                ser_ports = list(filter(lambda x: func(x.vid) == dev['vendor_id'] and func(x.pid) == dev['product_id'], ports))
                ser_ports = set(map(lambda x: x.device, ser_ports))
                occ_ports = self.__get_occupied_ports()

                try:
                    avail_ports = (ser_ports - occ_ports)
                    sorted_avail_ports = sorted(avail_ports, key=lambda x: int(x.split('USB')[1]))
                    chosen_port = sorted_avail_ports[0]
                except:
                    raise SerialPortNotFoundException(f"Serial port for {device_name} not found.")

                self.__update_device_port(chosen_port, data_type, idx)
                return chosen_port

        raise SerialPortNotFoundException(f"Serial port for {device_name} not found.")

    def __get_occupied_ports(self) -> set:
        return set(map(lambda x: x['port'], filter(lambda x: x['port'] != "", self.all_devices)))

    def __update_device_port(self, port: str, data_type: str, idx: int) -> None:
        self.all_devices[idx]["port"] = port
        self.all_devices[idx]["data_type"] = data_type
        with open(self.ALL_DEVICES_DIR, "w") as f:
            json.dump({"devices": self.all_devices}, f, indent=4)

if __name__ == "__main__":
    # Example values, these should be received via MQTT
    data_types = ["do", "feed_weight"]
    loop_devices = ["do_sensor", "uss_scale"]
    csv_name = "sensor_data"
    loop_id = "fermentation_loop"
    control_id = "test_loop"

    dm = DeviceManager(loop_id, control_id, data_types, loop_devices, csv_name)
    while True:
        print(dm.get_measurement())
        time.sleep(10)