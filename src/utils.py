import csv
import os
import math
import serial.tools.list_ports
import usb.core

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

def add_to_csv(data: list, file_name: str, header: list):
    curr_dir = os.path.dirname(__file__)
    csv_dir = curr_dir + f"../data/{file_name}"
    file_exists = os.path.isfile(csv_dir)
    
    with open(csv_dir, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # If the file is being created, write the header first
        if not file_exists:
            writer.writerow(header)
    
        writer.writerow(data)

def read_csv_file(file_name: str):
    data = []
    curr_directory = os.path.dirname(__file__)
    file_path = curr_directory + f"/../data/{file_name}"

    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
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

def find_usb_serial_port(vendor_id, product_id):
    ports = serial.tools.list_ports.comports()

    for port in ports:
        if port.vid == vendor_id and port.pid == product_id:
            return port.device
    return None

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
    print(find_usb_serial_port(0x0922, 0x8003))