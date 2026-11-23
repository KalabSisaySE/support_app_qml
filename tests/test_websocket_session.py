import support_app.websocket_session as websocket_session
from support_app.websocket_session import SupportWebSocketSession


class FakeSignal:
    def __init__(self):
        self.connected = []

    def connect(self, slot):
        self.connected.append(slot)


class FakeThread:
    def __init__(self, running=True):
        self.started = FakeSignal()
        self.running = running
        self.start_calls = 0
        self.quit_calls = 0
        self.wait_calls = 0

    def isRunning(self):
        return self.running

    def quit(self):
        self.quit_calls += 1
        self.running = False

    def wait(self):
        self.wait_calls += 1

    def start(self):
        self.start_calls += 1


class FakeWorker:
    def __init__(self):
        self.connection = FakeSignal()
        self.message_received = FakeSignal()
        self.error_occurred = FakeSignal()
        self.log = FakeSignal()
        self.toggleRecording = FakeSignal()
        self.receivedCourseData = FakeSignal()
        self.thread = None

    def moveToThread(self, thread):
        self.thread = thread

    def start_connection(self):
        pass

    def send_msg_to_server(self, message):
        pass


class FakeHost:
    def __init__(self):
        self.app_websocket_thread = None
        self.app_websocket_worker = None
        self.sendMessage = FakeSignal()
        self.lectoure_ws_data = None
        self.course_name = "Neznáme"
        self.app_websocket_status = "disabled"
        self.recording_toggled = 0

    def add_log(self, message):
        pass

    def recording_toggle(self):
        self.recording_toggled += 1

    def websocket_on_change_status(self, status):
        pass

    def websocket_on_message_received(self, message):
        pass

    def websocket_on_error(self, message):
        pass

    def websocket_on_toggle_recording(self):
        pass

    def websocket_on_received_course_data(self, course_data):
        pass


def test_setup_creates_worker_and_connects_signals(monkeypatch):
    host = FakeHost()
    worker = FakeWorker()
    monkeypatch.setattr(websocket_session, "WebSocketWorker", lambda: worker)
    monkeypatch.setattr(websocket_session, "QThread", FakeThread)

    SupportWebSocketSession(host).setup("CODE")

    thread = host.app_websocket_thread
    assert host.app_websocket_worker is worker
    assert worker.thread is thread
    assert thread.start_calls == 1
    assert worker.start_connection in thread.started.connected
    assert worker.connection.connected == [host.websocket_on_change_status]
    assert worker.message_received.connected == [host.websocket_on_message_received]
    assert worker.log.connected == [host.add_log]
    assert worker.toggleRecording.connected == [host.websocket_on_toggle_recording]
    assert worker.receivedCourseData.connected == [host.websocket_on_received_course_data]
    assert host.sendMessage.connected == [worker.send_msg_to_server]


def test_setup_stops_previous_thread(monkeypatch):
    host = FakeHost()
    previous = FakeThread(running=True)
    host.app_websocket_thread = previous
    monkeypatch.setattr(websocket_session, "WebSocketWorker", FakeWorker)
    monkeypatch.setattr(websocket_session, "QThread", FakeThread)

    SupportWebSocketSession(host).setup("CODE")

    assert previous.quit_calls == 1
    assert previous.wait_calls == 1


def test_empty_code_stops_without_creating_worker(monkeypatch):
    host = FakeHost()
    previous = FakeThread(running=True)
    host.app_websocket_thread = previous

    def no_worker():
        raise AssertionError("worker must not be created")

    monkeypatch.setattr(websocket_session, "WebSocketWorker", no_worker)

    SupportWebSocketSession(host).setup("")

    assert previous.quit_calls == 1
    assert host.app_websocket_thread is previous


def test_status_updates():
    host = FakeHost()
    session = SupportWebSocketSession(host)

    session.on_change_status(True)
    assert host.app_websocket_status == "enabled"
    session.on_change_status(False)
    assert host.app_websocket_status == "disabled"


def test_message_received_stores_initial_course_data():
    host = FakeHost()
    session = SupportWebSocketSession(host)

    session.on_message_received('{"message_type": "start", "class_id": 1}')
    session.on_message_received('{"message_type": "stop", "class_id": 2}')

    assert host.lectoure_ws_data == {"message_type": "start", "class_id": 1}


def test_message_received_ignores_invalid_json():
    host = FakeHost()
    session = SupportWebSocketSession(host)

    session.on_message_received("not json")

    assert host.lectoure_ws_data is None


def test_received_course_data_truncates_name():
    host = FakeHost()
    session = SupportWebSocketSession(host)

    session.on_received_course_data({"course_name": "x" * 40})

    assert host.lectoure_ws_data == {"course_name": "x" * 40}
    assert host.course_name == "x" * 25 + "..."


def test_received_course_data_keeps_fallback_name():
    host = FakeHost()
    session = SupportWebSocketSession(host)

    session.on_received_course_data({})

    assert host.course_name == "Neznáme"


def test_toggle_recording_delegates_to_host():
    host = FakeHost()

    SupportWebSocketSession(host).on_toggle_recording()

    assert host.recording_toggled == 1
