from usb_devices.scale import Scale
import time
from threading import Thread

SCALE_DATA = None # data read from the scale
INTERVAL = 1 # time in seconds for each reading

def continous_read():
    scale = Scale(0x0922, 0x8003)
    global SCALE_DATA
    while True:
        SCALE_DATA = scale.read_weight()

def process_data():
    while True:
        if SCALE_DATA is not None:
            print(f"Weight: {SCALE_DATA} g")

        time.sleep(INTERVAL)


def main() -> None:
    data_t = Thread(target=continous_read)
    data_t.daemon = True
    data_t.start()

    process_t = Thread(target=process_data)
    process_t.daemon = True
    process_t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated")

if __name__ == '__main__':
    main()