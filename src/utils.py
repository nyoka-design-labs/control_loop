import csv

def add_to_csv(data: list, csv_path: str):
    with open('test.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def extract_specific_cells(csv_path, start_row, end_row, col):
    with open(csv_path, 'r') as file:
        reader = csv.reader(file)
        # Skip the first start_rows - 1 rows
        for _ in range(start_row - 1):
            next(reader)
        # Extract the data from the specific column
        data = [row[col - 1] for row in reader][:(end_row - start_row + 1)] 
    return data