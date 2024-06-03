### Setup virtual environment

- Create virtual environment in the root directory of the repo called `env`: [venv docs](https://docs.python.org/3/library/venv.html)

- Once the virtual environment is activated, use pip to install libraries from docs/requirements.txt

`pip install -r docs/requirements.txt`

- To update the requirements file run the following command:

`pip freeze > docs/requirements.txt`

### Useful commands

- `sudo dmesg | grep tty`: shows connection log of devices connected to the serial ports
- `lsusb`: list all usb devices connected along with their vendor and product ids

### Ubuntu setup

- Ubuntu needs permission to access usb device. Create a new .rules files in the rules.d directory for 

```bash
$ sudo cat /etc/udev/rules.d/98-dymo.rules
SUBSYSTEM=="usb", ATTRS{idVendor}=="0922", ATTRS{idProduct}=="8004", MODE="666"
```

- Test to check if Pyusb can find USB device.

```python
import usb.core

# replace the following id's
dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

if (dev is None):
    raise ValueError("device not found")
```