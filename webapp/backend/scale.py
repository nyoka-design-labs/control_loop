import usb.core
import sys
import time
import csv
import time

SCALE_DATA = None

class Scale:
    """
    Represents all USB devices.
    """

    def __init__(self, vid: hex, pid: hex) -> None | ValueError:
        """
        Locates USB device and initializes attributes.
        
        Paramaters:
            vid: Vendor ID of USB device
            pid: Product ID of USB device
        """

        self.dev = usb.core.find(idVendor=vid, idProduct=pid)

        if self.dev is None:
            raise ValueError('Device not found')

        self.ep = self.dev[0][(0,0)][0]
        self.ep_address = self.ep.bEndpointAddress
        self.ep_packet_size = self.ep.wMaxPacketSize
        
    def read_weight(self) -> int:
        """
        Returns the weight read by the scale.
        """
        if self.dev.is_kernel_driver_active(0):
            self.dev.detach_kernel_driver(0)

        try:
            data = self.dev.read(self.ep_address, self.ep_packet_size)
        except:
            sys.exit("Data not read")

        weight = data[4] + (256 * data[5])

        return weight

def add_to_csv(data: list):
    with open('test.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)


def continous_read():
    scale = Scale(0x0922, 0x8003)
    global SCALE_DATA
    while True:
        weight = scale.read_weight()

        if weight is not None:
            SCALE_DATA = weight
            add_to_csv({SCALE_DATA, time.time()})

def process_data():
    while True:
        if SCALE_DATA is not None:
            print(f"Weight: {SCALE_DATA} g")
            add_to_csv(SCALE_DATA)

        time.sleep(5)

def get_current_weight():
    while True:
        if SCALE_DATA is not None:
            return SCALE_DATA
        time.sleep(1)