"""Build a support diagnostics archive for troubleshooting."""

from __future__ import annotations

import datetime
import os
import zipfile
from typing import Iterable, Mapping

SUMMARY_NAME = "summary.txt"


def build_summary(entries: Mapping[str, object]) -> str:
    """Render a plain-text summary from ordered key/value entries."""
    lines = [f"{key}: {value}" for key, value in entries.items()]
    return "\n".join(lines) + "\n"


def create_diagnostics_archive(
    destination_dir: str,
    summary: str,
    log_files: Iterable[str] = (),
) -> str:
    """Write a timestamped zip containing the summary and available logs."""
    os.makedirs(destination_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_path = os.path.join(destination_dir, f"support-diagnostics-{timestamp}.zip")

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(SUMMARY_NAME, summary)
        for path in log_files:
            if os.path.isfile(path):
                archive.write(path, arcname=os.path.basename(path))

    return archive_path
