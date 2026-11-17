"""Worker that opens the Macrosoft web page in the default browser."""

from PySide6.QtCore import QObject, Signal, Slot

from support_app.app_config import get_access_code
from support_app.utils import open_website


class OpenBrowserWorker(QObject):
    """manages opening/closing a browser"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.access = get_access_code()
        self.process_name = "open_browser"

    @Slot()
    def open_browser(self):
        """Open the default page in user's default browser."""
        try:
            self.log.emit("Otváram webovú stránku...")
            if open_website(self.access):
                self.log.emit("Webová stránka otvorená.")
            else:
                self.log.emit("Nepodarilo sa otvoriť webovú stránku.")

        except Exception as e:
            self.log.emit("Nepodarilo sa otvoriť webovú stránku.")

        self.finished.emit()
