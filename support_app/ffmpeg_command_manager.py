import io
from datetime import datetime
import shutil
import os
from PySide6.QtGui import QGuiApplication
import subprocess
import re
import urllib.request
import peertube
import random
import string
import platform
import tempfile
import zipfile
import requests
from pathlib import Path

def download_file(url, target_path, progress_callback=None):
    try:
        with urllib.request.urlopen(url) as response:
            total_size = int(response.getheader('Content-Length', '0'))
            downloaded = 0
            block_size = 8192
            with open(target_path, 'wb') as out_file:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    out_file.write(buffer)
                    downloaded += len(buffer)
                    if total_size > 0 and progress_callback:
                        progress_callback(int(downloaded * 100 / total_size))
        return True
    except Exception as e:
        print(f"Chyba pri sťahovaní súboru ({url}): {e}")
        return False


class RtmpUrlGenerator:
    def __init__(self, video_name=None, lectoure_data=None):
        self.token = self.get_token()
        if not lectoure_data:
            self.lectoure_data = {}
        else:
            self.lectoure_data = lectoure_data

        if video_name:
            self.video_name = video_name
        else:
            self.video_name = self.generate_random_name()

    def get_token(self):
        url = "https://mtube.macrosoft.sk/api/v1/users/token"

        data = {
            "client_id": "o676u80y1lfwh4xdo6neo7nova4av7t0",
            "client_secret": "sHIFWMO06HmJnhDcWHe71v2BRLX1OaQQ",
            "grant_type": "password",
            "response_type": "code",
            "username": "root",
            "password": "Test123***/"
        }

        try:
            response = requests.post(url, data=data)
            return response.json().get("access_token")
        except Exception as e:
            pass

    def get_configuration(self):
        configuration = peertube.Configuration(host="https://mtube.macrosoft.sk/api/v1")
        configuration.access_token = self.token

        return configuration

    def create_video(self):
        configuration = self.get_configuration()

        with peertube.ApiClient(configuration) as api_client:
            api_instance = peertube.LiveVideosApi(api_client)
            channel_id = 1

            name = self.video_name
            save_replay = True

            try:
                api_response = api_instance.videos_live_post(channel_id, name, save_replay=save_replay)
                video_uuid = api_response.video.uuid
                self.save_video_uuid(video_uuid)

                return video_uuid

            except Exception as e:
                print("Exception when calling LiveVideosApi->videos_live_post: %s\n" % e)

    def get_rtmp_url(self):
        configuration = self.get_configuration()
        video_id = self.create_video()

        if video_id:
            with peertube.ApiClient(configuration) as api_client:
                api_instance = peertube.LiveVideosApi(api_client)

                try:
                    api_response = api_instance.videos_live_id_get(video_id)
                    rtmp_url = api_response.rtmp_url
                    stream_key = api_response.stream_key

                    return f"{rtmp_url}/{stream_key}"

                except Exception as e:
                    print("Exception when calling LiveVideosApi->videos_live_id_get: %s\n" % e)

    def generate_random_name(self, prefix="random_", suffix_length=8):
        allowed_chars = string.ascii_lowercase + '_'
        suffix = ''.join(random.choices(allowed_chars, k=suffix_length))

        return prefix + suffix

    def save_video_uuid(self, video_uuid):
        print(f"\n\tsave_video_uuid called\n")
        try:
            if self.lectoure_data:
                print(f"\n\tlectoure_data exists: {self.lectoure_data}\n")
                data = {
                    "class_type": self.lectoure_data.get('class_type'),
                    "class_id": self.lectoure_data.get('class_id'),
                    "lectoure_id": self.lectoure_data.get('lectoure_id'),
                    "video_uuid": video_uuid,
                }
                print(f"\n\tdata: {data}\n")
                headers = {'Content-Type': 'application/json'}
                res = requests.post("https://online.macrosoft.sk/save/peertube/url/", headers=headers, json=data)
                print(f"\n\tres: {res.status_code}\n")
                print(f"\n\tres json: {res.json()}\n")
        except Exception as e:
            print(f"error while saving video uuid: {e}")
            pass



