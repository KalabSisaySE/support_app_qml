"""Worker that maintains the Macrosoft support websocket connection."""

import json

from PySide6.QtCore import (
    QByteArray,
    QObject,
    QTimer,
    QUrl,
    QUrlQuery,
    Signal,
    Slot,
)
from PySide6.QtNetwork import QAbstractSocket, QNetworkRequest
from PySide6.QtWebSockets import QWebSocket

from support_app.app_config import (
    SUPPORT_WEBSOCKET_URL,
    get_access_code,
    get_cloudflare_headers,
)


class WebSocketWorker(QObject):
    connection = Signal(bool)
    message_received = Signal(str)
    error_occurred = Signal(str)
    log = Signal(str)
    toggleRecording = Signal()
    receivedCourseData = Signal(dict)

    def __init__(self):
        super().__init__()
        self.access = get_access_code()

        # WebSocket setup
        url = QUrl(SUPPORT_WEBSOCKET_URL)
        query = QUrlQuery()
        query.addQueryItem("access_code", self.access)
        url.setQuery(query)

        request = QNetworkRequest(url)

        # 2. Set the Cloudflare service token headers
        # Note: Header names and values must be QByteArray, so we encode them
        for header_name, header_value in get_cloudflare_headers().items():
            request.setRawHeader(
                QByteArray(header_name.encode('utf-8')),
                QByteArray(header_value.encode('utf-8')),
            )
        self.url = url
        self.request = request


        self.websocket = QWebSocket(parent=self)
        self.websocket.connected.connect(self.on_connected)
        self.websocket.disconnected.connect(self.on_disconnected)
        self.websocket.textMessageReceived.connect(self.on_text_message_received)
        self.websocket.errorOccurred.connect(self.on_error)

        # Reconnection settings
        self.reconnect_enabled = True  # Master toggle
        self.initial_reconnect_delay = 1000  # 1 second
        self.max_reconnect_delay = 30000  # 30 seconds cap
        self.current_reconnect_delay = self.initial_reconnect_delay
        self.reconnect_needed = False  # Flag for network-related errors
        self.manual_disconnect = False  # Track user-initiated disconnects

        # Reconnection timer
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self.start_connection)


    @Slot()
    def start_connection(self):
        self.websocket.open(self.request)

    @Slot()
    def disconnect(self):
        # Manual disconnection (disable reconnection)
        self.manual_disconnect = True
        self.reconnect_enabled = False
        self.reconnect_timer.stop()
        self.websocket.close()
        self.log.emit("Manuálne požiadanie o odpojenie WebSocketu.")

    @Slot()
    def on_connected(self):
        self.log.emit("Pripojené k serveru Macrosoft WebSocket.")
        self.current_reconnect_delay = self.initial_reconnect_delay  # Reset delay
        self.reconnect_needed = False  # Clear error flag
        self.connection.emit(True)

    @Slot()
    def on_disconnected(self):
        self.log.emit("Odpojené od servera Macrosoft WebSocket.")
        self.connection.emit(False)

        close_code = self.websocket.closeCode()
        close_reason = self.websocket.closeReason()
        self.log.emit(f"Kód uzavretia: {close_code}, Dôvod: {close_reason}")


    @Slot(QAbstractSocket.SocketError)
    def on_error(self, error_code):
        error_msg = self.websocket.errorString()
        self.log.emit(f"Chyba WebSocketu: {error_msg}")
        self.error_occurred.emit(error_msg)

        # Classify errors: Set reconnect_needed only for network issues
        network_errors = [
            QAbstractSocket.HostNotFoundError,
            QAbstractSocket.NetworkError,
            QAbstractSocket.SocketTimeoutError,
            QAbstractSocket.TemporaryError,
        ]
        self.reconnect_needed = error_code in network_errors

        # Force cleanup if needed
        if self.websocket.state() != QAbstractSocket.UnconnectedState:
            self.websocket.abort()

    @Slot(str)
    def on_text_message_received(self, message):

        try:
            data = json.loads(message)
            self.receivedCourseData.emit(data)
            message_type = data.get("message_type")
            self.lectoure_ws_data = data
            if message_type in ["start_recording", "stop_recording"]:
                self.toggleRecording.emit()
            else:
                msg = json.dumps({
                    "client": "device",
                    "access_code": self.access,
                    "success": False,
                    "message": "Invalid message type, accept only start_recording or stop_recording",
                })

                self.send_message(msg)
                self.message_received.emit(message)
        except Exception as e:
            self.message_received.emit(message)

    def send_message(self, message):
        if self.websocket.state() == QAbstractSocket.ConnectedState:
            self.websocket.sendTextMessage(message)
        else:
            self.error_occurred.emit("Nie je pripojené k serveru WebSocket.")

    @Slot(dict)
    def send_msg_to_server(self, msg):
        """receives message from main thread and sends it to server"""
        message = json.dumps(msg)
        self.send_message(message)
