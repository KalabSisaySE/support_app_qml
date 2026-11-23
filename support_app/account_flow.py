"""Web account authentication flow and its post-login state updates."""

from __future__ import annotations

from typing import Any, Protocol

from support_app import api
from support_app.app_config import (
    RUSTDESK_REPORT_URL,
    get_cloudflare_headers,
    save_login_info,
)
from support_app.workers import AccountAuthWorker

DEFAULT_MISSING = "Nenájdené"


class AccountFlowHost(Protocol):
    """Backend surface required by the account flow."""

    is_change_account_btn_enabled: bool
    is_user_lectoure: bool
    access_code: str
    username: str
    _rust_id: str
    showDialog: Any

    def add_log(self, message: str) -> None: ...

    def _start_worker(
        self,
        task_name: str,
        worker_class: Any,
        start_method_name: str,
        finished_slot: Any,
        worker_args: Any = None,
    ) -> Any: ...

    def setup_websockets(self, code: str) -> None: ...

    def on_account_auth_finished(self, result_data: dict) -> None: ...


class AccountFlow:
    """Starts desktop authentication and applies the returned identity."""

    def __init__(self, host: AccountFlowHost) -> None:
        self._host = host

    def start(self) -> None:
        """Disable the button and launch the browser-based auth worker."""
        host = self._host
        host.is_change_account_btn_enabled = False
        host.add_log("Spúšťa sa proces zmeny účtu...")
        host._start_worker(
            task_name="account_auth",
            worker_class=AccountAuthWorker,
            start_method_name="start_auth_flow",
            finished_slot=host.on_account_auth_finished,
        )

    def on_finished(self, result_data: dict) -> None:
        """Persist the new identity and re-initialize dependent services."""
        host = self._host
        new_access_code = result_data.get('access_code')
        is_lectoure = result_data.get('is_lectoure', True)

        host.is_user_lectoure = is_lectoure

        if new_access_code:
            host.add_log("Účet bol úspešne zmenený.")

            # 1. Save the new code persistently
            save_login_info(new_access_code)

            # 2. Update the backend state
            host.access_code = new_access_code
            host.username = result_data.get('full_name', DEFAULT_MISSING)

            # 3. Re-initialize websockets with the new identity
            host.setup_websockets(new_access_code)

            # 4. Optionally, re-report RustDesk ID for the new user
            if host._rust_id != DEFAULT_MISSING:
                url = f"{RUSTDESK_REPORT_URL}?access={new_access_code}&rustdesk={host._rust_id}"
                try:
                    api.get(url, headers=get_cloudflare_headers(), retries=0)
                except Exception as e:
                    host.add_log(f"Nepodarilo sa znovu nahlásiť RustDesk ID: {e}")

            host.showDialog.emit(
                "Účet Zmenený", "Vaša identita bola úspešne aktualizovaná.", True
            )
        else:
            host.add_log("Proces zmeny účtu zlyhal alebo bol zrušený.")
            host.showDialog.emit("Chyba", "Nepodarilo sa zmeniť účet.", False)

        host.is_change_account_btn_enabled = True
