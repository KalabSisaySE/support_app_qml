import sys
from PySide6.QtCore import QObject, QThread, Signal, Slot, QUrl
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import QApplication

class WebSocketWorker(QObject):
    connected = Signal()
    message_received = Signal(str)
    send_message = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.websocket = QWebSocket()  # No parent!

        # Connect internal signals
        self.websocket.connected.connect(self.on_connected)
        self.websocket.textMessageReceived.connect(self.on_text_received)
        self.send_message.connect(self.websocket.sendTextMessage)

    @Slot()
    def start_connection(self):
        print(f"Opening socket in thread: {QThread.currentThread()}")
        self.websocket.open(self.url)

    @Slot()
    def on_connected(self):
        print("Connected!")
        self.connected.emit()

    @Slot(str)
    def on_text_received(self, message):
        self.message_received.emit(message)

    @Slot()
    def close_connection(self):
        self.websocket.close()

def main():
    app = QApplication(sys.argv)
    url = QUrl("wss://echo.websocket.org")

    # Setup thread and worker
    thread = QThread()
    worker = WebSocketWorker(url)
    worker.moveToThread(thread)

    # Start thread and connection
    thread.started.connect(worker.start_connection)
    thread.start()

    # Send a message after connection
    worker.connected.connect(
        lambda: worker.send_message.emit("Hello from thread!")
    )

    # Handle received messages
    worker.message_received.connect(
        lambda msg: print(f"Received: {msg}")
    )

    # Graceful shutdown
    app.aboutToQuit.connect(worker.close_connection)
    app.aboutToQuit.connect(thread.quit)
    app.aboutToQuit.connect(thread.wait)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()