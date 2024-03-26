# import usb.core

# dev = usb.core.find(idVendor=0x0403, idProduct=0x6001)

# if dev is None:
#     raise ValueError("USB device not found")

# ep = dev[0][(0,0)][0]
# # print(ep)

# if dev.is_kernel_driver_active(0):
#     dev.detach_kernel_driver(0)

# dev.reset()
# data = dev.read(ep.bEndpointAddress, 10)

# print(data)

# from pymodbus.client.serial import ModbusSerialClient
import pymodbus.client as ModbusClient

client = ModbusClient.ModbusSerialClient(port='/dev/ttyUSB0', baudrate=19200, stopbits=2, bytesize=8, parity='N')
client.connect()

res = client.read_holding_registers(method='rtu', address=2409, count=10, unit=1)
# res = client.read_input_registers(0, 1)

# rr = client.read_coils(1, 1, slave=1)

print(res)
print(res.registers)
print(res.decode)