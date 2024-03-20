import csv
import math
import serial
import sys
import time
import usb.core
import asyncio

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

class PumpController:
    """
    Controls the pump connected to an Arduino.
    """

    def __init__(self, port='/dev/ttyACM0', baudrate=57600):
        self.arduino = serial.Serial(port=port, baudrate=baudrate, timeout=1)

    def control_pump(self, turn_on):
        """
        Sends command to Arduino to control the pump.
        """
        command = '1' if turn_on else '0'
        self.arduino.write(command.encode())
    async def control_refill_pump(self):
        """
        Sends command to Arduino to control the refil pump.
        """
        command = '2'
        self.arduino.write(command.encode())
        await asyncio.sleep(122)
        command = '3'
        self.arduino.write(command.encode())

def read_csv_column(csv_path, start_row, end_row, col_index):
    """
    Extracts data from a specific column and range of rows in a CSV file.
    """
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        return [float(row[col_index]) for i, row in enumerate(reader) if start_row <= i+1 <= end_row]

async def main_loop(interval=60, m_0=100, csv_path='feed_data_v0-2_u-0.2_m0-5000.csv'):
    scale = Scale(0x0922, 0x8003)
    pump_controller = PumpController()
    weight_increases = read_csv_column(csv_path, 6, 614, 3)
    refill_task = None  # Initialize refill task
    start_time = time.time()
    last_weight = m_0

    for increase in weight_increases:
        current_time = time.time()
        elapsed_time = current_time - start_time
        current_weight = scale.get_weight()

        expected_weight = last_weight + increase
        print(f"Elapsed time: {elapsed_time:.2f}s, Current weight: {current_weight}, Expected weight: {expected_weight:.2f}")

        if current_weight - m_0 >= 950 and (refill_task is None or refill_task.done()):
            refill_task = asyncio.create_task(pump_controller.control_refill_pump()) # start the refill task

        if current_weight < expected_weight:
            pump_controller.control_pump(True)  # Start main pump
        else:
            pump_controller.control_pump(False)  # Stop main pump

        last_weight = expected_weight
        await asyncio.sleep(interval)  # Use asyncio.sleep here for async wait


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pump_controller = PumpController()
        pump_controller.control_pump(False)
        print("Program terminated")
