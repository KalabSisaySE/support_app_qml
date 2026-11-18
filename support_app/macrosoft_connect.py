"""Shared operations for the bundled Macrosoft Connect application.

Every worker used to rebuild the same install paths, service definition and
RustDesk reporting loop.  This module keeps that knowledge in one place so
callers only deal with the behaviour they actually need.
"""

import os
import subprocess
import time

from support_app import api, app_config
from support_app.rust_service_manager import ServiceManager

PROGRAM_FILES_DIR = r"C:\Program Files"


def app_install_dir():
    """Directory where Macrosoft Connect is installed."""
    return os.path.join(PROGRAM_FILES_DIR, app_config.NAME)


def app_executable_path():
    """Full path of the installed Macrosoft Connect executable."""
    return os.path.join(app_install_dir(), f"{app_config.EXE_NAME}.exe")


def uninstall_shortcut_path():
    """Path of the generated uninstall shortcut."""
    return os.path.join(app_install_dir(), f"Uninstall {app_config.NAME}.lnk")


def service_binary_path():
    """Command line used when registering the Windows service."""
    return f'"{app_executable_path()}" --service'


def create_service_manager():
    """Build the ServiceManager for the Macrosoft Connect service."""
    return ServiceManager(
        service_name=f"{app_config.NAME}",
        display_name=f"{app_config.NAME} Service",
        binary_path=service_binary_path(),
    )


def query_rustdesk_id(app_path=None):
    """Ask the installed executable for its RustDesk id.

    Returns the stripped id (possibly an empty string).  Any failure is
    propagated to the caller so it can keep its own logging behaviour.
    """
    app_path = app_path or app_executable_path()
    result = subprocess.run(
        [app_path, "--get-id"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip() if result.stdout else ""


def report_rustdesk_id(access, rustdesk_id, log=None, max_attempts=3):
    """Report a RustDesk id to the Macrosoft API, retrying on failure.

    ``log`` is an optional callable used to surface progress messages; the
    returned boolean tells the caller whether the report succeeded.
    """
    if not access:
        return False

    url = f"{app_config.RUSTDESK_REPORT_URL}?access={access}&rustdesk={rustdesk_id}"
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        try:
            response = api.get(
                url,
                headers=app_config.get_cloudflare_headers(),
                retries=0,
            )
            if response.status_code == 200:
                if log:
                    log("ID bolo úspešne odoslané.")
                return True
            if log:
                log(f"Odozva servera: {response.status_code}")
            if attempt < max_attempts:
                time.sleep(1)
        except Exception as e:
            if log:
                log(f"Nepodarilo sa odoslať ID: {e}")

    return False
