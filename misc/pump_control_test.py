import serial
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='pump_control.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Replace with the correct port for your ESP32
port = '/dev/cu.usbserial-0001'
baudrate = 9600

# Initialize serial connection
esp = serial.Serial(port=port, baudrate=baudrate, timeout=1)
time.sleep(2)  # Allow some time for the ESP32 to reset

def control_pump(cmd):
    print(f"Controlling pump with command {cmd}")
    pcu_id = "pcu1"
    command = cmd + pcu_id + '\n'
    esp.write(command.encode())
    time.sleep(2)
    if esp.in_waiting > 0:
        response = esp.read(esp.in_waiting).decode('utf-8')
        print(f"Response from ESP32: {response}")
        logging.info(f"Command {cmd} sent successfully: {response}")
        return True
    else:
        print(f"No response for command {cmd}")
        logging.error(f"No response for command {cmd}")
        return False

commands = [
    {"cmd": ["0", "1"], "index": 0},
    {"cmd": ["2", "3"], "index": 0},
    {"cmd": ["4", "5"], "index": 0},
    {"cmd": ["6", "7"], "index": 0},
    {"cmd": ["8", "9"], "index": 0},
]

try:
    while True:
        for command in commands:
            current_cmd = command["cmd"][command["index"] % 2]
            if control_pump(current_cmd):
                command["index"] += 1
            else:
                print(f"Retrying command {current_cmd} in the next cycle")
                logging.warning(f"Retrying command {current_cmd} in the next cycle")
        

except KeyboardInterrupt:
    print("Testing interrupted by user")
    logging.info("Testing interrupted by user")
finally:
    esp.close()