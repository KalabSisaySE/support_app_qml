"""Central application configuration.

This module is the single source of truth for service endpoints, static
credentials and the user-type driven application identity.

The identity is resolved **lazily** on first access to ``NAME``/``EXE_NAME``
so importing this module (e.g. in tests) never performs network I/O.  Use
``from support_app import app_config`` and read ``app_config.NAME`` at call
time; do not bind the attributes at import time.
"""

import os
import re

from support_app import api
from support_app.logging_setup import get_logger
from support_app.settings import (
    APP_DATA_PATH,
    CONFIG_FILE_PATH,
    DEFAULT_ACCESS_CODE,
    INSTALLER_PATH_FILE_NAME,
    extract_installer_code,
    get_access_code,
    load_settings,
    save_login_info,
)

logger = get_logger(__name__)

__all__ = [
    "APP_DATA_PATH",
    "APP_ROOT_PATH",
    "CONFIG_FILE_PATH",
    "DEFAULT_ACCESS_CODE",
    "DEFAULT_FULL_NAME",
    "DESKTOP_AUTH_CHECK_URL",
    "DESKTOP_AUTH_URL",
    "DOWNLOAD_TIMEOUT_SECONDS",
    "FALLBACK_DOWNLOAD_DIR",
    "FULL_NAME_URL",
    "INSTALLER_PATH_FILE_NAME",
    "LATEST_ACCESS_CODE_URL",
    "OBS_UPLOAD_URL",
    "ONLINE_BASE_URL",
    "RUSTDESK_REPORT_URL",
    "SUPPORT_WEBSOCKET_URL",
    "USER_TYPE_URL",
    "extract_installer_code",
    "get_access_code",
    "get_cloudflare_headers",
    "get_latest_obs_download_url",
    "get_user_type",
    "is_version_string",
    "load_settings",
    "reset_identity_cache",
    "save_login_info",
]

# Directory of the application sources (the parent of this package).
APP_ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FALLBACK_DOWNLOAD_DIR = os.path.join(APP_ROOT_PATH, "downloads")

# Installer downloads are large; allow more time than regular API calls.
DOWNLOAD_TIMEOUT_SECONDS = 30.0

# --- Identity defaults ------------------------------------------------------
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
OBS_UPLOAD_URL = f"{ONLINE_BASE_URL}/upload/recording/obs/"

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


def get_user_type():
    """Fetches user type from the API, config file or environment."""
    try:
        access_code = get_access_code()
        full_url = f"{USER_TYPE_URL}?access_code={access_code}"
        res = api.get(full_url, headers=get_cloudflare_headers(), retries=0)

        return res.json()['user_type']

    except Exception as e:
        logger.debug("Could not fetch user type from API, using local fallback: %s", e)
        settings = load_settings()
        if settings.is_lectoure is not None:
            return "lectoure" if settings.is_lectoure else "client"

    return os.getenv("USER_TYPE", "lectoure")


def get_latest_obs_download_url():
    """Return the URL of the newest OBS Studio Windows installer."""
    download_url = "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-31.1.2-Windows-x64-Installer.exe"

    try:
        url = "https://github.com/obsproject/obs-studio/releases/latest"
        base_url = "https://cdn-fastly.obsproject.com/downloads/"

        resp = api.get(url, allow_redirects=True)
        latest_link = resp.url
        latest_version = latest_link[latest_link.find("tag/"):].replace("tag/", "")

        if is_version_string(latest_version):
            logger.debug("Latest OBS version resolved from upstream.")
            download_url = f"{base_url}OBS-Studio-{latest_version}-Windows-x64-Installer.exe"
    except Exception as e:
        logger.debug("Could not resolve the latest OBS release: %s", e)

    return download_url


# --- Lazy application identity ---------------------------------------------
_USER_TYPE = None


def _resolve_identity() -> str:
    """Resolve and cache the user type and the matching app identity."""
    global _USER_TYPE
    if _USER_TYPE is None:
        user_type = get_user_type()
        if user_type == "client":
            name = "MacrosoftConnectQuickSupport"
            exe_name = "macrosoftconnectquicksupport"
        else:
            name = "MacrosoftConnect"
            exe_name = "macrosoftconnect"

        globals()["NAME"] = name
        globals()["EXE_NAME"] = exe_name
        _USER_TYPE = user_type

    return _USER_TYPE


def reset_identity_cache() -> None:
    """Drop the cached identity (used by tests and after account changes)."""
    global _USER_TYPE
    _USER_TYPE = None
    globals().pop("NAME", None)
    globals().pop("EXE_NAME", None)


def __getattr__(name):
    """Resolve ``NAME``/``EXE_NAME`` on first access instead of at import."""
    if name in ("NAME", "EXE_NAME"):
        _resolve_identity()
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
