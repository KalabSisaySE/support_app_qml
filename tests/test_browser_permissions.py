import json

from support_app.browser_permission_manager import (
    SITE_URL_KEY,
    BrowserPermissionManager,
)


def write_preferences(path, camera=1, microphone=1):
    data = {
        "profile": {
            "content_settings": {
                "exceptions": {
                    "media_stream_camera": {SITE_URL_KEY: {"setting": camera}},
                    "media_stream_mic": {SITE_URL_KEY: {"setting": microphone}},
                }
            }
        }
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_preference_allows_site(tmp_path):
    path = write_preferences(tmp_path / "Preferences")

    assert BrowserPermissionManager().check_preference_file_settings(str(path)) is True


def test_preference_denies_when_camera_disabled(tmp_path):
    path = write_preferences(tmp_path / "Preferences", camera=2)

    assert BrowserPermissionManager().check_preference_file_settings(str(path)) is False


def test_invalid_preference_file_is_logged(tmp_path, caplog):
    path = tmp_path / "Preferences"
    path.write_text("{invalid", encoding="utf-8")

    with caplog.at_level("DEBUG"):
        result = BrowserPermissionManager().check_preference_file_settings(str(path))

    assert result is None
    assert "Could not read preference file" in caplog.text


def test_read_firefox_profiles(tmp_path, monkeypatch):
    appdata = tmp_path / "appdata"
    firefox_dir = appdata / "Mozilla" / "Firefox"
    firefox_dir.mkdir(parents=True)
    (firefox_dir / "profiles.ini").write_text(
        "[Profile0]\nName=default\nIsRelative=1\nPath=Profiles/abc.default\n\n"
        "[Profile1]\nName=other\nIsRelative=0\nPath=C:/profiles/other\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("APPDATA", str(appdata))

    manager = BrowserPermissionManager()
    profiles = manager._read_firefox_profiles()

    assert [profile["Name"] for profile in profiles] == ["default", "other"]
    assert manager._firefox_profile_dir(profiles[0], str(appdata)).endswith(
        "Profiles/abc.default"
    )
    assert manager._firefox_profile_dir(profiles[1], str(appdata)) == "C:/profiles/other"


def test_missing_firefox_profiles_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))

    assert BrowserPermissionManager()._read_firefox_profiles() == []
