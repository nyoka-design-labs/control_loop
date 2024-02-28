import serial 
import time 
arduino = serial.Serial(port='/dev/tty.usbmodem1401', baudrate=115200, timeout=.5) 
def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 
while True: 
    num = input("Enter a number: ") # Taking input from user 
    value = write_read(num) 
    print(value.decode().strip())  # decoding and stripping to remove any trailing newline or spaces
