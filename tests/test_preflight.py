import support_app.preflight as preflight


def fake_check(name, value):
    return lambda *args, **kwargs: value if not callable(value) else value(*args, **kwargs)


def patch_checks(monkeypatch, *, installed=True, service=True, obs_installed=True, obs_running=True):
    monkeypatch.setattr(preflight.app_config, "NAME", "MacrosoftConnect", raising=False)
    monkeypatch.setattr(preflight, "check_installation", lambda: installed)
    monkeypatch.setattr(preflight, "is_service_running", lambda name: service)
    monkeypatch.setattr(preflight, "is_obs_installed", lambda: obs_installed)
    monkeypatch.setattr(preflight, "is_obs_running", lambda: obs_running)


def test_collect_checks_includes_websocket_for_lecturer(monkeypatch):
    patch_checks(monkeypatch)

    checks = preflight.collect_checks(
        permission_ok=True, internet_ok=True, websocket_ok=True
    )

    assert [check.label for check in checks] == [
        "Macrosoft Connect je nainštalovaný",
        "Služba MacrosoftConnect beží",
        "OBS je nainštalovaný",
        "OBS beží",
        "Povolenia pre mikrofón, kameru a prehliadač",
        "Pripojenie k support WebSocketu",
        "Pripojenie na internet",
    ]
    assert preflight.all_passed(checks) is True


def test_collect_checks_skips_websocket_for_client(monkeypatch):
    patch_checks(monkeypatch)

    checks = preflight.collect_checks(
        permission_ok=True, internet_ok=True, websocket_ok=None
    )

    assert not any("WebSocket" in check.label for check in checks)


def test_failed_check_is_detected(monkeypatch):
    patch_checks(monkeypatch, service=False)

    checks = preflight.collect_checks(
        permission_ok=True, internet_ok=True, websocket_ok=True
    )

    assert preflight.all_passed(checks) is False
    report = preflight.format_report(checks)
    assert "[CHYBA] Služba MacrosoftConnect beží" in report
    assert "[OK] OBS beží" in report


class FakeResponse:
    def __init__(self, text):
        self.text = text


def test_check_internet_success(monkeypatch):
    monkeypatch.setattr(preflight.api, "get", lambda *a, **kw: FakeResponse("1.2.3.4"))

    assert preflight.check_internet() is True


def test_check_internet_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("offline")

    monkeypatch.setattr(preflight.api, "get", boom)

    assert preflight.check_internet() is False
