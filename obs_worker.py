from datetime import datetime
import json
import sys
import uuid
import time
from PySide6.QtCore import QObject, Signal, Slot, QThread, QCoreApplication, QUrl
from PySide6.QtWebSockets import QWebSocket

from support_app.utils import is_obs_running, start_obs


class OBSClient(QObject):
    connection = Signal(bool)
    errorOccurred = Signal(str)

    streamStatusChange = Signal(bool)
    streamStatusUpdated = Signal(dict)

    def __init__(self, lectoure_data=None):
        super().__init__()

        self.url = QUrl("ws://localhost:4455")
        self.ws = QWebSocket()
        self.responses = {}
        self.identified = False
        self.lectoure_data = lectoure_data if lectoure_data else {}
        self.file_name = None

        class_id = self.lectoure_data.get("class_id")
        class_type = self.lectoure_data.get("class_type")
        date_info = datetime.now().strftime("%d.%m.%Y.%H.%M.%S")

        if class_id and class_type:
            self.file_name = f"{class_type}_{class_id}_{date_info}"

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
        print("Connected to WebSocket server")

    def on_disconnected(self):
        print("Disconnected from WebSocket server")
        self.connection.emit(False)

    def handle_error(self, error):
        error_msg = self.ws.errorString()
        self.errorOccurred.emit(error_msg)
        print("WebSocket error:", error_msg)

    def on_text_message_received(self, message):
        data = json.loads(message)
        op_code = data.get('op')

        if op_code == 0:  # Hello
            self.handle_hello(data)
        elif op_code == 2:  # Identified
            self.handle_identified(data)
        elif op_code == 7:  # RequestResponse
            self.handle_request_response(data['d'])

    def handle_hello(self, data):
        print("Received Hello message")
        self.send_identify()

    def send_identify(self):
        identify_payload = {
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "authentication": "",
                "eventSubscriptions": 0
            }
        }
        self.send_json(identify_payload)

    def handle_identified(self, data):
        print("Successfully identified with OBS")
        self.identified = True
        self.connection.emit(True)

    def handle_request_response(self, data):
        request_id = data.get('requestId')
        if request_id in self.responses:
            self.responses[request_id] = data
            # Emit response received signal or handle callback here

    def send_json(self, data):
        self.ws.sendTextMessage(json.dumps(data))

    def set_custom_rtmp(self):
        # rtmp_url_generator = RtmpUrlGenerator(self.file_name, self.lectoure_data)
        # rtmp_url = rtmp_url_generator.get_rtmp_url()
        # if rtmp_url:
        #     server_url, stream_key = rtmp_url.split("/")
        #     request_id = str(uuid.uuid4())
        #     payload = {
        #         "op": 6,
        #         "d": {
        #             "requestType": "SetStreamServiceSettings",
        #             "requestId": request_id,
        #             "requestData": {
        #                 "streamServiceType": "rtmp_custom",
        #                 "streamServiceSettings": {
        #                     "server": server_url,
        #                     "key": stream_key
        #                 }
        #             }
        #         }
        #     }
        #     self.send_json(payload)
        #     self.responses[request_id] = None

        server_url = "rtmp://live.restream.io/live"
        stream_key = "re_9442228_eventbc50b5ebd0644931aa1c7fcfd47961f8"

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

    @Slot()
    def start_stream(self):
        self.set_custom_rtmp()
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

    @Slot()
    def stop_stream(self):
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
        self.responses[request_id] = None

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


class StreamController(QObject):
    def __init__(self):
        super().__init__()
        self.obs_websocket_worker = None
        self.obs_websocket_thread = QThread()

    def setup_client(self, url):
        self.obs_websocket_worker = OBSClient()
        self.obs_websocket_worker.moveToThread(self.obs_websocket_thread)

        # Connect signals
        self.obs_websocket_thread.started.connect(self.obs_websocket_worker.connect_to_host)
        self.obs_websocket_worker.connection.connect(self.on_obs_websocket_status_change)
        self.obs_websocket_worker.streamStatusChange.connect(self.on_obs_stream_status_change)
        self.obs_websocket_worker.errorOccurred.connect(self.obs_websocket_on_error)
        self.obs_websocket_thread.start()

    @Slot(bool)
    def on_obs_websocket_status_change(self, status):
        self.add_log(f"OBS on_obs_websocket_status_change: {status}")
        if status:
            self.obs_websocket_status = "enabled"
        else:
            self.obs_websocket_status = "disabled"

    @Slot(bool)
    def on_obs_stream_status_change(self, status):
        self.add_log(f"OBS on_obs_stream_status_change: {status}")
        if status:
            self.recording_status = "enabled"
        else:
            self.recording_status = "disabled"

    @Slot(str)
    def websocket_on_message_received(self, message):
        self.add_log(f"OBS Websocket received: {message}")
        try:
            data = json.loads(message)

            message_type = data.get("message_type")
            self.lectoure_ws_data = data
            if message_type in ["start_recording", "stop_recording"]:
                pass
                # self.toggle_obs_recording(action=message_type)
            else:
                msg = json.dumps(
                    {
                        "client": "device",
                        "access_code": self._access_code,
                        "success": False,
                        "message": "Invalid message type, accept only start_recording or stop_recording",
                    }
                )
                self.send_message_to_server(msg)
        except json.JSONDecodeError:
            pass

    @Slot(str)
    def obs_websocket_on_error(self, message):
        self.add_log(message)

    def on_error(self, error_msg):
        print("Error:", error_msg)

    def shutdown(self):
        if self.client:
            self.client.disconnect_ws()
        self.thread.quit()
        self.thread.wait()


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    controller = StreamController()
    controller.setup_client("ws://localhost:4455")

    # Example usage pattern (would need proper signal/slot connections)
    # controller.client.set_custom_rtmp("rtmp://example.com/live", "stream_key")
    # controller.client.start_stream()

    sys.exit(app.exec_())