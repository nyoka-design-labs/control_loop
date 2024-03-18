### Setup virtual environment

- Create virtual environment in the root directory of the repo: [venv docs](https://docs.python.org/3/library/venv.html)

- Use pip to install libraries from docs/requirements.txt

- We ran into problems running the pyusb library on Mac OS and Windows, which is the main reason why we decided to use Ubuntu to run the control loop.

``` python
import usb.core

dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)

if (dev is None):
    raise ValueError("device not found")
```