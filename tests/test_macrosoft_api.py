from support_app import macrosoft_api


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


def test_open_website_requires_access_code():
    assert macrosoft_api.open_website("") is False


def test_open_website_uses_online_base(monkeypatch):
    opened = []
    monkeypatch.setattr(macrosoft_api.webbrowser, "open", opened.append)

    assert macrosoft_api.open_website("CODE") is True
    assert opened == ["https://online.macrosoft.sk/online/?access=CODE"]


def test_get_full_name_found(monkeypatch):
    monkeypatch.setattr(
        macrosoft_api.api,
        "get",
        lambda *args, **kwargs: FakeResponse({"status": "found", "full_name": "Janko"}),
    )

    assert macrosoft_api.get_full_name("CODE") == "Janko"
    assert macrosoft_api.get_full_name("") == ""


def test_get_full_name_falls_back_when_not_found(monkeypatch):
    monkeypatch.setattr(
        macrosoft_api.api, "get", lambda *args, **kwargs: FakeResponse({"status": "missing"})
    )

    assert macrosoft_api.get_full_name("CODE") == "Neznáme meno"


def test_get_latest_access_code(monkeypatch):
    monkeypatch.setattr(macrosoft_api, "get_public_ip", lambda: "1.2.3.4")
    monkeypatch.setattr(
        macrosoft_api.api,
        "post",
        lambda *args, **kwargs: FakeResponse({"access_code": "ABC"}),
    )

    assert macrosoft_api.get_latest_access_code() == "ABC"


def test_get_latest_access_code_without_ip(monkeypatch):
    monkeypatch.setattr(macrosoft_api, "get_public_ip", lambda: None)

    assert macrosoft_api.get_latest_access_code() == ""
