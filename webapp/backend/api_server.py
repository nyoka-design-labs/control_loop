import asyncio
import websockets
import json
import manager_server
import sys
import os

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

async def handle_client(websocket, path):
    while True:
        message = await asyncio.wait_for(websocket.recv(), timeout=60)
        data = json.loads(message)
        
        if data.get("type") == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
        else:
            await process_command(websocket, data)

async def process_command(websocket, data):
    command = data.get("command")
    loop_id = data.get("loopID")
    print(f"command received: {data.get('command')}")
    if "control" in command:
        await manager_server.control(loop_id, command, websocket)
    elif "collection" in command:
        await manager_server.collection(loop_id, command, websocket)
    elif "toggle" in command:
        await manager_server.toggle(loop_id, command, websocket)

async def start_server():
    server = await websockets.serve(
        handle_client,
        "localhost",
        8765,
        ping_interval=20,  # Send a ping every 20 seconds
        ping_timeout=40  # Wait 40 seconds for a pong before closing the connection
    )
    await server.wait_closed()  # Run server until it is closed

async def main():
    await start_server()

if __name__ == "__main__":
    asyncio.run(main())
