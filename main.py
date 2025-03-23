# This Python file uses the following encoding: utf-8
import time
import sys
import os
import datetime
import urllib.request
import subprocess

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal, QTimer, QUrl, Property, QThread
from PySide6.QtQuickControls2 import QQuickStyle  # Import QQuickStyle



class MainWindow(QObject):
    # Signal Set Name
    setName = Signal(str)
    addCounter = Signal(str)
    printTime = Signal(str)
    isVisible = Signal(bool)
    readText = Signal(str)



    # custom signals
    progressChanged = Signal(int)
    rustDeskStatusChanged = Signal(str)
    taskStarted = Signal()
    taskFinished = Signal()

    textField = ""

    def __init__(self):
        super().__init__()  # Prefer super() over direct QObject initialization

        # values
        self._progress = 0
        self.thread = None
        self.worker = None

        # QTimer - Run Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.setTime)
        self.timer.start(1000)

    @Property(int, notify=progressChanged)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        if self._progress != value:
            self._progress = value
            self.progressChanged.emit(value)

    @Slot()
    def install_and_run_macrosoft_connect(self):
        """installs and sets up macrosoft connect in a thread"""

        # Clean up any previous thread
        if self.thread is not None and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        # Setup new thread and worker
        self.thread = QThread()
        self.worker = InstallMacrosoftConnectWorker()
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run_task)
        self.worker.progress_changed.connect(self.update_progress)
        self.worker.finished.connect(self.on_task_finished)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()
        self.taskStarted.emit()


    def check_installation(self):
        """Check if the application is installed and update the UI accordingly."""
        app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"

        try:
            self.update_recording_status()

            if os.path.exists(app_path):
                pass
        except Exception as e:
            self.log_message(f"Error during installation check: {e}")


    @Slot(int)
    def update_progress(self, value):
        self.progress = value

    @Slot()
    def on_task_finished(self):
        self.taskFinished.emit()
        self.worker.deleteLater()
        self.worker = None

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


class InstallMacrosoftConnectWorker(QObject):
    progress_changed = Signal(int)
    finished = Signal()

    @Slot()
    def run_task(self):
        """Long-running task with progress updates"""
        # signals.log.emit("Začínam proces inštalácie...")

        download_url = (
            "https://online.macrosoft.sk/static/ztpt/output/downloads/macrosoftconnectquicksupport.exe"
        )
        # (__file__)
        new_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        temp_dir = os.environ.get("TEMP", new_path)
        temp_dir = new_path

        print(f"\n\n\t\tnew_path: {new_path}")
        print(f"\t\ttemp_dir: {temp_dir}\n\n")

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
            # signals.log.emit(f"Chyba pri sťahovaní súboru: {e}")
            # self.install_button.setEnabled(True)
            return

        try:
            # Prepare startup info to hide cmd window
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
            # signals.log.emit(f"Chyba počas inštalácie: {e}")
            # self.install_button.setEnabled(True)
            return

        self.finished.emit()





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