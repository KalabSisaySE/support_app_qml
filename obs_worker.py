import sys
import json
import uuid
from PySide6.QtCore import QObject, Signal, Slot, QThread, QCoreApplication
from PySide6.QtWebSockets import QWebSocket


class OBSClient(QObject):
    connected = Signal()
    disconnected = Signal()
    errorOccurred = Signal(str)
    streamStarted = Signal()
    streamStopped = Signal()
    streamStatusUpdated = Signal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.ws = QWebSocket()
        self.responses = {}
        self.identified = False

        # Connect websocket signals
        self.ws.connected.connect(self.on_connected)
        self.ws.disconnected.connect(self.on_disconnected)
        self.ws.textMessageReceived.connect(self.on_text_message_received)
        self.ws.error.connect(self.handle_error)

    def connect_to_host(self):
        self.ws.open(self.url)

    def on_connected(self):
        print("Connected to WebSocket server")

    def on_disconnected(self):
        print("Disconnected from WebSocket server")
        self.disconnected.emit()

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
        self.connected.emit()

    def handle_request_response(self, data):
        request_id = data.get('requestId')
        if request_id in self.responses:
            self.responses[request_id] = data
            # Emit response received signal or handle callback here

    def send_json(self, data):
        self.ws.sendTextMessage(json.dumps(data))

    @Slot(str, str)
    def set_custom_rtmp(self, server_url, stream_key):
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

    @Slot()
    def start_stream(self):
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
        self.client = None
        self.thread = QThread()

    def setup_client(self, url):
        self.client = OBSClient(url)
        self.client.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.client.connect_to_host)
        self.client.connected.connect(self.on_client_connected)
        self.client.errorOccurred.connect(self.on_error)

        self.thread.start()

    def on_client_connected(self):
        print("Client fully connected and identified")

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