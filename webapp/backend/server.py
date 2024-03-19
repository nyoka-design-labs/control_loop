# server.py
import asyncio
import websockets
from scale import get_current_weight, continous_read
import threading

scale_t = threading.Thread(target=continous_read, daemon=True).start()

async def scale_data_sender(websocket):
    while True:
        weight_data = get_current_weight()
        if weight_data is not None:
            await websocket.send(str(weight_data))
        await asyncio.sleep(1)

async def main():
    async with websockets.serve(scale_data_sender, "localhost", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())