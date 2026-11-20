"""One-click setup orchestration: install, permissions, then OBS if needed."""

from __future__ import annotations

from typing import Any, Protocol

from support_app.obs_control import is_obs_installed
from support_app.system_info import check_installation
from support_app.workers import AppInstallationWorker, OBSInstallationWorker, PermissionWorker


class OneClickHost(Protocol):
    """Backend surface required by the one-click flow."""

    is_app_install_btn_enabled: bool
    is_app_start_btn_enabled: bool
    is_app_service_btn_enabled: bool
    is_app_rust_id_btn_enabled: bool
    is_enable_microphone_only_btn_enabled: bool
    is_enable_microphone_and_camera_btn_enabled: bool
    is_obs_install_btn_enabled: bool
    is_user_lectoure: bool
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

    def on_installation_finished(self, result_data: dict) -> None: ...

    def update_permission_status(self, result_data: dict) -> None: ...

    def on_obs_installation_finished(self) -> None: ...

    def _on_one_click_install_finished(self, result_data: dict) -> None: ...

    def _on_one_click_permissions_finished(self, result_data: dict) -> None: ...

    def _on_one_click_obs_finished(self) -> None: ...


class OneClickFlow:
    """Runs the chained install → permissions → OBS workflow."""

    def __init__(self, host: OneClickHost) -> None:
        self._host = host

    def start(self) -> None:
        """Disable the action buttons and start the first applicable step."""
        host = self._host
        host.add_log("Spúšťa sa kompletné nastavenie na 1-klik...")

        # Disable all relevant buttons to prevent user interference
        host.is_app_install_btn_enabled = False
        host.is_app_start_btn_enabled = False
        host.is_app_service_btn_enabled = False
        host.is_app_rust_id_btn_enabled = False
        host.is_enable_microphone_only_btn_enabled = False
        host.is_enable_microphone_and_camera_btn_enabled = False
        host.is_obs_install_btn_enabled = False

        # Check if the app is already installed to skip the installation step
        if check_installation():
            host.add_log("Aplikácia je už nainštalovaná. Prechádzam na nastavenie povolení.")
            self.start_permissions()
        else:
            host._start_worker(
                task_name="one_click_install",
                worker_class=AppInstallationWorker,
                start_method_name="handle_install",
                finished_slot=host._on_one_click_install_finished,
            )

    def start_permissions(self) -> None:
        """Start the permission step of the chain."""
        self._host._start_worker(
            task_name="one_click_permissions",
            worker_class=PermissionWorker,
            start_method_name="set_microphone_and_camera_access_only",
            finished_slot=self._host._on_one_click_permissions_finished,
        )

    def on_install_finished(self, result_data: dict) -> None:
        """Update the installation state and continue with permissions."""
        host = self._host
        host.add_log("Inštalácia aplikácie dokončená. Pokračujem nastavením povolení...")
        host.on_installation_finished(result_data)
        self.start_permissions()

    def on_permissions_finished(self, result_data: dict) -> None:
        """Update permissions, then install OBS for lecturers if needed."""
        host = self._host
        host.add_log("Nastavenie povolení dokončené.")
        host.update_permission_status(result_data)

        # Check if we need to install OBS (lectoure user and OBS not installed)
        if host.is_user_lectoure and not is_obs_installed():
            host.add_log("Používateľ je lektor, spúšťa sa inštalácia OBS...")
            host._start_worker(
                task_name="one_click_obs_install",
                worker_class=OBSInstallationWorker,
                start_method_name="install_app",
                finished_slot=host._on_one_click_obs_finished,
            )
        else:
            if host.is_user_lectoure and is_obs_installed():
                host.add_log("OBS je už nainštalovaný, krok sa preskakuje.")
            self.complete()

    def on_obs_finished(self) -> None:
        """Update the OBS state and finish the chain."""
        self._host.add_log("Inštalácia OBS dokončená.")
        self._host.on_obs_installation_finished()
        self.complete()

    def complete(self) -> None:
        """Re-enable the action buttons and show the success dialog."""
        host = self._host
        host.add_log("Kompletné nastavenie na 1-klik bolo úspešne dokončené!")

        # Re-enable all buttons now that the entire sequence is complete
        host.is_app_install_btn_enabled = True
        host.is_app_start_btn_enabled = check_installation()
        host.is_app_service_btn_enabled = check_installation()
        host.is_app_rust_id_btn_enabled = check_installation()
        host.is_enable_microphone_only_btn_enabled = True
        host.is_enable_microphone_and_camera_btn_enabled = True
        host.is_obs_install_btn_enabled = not is_obs_installed()

        host.showDialog.emit(
            "Nastavenie Dokončené",
            "Kompletné nastavenie na 1-klik bolo úspešne dokončené!",
            True,
        )
