"""Logging setup."""

import logging
import os
from logging.handlers import RotatingFileHandler
from .config import config


def setup_logging():
    logger = logging.getLogger("aidoffline")
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))

    fmt_file = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    fmt_console = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)

    fh = RotatingFileHandler(config.LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
    fh.setFormatter(fmt_file)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt_console)

    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger


logger = setup_logging()
