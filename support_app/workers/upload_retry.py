"""Worker that retries queued recording-upload triggers on startup."""

from PySide6.QtCore import QObject, Signal, Slot

from support_app.logging_setup import get_logger
from support_app.upload_queue import flush_pending_uploads

logger = get_logger(__name__)


class UploadRetryWorker(QObject):
    """Drain the persisted upload queue without blocking the GUI thread."""

    finished = Signal(dict)

    @Slot()
    def run(self):
        try:
            sent, remaining = flush_pending_uploads()
        except Exception as e:
            logger.exception("Upload retry worker failed")
            self.finished.emit({"sent": 0, "remaining": -1, "error": str(e)})
            return

        self.finished.emit({"sent": sent, "remaining": remaining})
