import os
import re
import subprocess
import sys
import shutil

from support_app.version import __version__, version_string, version_tuple

# --- Configuration ---

# The name of your main Python script file.
APP_SCRIPT = "main.py"
EXE_NAME = "MacrosoftSupport"
ICON_FILE = "images/icon.ico"
VERSION_INFO_TEMPLATE = "config_files/version_info_main.txt"
INNO_SCRIPT = "config_files/installer.iss"
SLOVAK_ISL_FILE = "config_files/Slovak.isl"
OUTPUT_DIR = "output"
BUILD_DIR = "build"
RENDERED_VERSION_FILE = os.path.join(BUILD_DIR, "version_info_main.txt")



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



def render_version_info(template_path, output_path):
    """Render a PyInstaller version-info file from the single version source."""
    with open(template_path, 'r', encoding='utf-8') as file:
        text = file.read()

    four_part_tuple = version_tuple()
    four_part_string = version_string()

    text = re.sub(r"filevers=\([^)]*\)", f"filevers={four_part_tuple}", text)
    text = re.sub(r"prodvers=\([^)]*\)", f"prodvers={four_part_tuple}", text)
    text = re.sub(
        r"(StringStruct\('FileVersion', ')[^']*(')",
        rf"\g<1>{four_part_string}\g<2>",
        text,
    )
    text = re.sub(
        r"(StringStruct\('ProductVersion', ')[^']*(')",
        rf"\g<1>{four_part_string}\g<2>",
        text,
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return output_path


def render_installer_script(template_path, output_path):
    """Render the Inno Setup script with the current application version."""
    with open(template_path, 'r', encoding='utf-8') as file:
        text = file.read()

    text = re.sub(r"(?m)^AppVersion=.*$", f"AppVersion={__version__}", text, count=1)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return output_path


def compile_application():
    """
    Compiles the application using PyInstaller for a specific user type.
    """
    print("\n>>> Compiling ...")

    # Clean up previous build files
    if os.path.exists('output'):
        print("\n>>> output directory existed and has been removed ...")
        shutil.rmtree('output')
    if os.path.exists('build'):
        print("\n>>> build directory existed and has been removed ...")
        shutil.rmtree('build')

    version_file = render_version_info(VERSION_INFO_TEMPLATE, RENDERED_VERSION_FILE)

    # Construct the PyInstaller command
    pyinstaller_command = [
        'pyinstaller',
        '--noconfirm',
        '--onedir',
        '--windowed',  # Use --console if you need a terminal window for debugging
        '--name', EXE_NAME,
        '--icon', ICON_FILE,
        '--version-file', version_file,
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
    print(">>> Preparing installer directory ...")

    for file in FILES_TO_REMOVE:
        if os.path.isfile(file):
            os.remove(file)

    languages_dir = os.path.join(OUTPUT_DIR, "Languages")
    os.makedirs(languages_dir)

    render_installer_script(INNO_SCRIPT, os.path.join(OUTPUT_DIR, os.path.basename(INNO_SCRIPT)))
    shutil.copy(ICON_FILE, OUTPUT_DIR)
    shutil.copy(SLOVAK_ISL_FILE, languages_dir)



def main():
    """Main function to run the entire build process."""
    print("==========================================")
    print(f"=== Macrosoft Support Build {__version__} ===")
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
    print("=== Build Process for Completed Successfully ===")
    print("==========================================")


if __name__ == "__main__":
    main()