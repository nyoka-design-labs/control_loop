import json
import asyncio
import time
import websockets

import sys
sys.path.append("../../src")

from devices import get_measurement, tare
from controller import Controller
from utils import add_to_csv, read_csv_file

status = {
    "control_loop_status": "control_off",
    "data_collection_status": "data_collection_off",
    "feed_pump_status": "0",
    "base_pump_status": "2",
    "buffer_pump_status": "4",
    "lysate_pump_status": "6"
}

data = {
    "control_loop_status": "control_off",
    "data_collection_status": "data_collection_off",
    "feed_pump_status": "0",
    "base_pump_status": "2"
}

INTERVAL = 15 # time in seconds between readings

async def load_data(websocket):
    data = read_csv_file("data.csv")
    start_time = data[0][4]
    
    for row in data:
        row_dict = {"weight_buff": row[0],
                     "weight_lys": row[1],
                       "time": row[2]}
        
        added_data = configure_data(start_time, row_dict)

        await websocket.send(added_data)

async def collect_data(websocket, start_time, control):
    data_path = 'data/data.csv'  # Replace with the actual path
    headers = ['weight', 'do', 'ph', 'temp', 'time']

    while True:
        if status["control_loop_status"] != "control_on":
            data = get_measurement()
            control.arduino.write("8".encode())
            data = configure_data(start_time, data)
            print(f"from data collection: {data}")
            await websocket.send(data)

        status["data_collection_status"] = "data_collection_on"
        await send_status_update(websocket)
        await asyncio.sleep(INTERVAL)

# Task to send weight data
async def start_control(websocket, control, start_time):
    while True:
        print("loop controlled")
        data = get_measurement()
        control.arduino.write("8".encode())
        # expected_weight = control.ph_do_feed_loop(data)
        expected_weight = 0
        control.loop2(data)
        data = configure_data(start_time, data, expected_weight)
        print(f"from control: {data}")
        status["control_loop_status"] = "control_on"
        status["base_pump_status"] = str(control.pH_pump.state)
        status["feed_pump_status"] = str(control.feed_pump.state)
        status["buffer_pump_status"] = str(control.buffer_pump.state)
        status["lysate_pump_status"] = str(control.lysate_pump.state)

        await websocket.send(data)
        await send_status_update(websocket)
        await asyncio.sleep(INTERVAL)

async def send_status_update(websocket):
    """ Send the consolidated status object to the websocket client. """
    await websocket.send(json.dumps({"type": "status", **status}))

def configure_data(start_time, data, expected_weight = 0):
    elapsed_time = data['time'] - start_time
    data = json.dumps({
        "type": 'data',
        "buffer_weight": data['weight_buff'],
        "lysate_weight": data['weight_lys'],
        # "do": data['do'],
        # "ph": data['ph_reading'],
        # "temp": data['temp'],
        "time": round(elapsed_time, 0),
        # "expected_weight": expected_weight,
    })
    return data

# Handle incoming messages and manage tasks
async def handler(websocket):
    control_task = None
    collection_task = None
    start_time = time.time()
    control = Controller()

    if (True):
        asyncio.create_task(load_data(websocket))
  
    async for message in websocket:
        print(f"Received command: {message}")

        if message == "start_collection":
            if collection_task is None:
                collection_task = asyncio.create_task(collect_data(websocket, start_time, control))
                print("created collection task")
            print("data collection started")

        elif message == "stop_collection":
            # Stop the control loop, but let data collection continue
            if collection_task is not None:
                status["data_collection_status"] = "data_collection_off"
                await send_status_update(websocket)
                collection_task.cancel()
                collection_task = None
                print("data collection stopped.")

        elif message == "toggle_feed":
            control.toggle_feed()
            status["feed_pump_status"] = str(control.feed_pump.state)
            await send_status_update(websocket)
        elif message == "toggle_base":
            control.toggle_base()
            status["base_pump_status"] = str(control.pH_pump.state)
            await send_status_update(websocket)

        elif message == "toggle_buffer":
            control.toggle_buffer()
            status["buffer_pump_status"] = str(control.buffer_pump.state)
            await send_status_update(websocket)

        elif message == "toggle_lysate":
            control.toggle_lysate()
            status["lysate_pump_status"] = str(control.lysate_pump.state)
            await send_status_update(websocket)

        elif message == "start_control":
            if collection_task is None:
                collection_task = asyncio.create_task(collect_data(websocket, start_time, control))
                print("Data collection started as part of control loop.")

            # Start control if not already started
            if control_task is None:
                status["control_loop_status"] = "control_on"
                control_task = asyncio.create_task(start_control(websocket, control, start_time))
                print("Control loop started.")

        elif message == "stop_control":
            # Stop the control loop, but let data collection continue
            if control_task is not None:
                control_task.cancel()
                control_task = None
                print("Control loop stopped.")
            control.stop_loop()
            status["control_loop_status"] = "control_off"
            status["base_pump_status"] = str(control.pH_pump.state)
            status["feed_pump_status"] = str(control.feed_pump.state)
            status["buffer_pump_status"] = str(control.buffer_pump.state)
            status["lysate_pump_status"] = str(control.lysate_pump.state)
            await send_status_update(websocket)
        elif message.startswith("tare_ph:"):
            # Split the message by the colon to get the value
            _, tare_value = message.split(":")
            
            # Perform the taring operation
            tare("ph", float(tare_value))
            
            # Print the tare value
            print(f"Tare value received: {tare_value}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
