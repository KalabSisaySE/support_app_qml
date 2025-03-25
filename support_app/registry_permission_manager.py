import subprocess


class RegistryPermissionManager:
    """handles setting device permissions as a global"""
    def __init__(self, log_message=None):
        pass

    def is_microphone_allowed(self):
        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone\\NonPackaged"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                command = f"(Get-ItemProperty -Path {p}).Value"
                status = self.run_powershell_command(command)
                if status != "Allow":
                    return False
            return True
        except Exception as e:
            # self.log_message(f"Nepodarilo sa overiť prístup mikrofónu: {e}")
            return False

    def is_webcam_allowed(self):
        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                command = f"(Get-ItemProperty -Path {p}).Value"
                status = self.run_powershell_command(command)
                if status != "Allow":
                    return False
            return True
        except Exception as e:
            # self.log_message(f"Nepodarilo sa overiť prístup kamery: {e}")
            return False

    def run_powershell_command(self, command):
        """Run a PowerShell command and return the output."""
        result = subprocess.run(['powershell', '-Command', command], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(result.stderr.strip())
        return result.stdout.strip()

    def set_device_status(self, device_path, status):
        """Set the device status to Allow or Deny using PowerShell."""
        try:
            command = f"Set-ItemProperty -Path '{device_path}' -Name Value -Value '{status}'"
            self.run_powershell_command(command)
            # self.log_message(f"Set {device_path} to {status}")
        except Exception as e:
            pass
            # self.log_message(f"Nepodarilo sa nastaviť {device_path} na {status}: {e}")

    def set_microphone_access_powershell(self):
        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone\\NonPackaged"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                self.set_device_status(p, "Allow")
            # self.log_message("Mikrofón prístup bol povolený pomocou PowerShell.")
        except Exception as e:
            pass
            # self.log_message(f"Chyba pri nastavovaní mikrofónu cez PowerShell: {e}")

    def set_webcam_access_powershell(self):
        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\webcam\\NonPackaged"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                self.set_device_status(p, "Allow")
            # self.log_message("Kamera prístup bol povolený pomocou PowerShell.")
        except Exception as e:
            pass
            # self.log_message(f"Chyba pri nastavovaní kamery cez PowerShell: {e}")

    def set_microphone_only_access_powershell(self):
        try:
            global_settings = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone\\NonPackaged"
            desktop_apps_settings = "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"

            permission_paths = [global_settings, apps_settings, desktop_apps_settings]
            for p in permission_paths:
                self.set_device_status(p, "Allow")

            # self.log_message("Mikrofón prístup bol povolený pomocou PowerShell.")

        except Exception as e:
            pass
            # self.log_message(f"Chyba pri nastavovaní mikrofónu cez PowerShell: {e}")

    def set_microphone_and_webcam_access_powershell(self):
        try:
            self.set_microphone_access_powershell()
            self.set_webcam_access_powershell()

        except Exception as e:
            pass
            # self.log_message(f"Chyba pri nastavovaní prístupov: {e}")

    def set_microphone_access(self):
        self.set_microphone_and_webcam_access_powershell()

