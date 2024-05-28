import json
import asyncio
import time
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


async def collection(loop_id, command, websocket):
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

async def load_previous_data(controller: c, websocket: websockets, loop_id: str):
    control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
    csv_name = get_control_constant(loop_id, control_id, "csv_name")
    data = read_csv_file(f"{csv_name}.csv")
    
    # Make sure there is data and a header was found and read
    if data:
        start_time = float(data[0]["start_time"])  # Update 'YourStartTimeColumnName' with the actual column name
        
        # Store the start time in the controller's device manager
        controller.device_manager.start_time = start_time
        
        # Iterate over rows starting from the first actual data row
        for row in data:
            row_dict = {
                "feed_weight": row["feed_weight"],
                "do": row["do"],
                "ph": row["ph"],
                "temp": row["temp"],
                "lactose_weight": row["lactose_weight"],
                "acid_weight": row["acid_weight"],
                "time": row["time"],
                "type": "data"
            }
            await websocket.send(json.dumps(row_dict))

async def control_task(controller, websocket):
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

async def collection_task(controller, websocket, loop_id):
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

async def send_status_update(websocket, status):
    """ Send the consolidated status object to the websocket client. """
    await websocket.send(json.dumps({"type": "status", **status}))

def get_controller(loop_id):
    # Initialize controller and device manager if they don't exist for this loop
    if loop_id not in controllers:
        control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
        
        controller, device_manager = c.create_controller(loop_id, control_id, testing)
        controllers[loop_id] = {
            "controller": controller,  # Replace with appropriate constructor arguments
            "device_manager": device_manager  # Replace with appropriate constructor arguments
        }
    return controllers[loop_id]

async def toggle(loop_id, command, websocket):
    controller_info = get_controller(loop_id)

    # controller_info["controller"].toggle_pump(command.split('_')[1] + "_pump")

    # if command == "toggle_base":
    #     controller_info["controller"].toggle_base()

    # if command == "toggle_feed":
    #     controller_info["controller"].toggle_feed()
   
    # if command == "toggle_buffer":
    #     controller_info["controller"].toggle_buffer()

    # if command == "toggle_lysate":
    #     controller_info["controller"].toggle_lysate()

    # if command == "toggle_lactose":
    #     controller_info["controller"].toggle_lactose()
        
    # if command == "toggle_acid":
    #     controller_info["controller"].toggle_acid()
    
    if command == "toggle_feed_media":
        controller_info["controller"].switch_feed_media()
    else:
        controller_info["controller"].toggle_pump(command.split('_')[1] + "_pump")

    status = controller_info["controller"].status

    
    
    await send_status_update(websocket, status)
