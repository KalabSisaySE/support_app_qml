import os
import json
import secrets
import requests
import string
import subprocess
import time
import psutil
from obswebsocket import obsws, requests as obs_requests

# Configuration
OBS_WS_HOST = "localhost"
OBS_WINDOWS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_INSTALLER_URL = "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-29.1.3-Full-Installer-x64.exe"


def get_obs_websocket_config_path():
    return os.path.join(
        os.environ['APPDATA'],
        'obs-studio',
        'plugin_config',
        'obs-websocket',
        'config.json'
    )


def generate_password(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def load_or_create_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    return {
        "alerts_enabled": True,
        "auth_required": True,
        "first_load": False,
        "server_enabled": True,
        "server_password": generate_password(),
        "server_port": 4455
    }


def update_config(config):
    config["server_enabled"] = True
    config["auth_required"] = True
    config["server_password"] = config.get("server_password", generate_password())
    config["server_port"] = config.get("server_port", 4455)
    return config


def save_config(config, config_path):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


def is_obs_installed():
    return os.path.exists(OBS_WINDOWS_PATH)


def install_obs():
    """Download and install OBS (Windows example)"""
    print("Downloading OBS...")
    installer_path = os.path.join(os.environ["TEMP"], "obs_installer.exe")

    with requests.get(OBS_INSTALLER_URL, stream=True) as r:
        r.raise_for_status()
        with open(installer_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print("Installing OBS...")
    subprocess.run([installer_path, '/S'], check=True)

def terminate_obs():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['obs64.exe', 'obs']:
            proc.kill()
    time.sleep(2)  # Wait for process termination


def start_obs():
    """Start OBS with correct working directory"""
    obs_install_dir = os.path.dirname(OBS_WINDOWS_PATH)
    subprocess.Popen(
        [OBS_WINDOWS_PATH],
        cwd=obs_install_dir  # Set working directory to OBS install location
    )


def main():
    # Install OBS if needed
    if not is_obs_installed():
        install_obs()

    # Terminate OBS if running
    terminate_obs()

    # Configure WebSocket settings
    config_path = get_obs_websocket_config_path()
    print(f"\n\n\nconfig_path: {config_path}\n\n")

    config = load_or_create_config(config_path)
    print(f"\n\n\nfirst config: {config}\n\n")

    config = update_config(config)
    print(f"\n\n\nupdate config: {config}\n\n")

    save_config(config, config_path)

    # Start OBS with new settings
    print(f"Start OBS application")

    start_obs()
    time.sleep(30)  # Wait for OBS initialization

    # # Connect using configured credentials
    ws = obsws(
        OBS_WS_HOST,
        config["server_port"],
        config["server_password"]
    )

    try:
        ws.connect()
        print(f"Connected to OBS WebSocket on port {config['server_port']}")

        # Example usage
        # ws.call(obs_requests.StartRecord())
        print("Recording started")

        time.sleep(2)

        # ... rest of your streaming/recording logic

    finally:
        ws.disconnect()


if __name__ == "__main__":
    main()