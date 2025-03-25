class InstallMacrosoftConnectWorker(QObject):
    progress_changed = Signal(int)
    log_text = Signal(str)
    finished = Signal()


    @Slot()
    def run_task(self):
        """Long-running task with progress updates"""
        # signals.log.emit("Začínam proces inštalácie...")

        download_url = (
            "https://online.macrosoft.sk/static/ztpt/output/downloads/macrosoftconnectquicksupport.exe"
        )

        new_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        temp_dir = os.environ.get("TEMP", new_path)
        temp_dir = new_path

        os.makedirs(temp_dir, exist_ok=True)
        installer_path = os.path.join(temp_dir, "macrosoftconnectquicksupport.exe")

        try:
            with urllib.request.urlopen(download_url) as response:
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
                            percent = int(downloaded * 100 / total_size)
                            self.progress_changed.emit(percent)
        except Exception as e:
            # signals.log.emit(f"Chyba pri sťahovaní súboru: {e}")
            # self.install_button.setEnabled(True)
            return

        try:
            # Prepare startup info to hide cmd window
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

            time.sleep(10)  # Wait 10 seconds after installation
        except Exception as e:
            # signals.log.emit(f"Chyba počas inštalácie: {e}")
            # self.install_button.setEnabled(True)
            return

        self.finished.emit()

class UninstallMacrosoftConnectWorker(QObject):
    progress_changed = Signal(int)
    finished = Signal()

    @Slot()
    def run_task(self):
        """Long-running task with progress updates"""

        uninstall_path = os.path.join(
            "C:\\Program Files\\MacrosoftConnectQuickSupport",
            "Uninstall MacrosoftConnectQuickSupport.lnk",
        )

        print(uninstall_path)

        if not os.path.exists(uninstall_path):
            print("not os.path.exists(uninstall_path)")
        #     # signals.log.emit("Odinštalačný súbor nebol nájdený.")
        #     # self.install_button.setEnabled(True)
            return
        else:
            print("Yes os.path.exists(uninstall_path)")
        try:
            SW_HIDE = 0
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "open", uninstall_path, None, None, SW_HIDE
            )
            if result <= 32:
                raise Exception(f"ShellExecuteW zlyhalo s kódom {result}")
            app_path = r"C:\Program Files\MacrosoftConnectQuickSupport\macrosoftconnectquicksupport.exe"
            max_wait_time = 120  # Maximum wait time in seconds
            start_time = time.time()
            while os.path.exists(app_path):
                if time.time() - start_time > max_wait_time:
                    # signals.log.emit("Odinštalácia trvá príliš dlho.")
                    break
                time.sleep(1)
            # signals.log.emit("MacrosoftConnectQuickSupport bol odinštalovaný úspešne.")
        except Exception as e:
            # signals.log.emit(f"Nepodarilo sa spustiť odinštalátor: {e}")
            pass


