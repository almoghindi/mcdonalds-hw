import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIRECTORY = Path(os.getenv('LOG_DIR', PROJECT_ROOT / 'logs'))
LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
LOG_FILENAME = os.getenv('LOG_FILE', 'application.log')
LOG_PATH = LOG_DIRECTORY / LOG_FILENAME

MAX_LOG_FILE_SIZE = 10 * 1024 * 1024 
LOG_BACKUP_COUNT = 5


def get_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    file_handler = RotatingFileHandler(
        filename=str(LOG_PATH),
        maxBytes=MAX_LOG_FILE_SIZE,
        backupCount=LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

logger = get_logger(__name__)
