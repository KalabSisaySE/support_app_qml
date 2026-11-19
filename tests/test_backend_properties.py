import pytest

import support_app.backend as backend_module
from support_app.backend import MacrosoftBackend
from support_app.status import Status


@pytest.fixture
def backend(monkeypatch):
    """Build the backend without starting the initialization worker."""
    monkeypatch.setattr(backend_module, "get_user_type", lambda: "lectoure")
    monkeypatch.setattr(MacrosoftBackend, "app_init", lambda self: None)
    return MacrosoftBackend()


def test_defaults(backend):
    assert backend.is_user_lectoure is True
    assert backend.progress == 0
    assert backend.app_installation_status == Status.DISABLED
    assert backend.is_enable_microphone_only_btn_enabled is True


def test_bool_property_emits_only_on_change(backend):
    changes = []
    backend.openBrowserBtnEnabledChanged.connect(changes.append)

    backend.is_open_browser_btn_enabled = False
    backend.is_open_browser_btn_enabled = False

    assert changes == [False]


def test_username_uses_localized_fallback(backend):
    changes = []
    backend.usernameChanged.connect(changes.append)

    backend.username = ""

    assert backend.username == "Nenájdené"
    assert changes == ["Nenájdené"]


def test_start_button_requires_installation(backend, monkeypatch):
    changes = []
    backend.appStartBtnEnabledChanged.connect(changes.append)
    monkeypatch.setattr(backend_module, "check_installation", lambda: False)

    backend.is_app_start_btn_enabled = True

    assert backend.is_app_start_btn_enabled is False
    assert changes == [False]


def test_start_button_enabled_when_installed(backend, monkeypatch):
    monkeypatch.setattr(backend_module, "check_installation", lambda: True)

    backend.is_app_start_btn_enabled = True

    assert backend.is_app_start_btn_enabled is True


def test_status_property_emits_string_value(backend):
    changes = []
    backend.appInstallationStatusChanged.connect(changes.append)

    backend.app_installation_status = Status.ENABLED

    assert changes == ["enabled"]
    assert backend.app_installation_status == "enabled"
