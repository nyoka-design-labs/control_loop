import json
import asyncio
import time
import websockets

import sys
sys.path.append("/Users/mba_sam/Github/Nyoka Design Labs/control_loop/src")

import controllers as c


INTERVAL = 5
controllers = {}

async def control_task(controller, websocket):
    while True:
        print("loop controlled")
        status = controller.start_control()
        await send_status_update(websocket, status)
        await asyncio.sleep(INTERVAL)


async def collection_task(controller, websocket):

      while True:
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

def control(loop_id, command, websocket):
    controller_info = get_controller(loop_id)

    if command == "start_control":
        if "control_task" not in controller_info:
            controller_info["control_task"] = asyncio.create_task(control_task(controller_info["controller"], websocket))
    
        if "collection_task" not in controller_info: # if data collection is not already happening then start it
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket))

    elif command == "stop_control":
        if "control_task" in controller_info:
            status = controller_info["controller"].stop_control()
            send_status_update(websocket, status)
            controller_info["control_task"].cancel()
            controller_info["control_task"] = None
            del controller_info["control_task"]

        controller_info["controller"].stop_control()

    else:
        print("Invalid control command")


def collection(loop_id, command, websocket):
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
            send_status_update(websocket, status)
            controller_info["collection_task"].cancel()
            controller_info["collection_task"] = None
            del controller_info["collection_task"]

    else:
        print("Invalid control command")

def toggle(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    device_name = command.split("_")[1]  # Assuming command format is "toggle_<deviceName>"
    status = controller_info["device_manager"].toggle(device_name)
    
    send_status_update(websocket, status)
