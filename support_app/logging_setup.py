"""Application logging configuration.

Logs go to a rotating file under ``%APPDATA%\\MacrosoftSupport`` and are
mirrored to the console, so existing troubleshooting workflows keep working.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from support_app.settings import APP_DATA_PATH

LOG_FILE_NAME = "support_app.log"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
LOG_MAX_BYTES = 2_000_000
LOG_BACKUP_COUNT = 3

_configured = False


def log_file_path() -> str:
    """Full path of the current application log file."""
    return os.path.join(APP_DATA_PATH, LOG_FILE_NAME)


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a console and a rotating file handler to the root logger once."""
    global _configured
    if _configured:
        return

    _configured = True
    root = logging.getLogger()
    root.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    try:
        os.makedirs(APP_DATA_PATH, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file_path(),
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
    except OSError:
        logging.getLogger(__name__).warning("Could not open log file %s", log_file_path())


def get_logger(name: str) -> logging.Logger:
    """Return a named logger (handlers are configured by ``configure_logging``)."""
    return logging.getLogger(name)
