import logging
import sys
from config.settings import settings
import os

def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            # Ideally, file handler would be added here if needed, but Docker logs are best collected via stdout
        ]
    )
    
    # Ensure log directory exists if we were to use a FileHandler
    log_dir = os.path.dirname(settings.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(settings.APP_NAME)
    return logger

logger = setup_logging()
