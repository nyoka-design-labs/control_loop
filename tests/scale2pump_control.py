"""
Script used for testing of only the scale and pump control loop.
"""

from cv2 import repeat
import usb.core
import sys
import threading
import time
from datetime import datetime
import csv
import math
import serial
import time
import polynomialFunc as pf

class Scale:
    """
    Represents the Dymo M25 scale.
    """

    def __init__(self, vid: hex, pid: hex) -> None | ValueError:
        """
        Locates scale device and initializes attributes.
        
        Paramaters:
            vid: Vendor ID of USB device
            pid: Product ID of USB device
        """

        self.name = f"scale_{pid}"
        self.dev = usb.core.find(idVendor=vid, idProduct=pid)

        if self.dev is None:
            raise ValueError('Device not found')
        
        endpoint = self.dev[0][(0,0)][0]
        self.ep_address = endpoint.bEndpointAddress
        self.ep_packet_size = endpoint.wMaxPacketSize
    
    def get_weight(self) -> int:
        """
        Returns weight updated by continuous read thread.
        """

        if self.dev.is_kernel_driver_active(0):
            self.dev.detach_kernel_driver(0)

        try:
            self.dev.reset()
            data = self.dev.read(self.ep_address, self.ep_packet_size)
        except:
            sys.exit("Data not read")

        return data[4] + (256 * data[5])

interval = 60

m_0 = 10000

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=1)

scale = Scale(0x0922, 0x8003)

def get_current_weight():
    return scale.get_weight()

def extract_specific_cells(csv_path, start_row, end_row, col):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        # Skip the first start_rows - 1 rows
        for _ in range(start_row - 1):
            next(reader)
        # Extract the data from the specific column
        data = [row[col] for row in reader][:(end_row - start_row + 1)] 
    return data

def get_expected_weight(time_arg):
    x0 = 86
    mu = 0.005

    return x0*math.exp(mu*time_arg)

def control_pump(turn_on):
    # Send command to Arduino to control the pump
    command = '1' if turn_on else '0'
    arduino.write(command.encode())

def loop():
    start_time = time.time()
    i = 0
    last_weight = m_0
    weight_drops_by_min = extract_specific_cells('feed_data_v0-2_u-0.2_m0-5000.csv', 6, 614, 3)
    while i in range(0, len(weight_drops_by_min)): 
        current_time = time.time()
        elapsed_time = current_time - start_time

        current_weight = get_current_weight()
        # expected_weight = get_expected_weight(elapsed_time)
        expected_weight = last_weight - float(weight_drops_by_min[i])

        print(f"Elapsed time: {elapsed_time:.2f}s, Current weight: {current_weight}, Expected weight: {expected_weight:.2f}")
        add_to_csv([current_weight, round(expected_weight, 2)])

        # if current_weight < 50:
        #     control_pump(False)
        #     arduino.write('2'.encode())
        #     time.sleep(122)
        #     arduino.write('3'.encode())
        #     last_weight = get_current_weight()
        #     control_pump(True)
        #     time.sleep(interval)
        #     continue

        if current_weight >= expected_weight:
            control_pump(True)  # Turn on the pump
        elif current_weight < expected_weight:
            control_pump(False)  # Turn off the pump

        last_weight = expected_weight # Update the last weight

        # Wait for the next interval before the next iteration
        i += 1
        time.sleep(interval)
    
    control_pump(True)  # Turn off the pump

def add_to_csv(data: list):
    # current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # data = [current_datetime, number]

    with open('test.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

if __name__ == "__main__":
    process_t = threading.Thread(target=loop)
    process_t.daemon = True
    process_t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        control_pump(False)
        print("Program terminated")
