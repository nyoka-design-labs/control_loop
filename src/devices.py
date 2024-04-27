from usb_devices.scale import Scale, USS_Scale
from usb_devices.ham_sensor import PH, DO
import time
from utils import add_to_csv
import datetime

# initialize devices
scale1 = USS_Scale(port="/dev/ttyUSB2")
scale2 = USS_Scale(port="/dev/ttyUSB3")
# scale3 = USS_Scale(port="/dev/ttyUSB4")
do_sensor = DO(port="/dev/ttyUSB0")
ph_sensor = PH(port="/dev/ttyUSB1")

i = 0

def get_measurement():
    """
    Get the current measurement from all the devices.
    """
    
    # get data from devices
    weight_buff = scale1.get_weight()
    weight_lys = scale2.get_weight()

    do = do_sensor.get_do()
    ph_reading = ph_sensor.get_tared_ph()
    ph = ph_sensor.get_ph()
    temperature = ph_sensor.get_temp()

    t = time.time()

    add_to_csv([datetime.datetime.now(), weight_buff, weight_lys, do, ph, temperature], "data.csv", ['time', 'weight_buff', 'weight_lys', 'do', 'ph', 'temp'])

    return {
        'time': t, # time of measurement
        'weight_buff': weight_buff,
        'weight_lys': weight_lys,
        'do': do,
        'ph_reading': ph_reading, # ph reading adjusts true value for tare
        'ph': ph,
        'temp': temperature
    }

def tare(value: float):
    ph_sensor.update_tare_constant(value)

if __name__ == "__main__":
    while True:
        print(get_measurement())
        time.sleep(2)