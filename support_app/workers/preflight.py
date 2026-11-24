"""Worker that runs the pre-flight readiness checks off the GUI thread."""

from PySide6.QtCore import QObject, Signal, Slot

from support_app.preflight import (
    all_passed,
    check_internet,
    collect_checks,
    format_report,
)


class PreflightWorker(QObject):
    """Run installation/service/OBS/permission/network checks."""

    finished = Signal(dict)

    def __init__(self, permission_ok: bool = False, websocket_ok: bool | None = None):
        super().__init__()
        self.permission_ok = permission_ok
        self.websocket_ok = websocket_ok

    @Slot()
    def run(self):
        checks = collect_checks(
            permission_ok=self.permission_ok,
            internet_ok=check_internet(),
            websocket_ok=self.websocket_ok,
        )
        self.finished.emit({
            "all_passed": all_passed(checks),
            "report": format_report(checks),
            "checks": [
                {"label": check.label, "passed": check.passed}
                for check in checks
            ],
        })
