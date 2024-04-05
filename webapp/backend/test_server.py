import json
import asyncio
import time
import websockets

import sys
sys.path.append("../../src")

from devices import get_measurement

INTERVAL = 3

# scale = Scale(0x0922, 0x8003)

# Dummy function to simulate pump actions
# can be manipulated to send arduino the stop command
async def pump_action(action):
    print(f"Pump {action}")

# Task to send weight data
async def send_weight(websocket, start_time, stop_event):
    while not stop_event.is_set():
        # now = datetime.datetime.now()
        data = get_measurement()
        elapsed_time = data['time'] - start_time
        data = json.dumps({
            "weight": data['weight'],
            "do": data['do'],
            "time": round(elapsed_time, 0)
        })
        await websocket.send(data)
        await asyncio.sleep(INTERVAL)

# Handle incoming messages and manage tasks
async def handler(websocket):
    weight_task = None
    async for message in websocket:
        print(f"Received command: {message}")

        if message == "start_pump":
            await pump_action("started")
        elif message == "stop_pump":
            await pump_action("stopped")
        elif message == "show_weight" and weight_task is None:
            start_time = time.time()  # Capture the time when "Show Weight" is pressed
            if weight_task is None:
                stop_event = asyncio.Event()
                # Start sending weight data if not already doing so, pass start_time to send_weight
                weight_task = asyncio.create_task(send_weight(websocket, start_time, stop_event))
        elif message == "hide_weight": 
            if weight_task is not None:
                weight_task.cancel()
                weight_task = None

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
