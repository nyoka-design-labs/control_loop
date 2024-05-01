import asyncio
import websockets
import json
from manager_server import execute_command
import manager_server

async def handle_client(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        command = data.get("command")
        loop_id = data.get("loopID")
        
        if "control" in command:
            status, data = manager_server.control(loop_id, command, websocket)
        elif "collection" in command:
            status, data = manager_server.collection(loop_id, command, websocket)
        elif "toggle" in command:
            status, data = manager_server.toggle(loop_id, command, websocket)
        
        # Send the response back to the client
        await websocket.send(data, status)


async def main():
    start_server = websockets.serve(handle_client, "localhost", 8765)
    async with start_server:
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
