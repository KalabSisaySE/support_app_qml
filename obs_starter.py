import os
import subprocess
import time
import psutil
import requests
from obswebsocket import obsws, requests as obs_requests

# Configuration
OBS_WS_HOST = "localhost"
OBS_WS_PORT = 4455
OBS_WS_PASSWORD = "your_password"  # Set in OBS > Tools > WebSocket Server Settings
RTMP_SERVER = "rtmp://your.server/live/stream_key"

# OBS Paths (Windows example)
OBS_WINDOWS_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
OBS_INSTALLER_URL = "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-29.1.3-Full-Installer-x64.exe"


def is_obs_installed():
    """Check if OBS is installed"""
    if os.path.exists(OBS_WINDOWS_PATH):
        return True
    # Add checks for other OSes here
    return False


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


def is_obs_running():
    """Check if OBS process is running"""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['obs64.exe', 'obs']:
            return True
    return False


def start_obs():
    """Start OBS application"""
    subprocess.Popen([OBS_WINDOWS_PATH])


def obs_connect():
    """Connect to OBS WebSocket"""
    ws = obsws(OBS_WS_HOST, OBS_WS_PORT, OBS_WS_PASSWORD)
    ws.connect()
    return ws


def main():
    print(f"\t\tis_obs_installed: {is_obs_installed()}")
    print(f"\t\tis_obs_running: {is_obs_running()}")
    # Check and install OBS
    if not is_obs_installed():
        install_obs()

    # Check and start OBS
    if not is_obs_running():
        start_obs()
        time.sleep(10)  # Wait for OBS to initialize
    #
    # # Connect to WebSocket
    # ws = obs_connect()

    # try:
    #     # Get WebSocket info
    #     version = ws.call(obs_requests.GetVersion())
    #     print(f"OBS Version: {version.getOBSVersion()}, WebSocket Version: {version.getObsWebSocketVersion()}")
    #
    #     # Start recording and streaming
    #     ws.call(obs_requests.StartRecord())
    #     ws.call(obs_requests.StartStream())
    #     print("Recording and streaming started")
    #
    #     # Get recording status
    #     record_status = ws.call(obs_requests.GetRecordStatus())
    #     print(f"Recording status: {record_status.isRecording()}")
    #
    #     # Example: Wait for 10 seconds then stop
    #     time.sleep(10)
    #
    #     # Stop recording and streaming
    #     ws.call(obs_requests.StopRecord())
    #     ws.call(obs_requests.StopStream())
    #     print("Recording and streaming stopped")
    #
    # finally:
    #     ws.disconnect()


if __name__ == "__main__":
    main()