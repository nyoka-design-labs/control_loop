import usb.core
import sys
import time

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


if __name__ == "__main__":
    # example usage of Scale class
    scale = Scale(0x0922, 0x8003)

    try:
        while True:
            print(f"Weight: {scale.get_weight()} g")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated")
