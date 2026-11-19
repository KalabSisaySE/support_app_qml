"""Worker that resolves and reports the Macrosoft Connect RustDesk id."""

import os

from PySide6.QtCore import QObject, Signal, Slot

from support_app import app_config
from support_app.app_config import get_access_code
from support_app.macrosoft_connect import (
    app_executable_path,
    query_rustdesk_id,
    report_rustdesk_id,
)
from support_app.macrosoft_api import get_full_name


class UserInfoWorker(QObject):
    """manages macrosoft rustdesk and userinfo"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.result_data = {
            "username": "",
            "rust_id": "Nenájdené"
        }
        self.access = get_access_code()
        self.app_path = app_executable_path()
        self.process_name = "user_info"

    @Slot()
    def get_rustdesk_id(self):
        """Retrieve the RustDesk ID."""
        if not os.path.exists(self.app_path):
            self.log.emit(
                f"{app_config.NAME} nie je nainštalovaný, prosím kliknite na Inštalovať {app_config.NAME}"
            )
            self.finished.emit(self.result_data)

        try:
            rustdesk_id = query_rustdesk_id(self.app_path) or "Nenájdené"

            self.log.emit(f"Vaše ID je: {rustdesk_id}")
            self.report_rustdesk_id(rustdesk_id)
            self.result_data["rust_id"] = rustdesk_id

        except Exception as e:
            self.log.emit(f"Nepodarilo sa získať ID: {e}")

        self.finished.emit(self.result_data)

    def report_rustdesk_id(self, rustdesk_id, max_attempts=3):
        """Report the RustDesk ID to the server."""
        report_rustdesk_id(
            self.access,
            rustdesk_id,
            log=self.log.emit,
            max_attempts=max_attempts,
        )

    @Slot()
    def set_username(self):
        """Fetch and set the user's full name."""
        self.log.emit("Načítavam používateľské meno...")
        full_name = get_full_name(self.access)
        if full_name:
            self.log.emit(f"Úplné meno načítané.: {full_name}")
        else:
            self.log.emit("Nepodarilo sa získať meno z API")

        self.finished.emit()
