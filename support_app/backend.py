"""Backend object exposed to QML by the Macrosoft Support application."""

import os
import platform
from datetime import datetime

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication

from support_app import app_config, diagnostics, settings
from support_app.account_flow import AccountFlow
from support_app.app_config import (
    get_user_type,
)
from support_app.logging_setup import get_logger, log_files
from support_app.macrosoft_connect import uninstall_shortcut_path
from support_app.qt_bindings import notifying_property
from support_app.status import Status
from support_app.tasks import TaskRunner
from support_app.obs_control import is_obs_installed
from support_app.one_click import OneClickFlow
from support_app.progress import ProgressAggregator
from support_app.system_info import check_installation, is_service_running
from support_app.version import __version__
from support_app.websocket_session import SupportWebSocketSession
from support_app.workers import (
    AppInstallationWorker,
    AppServiceWorker,
    InitializeApp,
    OBSClientWorker,
    OBSInstallationWorker,
    OpenBrowserWorker,
    OpenOBSWorker,
    PermissionWorker,
    PreflightWorker,
    StartAppWorker,
    UserInfoWorker,
    UploadRetryWorker,
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
    themeChanged = Signal(bool)
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

        saved_settings = settings.load_settings()
        self._is_dark_theme = True if saved_settings.dark_theme is None else saved_settings.dark_theme

        self._progress = 0
        self._progress_aggregator = ProgressAggregator()
        self._task_runner = TaskRunner(
            on_progress=self.update_progress,
            on_log=self.add_log,
            on_self_uninstall=self.quit_application,
            on_task_error=self._on_worker_error,
        )
        self._one_click = OneClickFlow(self)
        self._account_flow = AccountFlow(self)
        self._websocket_session = SupportWebSocketSession(self)
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
    is_dark_theme = notifying_property(bool, "_is_dark_theme", "themeChanged")

    @Slot()
    def change_account(self):
        """Starts the web authentication flow."""
        self._account_flow.start()

    @Slot(dict)
    def on_account_auth_finished(self, result_data):
        """Handles the result from the AccountAuthWorker."""
        self._account_flow.on_finished(result_data)


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

    @Slot()
    def copy_rust_id(self):
        """Copy the current RustDesk id to the system clipboard."""
        QGuiApplication.clipboard().setText(self._rust_id)
        self.add_log(f"ID {self._rust_id} bolo skopírované do schránky.")

    @Slot()
    def toggle_theme(self):
        """Switch between the dark and light palettes and persist the choice."""
        self.is_dark_theme = not self._is_dark_theme
        saved = settings.load_settings()
        saved.dark_theme = self._is_dark_theme
        try:
            settings.save_settings(saved)
        except Exception as e:
            logger.warning("Could not persist the theme preference: %s", e)
        self.add_log("Téma: tmavá." if self._is_dark_theme else "Téma: svetlá.")

    @Slot()
    def create_diagnostics_bundle(self):
        """Write a timestamped zip with a status summary and the app logs."""
        summary = diagnostics.build_summary({
            "Generated": datetime.now().isoformat(timespec="seconds"),
            "App version": __version__,
            "Platform": platform.platform(),
            "User type": self._user_type,
            "Access code": self._access_code,
            "RustDesk ID": self._rust_id,
            "Username": self._username,
            "App installation": self._app_installation_status,
            "App service": self._app_service_status,
            "Permissions": self._permission_status,
            "Support websocket": self._app_websocket_status,
            "OBS installation": self._obs_installation_status,
            "OBS websocket": self._obs_websocket_status,
            "Recording": self._recording_status,
        })

        try:
            archive_path = diagnostics.create_diagnostics_archive(
                os.path.join(settings.APP_DATA_PATH, "diagnostics"),
                summary,
                log_files=log_files(),
            )
        except Exception as e:
            logger.exception("Could not create the diagnostics bundle")
            self.add_log(f"Diagnostický balík sa nepodarilo vytvoriť: {e}")
            self.showDialog.emit(
                "Chyba",
                "Diagnostický balík sa nepodarilo vytvoriť. Skontrolujte protokol aplikácie.",
                False,
            )
            return

        self.add_log(f"Diagnostický balík bol vytvorený: {archive_path}")
        self.showDialog.emit(
            "Diagnostický balík",
            f"Vytvorený súbor:\n{archive_path}",
            True,
        )

    @Slot()
    def run_preflight(self):
        """Run readiness checks in a worker and show the report."""
        self.add_log("Spúšťa sa pre-flight kontrola...")
        websocket_ok = None
        if self._is_user_admin:
            websocket_ok = self._app_websocket_status == Status.ENABLED
        self._start_worker(
            task_name="preflight",
            worker_class=PreflightWorker,
            start_method_name="run",
            finished_slot=self.on_preflight_finished,
            worker_args=(
                self._permission_status == Status.ENABLED,
                websocket_ok,
            ),
        )

    @Slot(dict)
    def on_preflight_finished(self, result):
        """Show the readiness report and mirror it to the log."""
        report = result.get("report", "")
        passed = bool(result.get("all_passed"))
        self.add_log(f"Pre-flight kontrola: {'v poriadku' if passed else 'našla problémy'}.")
        self.showDialog.emit("Pre-flight kontrola", report, passed)

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

    def _on_worker_error(self, task_name: str, error: BaseException) -> None:
        """Surface unexpected worker failures instead of leaving the UI stuck."""
        logger.error("Worker task %s failed: %s", task_name, error)
        self.add_log(f"Operácia zlyhala ({task_name}): {error}")
        self.showDialog.emit(
            "Chyba",
            "Operáciu sa nepodarilo dokončiť. Skontrolujte protokol aplikácie.",
            False,
        )

    # 1. THE PUBLIC SLOT FOR THE BUTTON
    @Slot()
    def one_click_setup(self):
        """Starts the one-click install → permissions → OBS workflow."""
        self._one_click.start()

    @Slot(dict)
    def _on_one_click_install_finished(self, result_data):
        self._one_click.on_install_finished(result_data)

    @Slot(dict)
    def _on_one_click_permissions_finished(self, result_data):
        self._one_click.on_permissions_finished(result_data)

    @Slot()
    def _on_one_click_obs_finished(self):
        self._one_click.on_obs_finished()

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
        aggregate_value = self._progress_aggregator.update(process_name, value)
        self.progress = aggregate_value

        if aggregate_value == 100:
            self._progress_aggregator.clear()
            QTimer.singleShot(100, self.reset_progress)

    def reset_progress(self):
        if self._progress_aggregator.is_empty:
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

        if self.is_user_lectoure:
            self.retry_pending_uploads()

        # if data["is_obs_running"]:
        #     self.connect_to_obs_websocket()

    def retry_pending_uploads(self):
        """Retry queued recording uploads in the background."""
        self._start_worker(
            task_name="upload_retry",
            worker_class=UploadRetryWorker,
            start_method_name="run",
            finished_slot=self.on_upload_retry_finished,
        )

    @Slot(dict)
    def on_upload_retry_finished(self, result):
        sent = result.get("sent", 0)
        remaining = result.get("remaining", 0)
        if sent:
            self.add_log(f"Znovu odoslaných nahrávok: {sent}.")
        if remaining == -1:
            self.add_log("Kontrola čakajúcich nahrávok zlyhala.")
        elif remaining:
            self.add_log(f"Čakajúcich nahrávok na odoslanie: {remaining}.")

    @Slot()
    def connect_to_obs_websocket(self):
        """connects to OBS websocket"""
        self._start_obs_client()

    def setup_websockets(self, code):
        """sets up websockets"""
        self._websocket_session.setup(code)

    @Slot()
    def websocket_on_toggle_recording(self):
        self._websocket_session.on_toggle_recording()

    @Slot(bool)
    def websocket_on_change_status(self, status):
        self._websocket_session.on_change_status(status)

    @Slot(str)
    def websocket_on_message_received(self, message):
        self._websocket_session.on_message_received(message)

    @Slot(str)
    def websocket_on_error(self, message):
        self._websocket_session.on_error(message)

    @Slot(dict)
    def websocket_on_received_course_data(self, course_data):
        self._websocket_session.on_received_course_data(course_data)


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

            # Flush the queued websocket frame instead of blocking the GUI
            # thread with a sleep during shutdown.
            self.obs_ws_worker.flush_websocket()
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
