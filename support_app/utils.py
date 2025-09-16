import ctypes
import psutil
import requests
import socket
import webbrowser
import os
import time
import subprocess
import win32gui
import win32con
import json
import string
import secrets
import re

def get_process_command_lines(process_name):
    try:
        command_lines = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                print(f"\n\t\t\tcmdline: {cmdline}")
                command_lines.append(cmdline)
        print(f"\n\t\t\tcmdline over")
        return command_lines
    except Exception as e:
        return []

def is_app_running():
    """
    Check if a Macrosoft Remote Desktop is running.
    :return: True if the process is running, False otherwise.
    """
    from main import NAME, EXE_NAME
    process_name = f"{EXE_NAME}.exe"

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
        return False

def get_full_name(access):
    import requests
    if access:
        url = f'https://online.macrosoft.sk/rustdesk/username/?access={access}'
        try:
            res = requests.get(url, headers=get_cloudflare_headers())

            json_data = res.json()
            if json_data.get('status') == 'found':
                return json_data.get('full_name', 'Neznáme meno')
            else:
                return 'Neznáme meno'

        except Exception as e:
            return ""
    return ""

def open_website(access):
    if access:
        url = f'https://online.macrosoft.sk/online/?access={access}'
        webbrowser.open(url)
        return True
    else:
        return False

def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_public_ip():
    try:
        return requests.get("https://api64.ipify.org?format=text").text
    except requests.RequestException:
        return


def get_latest_access_code():
    try:
        my_ip = get_public_ip()
        if my_ip:
            url = "https://online.macrosoft.sk/get/lectoure/access/"
            res = requests.post(url, json={"ip_address": my_ip}, headers=get_cloudflare_headers())

            if res.status_code == 200:
                return res.json().get('access_code', "")
        else:
            return ""
    except:
        return ""

def extract_installer_code(input_str):
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
        pass


def check_installation():
    """Check if the application is installed on user's computer."""
    from main import NAME, EXE_NAME
    app_path = fr"C:\Program Files\{NAME}\{EXE_NAME}.exe"
    return os.path.exists(app_path)

def is_obs_installed():
    """Check if OBS is installed"""
    OBS_WINDOWS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"

    if os.path.exists(OBS_WINDOWS_PATH):
        return True

    return False

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

        print("OBS closed and ConfirmOnExit set to false.")

def start_obs(first_time=False):
    """Start OBS with confirmation dialog disabled."""
    # Ensure OBS does NOT show exit confirmation
    if not first_time:
        set_obs_exit_confirmation()

    # Launch OBS
    OBS_WINDOWS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
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
    config_path = os.path.join(
        os.environ['APPDATA'],
        'obs-studio',
        'plugin_config',
        'obs-websocket',
        'config.json'
    )

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
    config_path = os.path.join(
        os.environ['APPDATA'],
        'obs-studio',
        'plugin_config',
        'obs-websocket',
        'config.json'
    )

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
        return


def get_cloudflare_headers():
    return {
        "cf-access-client-id": "e5227eb75bb71fa25a09e6bed7362bb1.access",
        "cf-access-client-secret": "32097cf5a9639d6bd46e818112e0171119be7754a1acd243f703116f93ca9a38",
    }