class FFmpegCommandGenerator:
    def __init__(self, mic_device=None, fixed_resolution="1920x1080", file_name=None, lectoure_data=None):
        self.file_name = file_name
        self.lectoure_data = lectoure_data
        now = datetime.now()

        # Skontrolujeme, či ffmpeg.exe je dostupný. Ak nie, stiahne sa s priebehom.
        self.ensure_ffmpeg()
        self.ffmpeg = shutil.which("ffmpeg")

        # Pokračujeme v pôvodnej inicializácii.
        audio_devices = self.get_dshow_audio_devices()
        audio_device = None

        if mic_device:
            if mic_device in audio_devices:
                audio_device = mic_device
            elif audio_devices:
                audio_device = audio_devices[0]
        elif audio_devices:
            audio_device = audio_devices[0]
        self.config = {
            'system_audio_device': None,
            'mic_device': audio_device,
            'preset': "fast",
            'output_file': f"output_{now.strftime('%d.%m.%Y.%H.%M.%S')}.mp4",
            'resolution': fixed_resolution,
            'fps': 30,
        }

    def get_screen_resolution(self):
        # Check if a QGuiApplication instance already exists
        app = QGuiApplication.instance()
        if not app:
            # If not, create one. Pass empty list to avoid unnecessary arguments.
            app = QGuiApplication([])

        # Get the primary screen
        screen = app.primaryScreen()
        if screen is not None:
            # Retrieve the size of the screen
            size = screen.size()
            width = size.width()
            height = size.height()
            return f"{width}x{height}"
        else:
            return "1920x1080"

    def get_dshow_audio_devices(self):
        print(self.ffmpeg)
        command = [self.ffmpeg, '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
        result = subprocess.run(command, stderr=subprocess.PIPE, text=True, check=False)
        return re.findall(r'\[dshow.*?\] "(.*?)" \(audio\)', result.stderr)

    def build_command(self, output_to="rtmp"):
        config = self.config
        cmd = [
            self.ffmpeg,
            '-y',
            '-f', 'gdigrab',
            '-framerate', str(config['fps']),
            '-video_size', config['resolution'],
            '-i', 'desktop',
        ]
        audio_inputs = []
        if config['system_audio_device']:
            cmd += ['-f', 'wasapi', '-i', config['system_audio_device']]
            audio_inputs.append(1)
        if config['mic_device']:
            cmd += ['-f', 'dshow', '-i', f"audio={config['mic_device']}"]
            audio_inputs.append(2 if config['system_audio_device'] else 1)
        cmd += ['-c:v', 'libx264', '-preset', config['preset'], '-crf', '23', '-pix_fmt', 'yuv420p']
        if len(audio_inputs) == 2:
            cmd += ['-filter_complex', f'[{audio_inputs[0]}:a][{audio_inputs[1]}:a]amix=inputs=2[a]',
                    '-map', '0:v', '-map', '[a]']
        elif len(audio_inputs) == 1:
            cmd += ['-map', '0:v', '-map', f'{audio_inputs[0]}:a']
        else:
            cmd += ['-map', '0']
        cmd += ['-c:a', 'aac', '-b:a', '192k', '-ac', '2']

        # output
        rtmp_url_generator = RtmpUrlGenerator(self.file_name, self.lectoure_data)
        rtmp_url = rtmp_url_generator.get_rtmp_url()

        if output_to == "rtmp" and rtmp_url:
            cmd += ['-f', 'flv', rtmp_url]
        else:
            cmd += [config['output_file']]

        return cmd

    def ensure_ffmpeg(self):
        """
        Ensure FFmpeg is available in system PATH.
        Installs to temp directory if missing and adds to PATH.
        Returns True if FFmpeg is available, False otherwise.
        """
        # Check if FFmpeg is already available
        ffmpeg_executable = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'
        ffmpeg_path = shutil.which('ffmpeg')

        # Verify if found path actually exists and is executable
        if ffmpeg_path and Path(ffmpeg_path).exists():
            try:
                subprocess.run([ffmpeg_path, '-version'], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except (subprocess.CalledProcessError, PermissionError):
                pass

        # Platform-specific installation handling
        system = platform.system()
        temp_dir = Path(tempfile.gettempdir()) / 'ffmpeg_bin'
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Check if we already have a downloaded version
        downloaded_ffmpeg = temp_dir / ffmpeg_executable
        if downloaded_ffmpeg.exists():
            try:
                subprocess.run([str(downloaded_ffmpeg), '-version'], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.environ['PATH'] = f"{temp_dir}{os.pathsep}{os.environ['PATH']}"
                return True
            except (subprocess.CalledProcessError, PermissionError):
                downloaded_ffmpeg.unlink()

        # Download FFmpeg if not found
        if system == 'Windows':
            ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            try:
                response = requests.get(ffmpeg_url, timeout=10)
                response.raise_for_status()

                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    for member in zip_ref.namelist():
                        if member.endswith('ffmpeg.exe'):
                            zip_ref.extract(member, temp_dir)
                            (temp_dir / member).rename(downloaded_ffmpeg)

                # Verify downloaded binary
                subprocess.run([str(downloaded_ffmpeg), '-version'], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                # Add to PATH for current process
                os.environ['PATH'] = f"{temp_dir}{os.pathsep}{os.environ['PATH']}"
                return True

            except Exception as e:
                print(f"Failed to download FFmpeg: {str(e)}")
                return False

        else:  # Linux/macOS
            print("Please install FFmpeg using your system package manager:")
            print("\nFor Debian/Ubuntu:")
            print("sudo apt install ffmpeg")
            print("\nFor macOS (using Homebrew):")
            print("brew install ffmpeg")
            return False
# ───────────── Global premená pre priebeh sťahovania ffmpeg ─────────────
download_progress_callback = None  # Bude nastavená v TkApp.__init__
