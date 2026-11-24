"""Persistent application settings and installer access-code helpers.

All filesystem persistence for the app lives here so callers never have to
know the on-disk layout.  Writes are atomic to avoid leaving a half-written
settings file behind when the process is interrupted.
"""

import json
import logging
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

APP_DATA_PATH = os.path.join(os.getenv('APPDATA') or os.path.expanduser('~'), 'MacrosoftSupport')
CONFIG_FILE_PATH = os.path.join(APP_DATA_PATH, 'config.json')
INSTALLER_PATH_FILE_NAME = "installer_path.txt"

DEFAULT_ACCESS_CODE = "Nenájdené"


@dataclass
class AppSettings:
    """Persisted, user-scoped application settings."""

    is_lectoure: Optional[bool] = None


def write_text_atomic(path: str, content: str) -> None:
    """Write *content* to *path* via a temporary file and an atomic replace."""
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            file.write(content)
        os.replace(temp_path, path)
    except Exception:
        try:
            os.remove(temp_path)
        except OSError as cleanup_error:
            logger.debug("Could not remove temporary settings file: %s", cleanup_error)
        raise


def load_settings() -> AppSettings:
    """Read the settings file, falling back to defaults when missing/corrupt."""
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError) as e:
        logger.debug("Could not read settings from %s: %s", CONFIG_FILE_PATH, e)
        return AppSettings()

    if not isinstance(data, dict):
        return AppSettings()

    is_lectoure = data.get('is_lectoure')
    return AppSettings(is_lectoure=is_lectoure if isinstance(is_lectoure, bool) else None)


def save_settings(settings: AppSettings) -> None:
    """Persist *settings*, preserving unknown keys already in the file."""
    data = {}
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
            existing = json.load(file)
            if isinstance(existing, dict):
                data = existing
    except (OSError, json.JSONDecodeError) as e:
        logger.debug("Could not merge existing settings from %s: %s", CONFIG_FILE_PATH, e)

    data['is_lectoure'] = settings.is_lectoure
    write_text_atomic(CONFIG_FILE_PATH, json.dumps(data, indent=4))


def extract_installer_code(input_str: str):
    """Extract the short access code from an installer file name."""
    try:
        pattern = re.compile(
            r'MacrosoftSupportInstaller_([^_]+)_.*?\.exe',
            re.IGNORECASE
        )

        if match := pattern.search(input_str):
            code = match.group(1)
            if len(code) > 0:
                return code

    except Exception as e:
        logger.debug("Could not extract the installer access code: %s", e)


def installer_path_file() -> str:
    """Path of the file that stores the installer name next to the exe."""
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, INSTALLER_PATH_FILE_NAME)


def save_login_info(access_code: str) -> None:
    """Persist the current installer access code next to the executable."""
    write_text_atomic(
        installer_path_file(),
        f"Installer Path: MacrosoftSupportInstaller_{access_code}_.exe\n",
    )


def get_access_code() -> str:
    """Get the access code from the installer file, falling back to legacy names."""
    script_name = os.path.basename(sys.argv[0])
    access = DEFAULT_ACCESS_CODE
    if "installrustdesk_" in script_name:
        access = (
            script_name.replace("installrustdesk_", "")
            .replace(".py", "")
            .replace(".exe", "")
        )
    elif script_name.endswith(".exe"):
        try:
            with open(installer_path_file(), 'r', encoding='utf-8') as file:
                content = file.read().strip()
                code = extract_installer_code(content)
                if code:
                    return code
        except Exception as e:
            logger.debug("Could not read the installer access code file: %s", e)

    return access
