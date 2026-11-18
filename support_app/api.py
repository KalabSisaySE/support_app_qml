"""HTTP client helpers with explicit timeouts, bounded retries and logging.

GET requests are retried on connection/timeout errors because they are
idempotent by convention.  POST requests are **not** retried by default so a
retry can never duplicate a server-side side effect (video creation, upload
trigger, ...).  Callers can override either default explicitly.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from support_app.logging_setup import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_GET_RETRIES = 2
DEFAULT_BACKOFF_SECONDS = 1.0

_RETRYABLE_EXCEPTIONS = (requests.ConnectionError, requests.Timeout)


class HttpClient:
    """Thin ``requests`` wrapper that applies timeouts and retry policy."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        get_retries: int = DEFAULT_GET_RETRIES,
        backoff: float = DEFAULT_BACKOFF_SECONDS,
    ) -> None:
        self.timeout = timeout
        self.get_retries = get_retries
        self.backoff = backoff
        self.session = requests.Session()

    def request(
        self,
        method: str,
        url: str,
        *,
        timeout: float | None = None,
        retries: int = 0,
        **kwargs: Any,
    ) -> requests.Response:
        attempts = max(1, retries + 1)
        effective_timeout = self.timeout if timeout is None else timeout
        last_error: requests.RequestException | None = None

        for attempt in range(1, attempts + 1):
            try:
                return self.session.request(
                    method, url, timeout=effective_timeout, **kwargs
                )
            except _RETRYABLE_EXCEPTIONS as exc:
                last_error = exc
                if attempt >= attempts:
                    break
                logger.warning(
                    "%s %s failed (attempt %d/%d): %s",
                    method.upper(), url, attempt, attempts, exc,
                )
                if self.backoff:
                    time.sleep(self.backoff)

        if last_error is None:  # pragma: no cover - defensive
            raise requests.RequestException(f"{method.upper()} {url} failed")
        raise last_error

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        retries = kwargs.pop("retries", self.get_retries)
        return self.request("GET", url, retries=retries, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        retries = kwargs.pop("retries", 0)
        return self.request("POST", url, retries=retries, **kwargs)


_client = HttpClient()


def get(url: str, **kwargs: Any) -> requests.Response:
    """GET *url* with the default timeout and retry policy."""
    return _client.get(url, **kwargs)


def post(url: str, **kwargs: Any) -> requests.Response:
    """POST *url* with the default timeout and no retries."""
    return _client.post(url, **kwargs)
