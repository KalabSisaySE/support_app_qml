"""Initial application state discovery worker."""

from PySide6.QtCore import QObject, Signal, Slot

from support_app import app_config
from support_app.app_config import get_access_code
from support_app.browser_permission_manager import BrowserPermissionManager
from support_app.macrosoft_connect import (
    app_executable_path,
    query_rustdesk_id,
    report_rustdesk_id,
)
from support_app.registry_permission_manager import RegistryPermissionManager
from support_app.utils import (
    check_installation,
    check_obs_config,
    close_obs,
    get_full_name,
    is_obs_installed,
    is_obs_running,
    is_service_running,
    setup_obs_config,
    start_obs,
)


class InitializeApp(QObject):
    """initializes app state in a thread (prevent powershell flashes)"""
    complete = Signal(dict)

    def __init__(self):
        super().__init__()
        self.registry_permission = RegistryPermissionManager()
        self.browser_permission = BrowserPermissionManager()

        self.result = {
            "access_code": "Nenájdené",
            "full_name": "Nenájdené",
            "rust_id": "Nenájdené",
            "is_app_installed": False,
            "is_app_service_running": False,
            "is_obs_installed": False,
            "is_obs_running": False,
            "permission_status": False,
        }

    @Slot()
    def start(self):
        code = get_access_code()
        self.result["access_code"] = code

        # APP STATUS
        if check_installation():
            self.result["is_app_installed"] = True
            self.result["is_app_service_running"] = is_service_running(app_config.NAME)

            # get rust_id
            try:
                rust_id = query_rustdesk_id(app_executable_path())
                self.result["rust_id"] = rust_id
                report_rustdesk_id(code, rust_id)

            except Exception:
                self.result["is_app_installed"] = False
        else:
            self.result["is_app_installed"] = False

        # USERNAME
        username = get_full_name(code)
        self.result["full_name"] = username

        # PERMISSIONS
        mic_allowed = self.registry_permission.is_microphone_allowed()
        cam_allowed = self.registry_permission.is_webcam_allowed()
        browser_allowed = self.browser_permission.is_browser_permissions_allowed()

        if mic_allowed and cam_allowed and browser_allowed:
            self.result["permission_status"] = "enabled"
        elif mic_allowed:
            self.result["permission_status"] = "checking"
        else:
            self.result["permission_status"] = "disabled"

        # OBS CONFIG
        is_installed = is_obs_installed()
        self.result["is_obs_installed"] = is_installed

        if is_installed:
            is_running = is_obs_running()
            self.result["is_obs_running"] = is_running

            is_obs_configed = check_obs_config()
            if not is_obs_configed:
                if is_running:
                    close_obs()
                    setup_obs_config()
                    start_obs()
                else:
                    setup_obs_config()

        self.complete.emit(self.result)
        # setup websocket
        # self.setup_websockets(code)
