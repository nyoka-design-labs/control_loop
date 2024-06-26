import json
import asyncio
import websockets
import os
import sys
import traceback

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.utils import *
import controllers as c
from resources.logging_config import setup_logger

logger = setup_logger()
load_data = eval(get_loop_constant(loop_id="server_consts", const="load_data"))
INTERVAL = get_loop_constant("server_consts", "interval")
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
controllers = {}

async def control(loop_id, command, websocket):
    """
    Handles control commands for specific control loops via WebSocket connections.

    Args:
        loop_id (str): Identifier for the specific control loop.
        command (str): Control command to execute, such as 'start_control' or 'stop_control'.
        websocket (WebSocketServerProtocol): WebSocket connection object for sending data and updates.

    This function manages starting and stopping control tasks based on incoming commands.
    """
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
        print(f"Error in control: \n Input: {command}, \n{e}")
        logger.error(f"Error in control: \n Input: {command}, \n{e}\n{traceback.format_exc()}")

async def collection(loop_id, command, websocket):
    """
    Handles data collection commands for specific control loops via WebSocket connections.

    Args:
        loop_id (str): Identifier for the specific control loop.
        command (str): Collection command to execute, such as 'start_collection' or 'stop_collection'.
        websocket (WebSocketServerProtocol): WebSocket connection object for sending data and updates.

    This function manages the lifecycle of data collection tasks based on received commands.
    """
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
        print(f"Error in collection: \nInput: command: {command}, \n{e}")
        logger.error(f"Error in collection: \nInput: {command}, \n{e}\n{traceback.format_exc()}")

async def control_task(controller, websocket):
    """
    A coroutine that runs a control loop task, sending control data and status updates via WebSocket.

    Args:
        controller (Controller): The controller instance that manages control logic.
        websocket (WebSocketServerProtocol): WebSocket connection to send data and status updates.

    Continuously sends control commands and status updates at regular intervals defined by INTERVAL.
    """
    try:
        try:
            while True:
                print("loop controlled")
                logger.info("loop controlled")
                data, status = controller.start_control()
                logger.info(f"data sent from control: {data}")
                await websocket.send(json.dumps(data))
                await send_status_update(websocket, status)
                await asyncio.sleep(INTERVAL)
        except asyncio.CancelledError:
            print("Control task was cancelled")
            status = controller.stop_control() # first stop_all error
            await send_status_update(websocket, status) # does when there is an error
    except Exception as e:
        print(f"Error in control_task: {e}")
        logger.error(f"Error in control_task: {e}\n{traceback.format_exc()}")

async def collection_task(controller, websocket, loop_id):
    """
    A coroutine that manages the data collection process for a controller, sending data via WebSocket.

    Args:
        controller (Controller): The controller instance that performs data collection.
        websocket (WebSocketServerProtocol): WebSocket connection to send data and status updates.
        loop_id (str): The loop identifier for which data collection is being performed.

    Continuously sends data collected by the controller to a WebSocket client at regular intervals.
    """
    try:
        try: 
            global load_data
            if load_data:
                await load_previous_data(controller, websocket, loop_id)
                load_data = False

            while True:
                print(f"data being collected")
                if controller.status["control_loop_status"] == "control_off":
                    status, data = controller.start_collection(False)
                    logger.info(f"data sent from collect: {data}")
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
        print(f"Error in collection_task: {e}")
        logger.error(f"Error in collection_task: {e}\n{traceback.format_exc()}")

async def toggle(loop_id, command, websocket):
    """
    Handles toggle commands to switch modes or states of devices in the control loop via WebSocket.

    Args:
        loop_id (str): Identifier for the control loop.
        command (str): Toggle command to execute, may include toggling feed media or specific pumps.
        websocket (WebSocketServerProtocol): WebSocket connection to send status updates.

    Executes commands that toggle operational states of devices within the control system.
    """
    try:
        controller_info = get_controller(loop_id)
        if command == "toggle_feed_media":
            controller_info["controller"].switch_feed_media()
        else:
            pump_name = extract_after_toggle(command)
            controller_info["controller"].toggle_pump(pump_name + "_pump")

        status = controller_info["controller"].status
        await send_status_update(websocket, status)
    except Exception as e:
        print(f"Error in toggle: \n Input: {command}, \n{e}")
        logger.error(f"Error in toggle: \n Input: {command}, \n{e}\n{traceback.format_exc()}")

