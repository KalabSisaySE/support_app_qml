"""Pre-flight readiness checks before a support/recording session."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from support_app import api, app_config
from support_app.obs_control import is_obs_installed, is_obs_running
from support_app.system_info import check_installation, is_service_running

INTERNET_CHECK_URL = "https://api64.ipify.org?format=text"
INTERNET_TIMEOUT_SECONDS = 5.0


@dataclass(frozen=True)
class CheckResult:
    """One readiness check shown to the user."""

    label: str
    passed: bool


def check_internet() -> bool:
    """Return True when a small public request succeeds."""
    try:
        response = api.get(
            INTERNET_CHECK_URL,
            timeout=INTERNET_TIMEOUT_SECONDS,
            retries=0,
        )
        return bool(response.text)
    except Exception:
        return False


def collect_checks(
    *,
    permission_ok: bool,
    internet_ok: bool,
    websocket_ok: bool | None = None,
) -> list[CheckResult]:
    """Collect all readiness checks relevant for the current user."""
    checks = [
        CheckResult("Macrosoft Connect je nainštalovaný", check_installation()),
        CheckResult(f"Služba {app_config.NAME} beží", is_service_running(app_config.NAME)),
        CheckResult("OBS je nainštalovaný", is_obs_installed()),
        CheckResult("OBS beží", is_obs_running()),
        CheckResult("Povolenia pre mikrofón, kameru a prehliadač", permission_ok),
    ]
    if websocket_ok is not None:
        checks.append(CheckResult("Pripojenie k support WebSocketu", websocket_ok))
    checks.append(CheckResult("Pripojenie na internet", internet_ok))
    return checks


def all_passed(checks: Iterable[CheckResult]) -> bool:
    return all(check.passed for check in checks)


def format_report(checks: Iterable[CheckResult]) -> str:
    """Render checks as a compact multi-line report for the dialog/log."""
    return "\n".join(
        f"[{'OK' if check.passed else 'CHYBA'}] {check.label}" for check in checks
    )
