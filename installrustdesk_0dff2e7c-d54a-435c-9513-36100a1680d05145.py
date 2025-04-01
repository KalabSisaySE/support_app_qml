# This Python file uses the following encoding: utf-8
import ctypes
import time
import sys
import os
import datetime
import urllib.request
import subprocess

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal, QTimer, QUrl, Property, QThread, QUrlQuery
from PySide6.QtWebSockets import QWebSocket, QWebSocketProtocol
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtQuickControls2 import QQuickStyle

from support_app.utils import is_app_running, is_service_running, get_access_code, get_full_name, check_installation, open_website, is_obs_running, is_obs_installed, start_obs, close_obs
from support_app.rust_service_manager import ServiceManager
from support_app.registry_permission_manager import RegistryPermissionManager
from support_app.browser_permission_manager import BrowserPermissionManager


class AppInstallationWorker(QObject):
    """manages macrosoft rustdesk installation and uninstallation"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.result_data = {
            "app_installed": False,
            "app_service_on": False,
            "rust_id": "Nenájdené"
        }
        self.access = get_access_code(os.path.basename(sys.argv[0]))
        self.manager = ServiceManager(
            service_name="MacrosoftConnectQuickSupport",
            display_name="MacrosoftConnectQuickSupport Service",
            binary_path=(
                r'"C:\Program Files\MacrosoftConnectQuickSupport\MacrosoftConnectQuickSupport.exe" --service'
            ),
        )

    @Slot()
    def handle_install(self):
        """handles installation state"""
        if check_installation():
            self.uninstall_app()
        else:
            self.install_app()

    def install_app(self):
        """installs and rust Macrosoft RustDesk"""
        self.log.emit("Začínam proces inštalácie...")

        base_url = "https://online.macrosoft.sk/static/"
        download_url = f"{base_url}ztpt/output/downloads/macrosoftconnectquicksupport.exe"
        new_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        temp_dir = os.environ.get("TEMP", new_path)

        os.makedirs(temp_dir, exist_ok=True)
        installer_path = os.path.join(temp_dir, "macrosoftconnectquicksupport.exe")

        try:
            with urllib.request.urlopen(download_url) as response:
                total_size = int(response.getheader("Content-Length", "0"))
                block_size = 8192
                with open(installer_path, "wb") as file:
                    downloaded = 0
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        file.write(buffer)
                        downloaded += len(buffer)
                        if total_size > 0:
                            percent = int(downloaded * 100 / total_size)
                            self.progress_changed.emit(percent)
        except Exception as e:
            self.log.emit(f"Chyba pri sťahovaní súboru: {e}")
            self.finished.emit(self.result_data)
            return

        try:
            # Prepare startup info to hide cmd window
            self.log.emit(f"Installing Macrosoft Connect Quick Support...")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            SW_HIDE = 0
            startupinfo.wShowWindow = SW_HIDE

            # Run the installer
            process = subprocess.Popen(
                [installer_path, "--silent-install"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
            )

            time.sleep(10)  # Wait 10 seconds after installation
            self.result_data["app_installed"] = True
            self.result_data["app_service_on"] = self.start_service()
            self.result_data["rust_id"] = self.get_rustdesk_id()

        except Exception as e:
            self.log.emit(f"Chyba počas inštalácie: {e}")

        self.finished.emit(self.result_data)

    def uninstall_app(self):
        """uninstalls and rust Macrosoft RustDesk"""
        uninstall_path = os.path.join(
            "C:\\Program Files\\MacrosoftConnectQuickSupport",
            "Uninstall MacrosoftConnectQuickSupport.lnk",
        )

        if not os.path.exists(uninstall_path):
            self.log.emit("Odinštalačný súbor nebol nájdený.")
            self.finished.emit(self.result_data)
            return

        try:
            SW_HIDE = 0
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "open", uninstall_path, None, None, SW_HIDE
            )
            if result <= 32:
                raise Exception(f"ShellExecuteW zlyhalo s kódom {result}")
            app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"
            max_wait_time = 120  # Maximum wait time in seconds
            start_time = time.time()
            while os.path.exists(app_path):
                if time.time() - start_time > max_wait_time:
                    self.log.emit("Odinštalácia trvá príliš dlho.")
                    break
                time.sleep(1)
            self.log.emit("MacrosoftConnectQuickSupport bol odinštalovaný úspešne.")
        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť odinštalátor: {e}")

        self.finished.emit(self.result_data)

    def get_rustdesk_id(self):
        """Retrieve the RustDesk ID."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

        if not os.path.exists(app_path):
            self.log.emit(
                "MacrosoftConnectQuickSupport nie je nainštalovaný, prosím kliknite na Inštalovať MacrosoftConnectQuickSupport"
            )
            return "Nenájdené"

        try:
            result = subprocess.run(
                [app_path, "--get-id"],
                capture_output=True,
                text=True,
                check=True,
            )
            rustdesk_id = result.stdout.strip() if result.stdout else "Nenájdené"


            self.log.emit(f"Vaše ID je: {rustdesk_id}")
            self.report_rustdesk_id(rustdesk_id)
            return rustdesk_id

        except Exception as e:
            self.log.emit(f"Nepodarilo sa získať ID: {e}")
            return "Nenájdené"

    def report_rustdesk_id(self, rustdesk_id, max_attempts=3):
        """report the RustDesk ID to the server."""
        if self.access:
            base_url = "https://online.macrosoft.sk/rustdesk/"
            url = f"{base_url}?access={self.access}&rustdesk={rustdesk_id}"
            attempt = 0

            while attempt < max_attempts:
                attempt += 1
                try:
                    with urllib.request.urlopen(url) as response:
                        if response.status == 200:
                            self.log.emit("ID bolo úspešne odoslané.")
                        else:
                            self.log.emit(f"Odozva servera: {response.status}")
                            if attempt < max_attempts:
                                time.sleep(1)
                except Exception as e:
                    self.log.emit(f"Nepodarilo sa odoslať ID: {e}")

    def check_installation(self):
        """Check if the application is installed and update the UI accordingly."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

        if os.path.exists(app_path):
            return True

    def start_macrosoftconnect(self):
        """Start the MacrosoftConnectQuickSupport application."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"
        if not os.path.exists(app_path):
            return

        try:
            subprocess.Popen(
                [app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return True
        except Exception as e:
            return

    def start_service(self):
        """Start the MacrosoftConnectQuickSupport service."""
        try:
            if is_service_running("MacrosoftConnectQuickSupport"):
                self.log.emit("Service is running...")
                return True

            if not self.check_installation():
                self.log.emit("App is not installed. Install app first...")
                return

            if not is_app_running():
                self.log.emit("App is not running. Running app...")
                if not self.start_macrosoftconnect():
                    self.log.emit("Couldn't start app automatically...")
                    return

            if not self.manager.is_service_installed():
                self.log.emit("Creating Service...")
                self.manager.create_service()

            self.manager.start_service()
            self.log.emit("MacrosoftConnectQuickSupport Service is running")
            return True

        except Exception as e:
            self.log.emit(f"Failed to start MacrosoftConnectQuickSupport Service, {e}")


    def stop_service(self):
        """Stop the MacrosoftConnectQuickSupport service."""
        try:
            if is_service_running("MacrosoftConnectQuickSupport"):
                self.log.emit("service is running")
                if is_app_running():
                    self.log.emit("app is running")
                    self.manager.stop_service()
                    self.log.emit("MacrosoftConnectQuickSupport Service has stopped")
                    return True
                else:
                    self.log.emit("Service is not running...")

            else:
                self.log.emit("Service is not running...")
                return True
        except Exception as e:
            self.log.emit(
                f"Failed to stop MacrosoftConnectQuickSupport Service {e}"
            )

class StartAppWorker(QObject):
    """manages macrosoft rustdesk starting"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal()

    @Slot()
    def start_macrosoftconnect(self):
        """Start the MacrosoftConnectQuickSupport application."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

        if not os.path.exists(app_path):
            self.log.emit(
                "MacrosoftConnectQuickSupport nie je nainštalovaný, prosím kliknite na Inštalovať MacrosoftConnectQuickSupport"
            )

        try:
            subprocess.Popen(
                [app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self.log.emit("MacrosoftConnectQuickSupport bol spustený.")
        except Exception as e:
            self.log.emit(
                f"Nepodarilo sa spustiť MacrosoftConnectQuickSupport: {e}"
            )


        self.finished.emit()

class AppServiceWorker(QObject):
    """manages macrosoft rustdesk service"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal()
    manager = ServiceManager(
        service_name="MacrosoftConnectQuickSupport",
        display_name="MacrosoftConnectQuickSupport Service",
        binary_path=(
            r'"C:\Program Files\MacrosoftConnectQuickSupport\MacrosoftConnectQuickSupport.exe" --service'
        ),
    )

    def check_installation(self):
        """Check if the application is installed and update the UI accordingly."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

        if os.path.exists(app_path):
            return True

    def start_macrosoftconnect(self):
        """Start the MacrosoftConnectQuickSupport application."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

        if not os.path.exists(app_path):
            return

        try:
            subprocess.Popen(
                [app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return True
        except Exception as e:
            return

    @Slot()
    def start_service(self, signals=None):
        """Start the MacrosoftConnectQuickSupport service."""
        try:
            if not self.check_installation():
                self.log.emit("App is not installed. Install app first...")
                self.finished.emit()
                return

            if not is_app_running():
                self.log.emit("App is not running. Running app...")
                if not self.start_macrosoftconnect():
                    self.log.emit("Couldn't start app automatically...")
                    self.finished.emit()
                    return

            if not self.manager.is_service_installed():
                self.log.emit("Creating Service...")
                self.manager.create_service()

            self.manager.start_service()
            self.log.emit("MacrosoftConnectQuickSupport Service is running")

        except Exception as e:
            self.log.emit(f"Failed to start MacrosoftConnectQuickSupport Service, {e}")

        self.finished.emit()

    @Slot()
    def stop_service(self):
        """Stop the MacrosoftConnectQuickSupport service."""
        try:
            self.log.emit("In Stop Service")
            if is_service_running("MacrosoftConnectQuickSupport"):
                self.log.emit("service is running")
                if is_app_running():
                    self.log.emit("app is running")
                    self.manager.stop_service()
                    self.log.emit("MacrosoftConnectQuickSupport Service has stopped")

                else:
                    self.log.emit("Service is not running...")
            else:
                self.log.emit("Service is not running...")
        except Exception as e:
            self.log.emit(
                f"Failed to stop MacrosoftConnectQuickSupport Service {e}"
            )

        self.finished.emit()

class UserInfoWorker(QObject):
    """manages macrosoft rustdesk and userinfo"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.result_data = {
            "username": "",
            "rust_id": "Nenájdené"
        }
        self.access = get_access_code(os.path.basename(sys.argv[0]))
        self.app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

    @Slot()
    def get_rustdesk_id(self):
        """Retrieve the RustDesk ID."""
        if not os.path.exists(self.app_path):
            self.log.emit(
                "MacrosoftConnectQuickSupport nie je nainštalovaný, prosím kliknite na Inštalovať MacrosoftConnectQuickSupport"
            )
            self.finished.emit(self.result_data)

        try:
            result = subprocess.run(
                [self.app_path, "--get-id"],
                capture_output=True,
                text=True,
                check=True,
            )
            rustdesk_id = result.stdout.strip() if result.stdout else "Nenájdené"

            self.log.emit(f"Vaše ID je: {rustdesk_id}")
            self.report_rustdesk_id(rustdesk_id)
            self.result_data["rust_id"] = rustdesk_id

        except Exception as e:
            self.log.emit(f"Nepodarilo sa získať ID: {e}")

        self.finished.emit(self.result_data)

    def report_rustdesk_id(self, rustdesk_id, max_attempts=3):
        """Report the RustDesk ID to the server."""
        if self.access:
            url = f"https://online.macrosoft.sk/rustdesk/?access={self.access}&rustdesk={rustdesk_id}"
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                try:
                    with urllib.request.urlopen(url) as response:
                        if response.status == 200:
                            self.log.emit("ID bolo úspešne odoslané.")
                        else:
                            self.log.emit(f"Odozva servera: {response.status}")
                            if attempt < max_attempts:
                                time.sleep(1)
                except Exception as e:
                    self.log.emit(f"Nepodarilo sa odoslať ID: {e}")

    @Slot()
    def set_username(self):
        """Fetch and set the user's full name."""
        self.log.emit("Fetching username...")
        full_name = get_full_name(self.access)
        if full_name:
            self.log.emit(f"Full name fetched: {full_name}")
        else:
            self.log.emit("Nepodarilo sa získať meno z API")

        self.finished.emit()

class OpenBrowserWorker(QObject):
    """manages opening/closing a browser"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.access = get_access_code(os.path.basename(sys.argv[0]))

    @Slot()
    def open_browser(self):
        """Open the default page in user's default browser."""
        try:
            self.log.emit("Opening website ...")
            if open_website(self.access):
                self.log.emit("Website Opened")
            else:
                self.log.emit("Website Failed to open")

        except Exception as e:
            self.log.emit("Website Failed to open")

        self.finished.emit()

class PermissionWorker(QObject):
    """manages opening/closing a browser"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.access = get_access_code(os.path.basename(sys.argv[0]))
        self.registry_permission = RegistryPermissionManager()
        self.browser_permission = BrowserPermissionManager()
        self.result_data = {
            "is_webcam_allowed": False,
            "is_microphone_allowed": False,
            "is_browser_permissions_allowed": False,
        }

    @Slot()
    def set_microphone_access_only(self):
        """Set microphone access permissions only."""
        self.log.emit("Setting microphone access only.")
        self.registry_permission.set_microphone_only_access_powershell()
        self.check_permissions()
        self.finished.emit(self.result_data)

    @Slot()
    def set_microphone_and_camera_access_only(self):
        """Set all necessary permissions."""
        self.log.emit("Setting all permissions...")
        self.registry_permission.set_microphone_and_webcam_access_powershell()
        self.browser_permission.set_browser_permissions()
        self.check_permissions()
        self.finished.emit(self.result_data)

    def check_permissions(self):
        """checks permissions statuses"""
        is_microphone_allowed = self.registry_permission.is_microphone_allowed()
        is_webcam_allowed = self.registry_permission.is_webcam_allowed()
        is_browser_permissions_allowed = self.browser_permission.is_browser_permissions_allowed()

        self.result_data["is_microphone_allowed"] = is_microphone_allowed
        self.result_data["is_webcam_allowed"] = is_webcam_allowed
        self.result_data["is_browser_permissions_allowed"] = is_browser_permissions_allowed

        self.log.emit(f"microphone_allowed: {is_microphone_allowed}")
        self.log.emit(f"webcam_allowed: {is_webcam_allowed}")
        self.log.emit(f"browser_permissions_allowed: {is_browser_permissions_allowed}")

class WebSocketWorker(QObject):
    connection = Signal(bool)
    message_received = Signal(str)
    error_occurred = Signal(str)
    log = Signal(str)

    def __init__(self):
        super().__init__()
        script_name = os.path.basename(sys.argv[0])
        self.access = get_access_code(script_name)

        # WebSocket setup
        url = QUrl("wss://online.macrosoft.sk/ws/support/")
        query = QUrlQuery()
        query.addQueryItem("access_code", self.access)
        url.setQuery(query)
        self.url = url

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

        self.log.emit("WebSocketWorker initialized")

    @Slot()
    def start_connection(self):
        self.log.emit("Attempting WebSocket connection...")
        self.websocket.open(QUrl(self.url))

    @Slot()
    def disconnect(self):
        # Manual disconnection (disable reconnection)
        self.manual_disconnect = True
        self.reconnect_enabled = False
        self.reconnect_timer.stop()
        self.websocket.close()
        self.log.emit("Manual disconnect requested")

    @Slot()
    def on_connected(self):
        self.log.emit("Connected to WebSocket server")
        self.current_reconnect_delay = self.initial_reconnect_delay  # Reset delay
        self.reconnect_needed = False  # Clear error flag
        self.connection.emit(True)

    @Slot()
    def on_disconnected(self):
        self.log.emit("Disconnected from WebSocket server")
        self.connection.emit(False)

        close_code = self.websocket.closeCode()
        close_reason = self.websocket.closeReason()
        self.log.emit(f"Close code: {close_code}, reason: {close_reason}")

        # Do not reconnect if:
        # 1. User manually disconnected
        # 2. Server closed gracefully (non-network issue)
        # 3. Error was non-network-related (e.g., invalid access code)
        if self.manual_disconnect:
            self.manual_disconnect = False  # Reset for next session
            self.log.emit("Manual disconnect: No reconnection")
            return

        if close_code != QWebSocketProtocol.CloseCodeAbnormalClosure:
            self.log.emit("Server-initiated disconnect: No reconnection")
            return

        if not self.reconnect_needed:
            self.log.emit("Non-network error: No reconnection")
            return

        # Proceed with reconnection for network failures
        if self.reconnect_enabled:
            delay = self.current_reconnect_delay
            self.log.emit(f"Reconnecting in {delay / 1000} seconds...")
            self.reconnect_timer.start(delay)
            self.current_reconnect_delay = min(
                self.current_reconnect_delay * 2,
                self.max_reconnect_delay
            )

    @Slot(QAbstractSocket.SocketError)
    def on_error(self, error_code):
        error_msg = self.websocket.errorString()
        self.log.emit(f"WebSocket error: {error_msg}")
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

    # ... (rest of existing methods like send_message)
    @Slot(str)
    def on_text_message_received(self, message):
        self.log.emit(f"WebSocketWorker on_text_message_received")
        self.message_received.emit(message)


    @Slot(str)
    def send_message(self, message):
        self.log.emit(f"WebSocketWorker send_message")
        if self.websocket.state() == QAbstractSocket.ConnectedState:
            self.websocket.sendTextMessage(message)
        else:
            self.error_occurred.emit("Not connected to WebSocket server")


class MainWindow(QObject):
    # Signal Set Name
    setName = Signal(str)
    addCounter = Signal(str)
    printTime = Signal(str)
    isVisible = Signal(bool)
    readText = Signal(str)

    # custom signals
    progressChanged = Signal(int)
    appInstallationStatusChanged = Signal(str)
    appServiceStatusChanged = Signal(str)
    appWebsocketStatusChanged = Signal(str)
    permissionStatusChanged = Signal(str)
    obsInstallationStatusChanged = Signal(str)
    recordingStatusChanged = Signal(str)


    appInstallBtnEnabledChanged = Signal(bool)
    appServiceBtnEnabledChanged = Signal(bool)
    appStartBtnEnabledChanged = Signal(bool)
    appRustIdBtnEnabledChanged = Signal(bool)
    enableMicrophoneOnlyBtnEnabledChanged = Signal(bool)
    enableMicrophoneAndCameraBtnEnabledChanged = Signal(bool)
    openBrowserBtnEnabledChanged = Signal(bool)

    newLogAdded = Signal(str)
    rustIdChanged = Signal(str)
    accessCodeChanged = Signal(str)
    usernameChanged = Signal(str)

    taskStarted = Signal()
    taskFinished = Signal()

    textField = ""

    def __init__(self):
        super().__init__()  # Prefer super() over direct QObject initialization

        # values
        self._progress = 0
        self._app_installation_status = "enabled" if self.check_installation() else "disabled"
        self._app_service_status = "enabled" if self.check_installation() and self.is_service_on() else "disabled"
        self._app_websocket_status = "disabled"
        self._permission_status = "disabled"
        self._obs_installation_status = "disabled"
        self._recording_status = "disabled"

        self._is_app_install_btn_enabled = False
        self._is_app_start_btn_enabled = self.check_installation()
        self._is_app_service_btn_enabled = self.check_installation()
        self._is_app_rust_id_btn_enabled = self.check_installation()
        self._is_enable_microphone_only_btn_enabled = True
        self._is_enable_microphone_and_camera_btn_enabled = True
        self._is_open_browser_btn_enabled = True

        self._access_code = ""
        self._rust_id = "Nenájdené"
        self._username = "Nenájdené"

        self.app_installation_thread = None
        self.app_installation_worker = None

        self.app_start_thread = None
        self.app_start_worker = None

        self.app_service_thread = None
        self.app_service_worker = None

        self.app_websocket_thread = None
        self.app_websocket_worker = None

        self.app_rust_id_thread = None
        self.app_rust_id_worker = None

        self.microphone_only_thread = None
        self.microphone_only_worker = None

        self.microphone_and_camera_thread = None
        self.microphone_and_camera_worker = None

        self.open_browser_thread = None
        self.open_browser_worker = None

        # Cross-thread communication
        self.sendMessageRequested = Signal(str)

        # QTimer - Run Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.setTime)
        self.timer.start(1000)

        self.app_init()

    @Property(int, notify=progressChanged)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if self._progress != value:
            self._progress = value
            self.progressChanged.emit(value)

    @Property(str, notify=rustIdChanged)
    def rust_id(self):
        return self._rust_id

    @rust_id.setter
    def rust_id(self, id):
        if self._rust_id != id:
            self._rust_id = id
            self.rustIdChanged.emit(id)

    @Property(str, notify=accessCodeChanged)
    def access_code(self):
        return self._access_code

    @access_code.setter
    def access_code(self, code):
        if self._access_code != code:
            self._access_code = code
            self.accessCodeChanged.emit(code)

    @Property(str, notify=usernameChanged)
    def username(self):
        return self._username

    @username.setter
    def username(self, name):
        if self._username != name:
            self._username = name
            self.usernameChanged.emit(name)

    @Property(bool, notify=appInstallBtnEnabledChanged)
    def is_app_install_btn_enabled(self):
        return self._is_app_install_btn_enabled

    @is_app_install_btn_enabled.setter
    def is_app_install_btn_enabled(self, is_running):
        if self._is_app_install_btn_enabled != is_running:
            self._is_app_install_btn_enabled = is_running
            self.appInstallBtnEnabledChanged.emit(is_running)

    @Property(bool, notify=appStartBtnEnabledChanged)
    def is_app_start_btn_enabled(self):
        return self._is_app_start_btn_enabled

    @is_app_start_btn_enabled.setter
    def is_app_start_btn_enabled(self, is_enabled):
        if self._is_app_start_btn_enabled != is_enabled:
            # check also if app is installed before allowing
            status = is_enabled if self.check_installation() else False
            self._is_app_start_btn_enabled = status
            self.appStartBtnEnabledChanged.emit(status)

    @Property(bool, notify=appServiceBtnEnabledChanged)
    def is_app_service_btn_enabled(self):
        return self._is_app_service_btn_enabled

    @is_app_service_btn_enabled.setter
    def is_app_service_btn_enabled(self, status):
        if self._is_app_service_btn_enabled != status:
            self._is_app_service_btn_enabled = status
            self.appServiceBtnEnabledChanged.emit(status)

    @Property(bool, notify=appRustIdBtnEnabledChanged)
    def is_app_rust_id_btn_enabled(self):
        return self._is_app_rust_id_btn_enabled

    @is_app_rust_id_btn_enabled.setter
    def is_app_rust_id_btn_enabled(self, is_enabled):
        if self._is_app_rust_id_btn_enabled != is_enabled:
            self._is_app_rust_id_btn_enabled = is_enabled
            self.appRustIdBtnEnabledChanged.emit(is_enabled)

    @Property(bool, notify=enableMicrophoneOnlyBtnEnabledChanged)
    def is_enable_microphone_only_btn_enabled(self):
        return self._is_enable_microphone_only_btn_enabled

    @is_enable_microphone_only_btn_enabled.setter
    def is_enable_microphone_only_btn_enabled(self, is_enabled):
        if self._is_enable_microphone_only_btn_enabled != is_enabled:
            self._is_enable_microphone_only_btn_enabled = is_enabled
            self.enableMicrophoneOnlyBtnEnabledChanged.emit(is_enabled)

    @Property(bool, notify=enableMicrophoneAndCameraBtnEnabledChanged)
    def is_enable_microphone_and_camera_btn_enabled(self):
        return self._is_enable_microphone_and_camera_btn_enabled

    @is_enable_microphone_and_camera_btn_enabled.setter
    def is_enable_microphone_and_camera_btn_enabled(self, is_enabled):
        if self._is_enable_microphone_and_camera_btn_enabled != is_enabled:
            self._is_enable_microphone_and_camera_btn_enabled = is_enabled
            self.enableMicrophoneAndCameraBtnEnabledChanged.emit(is_enabled)

    @Property(bool, notify=openBrowserBtnEnabledChanged)
    def is_open_browser_btn_enabled(self):
        return self._is_open_browser_btn_enabled

    @is_open_browser_btn_enabled.setter
    def is_open_browser_btn_enabled(self, is_enabled):
        if self._is_open_browser_btn_enabled != is_enabled:
            self._is_open_browser_btn_enabled = is_enabled
            self.openBrowserBtnEnabledChanged.emit(is_enabled)

    @Property(str, notify=appInstallationStatusChanged)
    def app_installation_status(self):
        return self._app_installation_status

    @app_installation_status.setter
    def app_installation_status(self, status):
        if self._app_installation_status != status:
            self._app_installation_status = status
            self.appInstallationStatusChanged.emit(status)

    @Property(str, notify=appServiceStatusChanged)
    def app_service_status(self):
        return self._app_service_status

    @app_service_status.setter
    def app_service_status(self, status):
        if self._app_service_status != status:
            self._app_service_status = status
            self.appServiceStatusChanged.emit(status)

    @Property(str, notify=permissionStatusChanged)
    def permission_status(self):
        return self._permission_status

    @permission_status.setter
    def permission_status(self, status):
        if self._permission_status != status:
            self._permission_status = status
            self.permissionStatusChanged.emit(status)

    @Property(str, notify=appWebsocketStatusChanged)
    def app_websocket_status(self):
        return self._app_websocket_status

    @app_websocket_status.setter
    def app_websocket_status(self, status):
        if self._app_websocket_status != status:
            self._app_websocket_status = status
            self.appWebsocketStatusChanged.emit(status)

    @Property(str, notify=obsInstallationStatusChanged)
    def obs_installation_status(self):
        return self._obs_installation_status

    @obs_installation_status.setter
    def obs_installation_status(self, status):
        if self._obs_installation_status != status:
            self._obs_installation_status = status
            self.obsInstallationStatusChanged.emit(status)

    @Property(str, notify=recordingStatusChanged)
    def recording_status(self):
        return self._recording_status

    @recording_status.setter
    def recording_status(self, status):
        if self._recording_status != status:
            self._recording_status = status
            self.recordingStatusChanged.emit(status)

    @Slot(str)
    def add_log(self, log):
        """adds a new log to UI"""
        self.newLogAdded.emit(log)

    @Slot()
    def install_or_uninstall(self):
        """dynamically installs or uninstalls Macrosoft RustDesk based on the current status"""

        if self.app_installation_thread and self.app_installation_thread.isRunning():
            self.app_installation_thread.quit()
            self.app_installation_thread.wait()

        self.app_installation_thread = QThread()
        self.app_installation_worker = AppInstallationWorker()
        self.app_installation_worker.moveToThread(self.app_installation_thread)

        self.app_installation_thread.started.connect(self.app_installation_worker.handle_install)

        self.app_installation_worker.progress_changed.connect(self.update_progress)
        self.app_installation_worker.log.connect(self.add_log)
        self.app_installation_worker.finished.connect(self.on_installation_finished)
        # self.worker.finished.connect(self.install_thread.quit)
        # self.install_thread.finished.connect(self.install_thread.deleteLater)

        # Start the thread
        self.is_app_install_btn_enabled = False
        self.is_app_start_btn_enabled = False
        self.is_app_service_btn_enabled = False
        self.is_app_rust_id_btn_enabled = False
        self.app_installation_thread.start()

    @Slot()
    def start_app(self):
        """open Macrosoft RustDesk application"""
        if self.app_start_thread and self.app_start_thread.isRunning():
            self.app_start_thread.quit()
            self.app_start_thread.wait()

        self.app_start_thread = QThread()
        self.app_start_worker = StartAppWorker()
        self.app_start_worker.moveToThread(self.app_start_thread)

        self.app_start_thread.started.connect(self.app_start_worker.start_macrosoftconnect)

        self.app_start_worker.progress_changed.connect(self.update_progress)
        self.app_start_worker.log.connect(self.add_log)
        self.app_start_worker.finished.connect(self.on_start_app_finished)

        # Start the thread
        self.is_app_start_btn_enabled = False
        self.app_start_thread.start()

    @Slot()
    def get_rustid(self):
        """finds the apps rust id"""
        if self.app_rust_id_thread and self.app_rust_id_thread.isRunning():
            self.app_rust_id_thread.quit()
            self.app_rust_id_thread.wait()

        self.app_rust_id_thread = QThread()
        self.app_rust_id_worker = UserInfoWorker()
        self.app_rust_id_worker.moveToThread(self.app_rust_id_thread)

        self.app_rust_id_thread.started.connect(self.app_rust_id_worker.get_rustdesk_id)

        self.app_rust_id_worker.progress_changed.connect(self.update_progress)
        self.app_rust_id_worker.log.connect(self.add_log)
        self.app_rust_id_worker.finished.connect(self.on_get_rustid_finished)

        # Start the thread
        self.is_app_rust_id_btn_enabled = False
        self.app_rust_id_thread.start()


    @Slot()
    def toggle_service(self):
        """turns on/off Macrosoft Rustdesk service"""
        if self.app_service_thread and self.app_service_thread.isRunning():
            self.app_service_thread.quit()
            self.app_service_thread.wait()

        self.app_service_thread = QThread()
        self.app_service_worker = AppServiceWorker()
        self.app_service_worker.moveToThread(self.app_service_thread)

        if self.is_service_on():
            self.app_service_thread.started.connect(self.app_service_worker.stop_service)
        else:
            self.app_service_thread.started.connect(self.app_service_worker.start_service)

        self.app_service_worker.progress_changed.connect(self.update_progress)
        self.app_service_worker.log.connect(self.add_log)
        self.app_service_worker.finished.connect(self.on_toggle_service_finished)

        # self.is_app_install_btn_enabled = True
        self.is_app_service_btn_enabled = False
        self.app_service_thread.start()

    @Slot()
    def open_webpage(self):
        """opens Macrosoft website in user's browser"""
        if self.open_browser_thread and self.open_browser_thread.isRunning():
            self.open_browser_thread.quit()
            self.open_browser_thread.wait()

        self.open_browser_thread = QThread()
        self.open_browser_worker = OpenBrowserWorker()
        self.open_browser_worker.moveToThread(self.open_browser_thread)

        self.open_browser_thread.started.connect(self.open_browser_worker.open_browser)

        self.open_browser_worker.progress_changed.connect(self.update_progress)
        self.open_browser_worker.log.connect(self.add_log)
        self.open_browser_worker.finished.connect(self.on_open_webpage_finished)

        self.is_open_browser_btn_enabled = False
        self.open_browser_thread.start()


    @Slot()
    def enable_microphone_only(self):
        """changes user devices settings to enable mic access"""
        if self.microphone_only_thread and self.microphone_only_thread.isRunning():
            self.microphone_only_thread.quit()
            self.microphone_only_thread.wait()

        self.microphone_only_thread = QThread()
        self.microphone_only_worker = PermissionWorker()
        self.microphone_only_worker.moveToThread(self.microphone_only_thread)

        self.microphone_only_thread.started.connect(self.microphone_only_worker.set_microphone_access_only)

        self.microphone_only_worker.progress_changed.connect(self.update_progress)
        self.microphone_only_worker.log.connect(self.add_log)
        self.microphone_only_worker.finished.connect(self.on_enable_microphone_only_finished)

        self.is_enable_microphone_only_btn_enabled = False
        self.is_enable_microphone_and_camera_btn_enabled = False
        self.microphone_only_thread.start()


    @Slot()
    def enable_microphone_and_camera(self):
        """changes user devices settings to enable mic and camera access"""
        if self.microphone_and_camera_thread and self.microphone_and_camera_thread.isRunning():
            self.microphone_and_camera_thread.quit()
            self.microphone_and_camera_thread.wait()

        self.microphone_and_camera_thread = QThread()
        self.microphone_and_camera_worker = PermissionWorker()
        self.microphone_and_camera_worker.moveToThread(self.microphone_and_camera_thread)

        self.microphone_and_camera_thread.started.connect(
            self.microphone_and_camera_worker.set_microphone_and_camera_access_only
        )

        self.microphone_and_camera_worker.progress_changed.connect(self.update_progress)
        self.microphone_and_camera_worker.log.connect(self.add_log)
        self.microphone_and_camera_worker.finished.connect(self.on_enable_microphone_and_camera_finished)

        self.is_enable_microphone_only_btn_enabled = False
        self.is_enable_microphone_and_camera_btn_enabled = False
        self.microphone_and_camera_thread.start()

    @Slot()
    def check_installation(self):
        """Check if the application is installed and update the UI accordingly."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"
        if os.path.exists(app_path):
            return True

    @Slot(int)
    def update_progress(self, value):
        self.progress = value

    @Slot()
    def app_init(self):

        self.is_app_install_btn_enabled = True

        script_name = os.path.basename(sys.argv[0])
        code = get_access_code(script_name)
        rustdesk_id = ""
        is_rust_id_reported = False

        if self.check_installation():
            self.app_installation_status = "enabled"

            # get rust_id
            try:
                max_attempts = 3
                app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

                result = subprocess.run(
                    [app_path, "--get-id"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                rustdesk_id = result.stdout.strip() if result.stdout else ""

                self.rust_id = rustdesk_id
                self.access_code = code

                # report rustdesk
                if code:
                    url = f"https://online.macrosoft.sk/rustdesk/?access={code}&rustdesk={rustdesk_id}"
                    attempt = 0
                    while attempt < max_attempts:
                        attempt += 1
                        try:
                            with urllib.request.urlopen(url) as response:
                                if response.status != 200 and attempt < max_attempts:
                                    time.sleep(1)
                                else:
                                    is_rust_id_reported = True
                        except Exception as e:
                            pass
            except Exception as e:
                pass

        else:
            self.app_installation_status = "disabled"

        # get username
        self.username = get_full_name(code)

        # check permissions
        registry_permission = RegistryPermissionManager()
        browser_permission = BrowserPermissionManager()
        microphone_allowed = registry_permission.is_microphone_allowed()
        webcam_allowed = registry_permission.is_webcam_allowed()
        browser_permissions_allowed = (
            browser_permission.is_browser_permissions_allowed()
        )

        self.add_log(f"\tmicrophone_allowed: {microphone_allowed}")
        self.add_log(f"\twebcam_allowed: {webcam_allowed}")
        self.add_log(f"\tbrowser_permissions_allowed: {browser_permissions_allowed}")

        if microphone_allowed and webcam_allowed and browser_permissions_allowed:
            self.permission_status = "enabled"
        elif microphone_allowed:
            self.permission_status = "checking"
        else:
            self.permission_status = "disabled"

        # OBS setup
        self.obs_installation_status = "enabled" if is_obs_installed() else "disabled"


        # setup websocket
        self.setup_websockets(code)


        print("\n\n\nApplication init:")
        print(f"\tcode: {code}")
        print(f"\tusername: {self.username}")
        print(f"\trust_id: {rustdesk_id}")
        print(f"\tis_rust_id_reported: {is_rust_id_reported}")
        print(f"\twebsocket status: {self._app_websocket_status}")
        print(f"\tOBS status: {self._obs_installation_status}")
        print("\n\n\n")

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

            # self.sendMessageRequested.connect(self.app_websocket_worker.send_message)
            self.app_websocket_thread.start()

    @Slot(bool)
    def websocket_on_change_status(self, status):
        self.add_log(f"websocket_on_change_status: {status}")
        if status:
            self.app_websocket_status = "enabled"
        else:
            self.app_websocket_status = "disabled"

    @Slot(str)
    def websocket_on_message_received(self, message):
        self.add_log(message)

    @Slot(str)
    def websocket_on_error(self, message):
        self.add_log(message)

    @Slot()
    def refresh_app_status(self):
        """refreshes whole app status"""
        self.is_app_install_btn_enabled = True
        self.is_app_start_btn_enabled = True
        self.is_app_service_btn_enabled = True

        if self.check_installation():
            self.app_installation_status = "enabled"
            if self.is_service_on():
                self.app_service_status = "enabled"
            else:
                self.app_service_status = "disabled"
        else:
            self.app_installation_status = "disabled"
            self.is_app_start_btn_enabled = False
            self.is_app_service_btn_enabled = False

    def is_service_on(self):
        """checks if Macrosoft rustdesk service is running"""
        return is_service_running("MacrosoftConnectQuickSupport")



    @Slot(dict)
    def on_installation_finished(self, result_data):
        """updates app state, cleans up, releases resources"""
        print(f"\n\n\ton_installation_finished called ...\n\n")
        print(f"\n\n\n\t{result_data}\n\n\n")

        if result_data.get("app_installed"):
            self.app_installation_status = "enabled"

            if result_data.get("app_service_on"):
                self.app_service_status = "enabled"

            if result_data.get("rust_id"):
                self.rust_id = result_data.get("rust_id")

            self.is_app_start_btn_enabled = True
            self.is_app_service_btn_enabled = True
            self.is_app_rust_id_btn_enabled = True
        else:
            self.app_installation_status = "disabled"
            self.app_service_status = "disabled"
            self.rust_id = result_data.get("rust_id")
            self.is_app_start_btn_enabled = False
            self.is_app_service_btn_enabled = False
            self.is_app_rust_id_btn_enabled = False

        self.update_progress(0)
        self.is_app_install_btn_enabled = True

        self.app_installation_thread.quit()
        self.app_installation_thread.wait()
        self.app_installation_thread.deleteLater()
        self.app_installation_thread = None

        self.app_installation_worker.deleteLater()
        self.app_installation_worker = None

    @Slot()
    def on_start_app_finished(self):
        """cleans up when start app button is clicked"""
        print(f"\n\n\ton_start_app_finished called ...\n\n")

        self.app_start_thread.quit()
        self.app_start_thread.wait()
        self.app_start_thread.deleteLater()
        self.app_start_thread = None

        self.app_start_worker.deleteLater()
        self.app_start_worker = None
        self.is_app_start_btn_enabled = self.check_installation()

    @Slot()
    def on_get_rustid_finished(self):
        """cleans up when start app button is clicked"""
        print(f"\n\n\ton_get_rustid_finished called ...\n\n")

        self.app_rust_id_thread.quit()
        self.app_rust_id_thread.wait()
        self.app_rust_id_thread.deleteLater()
        self.app_rust_id_thread = None

        self.app_rust_id_worker.deleteLater()
        self.app_rust_id_worker = None
        self.is_app_rust_id_btn_enabled = True

    @Slot()
    def on_toggle_service_finished(self):
        """cleans up when start service button is clicked"""
        print(f"\n\n\ton_toggle_service_finished called ...\n\n")

        self.app_service_thread.quit()
        self.app_service_thread.wait()
        self.app_service_thread.deleteLater()
        self.app_service_thread = None

        self.app_service_worker.deleteLater()
        self.app_service_worker = None
        # self.is_app_start_enabled = self.check_installation()

        self.app_service_status = "enabled" if self.check_installation() and self.is_service_on() else "disabled"

        self.is_app_service_btn_enabled = True

    @Slot()
    def on_open_webpage_finished(self):

        self.open_browser_thread.quit()
        self.open_browser_thread.wait()
        self.open_browser_thread.deleteLater()
        self.open_browser_thread = None

        self.open_browser_worker.deleteLater()
        self.open_browser_worker = None

        self.is_open_browser_btn_enabled = True

    @Slot(dict)
    def on_enable_microphone_only_finished(self, result):
        print(f"\n\n\non_enable_microphone_only_finished")
        print(f"\t{result}")

        self.update_permission_status(result)

        print(f"\n\tpermission_status: {self.permission_status}\n\n")

        self.microphone_only_thread.quit()
        self.microphone_only_thread.wait()
        self.microphone_only_thread.deleteLater()
        self.microphone_only_thread = None

        self.microphone_only_worker.deleteLater()
        self.microphone_only_worker = None

        self.is_enable_microphone_only_btn_enabled = True
        self.is_enable_microphone_and_camera_btn_enabled = True

    @Slot(dict)
    def on_enable_microphone_and_camera_finished(self, result):
        print(f"\n\n\non_enable_microphone_and_camera_finished")
        print(f"\t{result}")
        self.update_permission_status(result)
        print(f"\n\tpermission_status: {self.permission_status}\n\n")

        self.microphone_and_camera_thread.quit()
        self.microphone_and_camera_thread.wait()
        self.microphone_and_camera_thread.deleteLater()
        self.microphone_and_camera_thread = None

        self.microphone_and_camera_worker.deleteLater()
        self.microphone_and_camera_worker = None

        self.is_enable_microphone_only_btn_enabled = True
        self.is_enable_microphone_and_camera_btn_enabled = True

    def update_permission_status(self, result):
        """updates permission status based on the given data"""
        webcam_allowed = result.get("is_webcam_allowed")
        microphone_allowed = result.get("is_microphone_allowed")
        browser_permissions_allowed = result.get("is_browser_permissions_allowed")

        if microphone_allowed and webcam_allowed and browser_permissions_allowed:
            self.permission_status = "enabled"
        elif microphone_allowed:
            self.permission_status = "checking"
        else:
            self.permission_status = "disabled"

    @Slot(str)
    def openFile(self, filePath):
        try:
            with open(QUrl(filePath).toLocalFile(), encoding="utf-8") as file:
                text = file.read()
                print(text)
                self.readText.emit(text)
        except Exception as e:
            print(f"Error opening file: {e}")

    # Read Text
    @Slot(str)
    def getTextField(self, text):
        self.textField = text

    # Write File
    @Slot(str)
    def writeFile(self, filePath):
        try:
            with open(QUrl(filePath).toLocalFile(), "w", encoding="utf-8") as file:
                file.write(self.textField)
                print(f"Written to file: {self.textField}")
        except Exception as e:
            print(f"Error writing file: {e}")

    # Show / Hide Rectangle
    @Slot(bool)
    def showHideRectangle(self, isChecked):
        print("Is rectangle visible:", isChecked)
        self.isVisible.emit(isChecked)

    # Set Timer Function
    def setTime(self):
        now = datetime.datetime.now()
        formatDate = now.strftime("Now is %H:%M:%S %p of %Y/%m/%d")
        # print(formatDate)
        self.printTime.emit(formatDate)

    # Function Set Name To Label
    @Slot(str)
    def welcomeText(self, name):
        self.setName.emit(f"Welcome, {name}")

    @Slot()
    def start_action(self):
        print("\n\tStart Action\n")

    @Slot(str)
    def new_signal(self, text):
        print(f"\n\tnew_signal\n")
        # for i in range(10):
        #     time.sleep(1)
        import random
        i = random.randint(1, 10)
        self.addCounter.emit(f"Counter: {i}")

    def cleanup(self):
        """handles threads, worker cleanup"""
        print(f"\n\n\nbackend.cleanup\n\n")
        # time.sleep(5)
        app_threads = [self.app_websocket_thread]
        app_workers = [self.app_websocket_worker]
        for thread in app_threads:
            if thread and thread.isRunning():
                thread.quit()
                thread.wait()
                thread.deleteLater()

        for worker in app_workers:
            if worker:
                worker.deleteLater()

        # handle websocket
        # self.worker.disconnect()
        # self.thread.quit()
        # self.thread.wait()


if __name__ == "__main__":
    # 1. Set the desired Qt Quick Controls style before creating the application
    QQuickStyle.setStyle("Fusion")  # Options: "Basic", "Fusion", "Material", "Imagine", etc.

    # 2. Initialize the application
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # 3. Get Context
    backend = MainWindow()

    engine.rootContext().setContextProperty("backend", backend)

    # 4. Set App Extra Info
    app.setOrganizationName("Wanderson M. Pimenta")
    app.setOrganizationDomain("N/A")

    # 5. Load QML File
    qml_file = os.path.join(os.path.dirname(__file__), "qml/main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    app.aboutToQuit.connect(backend.cleanup)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())