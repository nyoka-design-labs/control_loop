import logging
import os

# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure the logger
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a logger object
logger = logging.getLogger(__name__)
