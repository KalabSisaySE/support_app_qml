import requests

# Configuration
INSTANCE_URL = "https://mtube.macrosoft.sk"
# VIDEO_UUID = "e77bf827-3d78-41dc-8292-58836169dd1e"  # Saved from the initial live creation response
VIDEO_UUID = "40b588e3-5407-4dfc-8f57-454d017a48ab"  # Saved from the initial live creation response
TOKEN = "582934b952d7cdeab7d420e1f0dd9d2ffa1068b8"



# Fetch video details with authentication
headers = {"Authorization": f"Bearer {TOKEN}"}
video_url = f"{INSTANCE_URL}/api/v1/videos/{VIDEO_UUID}"
response = requests.get(video_url, headers=headers)

if response.status_code == 200:
    video_details = response.json()
    embed_url = f"{INSTANCE_URL}/videos/embed/{VIDEO_UUID}"
    video_state = video_details.get("state")
    print(f"Embed URL: {embed_url}")
    print("Video State:", video_state)
    print("Video Details:", video_details)
else:
    print(f"Error: {response.status_code}", response.text)