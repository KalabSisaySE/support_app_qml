import json
import os
import shutil
import sqlite3
import tempfile
import time

import psutil

from support_app.logging_setup import get_logger

logger = get_logger(__name__)

SITE_URL = 'https://online.macrosoft.sk'
SITE_URL_KEY = f'{SITE_URL}:443,*'

FIREFOX_PROFILES_INI = ('Mozilla', 'Firefox', 'profiles.ini')
FIREFOX_PERMISSIONS_DB = 'permissions.sqlite'
FIREFOX_USER_DIR = ('Mozilla', 'Firefox')

BROWSER_PROCESS_NAMES = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe"]


class BrowserPermissionManager:
    """manages browser permissions"""

    def __init__(self, log_message=None):
        self.user_account = None

        try:
            self.user_account = os.getlogin()
        except Exception as e:
            logger.debug("Could not determine the current user account: %s", e)

        if self.user_account:
            self.chrome_basepath = f"C:\\Users\\{self.user_account}\\AppData\\Local\\Google\\Chrome\\"
            self.brave_basepath = f"C:\\Users\\{self.user_account}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\"
            self.edge_basepath = f"C:\\Users\\{self.user_account}\\AppData\\Local\\Microsoft\\Edge\\"
        else:
            self.chrome_basepath = ""
            self.brave_basepath = ""
            self.edge_basepath = ""

    def _chromium_browser_paths(self):
        """The Chromium based browsers and their user data directories."""
        return (
            ("Edge", self.edge_basepath),
            ("Chrome", self.chrome_basepath),
            ("Brave", self.brave_basepath),
        )

    def find_preferences_files(self, base_path):
        """
        Searches for the 'Preferences' file in 'Default' and dynamically numbered 'Profile n' folders.

        Args:
            base_path (str): The base directory where the search starts.

        Returns:
            list: A list of absolute paths to 'Preferences' files that exist.
        """
        result_paths = []

        # Check the "Default" folder
        default_path = os.path.join(base_path, "User Data", "Default", "Preferences")
        if os.path.isfile(default_path):
            result_paths.append(os.path.abspath(default_path))

        # Check the "Profile n" folders dynamically
        profile_number = 1
        while True:
            profile_path = os.path.join(base_path, "User Data", f"Profile {profile_number}", "Preferences")
            if os.path.isfile(profile_path):
                result_paths.append(os.path.abspath(profile_path))
                profile_number += 1
            else:
                # Exit loop if the folder doesn't exist
                break

        return result_paths

    def modify_preference_file(self, file_path):
        """
        Modifies a JSON file with specific conditions and updates the data.

        Args:
            file_path (str): The path to the JSON file (no extension).

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the required keys are not found in the JSON structure.
        """
        # close browsers first
        self.check_and_close_browser()

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        # Read the original file and create a temporary copy
        temp_file = file_path + ".json"
        shutil.copyfile(file_path, temp_file)

        try:
            # Load JSON content
            with open(temp_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Navigate to required keys
            profile = data.get("profile", {})
            content_settings = profile.get("content_settings", {})
            exceptions = content_settings.get("exceptions", {})
            media_stream_camera = exceptions.get("media_stream_camera", {})
            media_stream_mic = exceptions.get("media_stream_mic", {})

            # Ensure the required keys exist
            if not (exceptions or media_stream_camera) or not (exceptions or media_stream_mic):
                raise ValueError("Required keys 'media_stream_camera' and 'media_stream_mic' do not exist.")

            # Data to add or update
            update_data = {
                "setting": 1,
            }

            # Update or add the key in media_stream_camera
            if SITE_URL_KEY in media_stream_camera:
                media_stream_camera[SITE_URL_KEY]["setting"] = 1
            else:
                media_stream_camera[SITE_URL_KEY] = update_data

            # Update or add the key in media_stream_mic
            if SITE_URL_KEY in media_stream_mic:
                media_stream_mic[SITE_URL_KEY]["setting"] = 1
            else:
                media_stream_mic[SITE_URL_KEY] = update_data

            # Save back to the original file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        except (json.JSONDecodeError, ValueError) as e:
            # Restore original file in case of error
            shutil.copyfile(temp_file, file_path)
            raise e

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def set_browser_permissions(self):
        """Grant microphone and camera access to the site in every browser."""
        for browser_name, base_path in self._chromium_browser_paths():
            try:
                if os.path.exists(base_path):
                    for preference in self.find_preferences_files(base_path):
                        self.modify_preference_file(preference)
            except Exception as e:
                logger.debug("Could not set %s permissions: %s", browser_name, e)

        # For Firefox
        try:
            self.set_firefox_permissions()
        except Exception as e:
            logger.debug("Could not set Firefox permissions: %s", e)

    def is_browser_permissions_allowed(self):
        permissions_allowed = False

        # Check the Chromium based browsers (Edge, Chrome, Brave)
        for browser_name, base_path in self._chromium_browser_paths():
            try:
                if os.path.exists(base_path):
                    for preference in self.find_preferences_files(base_path):
                        if not self.check_preference_file_settings(preference):
                            return
                permissions_allowed = True
            except Exception as e:
                # Silently skip if the browser is not installed or an error occurs
                logger.debug("Could not check %s permissions: %s", browser_name, e)

        # Check Firefox
        try:
            appdata = os.getenv('APPDATA')
            for profile in self._read_firefox_profiles():
                if 'Path' not in profile:
                    continue

                profile_dir = self._firefox_profile_dir(profile, appdata)
                permissions_file = os.path.join(profile_dir, FIREFOX_PERMISSIONS_DB)
                if not os.path.exists(permissions_file):
                    continue

                conn = sqlite3.connect(permissions_file)
                c = conn.cursor()
                # Check if permissions table exists
                c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moz_perms'")
                if c.fetchone():
                    c.execute('SELECT permission FROM moz_perms WHERE origin=? AND type=?', (SITE_URL, 'microphone'))
                    mic_permission = c.fetchone()
                    c.execute('SELECT permission FROM moz_perms WHERE origin=? AND type=?', (SITE_URL, 'camera'))
                    cam_permission = c.fetchone()
                    if mic_permission and mic_permission[0] == 1 and cam_permission and cam_permission[0] == 1:
                        permissions_allowed = True
                conn.close()
        except Exception as e:
            # Silently skip if Firefox is not installed or an error occurs
            logger.debug("Could not check Firefox permissions: %s", e)

        return permissions_allowed

    def check_and_close_browser(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Check if the process name matches any browser executable
                if proc.info['name'] in BROWSER_PROCESS_NAMES:
                    proc.terminate()  # Terminate the browser process
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def check_preference_file_settings(self, file_path):
        """
        Checks a JSON file with specific conditions

        Args:
            file_path (str): The path to the JSON file (no extension).

        Raises:
            ValueError: If the required keys are not found in the JSON structure.
        """
        if not os.path.isfile(file_path):
            return

        try:
            # Load JSON content
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Navigate to required keys
            profile = data.get("profile", {})
            content_settings = profile.get("content_settings", {})
            exceptions = content_settings.get("exceptions", {})
            media_stream_camera = exceptions.get("media_stream_camera", {})
            media_stream_mic = exceptions.get("media_stream_mic", {})

            # Ensure the required keys exist
            if not (exceptions or media_stream_camera) or not (exceptions or media_stream_mic):
                return

            camera_perm = False
            mic_perm = False

            # Update or add the key in media_stream_camera
            if SITE_URL_KEY in media_stream_camera:
                camera_perm = media_stream_camera[SITE_URL_KEY]["setting"] == 1

            if SITE_URL_KEY in media_stream_mic:
                mic_perm = media_stream_mic[SITE_URL_KEY]["setting"] == 1

            return camera_perm and mic_perm

        except Exception as e:
            logger.debug("Could not read preference file %s: %s", file_path, e)
            return

    def _read_firefox_profiles(self):
        """Parse profiles.ini and return the list of profile dictionaries."""
        appdata = os.getenv('APPDATA')
        profiles_ini_path = os.path.join(appdata, *FIREFOX_PROFILES_INI)
        if not os.path.exists(profiles_ini_path):
            return []

        with open(profiles_ini_path, 'r') as f:
            lines = f.readlines()

        profiles = []
        current_profile = {}
        for line in lines:
            line = line.strip()
            if line.startswith('['):
                if current_profile:
                    profiles.append(current_profile)
                    current_profile = {}
            elif '=' in line:
                key, value = line.split('=', 1)
                current_profile[key.strip()] = value.strip()
        if current_profile:
            profiles.append(current_profile)

        return profiles

    def _firefox_profile_dir(self, profile, appdata):
        """Resolve the on-disk directory of a Firefox profile."""
        profile_path = profile['Path']
        is_relative = profile.get('IsRelative', '1') == '1'
        if is_relative:
            return os.path.join(appdata, *FIREFOX_USER_DIR, profile_path)
        return profile_path

    def set_firefox_permissions(self):
        # Kill Firefox processes if running to avoid conflicts with database access
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'firefox' in proc.info['name'].lower():
                proc.terminate()
        # Wait for processes to terminate
        time.sleep(2)

        appdata = os.getenv('APPDATA')
        profiles_ini_path = os.path.join(appdata, *FIREFOX_PROFILES_INI)
        if not os.path.exists(profiles_ini_path):
            return

        # Now, for each profile, modify the permissions
        for profile in self._read_firefox_profiles():
            if 'Path' not in profile:
                continue

            profile_dir = self._firefox_profile_dir(profile, appdata)
            permissions_file = os.path.join(profile_dir, FIREFOX_PERMISSIONS_DB)
            if not os.path.exists(permissions_file):
                continue

            # Copy permissions.sqlite to a temporary file
            temp_permissions_file = os.path.join(tempfile.gettempdir(), FIREFOX_PERMISSIONS_DB)
            shutil.copy2(permissions_file, temp_permissions_file)
            # Connect to the SQLite database
            conn = sqlite3.connect(temp_permissions_file)
            c = conn.cursor()
            # Check if permissions table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moz_perms'")
            if c.fetchone():
                # Insert or replace permission
                # permission values: 1=Allow, 2=Deny, 3=Prompt
                permissions = [
                    (SITE_URL, 'microphone', 1),
                    (SITE_URL, 'camera', 1)
                ]
                for host, type_, permission in permissions:
                    c.execute(
                        'REPLACE INTO moz_perms (origin, type, permission, expireType, expireTime, modificationTime) VALUES (?,?,?,?,?,?)',
                        (host, type_, permission, 0, 0, int(time.time() * 1000)))
                conn.commit()
            conn.close()
            # Copy the temp file back to the original
            shutil.copy2(temp_permissions_file, permissions_file)
            os.remove(temp_permissions_file)

        return True
