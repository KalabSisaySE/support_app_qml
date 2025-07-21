import requests
import peertube
import string
import random

class RtmpUrlGenerator:

    def __init__(self, video_name=None, lectoure_data=None):
        self.token = self.get_token()
        self.video_id = ""

        self.lectoure_data = lectoure_data if lectoure_data else {}
        self.video_name = video_name if video_name else self.generate_random_name()

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
                self.video_id = video_uuid

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

                    return [rtmp_url, stream_key]

                except Exception as e:
                    print("Exception when calling LiveVideosApi->videos_live_id_get: %s\n" % e)

    def generate_random_name(self, prefix="random_", suffix_length=8):
        allowed_chars = string.ascii_lowercase + '_'
        suffix = ''.join(random.choices(allowed_chars, k=suffix_length))

        return prefix + suffix

    def save_video_uuid(self, video_uuid):
        try:
            if self.lectoure_data:
                print(f"\n\tlectoure_data exists: {self.lectoure_data}\n")
                data = {
                    "class_type": self.lectoure_data.get('class_type'),
                    "class_id": self.lectoure_data.get('class_id'),
                    "room_id": self.lectoure_data.get('room_id'),
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

    def upload_recording_to_vimeo(self):
        """tiggers video upload to vimeo once recording is complete"""
        try:
            if self.lectoure_data and self.video_id:

                data = {
                    "class_type": self.lectoure_data.get('class_type'),
                    "class_id": self.lectoure_data.get('class_id'),
                    "room_id": self.lectoure_data.get('room_id'),
                    "lectoure_id": self.lectoure_data.get('lectoure_id'),
                    "video_url": f"https://mtube.macrosoft.sk/videos/embed/{self.video_id}",
                    "video_name": self.video_name,
                }

                headers = {'Content-Type': 'application/json'}
                res = requests.post("https://online.macrosoft.sk/upload/recording/obs/", headers=headers, json=data)
                print(f"\n\tres: {res.status_code}\n")
                print(f"\n\tres json: {res.json()}\n")
        except Exception as e:
            print(f"error while uploading recording {e}")
            pass


import cloudscraper
import json

# --- Your credentials and initial setup ---
PEERTUBE_URL = "https://mtube.macrosoft.sk"
CLIENT_ID = "o676u80y1lfwh4xdo6neo7nova4av7t0"
CLIENT_SECRET = "sHIFWMO06HmJnhDcWHe71v2BRLX1OaQQ"
USERNAME = "root"
PASSWORD = "Test123***/"

access_token = None
video_id = None
scraper = cloudscraper.create_scraper()

# --- Step 1: Get Access Token ---
try:
    print("Step 1: Requesting access token...")
    token_url = f"{PEERTUBE_URL}/api/v1/users/token"
    payload = {
        'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET,
        'grant_type': 'password', 'response_type': 'token',
        'username': USERNAME, 'password': PASSWORD
    }
    response = scraper.post(token_url, data=payload)
    response.raise_for_status()
    access_token = response.json().get('access_token')
    print("✅ Token received successfully!\n")
except Exception as e:
    print(f"❌ Error fetching token: {e}")
    if 'response' in locals() and hasattr(response, 'text'): print(f"Response: {response.text}")
    # Exit if we can't get a token
    exit()

# --- Step 2: Create Live Video ---
if access_token:
    try:
        print("Step 2: Creating live video...")
        live_video_url = f"{PEERTUBE_URL}/api/v1/videos/live"
        headers = {"Authorization": f"Bearer {access_token}"}
        video_data = {
            'channelId': 1,
            'name': 'Live Stream via REST API',
            'saveReplay': True,
        }
        response = scraper.post(live_video_url, json=video_data, headers=headers)
        response.raise_for_status()

        video_resp = response.json()
        # Get the ID of the video we just created from the actual response structure
        video_id = video_resp['video']['id']
        print(f"✅ Live video created successfully! (ID: {video_id})\n")

    except Exception as e:
        print(f"❌ Error creating live video: {e}")
        if 'response' in locals() and hasattr(response, 'text'): print(f"Response: {response.text}")

# --- Step 3: Get Live Video Info using its ID ---
if video_id:
    try:
        print(f"Step 3: Fetching info for live video ID {video_id}...")
        # Construct the URL with the video ID
        info_url = f"{PEERTUBE_URL}/api/v1/videos/live/{video_id}"
        headers = {"Authorization": f"Bearer {access_token}"}

        # Make the GET request (no `data` or `json` payload needed)
        response = scraper.get(info_url, headers=headers)
        response.raise_for_status()

        live_info = response.json()

        # Extract the details from the response of this third call
        rtmp_url = live_info.get('rtmpUrl')
        stream_key = live_info.get('streamKey')

        print("\n--- Streaming Details ---")
        print(f"RTMP URL:   {rtmp_url}")
        print(f"Stream Key: {stream_key}")
        print("-------------------------")

    except Exception as e:
        print(f"❌ Error fetching live video info: {e}")
        if 'response' in locals() and hasattr(response, 'text'): print(f"Response: {response.text}")