import serial
import time

# Replace with the correct port for your ESP32
port = '/dev/cu.usbserial-0001'
baudrate = 9600

try:
    esp = serial.Serial(port=port, baudrate=baudrate, timeout=1)
    time.sleep(2)  # Give some time for the ESP32 to reset after opening the serial port

    state = "1"
    pcu_id = "pcu1"
    command = state + pcu_id + '\n'

    print(f"Sending command: {command.encode()}")  # For debugging
    esp.write(command.encode())


    state = "1"
    pcu_id = "pcu1"
    command = state + pcu_id + '\n'

    print(f"Sending command: {command.encode()}")  # For debugging
    esp.write(command.encode())



    state = "3"
    pcu_id = "pcu1"
    command = state + pcu_id + '\n'

    print(f"Sending command: {command.encode()}")  # For debugging
    esp.write(command.encode())

    # # Optionally, read back any response from the ESP32
    # time.sleep(1)  # Wait a bit for response
    # if esp.in_waiting > 0:
    #     response = esp.read(esp.in_waiting).decode('utf-8')
    #     print(f"Response from ESP32: {response}")

    # esp.close()
except serial.SerialException as e:
    print(f"Error opening or communicating through serial port: {e}")