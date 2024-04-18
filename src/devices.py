from usb_devices.scale import Scale
from usb_devices.ham_sensor import PH, DO
import time
from utils import add_to_csv

# initialize devices
scale = Scale(0x0922, 0x8003)
do_sensor = DO(port="/dev/ttyUSB1")
ph_sensor = PH(port="/dev/ttyUSB0")

def get_measurement():
    """
    Get the current measurement from all the devices.
    """

    # get data from devices
    weight = scale.get_weight()
    do = do_sensor.get_do()
    ph_reading = ph_sensor.get_tared_ph()
    ph = ph_sensor.get_ph()
    temperature = do_sensor.get_temperature()
    t = time.time()

    add_to_csv([weight, do, ph, ph_reading, temperature, t], "../../tests/first_run.csv")

    return {
        'time': t, # time of measurement
        'weight': weight,
        'do': do,
        'ph_reading': ph_reading, # ph reading adjusts true value for tare
        'ph': ph,
        'temp': temperature
    }

def tare(value: float):
    ph_sensor.update_tare_constant(value)

if __name__ == "__main__":
    print(get_measurement())