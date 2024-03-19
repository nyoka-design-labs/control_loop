import json
import asyncio
import datetime
import websockets

# Dummy function to simulate pump actions
# can be manipulated to send arduino the stop command
async def pump_action(action):
    print(f"Pump {action}")

# Task to send weight data
async def send_weight(websocket, start_time, stop_event):
    weight_data = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] # Simulate getting weight data by switching out for call to get_current_weight
    i = 0
    while not stop_event.is_set():
        now = datetime.datetime.now()
        elapsed_time = (now - start_time).total_seconds()  # Calculate time elapsed in seconds
        data = json.dumps({
            "weight": weight_data[i],
            "time": elapsed_time
        })
        await websocket.send(data)
        i = (i + 1) % len(weight_data)
        await asyncio.sleep(1)

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
            start_time = datetime.datetime.now()  # Capture the time when "Show Weight" is pressed
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
