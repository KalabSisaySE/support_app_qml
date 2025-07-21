import cloudscraper
import string
import random
import requests  # Still needed for the external call to online.macrosoft.sk


class RtmpUrlGenerator:
    # --- Class-level constants for better organization ---
    PEERTUBE_URL = "https://mtube.macrosoft.sk"
    CLIENT_ID = "o676u80y1lfwh4xdo6neo7nova4av7t0"
    CLIENT_SECRET = "sHIFWMO06HmJnhDcWHe71v2BRLX1OaQQ"
    PEERTUBE_USERNAME = "root"
    PEERTUBE_PASSWORD = "Test123***/"

    # External service URL
    SAVE_URL = "https://online.macrosoft.sk/save/peertube/url/"
    UPLOAD_URL = "https://online.macrosoft.sk/upload/recording/obs/"

    def __init__(self, video_name=None, lectoure_data=None):
        """
        Initializes the generator.
        - video_name (str, optional): The desired name for the video. Will be sanitized.
        - lectoure_data (dict, optional): Data for external service integration.
        """
        self.scraper = cloudscraper.create_scraper()
        self.token = self._get_token()
        self.video_id = None  # Will be set to the video's UUID after creation

        self.lectoure_data = lectoure_data if lectoure_data else {}

        # Sanitize the video name to meet API requirements (3-20 characters)
        raw_name = video_name if video_name else self._generate_random_name()
        self.video_name = self._sanitize_video_name(raw_name)

    def _sanitize_video_name(self, name):
        """Ensures the video name is between 3 and 20 characters long."""
        # Truncate to a maximum of 20 characters
        sanitized = name[:20]
        # Pad with a character if it's less than 3 characters
        if len(sanitized) < 3:
            sanitized = sanitized.ljust(3, '_')
        return sanitized

    def _get_token(self):
        """Fetches the OAuth2 access token using direct API call."""
        token_url = f"{self.PEERTUBE_URL}/api/v1/users/token"
        payload = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "grant_type": "password",
            "response_type": "token",  # CORRECTED: Was 'code', must be 'token'
            "username": self.PEERTUBE_USERNAME,
            "password": self.PEERTUBE_PASSWORD
        }
        try:
            print("Step 1: Requesting access token...")
            response = self.scraper.post(token_url, data=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            access_token = response.json().get("access_token")
            if access_token:
                print("✅ Token received successfully!\n")
                return access_token
            else:
                print("❌ Failed to get access token from response.")
                return None
        except Exception as e:
            print(f"❌ Exception when fetching token: {e}")
            return None

    def _create_video(self):
        """Creates a live video placeholder using a direct API call."""
        if not self.token:
            print("Cannot create video: No access token.")
            return None

        create_url = f"{self.PEERTUBE_URL}/api/v1/videos/live"
        headers = {"Authorization": f"Bearer {self.token}"}
        video_data = {
            'channelId': 1,
            'name': self.video_name,
            'saveReplay': True,
        }

        try:
            print(f"Step 2: Creating live video with name '{self.video_name}'...")
            response = self.scraper.post(create_url, json=video_data, headers=headers)
            response.raise_for_status()

            video_info = response.json().get('video', {})
            video_uuid = video_info.get('uuid')

            if video_uuid:
                print(f"✅ Live video created successfully! (UUID: {video_uuid})\n")
                self.video_id = video_uuid  # Store the UUID
                self.save_video_uuid(video_uuid)  # Call the save hook
                return video_uuid
            else:
                print("❌ Video created, but UUID not found in response.")
                return None
        except Exception as e:
            print(f"❌ Exception when creating live video: {e}")
            if 'response' in locals(): print(f"Response Body: {response.text}")
            return None

    def get_rtmp_url(self):
        """
        The main public method. Creates a video and returns its RTMP URL and Stream Key.
        Returns:
            list: A list containing [rtmp_url, stream_key], or None if failed.
        """
        video_uuid = self._create_video()
        if not video_uuid:
            return None

        info_url = f"{self.PEERTUBE_URL}/api/v1/videos/live/{video_uuid}"
        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            print(f"Step 3: Fetching info for live video UUID {video_uuid}...")
            response = self.scraper.get(info_url, headers=headers)
            response.raise_for_status()

            live_info = response.json()
            rtmp_url = live_info.get('rtmpUrl')
            stream_key = live_info.get('streamKey')

            if rtmp_url and stream_key:
                print("✅ RTMP details fetched successfully!")
                return [rtmp_url, stream_key]
            else:
                print("❌ Failed to find RTMP details in the response.")
                return None
        except Exception as e:
            print(f"❌ Exception when fetching RTMP details: {e}")
            if 'response' in locals(): print(f"Response Body: {response.text}")
            return None

    def _generate_random_name(self, length=12):
        """Generates a random name for the video."""
        allowed_chars = string.ascii_lowercase + string.digits
        return ''.join(random.choices(allowed_chars, k=length))

    def save_video_uuid(self, video_uuid):
        """Saves the video UUID to an external service."""
        if not self.lectoure_data:
            return

        try:
            print(f"Saving video UUID to external service...")
            data = {
                "class_type": self.lectoure_data.get('class_type'),
                "class_id": self.lectoure_data.get('class_id'),
                "room_id": self.lectoure_data.get('room_id'),
                "lectoure_id": self.lectoure_data.get('lectoure_id'),
                "video_uuid": video_uuid,
            }
            headers = {'Content-Type': 'application/json'}
            # Using standard requests here as the external service may not need cloudscraper
            res = requests.post(self.SAVE_URL, headers=headers, json=data)
            print(f"Save response status: {res.status_code}")
        except Exception as e:
            print(f"❌ Error while saving video uuid: {e}")

    def upload_recording_to_vimeo(self):
        """Triggers video upload to an external service once recording is complete."""
        if not (self.lectoure_data and self.video_id):
            print("Skipping upload: Missing lecture data or video ID.")
            return

        try:
            print(f"Triggering upload for video {self.video_id}...")
            data = {
                "class_type": self.lectoure_data.get('class_type'),
                "class_id": self.lectoure_data.get('class_id'),
                "room_id": self.lectoure_data.get('room_id'),
                "lectoure_id": self.lectoure_data.get('lectoure_id'),
                "video_url": f"{self.PEERTUBE_URL}/videos/embed/{self.video_id}",
                "video_name": self.video_name,
            }
            headers = {'Content-Type': 'application/json'}
            res = requests.post(self.UPLOAD_URL, headers=headers, json=data)
            print(f"Upload trigger response status: {res.status_code}")
        except Exception as e:
            print(f"❌ Error while triggering recording upload: {e}")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Running Test 1: Generate with a random name ---")
    generator = RtmpUrlGenerator()
    rtmp_details = generator.get_rtmp_url()

    if rtmp_details:
        print("\n--- FINAL RESULT ---")
        print(f"RTMP URL:   {rtmp_details[0]}")
        print(f"Stream Key: {rtmp_details[1]}")
        print("--------------------\n")
        # Example of calling the other method
        generator.upload_recording_to_vimeo()
    else:
        print("\n--- FAILED TO GET RTMP DETAILS ---")

    print("\n--- Running Test 2: Provide a custom (long) name ---")
    # This name is too long and will be automatically truncated
    long_name = "this_is_a_very_long_video_name_that_exceeds_the_limit"
    generator_2 = RtmpUrlGenerator(video_name=long_name)
    generator_2.get_rtmp_url()

    print("\n--- Running Test 3: Provide a custom (short) name ---")
    # This name is too short and will be automatically padded
    short_name = "hi"
    generator_3 = RtmpUrlGenerator(video_name=short_name)
    generator_3.get_rtmp_url()