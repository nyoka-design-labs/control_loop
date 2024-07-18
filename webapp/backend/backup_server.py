import sys
import os
import traceback
import time

curr_directory = os.path.dirname(__file__)
SRC_DIR = os.path.join(curr_directory, "..", "..", "src")
sys.path.append(SRC_DIR)

from resources.utils import get_loop_constant
import controllers_mqtt as c
from resources.logging_config import setup_logger
from resources.error_notification import send_notification

logger = setup_logger()
INTERVAL = get_loop_constant("server_consts", "interval")
testing = eval(get_loop_constant(loop_id="server_consts", const="testing"))
controllers = {}

def control(loop_id, controller):
    """
    Initiates the control process for the backup server either with a provided controller or by retrieving one.

    Args:
        loop_id (str): Identifier for the control loop.
        controller (Controller): Optional; a controller object to use for the control task. If not provided, the controller is retrieved using `get_controller`.

    This function starts the control task and sends a notification when the backup server starts. In case of an error, it sends a crash notification and logs the error.
    """
    try:
        send_notification(f"Backup Server Started", "H")
        if controller:
            control_task(controller)
        else:
            controller_info = get_controller(loop_id)
            control_task(controller_info["controller"])
    except Exception as e:
        send_notification(f"Backup Server Crashed")
        # print(f"Error in backup server control_task: {e}")
        logger.error(f"Error in backup server control_task: {e}\n{traceback.format_exc()}")
        

def control_task(controller):
    """
    Runs the control task continuously, executing control logic at regular intervals defined by INTERVAL.

    Args:
        controller (Controller): The controller instance that manages and executes the control logic.

    Continuously monitors and logs the operation of the backup server. Handles data acquisition and status reporting from the controller, pausing for INTERVAL seconds between cycles. Notifies and logs on crash.
    """
    try:
        while True:
            # print("back up server running")
            logger.info("back up server running")
            data, status = controller.start_control()
            logger.info(f"data: {data}")
            time.sleep(INTERVAL)
    except Exception as e:
        send_notification(f"Backup Server Crashed in control_task")
        # print(f"Error in backup server control_task: {e}")
        logger.error(f"Error in backup server control_task: {e}\n{traceback.format_exc()}")
    except KeyboardInterrupt as e:
        controller.stop_control()


def get_controller(loop_id):
    """
    Retrieves or initializes a controller and device manager for a specific loop ID.

    Args:
        loop_id (str): Identifier for the control loop for which the controller is retrieved or created.

    Returns:
        dict: A dictionary containing the controller and device manager objects for the specified loop.

    This function checks if a controller for the given loop ID is already initialized and stored; if not, it initializes and stores it. This ensures that there is a single instance of the controller and device manager per loop.
    """
    if loop_id not in controllers:
        controller = c.create_controller(loop_id)
        controllers[loop_id] = {"controller": controller}
    return controllers[loop_id]
