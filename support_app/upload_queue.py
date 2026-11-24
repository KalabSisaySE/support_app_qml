"""Persistent queue for recording uploads that failed to trigger."""

from __future__ import annotations

import json
import os
from typing import Callable, Iterable

from support_app import api
from support_app.app_config import OBS_UPLOAD_URL, get_cloudflare_headers
from support_app.logging_setup import get_logger
from support_app.settings import APP_DATA_PATH, write_text_atomic

logger = get_logger(__name__)

QUEUE_FILE_NAME = "pending_uploads.json"


def default_queue_path() -> str:
    return os.path.join(APP_DATA_PATH, QUEUE_FILE_NAME)


def default_sender(payload: dict) -> None:
    """POST one queued upload trigger and raise on an HTTP error."""
    response = api.post(
        OBS_UPLOAD_URL,
        headers=get_cloudflare_headers(),
        json=payload,
    )
    response.raise_for_status()


class UploadQueue:
    """JSON-backed FIFO of upload payloads, drained with a sender callable."""

    def __init__(self, path: str, send: Callable[[dict], None] = default_sender) -> None:
        self.path = path
        self._send = send

    def _load(self) -> list[dict]:
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as e:
            logger.debug("Could not read pending uploads from %s: %s", self.path, e)
            return []

        if not isinstance(data, list):
            logger.warning("Ignoring malformed pending upload queue: %s", self.path)
            return []

        return [item for item in data if isinstance(item, dict)]

    def _save(self, items: Iterable[dict]) -> None:
        write_text_atomic(self.path, json.dumps(list(items), indent=2))

    def pending(self) -> list[dict]:
        return self._load()

    def enqueue(self, payload: dict) -> None:
        items = self._load()
        items.append(payload)
        self._save(items)
        logger.info("Queued recording upload for retry (%d pending).", len(items))

    def flush(self) -> tuple[int, int]:
        """Try to send every queued payload; return (sent, remaining)."""
        items = self._load()
        if not items:
            return 0, 0

        remaining = []
        sent = 0
        for payload in items:
            try:
                self._send(payload)
                sent += 1
            except Exception as e:
                logger.warning("Recording upload retry failed: %s", e)
                remaining.append(payload)

        self._save(remaining)
        return sent, len(remaining)


def enqueue_upload(payload: dict) -> None:
    """Add one upload payload to the default queue."""
    UploadQueue(default_queue_path()).enqueue(payload)


def flush_pending_uploads() -> tuple[int, int]:
    """Retry all queued uploads using the default sender."""
    return UploadQueue(default_queue_path()).flush()
