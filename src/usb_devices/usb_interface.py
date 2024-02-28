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