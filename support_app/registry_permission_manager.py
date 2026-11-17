import subprocess
import sys

CONSENT_STORE_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"

MICROPHONE_PERMISSION_PATHS = (
    f"HKLM:\\{CONSENT_STORE_PATH}\\microphone",
    f"HKCU:\\{CONSENT_STORE_PATH}\\microphone\\NonPackaged",
    f"HKCU:\\{CONSENT_STORE_PATH}\\microphone",
)

WEBCAM_PERMISSION_PATHS = (
    f"HKLM:\\{CONSENT_STORE_PATH}\\webcam",
    f"HKCU:\\{CONSENT_STORE_PATH}\\webcam",
    f"HKCU:\\{CONSENT_STORE_PATH}\\webcam\\NonPackaged",
)


class RegistryPermissionManager:
    """handles setting device permissions as a global"""
    def __init__(self, log_message=None):
        pass

    def _is_device_allowed(self, permission_paths):
        """Return True when every path reports the 'Allow' value."""
        try:
            for path in permission_paths:
                command = f"(Get-ItemProperty -Path {path}).Value"
                status = self.run_powershell_command(command)
                if status != "Allow":
                    return False
            return True
        except Exception:
            # self.log_message(f"Nepodarilo sa overiť prístup: {e}")
            return False

    def is_microphone_allowed(self):
        return self._is_device_allowed(MICROPHONE_PERMISSION_PATHS)

    def is_webcam_allowed(self):
        return self._is_device_allowed(WEBCAM_PERMISSION_PATHS)

    def run_powershell_command(self, command):
        """Run a PowerShell command with hidden window and return output."""
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        result = subprocess.run(
            ['powershell', '-Command', command],
            capture_output=True,
            text=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        if result.returncode != 0:
            raise Exception(result.stderr.strip())
        return result.stdout.strip()

    def set_device_status(self, device_path, status):
        """Set the device status to Allow or Deny using PowerShell."""
        try:
            command = f"Set-ItemProperty -Path '{device_path}' -Name Value -Value '{status}'"
            self.run_powershell_command(command)
            # self.log_message(f"Set {device_path} to {status}")
        except Exception:
            pass
            # self.log_message(f"Nepodarilo sa nastaviť {device_path} na {status}: {e}")

    def _allow_permission_paths(self, permission_paths):
        """Set every path in *permission_paths* to 'Allow'."""
        try:
            for path in permission_paths:
                self.set_device_status(path, "Allow")
        except Exception:
            pass

    def set_microphone_access_powershell(self):
        self._allow_permission_paths(MICROPHONE_PERMISSION_PATHS)

    def set_webcam_access_powershell(self):
        self._allow_permission_paths(WEBCAM_PERMISSION_PATHS)

    def set_microphone_only_access_powershell(self):
        self.set_microphone_access_powershell()

    def set_microphone_and_webcam_access_powershell(self):
        self.set_microphone_access_powershell()
        self.set_webcam_access_powershell()

    def set_microphone_access(self):
        self.set_microphone_and_webcam_access_powershell()
