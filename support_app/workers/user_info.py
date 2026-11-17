"""Worker that resolves and reports the Macrosoft Connect RustDesk id."""

import os
import subprocess
import time
import urllib.request

from PySide6.QtCore import QObject, Signal, Slot

from support_app.app_config import (
    EXE_NAME,
    NAME,
    RUSTDESK_REPORT_URL,
    get_access_code,
    get_cloudflare_headers,
)
from support_app.utils import get_full_name


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
        self.app_path = fr"C:\Program Files\{NAME}\{EXE_NAME}.exe"
        self.process_name = "user_info"

    @Slot()
    def get_rustdesk_id(self):
        """Retrieve the RustDesk ID."""
        if not os.path.exists(self.app_path):
            self.log.emit(
                f"{NAME} nie je nainštalovaný, prosím kliknite na Inštalovať {NAME}"
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
            url = f"{RUSTDESK_REPORT_URL}?access={self.access}&rustdesk={rustdesk_id}"
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                try:
                    req = urllib.request.Request(url, headers=get_cloudflare_headers())
                    with urllib.request.urlopen(req) as response:
                        if response.status == 200:
                            self.log.emit("ID bolo úspešne odoslané.")
                            break
                        else:
                            self.log.emit(f"Odozva servera: {response.status}")
                            if attempt < max_attempts:
                                time.sleep(1)
                except Exception as e:
                    self.log.emit(f"Nepodarilo sa odoslať ID: {e}")

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
