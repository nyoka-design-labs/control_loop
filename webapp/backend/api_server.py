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
    Handle errors by logging, printing, and sending notifications.

    Parameters:
    exception (Exception): The exception to handle.
    context (str): The context in which the error occurred.
    data (dict, optional): Additional data related to the error.
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
    Handle incoming messages from the client, process them, and send responses.

    Parameters:
    websocket (websockets.WebSocketServerProtocol): The websocket connection to the client.
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
    Process a command received from the client.

    Parameters:
    websocket (websockets.WebSocketServerProtocol): The websocket connection to the client.
    data (dict): The JSON-decoded data received from the client.
    """
    try:
        command = data.get("command")
        loop_id = data.get("loopID")
        print(f"Command received: {command}")
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
    Start the WebSocket server and listen for connections.
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
    Start the backup server in case of critical failure.

    Parameters:
    controller (object): The controller object to be used by the backup server.
    loop_id (str): The loop ID for the backup server control.
    """
    try:
        print("Starting backup server due to critical failure.")
        backup_server.control(loop_id, controller)
        logger.error("Backup Server Started")
    except Exception as e:
        handle_error(e, "start_backup_server")

async def handle_server_error():
    """
    Handle errors in the server by attempting to stop all operations and start the backup server.
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
    The main entry point for the program to start the WebSocket server.
    """
    await start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        update_loop_constant("server_consts", "error", "False")
        print("\nProgram terminated")