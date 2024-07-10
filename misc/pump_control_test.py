import serial
import time

# Replace with the correct port for your ESP32
port = '/dev/ttyUSB0'
baudrate = 460800
esp = serial.Serial(port=port, baudrate=baudrate, timeout=1)
# time.sleep(2)
# esp.reset_input_buffer()
# esp.reset_output_buffer()
time.sleep(2)
# state = "5"
# pcu_id = "pcu1"
# command = state + pcu_id + '\n'
# esp.write(command.encode())
# time.sleep(1)
# if esp.in_waiting > 0:
#     response = esp.read(esp.in_waiting).decode('utf-8')
#     print(f"Response from ESP32: {response}")


def control_pump(cmd):
    print("controlling pump")
    pcu_id = "pcu1"
    command = cmd + pcu_id + '\n'
    esp.write(command.encode())
    time.sleep(2)
    if esp.in_waiting > 0:
        response = esp.read(esp.in_waiting).decode('utf-8')
        print(f"Response from ESP32: {response}")

try:
    
    control_pump("1")

    control_pump("5")

    control_pump("3")

    control_pump("7")

    control_pump("9")

    control_pump("0")
    # # Optionally, read back any response from the ESP32
    # time.sleep(1)  # Wait a bit for response
    # if esp.in_waiting > 0:
    #     response = esp.read(esp.in_waiting).decode('utf-8')
    #     print(f"Response from ESP32: {response}")

    # esp.close()
except serial.SerialException as e:
    print(f"Error opening or communicating through serial port: {e}")