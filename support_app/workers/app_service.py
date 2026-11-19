"""Workers that start the application and toggle its Windows service."""

import os
import subprocess

from PySide6.QtCore import QObject, Signal, Slot

from support_app import app_config
from support_app.macrosoft_connect import (
    app_executable_path,
    create_service_manager,
)
from support_app.system_info import check_installation, is_app_running, is_service_running


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
                f"{app_config.NAME} nie je nainštalovaný, prosím kliknite na Inštalovať {app_config.NAME}"
            )

        try:
            subprocess.Popen(
                [app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            self.log.emit(f"{app_config.NAME} bol spustený.")
        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť {app_config.NAME}: {e}")

        self.finished.emit()


class AppServiceWorker(QObject):
    """manages macrosoft rustdesk service"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.manager = create_service_manager()
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
        except Exception:
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
            self.log.emit(f"Služba {app_config.NAME} je spustená.")

        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť službu {app_config.NAME}., {e}")

        self.finished.emit()

    @Slot()
    def stop_service(self):
        """Stop the Macrosoft Connect service."""
        try:
            if is_service_running(f"{app_config.NAME}"):
                if is_app_running():
                    self.manager.stop_service()
                    self.log.emit(f"Služba {app_config.NAME} bola zastavená.")

                else:
                    self.log.emit("Služba nie je spustená...")
            else:
                self.log.emit("Služba nie je spustená...")
        except Exception as e:
            self.log.emit(
                f"Nepodarilo sa zastaviť službu {app_config.NAME}. {e}"
            )

        self.finished.emit()
