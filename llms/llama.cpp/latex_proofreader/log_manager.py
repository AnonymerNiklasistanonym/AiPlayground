import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent


def setup_logging():
    logger = logging.getLogger()
    # lowest level of all loggers
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s - %(name)s] %(message)s"
    )

    # console (only info per default)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # file (log lowest level)
    log_dir = ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(log_dir / "app.log", maxBytes=5_000_000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
