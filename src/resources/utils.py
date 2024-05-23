import csv
import os
import math
import serial.tools.list_ports
import usb.core
import json
import numpy as np

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

def calculate_derivative(key, loop_id, num_points=10):
    csv_name = get_control_constant(loop_id, "do_der_control", "csv_name")
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

def extract_specific_cells(csv_path, start_row, end_row, col):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        # Skip the first start_rows - 1 rows
        for _ in range(start_row - 1):
            next(reader)
        # Extract the data from the specific column
        data = [row[col - 1] for row in reader][:(end_row - start_row + 1)] 
    return data

def find_usb_serial_port(vendor_id: hex, product_id: hex):
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

def get_csv_name(loop_id):
    curr_dir = os.path.dirname(__file__)
    json_path = os.path.join(curr_dir, "constants.json")
    # Load the JSON data from the given path
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Iterate through each entry in the "loop" list
    for loop in data["loop"]:
        if loop.get("loop_id") == loop_id:
            # Return the 'csv_name' if the loop_id matches and 'csv_name' exists
            return loop.get("csv_name", "No CSV name provided")

    # Return a message if the loop_id is not found
    return "Loop ID not found"

def get_control_constant(loop_id: str, control_id: str, const: str):
    curr_dir = os.path.dirname(__file__)
    json_path = os.path.join(curr_dir, "constants.json")
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
    curr_dir = os.path.dirname(__file__)
    json_path = os.path.join(curr_dir, "constants.json")
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

if __name__ == "__main__":
    # import matplotlib.pyplot as plt

    # t_values = range(1, 501)
    # c1 = 0
    # v2_values = []
    # for t in t_values:
    #     v, c2 = exponential_func(t, c1)
    #     v2_values += [v]
    #     c1 = c2

    # plt.plot(t_values, v2_values)
    # plt.xlabel('Time (t)')
    # plt.ylabel('Volume (v2)')
    # plt.title('Exponential Function')
    # plt.show()
    # d = extract_specific_cells("../tests/feed_data_v0-2_u-0.1_m0-1000.csv", 6, 1217, 4)
    # data = list(map(lambda x: float(x)*1000, d))
    # print(sum(data))
    # print(find_usb_serial_port(0x1a86, 0x7523))
    test_data = {"do": 70, "ph": 6.5, "feed_weight": 1000, "time": 0, "type": "data"}
    file_name = "test_data.csv"
    
    # Add test data to CSV
    add_test_data_to_csv(test_data, file_name)