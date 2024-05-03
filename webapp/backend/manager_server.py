import json
import asyncio
import time
import websockets
import controllers as c


INTERVAL = 5
controllers = {}

async def control_task(controlToRun, websocket):
    while True:

        status, data = controlToRun()
        await websocket.send(data)
        await send_status_update(websocket, status)
        await asyncio.sleep(INTERVAL)


async def collection_task(collectionToRun, websocket):

      while True:

        status, data = collectionToRun()
        await websocket.send(data)
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
        if controller_info["control_task"] is None:
            controller_info["control_task"] = asyncio.create_task(control_task(controller_info["controller"].start_control(), websocket))
    
        if controller_info["collection_task"] is None: # if data collection is not already happening then start it
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"].start_collection(), websocket))

    elif command == "stop_control":
        if controller_info["control_task"] is not None:
            controller_info["control_task"].cancel()
            controller_info["control_task"] = None

        controller_info["controller"].stop_control()

    else:
        result = "Invalid control command"


def collection(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    if command == "start_collection":
        if controller_info["collection_task"] is None: # if data collection is not already happening then start it
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"].start_collection(), websocket))

    elif command == "stop_collection":
        if controller_info["collection_task"] is not None:
            controller_info["collection_task"].cancel()
            controller_info["collection_task"] = None
    else:
        result = "Invalid collection command"

def toggle(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    device_name = command.split("_")[1]  # Assuming command format is "toggle_<deviceName>"
    status = controller_info["device_manager"].toggle(device_name)
    
    send_status_update(websocket, status)
