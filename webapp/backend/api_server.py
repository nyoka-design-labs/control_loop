import asyncio
import websockets
import json
import manager_server
from resources.utils import read_csv_file

async def handle_client(websocket):

    if (False):
        # start_time = asyncio.create_task(load_data(websocket))
        data = read_csv_file("05-07-2024_fermentation_data.csv")
        # start_time = float(data[0][6])
        data = data
        
        for row in data:
            row_dict = {"feed_weight": row[1],
                        "do": row[2],
                        "ph": row[3],
                        "temp": row[4],
                        "time": row[5],
                        "type": "data"}

            
            # added_data = configure_data(start_time, row_dict)

            await websocket.send(json.dumps(row_dict))

    async for message in websocket:
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
        
        # Send the response back to the client
        # await websocket.send(data, status)


async def main():
    start_server = websockets.serve(handle_client, "localhost", 8765)
    async with start_server:
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
