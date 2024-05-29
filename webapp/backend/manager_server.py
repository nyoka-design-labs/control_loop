import json
import asyncio
import time
import websockets
import os
import sys
import traceback


curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.utils import read_csv_file, get_loop_constant, get_control_constant
import controllers as c
from resources.logging_config import logger

load_data = eval(get_loop_constant(loop_id="server_consts", const="load_data"))
INTERVAL = get_loop_constant("server_consts", "interval")
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
controllers = {}

async def control(loop_id, command, websocket):
    try:
        controller_info = get_controller(loop_id)

        if command == "start_control":
            if "control_task" not in controller_info:
                controller_info["control_task"] = asyncio.create_task(control_task(controller_info["controller"], websocket))
        
            if "collection_task" not in controller_info: # if data collection is not already happening then start it
                controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket, loop_id))

        elif command == "stop_control":
            if "control_task" in controller_info:
                controller_info["control_task"].cancel()
                await controller_info["control_task"]  # Ensure cancellation is handled properly
                del controller_info["control_task"]

            controller_info["controller"].stop_control()

        else:
            print("Invalid control command")
    except Exception as e:
        logger.error(f"Error in control: {e}\n{traceback.format_exc()}")


async def collection(loop_id, command, websocket):
    try:
        controller_info = get_controller(loop_id)
        if command == "start_collection":
            if "collection_task" not in controller_info: # if data collection is not already happening then start it
                controller_info["collection_task"] = asyncio.create_task(collection_task(controller_info["controller"], websocket, loop_id))

        elif command == "stop_collection":
            if "collection_task" in controller_info:
                controller_info["collection_task"].cancel()
                await controller_info["collection_task"]  # Ensure cancellation is handled properly
                del controller_info["collection_task"]

        else:
            print("Invalid control command")
    except Exception as e:
        logger.error(f"Error in collection: {e}\n{traceback.format_exc()}")

async def load_previous_data(controller, websocket: websockets.WebSocketServerProtocol, loop_id: str):
    try:
        control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
        csv_name = get_control_constant(loop_id, control_id, "csv_name")
        data = read_csv_file(f"{csv_name}.csv")

        # Make sure there is data and a header was found and read
        if data:
            headers = data[0].keys()  # Get headers from the first row
            start_time = float(data[0]["start_time"])  # Update 'YourStartTimeColumnName' with the actual column name

            # Store the start time in the controller's device manager
            controller.device_manager.start_time = start_time

            # Iterate over rows starting from the first actual data row
            for row in data:
                row_dict = {key: row[key] for key in headers}
                row_dict["type"] = "data"
                await websocket.send(json.dumps(row_dict))
    except Exception as e:
        logger.error(f"Error in load_previous_data: {e}\n{traceback.format_exc()}")


async def control_task(controller, websocket):
    try:
        try:
            while True:
                print("loop controlled")
                data, status = controller.start_control()
                print(f"data sent from control: {data}")
                await websocket.send(json.dumps(data))
                await send_status_update(websocket, status)
                await asyncio.sleep(INTERVAL)
        except asyncio.CancelledError:
            print("Control task was cancelled")
            status = controller.stop_control()
            await send_status_update(websocket, status)
    except Exception as e:
        logger.error(f"Error in control_task: {e}\n{traceback.format_exc()}")

async def collection_task(controller, websocket, loop_id):
    try:
        try: 
            global load_data
            if load_data:
                await load_previous_data(controller, websocket, loop_id)
                load_data = False

            while True:
                controller.pump_control("T")
                print(f"data being collected")
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
    except Exception as e:
        logger.error(f"Error in collection_task: {e}\n{traceback.format_exc()}")

async def send_status_update(websocket, status):
    """ Send the consolidated status object to the websocket client. """
    await websocket.send(json.dumps({"type": "status", **status}))

def get_controller(loop_id):
    try:
        # Initialize controller and device manager if they don't exist for this loop
        if loop_id not in controllers:
            control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
            
            controller, device_manager = c.create_controller(loop_id, control_id, testing)
            controllers[loop_id] = {
                "controller": controller,  # Replace with appropriate constructor arguments
                "device_manager": device_manager  # Replace with appropriate constructor arguments
            }
        return controllers[loop_id]
    except Exception as e:
        logger.error(f"Error in get_data: {e}\n{traceback.format_exc()}")

async def toggle(loop_id, command, websocket):
    controller_info = get_controller(loop_id)
    
    if command == "toggle_feed_media":
        controller_info["controller"].switch_feed_media()
    else:
        controller_info["controller"].toggle_pump(command.split('_')[1] + "_pump")

    status = controller_info["controller"].status

    
    
    await send_status_update(websocket, status)
