import usb.core
import serial
import sys
import time
import os
curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..")
sys.path.append(SRC_DIR)
from resources.logging_config import logger
import traceback
from resources.utils import *

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
            data = data[4] + (256 * data[5])
        except:
            data = -1

        return data
    
    def __call__(self, *args, **kwds) -> float:
        return self.get_weight()
    
class USS_Scale:
    """
    Represents the US Solids scales.
    """

    def __init__(self, port) -> None:
        self.port = port
        self.conn = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=None
        )

    def __call__(self, *args, **kwds) -> float:
        try:
            return self.get_weight()
        except Exception as e:
            print(f"failed to get weight: \n for port {self.port}, \n{e}")
            logger.error(f"Error in __call__ for USS scale: \n for port {self.port}, \n {e}\n{traceback.format_exc()}")

    def get_weight(self) -> float:
        """
        Read the weight from the scale.
        """

        self.conn.reset_input_buffer()  # Flush the input buffer to remove old data
        reading = self.conn.readline().decode().strip()  # Read the latest line and decode from bytes to string

        try:
            data = float(reading[1:-1])
        except ValueError:
            # data not properly read from scale
            data = -1

        return data

if __name__ == "__main__":
    # example usage of Scale class
    # scale = Scale(vid=0x0922, pid=0x8003)
    uss_scale = USS_Scale("/dev/ttyUSB2")

    try:
        while True:
            print(f"Weight: {uss_scale.get_weight()} g")
            time.sleep(3)
    except KeyboardInterrupt:
        print("Program terminated")