async def stop_all(loop_id):
    """
    Stops all running tasks for a given control loop and safely shuts down the controller.

    Args:
        loop_id (str): Identifier for the control loop whose tasks need to be stopped.

    Cancels all active control and collection tasks and ensures proper cleanup and status updates.
    """
    controller_info = get_controller(loop_id)
    tasks_to_cancel = []

    # Collect tasks that need to be cancelled if they exist
    if "control_task" in controller_info:
        controller_info["control_task"].cancel()
        tasks_to_cancel.append(controller_info["control_task"])
    
    if "collection_task" in controller_info:
        controller_info["collection_task"].cancel()
        tasks_to_cancel.append(controller_info["collection_task"])
    
    # Await cancellation of all gathered tasks
    if tasks_to_cancel:
        await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
    
    # Safely shut down the controller
    if "controller" in controller_info:
        controller_info["controller"].stop_control()

    # Return the controller object for further use
    return controller_info.get("controller", None)

async def load_previous_data(controller, websocket: websockets.WebSocketServerProtocol, loop_id: str):
    """
    Loads previously saved control data from a CSV file and sends it via WebSocket.

    Args:
        controller (Controller): The controller instance associated with the control loop.
        websocket (WebSocketServerProtocol): WebSocket connection to send data.
        loop_id (str): The loop identifier for which previous data is loaded.

    Reads data from a specified CSV file and sends it to a WebSocket client.
    """
    try:
        control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
        control_consts = get_control_constant(loop_id, control_id, "control_consts")
        csv_name = control_consts["csv_name"]
        data = read_csv_file(f"{csv_name}.csv")

        # Make sure there is data and a header was found and read
        if data:
            headers = data[0].keys()  # Get headers from the first row
            # Iterate over rows starting from the first actual data row
            for row in data:
                row_dict = {key: row[key] for key in headers}
                row_dict["type"] = "data"
                await websocket.send(json.dumps(row_dict))
    except Exception as e:
        print(f"Error in load_previous_data: {e}")
        logger.error(f"Error in load_previous_data: {e}\n{traceback.format_exc()}")

async def send_status_update(websocket, status):
    """
    Sends a status update message via WebSocket.

    Args:
        websocket (WebSocketServerProtocol): WebSocket connection to send the status update.
        status (dict): Dictionary containing the status information to be sent.

    Formats and sends a JSON message containing status information over WebSocket.
    """
    try:
        await websocket.send(json.dumps({"type": "status", **status}))
    except Exception as e:
        print(f"Error in send_status_update: \n Input: {status}, \n {e}")
        logger.error(f"Error in send_status_update: \n Input: {status}, \n {e}\n{traceback.format_exc()}")

def get_controller(loop_id):
    """
    Retrieves or initializes a controller and device manager for a given loop ID.

    Args:
        loop_id (str): Identifier for the control loop for which the controller is retrieved or created.

    Returns:
        dict: A dictionary containing the controller and device manager for the specified loop.

    Manages the caching and retrieval of controller instances to ensure only one instance per loop.
    """
    try:
        # Initialize controller and device manager if they don't exist for this loop
        if loop_id not in controllers:
            controller, device_manager = c.create_controller(loop_id)
            controllers[loop_id] = {
                "controller": controller,  # Replace with appropriate constructor arguments
                "device_manager": device_manager  # Replace with appropriate constructor arguments
            }
        return controllers[loop_id]
    except Exception as e:
        print(f"Error in get_controller: \n Input: {loop_id}, \n {e}")
        logger.error(f"Error in get_controller: \n Input: {loop_id}, \n {e}\n{traceback.format_exc()}")