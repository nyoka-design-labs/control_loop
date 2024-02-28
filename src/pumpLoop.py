import serial
import time
import polynomialFunc as pf

interval = 30  # Interval in seconds
data = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]  # Example data points

poly_func = pf.fit_polynomial(data, interval, degree=3)

# Setup serial connection (adjust port name to match your system)
arduino = serial.Serial(port='/dev/tty.usbmodem1401', baudrate=57600, timeout=1)

def get_current_weight():
    # Placeholder function to get the current weight
    return 0.0

def get_expected_weight(time_arg):
    
    return poly_func(time_arg)

def control_pump(turn_on):
    # Send command to Arduino to control the pump
    command = '1' if turn_on else '0'
    arduino.write(command.encode())

start_time = time.time()
interval = 30  # Interval in seconds

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    current_weight = get_current_weight()
    expected_weight = get_expected_weight(elapsed_time)

    if current_weight >= expected_weight:
        control_pump(True)  # Turn on the pump
    elif current_weight < expected_weight:
        control_pump(False)  # Turn off the pump

    # Wait for the next interval before the next iteration
    time.sleep(interval)
 