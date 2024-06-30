import csv
import os
import math
import serial.tools.list_ports
import usb.core
import json
import numpy as np
import inspect
import re

curr_dir = os.path.dirname(__file__)
json_path = os.path.join(curr_dir, "constants.json")

#################################################### Port Funcs ####################################################
def find_usb_serial_port(vendor_id: hex, product_id: hex):
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None


#################################################### Math Funcs ####################################################
def exponential_func(t: int, c1: int) -> float:
    """
    Returns the expected volume at elapsed time t. Assuming 1 ml = 1 g.
    """

    # target concentration constants
    x0 = 22 # g/L
    mu = 0.1 # rate

    # target substrate concentration
    X_t = lambda t: x0*math.exp(mu*t) # g/L

    # volume constants
    v1 = 2 # L
    c2 = 225 # g/L

    v2 = (v1*X_t(t) - v1*c1) / (c2 - X_t(t)) # L

    return v2, c2


def isDerPositive(derivatives, num_points=5):
    """
    Checks if the last `num_points` values in the list of derivatives are positive.
    
    Args:
        derivatives (list): The list of derivatives.
        num_points (int): The number of last values to check.
        
    Returns:
        bool: True if all the last `num_points` values are positive, False otherwise.
    """
    if len(derivatives) < num_points:
        return False
    
    last_values = derivatives[-num_points:]
    return all(value > 0 for value in last_values)

def calculate_derivative(key, csv_name, num_points=10):
    data = read_csv_file(f"{csv_name}.csv")
    do_values = [float(row[f"{key}"]) for row in data]
    time_values = [float(row["time"]) for row in data]

    if len(do_values) < num_points:
        raise ValueError("Not enough data points to calculate the derivative")

    # Calculate the derivative using the last num_points
    y = do_values[-num_points:]
    x = time_values[-num_points:]
    # Fit a linear line to the data points
    poly = np.polyfit(x, y, 1)
    # The slope of the line is the derivative
    derivative = poly[0]

    return derivative


#################################################### JSON/CSV Funcs ####################################################
def load_test_data(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)
    
def add_to_csv(data: list, file_name: str, header: list):
    curr_dir = os.path.dirname(__file__)
    csv_dir = os.path.join(curr_dir, "..", "data", file_name)
    
    # Check if the file exists and if it is empty
    file_exists = os.path.isfile(csv_dir)
    file_empty = os.path.getsize(csv_dir) == 0 if file_exists else True
    
    with open(csv_dir, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # If the file doesn't exist or is empty, write the header
        if file_empty:
            writer.writerow(header)
        
        writer.writerow(data)

def add_test_data_to_csv(data, file_name: str):
    curr_dir = os.path.dirname(__file__)
    csv_dir = os.path.join(curr_dir, "..", "data", file_name)
    
    # Check if the file exists and if it is empty
    file_exists = os.path.isfile(csv_dir)
    file_empty = os.path.getsize(csv_dir) == 0 if file_exists else True

    with open(csv_dir, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # If the file is empty or doesn't exist, write the header first
        if not file_exists or file_empty:
            headers = list(data.keys())
            writer.writerow(headers)
        
        # Write the data
        writer.writerow(data.values())

def read_csv_file(file_name: str):
    data = []
    curr_dir = os.path.dirname(__file__)
    csv_dir = os.path.join(curr_dir, "..", "data", file_name)

    with open(csv_dir, 'r', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data
def extract_specific_cells(csv_path, start_row, end_row, col):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        # Skip the first start_rows - 1 rows
        for _ in range(start_row - 1):
            next(reader)
        # Extract the data from the specific column
        data = [row[col - 1] for row in reader][:(end_row - start_row + 1)] 
    return data
                
#################################################### Control Loop Funcs ####################################################
def get_control_constant(loop_id: str, control_id: str, const: str):
    # Load the JSON data from the given path
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Iterate through each entry in the "loop" list
    for loop in data["loop"]:
        if loop.get("loop_id") == loop_id:
            for controller in loop["controllers"]:
                if controller.get("controller_id") == control_id:
                    # Return the 'csv_name' if the loop_id matches and 'csv_name' exists
                    return controller.get(f"{const}", f"No {const} provided")
            return "Control ID not found"

    # Return a message if the loop_id is not found
    return "Loop ID not found"

def get_loop_constant(loop_id: str, const: str):
    # Load the JSON data from the given path
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Iterate through each entry in the "loop" list
    for loop in data["loop"]:
        if loop.get("loop_id") == loop_id:
            # Return the 'csv_name' if the loop_id matches and 'csv_name' exists
            return loop.get(f"{const}", f"No {const} provided")

    # Return a message if the loop_id is not found
    return "Loop ID not found"
                    

def update_control_constant(loop_id, control_name, constant_name, new_value):
    # Read the JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Locate the specific controller to update
    for loop in data['loop']:
        if loop['loop_id'] == loop_id:
            for controller in loop['controllers']:
                if controller['controller_id'] == control_name:
                    # Update the specified constant value
                    controller[constant_name] = new_value
                    print(f"Updated {constant_name} for {control_name} in loop {loop_id} to {new_value}")

                    # Write the updated JSON back to the file
                    with open(json_path, 'w') as file:
                        json.dump(data, file, indent=4)
                    return
def update_loop_constant(loop_id, constant_name, new_value):
    # Read the JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Locate the specific controller to update
    for loop in data['loop']:
        if loop['loop_id'] == loop_id:
            loop[constant_name] = new_value
            print(f"Updated {constant_name} in loop {loop_id} to {new_value}")

            # Write the updated JSON back to the file
            with open(json_path, 'w') as file:
                json.dump(data, file, indent=4)
            return
#################################################### MISC ####################################################

def update_dict(original: dict={}, *args, **kwargs):
    if len(args) == 1 and isinstance(args[0], dict):
        original.update(args[0])
    elif len(args) == 2 and isinstance(args[0], list) and isinstance(args[1], list):
        keys, values = args
        if len(keys) != len(values):
            raise ValueError("Keys and values lists must be of the same length")
        else:
            original.update(zip(keys, values))
    elif len(args) == 2 and isinstance(args[0], str):
        key, value = args
        original[key] = value
    elif not args and kwargs:
        original.update(kwargs)
    return original

def called_from():
    stack = inspect.stack()
    # The first element on the stack is this function, the second is the caller
    caller = stack[1]
    caller_frame = caller[0]
    info = inspect.getframeinfo(caller_frame)
    
    # Print caller's details
    print(f"Called from {info.filename} at line {info.lineno} in function {info.function}")


def extract_after_toggle(input_string):
    # Define a regular expression pattern that looks for 'toggle_' followed by any characters
    pattern = r"toggle_(.*)"

    # Search for the pattern in the input string
    match = re.search(pattern, input_string)
    if match:
        # Return the part of the string after 'toggle_'
        return match.group(1)
    else:
        # Return None or some default value if 'toggle_' is not found
        return None
                
if __name__ == "__main__":
    pass