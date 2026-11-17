"""Central application configuration.

This module is the single source of truth for filesystem paths, service
endpoints, static credentials and the user-type driven application
identity.  It intentionally does not import any other ``support_app``
module so that it can be imported from anywhere without circular imports.
"""

import json
import os
import re
import sys

import requests

# --- Filesystem paths -------------------------------------------------------
APP_DATA_PATH = os.path.join(os.getenv('APPDATA'), 'MacrosoftSupport')
CONFIG_FILE_PATH = os.path.join(APP_DATA_PATH, 'config.json')
INSTALLER_PATH_FILE_NAME = "installer_path.txt"

# Directory of the application sources (the parent of this package).
APP_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FALLBACK_DOWNLOAD_DIR = os.path.join(APP_ROOT_PATH, "downloads")

# --- Identity defaults ------------------------------------------------------
DEFAULT_ACCESS_CODE = "Nenájdené"
DEFAULT_FULL_NAME = "Nenájdené"

# --- Service endpoints ------------------------------------------------------
ONLINE_BASE_URL = "https://online.macrosoft.sk"
USER_TYPE_URL = f"{ONLINE_BASE_URL}/support/app/get-user-type"
FULL_NAME_URL = f"{ONLINE_BASE_URL}/rustdesk/username/"
RUSTDESK_REPORT_URL = f"{ONLINE_BASE_URL}/rustdesk/"
DESKTOP_AUTH_URL = f"{ONLINE_BASE_URL}/desktop-auth/"
DESKTOP_AUTH_CHECK_URL = f"{ONLINE_BASE_URL}/api/desktop-auth/check/"
SUPPORT_WEBSOCKET_URL = "wss://online.macrosoft.sk/ws/support/"
LATEST_ACCESS_CODE_URL = f"{ONLINE_BASE_URL}/get/lectoure/access/"

# --- Cloudflare access credentials -----------------------------------------
CF_ACCESS_CLIENT_ID = "e5227eb75bb71fa25a09e6bed7362bb1.access"
CF_ACCESS_CLIENT_SECRET = "32097cf5a9639d6bd46e818112e0171119be7754a1acd243f703116f93ca9a38"


def get_cloudflare_headers():
    """Return the Cloudflare service-token headers required by the API."""
    return {
        "cf-access-client-id": CF_ACCESS_CLIENT_ID,
        "cf-access-client-secret": CF_ACCESS_CLIENT_SECRET,
    }


def is_version_string(s: str) -> bool:
    """Return True when *s* looks like a dotted numeric version."""
    s = s.strip()
    pattern = r'^\d+(\.\d+)*$'
    return re.match(pattern, s) is not None


def extract_installer_code(input_str):
    """Extract the short access code from an installer file name."""
    try:
        pattern = re.compile(
            r'MacrosoftSupportInstaller_([^_]+)_.*?\.exe',
            re.IGNORECASE
        )

        if match := pattern.search(input_str):
            code = match.group(1)
            if len(code) > 0:
                return code

    except Exception:
        pass


def installer_path_file():
    """Path of the file that stores the installer name next to the exe."""
    base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, INSTALLER_PATH_FILE_NAME)


def save_login_info(access_code):
    """Saves the access code and user type to a persistent config file."""
    with open(installer_path_file(), 'w', encoding='utf-8') as f:
        f.write(f"Installer Path: MacrosoftSupportInstaller_{access_code}_.exe\n")


def get_user_type():
    """Fetches user type from the API, config file or environment."""
    try:
        access_code = get_access_code()
        full_url = f"{USER_TYPE_URL}?access_code={access_code}"
        res = requests.get(full_url, headers=get_cloudflare_headers())

        return res.json()['user_type']

    except Exception:
        if os.path.exists(CONFIG_FILE_PATH):
            try:
                with open(CONFIG_FILE_PATH, 'r') as f:
                    config = json.load(f)
                    if 'is_lectoure' in config:
                        is_lectoure = config['is_lectoure']
                        return "lectoure" if is_lectoure else "client"

            except Exception:
                pass  # File might be corrupt, fall through

    return os.getenv("USER_TYPE", "lectoure")


def get_access_code():
    """Gets the access code from the config file, falling back to old methods."""
    script_name = os.path.basename(sys.argv[0])
    access = DEFAULT_ACCESS_CODE
    if "installrustdesk_" in script_name:
        access = (
            script_name.replace("installrustdesk_", "")
            .replace(".py", "")
            .replace(".exe", "")
        )
    elif script_name.endswith(".exe"):
        try:
            with open(installer_path_file(), 'r') as file:
                content = file.read().strip()
                code = extract_installer_code(content)
                if code:
                    return code
        except Exception:
            pass

    return access


def get_latest_obs_download_url():
    """Return the URL of the newest OBS Studio Windows installer."""
    download_url = "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-31.1.2-Windows-x64-Installer.exe"

    try:
        url = "https://github.com/obsproject/obs-studio/releases/latest"
        base_url = "https://cdn-fastly.obsproject.com/downloads/"

        resp = requests.get(url, allow_redirects=True)
        latest_link = resp.url
        latest_version = latest_link[latest_link.find("tag/"):].replace("tag/", "")

        if is_version_string(latest_version):
            print("latest version is here")
            download_url = f"{base_url}OBS-Studio-{latest_version}-Windows-x64-Installer.exe"
    except Exception:
        pass

    return download_url


# Resolved once at import time, exactly like the original entry point did.
USER_TYPE = get_user_type()
NAME = "MacrosoftConnectQuickSupport" if USER_TYPE == "client" else "MacrosoftConnect"
EXE_NAME = "macrosoftconnectquicksupport" if USER_TYPE == "client" else "macrosoftconnect"
