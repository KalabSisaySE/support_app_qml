"""Workers that start the application and toggle its Windows service."""

import os
import subprocess

from PySide6.QtCore import QObject, Signal, Slot

from support_app.app_config import NAME
from support_app.macrosoft_connect import (
    app_executable_path,
    create_service_manager,
)
from support_app.utils import check_installation, is_app_running, is_service_running


class StartAppWorker(QObject):
    """manages macrosoft rustdesk starting"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.process_name = "start_app"

    @Slot()
    def start_macrosoftconnect(self):
        """Start the Macrosoft Connect application."""
        app_path = app_executable_path()

        if not os.path.exists(app_path):
            self.log.emit(
                f"{NAME} nie je nainštalovaný, prosím kliknite na Inštalovať {NAME}"
            )

        try:
            subprocess.Popen(
                [app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self.log.emit(f"{NAME} bol spustený.")
        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť {NAME}: {e}")

        self.finished.emit()


class AppServiceWorker(QObject):
    """manages macrosoft rustdesk service"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal()
    manager = create_service_manager()

    def __init__(self):
        super().__init__()
        self.process_name = "app_service"

    def start_macrosoftconnect(self):
        """Start the Macrosoft Connect application."""
        app_path = app_executable_path()

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
        """Start the Macrosoft Connect service."""
        try:
            if not check_installation():
                self.log.emit("Aplikácia nie je nainštalovaná. Najprv nainštalujte aplikáciu...")
                self.finished.emit()
                return

            if not is_app_running():
                self.log.emit("Aplikácia nie je spustená. Spúšťa sa aplikácia...")
                if not self.start_macrosoftconnect():
                    self.log.emit("Nepodarilo sa automaticky spustiť aplikáciu...")
                    self.finished.emit()
                    return

            if not self.manager.is_service_installed():
                self.log.emit("Vytváranie služby...")
                self.manager.create_service()

            self.manager.start_service()
            self.log.emit(f"Služba {NAME} je spustená.")

        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť službu {NAME}., {e}")

        self.finished.emit()

    @Slot()
    def stop_service(self):
        """Stop the Macrosoft Connect service."""
        try:
            if is_service_running(f"{NAME}"):
                if is_app_running():
                    self.manager.stop_service()
                    self.log.emit(f"Služba {NAME} bola zastavená.")

                else:
                    self.log.emit("Služba nie je spustená...")
            else:
                self.log.emit("Služba nie je spustená...")
        except Exception as e:
            self.log.emit(
                f"Nepodarilo sa zastaviť službu {NAME}. {e}"
            )

        self.finished.emit()
