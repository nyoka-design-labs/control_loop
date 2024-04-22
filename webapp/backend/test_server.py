import json
import asyncio
import time
import websockets

import sys
sys.path.append("../../src")

from devices import get_measurement, tare
from controller import Controller
from utils import add_to_csv
status = {
    "control_loop_status": "control_off",
    "data_collection_status": "data_collection_off",
    "feed_pump_status": "0",
    "base_pump_status": "2"
}
INTERVAL = 5 # time in seconds before readings
async def collect_data(websocket, start_time):
    data_path = 'data/data.csv'  # Replace with the actual path
    headers = ['weight', 'do', 'ph', 'temp', 'time']
    while True:
        data = get_measurement()

        elapsed_time = data['time'] - start_time
        data = json.dumps({
            "type": 'data',
            "weight": data['weight'],
            "do": data['do'],
            "ph": data['ph_reading'],
            "temp": data['temp'],
            "time": round(elapsed_time, 0), 
        })

        # add_to_csv(data, data_path, headers)
        print(data)
        await websocket.send(data)
        status["data_collection_status"] = "data_collection_on"
        await send_status_update(websocket)
        await asyncio.sleep(INTERVAL)
        
# Task to send weight data
async def start_control(websocket, control):
    
    while True:
        data = get_measurement()
        print("loop controlled")
        control.ph_do_feed_loop(data)
        status["control_loop_status"] = "control_on"
        status["base_pump_status"] = str(control.pH_pump.state)
        status["feed_pump_status"] = str(control.feed_pump.state)
        await send_status_update(websocket)
        await asyncio.sleep(INTERVAL)

async def send_status_update(websocket):
    """ Send the consolidated status object to the websocket client. """
    await websocket.send(json.dumps({"type": "status", **status}))

# Handle incoming messages and manage tasks
async def handler(websocket):
    control_task = None
    collection_task = None
    start_time = time.time()
    control = Controller()
  
    async for message in websocket:
        print(f"Received command: {message}")

        if message == "start_collection":
            if collection_task is None:
                collection_task = asyncio.create_task(collect_data(websocket, start_time))
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

        elif message == "start_control":
            if collection_task is None:
                collection_task = asyncio.create_task(collect_data(websocket, start_time))
                print("Data collection started as part of control loop.")

            # Start control if not already started
            if control_task is None:
                control_task = asyncio.create_task(start_control(websocket, control))
                print("Control loop started.")

        elif message == "stop_control":
            # Stop the control loop, but let data collection continue
            if control_task is not None:
                control_task.cancel()
                control_task = None
                print("Control loop stopped.")
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
