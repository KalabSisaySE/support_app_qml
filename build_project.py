import json
import os
import subprocess
import sys
import shutil

# --- Configuration ---

# The name of your main Python script file.
APP_SCRIPT = "main.py"
EXE_NAME = "MacrosoftSupport"
ICON_FILE = "images/icon.ico"
VERSION_FILE = "config_files/version_info_main.txt"
INNO_SCRIPT = "config_files/installer.iss"
SLOVAK_ISL_FILE = "config_files/Slovak.isl"
OUTPUT_DIR = "output"



# Directories that need to be included with your application (e.g., qml files, images).
# Format: 'source_path:destination_in_dist'
ADDITIONAL_DATA = {
    'qml': 'qml',
    'images': 'images',
}

# Files to remove, reduce size
FILES_TO_REMOVE = [
    os.path.join(OUTPUT_DIR, 'MacrosoftSupport', '_internal', 'PySide6', 'Qt6WebEngineCore.dll'),
    os.path.join(OUTPUT_DIR, 'MacrosoftSupport', '_internal', 'PySide6', 'Qt6Widgets.dll'),
]


# --- Build Logic ---
def run_command(command, env=None):
    """Executes a command in the shell and prints its output."""
    print(f"--- Running command: {' '.join(command)} ---")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        if rc != 0:
            print(f"--- Command failed with exit code {rc} ---")
            sys.exit(rc)
        print("--- Command finished successfully ---")
        return True
    except Exception as e:
        print(f"--- An error occurred: {e} ---")
        sys.exit(1)



def compile_application():
    """
    Compiles the application using PyInstaller for a specific user type.
    """
    print(f"\n>>> Compiling ...")

    # Clean up previous build files
    if os.path.exists('output'):
        print(f"\n>>> output directory existed and has been removed ...")
        shutil.rmtree('output')
    if os.path.exists('build'):
        print(f"\n>>> build directory existed and has been removed ...")
        shutil.rmtree('build')



    # Construct the PyInstaller command
    pyinstaller_command = [
        'pyinstaller',
        '--noconfirm',
        '--onedir',
        '--windowed',  # Use --console if you need a terminal window for debugging
        '--name', EXE_NAME,
        '--icon', ICON_FILE,
        '--version-file', VERSION_FILE,
        '--distpath', OUTPUT_DIR,
        '--optimize', "2",
        '--uac-admin',
        APP_SCRIPT,
    ]

    # Add data files (like the qml directory)
    for src, dst in ADDITIONAL_DATA.items():
        pyinstaller_command.extend(['--add-data', f'{src}{os.pathsep}{dst}'])

    print(f"\n\npyinstaller_command: {" ".join(pyinstaller_command)}")

    # Run the compilation
    run_command(pyinstaller_command)

    print(f">>> Successfully compiled version into '{OUTPUT_DIR}' folder.")


def prepare_installer_directory():
    """
    Creates the final 'installer' directory required by the Inno Setup script.
    """
    print(f">>> Preparing installer directory ...")

    for file in FILES_TO_REMOVE:
        if os.path.isfile(file):
            os.remove(file)

    languages_dir = os.path.join(OUTPUT_DIR, "Languages")
    os.makedirs(languages_dir)

    shutil.copy(INNO_SCRIPT, OUTPUT_DIR)
    shutil.copy(ICON_FILE, OUTPUT_DIR)
    shutil.copy(SLOVAK_ISL_FILE, languages_dir)



def main():
    """Main function to run the entire build process."""
    print("==========================================")
    print("=== Macrosoft Support Build Automation ===")
    print("==========================================")

    # 1. Compile the application for the chosen build type
    compile_application()

    # 2. Prepare the final directory structure for Inno Setup
    prepare_installer_directory()

    # 3. Final cleanup of intermediate folders
    print("\n>>> Cleaning up intermediate build files...")
    if os.path.exists('build'):
        shutil.rmtree('build')
    spec_file = f'{os.path.splitext(APP_SCRIPT)[0]}.spec'
    if os.path.exists(spec_file):
        os.remove(spec_file)
    # if os.path.exists('dist'):
    #     shutil.rmtree('dist')


    print("\n==========================================")
    print(f"=== Build Process for Completed Successfully ===")
    print("==========================================")


if __name__ == "__main__":
    main()