from usb_devices.scale import Scale
from usb_devices.ham_sensor import Sensor
import time

# initialize devices
scale = Scale(0x0922, 0x8003)
sensor = Sensor(type="do")

def get_measurement():
    """
    Get the current measurement from all the devices.
    """

    # get data from devices
    weight = scale.get_weight()
    do = sensor.get_data()
    temperature = None

    return {
        'time': time.time(), # time of measurement
        'weight': weight,
        'do': do,
        'temp': temperature
    }