import json
import asyncio
import websockets
import os
import sys

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.utils import read_csv_file, get_loop_constant, get_control_constant
import controllers as c

load_data = eval(get_loop_constant(loop_id="server_consts", const="load_data"))
INTERVAL = get_loop_constant("server_consts", "interval")
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
controllers = {}

async def control(loop_id, command, websocket):
    controller_info = get_controller(loop_id)

    if command == "start_control":
        if "control_task" not in controller_info:
            controller_info["control_task"] = asyncio.create_task(control_task(controller_info["controller"], websocket))

        if "collection_task" not in controller_info:
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket, loop_id))

    elif command == "stop_control":
        if "control_task" in controller_info:
            controller_info["control_task"].cancel()
            await controller_info["control_task"]
            del controller_info["control_task"]

        controller_info["controller"].stop_control()
    else:
        print("Invalid control command")

async def collection(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    if command == "start_collection":
        if "collection_task" not in controller_info:
            controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket, loop_id))

    elif command == "stop_collection":
        if "collection_task" in controller_info:
            controller_info["collection_task"].cancel()
            await controller_info["collection_task"]
            del controller_info["collection_task"]
    else:
        print("Invalid collection command")

async def load_previous_data(controller, websocket, loop_id):
    control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
    csv_name = get_control_constant(loop_id, control_id, "csv_name")
    data = read_csv_file(f"{csv_name}.csv")

    if data:
        headers = data[0].keys()
        for row in data:
            row_dict = {key: row[key] for key in headers}
            row_dict["type"] = "data"
            await websocket.send(json.dumps(row_dict))

async def control_task(controller, websocket):
    try:
        while True:
            data, status = controller.start_control()
            print(f"data sent from control: {data}")
            await websocket.send(json.dumps(data))
            await send_status_update(websocket, status)
            await asyncio.sleep(INTERVAL)
    except asyncio.CancelledError:
        print("Control task was cancelled")
        status = controller.stop_control()
        await send_status_update(websocket, status)

async def collection_task(controller, websocket, loop_id):
    try:
        if load_data:
            await load_previous_data(controller, websocket, loop_id)
            global load_data
            load_data = False

        while True:
            controller.pump_control("T")
            if controller.status["control_loop_status"] == "control_off":
                status, data = controller.start_collection(False)
                print(f"data sent from collect: {data}")
                await websocket.send(json.dumps(data))
                await send_status_update(websocket, status)
            await asyncio.sleep(INTERVAL)
    except asyncio.CancelledError:
        print("Collection task was cancelled")
        status = controller.status
        status.update({
            "data_collection_status": "data_collection_off"
        })
        await send_status_update(websocket, status)

async def send_status_update(websocket, status):
    await websocket.send(json.dumps({"type": "status", **status}))

def get_controller(loop_id):
    if loop_id not in controllers:
        control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
        controller, device_manager = c.create_controller(loop_id, control_id, testing)
        controllers[loop_id] = {"controller": controller, "device_manager": device_manager}
    return controllers[loop_id]

async def toggle(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    if command == "toggle_feed_media":
        controller_info["controller"].switch_feed_media()
    else:
        controller_info["controller"].toggle_pump(command.split('_')[1] + "_pump")

    status = controller_info["controller"].status
    await send_status_update(websocket, status)
