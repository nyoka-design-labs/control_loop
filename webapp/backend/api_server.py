import asyncio
import websockets
import json
import manager_server

async def handle_client(websocket):

    if (False):
        # start_time = asyncio.create_task(load_data(websocket))
        data = read_csv_file("DO_ferementation_30-04-2024.csv")
        start_time = float(data[1][6])
        data = data[1:]
        
        for row in data:
            row_dict = {"feed_weight": row[0],
                        "do": row[2],
                        "ph_reading": row[3],
                        "temp": row[4],
                        "time": row[5]}
            
            added_data = configure_data(start_time, row_dict)

            await websocket.send(added_data)

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
