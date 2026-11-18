"""Worker that applies microphone, camera and browser permissions."""

import os

from PySide6.QtCore import QObject, Signal, Slot

from support_app.app_config import get_access_code
from support_app.browser_permission_manager import BrowserPermissionManager
from support_app.registry_permission_manager import RegistryPermissionManager


class PermissionWorker(QObject):
    """manages opening/closing a browser"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal(dict)

    def __init__(self):
        super().__init__()
        self.access = get_access_code()
        self.registry_permission = RegistryPermissionManager()
        self.browser_permission = BrowserPermissionManager()
        self.result_data = {
            "is_webcam_allowed": False,
            "is_microphone_allowed": False,
            "is_browser_permissions_allowed": False,
        }
        self.process_name = "all_permissions"
        self.progress = 0

    @Slot()
    def set_microphone_access_only(self):
        """Set microphone access permissions only."""
        self.process_name = "microphone_only"
        self.log.emit("Nastavujem prístup k mikrofónu iba...")

        self.set_microphone_access_powershell(all_permissions=False)

        self.check_permissions()
        self.progress = 100
        self.progress_changed.emit(self.progress, self.process_name)
        self.finished.emit(self.result_data)

    @Slot()
    def set_microphone_and_camera_access_only(self):
        """Set all necessary permissions."""
        self.log.emit("Nastavujem všetky povolenia...")
        self.log.emit("Nastavujem prístup k mikrofónu cez PowerShell...")

        self.set_microphone_access_powershell()

        self.log.emit("Nastavujem prístup k kamere cez PowerShell...")

        self.set_camera_access_powershell()

        self.set_browser_permissions()

        self.check_permissions()

        self.progress = 100
        self.progress_changed.emit(self.progress, self.process_name)
        self.finished.emit(self.result_data)

    def check_permissions(self):
        """checks permissions statuses"""
        is_microphone_allowed = self.registry_permission.is_microphone_allowed()
        is_webcam_allowed = self.registry_permission.is_webcam_allowed()
        is_browser_permissions_allowed = self.browser_permission.is_browser_permissions_allowed()

        self.result_data["is_microphone_allowed"] = is_microphone_allowed
        self.result_data["is_webcam_allowed"] = is_webcam_allowed
        self.result_data["is_browser_permissions_allowed"] = is_browser_permissions_allowed


    def set_microphone_access_powershell(self, all_permissions=True):
        inc = 6 if all_permissions else 25

        # setting microphone access
        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone\\NonPackaged"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                self.registry_permission.set_device_status(p, "Allow")
                self.progress += inc
                self.progress_changed.emit(self.progress, self.process_name)

            self.log.emit("Mikrofón prístup bol povolený pomocou PowerShell.")
        except Exception as e:
            self.log.emit(f"Chyba pri nastavovaní mikrofónu cez PowerShell: {e}")

    def set_camera_access_powershell(self, all_permissions=True):
        inc = 6 if all_permissions else 25

        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                self.registry_permission.set_device_status(p, "Allow")
                self.progress += inc
                self.progress_changed.emit(self.progress, self.process_name)

            self.log.emit("Kamera prístup bol povolený pomocou PowerShell.")
        except Exception as e:
            pass
            self.log.emit(f"Chyba pri nastavovaní kamery cez PowerShell: {e}")

    def set_browser_permissions(self):
        # URL to allow
        inc = 9

        # For Edge
        try:
            if os.path.exists(self.browser_permission.edge_basepath):
                edge_preferences = self.browser_permission.find_preferences_files(self.browser_permission.edge_basepath)

                for preference in edge_preferences:
                    self.browser_permission.modify_preference_file(preference)
            self.log.emit("Povolenia pre Microsoft Edge boli nastavené.")
        except Exception as e:
            self.log.emit(f"Povolenia pre Edge neboli nastavené: {e}")

        self.progress += inc
        self.progress_changed.emit(self.progress, self.process_name)

        # For Chrome
        try:
            if os.path.exists(self.browser_permission.chrome_basepath):
                chrome_preferences = self.browser_permission.find_preferences_files(
                    self.browser_permission.chrome_basepath)

                for preference in chrome_preferences:
                    self.browser_permission.modify_preference_file(preference)
            self.log.emit("Povolenia pre Google Chrome boli nastavené.")
        except Exception as e:
            self.log.emit(f"Povolenia pre Chrome neboli nastavené: {e}")

        self.progress += inc
        self.progress_changed.emit(self.progress, self.process_name)

        # For Brave (Brave uses Chromium policies)
        try:
            if os.path.exists(self.browser_permission.brave_basepath):
                brave_preferences = self.browser_permission.find_preferences_files(
                    self.browser_permission.brave_basepath)

                for preference in brave_preferences:
                    self.browser_permission.modify_preference_file(preference)
            self.log.emit("Povolenia pre Brave boli nastavené.")
        except Exception as e:
            self.log.emit(f"Povolenia pre Brave neboli nastavené: {e}")

        self.progress += inc
        self.progress_changed.emit(self.progress, self.process_name)

        # For Firefox
        try:
            if self.browser_permission.set_firefox_permissions():
                self.log.emit("Povolenia pre Firefox boli nastavené.")
            else:
                self.log.emit("Firefox profily neboli nájdené.")
        except Exception as e:
            self.log.emit(f"Povolenia pre Firefox neboli nastavené: {e}")

        self.progress += inc
        self.progress_changed.emit(self.progress, self.process_name)
