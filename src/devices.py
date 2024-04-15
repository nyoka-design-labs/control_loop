from usb_devices.scale import Scale
from usb_devices.ham_sensor import Sensor
import time
from utils import add_to_csv

# initialize devices
# scale = Scale(0x0922, 0x8003)
sensor = Sensor(type="do", port="/dev/ttyUSB0")
sensor_ph = Sensor(type="ph", port="/dev/ttyUSB1")

def get_measurement():
    """
    Get the current measurement from all the devices.
    """

    # get data from devices
    # weight = scale.get_weight()
    do = sensor.get_data() + 9.5
    ph_reading = sensor_ph.get_reading()*0.977 + 0.147
    ph = sensor_ph.get_data()
    temperature = sensor_ph.get_temp()
    t = time.time()

    # add_to_csv([do, ph, temperature, t], "../../tests/data.csv")

    return {
        'time': t, # time of measurement
        # 'weight': weight,
        'do': do,
        'ph_reading': ph_reading, # ph reading adjusts true value for tare
        'ph': ph,
        'temp': temperature
    }

def tare(sensor_type: str, value: float):
    if (sensor_type == "ph"):
        sensor_ph.tare_ph(value)

if __name__ == "__main__":
    print(get_measurement())