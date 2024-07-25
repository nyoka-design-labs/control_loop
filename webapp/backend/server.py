import sys
import os
import asyncio
import threading
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.utils import *
import system_manager

app = Flask(__name__)
api = Api(app)

# Create an asyncio queue for commands
command_queue = asyncio.Queue()

# Define the async method for processing commands from the queue
async def process_commands():
    while True:
        command = await command_queue.get()
        try:
            await process_command(command)
        except Exception as e:
            print(f"Error processing command {command}: {e}")
        command_queue.task_done()

# Async command processing method
async def process_command(command):
    print(f"Processing command: {command}")
    loop_id = command.get("loopID")
    if "control" in command.get("command"):
        await system_manager.control(loop_id, command.get("command"))
    elif "collection" in command.get("command"):
        await system_manager.collection(loop_id, command.get("command"))
    elif "toggle" in command.get("command"):
        await system_manager.toggle(loop_id, command.get("command"))
    return {"status": "Command processed"} 

# Start the asyncio loop in a separate thread
def start_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

loop = asyncio.new_event_loop()
thread = threading.Thread(target=start_async_loop, args=(loop,))
thread.start()

class Config(Resource):
    def get(self):
        try:
            fer_control_id = get_loop_constant("fermentation_loop", "chosen_control")
            con_control_id = get_loop_constant("concentration_loop", "chosen_control")

            con_sp_config = get_control_constant("concentration_loop", con_control_id, "control_config")
            con_pump_config = get_control_constant("concentration_loop", con_control_id, "pumps")
            ferm_sp_config = get_control_constant("fermentation_loop", fer_control_id, "control_config")
            ferm_pump_config = get_control_constant("fermentation_loop", fer_control_id, "pumps")

            sp_config = {
                "fermentation_loop": ferm_sp_config,
                "concentration_loop": con_sp_config
            }

            pump_config = {
                "fermentation_loop": ferm_pump_config,
                "concentration_loop": con_pump_config
            }

            combined_config = {
                "sp_config": sp_config,
                "pump_config": pump_config
            }

            return jsonify(combined_config)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    
    def post(self):
        try:
            data = request.get_json()
            control_id = get_loop_constant(data["loop_id"], "chosen_control")
            control_config = get_control_constant(data["loop_id"], control_id, "control_config")

            key = data["key"]
            value = float(data["value"])
            control_config[key] = value

            update_control_constant(data["loop_id"], control_id, "control_config", control_config)
            return jsonify({"status": "Config updated"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

class Command(Resource):
    def post(self):
        try:
            data = request.get_json()
            if data and "command" in data:
                asyncio.run_coroutine_threadsafe(command_queue.put(data), loop)
                return jsonify({'status': 'command added to queue'})
            return jsonify({'status': 'no command found'}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

api.add_resource(Config, "/config")
api.add_resource(Command, "/command")

if __name__ == '__main__':
    asyncio.run_coroutine_threadsafe(process_commands(), loop)
    app.run(host="localhost", debug=True)