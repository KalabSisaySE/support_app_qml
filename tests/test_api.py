import pytest
import requests

from support_app.api import DEFAULT_TIMEOUT_SECONDS, HttpClient


class FakeSession:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def make_client(outcomes, get_retries=2, monkeypatch=None):
    if monkeypatch is not None:
        monkeypatch.setattr("support_app.api.time.sleep", lambda *_: None)
    client = HttpClient(get_retries=get_retries, backoff=0)
    client.session = FakeSession(outcomes)
    return client


def test_get_applies_default_timeout(monkeypatch):
    sentinel = object()
    client = make_client([sentinel], monkeypatch=monkeypatch)

    assert client.get("https://example.test/resource") is sentinel

    method, url, kwargs = client.session.calls[0]
    assert (method, url) == ("GET", "https://example.test/resource")
    assert kwargs["timeout"] == DEFAULT_TIMEOUT_SECONDS


def test_get_retries_timeouts(monkeypatch):
    sentinel = object()
    client = make_client(
        [requests.Timeout("first"), requests.ConnectionError("second"), sentinel],
        monkeypatch=monkeypatch,
    )

    assert client.get("https://example.test/resource") is sentinel
    assert len(client.session.calls) == 3


def test_get_raises_after_exhausting_retries(monkeypatch):
    client = make_client(
        [requests.Timeout("first"), requests.Timeout("second")],
        get_retries=1,
        monkeypatch=monkeypatch,
    )

    with pytest.raises(requests.Timeout):
        client.get("https://example.test/resource")
    assert len(client.session.calls) == 2


def test_post_does_not_retry_by_default(monkeypatch):
    client = make_client([requests.ConnectionError("down")], monkeypatch=monkeypatch)

    with pytest.raises(requests.ConnectionError):
        client.post("https://example.test/resource", json={"a": 1})
    assert len(client.session.calls) == 1


def test_options_are_forwarded(monkeypatch):
    sentinel = object()
    client = make_client([sentinel], monkeypatch=monkeypatch)

    client.get(
        "https://example.test/resource",
        headers={"X-Test": "1"},
        retries=0,
        timeout=2.5,
    )

    _, _, kwargs = client.session.calls[0]
    assert kwargs == {"headers": {"X-Test": "1"}, "timeout": 2.5}
