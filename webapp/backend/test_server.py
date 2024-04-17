import json
import asyncio
import time
import websockets

import sys
sys.path.append("../../src")

from devices import get_measurement, tare
from controller import Controller
from utils import extract_specific_cells

INTERVAL = 10 # change interval

# t = extract_specific_cells('../../tests/feed_data_v0-2_u-0.1_m0-1000.csv', 6, 1217, 4)
# target = list(map(lambda x: float(x)*1000, t))
# i = 0

# m0 = 322
# last_weight = m0
# total = m0

# ph_control = Controller()

# start = False

# Task to send weight data
async def send_weight(websocket, start_time, stop_event, start, last_weight, target, i, ph_control):
    while not stop_event.is_set():
        data = get_measurement()
        ph_control.pump.arduino.write('5'.encode())

        if (data['ph'] > 6.75):
            start = True

        if (start):
            current_weight = data["weight"]
            # expected_weight = last_weight - target[i]
            last_weight -= target[i]

            print(f"Elapsed time: {elapsed_time:.2f}s, Current weight: {current_weight}, Expected weight: {last_weight:.2f}")

            if current_weight >= last_weight:
                ph_control.pump.arduino.write('3'.encode()) # turn on the pump
            elif current_weight < last_weight:
                ph_control.pump.arduino.write('4'.encode()) # turn off the pump

            i += 1

            # last_weight = expected_weight


        ph_control.pH_loop(data["ph"])

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
    ph_control = Controller()
    async for message in websocket:
        print(f"Received command: {message}")

        if message == "start_pump":
            ph_control.pump.control(True)
            print("pump started")
        elif message == "stop_pump":
            ph_control.pump.control(False)
            print("pump stopped")
        elif message == "show_weight" and weight_task is None:
            start_time = time.time()  # Capture the time when "Show Weight" is pressed

            start = False
            m0 = 556 # change this when running
            last_weight = m0
            t = extract_specific_cells('../../tests/feed_data_v0-2_u-0.1_m0-1000.csv', 6, 1217, 4)
            target = list(map(lambda x: float(x)*1000, t))
            i = 0
            # ph_control = Controller()

            if weight_task is None:
                stop_event = asyncio.Event()
                # Start sending weight data if not already doing so, pass start_time to send_weight
                weight_task = asyncio.create_task(send_weight(websocket, start_time, stop_event, start, last_weight, target, i, ph_control))
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
