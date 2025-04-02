import requests
import peertube
import string
import random

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

