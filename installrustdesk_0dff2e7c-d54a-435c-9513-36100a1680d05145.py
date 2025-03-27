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
from PySide6.QtCore import QObject, Slot, Signal, QTimer, QUrl, Property, QThread
from PySide6.QtQuickControls2 import QQuickStyle


from support_app.utils import is_app_running, is_service_running, get_access_code, get_full_name, check_installation
from support_app.rust_service_manager import ServiceManager


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
    appInstallationRunning = Signal(bool)
    appStartBtnEnabledChanged = Signal(bool)
    appServiceStatusChanged = Signal(str)
    appServiceButtonStatusChanged = Signal(bool)
    appRustIdBtnEnabledChanged = Signal(bool)
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

        self._is_app_install_btn_enabled = False
        self._is_app_start_btn_enabled = self.check_installation()
        self._is_app_service_btn_enabled = self.check_installation()
        self._is_app_rust_id_btn_enabled = self.check_installation()

        self._access_code = ""
        self._rust_id = "Nenájdené"
        self._username = "Nenájdené"

        self.app_installation_thread = None
        self.app_installation_worker = None

        self.app_start_thread = None
        self.app_start_worker = None

        self.app_service_thread = None
        self.app_service_worker = None

        self.app_rust_id_thread = None
        self.app_rust_id_worker = None

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

    @Property(bool, notify=appInstallationRunning)
    def is_app_install_btn_enabled(self):
        return self._is_app_install_btn_enabled

    @is_app_install_btn_enabled.setter
    def is_app_install_btn_enabled(self, is_running):
        if self._is_app_install_btn_enabled != is_running:
            self._is_app_install_btn_enabled = is_running
            self.appInstallationRunning.emit(is_running)

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

    @Property(bool, notify=appServiceButtonStatusChanged)
    def is_app_service_btn_enabled(self):
        return self._is_app_service_btn_enabled

    @is_app_service_btn_enabled.setter
    def is_app_service_btn_enabled(self, status):
        if self._is_app_service_btn_enabled != status:
            self._is_app_service_btn_enabled = status
            self.appServiceButtonStatusChanged.emit(status)

    @Property(bool, notify=appRustIdBtnEnabledChanged)
    def is_app_rust_id_btn_enabled(self):
        return self._is_app_rust_id_btn_enabled

    @is_app_rust_id_btn_enabled.setter
    def is_app_rust_id_btn_enabled(self, is_enabled):
        if self._is_app_rust_id_btn_enabled != is_enabled:
            self._is_app_rust_id_btn_enabled = is_enabled
            self.appRustIdBtnEnabledChanged.emit(is_enabled)

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

        print("\n\n\nApplication init:")
        print(f"\tcode: {code}")
        print(f"\tusername: {self.username}")
        print(f"\trust_id: {rustdesk_id}")
        print(f"\tis_rust_id_reported: {is_rust_id_reported}")
        print("\n\n\n")

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
            self.is_app_start_btn_enabled = True
            self.is_app_service_btn_enabled = True
        else:
            self.app_installation_status = "disabled"
            self.app_service_status = "disabled"
            self.rust_id = result_data.get("rust_id")
            self.is_app_start_btn_enabled = False
            self.is_app_service_btn_enabled = False

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


    # Open File
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





if __name__ == "__main__":
    # 1. Set the desired Qt Quick Controls style before creating the application
    QQuickStyle.setStyle("Fusion")  # Options: "Basic", "Fusion", "Material", "Imagine", etc.

    # 2. Initialize the application
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # 3. Get Context
    main = MainWindow()

    engine.rootContext().setContextProperty("backend", main)

    # 4. Set App Extra Info
    app.setOrganizationName("Wanderson M. Pimenta")
    app.setOrganizationDomain("N/A")

    # 5. Load QML File
    qml_file = os.path.join(os.path.dirname(__file__), "qml/main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())