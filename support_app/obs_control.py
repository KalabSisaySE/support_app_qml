"""OBS install detection, lifecycle and websocket configuration helpers."""

import json
import os
import secrets
import string
import subprocess
import time

import psutil
import win32con
import win32gui

from support_app.logging_setup import get_logger

logger = get_logger(__name__)

OBS_WINDOWS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_WEBSOCKET_CONFIG = ('obs-studio', 'plugin_config', 'obs-websocket', 'config.json')


def is_obs_installed():
    """Check if OBS is installed"""
    return os.path.exists(OBS_WINDOWS_PATH)


def is_obs_running():
    """Check if OBS process is running"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['obs64.exe', 'obs']:
            return True
    return False


def set_obs_exit_confirmation():
    """Set ConfirmOnExit to false in OBS's user.ini (even if OBS overwrites it)."""
    obs_settings_path = os.path.join(os.getenv('APPDATA'), 'obs-studio', 'user.ini')

    # Close OBS to prevent it from overwriting the file
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['obs64.exe', 'obs32.exe', 'obs.exe']:
            proc.kill()

    if os.path.exists(obs_settings_path):

        # Read the file as text (preserving formatting)
        with open(obs_settings_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        # Find and update the ConfirmOnExit line under [General]
        in_general_section = False
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped == '[General]':
                in_general_section = True
            elif in_general_section and line_stripped.startswith('ConfirmOnExit'):
                # Update the line to ConfirmOnExit=false
                lines[i] = 'ConfirmOnExit=false\n'
                break  # Stop after the first occurrence in [General]

        # Write the modified content back to the file
        with open(obs_settings_path, 'w', encoding='utf-8-sig') as f:
            f.writelines(lines)

        logger.info("OBS closed and ConfirmOnExit set to false.")


def start_obs(first_time=False):
    """Start OBS with confirmation dialog disabled."""
    # Ensure OBS does NOT show exit confirmation
    if not first_time:
        set_obs_exit_confirmation()

    # Launch OBS
    obs_install_dir = os.path.dirname(OBS_WINDOWS_PATH)
    subprocess.Popen(
        [OBS_WINDOWS_PATH],
        cwd=obs_install_dir
    )


def close_obs():
    """Gracefully close OBS by sending WM_CLOSE to its windows."""

    def enum_windows_callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if "OBS" in window_title:  # Match OBS windows
                hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(enum_windows_callback, hwnds)

    # Politely ask OBS to close
    for hwnd in hwnds:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

    # Wait for graceful exit (no confirmation dialog now)
    obs_processes = ['obs64.exe', 'obs']
    for _ in range(10):  # Wait up to 10 seconds
        processes = [proc.info['name'] for proc in psutil.process_iter(['name'])
                     if proc.info['name'] in obs_processes]
        if not processes:
            break
        time.sleep(1)
    else:
        # Force terminate if still running
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] in obs_processes:
                proc.terminate()


def setup_obs_config():
    config_path = os.path.join(os.environ['APPDATA'], *OBS_WEBSOCKET_CONFIG)

    chars = string.ascii_letters + string.digits
    generated_password = ''.join(secrets.choice(chars) for _ in range(16))

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        else:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            config_data = {
                "alerts_enabled": True,
                "auth_required": False,
                "first_load": False,
                "server_enabled": True,
                "server_password": generated_password,
                "server_port": 4455
            }
    except Exception as e:
        logger.warning("Could not load OBS websocket config: %s", e)
        config_data = {}

    config_data["server_enabled"] = True
    config_data["auth_required"] = False
    config_data["alerts_enabled"] = True
    config_data["server_password"] = config_data.get("server_password", generated_password)
    config_data["server_port"] = 4455

    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=4)


def check_obs_config():
    """verifies if OBS is configured properly (as needed)"""
    config_path = os.path.join(os.environ['APPDATA'], *OBS_WEBSOCKET_CONFIG)

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)

                alert = config_data["alerts_enabled"]
                auth = not config_data["auth_required"]
                server = config_data["server_enabled"]
                port = config_data["server_port"] == 4455

                return alert and auth and server and port
    except Exception as e:
        logger.debug("Could not verify OBS websocket config: %s", e)
        return
