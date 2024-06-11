import sys
import os
import traceback
import time
import asyncio

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.utils import get_loop_constant, update_loop_constant
import controllers as c
from resources.logging_config import logger
from resources.error_notification import send_notification

INTERVAL = get_loop_constant("server_consts", "interval")
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
controllers = {}

def control(loop_id, controller):
    try:
        send_notification(f"Backup Server Started.", "H")
        if controller:
            control_task(controller)
        else:
            controller_info = get_controller(loop_id)
            control_task(controller_info["controller"])
    except Exception as e:
        send_notification(f"Backup Server Crashed in control")
        print(f"Error in backup server control_task: {e}")
        logger.error(f"Error in backup server control_task: {e}\n{traceback.format_exc()}")
        

def control_task(controller):
    try:
        while True:
            print("back up server running")
            data, status = controller.start_control()
            print(f"data: {data}")
            time.sleep(INTERVAL)
    except Exception as e:
        send_notification(f"Backup Server Crashed in control_task")
        print(f"Error in backup server control_task: {e}")
        logger.error(f"Error in backup server control_task: {e}\n{traceback.format_exc()}")
    except KeyboardInterrupt as e:
        controller.stop_control()


def get_controller(loop_id):
    if loop_id not in controllers:
        control_id = get_loop_constant(loop_id=loop_id, const="chosen_control")
        controller, device_manager = c.create_controller(loop_id, control_id, testing)
        controllers[loop_id] = {"controller": controller, "device_manager": device_manager}
    return controllers[loop_id]
