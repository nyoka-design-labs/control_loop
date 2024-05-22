import json
import asyncio
import time
import websockets


import sys
sys.path.append("/home/sam/Desktop/control_loop/src")
from resources.utils import read_csv_file, get_csv_name
import controllers as c


INTERVAL = 13
controllers = {}

async def load_previous_data(controller: c, websocket: websockets, loop_id: str):
    csv_name = get_csv_name(loop_id)
    data = read_csv_file(f"{csv_name}.csv")
    start_time = float(data[1][7])
    data = data[1:]
    controller.device_manager.start_time = start_time
    for row in data:
        row_dict = {"feed_weight": row[1],
                    "do": row[2],
                    "ph": row[3],
                    "temp": row[4],
                    "time": row[5],
                    "type": "data"}

        await websocket.send(json.dumps(row_dict))

async def control_task(controller, websocket):
    while True:
        print("loop controlled")
        status = controller.start_control()
        # print(status)
        await send_status_update(websocket, status)
        await asyncio.sleep(INTERVAL)

async def collection_task(controller, websocket, loop_id):
      
    #   await load_previous_data(csv_name, controller, websocket, loop_id)

      while True:
        controller.pump_control("T")
        print(f"data being collected")
        status, data = controller.start_collection()
        print(f"data sent: {data}")
        await websocket.send(json.dumps(data))
        await send_status_update(websocket, status)
        await asyncio.sleep(INTERVAL)


async def send_status_update(websocket, status):
    """ Send the consolidated status object to the websocket client. """
    await websocket.send(json.dumps({"type": "status", **status}))

def get_controller(loop_id):
    # Initialize controller and device manager if they don't exist for this loop
    if loop_id not in controllers:
        controller, device_manager = c.create_controller(loop_id)
        controllers[loop_id] = {
            "controller": controller,  # Replace with appropriate constructor arguments
            "device_manager": device_manager  # Replace with appropriate constructor arguments
        }
    return controllers[loop_id]

async def control(loop_id, command, websocket):
    controller_info = get_controller(loop_id)

    if command == "start_control":
        if "control_task" not in controller_info:
            controller_info["control_task"] = asyncio.create_task(control_task(controller_info["controller"], websocket))
    
        if "collection_task" not in controller_info: # if data collection is not already happening then start it
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket))

    elif command == "stop_control":
        if "control_task" in controller_info:
            status = controller_info["controller"].stop_control()
            print(status)
            await send_status_update(websocket, status)
            controller_info["control_task"].cancel()
            controller_info["control_task"] = None
            del controller_info["control_task"]

        controller_info["controller"].stop_control()

    else:
        print("Invalid control command")


async def collection(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    if command == "start_collection":
        if "collection_task" not in controller_info: # if data collection is not already happening then start it
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket))

    elif command == "stop_collection":
        if "collection_task" in controller_info:
            status = controller_info["controller"].status
            status.update({
            "data_collection_status": "data_collection_off"
            })
            await send_status_update(websocket, status)
            controller_info["collection_task"].cancel()
            controller_info["collection_task"] = None
            del controller_info["collection_task"]

    else:
        print("Invalid control command")

async def toggle(loop_id, command, websocket):
    controller_info = get_controller(loop_id)

    if command == "toggle_base":
        controller_info["controller"].toggle_base()

    if command == "toggle_feed":
        controller_info["controller"].toggle_feed()
   
    if command == "toggle_buffer":
        controller_info["controller"].toggle_buffer()

    if command == "toggle_lysate":
        controller_info["controller"].toggle_lysate()

    if command == "toggle_lactose":
        controller_info["controller"].toggle_lactose()

    status = controller_info["controller"].status
    
    await send_status_update(websocket, status)
