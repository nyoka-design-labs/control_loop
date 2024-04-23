import usb.core
import serial
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
    
class USS_Scale:
    """
    """

    def __init__(self, port) -> None:
        self.conn = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=None
        )

    def get_weight(self):
        """
        """

        self.conn.reset_input_buffer()  # Flush the input buffer to remove old data
        data = self.conn.readline().decode().strip()  # Read the latest line and decode from bytes to string
        return float(data[1:-1]) # slice represents 5 digit value including tenths digit

if __name__ == "__main__":
    # example usage of Scale class
    scale = USS_Scale(port="/dev/ttyUSB0")

    try:
        while True:
            print(f"Weight: {scale.get_weight()} g")
            time.sleep(3)
    except KeyboardInterrupt:
        print("Program terminated")
