import sys
from PySide6.QtCore import QObject, Slot, Signal, Property, QUrl, QThread
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtNetwork import QNetworkRequest
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication


class WebSocketHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._websocket = None
        self.websocket
        self._is_connected = False
        self._setup_connections()
        self._websocket_thread = None

    # Signals
    messageReceived = Signal(str)
    connectionChanged = Signal(bool)
    errorOccurred = Signal(str)

    def _setup_connections(self):
        self._websocket.connected.connect(self._on_connected)
        self._websocket.disconnected.connect(self._on_disconnected)
        self._websocket.textMessageReceived.connect(self.messageReceived)
        self._websocket.error.connect(self._on_error)

    # Property for QML binding
    @Property(bool, notify=connectionChanged)
    def isConnected(self):
        return self._is_connected

    @Slot()
    def toggleConnection(self):

        if self._is_connected:
            self._websocket.close()
            if self._websocket_thread and self._websocket_thread.isRunning():
                self._websocket_thread.quit()
                self._websocket_thread.wait()
                self._websocket_thread = None
        else:
            request = QNetworkRequest(QUrl("wss://echo.websocket.org"))
            self._websocket = QWebSocket(QUrl("wss://echo.websocket.org"))

            self._websocket_thread = QThread()
            self._websocket_thread.moveToThread(self._websocket)
            self._websocket_thread.started.connect(self._websocket.open)

            self._websocket.open(request)

    @Slot(str)
    def sendMessage(self, message):
        if self._is_connected and message:
            self._websocket.sendTextMessage(message)
            self.messageReceived.emit(f"Sent: {message}")

    def _on_connected(self):
        self._is_connected = True
        self.connectionChanged.emit(True)
        self.messageReceived.emit("Connected!")

    def _on_disconnected(self):
        self._is_connected = False
        self.connectionChanged.emit(False)
        self.messageReceived.emit("Disconnected!")

    def _on_error(self, error):
        error_msg = f"Error: {self._websocket.errorString()}"
        self.errorOccurred.emit(error_msg)
        self.messageReceived.emit(error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and expose WebSocket handler to QML
    handler = WebSocketHandler()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("websocketHandler", handler)
    engine.load("main_websocket.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())


#
# import sys
# from PySide6.QtCore import QThread, QCoreApplication
# from PySide6.QtWebSockets import QWebSocket
#
# app = QCoreApplication(sys.argv)
#
# # Create QWebSocket in the main thread
# websocket = QWebSocket()
#
# websocket_thread = websocket.thread()
# app_thread = app.thread()
#
# print(f"websocket thread current: {websocket_thread.isCurrentThread()}")
# print(f"app thread current: {app_thread.isCurrentThread()}")
#
# print(f"websocket thread main: {websocket_thread.isMainThread()}")
# print(f"app thread main: {app_thread.isMainThread()}")
#
# print(f"websocket_thread: {(websocket_thread)}")
# print(f"app_thread: {(app_thread)}")
#
# # Check if it's in the main thread
# print("Is websocket in main thread initially?", websocket.thread() == app.thread())  # Output: True