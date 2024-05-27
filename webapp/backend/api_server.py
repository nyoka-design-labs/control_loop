import asyncio
import websockets
import json
import manager_server

async def handle_client(websocket):

    async for message in websocket:
        try:
            data = json.loads(message)
            command = data.get("command")
            loop_id = data.get("loopID")
            print(f"commmand recieved: {data.get('command')}")
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
        # Send the response back to the client
        # await websocket.send(data, status)


async def main():
    start_server = websockets.serve(handle_client, "localhost", 8765)
    async with start_server:
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
