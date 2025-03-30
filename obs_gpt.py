import os
import subprocess
import time
import requests
import psutil
from obswebsocket import obsws, requests as obs_requests

# ----- Configuration -----
# Path to OBS executable (default Windows installation)
OBS_INSTALL_PATH = r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"
# URL for the OBS installer (this example URL might need updating)
OBS_INSTALLER_URL = "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-27.2.4-Full-Installer-x64.exe"
OBS_INSTALLER_PATH = "OBS_Installer.exe"
# obs-websocket connection settings
HOST = "localhost"
PORT = 4444
PASSWORD = "your_password_here"  # Set this to match your OBS obs-websocket settings
# RTMP server (assumes OBS has been pre-configured with streaming settings)
RTMP_URL = "rtmp://your.rtmp.server/app/streamkey"

# ----- Utility Functions -----
def is_obs_installed():
    """Check if OBS is installed by verifying the executable exists."""
    return os.path.exists(OBS_INSTALL_PATH)

def download_and_install_obs():
    """Download the OBS installer and run it.
       (This is a simplified example; real-world use may need error handling and privilege elevation.)"""
    print("OBS not installed. Downloading installer...")
    r = requests.get(OBS_INSTALLER_URL, stream=True)
    with open(OBS_INSTALLER_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete. Launching installer...")
    subprocess.run([OBS_INSTALLER_PATH, "/S"], check=True)
    print("OBS installation initiated (you may need to follow installer prompts).")

def is_obs_running():
    """Detect if OBS is running by checking for the obs64.exe process."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "obs64.exe" in proc.info['name'].lower():
            return True
    return False

def launch_obs():
    """Launch OBS if it’s not already running."""
    if not is_obs_running():
        print("Launching OBS...")
        subprocess.Popen([OBS_INSTALL_PATH])
        time.sleep(5)  # Wait a few seconds for OBS to launch

# ----- obs-websocket Functions -----
def connect_obs_websocket(host=HOST, port=PORT, password=PASSWORD):
    """Connect to the obs-websocket server."""
    try:
        ws = obsws(host, port, password)
        ws.connect()
        print("Connected to obs-websocket!")
        return ws
    except Exception as e:
        print("Failed to connect to obs-websocket:", e)
        return None

def get_websocket_info(ws):
    """Retrieve websocket info (e.g., authentication requirements)."""
    auth_info = ws.call(obs_requests.GetAuthRequired())
    print("Websocket Auth Required:", auth_info.getAuthRequired())
    print("Challenge:", auth_info.getChallenge())
    print("Salt:", auth_info.getSalt())

def enable_websocket(ws):
    """
    There is no API call to enable obs-websocket if it is disabled.
    You must ensure that obs-websocket is enabled via OBS settings.
    This function serves as a placeholder for any configuration steps.
    """
    print("Please ensure obs-websocket is enabled in OBS settings.")

def start_record_and_stream(ws):
    """Initiate screen recording and start streaming."""
    print("Starting recording and streaming...")
    # These commands assume that your OBS profile is pre-configured with proper streaming settings.
    ws.call(obs_requests.StartRecording())
    ws.call(obs_requests.StartStreaming())

def get_recording_status(ws):
    """Retrieve and print the recording status."""
    status = ws.call(obs_requests.GetRecordStatus())
    print("Is Recording:", status.getIsRecording())
    return status.getIsRecording()

def stop_recording(ws):
    """Stop recording gracefully."""
    print("Stopping recording...")
    ws.call(obs_requests.StopRecording())

# ----- Main Script -----
def main():
    # 1. Check if OBS is installed; if not, download and install it.
    if not is_obs_installed():
        download_and_install_obs()

    # 2. Launch OBS if it isn’t already running.
    launch_obs()

    # 3. Connect to obs-websocket.
    ws = connect_obs_websocket()
    if ws is None:
        return

    # 4. Get websocket info.
    get_websocket_info(ws)

    # 5. Ensure websockets are enabled (manual/config step).
    enable_websocket(ws)

    # 6. Start recording and streaming.
    start_record_and_stream(ws)

    # Let recording/streaming run for a short while.
    time.sleep(10)

    # 7. Get current recording status.
    get_recording_status(ws)

    # 8. Stop recording gracefully.
    stop_recording(ws)

    # Disconnect from the websocket.
    ws.disconnect()

if __name__ == "__main__":
    main()
