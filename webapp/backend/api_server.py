import asyncio
import websockets
import json
import sys
import os
import traceback
import manager_server
import backup_server
from resources.logging_config import setup_logger
from resources.utils import *
from resources.error_notification import send_notification

# Set the current directory and source directories
curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

logger = setup_logger()
current_websocket = None
def handle_error(exception, context, data=None, notify=True):
    """
    Handles errors by logging, printing to standard output, and optionally sending notifications.

    Args:
        exception (Exception): The exception that triggered the error handling.
        context (str): A brief description of where the error occurred, providing context.
        data (dict, optional): Additional data related to the error to include in logs.
        notify (bool, default=True): Whether to send out a notification about the error.

    Logs detailed error information, including a traceback, and sends a notification if enabled.
    """
    error_message = f"Error in {context}\nUnexpected error: {exception}\n{traceback.format_exc()}"
    logger.error(error_message)
    logger.error(f"type of exception: {type(exception)}")

    # print(error_message)
    if data:
        logger.error(f"Input data: {data}")
        # print(f"Input data: {data}")
    if notify:
        send_notification(f"Unexpected error in {context}")

async def send_config_data(websocket):
    try:
        # Fetch configuration for fermentation loop
        fer_control_id = get_loop_constant("fermentation_loop", "chosen_control")
        fermentation_config = get_control_constant("fermentation_loop", fer_control_id, "control_config")

        # Fetch configuration for concentration loop
        con_control_id = get_loop_constant("concentration_loop", "chosen_control")
        concentration_config = get_control_constant("concentration_loop", con_control_id, "control_config")

        # Combine both configurations into a single data structure
        combined_config = {
            "fermentation_loop": fermentation_config,
            "concentration_loop": concentration_config
        }

        await websocket.send(json.dumps({
            "type": "config_setup",
            "data": combined_config
        }))
    except Exception as e:
        handle_error(e, "send_config_data", notify=False)

async def send_pump_data(websocket):
    """
    Sends the pump data to the frontend.

    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection to send data through.
    """
    try:
        fer_control_id = get_loop_constant("fermentation_loop", "chosen_control")
        fermentation_pumps = get_control_constant("fermentation_loop", fer_control_id, "pumps")

        con_control_id = get_loop_constant("concentration_loop", "chosen_control")
        concentration_pumps = get_control_constant("concentration_loop", con_control_id, "pumps")

        pump_data = {
            "fermentation_loop": fermentation_pumps,
            "concentration_loop": concentration_pumps
        }

        await websocket.send(json.dumps({
            "type": "button_setup",
            "data": pump_data
        }))
    except Exception as e:
        handle_error(e, "send_pump_data", notify=False)

async def update_config(data):
    try:
        control_id = get_loop_constant(data["loop_id"], "chosen_control")
        control_config = get_control_constant(data["loop_id"], control_id, "control_config")

        key = data["key"]
        value = float(data["value"])
        control_config[key] = value

        update_control_constant(data["loop_id"], control_id, "control_config", control_config)

        logger.info(f"Updated {key} to {value} in control_config")
    except Exception as e:
        handle_error(e, "update_config", data)
        
async def handle_client(websocket):
    """
    Continuously listens for and processes messages from clients over a WebSocket.

    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection to handle.

    Listens for incoming messages on the websocket, processes them based on type ('ping' or command), and sends appropriate responses. Handles exceptions by logging and notifying errors, and potentially initiating backup procedures.
    """
    global current_websocket
    current_websocket = websocket
    try:
        try:
            await send_pump_data(websocket)
            await send_config_data(websocket)
        except websockets.exceptions.ConnectionClosedOK:
            handle_error(e, "intial_startup", notify=False)
        except websockets.exceptions.ConnectionClosedError:
            handle_error(e, "intial_startup", notify=False)
        while True:
            message = await asyncio.wait_for(websocket.recv(), timeout=60)
            data = json.loads(message)
            if data.get("type") == "ping":
                # print("recieved ping")
                logger.info("recieved ping from frontend")
                await websocket.send(json.dumps({"type": "pong"}))
            elif data.get("type") == "update_config":
                await update_config(data)
            else:
                await process_client_command(websocket, data)
    except Exception as e:       
        error = eval(get_loop_constant(loop_id="server_consts", const="error"))
 
        if error:
            try:
                handle_error(e, "handle_client")
                # print("starting backup server")
                logger.error("Backup Server Starting")
                await handle_server_error()
            except Exception as e:
                handle_error(e, "backup protocol in handle_client")
        else:
            update_loop_constant("server_consts", "error", "True")
            
    

