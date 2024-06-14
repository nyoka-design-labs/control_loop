import asyncio
import websockets
import json
import manager_server
import sys
import os
from websockets.exceptions import ConnectionClosedError
import traceback
import backup_server
curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
FRONTEND_DIR = os.path.join(curr_directory, "..", "frontend")
sys.path.append(SRC_DIR)

from resources.logging_config import logger
from resources.utils import *
from resources.error_notification import send_notification
backup_server_loop = "fermentation_loop"
curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

error = False
async def handle_client(websocket, path):
    try:
        while True:
            message = await asyncio.wait_for(websocket.recv(), timeout=60)
            data = json.loads(message)
            
            if data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
            else:
                await process_command(websocket, data)
    except ConnectionClosedError as e:
        logger.error(f"WebSocket connection closed: {e.code} - {e.reason}")
        print(f"Error in handling client\nWebSocket connection closed: {e.code} - {e.reason}")
        error = eval(get_loop_constant(loop_id="server_consts", const="error"))
        if error:
            try:
                logger.error(f"Backup Server Starting")
                send_notification(f"WebSocket connection closed: {e.code}\nAttempting to start backup server.")
                await handle_server_error()
            except Exception as e:    
                send_notification(f"Unexpected error in trying to run backup protocol from handle_client: {e}\n{traceback.format_exc()}")
                logger.error(f"Unexpected error in trying to run backup protocol from handle_client: {e}\n{traceback.format_exc()}")
                print(f"Unexpected error: {e}\n{traceback.format_exc()}")
        else:
            update_loop_constant("server_consts", "error", "True")
            

    except Exception as e:
        logger.error(f"Unexpected error in handle_client: {e}\n{traceback.format_exc()}")
        print(f"Error in handling client\nUnexpected error: {e}\n{traceback.format_exc()}")
        error = eval(get_loop_constant(loop_id="server_consts", const="error"))
        if error:
            try:
                logger.error(f"Backup Server Starting")
                send_notification(f"Unexpected error in handle_client: {e}\n{traceback.format_exc()}")
                await handle_server_error()
            except Exception as e:
                send_notification(f"Unexpected error in trying to run backup protocol from handle_client: {e}\n{traceback.format_exc()}")
                logger.error(f"Unexpected error in trying to run backup protocol from handle_client: {e}\n{traceback.format_exc()}")
                print(f"Unexpected error: {e}\n{traceback.format_exc()}")
        else:
            update_loop_constant("server_consts", "error", "True")

async def process_command(websocket, data):
    try:
        command = data.get("command")
        loop_id = data.get("loopID")
        print(f"command received: {data.get('command')}")
        update_loop_constant("server_consts", "control_running", loop_id)
        if "control" in command:
            await manager_server.control(loop_id, command, websocket)
        elif "collection" in command:
            await manager_server.collection(loop_id, command, websocket)
        elif "toggle" in command:
            await manager_server.toggle(loop_id, command, websocket)
    except Exception as e:
        print(f"Failed to process command : \n input: {data.get('command')}  {data.get('loopID')}, \n{e}\n{traceback.format_exc()}")
        logger.error(f"Error in process_command: \n input: {data.get('command')}  {data.get('loopID')}, \n{e}\n{traceback.format_exc()}")
        send_notification(f"Error in process_command: \n input: {data.get('command')}  {data.get('loopID')}, \n{e}")
        
        
async def start_server():
    try:
        server = await websockets.serve(
            handle_client,
            "localhost",
            8765,
            ping_interval=20,  # Send a ping every 20 seconds
            ping_timeout=40  # Wait 40 seconds for a pong before closing the connection
        )
        await server.wait_closed()  # Run server until it is closed
    except Exception as e:
        print(f"Failed to start server: {e}\n{traceback.format_exc()}")
        logger.error(f"Error in start_server: {e}\n{traceback.format_exc()}")
        send_notification(f"Error in start_server: {e}\n{traceback.format_exc()}")

def start_backup_server(controller, loop_id):
    try:
        print("Starting backup server due to critical failure.")
        backup_server.control(loop_id, controller)
        logger.error("Backup Server Started")
    except Exception as e:
        print(f"Failed to start backup server: {e}")
        logger.error(f"Failed to start backup server: {e}\n{traceback.format_exc()}")
        
async def handle_server_error():
    loop_id = get_loop_constant(loop_id="server_consts", const="control_running")
    try:
        # Attempt to safely stop all and retrieve the controller
        controller = await manager_server.stop_all(loop_id)
        if controller:
            print("Controller retrieved, starting backup server.")
            start_backup_server(controller, loop_id)
        else:
            print("No controller was active or available.")
    except Exception as e:
        print(f"Failed to handle server error properly: {e}")
        logger.error(f"Server error handling failed: {e}\n{traceback.format_exc()}")

async def main():
    await start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        update_loop_constant("server_consts", "error", "False")
        print("\n program terminated")
