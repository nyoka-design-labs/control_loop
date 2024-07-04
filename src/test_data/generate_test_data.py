import json
from datetime import datetime, timedelta

def generate_data_point(do, ph, temp, feed_weight, lactose_weight, base_weight, acid_weight, time, date, time_of_day):
    return {
        "do": do,
        "ph": ph,
        "temp": temp,
        "feed_weight": feed_weight,
        "lactose_weight": lactose_weight,
        "base_weight": base_weight,
        "acid_weight": acid_weight,
        "time": time,
        "date": date,
        "time_of_day": time_of_day,
        "type": "data"
    }

def generate_test_data(test_name):
    initial_time = datetime(2024, 6, 20, 9, 12, 43)
    time_step = timedelta(seconds=7)
    
    test_data = {test_name: []}
    
    # Initial conditions
    temp = 35.936
    feed_weight = 1512.3
    lactose_weight = 1064.5
    base_weight = 672.4
    acid_weight = 672.4
    initial_do = 8.0
    initial_ph = 6.7
    
    current_time = 0
    current_date_time = initial_time

    # Function to generate sets
    def generate_set(do_values, ph_values):
        nonlocal current_time, current_date_time
        for do, ph in zip(do_values, ph_values):
            time_of_day = current_date_time.strftime('%H:%M:%S')
            date = current_date_time.strftime('%d-%m-%Y')
            test_data[test_name].append(generate_data_point(do, ph, temp, feed_weight, lactose_weight, base_weight, acid_weight, current_time, date, time_of_day))
            current_time += 7 / 3600  # Incrementing time in hours
            current_date_time += time_step

    # Test 1 sets
    sets = [
        ([8.0, 8.5, 9.0, 9.5, 10.0], [7.7, 6.8, 6.9, 7.0, 7.02]),  # Set 1
        ([70, 70, 8.5, 70, 70], [7.1, 7.15, 7.2, 7.25, 7.3]),  # Set 2
        ([8.0, 8.5, 70, 70, 70], [7.3, 7.25, 7.2, 7.1, 7.03]),  # Set 3
        ([10.5, 11.0, 11.5, 12.0, 12.5], [7.03, 7.03, 7.03, 7.03, 7.03]),  # Set 4
        ([13.0, 13.5, 14.0, 14.5, 15.0], [7.03, 7.0, 7.0, 7.03, 7.03]),  # Set 5
        ([15.5, 16.0, 16.5, 17.0, 17.5], [7.03, 7.11, 7.11, 7.03, 7.03]),  # Set 6
        ([17.0, 18.5, 19.0, 20.5, 20.0], [7.1, 7.15, 7.2, 7.25, 7.3]),  # Set 7
        ([16.0, 17.0, 18.0, 19.0, 20.0], [7.7, 6.8, 6.9, 7.0, 7.02]),  # Set 8
        ([23.0, 24.0, 25.0, 24.0, 23.0], [7.1, 7.15, 7.2, 7.25, 7.3]),  # Set 9
        ([22.0, 22.5, 23.0, 23.5, 24.0], [7.03, 7.03, 7.03, 7.03, 7.03]),  # Set 10
        ([24.5, 25.0, 25.5, 26.0, 26.5], [7.7, 6.8, 6.9, 7.0, 7.02]),   # Set 11
        ([20.5, 25.0, 25.5, 22.0, 26.5], [7.7, 6.8, 6.9, 7.0, 7.02]),   # Set 12
        ([23.0, 24.0, 25.0, 24.0, 23.0], [7.1, 7.15, 7.2, 7.25, 7.3]),  # Set 13
        ([22.0, 22.5, 23.0, 23.5, 24.0], [7.03, 7.03, 7.03, 7.03, 7.03]),  # Set 14
        ([24.5, 25.0, 25.5, 26.0, 26.5], [7.7, 6.8, 6.9, 7.0, 7.02]),   # Set 15
        ([20.5, 25.0, 25.5, 22.0, 26.5], [7.7, 6.8, 6.9, 7.0, 7.02])   # Set 16
    ]

    for do_values, ph_values in sets:
        generate_set(do_values, ph_values)

    # Load existing JSON file
    with open('src/test_data/test_data.json', 'r') as file:
        existing_data = json.load(file)

    # Add the new test data without erasing existing tests
    existing_data[test_name] = test_data[test_name]

    # Save updated data back to the JSON file with one dictionary per line
    with open('src/test_data/test_data.json', 'w') as file:
        file.write(
            '{\n' +
            ',\n'.join(f'"{key}": [\n' + ',\n'.join(json.dumps(item) for item in value) + '\n]' for key, value in existing_data.items()) +
            '\n}'
        )

# Specify the test name here
generate_test_data("2_phase_test_1")
