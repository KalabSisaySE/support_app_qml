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


class AppInstallationWorker(QObject):
    """manages macrosoft rustdesk installation and uninstallation"""
    progress_changed = Signal(int)
    log = Signal(str)
    finished = Signal()

    @Slot()
    def install_app(self):
        """installs and rust Macrosoft RustDesk"""
        self.log.emit("Začínam proces inštalácie...")

        download_url = (
            "https://online.macrosoft.sk/static/ztpt/output/downloads/macrosoftconnectquicksupport.exe"
        )

        new_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        temp_dir = os.environ.get("TEMP", new_path)
        temp_dir = new_path

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
            self.finished.emit()
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
        except Exception as e:
            self.log.emit(f"Chyba počas inštalácie: {e}")
            self.finished.emit()
            return

        self.finished.emit()

    @Slot()
    def uninstall_app(self):
        """uninstalls and rust Macrosoft RustDesk"""

        uninstall_path = os.path.join(
            "C:\\Program Files\\MacrosoftConnectQuickSupport",
            "Uninstall MacrosoftConnectQuickSupport.lnk",
        )

        if not os.path.exists(uninstall_path):
            print("not os.path.exists(uninstall_path)")
            self.log.emit("Odinštalačný súbor nebol nájdený.")
            self.finished.emit()
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
            pass

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
    newLogAdded = Signal(str)

    taskStarted = Signal()
    taskFinished = Signal()

    textField = ""

    def __init__(self):
        super().__init__()  # Prefer super() over direct QObject initialization

        # values
        self._progress = 0
        self._app_installation_status = self.check_installation()
        self._is_app_installation_running = False

        self.app_installation_thread = None
        self.app_installation_worker = None

        # QTimer - Run Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.setTime)
        self.timer.start(1000)

        self.app_status()

    @Property(int, notify=progressChanged)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if self._progress != value:
            self._progress = value
            self.progressChanged.emit(value)

    @Property(bool, notify=appInstallationRunning)
    def is_app_installation_running(self):
        return not self._is_app_installation_running

    @is_app_installation_running.setter
    def is_app_installation_running(self, is_running):
        if self._is_app_installation_running != is_running:
            self._is_app_installation_running = is_running
            self.appInstallationRunning.emit(is_running)

    @Property(str, notify=appInstallationStatusChanged)
    def app_installation_status(self):
        return self._app_installation_status

    @app_installation_status.setter
    def app_installation_status(self, status):
        if self._app_installation_status != status:
            self._app_installation_status = status
            self.appInstallationStatusChanged.emit(status)


    @Slot(str)
    def add_log(self, log):
        """adds a new log to UI"""
        self.newLogAdded.emit(log)

    @Slot()
    def install_or_uninstall(self):
        """dynamically installs or uninstalls Macrosoft RustDesk based on the current status"""

        status = self.app_installation_status

        if self.app_installation_thread and self.app_installation_thread.isRunning():
            self.app_installation_thread.quit()
            self.app_installation_thread.wait()

        self.app_installation_thread = QThread()
        self.app_installation_worker = AppInstallationWorker()
        self.app_installation_worker.moveToThread(self.app_installation_thread)

        if status == "checking" or status == "disabled":
            print(f"\n\n\n\tinstall_macrosoft_connect\n\n")
            self.app_installation_thread.started.connect(self.app_installation_worker.install_app)
        else:
            print(f"\n\n\n\tuninstall_macrosoft_connect\n\n")
            self.app_installation_thread.started.connect(self.app_installation_worker.uninstall_app)


        self.app_installation_worker.progress_changed.connect(self.update_progress)
        self.app_installation_worker.log.connect(self.add_log)
        self.app_installation_worker.finished.connect(self.on_task_finished)
        # self.worker.finished.connect(self.install_thread.quit)
        # self.install_thread.finished.connect(self.install_thread.deleteLater)

        # Start the thread
        self.is_app_installation_running = True
        self.app_installation_thread.start()


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
    def app_status(self):

        self.is_app_installation_running = False

        if self.check_installation():
            self.app_installation_status = "enabled"
        else:
            self.app_installation_status = "disabled"

    @Slot()
    def on_task_finished(self):
        """updates app state, cleans up, releases resources"""
        print(f"\n\n\ton_task_finished called ...\n\n")
        if self.check_installation():
            self.app_installation_status = "enabled"
        else:
            self.app_installation_status = "disabled"



        self.app_installation_thread.quit()
        self.app_installation_thread.wait()
        self.app_installation_thread.deleteLater()
        self.app_installation_thread = None

        self.app_installation_worker.deleteLater()
        self.app_installation_worker = None

        self.is_app_installation_running = False

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

    print(f"\n\n\t\tapp_installation_status: {main.app_installation_status}\n\n")

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