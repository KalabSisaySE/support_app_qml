"""Backend object exposed to QML by the Macrosoft Support application."""

import json
import os
import time

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication

from support_app import api, app_config
from support_app.app_config import (
    RUSTDESK_REPORT_URL,
    get_cloudflare_headers,
    get_user_type,
    save_login_info,
)
from support_app.logging_setup import get_logger
from support_app.macrosoft_connect import uninstall_shortcut_path
from support_app.qt_bindings import notifying_property
from support_app.status import Status
from support_app.tasks import TaskRunner
from support_app.utils import check_installation, is_obs_installed, is_service_running
from support_app.workers import (
    AccountAuthWorker,
    AppInstallationWorker,
    AppServiceWorker,
    InitializeApp,
    OBSClientWorker,
    OBSInstallationWorker,
    OpenBrowserWorker,
    OpenOBSWorker,
    PermissionWorker,
    StartAppWorker,
    UserInfoWorker,
    WebSocketWorker,
)

logger = get_logger(__name__)


class MacrosoftBackend(QObject):
    # Signal Set Name
    userTypeChanged = Signal(bool)
    showDialog = Signal(str, str, bool)
    changeAccountBtnEnabledChanged = Signal(bool)

    startStream = Signal()
    stopStream = Signal()
    sendMessage = Signal(dict)

    # custom signals
    progressChanged = Signal(float)
    appInstallationStatusChanged = Signal(str)
    appServiceStatusChanged = Signal(str)
    appWebsocketStatusChanged = Signal(str)
    permissionStatusChanged = Signal(str)
    obsInstallationStatusChanged = Signal(str)
    obsWebsocketStatusChanged = Signal(str)
    recordingStatusChanged = Signal(str)


    appInstallBtnEnabledChanged = Signal(bool)
    appServiceBtnEnabledChanged = Signal(bool)
    appStartBtnEnabledChanged = Signal(bool)
    appRustIdBtnEnabledChanged = Signal(bool)
    enableMicrophoneOnlyBtnEnabledChanged = Signal(bool)
    enableMicrophoneAndCameraBtnEnabledChanged = Signal(bool)
    openBrowserBtnEnabledChanged = Signal(bool)
    openObsBtnEnabledChanged = Signal(bool)
    obsInstallBtnEnabledChanged = Signal(bool)

    newLogAdded = Signal(str)
    rustIdChanged = Signal(str)
    accessCodeChanged = Signal(str)
    usernameChanged = Signal(str)
    streamingUrlChanged = Signal(str)
    courseNameChanged = Signal(str)

    taskStarted = Signal()
    taskFinished = Signal()

    textField = ""

    def __init__(self):
        super().__init__()

        # values
        self._user_type = get_user_type()
        logger.info("user_type: %s", self._user_type)

        self._is_user_admin = self._user_type == "lectoure"
        logger.info("is_user_admin: %s", self._is_user_admin)

        self._progress = 0
        self._running_progresses = {}
        self._task_runner = TaskRunner(
            on_progress=self.update_progress,
            on_log=self.add_log,
            on_self_uninstall=self.quit_application,
        )
        self._app_installation_status = Status.DISABLED
        self._app_service_status = Status.DISABLED
        self._app_websocket_status = Status.DISABLED
        self._permission_status = Status.DISABLED
        self._obs_installation_status = Status.DISABLED
        self._obs_websocket_status = Status.DISABLED
        self._recording_status = Status.DISABLED

        self._is_app_install_btn_enabled = False
        self._is_app_start_btn_enabled = False
        self._is_app_service_btn_enabled = False
        self._is_app_rust_id_btn_enabled = False
        self._is_enable_microphone_only_btn_enabled = True
        self._is_enable_microphone_and_camera_btn_enabled = True
        self._is_open_browser_btn_enabled = True
        self._is_open_obs_btn_enabled = False
        self._is_obs_install_btn_enabled = False
        self._is_obs_record_btn_enabled = False
        self._is_change_account_btn_enabled = True

        self._access_code = "Nenájdené"
        self._rust_id = "Nenájdené"
        self._username = "Nenájdené"
        self._streaming_url = "Nevysiela sa"
        self._course_name = "Neznáme"

        self.lectoure_ws_data = None

        self.app_websocket_thread = None
        self.app_websocket_worker = None

        self.obs_ws_thread = None
        self.obs_ws_worker = None

        self.app_init_thread = None
        self.app_init_worker = None

        self.app_init()

    is_user_lectoure = notifying_property(bool, "_is_user_admin", "userTypeChanged")

    @Slot()
    def change_account(self):
        """Starts the web authentication flow."""
        self.is_change_account_btn_enabled = False
        self.add_log("Spúšťa sa proces zmeny účtu...")
        self._start_worker(
            task_name="account_auth",
            worker_class=AccountAuthWorker,  # Your new worker
            start_method_name="start_auth_flow",
            finished_slot=self.on_account_auth_finished
        )

    @Slot(dict)
    def on_account_auth_finished(self, result_data):
        """Handles the result from the AccountAuthWorker."""
        new_access_code = result_data.get('access_code')
        is_lectoure = result_data.get('is_lectoure', True)

        self.is_user_lectoure = is_lectoure


        if new_access_code:
            self.add_log("Účet bol úspešne zmenený.")

            # 1. Save the new code persistently
            save_login_info(new_access_code)

            # 2. Update the backend state
            self.access_code = new_access_code
            self.username = result_data.get('full_name', 'Nenájdené')

            # 3. Re-initialize websockets with the new identity
            # This will disconnect the old one and connect the new one
            self.setup_websockets(new_access_code)

            # 4. Optionally, re-report RustDesk ID for the new user
            if self._rust_id != "Nenájdené":
                # You might want a simple way to re-run this
                url = f"{RUSTDESK_REPORT_URL}?access={new_access_code}&rustdesk={self._rust_id}"
                try:
                    api.get(url, headers=get_cloudflare_headers(), retries=0)
                except Exception as e:
                    self.add_log(f"Nepodarilo sa znovu nahlásiť RustDesk ID: {e}")

            self.showDialog.emit("Účet Zmenený", "Vaša identita bola úspešne aktualizovaná.", True)
        else:
            self.add_log("Proces zmeny účtu zlyhal alebo bol zrušený.")
            self.showDialog.emit("Chyba", "Nepodarilo sa zmeniť účet.", False)

        self.is_change_account_btn_enabled = True


    is_change_account_btn_enabled = notifying_property(
        bool, "_is_change_account_btn_enabled", "changeAccountBtnEnabledChanged"
    )
    progress = notifying_property(float, "_progress", "progressChanged")
    rust_id = notifying_property(str, "_rust_id", "rustIdChanged")
    streaming_url = notifying_property(str, "_streaming_url", "streamingUrlChanged")
    course_name = notifying_property(str, "_course_name", "courseNameChanged")
    access_code = notifying_property(str, "_access_code", "accessCodeChanged")
    username = notifying_property(
        str, "_username", "usernameChanged", transform=lambda name: name or "Nenájdené"
    )
    is_app_install_btn_enabled = notifying_property(
        bool, "_is_app_install_btn_enabled", "appInstallBtnEnabledChanged"
    )
    is_app_start_btn_enabled = notifying_property(
        bool,
        "_is_app_start_btn_enabled",
        "appStartBtnEnabledChanged",
        transform=lambda enabled: enabled if check_installation() else False,
    )
    is_app_service_btn_enabled = notifying_property(
        bool, "_is_app_service_btn_enabled", "appServiceBtnEnabledChanged"
    )
    is_app_rust_id_btn_enabled = notifying_property(
        bool, "_is_app_rust_id_btn_enabled", "appRustIdBtnEnabledChanged"
    )
    is_enable_microphone_only_btn_enabled = notifying_property(
        bool, "_is_enable_microphone_only_btn_enabled", "enableMicrophoneOnlyBtnEnabledChanged"
    )
    is_enable_microphone_and_camera_btn_enabled = notifying_property(
        bool,
        "_is_enable_microphone_and_camera_btn_enabled",
        "enableMicrophoneAndCameraBtnEnabledChanged",
    )
    is_open_browser_btn_enabled = notifying_property(
        bool, "_is_open_browser_btn_enabled", "openBrowserBtnEnabledChanged"
    )
    is_open_obs_btn_enabled = notifying_property(
        bool, "_is_open_obs_btn_enabled", "openObsBtnEnabledChanged"
    )
    is_obs_install_btn_enabled = notifying_property(
        bool, "_is_obs_install_btn_enabled", "obsInstallBtnEnabledChanged"
    )
    is_obs_record_btn_enabled = notifying_property(
        bool, "_is_obs_record_btn_enabled", "obsInstallBtnEnabledChanged"
    )
    app_installation_status = notifying_property(
        str, "_app_installation_status", "appInstallationStatusChanged"
    )
    app_service_status = notifying_property(
        str, "_app_service_status", "appServiceStatusChanged"
    )
    permission_status = notifying_property(
        str, "_permission_status", "permissionStatusChanged"
    )
    app_websocket_status = notifying_property(
        str, "_app_websocket_status", "appWebsocketStatusChanged"
    )
    obs_installation_status = notifying_property(
        str, "_obs_installation_status", "obsInstallationStatusChanged"
    )
    obs_websocket_status = notifying_property(
        str, "_obs_websocket_status", "obsWebsocketStatusChanged"
    )
    recording_status = notifying_property(
        str, "_recording_status", "recordingStatusChanged"
    )

    @Slot(str)
    def add_log(self, log):
        """adds a new log to UI"""
        logger.info("%s", log)
        self.newLogAdded.emit(log)

    # Add this method inside the MacrosoftBackend class


    def _start_worker(self, task_name: str, worker_class, start_method_name: str, finished_slot, worker_args=None):
        """Create, configure and start a worker in a new thread."""
        self._task_runner.start(
            task_name,
            worker_class,
            start_method_name,
            finished_slot,
            worker_args=worker_args,
        )

    # 1. THE PUBLIC SLOT FOR THE BUTTON
    @Slot()
    def one_click_setup(self):
        """
        Starts the one-click process: install app, set permissions, and (if lectoure) install OBS.
        """
        self.add_log("Spúšťa sa kompletné nastavenie na 1-klik...")

        # Disable all relevant buttons to prevent user interference
        self.is_app_install_btn_enabled = False
        self.is_app_start_btn_enabled = False
        self.is_app_service_btn_enabled = False
        self.is_app_rust_id_btn_enabled = False
        self.is_enable_microphone_only_btn_enabled = False
        self.is_enable_microphone_and_camera_btn_enabled = False
        self.is_obs_install_btn_enabled = False

        # Check if the app is already installed to skip the installation step
        if check_installation():
            self.add_log("Aplikácia je už nainštalovaná. Prechádzam na nastavenie povolení.")
            # If installed, skip directly to the permission worker (Step 2)
            self._start_worker(
                task_name="one_click_permissions",
                worker_class=PermissionWorker,
                start_method_name="set_microphone_and_camera_access_only",
                finished_slot=self._on_one_click_permissions_finished
            )
        else:
            # If not installed, start with the installation worker (Step 1)
            self._start_worker(
                task_name="one_click_install",
                worker_class=AppInstallationWorker,
                start_method_name="handle_install",
                finished_slot=self._on_one_click_install_finished
            )

    @Slot(dict)
    def _on_one_click_install_finished(self, result_data):
        """
        Called after the installation worker finishes. Starts the permission worker.
        """
        self.add_log("Inštalácia aplikácie dokončená. Pokračujem nastavením povolení...")
        self.on_installation_finished(result_data)  # Update UI based on installation

        self._start_worker(
            task_name="one_click_permissions",
            worker_class=PermissionWorker,
            start_method_name="set_microphone_and_camera_access_only",
            finished_slot=self._on_one_click_permissions_finished
        )

    @Slot(dict)
    def _on_one_click_permissions_finished(self, result_data):
        """
        Called after the PermissionWorker finishes. Checks if OBS needs to be installed.
        """
        self.add_log("Nastavenie povolení dokončené.")
        self.update_permission_status(result_data)

        # Check if we need to install OBS (lectoure user and OBS not installed)
        if self.is_user_lectoure and not is_obs_installed():
            self.add_log("Používateľ je lektor, spúšťa sa inštalácia OBS...")
            self._start_worker(
                task_name="one_click_obs_install",
                worker_class=OBSInstallationWorker,
                start_method_name="install_app",
                finished_slot=self._on_one_click_obs_finished
            )
        else:
            if self.is_user_lectoure and is_obs_installed():
                self.add_log("OBS je už nainštalovaný, krok sa preskakuje.")
            self._on_one_click_complete()

    @Slot()
    def _on_one_click_obs_finished(self):
        """
        Called after the OBSInstallationWorker finishes.
        """
        self.add_log("Inštalácia OBS dokončená.")
        self.on_obs_installation_finished()
        self._on_one_click_complete()

    def _on_one_click_complete(self):
        """
        Called at the very end of the one-click chain. Re-enables buttons and shows a success message.
        """
        self.add_log("Kompletné nastavenie na 1-klik bolo úspešne dokončené!")

        # Re-enable all buttons now that the entire sequence is complete
        self.is_app_install_btn_enabled = True
        self.is_app_start_btn_enabled = check_installation()
        self.is_app_service_btn_enabled = check_installation()
        self.is_app_rust_id_btn_enabled = check_installation()
        self.is_enable_microphone_only_btn_enabled = True
        self.is_enable_microphone_and_camera_btn_enabled = True
        self.is_obs_install_btn_enabled = not is_obs_installed()

        self.showDialog.emit("Nastavenie Dokončené", "Kompletné nastavenie na 1-klik bolo úspešne dokončené!", True)

    @Slot()
    def install_or_uninstall(self):
        """dynamically installs or uninstalls Macrosoft RustDesk based on the current status"""

        self.is_app_install_btn_enabled = False
        self.is_app_start_btn_enabled = False
        self.is_app_service_btn_enabled = False
        self.is_app_rust_id_btn_enabled = False

        self._start_worker(
            task_name="app_installation",
            worker_class=AppInstallationWorker,
            start_method_name="handle_install",
            finished_slot=self.on_installation_finished
        )

    @Slot()
    def quit_application(self):
        """Gracefully quits the application."""
        self.add_log("Aplikácia sa zatvára na základe požiadavky na odinštalovanie.")
        QGuiApplication.instance().quit()


    @Slot()
    def install_obs(self):
        """install and updates OBS configs"""

        # Start the thread
        self.is_obs_install_btn_enabled = False
        self.is_open_obs_btn_enabled = False
        self.is_obs_record_btn_enabled = False
        self._start_worker(
            task_name="obs_installation",
            worker_class=OBSInstallationWorker,
            start_method_name="install_app",
            finished_slot=self.on_obs_installation_finished
        )

    @Slot()
    def start_app(self):
        """open Macrosoft RustDesk application"""

        self.is_app_start_btn_enabled = False
        self._start_worker(
            task_name="app_start",
            worker_class=StartAppWorker,
            start_method_name="start_macrosoftconnect",
            finished_slot=self.on_start_app_finished
        )

    @Slot()
    def get_rustid(self):
        """finds the apps rust id"""

        # Start the thread
        self.is_app_rust_id_btn_enabled = False
        self._start_worker(
            task_name="app_rust_id",
            worker_class=UserInfoWorker,
            start_method_name="get_rustdesk_id",
            finished_slot=self.on_get_rustid_finished
        )


    @Slot()
    def toggle_service(self):
        """turns on/off Macrosoft Rustdesk service"""
        start_method_name = "stop_service" if self.is_service_on() else "start_service"
        self.is_app_service_btn_enabled = False

        self._start_worker(
            task_name="app_service",
            worker_class=AppServiceWorker,
            start_method_name=start_method_name,
            finished_slot=self.on_toggle_service_finished
        )

    @Slot()
    def open_webpage(self):
        """opens Macrosoft website in user's browser"""

        self.is_open_browser_btn_enabled = False
        self._start_worker(
            task_name="open_browser",
            worker_class=OpenBrowserWorker,
            start_method_name="open_browser",
            finished_slot=self.on_open_webpage_finished
        )


    @Slot()
    def enable_microphone_only(self):
        """changes user devices settings to enable mic access"""
        self.is_enable_microphone_only_btn_enabled = False
        self.is_enable_microphone_and_camera_btn_enabled = False

        self._start_worker(
            task_name="microphone_only",
            worker_class=PermissionWorker,
            start_method_name="set_microphone_access_only",
            finished_slot=self.on_enable_microphone_only_finished
        )


    @Slot()
    def enable_microphone_and_camera(self):
        """changes user devices settings to enable mic and camera access"""

        self.is_enable_microphone_only_btn_enabled = False
        self.is_enable_microphone_and_camera_btn_enabled = False

        self._start_worker(
            task_name="microphone_and_camera",
            worker_class=PermissionWorker,
            start_method_name="set_microphone_and_camera_access_only",
            finished_slot=self.on_enable_microphone_and_camera_finished
        )

    @Slot()
    def toggle_recording(self):
        """handles button click to start/stop recording"""
        self.recording_toggle()

    def _start_obs_client(self):
        """Create and start the OBS websocket client thread if needed."""
        if self.obs_ws_thread and self.obs_ws_thread.isRunning():
            return

        self.obs_ws_worker = OBSClientWorker(self.lectoure_ws_data)
        self.obs_ws_thread = QThread()
        self.obs_ws_worker.moveToThread(self.obs_ws_thread)

        # Connect signals
        self.obs_ws_thread.started.connect(self.obs_ws_worker.connect_to_host)
        self.obs_ws_worker.connection.connect(self.on_obs_ws_status_change)
        self.obs_ws_worker.streamStatusChange.connect(self.on_obs_ws_stream_status_change)
        self.obs_ws_worker.streamStateInTransition.connect(self.on_obs_ws_stream_state_transitioning)
        self.obs_ws_worker.log.connect(self.add_log)
        self.obs_ws_worker.errorOccurred.connect(self.on_obs_ws_error)
        self.obs_ws_worker.rtmpUrlFetched.connect(self.on_obs_ws_rtmp_fetched)
        self.obs_ws_worker.complete.connect(self.on_obs_ws_complete)

        self.startStream.connect(self.obs_ws_worker.start_stream)
        self.stopStream.connect(self.obs_ws_worker.stop_stream)

        self.obs_ws_thread.start()

    def recording_toggle(self):
        self._start_obs_client()

        if self._recording_status != Status.ENABLED:
            self.startStream.emit()
        else:
            self.stopStream.emit()

        self.is_obs_record_btn_enabled = False
        self.is_open_obs_btn_enabled = False

    @Slot(bool)
    def on_obs_ws_status_change(self, status):
        if status:
            self.obs_websocket_status = Status.ENABLED
        else:
            self.sendMessage.emit({
                "client": "device",
                "access_code": self._access_code,
                "success": False,
                "message": "OBS disconnected"
            }
            )
            self.obs_websocket_status = Status.DISABLED
            self.recording_status = Status.DISABLED
            if self.obs_ws_thread and self.obs_ws_thread.isRunning():

                self.obs_ws_thread.quit()
                self.obs_ws_thread.wait()
                self.obs_ws_thread.deleteLater()
                self.obs_ws_thread = None

            if self.obs_ws_worker:

                self.obs_ws_worker.deleteLater()
                self.obs_ws_worker = None
            is_installed = is_obs_installed()
            self.is_open_obs_btn_enabled = is_installed
            self.is_obs_record_btn_enabled = is_installed
            self.streaming_url = "Nevysiela sa"
            self.course_name = "Neznáme"

    @Slot(bool)
    def on_obs_ws_stream_status_change(self, status):

        if status:
            self.recording_status = Status.ENABLED
            self.sendMessage.emit({
                    "client": "device",
                    "access_code": self._access_code,
                    "success": True,
                    "message": "Recording started successfully"
                }
            )
        else:
            self.recording_status = Status.DISABLED
            self.sendMessage.emit({
                "client": "device",
                "access_code": self._access_code,
                "success": True,
                "message": "Recording stopped successfully"
            }
            )
            self.streaming_url = "Nevysiela sa"
            self.course_name = "Neznáme"

        self.is_obs_record_btn_enabled = True
        self.is_open_obs_btn_enabled = True

    @Slot()
    def on_obs_ws_stream_state_transitioning(self):
        self.is_obs_record_btn_enabled = False
        self.is_open_obs_btn_enabled = False

    @Slot(str)
    def on_obs_ws_error(self, message):
        self.add_log(f"OBS websocket error: {message}")

    @Slot(str)
    def on_obs_ws_rtmp_fetched(self, rtmp_url):
        self.streaming_url = rtmp_url

    @Slot()
    def on_obs_ws_complete(self):
        self.is_obs_record_btn_enabled = True


    @Slot()
    def open_obs(self):
        """opens OBS"""
        self.is_open_obs_btn_enabled = False
        self._start_worker(
            task_name="open_obs",
            worker_class=OpenOBSWorker,
            start_method_name="open_obs_app",
            finished_slot=self.on_open_obs_finished
        )


    @Slot(float, str)
    def update_progress(self, value, process_name):
        self._running_progresses[process_name] = value
        aggregate_value = sum(self._running_progresses.values()) / len(self._running_progresses)
        self.progress = aggregate_value

        if aggregate_value == 100:
            self._running_progresses = {}
            QTimer.singleShot(100, self.reset_progress)

    def reset_progress(self):
        if not self._running_progresses:
            self.progress = 0

    def app_init(self):
        if self.app_init_thread and self.app_init_thread.isRunning():
            self.app_init_thread.quit()
            self.app_init_thread.wait()

        self.app_init_thread = QThread()
        self.app_init_worker = InitializeApp()
        self.app_init_worker.moveToThread(self.app_init_thread)

        self.app_init_thread.started.connect(self.app_init_worker.start)
        self.app_init_worker.complete.connect(self.on_app_init_complete)

        self.app_init_thread.start()

    @Slot(dict)
    def on_app_init_complete(self, data):

        self.app_init_thread.quit()
        self.app_init_thread.wait()
        self.app_init_thread.deleteLater()
        self.app_init_thread = None

        self.app_init_worker.deleteLater()
        self.app_init_worker = None

        code = data["access_code"]

        self.access_code = code
        self.username = data["full_name"]
        self.rust_id = data["rust_id"]
        self.permission_status = data["permission_status"]
        self.app_installation_status = Status.ENABLED if data["is_app_installed"] else Status.DISABLED
        self.app_service_status = Status.ENABLED if data["is_app_service_running"] else Status.DISABLED
        self.obs_installation_status = Status.ENABLED if data["is_obs_installed"] else Status.DISABLED

        self.is_app_install_btn_enabled = True
        if data["is_app_installed"]:
            self.is_app_start_btn_enabled = True
            self.is_app_service_btn_enabled = True
            self.is_app_rust_id_btn_enabled = True
        else:
            self.is_app_start_btn_enabled = False
            self.is_app_service_btn_enabled = False
            self.is_app_rust_id_btn_enabled = False

        if data["is_obs_installed"]:
            self.is_open_obs_btn_enabled = True
            self.is_obs_install_btn_enabled = False
            self.is_obs_record_btn_enabled = True
        else:
            self.is_obs_install_btn_enabled = True

        # setup websocket
        if code != "Nenájdené":
            if self.is_user_lectoure:
                self.setup_websockets(code)

        # if data["is_obs_running"]:
        #     self.connect_to_obs_websocket()

    @Slot()
    def connect_to_obs_websocket(self):
        """connects to OBS websocket"""
        self._start_obs_client()

    def setup_websockets(self, code):
        """sets up websockets"""
        if self.app_websocket_thread and self.app_websocket_thread.isRunning():
            self.app_websocket_thread.quit()
            self.app_websocket_thread.wait()

        if code:
            self.app_websocket_worker = WebSocketWorker()
            self.app_websocket_thread = QThread()
            self.app_websocket_worker.moveToThread(self.app_websocket_thread)

            # Connect signals
            self.app_websocket_thread.started.connect(self.app_websocket_worker.start_connection)
            self.app_websocket_worker.connection.connect(self.websocket_on_change_status)
            self.app_websocket_worker.message_received.connect(self.websocket_on_message_received)
            self.app_websocket_worker.error_occurred.connect(self.websocket_on_error)
            self.app_websocket_worker.log.connect(self.add_log)
            self.app_websocket_worker.toggleRecording.connect(self.websocket_on_toggle_recording)
            self.app_websocket_worker.receivedCourseData.connect(self.websocket_on_received_course_data)
            self.sendMessage.connect(self.app_websocket_worker.send_msg_to_server)

            self.app_websocket_thread.start()

    @Slot()
    def websocket_on_toggle_recording(self):
        self.recording_toggle()

    @Slot(bool)
    def websocket_on_change_status(self, status):
        if status:
            self.app_websocket_status = Status.ENABLED
        else:
            self.app_websocket_status = Status.DISABLED

    @Slot(str)
    def websocket_on_message_received(self, message):
        try:
            data = json.loads(message)

            message_type = data.get("message_type")
            if not self.lectoure_ws_data and message_type:
                self.lectoure_ws_data = data
        except json.JSONDecodeError as e:
            logger.debug("Ignoring non-JSON websocket message: %s", e)

    @Slot(str)
    def websocket_on_error(self, message):
        logger.debug("Support websocket error: %s", message)

    @Slot(dict)
    def websocket_on_received_course_data(self, course_data):
        self.lectoure_ws_data = course_data
        name = course_data.get("course_name", "course_name")
        if name != "course_name":
            self.course_name = name[:25] + "..." if len(name) > 25 else name


    @Slot()
    def refresh_app_status(self):
        """refreshes whole app status"""
        self.is_app_install_btn_enabled = True
        self.is_app_start_btn_enabled = True
        self.is_app_service_btn_enabled = True

        if check_installation():
            self.app_installation_status = Status.ENABLED
            if self.is_service_on():
                self.app_service_status = Status.ENABLED
            else:
                self.app_service_status = Status.DISABLED
        else:
            self.app_installation_status = Status.DISABLED
            self.is_app_start_btn_enabled = False
            self.is_app_service_btn_enabled = False

    def is_service_on(self):
        """checks if Macrosoft rustdesk service is running"""
        return is_service_running(f"{app_config.NAME}")



    @Slot(dict)
    def on_installation_finished(self, result_data):
        """updates app state, cleans up, releases resources"""
        logger.debug("on_installation_finished")
        if result_data.get("app_installed"):
            self.app_installation_status = Status.ENABLED

            if result_data.get("app_service_on"):
                self.app_service_status = Status.ENABLED

            if result_data.get("rust_id"):
                self.rust_id = result_data.get("rust_id")

            self.is_app_start_btn_enabled = True
            self.is_app_service_btn_enabled = True
            self.is_app_rust_id_btn_enabled = True

            # --- NEW: Show success dialog ---
            self.showDialog.emit("Inštalácia Úspešná", "Aplikácia Macrosoft QuickSupport bola úspešne nainštalovaná.", True)

        else:
            self.app_installation_status = Status.DISABLED
            self.app_service_status = Status.DISABLED
            self.rust_id = result_data.get("rust_id")
            self.is_app_start_btn_enabled = False
            self.is_app_service_btn_enabled = False
            self.is_app_rust_id_btn_enabled = False

            # --- NEW: Show different dialog for uninstallation ---
            # We check if the uninstaller path exists to guess if it was an uninstall action
            uninstall_path = uninstall_shortcut_path()
            if not os.path.exists(uninstall_path):
                self.showDialog.emit("Odinštalovanie Dokončené", "Aplikácia bola úspešne odinštalovaná.", True)
            else:
                # It might be a failed installation, you can add more logic here
                self.showDialog.emit("Chyba", "Počas inštalácie sa vyskytla chyba.", False)

        self.is_app_install_btn_enabled = True


    @Slot()
    def on_obs_installation_finished(self):
        """updates obs installation status"""
        self.obs_installation_status = Status.ENABLED if is_obs_installed() else Status.DISABLED
        self.is_obs_install_btn_enabled = False
        self.is_open_obs_btn_enabled = True
        self.is_obs_record_btn_enabled = True

    @Slot()
    def on_start_app_finished(self):
        """cleans up when start app button is clicked"""

        self.is_app_start_btn_enabled = check_installation()

    @Slot()
    def on_get_rustid_finished(self, result):
        """cleans up when start app button is clicked"""

        self.is_app_rust_id_btn_enabled = True

    @Slot()
    def on_toggle_service_finished(self):
        """cleans up when start service button is clicked"""

        self.app_service_status = Status.ENABLED if check_installation() and self.is_service_on() else Status.DISABLED

        self.is_app_service_btn_enabled = True

    @Slot()
    def on_open_webpage_finished(self):
        self.is_open_browser_btn_enabled = True

    @Slot()
    def on_open_obs_finished(self):
        self.is_open_obs_btn_enabled = True

    @Slot(dict)
    def on_enable_microphone_only_finished(self, result):

        self.update_permission_status(result)

        self.is_enable_microphone_only_btn_enabled = True
        self.is_enable_microphone_and_camera_btn_enabled = True


    @Slot(dict)
    def on_enable_microphone_and_camera_finished(self, result):
        self.update_permission_status(result)

        self.is_enable_microphone_only_btn_enabled = True
        self.is_enable_microphone_and_camera_btn_enabled = True

        # if "all_permissions" in self._running_progresses:
        #     del self._running_progresses["all_permissions"]


    def update_permission_status(self, result):
        """updates permission status based on the given data"""
        webcam_allowed = result.get("is_webcam_allowed")
        microphone_allowed = result.get("is_microphone_allowed")
        browser_permissions_allowed = result.get("is_browser_permissions_allowed")

        if microphone_allowed and webcam_allowed and browser_permissions_allowed:
            self.permission_status = Status.ENABLED
        elif microphone_allowed:
            self.permission_status = Status.CHECKING
        else:
            self.permission_status = Status.DISABLED

    def cleanup(self):
        """
        Handles application cleanup, including stopping the OBS stream if it's running.
        """
        # --- START: New Feature ---
        # Before shutting down threads, check if OBS is connected and streaming.
        # If so, send a command to stop the stream.
        if (self.obs_ws_worker and
                self._obs_websocket_status == Status.ENABLED and
                self._recording_status == Status.ENABLED):
            self.add_log("Aplikácia sa zatvára. Zastavuje sa stream v OBS...")

            # Call the dedicated method to stop the stream
            self.obs_ws_worker.force_stop_stream_on_exit()

            # Give the message a moment to be sent over the websocket before
            # the app fully closes and quits the worker thread.
            time.sleep(1)
        # --- END: New Feature ---

        # Original cleanup logic for threads and workers
        app_threads = [self.app_websocket_thread, self.obs_ws_thread]
        app_workers = [self.app_websocket_worker, self.obs_ws_worker]

        for thread in app_threads:
            if thread and thread.isRunning():
                thread.quit()
                thread.wait()
                thread.deleteLater()

        for worker in app_workers:
            if worker:
                # The OBS worker might have already been cleaned up if OBS disconnected,
                # so checking its existence is important.
                worker.deleteLater()