async def process_client_command(websocket, data):
    """
    Processes a command received from the client through WebSocket.

    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection to send responses.
        data (dict): The JSON-decoded data received from the client, containing the command and other parameters.

    Identifies the command from the data and executes relevant actions. It updates loop constants, handles control commands, collection requests, and toggles based on the command type.
    """
    try:
        command = data.get("command")
        loop_id = data.get("loopID")
        # print(f"Command received: {command}")
        logger.info(f"Command received: {command}")
        update_loop_constant("server_consts", "control_running", loop_id)
        if "control" in command:
            await manager_server.control(loop_id, command, websocket)
        elif "collection" in command:
            await manager_server.collection(loop_id, command, websocket)
        elif "toggle" in command:
            await manager_server.toggle(loop_id, command, websocket)
    except Exception as e:
        handle_error(e, "process_client_command", data)

async def start_server():
    """
    Starts a WebSocket server to manage client connections and handle messages.

    Behavior:
        Sets up and starts a WebSocket server configured for a specific host and port. Handles connections indefinitely unless interrupted by errors or manual closure.

    Manages WebSocket connections, facilitating real-time communication with clients, handling pings, and ensuring connections are maintained with appropriate timeouts.
    """ 
    try:
        server = await websockets.serve(
            handle_client,
            "localhost",
            8765,
            ping_interval=20,  # Send a ping every 20 seconds
            ping_timeout=40  # Wait 40 seconds for a pong before closing the connection
        )
        await server.wait_closed()
    except Exception as e:
        handle_error(e, "start_server")

def start_backup_server(controller, loop_id):
    """
    Initiates a backup server if the primary server encounters critical failures.

    Args:
        controller (object): The controller object that will be used by the backup server.
        loop_id (str): The identifier for the control loop that the backup server will manage.

    Starts a backup server using the given controller and loop ID to ensure continued operation despite failures in the primary server setup.
    """
    try:
        # print("Starting backup server due to critical failure.")
        logger.info("Starting backup server due to critical failure.")
        backup_server.control(loop_id, controller)
        logger.error("Backup Server Started")
    except Exception as e:
        handle_error(e, "start_backup_server")

async def handle_server_error():
    """
    Handles unexpected errors in server operations by attempting to gracefully stop activities and start a backup server.

    Attempts to retrieve and stop all current server activities based on the control loop's running state and starts a backup server if a controller is available.
    """
    loop_id = get_loop_constant(loop_id="server_consts", const="control_running")
    try:
        controller = await manager_server.stop_all(loop_id)
        if controller:
            # print("Controller retrieved, starting backup server.")
            logger.info("Controller retrieved, starting backup server.")
            start_backup_server(controller, loop_id)
        else:
            # print("No controller was active or available.")
            logger.info("No controller was active or available.")
    except Exception as e:
        handle_error(e, "handle_server_error")

async def close_websocket():
    global current_websocket
    if current_websocket:
        await current_websocket.close(code=1001, reason='Server shutdown')
        current_websocket = None

async def main():
    try:
        server = await websockets.serve(
            handle_client,
            "localhost",
            8765,
            ping_interval=20,
            ping_timeout=40
        )
        await server.wait_closed()
    except Exception as e:
        handle_error(e, "start_server")
    finally:
        await close_websocket()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
        asyncio.run(close_websocket())
        update_loop_constant("server_consts", "error", "False")