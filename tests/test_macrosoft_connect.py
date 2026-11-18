import requests

from support_app import macrosoft_connect


class FakeResponse:
    def __init__(self, status_code):
        self.status_code = status_code


def test_report_skips_without_access_code():
    assert macrosoft_connect.report_rustdesk_id("", "123") is False


def test_report_success(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse(200)

    monkeypatch.setattr(macrosoft_connect.api, "get", fake_get)
    logs = []

    assert macrosoft_connect.report_rustdesk_id("CODE", "123", log=logs.append) is True
    assert calls[0][0].endswith("?access=CODE&rustdesk=123")
    assert calls[0][1]["retries"] == 0
    assert logs == ["ID bolo úspešne odoslané."]


def test_report_retries_then_succeeds(monkeypatch):
    responses = [FakeResponse(500), FakeResponse(200)]
    calls = []

    def fake_get(url, **kwargs):
        calls.append(url)
        return responses.pop(0)

    monkeypatch.setattr(macrosoft_connect.api, "get", fake_get)
    monkeypatch.setattr(macrosoft_connect.time, "sleep", lambda *_: None)
    logs = []

    assert macrosoft_connect.report_rustdesk_id("CODE", "123", log=logs.append) is True
    assert len(calls) == 2
    assert "Odozva servera: 500" in logs


def test_report_returns_false_after_failures(monkeypatch):
    monkeypatch.setattr(
        macrosoft_connect.api, "get", lambda *a, **kw: FakeResponse(500)
    )
    monkeypatch.setattr(macrosoft_connect.time, "sleep", lambda *_: None)

    assert macrosoft_connect.report_rustdesk_id(
        "CODE", "123", max_attempts=2
    ) is False


def test_report_logs_exceptions(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(macrosoft_connect.api, "get", fake_get)
    logs = []

    assert macrosoft_connect.report_rustdesk_id(
        "CODE", "123", log=logs.append, max_attempts=1
    ) is False
    assert any("Nepodarilo sa odoslať ID" in line for line in logs)
