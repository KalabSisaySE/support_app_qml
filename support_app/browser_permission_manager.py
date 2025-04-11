import os
import json
import psutil
import shutil
import sqlite3
import tempfile
import time



class BrowserPermissionManager:
    """manages browser permissions"""

    def __init__(self, log_message=None):
        self.user_account = None

        try:
            self.user_account = os.getlogin()
        except:
            pass

        if self.user_account:
            self.chrome_basepath = f"C:\\Users\\{self.user_account}\\AppData\\Local\\Google\\Chrome\\"
            self.brave_basepath = f"C:\\Users\\{self.user_account}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\"
            self.edge_basepath = f"C:\\Users\\{self.user_account}\\AppData\\Local\\Microsoft\\Edge\\"
        else:
            self.chrome_basepath = ""
            self.brave_basepath = ""
            self.edge_basepath = ""

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
            url_key = "https://online.macrosoft.sk:443,*"
            # update_data = {
            #     "last_modified": "13379863098972389",
            #     "last_used": "13379863095987050",
            #     "last_visit": "13379385600000000",
            #     "setting": 1,
            # }

            update_data = {
                "setting": 1,
            }

            # Update or add the key in media_stream_camera
            if url_key in media_stream_camera:
                media_stream_camera[url_key]["setting"] = 1
            else:
                media_stream_camera[url_key] = update_data

            # Update or add the key in media_stream_mic
            if url_key in media_stream_mic:
                media_stream_mic[url_key]["setting"] = 1
            else:
                media_stream_mic[url_key] = update_data

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
        # URL to allow
        site_url = 'https://online.macrosoft.sk'

        # For Edge
        try:
            if os.path.exists(self.edge_basepath):
                edge_preferences = self.find_preferences_files(self.edge_basepath)

                for preference in edge_preferences:
                    self.modify_preference_file(preference)
        except Exception as e:
            pass

        # For Chrome
        try:
            if os.path.exists(self.chrome_basepath):
                chrome_preferences = self.find_preferences_files(self.chrome_basepath)

                for preference in chrome_preferences:
                    self.modify_preference_file(preference)
        except Exception as e:
            pass

        # For Brave (Brave uses Chromium policies)
        try:
            if os.path.exists(self.brave_basepath):
                brave_preferences = self.find_preferences_files(self.brave_basepath)

                for preference in brave_preferences:
                    self.modify_preference_file(preference)
        except Exception as e:
            pass

        # For Firefox
        try:
            self.set_firefox_permissions()
        except Exception as e:
            pass


    def is_browser_permissions_allowed(self):
        site_url = 'https://online.macrosoft.sk'
        permissions_allowed = False

        # Check Edge
        try:
            if os.path.exists(self.edge_basepath):
                edge_preferences = self.find_preferences_files(self.edge_basepath)
                for preference in edge_preferences:
                    if not self.check_preference_file_settings(preference):
                        return
            permissions_allowed = True
        except:
            pass  # Silently skip if Edge is not installed or error occurs

        # Check Chrome
        try:
            if os.path.exists(self.chrome_basepath):
                chrome_preferences = self.find_preferences_files(self.chrome_basepath)
                for preference in chrome_preferences:
                    if not self.check_preference_file_settings(preference):
                        return
            permissions_allowed = True
        except:
            pass  # Silently skip if Chrome is not installed or error occurs

        # Check Brave
        try:
            if os.path.exists(self.brave_basepath):
                brave_preferences = self.find_preferences_files(self.brave_basepath)
                for preference in brave_preferences:
                    if not self.check_preference_file_settings(preference):
                        return
            permissions_allowed = True
        except:
            pass  # Silently skip if Brave is not installed or error occurs

        # Check Firefox
        try:
            appdata = os.getenv('APPDATA')
            profiles_ini_path = os.path.join(appdata, 'Mozilla', 'Firefox', 'profiles.ini')
            if os.path.exists(profiles_ini_path):
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

                # Now, for each profile, check the permissions
                for profile in profiles:
                    if 'Path' in profile:
                        profile_path = profile['Path']
                        is_relative = profile.get('IsRelative', '1') == '1'
                        if is_relative:
                            profile_dir = os.path.join(appdata, 'Mozilla', 'Firefox', profile_path)
                        else:
                            profile_dir = profile_path
                        permissions_file = os.path.join(profile_dir, 'permissions.sqlite')
                        if os.path.exists(permissions_file):
                            # Connect to the SQLite database
                            conn = sqlite3.connect(permissions_file)
                            c = conn.cursor()
                            # Check if permissions table exists
                            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='moz_perms'")
                            if c.fetchone():
                                c.execute('SELECT permission FROM moz_perms WHERE origin=? AND type=?', (site_url, 'microphone'))
                                mic_permission = c.fetchone()
                                c.execute('SELECT permission FROM moz_perms WHERE origin=? AND type=?', (site_url, 'camera'))
                                cam_permission = c.fetchone()
                                if mic_permission and mic_permission[0] == 1 and cam_permission and cam_permission[0] == 1:
                                    permissions_allowed = True
                            conn.close()
        except:
            pass  # Silently skip if Firefox is not installed or error occurs

        return permissions_allowed

    def check_and_close_browser(self):
        browsers = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe"]
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Check if the process name matches any browser executable
                if proc.info['name'] in browsers:
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

            # Data to add or update
            url_key = "https://online.macrosoft.sk:443,*"

            camera_perm = False
            mic_perm = False

            # Update or add the key in media_stream_camera
            if url_key in media_stream_camera:
                camera_perm = media_stream_camera[url_key]["setting"] == 1

            if url_key in media_stream_mic:
                mic_perm = media_stream_mic[url_key]["setting"] == 1

            return camera_perm and mic_perm

        except Exception as e:
            return

    def set_firefox_permissions(self):
        site_url = 'https://online.macrosoft.sk'

        # Kill Firefox processes if running to avoid conflicts with database access
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'firefox' in proc.info['name'].lower():
                proc.terminate()
        # Wait for processes to terminate
        time.sleep(2)

        appdata = os.getenv('APPDATA')
        profiles_ini_path = os.path.join(appdata, 'Mozilla', 'Firefox', 'profiles.ini')
        if os.path.exists(profiles_ini_path):
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

            # Now, for each profile, modify the permissions
            for profile in profiles:
                if 'Path' in profile:
                    profile_path = profile['Path']
                    is_relative = profile.get('IsRelative', '1') == '1'
                    if is_relative:
                        profile_dir = os.path.join(appdata, 'Mozilla', 'Firefox', profile_path)
                    else:
                        profile_dir = profile_path
                    permissions_file = os.path.join(profile_dir, 'permissions.sqlite')
                    if os.path.exists(permissions_file):
                        # Copy permissions.sqlite to a temporary file
                        temp_permissions_file = os.path.join(tempfile.gettempdir(), 'permissions.sqlite')
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
                                (site_url, 'microphone', 1),
                                (site_url, 'camera', 1)
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
