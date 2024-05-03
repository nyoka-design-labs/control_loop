from usb_devices.scale import Scale, USS_Scale
from usb_devices.ham_sensor import PH, DO
import time
from utils import add_to_csv
import json
import serial.tools.list_ports

# initialize devices
# scale2 = USS_Scale(port="/dev/ttyUSB0")
# scale1 = Scale(pid=0x8003, vid=0x0922)
# scale3 = USS_Scale(port="/dev/ttyUSB4")
# do_sensor = DO(port="/dev/ttyUSB2")
# ph_sensor = PH(port="/dev/ttyUSB1")

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

    def __init__(self, loop_id: str) -> None:
        # names = self.__get_all_device_names()

        # self.devices = list(filter(lambda x: x in names, devs))
        # self.loop_id = loop_id
        # self.devices = self.__get_loop_devices()
        # map(lambda x: self.__find_usb_serial_port(x), self.devices)
        print(self.__get_occupied_ports())

    def get_measurement(self):
        pass

    def __find_usb_serial_port(self, device_name: str) -> str:
        """
        Returns the serial port to use for the device.
        """

        ports = serial.tools.list_ports.comports()

        f = open("constants.json")
        devs = json.load(f)['devices']

        for dev in devs:
            if dev['name'] == device_name and dev["port"] == "":
                # find active serial ports
                ser_ports = set(filter(lambda x: x.vid == dev['vid'] and x.pid == dev['pid'], ports))
                # find occupied ports
                occ_ports = self.__get_occupied_ports()
                # choose port that is not beign used
                chosen_port = (ser_ports - occ_ports).pop()
                break

        # for port in ports:
        #     if port.vid == vendor_id and port.pid == product_id:
        #         return port.device
        return None

    def __get_loop_devices(self) -> list:
        """
        Gets the devices in the loop.
        """

        f = open("constants.json")
        loops = json.load(f)['loop']
        f.close()

        return list(filter(lambda x: x['name'] == self.loop_id, loops))[0]['devices']

    def __get_all_device_names(self) -> set:
        """
        Gets all the device names from the constants file.
        """

        f = open("constants.json")
        devs = json.load(f)['devices']
        f.close()

        return [devs[i]['name'] for i in range(len(devs))]
    
    def __get_occupied_ports(self) -> list:
        """
        """

        f = open("constants.json")
        devs = json.load(f)['devices']
        f.close()

        return list(map(lambda x: x['port'], filter(lambda x: x['port'] != "", devs)))
    
    def update_device_port(self):
        with open("test.json", "r+") as f:
            file_data = json.load(f)
            # file_data["person"].append({"name": "Mervin", "age": 20, "city": "New York"})
            # f.seek(0)
            # json.dump(file_data, f, indent = 4)
            file_data["person"][0]["name"] = "Mervin"
            f.seek(0)
            json.dump(file_data, f, indent = 4)


# def get_measurement(start_time: time.time):
#     """
#     Get the current measurement from all the devices.
#     """
  
#     # get data from devices
#     feed_weight = scale1.get_weight()
#     base_weight = scale2.get_weight()

#     # do = do_sensor.get_do()
#     do = 60
#     ph_reading = ph_sensor.get_tared_ph()
#     ph = ph_sensor.get_ph()
#     temperature = ph_sensor.get_temp()

#     t = time.time()-start_time

#     add_to_csv([feed_weight, base_weight, do, ph, temperature, t, start_time], "DO_ferementation_30-04-2024.csv", header = ['feed_weight', 'base_weight','do', 'ph', 'temperature', 'time', 'start_time'])

#     return {
#         'time': t, # time of measurement
#         'feed_weight': feed_weight,
#         'base_weight': base_weight,
#         'do': do,
#         'ph_reading': ph_reading, # ph reading adjusts true value for tare
#         'ph': ph,
#         'temp': temperature
#     }

# def tare(value: float):
#     ph_sensor.update_tare_constant(value)

if __name__ == "__main__":
    dm = DeviceManager("concentration_loop")
    # dm.update_device_port()
