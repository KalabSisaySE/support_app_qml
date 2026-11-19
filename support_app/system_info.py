"""Windows process, service, network and installation checks."""

import ctypes
import os
import socket

import psutil
import requests

from support_app import api, app_config
from support_app.logging_setup import get_logger

logger = get_logger(__name__)


def get_process_command_lines(process_name):
    try:
        command_lines = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                logger.debug("cmdline: %s", cmdline)
                command_lines.append(cmdline)
        logger.debug("cmdline over")
        return command_lines
    except Exception as e:
        logger.debug("Could not read command lines for %s: %s", process_name, e)
        return []


def is_app_running():
    """
    Check if a Macrosoft Remote Desktop is running.
    :return: True if the process is running, False otherwise.
    """
    process_name = f"{app_config.EXE_NAME}.exe"

    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and process_name.lower() == proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def is_service_running(service_name):
    try:
        service = psutil.win_service_get(service_name)
        return service.status() == 'running'
    except psutil.NoSuchProcess:
        return False
    except Exception as e:
        logger.debug("Could not query service %s: %s", service_name, e)
        return False


def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.debug("Could not determine admin state: %s", e)
        return False


def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def get_public_ip():
    try:
        return api.get("https://api64.ipify.org?format=text").text
    except requests.RequestException as e:
        logger.debug("Could not determine public IP: %s", e)
        return


def check_installation():
    """Check if the application is installed on user's computer."""
    from support_app.macrosoft_connect import app_executable_path
    return os.path.exists(app_executable_path())
