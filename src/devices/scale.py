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
from serial.serialutil import SerialException

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

    def __init__(self, port):
            """
            Initialize the serial connection to the scale.
            """
            self.port = port
            self.conn = None
            self.connect()

    def connect(self):
        """
        Attempt to connect to the scale.
        """
        try:
            self.conn = serial.Serial(
                port=self.port,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
        except SerialException as e:
            print(f"Failed to initialize USS_Scale on port {self.port}: {e}")
            self.conn = None
    def __call__(self):
        """
        Return the weight or try reconnecting if disconnected.
        """
        weight = self.get_weight()
        if weight == -1 and self.conn is None:
            self.connect()  # Attempt to reconnect only if disconnected
        return weight

    def get_weight(self):
        """
        Read the weight from the scale.
        If the scale is disconnected, return -1 and attempt to reconnect.
        """
        if self.conn is not None:
            try:
                self.conn.reset_input_buffer()  # Clear buffer to ensure fresh data
                reading = self.conn.readline().decode().strip()
                reading = float(reading[1:-1])
                hello = True
                return reading
            except Exception as e:
                print(f"Error reading from USS_Scale on port {self.port}: {e}")
                # Attempt to reconnect in case of failure
                self.conn = None
        return -1  # Return -1 if disconnected or on read failure



if __name__ == "__main__":
    # example usage of Scale class
    # scale = Scale(vid=0x0922, pid=0x8003)
    uss_scale = USS_Scale("/dev/tty.usbserial-1140")

    try:
        while True:
            print(f"Weight: {uss_scale()} g")
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n Program terminated")
