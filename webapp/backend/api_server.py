import asyncio
import websockets
import json
import sys
import os
import traceback
from websockets.exceptions import ConnectionClosedError
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
    print(error_message)
    if data:
        logger.error(f"Input data: {data}")
        print(f"Input data: {data}")
    if notify:
        send_notification(f"Unexpected error in {context}: {exception}\n{traceback.format_exc()}")

async def handle_client(websocket):
    """
    Continuously listens for and processes messages from clients over a WebSocket.

    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection to handle.

    Listens for incoming messages on the websocket, processes them based on type ('ping' or command), and sends appropriate responses. Handles exceptions by logging and notifying errors, and potentially initiating backup procedures.
    """
    try:
        while True:
            message = await asyncio.wait_for(websocket.recv(), timeout=60)
            data = json.loads(message)
            if data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
            else:
                await process_client_command(websocket, data)
    except Exception as e:
        handle_error(e, "handle_client", notify=False)
        error = eval(get_loop_constant(loop_id="server_consts", const="error"))
        if error:
            try:
                handle_error(e, "handle_client")
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
        print(f"Command received: {command}")
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
        print("Starting backup server due to critical failure.")
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
            print("Controller retrieved, starting backup server.")
            start_backup_server(controller, loop_id)
        else:
            print("No controller was active or available.")
    except Exception as e:
        handle_error(e, "handle_server_error")

async def main():
    """
    The main entry point for starting the WebSocket server.

    Executes the setup and start of the WebSocket server, managing incoming client connections and facilitating real-time data exchange and control commands.
    """
    await start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        update_loop_constant("server_consts", "error", "False")
        print("\nProgram terminated")