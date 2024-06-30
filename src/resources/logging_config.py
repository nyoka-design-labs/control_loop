import logging
import os
from datetime import datetime

class FlushingFileHandler(logging.FileHandler):
    """ Custom file handler that flushes the write buffer after each logging call. """
    def emit(self, record):
        super().emit(record)
        self.flush()

def setup_logger():
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logger = logging.getLogger('my_app_logger')
    logger.handlers.clear()  # Clear existing handlers to avoid duplicate logs
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    current_date = datetime.now().strftime("%Y-%m-%d")
    info_filename = os.path.join(log_directory, f'{current_date}_info.log')
    error_filename = os.path.join(log_directory, f'{current_date}_error.log')

    info_handler = FlushingFileHandler(info_filename, mode='a')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)

    error_handler = FlushingFileHandler(error_filename, mode='a')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger