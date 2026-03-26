"""Development mode configuration for enhanced logging and debugging.

Provides FR40: development mode with configurable log levels and
enhanced agent coordination debugging output.
"""

from __future__ import annotations

import logging
import os

from scripts.utilities.logging_setup import setup_logging


def enable_dev_mode(log_to_file: bool = True) -> logging.Logger:
    """Enable development mode with DEBUG logging and file output.

    Sets the ``DEV_MODE`` environment flag and configures all loggers
    for maximum verbosity.

    Returns:
        The root project logger at DEBUG level.
    """
    os.environ["DEV_MODE"] = "1"
    logger = setup_logging(
        name="course-agents",
        level=logging.DEBUG,
        log_to_file=log_to_file,
    )
    logging.getLogger("scripts").setLevel(logging.DEBUG)
    logging.getLogger("skills").setLevel(logging.DEBUG)
    logger.info("Development mode enabled — DEBUG logging active")
    return logger


def is_dev_mode() -> bool:
    """Check if development mode is active."""
    return os.environ.get("DEV_MODE", "").lower() in ("1", "true", "yes")
