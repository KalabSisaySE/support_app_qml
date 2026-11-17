"""Macrosoft Connect installation and uninstallation worker."""

import ctypes
import os
import subprocess
import sys
import time
import urllib.request

from PySide6.QtCore import QObject, Signal, Slot

from support_app.app_config import (
    EXE_NAME,
    FALLBACK_DOWNLOAD_DIR,
    NAME,
    RUSTDESK_REPORT_URL,
    get_access_code,
    get_cloudflare_headers,
    get_user_type,
)
from support_app.rust_service_manager import ServiceManager
from support_app.utils import (
    check_installation,
    is_app_running,
    is_service_running,
)


class AppInstallationWorker(QObject):
    """manages macrosoft rustdesk installation and uninstallation"""
    progress_changed = Signal(float, str)
    log = Signal(str)
    finished = Signal(dict)
    selfUninstallTriggered = Signal()

    def __init__(self):
        super().__init__()
        self.result_data = {
            "app_installed": False,
            "app_service_on": False,
            "rust_id": "Nenájdené"
        }
        self.access = get_access_code()
        self.manager = ServiceManager(
            service_name=f"{NAME}",
            display_name=f"{NAME} Service",
            binary_path=(
                fr'"C:\Program Files\{NAME}\{EXE_NAME}.exe" --service'
            ),
        )
        self.process_name = "app_installation"

    @Slot()
    def handle_install(self):
        """handles installation state"""
        if check_installation():
            self.uninstall_app()
        else:
            self.install_app()

    def install_app(self):
        """installs and rust Macrosoft RustDesk"""
        self.log.emit("Začínam proces inštalácie...")

        base_url = "https://cloud.macrosoft.sk/"
        download_url = f"{base_url}support_app/{EXE_NAME}.exe"
        temp_dir = os.environ.get("TEMP", FALLBACK_DOWNLOAD_DIR)

        os.makedirs(temp_dir, exist_ok=True)
        installer_path = os.path.join(temp_dir, f"{EXE_NAME}.exe")

        try:
            req = urllib.request.Request(
                download_url,
                headers=get_cloudflare_headers(),
            )
            with urllib.request.urlopen(req) as response:
                total_size = int(response.getheader("Content-Length", "0"))
                block_size = 8192
                with open(installer_path, "wb") as file:
                    downloaded = 0
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        file.write(buffer)
                        downloaded += len(buffer)
                        if total_size > 0:
                            percent = (downloaded * 75) / total_size
                            self.progress_changed.emit(percent, self.process_name)
        except Exception as e:
            self.log.emit(f"Chyba pri sťahovaní súboru: {e}")
            self.finished.emit(self.result_data)
            return

        try:
            # Prepare startup info to hide cmd window
            self.log.emit(f"Inštaluje sa Macrosoft Connect Quick Support...")
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            SW_HIDE = 0
            startupinfo.wShowWindow = SW_HIDE

            # Run the installer
            process = subprocess.Popen(
                [installer_path, "--silent-install"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
            )

            time.sleep(5)  # Wait 10 seconds after installation

            self.progress_changed.emit(80, self.process_name)

            self.result_data["app_installed"] = True

            self.progress_changed.emit(88, self.process_name)

            self.result_data["app_service_on"] = self.start_service()

            self.progress_changed.emit(94, self.process_name)

            self.result_data["rust_id"] = self.get_rustdesk_id()

            self.progress_changed.emit(100, self.process_name)

        except Exception as e:
            self.log.emit(f"Chyba počas inštalácie: {e}")

        self.finished.emit(self.result_data)

    def uninstall_app(self):
        """uninstalls macrosoft connect and then triggers self-uninstall."""
        uninstall_path = os.path.join(
            f"C:\\Program Files\\{NAME}",
            f"Uninstall {NAME}.lnk",
        )

        if not os.path.exists(uninstall_path):
            self.log.emit("Odinštalačný súbor nebol nájdený.")
            self.finished.emit(self.result_data)
            return

        try:
            # --- This part for uninstalling Macrosoft Connect remains the same ---
            SW_HIDE = 0
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "open", uninstall_path, None, None, SW_HIDE
            )
            if result <= 32:
                raise Exception(f"ShellExecuteW zlyhalo s kódom {result}")

            app_path = fr"C:\Program Files\{NAME}\{EXE_NAME}.exe"
            max_wait_time = 120
            start_time = time.time()
            while os.path.exists(app_path):
                if time.time() - start_time > max_wait_time:
                    self.log.emit("Odinštalácia trvá príliš dlho.")
                    break
                time.sleep(1)
            self.log.emit(f"{NAME} bol odinštalovaný úspešne.")

            # --- START: NEW SELF-UNINSTALL LOGIC ---
            # Check if running as a compiled executable (frozen by PyInstaller)
            if get_user_type() == "client":
                if getattr(sys, 'frozen', False):
                    app_dir = os.path.dirname(sys.executable)
                    main_uninstaller_path = os.path.join(app_dir, "unins000.exe")

                    if os.path.exists(main_uninstaller_path):
                        self.log.emit("Spúšťanie odinštalácie hlavnej aplikácie...")
                        # Launch the main app's uninstaller silently and detach it
                        subprocess.Popen([main_uninstaller_path, "/SILENT"])
                        # Emit signal to tell the main app to close
                        self.selfUninstallTriggered.emit()
                    else:
                        self.log.emit("Odinštalačný program hlavnej aplikácie (unins000.exe) nebol nájdený.")
            # --- END: NEW SELF-UNINSTALL LOGIC ---

        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť odinštalátor: {e}")

        # Emit finished signal to allow the worker thread to be cleaned up
        self.finished.emit(self.result_data)

    def get_rustdesk_id(self):
        """Retrieve the RustDesk ID."""
        app_path = fr"C:\Program Files\{NAME}\{EXE_NAME}.exe"

        if not os.path.exists(app_path):
            self.log.emit(
                f"{NAME} nie je nainštalovaný, prosím kliknite na Inštalovať {NAME}"
            )
            return "Nenájdené"

        try:
            result = subprocess.run(
                [app_path, "--get-id"],
                capture_output=True,
                text=True,
                check=True,
            )
            rustdesk_id = result.stdout.strip() if result.stdout else "Nenájdené"


            self.log.emit(f"Vaše ID je: {rustdesk_id}")
            self.report_rustdesk_id(rustdesk_id)
            return rustdesk_id

        except Exception as e:
            self.log.emit(f"Nepodarilo sa získať ID: {e}")
            return "Nenájdené"

    def report_rustdesk_id(self, rustdesk_id, max_attempts=3):
        """report the RustDesk ID to the server."""
        if self.access:
            url = f"{RUSTDESK_REPORT_URL}?access={self.access}&rustdesk={rustdesk_id}"
            attempt = 0

            while attempt < max_attempts:
                attempt += 1
                try:
                    req = urllib.request.Request(url, headers=get_cloudflare_headers())
                    with urllib.request.urlopen(req) as response:
                        if response.status == 200:
                            self.log.emit("ID bolo úspešne odoslané.")
                            break
                        else:
                            self.log.emit(f"Odozva servera: {response.status}")
                            if attempt < max_attempts:
                                time.sleep(1)
                except Exception as e:
                    self.log.emit(f"Nepodarilo sa odoslať ID: {e}")


    def start_macrosoftconnect(self):
        """Start the Macrosoft Connect application."""
        app_path = fr"C:\Program Files\{NAME}\{EXE_NAME}.exe"
        if not os.path.exists(app_path):
            return

        try:
            subprocess.Popen(
                [app_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return True
        except Exception as e:
            return

    def start_service(self):
        """Start the Macrosoft Connect service."""
        try:
            if is_service_running(f"{NAME}"):
                self.log.emit("Služba je spustená...")
                return True

            if not check_installation():
                self.log.emit("Aplikácia nie je nainštalovaná. Najprv nainštalujte aplikáciu...")
                return

            if not is_app_running():
                self.log.emit("Aplikácia nie je spustená. Spúšťa sa aplikácia...")
                if not self.start_macrosoftconnect():
                    self.log.emit("Nepodarilo sa automaticky spustiť aplikáciu...")
                    return

            if not self.manager.is_service_installed():
                self.log.emit("Vytváranie služby...")
                self.manager.create_service()

            self.manager.start_service()
            self.log.emit(f"Služba {NAME} je spustená.")
            return True

        except Exception as e:
            self.log.emit(f"Nepodarilo sa spustiť službu {NAME}., {e}")


    def stop_service(self):
        """Stop the Macrosoft Connect service."""
        try:
            if is_service_running(f"{NAME}"):
                self.log.emit("Služba je spustená.")
                if is_app_running():
                    self.log.emit("Aplikácia je spustená.")
                    self.manager.stop_service()
                    self.log.emit(f"Služba {NAME} bola zastavená.")
                    return True
                else:
                    self.log.emit("Služba nie je spustená...")
            else:
                self.log.emit("Služba nie je spustená...")
                return True
        except Exception as e:
            self.log.emit(
                f"Nepodarilo sa zastaviť službu {NAME}. {e}"
            )
