"""
Central logging configuration for CareVoice AI.
"""

import logging

from config import (
    DATE_FORMAT,
    LOG_FORMAT,
    LOG_LEVEL,
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance.

    Parameters
    ----------
    name : str
        Usually __name__.

    Returns
    -------
    logging.Logger
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    logger.propagate = False

    return logger