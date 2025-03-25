import requests
import time


def get_private_video_by_name(instance_url, video_name, token, max_retries=10, delay=1):
    search_url = f"{instance_url}/api/v1/search/videos"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"search": video_name}

    # for _ in range(max_retries):
    response = requests.get(search_url, headers=headers, params=params)
    print(f"\t\t{response.status_code}")
    print(f"\t\t{response.text}")
    if response.status_code == 200:
        videos = response.json()['data']
        for video in videos:
            if video.get('name') == video_name:
                return video
    # time.sleep(delay)

    # return None


# Usage
INSTANCE_URL = "https://mtube.macrosoft.sk"
# VIDEO_NAME = "online_1_26.02.2025.23.35.23"
VIDEO_NAME = ""
TOKEN = "582934b952d7cdeab7d420e1f0dd9d2ffa1068b8"

video = get_private_video_by_name(INSTANCE_URL, VIDEO_NAME, TOKEN)

if video:
    embed_url = f"{INSTANCE_URL}/videos/embed/{video['uuid']}"
    print(f"Embed URL: {embed_url}")
else:
    print("Video not found after retries.")