"""Windows Authenticode verification for downloaded installers.

Verification is advisory for now: the Macrosoft installer is not guaranteed to
be signed in every distribution channel, so callers log the result and still
run the installer.  OBS releases are signed, so they normally report ``Valid``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass

from support_app.logging_setup import get_logger

logger = get_logger(__name__)

VERIFY_TIMEOUT_SECONDS = 30
_CREATION_FLAGS = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
SIGNATURE_CHECK_SCRIPT = (
    "$sig = Get-AuthenticodeSignature -LiteralPath $env:VERIFY_FILE; "
    "Write-Output $sig.Status"
)


@dataclass(frozen=True)
class SignatureResult:
    """Outcome of an Authenticode check."""

    status: str

    @property
    def is_valid(self) -> bool:
        return self.status == "Valid"


def is_verification_supported() -> bool:
    """Authenticode checks are only available on Windows."""
    return sys.platform == "win32"


def verify_authenticode(path: str) -> SignatureResult | None:
    """Return the Authenticode status of *path*, or None when unavailable."""
    if not os.path.isfile(path) or not is_verification_supported():
        return None

    env = os.environ.copy()
    env["VERIFY_FILE"] = os.path.abspath(path)

    try:
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                SIGNATURE_CHECK_SCRIPT,
            ],
            capture_output=True,
            text=True,
            env=env,
            timeout=VERIFY_TIMEOUT_SECONDS,
            creationflags=_CREATION_FLAGS,
        )
    except Exception as e:
        logger.debug("Could not verify the installer signature: %s", e)
        return None

    if result.returncode != 0:
        logger.debug(
            "Signature check for %s failed (exit %s): %s",
            path, result.returncode, result.stderr.strip(),
        )
        return None

    status = (result.stdout or "").strip() or "Unknown"
    return SignatureResult(status=status)


def log_signature_result(path: str, result: SignatureResult | None) -> None:
    """Write a human-readable verification line to the support log."""
    if result is None:
        logger.warning("Installer signature could not be verified: %s", path)
    elif result.is_valid:
        logger.info("Installer signature is valid: %s", path)
    else:
        logger.warning("Installer signature status is %s: %s", result.status, path)
