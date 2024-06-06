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
        print(f"Error in handling client")
        logger.error(f"WebSocket connection closed: {e.code} - {e.reason}")
        print(f"WebSocket connection closed: {e.code} - {e.reason}")
        
        error = eval(get_loop_constant(loop_id="server_consts", const="error"))
        if error:
            logger.error(f"Backup Server Starting")
            await manager_server.stop_all("fermentation_loop")
            await handle_server_error("fermentation_loop")
        else:
            update_loop_constant("server_consts", "error", "True")
            

    except Exception as e:
        logger.error(f"Unexpected error in handle_client: {e}\n{traceback.format_exc()}")
        print(f"Unexpected error: {e}\n{traceback.format_exc()}")
        error = eval(get_loop_constant(loop_id="server_consts", const="error"))
        if error:
            await manager_server.stop_all("fermentation_loop")
            await handle_server_error("fermentation_loop")
        else:
            update_loop_constant("server_consts", "error", "True")

async def process_command(websocket, data):
    try:
        command = data.get("command")
        loop_id = data.get("loopID")
        print(f"command received: {data.get('command')}")
        if "control" in command:
            await manager_server.control(loop_id, command, websocket)
        elif "collection" in command:
            await manager_server.collection(loop_id, command, websocket)
        elif "toggle" in command:
            await manager_server.toggle(loop_id, command, websocket)
    except Exception as e:
        print(f"Failed to process command : \n input: {data.get('command')}  {data.get('loopID')}, \n{e}\n{traceback.format_exc()}")
        logger.error(f"Error in process_command: \n input: {data.get('command')}  {data.get('loopID')}, \n{e}\n{traceback.format_exc()}")
        
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
        # await manager_server.stop_all("fermentation_loop")
        # await handle_server_error("fermentation_loop")

def start_backup_server(controller):
    try:
        print("Starting backup server due to critical failure.")
        backup_server.control("fermentation_loop", controller)
        logger.error("Backup Server Started")
    except Exception as e:
        print(f"Failed to start backup server: {e}")
        logger.error(f"Failed to start backup server: {e}\n{traceback.format_exc()}")
async def handle_server_error(loop_id):
    try:
        # Attempt to safely stop all and retrieve the controller
        controller = await manager_server.stop_all(loop_id)
        if controller:
            print("Controller retrieved, starting backup server.")
            # Here you would call your backup server logic, passing the controller
            start_backup_server(controller)
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


# import asyncio
# import websockets
# import json
# import manager_server
# import sys
# import os
# import signal
# import subprocess
# from websockets.exceptions import ConnectionClosedError
# import traceback
# import backup_server

# curr_directory = os.path.dirname(__file__)
# SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
# FRONTEND_DIR = os.path.join(curr_directory, "..", "frontend")
# sys.path.append(SRC_DIR)

# from resources.logging_config import logger
# from resources.utils import *

# restart_command = {
#     "command": "control",
#     "loopID": "your_loop_id",
#     "type": "restart"
# }

# async def handle_client(websocket, path):
#     try:
#         while True:
#             try:
#                 message = await asyncio.wait_for(websocket.recv(), timeout=60)
#                 data = json.loads(message)
                
#                 if data.get("type") == "ping":
#                     await websocket.send(json.dumps({"type": "pong"}))
#                 else:
#                     await process_command(websocket, data)
#             except asyncio.TimeoutError:
#                 await websocket.ping()
#     except ConnectionClosedError as e:
#         logger.error(f"WebSocket connection closed: {e.code} - {e.reason}")
#         print(f"WebSocket connection closed: {e.code} - {e.reason}")
#         code = e.code
#         if code == 1006:
#             await manager_server.stop_all("fermentation_loop")
#             await handle_server_error("fermentation_loop")

#     except Exception as e:
#         code = e.code

#         logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
#         print(f"Unexpected error: {e}\n{traceback.format_exc()}")
#         if code != 1001:
#             await manager_server.stop_all("fermentation_loop")
#             await handle_server_error("fermentation_loop")

# async def process_command(websocket, data):
#     try:
#         command = data.get("command")
#         loop_id = data.get("loopID")
#         print(f"command received: {data.get('command')}")
#         if "control" in command:
#             await manager_server.control(loop_id, command, websocket)
#         elif "collection" in command:
#             await manager_server.collection(loop_id, command, websocket)
#         elif "toggle" in command:
#             await manager_server.toggle(loop_id, command, websocket)
#     except Exception as e:
#         logger.error(f"Error processing command: {e}\n{traceback.format_exc()}")
#         print(f"Error processing command: {e}\n{traceback.format_exc()}")

# async def start_server():
#     try:
#         start_server = websockets.serve(
#             handle_client,
#             "localhost",
#             8765,
#             ping_interval=20,  # Send a ping every 20 seconds
#             ping_timeout=40  # Wait 40 seconds for a pong before closing the connection
#         )
#         async with start_server:
#             await asyncio.Future()  # Run forever
#     except Exception as e:
#         print(f"Error starting server: {e}\n{traceback.format_exc()}")
#         logger.error(f"Error starting server: {e}\n{traceback.format_exc()}")

# async def main():
#     while True:
#         try:
#             await start_server()
#         except Exception as e:
#             logger.error(f"Server encountered an error: {e}\n{traceback.format_exc()}")
#             print(f"Server encountered an error: {e}\n{traceback.format_exc()}")
#             print("Reconnecting in 10 seconds...")
#             update_loop_constant("server_consts", "load_data", "True")
#             update_loop_constant("server_consts", "restart", "True")

#             await asyncio.sleep(10)

# def shutdown(signal, loop):
#     print(f"Received exit signal {signal.name}...")
#     for task in asyncio.all_tasks(loop):
#         task.cancel()
#     loop.stop()

# def start_backup_server(controller):
#     try:
#         print("Starting backup server due to critical failure.")
#         backup_server.control("fermentation_loop", controller)
#     except Exception as e:
#         print(f"Failed to start backup server: {e}")
#         logger.error(f"Failed to start backup server: {e}\n{traceback.format_exc()}")
# async def handle_server_error(loop_id):
#     try:
#         # Attempt to safely stop all and retrieve the controller
#         controller = await manager_server.stop_all(loop_id)
#         if controller:
#             print("Controller retrieved, starting backup server.")
#             # Here you would call your backup server logic, passing the controller
#             start_backup_server(controller)
#         else:
#             print("No controller was active or available.")
#     except Exception as e:
#         print(f"Failed to handle server error properly: {e}")
#         logger.error(f"Server error handling failed: {e}\n{traceback.format_exc()}")


# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()

#     for sig in (signal.SIGINT, signal.SIGTERM):
#         loop.add_signal_handler(sig, shutdown, sig, loop)

#     try:
#         loop.run_until_complete(main())
#     finally:
#         loop.close()
