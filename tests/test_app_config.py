from support_app import app_config


def test_identity_is_lazy():
    app_config.reset_identity_cache()
    assert "NAME" not in vars(app_config)
    assert "EXE_NAME" not in vars(app_config)


def test_identity_for_client(monkeypatch):
    monkeypatch.setattr(app_config, "get_user_type", lambda: "client")

    assert app_config.NAME == "MacrosoftConnectQuickSupport"
    assert app_config.EXE_NAME == "macrosoftconnectquicksupport"


def test_identity_for_lectoure(monkeypatch):
    monkeypatch.setattr(app_config, "get_user_type", lambda: "lectoure")

    assert app_config.NAME == "MacrosoftConnect"
    assert app_config.EXE_NAME == "macrosoftconnect"


def test_identity_is_cached(monkeypatch):
    calls = []

    def fake_user_type():
        calls.append(1)
        return "lectoure"

    monkeypatch.setattr(app_config, "get_user_type", fake_user_type)

    assert app_config.NAME == app_config.NAME
    assert len(calls) == 1


def test_reset_identity_cache(monkeypatch):
    monkeypatch.setattr(app_config, "get_user_type", lambda: "lectoure")
    assert app_config.NAME == "MacrosoftConnect"

    app_config.reset_identity_cache()

    assert "NAME" not in vars(app_config)


def test_is_version_string():
    assert app_config.is_version_string("31.1.2")
    assert app_config.is_version_string(" 1 ")
    assert not app_config.is_version_string("v31.1.2")
    assert not app_config.is_version_string("")
