import chump
import asyncio
from resources.logging_config import setup_logger
import traceback
import time
logger = setup_logger()

def send_notification(message, priority="E"):
    try:
        app = chump.Application('aubr7cnv73kbgv9tvdmzg5k9d7xe12')
        user = app.get_user('u3h3wzk85stgd5cjaz3eecusmq3ozm')
        print(user.is_authenticated, user.devices)
        if priority == "E":
            priority = chump.EMERGENCY
        else:
            priority = chump.HIGH

        message = user.send_message(f"{message}", priority=priority)

        print(f"Message Sent: {message.is_sent}\nMessage ID:{message.id}\nMessage Sent At: {str(message.sent_at)}")
    except Exception as e:
        print(f"Error in send_notification: {e}\n{traceback.format_exc()}")
        logger.error(f"Error in send_notification: {e}\n{traceback.format_exc()}")
        
if __name__ == "__main__":
    asyncio.run(send_notification("yo it worked"))
