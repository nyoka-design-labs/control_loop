import usb.core

def find_usb(vid: hex, pid: hex) -> usb.core | ValueError:
    """
    Find USB device and returns USB object.
    
    Paramaters:
        vid: Vendor ID of USB device
        pid: Product ID of USB device
    """
    dev = usb.core.find(idVendor=vid, idProduct=pid)

    if dev is None:
        raise ValueError('Device not found')
    
    return dev

def read_weight(device: usb.core, endpoint) -> int:
    """
    Returns the weight read by the scale.
    """
    data = device.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
    weight = data[4] + (256 * data[5])

    return weight