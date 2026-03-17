# -*- coding: utf-8 -*-
"""
Provides a simple, easy-to-use logging configuration.
Ideal for distribution—requires no extra files or configuration.
"""

import logging
import logging.handlers
from pathlib import Path

LOGGING_OUTPUT_FILE = "app_cvyt.log"


def set_logging_settings(log_location_path: str = None):
    """Set logging settings.

    Args:
    log_location_path (str)= path to the folder, where the 'app_log file'
    (optional) will be stored
    """
    handler = get_logging_handler(log_location_path)
    logging.basicConfig(
        handlers=[handler],
        level=logging.INFO
    )


def get_logging_handler(log_location_path: str = None) ->\
        logging.handlers.RotatingFileHandler:
    """Settings for logging.

    Args:
    log_location_path (str)= path to the folder, where the 'app_log file'
    (optional) will be stored
    """
    handler = None
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s -ln: %(lineno)d - %(levelname)s - %(message)s')
    try:
        # Logging file destination
        log_destination = Path(log_location_path).\
                          joinpath(LOGGING_OUTPUT_FILE) if log_location_path\
                          else Path(__file__).parents[2].joinpath(
                               LOGGING_OUTPUT_FILE)

        if log_destination:
            # Set the "behaviour" of the log files(number of history file
            # max. file size)
            handler = logging.handlers.RotatingFileHandler(
                filename=str(log_destination),
                maxBytes=1000000,
                backupCount=3)
            handler.setFormatter(formatter)
        return handler
    except Exception as e:
        raise e
