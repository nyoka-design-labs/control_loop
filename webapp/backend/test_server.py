import json
import asyncio
import time
import websockets

import sys
sys.path.append("../../src")

from devices import get_measurement, tare
from controller import Controller
from utils import extract_specific_cells

INTERVAL = 60 # time in seconds before readings

# Task to send weight data
async def send_weight(websocket, start_time, stop_event, control):
    start_time = time.time()
    while not stop_event.is_set():
        data = get_measurement()

        control.loop(data)

        elapsed_time = data['time'] - start_time
        data = json.dumps({
            "weight": data['weight'],
            "do": data['do'],
            "ph": data['ph_reading'],
            "temp": data['temp'],
            "time": round(elapsed_time, 0)
        })
        await websocket.send(data)
        await asyncio.sleep(INTERVAL)

# Handle incoming messages and manage tasks
async def handler(websocket):
    weight_task = None
    control = Controller()

    async for message in websocket:
        print(f"Received command: {message}")

        if message == "start_pump":
            control.pump.control(True)
            print("pump started")
        elif message == "stop_pump":
            control.pump.control(False)
            print("pump stopped")
        elif message == "show_weight" and weight_task is None:
            if weight_task is None:
                stop_event = asyncio.Event()
                # Start sending weight data if not already doing so, pass start_time to send_weight
                weight_task = asyncio.create_task(send_weight(websocket, stop_event, control))
        elif message == "hide_weight":
            if weight_task is not None:
                weight_task.cancel()
                weight_task = None
        elif message == "tare_ph":
            tare_value = await websocket.recv()
            tare("ph", float(tare_value))
            print(tare_value)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
