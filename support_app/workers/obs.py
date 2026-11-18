"""Workers that manage the OBS installation, launch and websocket client."""

import datetime
import json
import os
import subprocess
import time
import urllib.request
import uuid

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWebSockets import QWebSocket

from support_app.app_config import (
    FALLBACK_DOWNLOAD_DIR,
    get_access_code,
    get_latest_obs_download_url,
)
from support_app.macrosoft_connect import create_service_manager
from support_app.rtmp_url_manager import RtmpUrlGenerator
from support_app.utils import (
    is_obs_installed,
    is_obs_running,
    setup_obs_config,
    start_obs,
)


class OpenOBSWorker(QObject):
    """manages opening/closing a browser"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.access = get_access_code()
        self.process_name = "open_obs"

    @Slot()
    def open_obs_app(self):
        """Open the default page in user's default browser."""
        try:
            self.log.emit("Otvorenie OBS...")
            if not is_obs_running():
                start_obs()
                self.log.emit("OBS bol spustený...")
            else:
                self.log.emit("OBS je už spustený.")
        except Exception:
            self.log.emit("Nepodarilo sa spustiť OBS.")

        self.finished.emit()


class OBSInstallationWorker(QObject):
    """manages macrosoft rustdesk installation and uninstallation"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.result_data = {
            "app_installed": False,
            "app_service_on": False,
            "rust_id": "Nenájdené"
        }
        self.access = get_access_code()
        self.manager = create_service_manager()
        self.process_name = "obs_install"

    @Slot()
    def install_app(self):
        """installs and rust Macrosoft RustDesk"""
        self.log.emit("Začínam proces inštalácie OBS...")

        download_url = get_latest_obs_download_url()
        if not download_url:
            self.log.emit("Inštalácia OBS bola zrušená, pretože sa nepodarilo nájsť odkaz na stiahnutie.")
            self.finished.emit()
            return

        temp_dir = os.environ.get("TEMP", FALLBACK_DOWNLOAD_DIR)
        os.makedirs(temp_dir, exist_ok=True)
        installer_path = os.path.join(temp_dir, "obs_installer.exe")

        try:
            with urllib.request.urlopen(download_url) as response:
                total_size = int(response.getheader("Content-Length", "0"))
                block_size = 8192
                with open(installer_path, "wb") as file:
                    downloaded = 0
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        file.write(buffer)
                        downloaded += len(buffer)
                        if total_size > 0:
                            percent = downloaded * 100 / total_size
                            self.progress_changed.emit(percent, self.process_name)
        except Exception as e:
            self.log.emit(f"Chyba pri sťahovaní súboru: {e}")
            self.finished.emit()
            return

        try:
            self.log.emit("Inštaluje sa OBS Studio...")
            # Run the installer silently
            subprocess.run([installer_path, "/S"], check=True)
            self.log.emit("OBS Studio bolo úspešne nainštalované.")
            time.sleep(5)

            setup_obs_config()
            start_obs(first_time=True)

        except subprocess.CalledProcessError as e:
            self.log.emit(f"Inštalátor OBS zlyhal s chybou: {e}")
        except Exception as e:
            self.log.emit(f"Chyba počas inštalácie: {e}")

        self.finished.emit()


class OBSClientWorker(QObject):

    connection = Signal(bool)
    errorOccurred = Signal(str)
    log = Signal(str)
    streamStatusChange = Signal(bool)
    streamStatusUpdated = Signal(dict)
    streamStateInTransition = Signal()
    rtmpUrlFetched = Signal(str)
    complete = Signal()

    def __init__(self, lectoure_data=None):
        super().__init__()

        self.url = QUrl("ws://localhost:4455")
        self.ws = QWebSocket(parent=self)
        self.responses = {}
        self.identified = False
        self.lectoure_data = lectoure_data if lectoure_data else {}
        self.file_name = None
        self.rtmp_url = ""
        self.rtmp_url_generator = None


        # OBS state
        self.streaming_started = "OBS_WEBSOCKET_OUTPUT_STARTED"
        self.streaming_starting = "OBS_WEBSOCKET_OUTPUT_STARTING"
        self.streaming_stopped = "OBS_WEBSOCKET_OUTPUT_STOPPED"
        self.streaming_stopping = "OBS_WEBSOCKET_OUTPUT_STOPPING"

        # class details
        self.class_id = self.lectoure_data.get("class_id")
        self.class_type = self.lectoure_data.get("class_type")
        self.course_name = self.lectoure_data.get("course_name")
        self.date_info = datetime.datetime.now().strftime("%d.%m.%Y.%H.%M.%S")

        self.is_start_stream_called_on_init = False
        self.is_stop_stream_called_on_init = False
        self.is_start_stream_called = False
        self.is_set_stream_response_received = False

        if self.class_id and self.class_type:
            self.file_name = f"{self.class_type}_{self.class_id}_{self.date_info}"

        # Connect websocket signals
        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_text_message_received)
        self.ws.error.connect(self.handle_error)

    def connect_to_host(self):
        if not is_obs_running():
            start_obs()
            time.sleep(2)

        self.ws.open(self.url)

    def on_connected(self):
        self.log.emit("Pripojené k serveru OBS WebSocket.")

    def on_disconnected(self):
        self.connection.emit(False)

    def handle_error(self, error):
        error_msg = self.ws.errorString()
        self.errorOccurred.emit(error_msg)

    def on_text_message_received(self, message):
        data = json.loads(message)
        op_code = data.get('op')

        if op_code == 0:
            self.handle_hello(data)
        elif op_code == 2:
            self.handle_identified(data)
        elif op_code == 5:
            event_type = data['d'].get('eventType', "")
            event_data = data['d'].get('eventData', {})
            if event_type == "StreamStateChanged":
                output_state = event_data.get("outputState")
                if output_state == self.streaming_started:
                    self.streamStatusChange.emit(True)
                elif output_state == self.streaming_stopped:
                    self.streamStatusChange.emit(False)
                elif output_state == self.streaming_starting or output_state == self.streaming_stopping:
                    self.streamStateInTransition.emit()
        elif op_code == 7:  # RequestResponse
            if data['d'].get("requestType") == "SetStreamServiceSettings":
                if data['d'].get("requestStatus", {}).get("result"):
                    if self.is_start_stream_called:
                        self.initiate_stream()

            self.handle_request_response(data['d'])

    def handle_hello(self, data):
        self.send_identify()

    def send_identify(self):
        identify_payload = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "authentication": "",
                "eventSubscriptions": 82
            }
        }
        self.send_json(identify_payload)

    def handle_identified(self, data):
        self.identified = True
        self.connection.emit(True)

        # later calls
        if self.is_start_stream_called_on_init:
            self.start_stream()
        elif self.is_stop_stream_called_on_init:
            self.stop_stream()

    def handle_request_response(self, data):
        request_id = data.get('requestId')
        if request_id in self.responses:
            self.responses[request_id] = data
            # Emit response received signal or handle callback here

    def send_json(self, data):
        self.ws.sendTextMessage(json.dumps(data))

    def set_custom_rtmp(self):
        self.rtmp_url_generator = RtmpUrlGenerator(self.file_name, self.lectoure_data)
        rtmp_url = self.rtmp_url_generator.get_rtmp_url()
        self.rtmp_url = rtmp_url
        # rtmp_url = ["rtmp://live.restream.io/live", "re_9442228_event075b2b509c5d4724860e1c04b3edcd85"]
        if rtmp_url:
            server_url = rtmp_url[0]
            stream_key = rtmp_url[1]

            self.log.emit(f"Streamovacia adresa (URL): {server_url}/{stream_key} Vytvorené. .... ")

            trimmed_server_url = server_url[:25] + "..." if len(server_url) > 25 else server_url

            self.rtmpUrlFetched.emit(trimmed_server_url)

            request_id = str(uuid.uuid4())
            payload = {
                "op": 6,
                "d": {
                    "requestType": "SetStreamServiceSettings",
                    "requestId": request_id,
                    "requestData": {
                        "streamServiceType": "rtmp_custom",
                        "streamServiceSettings": {
                            "server": server_url,
                            "key": stream_key
                        }
                    }
                }
            }
            self.send_json(payload)
            self.responses[request_id] = None
            return True

    def initiate_stream(self):
        """starts stream only after rtmp is set"""
        request_id = str(uuid.uuid4())
        payload = {
            "op": 6,
            "d": {
                "requestType": "StartStream",
                "requestId": request_id,
                "requestData": {}
            }
        }
        self.send_json(payload)
        self.responses[request_id] = None
        self.is_start_stream_called = False

    @Slot()
    def start_stream(self):
        if not self.identified:
            self.is_start_stream_called_on_init = True
            return

        self.log.emit("OBSClient spúšťa stream.")
        if is_obs_installed():
            self.is_start_stream_called = True
            self.set_custom_rtmp()
        else:
            self.log.emit("Nepodarilo sa spustiť stream, OBS nie je nainštalovaný.")

        self.complete.emit()

    @Slot()
    def stop_stream(self):
        if not self.identified:
            self.is_stop_stream_called_on_init = True
            return

        request_id = str(uuid.uuid4())
        payload = {
            "op": 6,
            "d": {
                "requestType": "StopStream",
                "requestId": request_id,
                "requestData": {}
            }
        }
        self.rtmp_url = ""
        self.rtmp_url_generator.upload_recording_to_vimeo()

        self.send_json(payload)
        self.responses[request_id] = None

        self.complete.emit()

    @Slot()
    def get_stream_status(self):
        request_id = str(uuid.uuid4())
        payload = {
            "op": 6,
            "d": {
                "requestType": "GetStreamStatus",
                "requestId": request_id,
                "requestData": {}
            }
        }
        self.send_json(payload)
        self.responses[request_id] = None

    def disconnect_ws(self):
        self.ws.close()

    @Slot()
    def force_stop_stream_on_exit(self):
        """
        Sends a 'StopStream' request to OBS without any other side effects.
        This is designed to be called during application shutdown.
        """
        if not self.identified:
            # Can't send the command if not connected to OBS
            return

        self.log.emit("Aplikácia sa zatvára, posiela sa príkaz na zastavenie streamu do OBS.")
        request_id = str(uuid.uuid4())
        payload = {
            "op": 6,
            "d": {
                "requestType": "StopStream",
                "requestId": request_id,
                "requestData": {}
            }
        }
        self.send_json(payload)
