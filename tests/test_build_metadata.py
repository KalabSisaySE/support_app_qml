from build_project import render_installer_script, render_version_info
from support_app.version import __version__, version_string, version_tuple


def test_version_tuple_is_four_parts():
    assert version_tuple() == (1, 0, 0, 0)
    assert version_string() == "1.0.0.0"


def test_render_version_info_uses_version_module(tmp_path):
    output = render_version_info(
        "config_files/version_info_main.txt", tmp_path / "version_info.txt"
    )
    text = output.read_text(encoding="utf-8")

    assert f"filevers={version_tuple()}" in text
    assert f"prodvers={version_tuple()}" in text
    assert f"StringStruct('FileVersion', '{version_string()}')" in text
    assert f"StringStruct('ProductVersion', '{version_string()}')" in text


def test_render_installer_script_uses_version_module(tmp_path):
    output = render_installer_script(
        "config_files/installer.iss", tmp_path / "installer.iss"
    )
    text = output.read_text(encoding="utf-8")

    assert f"AppVersion={__version__}" in text
    assert "AppName=Macrosoft Support" in text
