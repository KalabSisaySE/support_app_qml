import json
import sys

from support_app import settings


def test_extract_installer_code():
    assert settings.extract_installer_code(
        "Installer Path: MacrosoftSupportInstaller_ABC123_.exe"
    ) == "ABC123"
    assert settings.extract_installer_code(
        "macrosoftsupportinstaller_lower_.EXE"
    ) == "lower"
    assert settings.extract_installer_code("unrelated.txt") is None


def test_load_settings_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "CONFIG_FILE_PATH", str(tmp_path / "missing.json"))
    loaded = settings.load_settings()
    assert loaded.is_lectoure is None


def test_load_settings_corrupt_file(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(settings, "CONFIG_FILE_PATH", str(config_path))

    assert settings.load_settings().is_lectoure is None


def test_load_settings_reads_boolean(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"is_lectoure": False}), encoding="utf-8")
    monkeypatch.setattr(settings, "CONFIG_FILE_PATH", str(config_path))

    assert settings.load_settings().is_lectoure is False


def test_load_settings_ignores_non_boolean(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"is_lectoure": "yes"}), encoding="utf-8")
    monkeypatch.setattr(settings, "CONFIG_FILE_PATH", str(config_path))

    loaded = settings.load_settings()
    assert loaded.is_lectoure is None
    assert loaded.dark_theme is None


def test_dark_theme_roundtrip(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr(settings, "CONFIG_FILE_PATH", str(config_path))

    settings.save_settings(settings.AppSettings(dark_theme=False))

    assert settings.load_settings().dark_theme is False
    assert json.loads(config_path.read_text(encoding="utf-8")) == {"dark_theme": False}


def test_save_settings_preserves_unknown_keys(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"unrelated": 42}), encoding="utf-8")
    monkeypatch.setattr(settings, "CONFIG_FILE_PATH", str(config_path))

    settings.save_settings(settings.AppSettings(is_lectoure=True))

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data == {"unrelated": 42, "is_lectoure": True}
    assert settings.load_settings().is_lectoure is True


def test_save_login_info_and_get_access_code(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(tmp_path / "MacrosoftSupport.exe")])

    settings.save_login_info("CODE42")

    contents = (tmp_path / settings.INSTALLER_PATH_FILE_NAME).read_text(encoding="utf-8")
    assert contents == "Installer Path: MacrosoftSupportInstaller_CODE42_.exe\n"
    assert settings.get_access_code() == "CODE42"
