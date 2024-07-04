### Setup virtual environment

- Create virtual environment in the root directory of the repo called `env`: [venv docs](https://docs.python.org/3/library/venv.html)

- Once the virtual environment is activated, use pip to install libraries from docs/requirements.txt

`pip install -r docs/requirements.txt`

- To update the requirements file run the following command:

`pip freeze > docs/requirements.txt`

### Ubuntu setup

- We ran into problems running the pyusb library on Mac and Windows, which is the main reason why we decided to use Ubuntu to run the control loop.

- Ubuntu needs permission to access usb device.

``` bash
sudo vi /etc/udev/rules.d/98-dymo.rules
$ sudo cat /etc/udev/rules.d/98-dymo.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="0922", ATTR{idProduct}=="8003", MODE="666"
```

- Test to check if Pyusb can find USB device.

``` python
import usb.core

# replace the following id's
dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

if (dev is None):
    raise ValueError("device not found")
```