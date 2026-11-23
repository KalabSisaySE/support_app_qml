"""Lifecycle and message handling for the Macrosoft support WebSocket."""

from __future__ import annotations

import json
from typing import Any, Protocol

from PySide6.QtCore import QThread

from support_app.logging_setup import get_logger
from support_app.status import Status
from support_app.workers import WebSocketWorker

logger = get_logger(__name__)

DEFAULT_COURSE_NAME = "course_name"


class WebSocketSessionHost(Protocol):
    """Backend surface required by the support websocket session."""

    app_websocket_thread: Any
    app_websocket_worker: Any
    sendMessage: Any
    lectoure_ws_data: Any
    course_name: str
    app_websocket_status: str

    def add_log(self, message: str) -> None: ...

    def recording_toggle(self) -> None: ...

    def websocket_on_change_status(self, status: bool) -> None: ...

    def websocket_on_message_received(self, message: str) -> None: ...

    def websocket_on_error(self, message: str) -> None: ...

    def websocket_on_toggle_recording(self) -> None: ...

    def websocket_on_received_course_data(self, course_data: dict) -> None: ...


class SupportWebSocketSession:
    """Owns the support websocket worker and its QML-facing updates."""

    def __init__(self, host: WebSocketSessionHost) -> None:
        self._host = host

    def setup(self, code: str) -> None:
        """(Re)connect the support websocket for *code* when provided."""
        host = self._host
        if host.app_websocket_thread and host.app_websocket_thread.isRunning():
            host.app_websocket_thread.quit()
            host.app_websocket_thread.wait()

        if not code:
            return

        worker = WebSocketWorker()
        thread = QThread()
        worker.moveToThread(thread)

        # Connect signals
        thread.started.connect(worker.start_connection)
        worker.connection.connect(host.websocket_on_change_status)
        worker.message_received.connect(host.websocket_on_message_received)
        worker.error_occurred.connect(host.websocket_on_error)
        worker.log.connect(host.add_log)
        worker.toggleRecording.connect(host.websocket_on_toggle_recording)
        worker.receivedCourseData.connect(host.websocket_on_received_course_data)
        host.sendMessage.connect(worker.send_msg_to_server)

        host.app_websocket_worker = worker
        host.app_websocket_thread = thread
        thread.start()

    def on_toggle_recording(self) -> None:
        self._host.recording_toggle()

    def on_change_status(self, status: bool) -> None:
        if status:
            self._host.app_websocket_status = Status.ENABLED
        else:
            self._host.app_websocket_status = Status.DISABLED

    def on_message_received(self, message: str) -> None:
        try:
            data = json.loads(message)

            message_type = data.get("message_type")
            if not self._host.lectoure_ws_data and message_type:
                self._host.lectoure_ws_data = data
        except json.JSONDecodeError as e:
            logger.debug("Ignoring non-JSON websocket message: %s", e)

    def on_error(self, message: str) -> None:
        logger.debug("Support websocket error: %s", message)

    def on_received_course_data(self, course_data: dict) -> None:
        host = self._host
        host.lectoure_ws_data = course_data
        name = course_data.get("course_name", DEFAULT_COURSE_NAME)
        if name != DEFAULT_COURSE_NAME:
            host.course_name = name[:25] + "..." if len(name) > 25 else name
