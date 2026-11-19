"""Calls to the Macrosoft web API that are not tied to a specific worker."""

import webbrowser

from support_app import api
from support_app.app_config import (
    FULL_NAME_URL,
    LATEST_ACCESS_CODE_URL,
    ONLINE_BASE_URL,
    get_cloudflare_headers,
)
from support_app.logging_setup import get_logger
from support_app.system_info import get_public_ip

logger = get_logger(__name__)


def get_full_name(access):
    if access:
        url = f'{FULL_NAME_URL}?access={access}'
        try:
            res = api.get(url, headers=get_cloudflare_headers(), retries=0)

            json_data = res.json()
            if json_data.get('status') == 'found':
                return json_data.get('full_name', 'Neznáme meno')
            else:
                return 'Neznáme meno'

        except Exception as e:
            logger.debug("Could not fetch full name for access code: %s", e)
            return ""
    return ""


def open_website(access):
    if access:
        url = f'{ONLINE_BASE_URL}/online/?access={access}'
        webbrowser.open(url)
        return True
    else:
        return False


def get_latest_access_code():
    try:
        my_ip = get_public_ip()
        if my_ip:
            url = LATEST_ACCESS_CODE_URL
            res = api.post(url, json={"ip_address": my_ip}, headers=get_cloudflare_headers())

            if res.status_code == 200:
                return res.json().get('access_code', "")
        else:
            return ""
    except Exception as e:
        logger.debug("Could not fetch the latest access code: %s", e)
        return ""
