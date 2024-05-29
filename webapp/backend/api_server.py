import asyncio
import websockets
import json
import manager_server
import sys
import os
import signal
import subprocess
from websockets.exceptions import ConnectionClosedError
import traceback

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
FRONTEND_DIR = os.path.join(curr_directory, "..", "frontend")
sys.path.append(SRC_DIR)

from resources.logging_config import logger
from resources.utils import *

restart_command = {
    "command": "control",
    "loopID": "your_loop_id",
    "type": "restart"
}

async def handle_client(websocket, path):
    try:
        if eval(get_loop_constant("server_consts", "restart")):
            await restart_frontend()
            await process_command(websocket, restart_command)
            update_loop_constant("server_consts", "restart", "False")
            
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=60)
                data = json.loads(message)
                
                if data.get("type") == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))
                else:
                    await process_command(websocket, data)
            except asyncio.TimeoutError:
                await websocket.ping()
    except ConnectionClosedError as e:
        logger.error(f"WebSocket connection closed: {e.code} - {e.reason}")
        print(f"WebSocket connection closed: {e.code} - {e.reason}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
        print(f"Unexpected error: {e}\n{traceback.format_exc()}")

async def restart_frontend():
    try:
        # Stop the frontend
        subprocess.run(["npm", "stop"], check=True, cwd=FRONTEND_DIR)
        # Start the frontend
        subprocess.run(["npm", "start"], check=True, cwd=FRONTEND_DIR)
        print("Frontend restarted successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error restarting frontend: {e}\n{traceback.format_exc()}")
        print(f"Error restarting frontend: {e}\n{traceback.format_exc()}")

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
        logger.error(f"Error processing command: {e}\n{traceback.format_exc()}")
        print(f"Error processing command: {e}\n{traceback.format_exc()}")

async def start_server():
    try:
        start_server = websockets.serve(
            handle_client,
            "localhost",
            8765,
            ping_interval=20,  # Send a ping every 20 seconds
            ping_timeout=40  # Wait 40 seconds for a pong before closing the connection
        )
        async with start_server:
            await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Error starting server: {e}\n{traceback.format_exc()}")
        print(f"Error starting server: {e}\n{traceback.format_exc()}")

async def main():
    while True:
        try:
            await start_server()
        except Exception as e:
            logger.error(f"Server encountered an error: {e}\n{traceback.format_exc()}")
            print(f"Server encountered an error: {e}\n{traceback.format_exc()}")
            print("Reconnecting in 10 seconds...")
            update_loop_constant("server_consts", "load_data", "True")
            update_loop_constant("server_consts", "restart", "True")

            await asyncio.sleep(10)

def shutdown(signal, loop):
    print(f"Received exit signal {signal.name}...")
    for task in asyncio.all_tasks(loop):
        task.cancel()
    loop.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown, sig, loop)

    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
