"""
Logging Configuration Module.

Sets up a centralized logging system that writes to both
the console (stdout) and a rotating log file (logs/bot.log).
All API requests, responses, errors, and runtime events are captured.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "bot.log")

# Maximum size per log file: 5 MB, keep 3 backups
MAX_LOG_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3

# Formatting
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    """
    Configure and return the root application logger.

    Creates:
        - A file handler  → logs/bot.log  (DEBUG and above)
        - A console handler → stdout       (INFO and above)

    Parameters
    ----------
    level : int
        Minimum logging level for the file handler.
        Defaults to ``logging.DEBUG``.

    Returns
    -------
    logging.Logger
        The configured root logger named ``"trading_bot"``.
    """
    # Ensure log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)

    # Prevent duplicate handlers on repeated calls
    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # ── File handler (rotating) ──────────────────────────────────────────
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # ── Console handler ──────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.debug("Logging initialised – file: %s", LOG_FILE)
    return logger
