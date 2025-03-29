from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import QThread


class WebSocketWorker(QObject):
    connected = Signal()
    message_received = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = QUrl(url)
        self.websocket = QWebSocket()

        # Connect signals
        self.websocket.connected.connect(self.on_connected)
        self.websocket.textMessageReceived.connect(self.on_text_received)

    @Slot()
    def start_connection(self):
        self.websocket.open(self.url)

    @Slot()
    def on_connected(self):
        self.connected.emit()

    @Slot(str)
    def on_text_received(self, message):
        self.message_received.emit(message)

    @Slot()
    def close_connection(self):
        self.websocket.close()



def setup_websocket_thread(url):
    # Create thread and worker
    thread = QThread()
    worker = WebSocketWorker(url)
    worker.moveToThread(thread)

    # Connect thread start to worker initialization
    thread.started.connect(worker.start_connection)

    # Cleanup on thread finish
    thread.finished.connect(thread.deleteLater)
    worker.connected.connect(lambda: print("Connected!"))
    worker.message_received.connect(lambda msg: print(f"Received: {msg}"))

    return thread, worker


from PySide6.QtWidgets import QApplication

app = QApplication([])

# Set up the thread
thread, worker = setup_websocket_thread("wss://echo.websocket.org")
thread.start()


print(f"app.thread().isMainThread(): {app.thread().isMainThread()}")
print(f"app.thread().isCurrentThread(): {app.thread().isCurrentThread()}")


print(f"thread.isCurrentThread(): {thread.isCurrentThread()}")
print(f"thread.isMainThread(): {thread.isMainThread()}")


# Example: Send a message later (use signals to interact across threads)
worker.connected.connect(
    lambda: worker.websocket.sendTextMessage("Hello from thread!")
)

# Execute the application
app.exec()





# Cleanup
worker.close_connection()
thread.quit()
thread.wait()