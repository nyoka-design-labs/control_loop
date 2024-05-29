import asyncio
import websockets
import json
import manager_server
import sys
import os
import traceback

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.logging_config import logger

async def handle_client(websocket, path):
    async for message in websocket:
        try:
            data = json.loads(message)
            if data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
            else:
                command = data.get("command")
                loop_id = data.get("loopID")
                print(f"command received: {data.get('command')}")
                if "control" in command:
                    await manager_server.control(loop_id, command, websocket)
                elif "collection" in command:
                    await manager_server.collection(loop_id, command, websocket)
                elif "toggle" in command:
                    await manager_server.toggle(loop_id, command, websocket)
        except websockets.ConnectionClosedError as e:
            print(f"WebSocket connection closed: {e.code} - {e.reason}")
        except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")


async def main():
    start_server = websockets.serve(
        handle_client,
        "localhost",
        8765,
        ping_interval=20,  # Send a ping every 60 seconds
        ping_timeout=40  # Wait 120 seconds for a pong before closing the connection
    )
    async with start_server:
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
