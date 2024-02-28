import usb.core

def read_weight(device: usb.core, endpoint) -> int:
    data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
    weight = data[4] + (256 * data[5])

    return weight