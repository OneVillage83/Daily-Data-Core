from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, cast

import pytest
import requests

import daily_data_core.http as http_module
from daily_data_core.http import HttpClient, HttpError, RetryableHttpError

SECRET = "ddc-http-secret"


@dataclass
class RecordedCall:
    url: str
    params: dict[str, str] | None
    headers: dict[str, str] | None
    timeout: int


class SequenceSession:
    def __init__(self, items: list[requests.Response | requests.RequestException]) -> None:
        self.items = items
        self.calls: list[RecordedCall] = []

    def get(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int,
    ) -> requests.Response:
        self.calls.append(RecordedCall(url, params, headers, timeout))
        item = self.items.pop(0)
        if isinstance(item, requests.RequestException):
            raise item
        return item


def _response(
    status: int,
    payload: object,
    *,
    headers: dict[str, str] | None = None,
    url: str = "https://example.test/resource",
) -> requests.Response:
    response = requests.Response()
    response.status_code = status
    response.url = url
    response.headers.update(headers or {})
    response._content = json.dumps(payload).encode()
    response.encoding = "utf-8"
    return response


def _client(
    items: list[requests.Response | requests.RequestException],
    *,
    max_attempts: int = 3,
    retry_max_seconds: float = 30.0,
) -> tuple[HttpClient, SequenceSession]:
    client = HttpClient(
        timeout=17,
        max_attempts=max_attempts,
        retry_max_seconds=retry_max_seconds,
    )
    session = SequenceSession(items)
    client.session = cast(requests.Session, session)
    return client, session


def test_retry_after_is_respected_and_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(http_module.time, "sleep", sleeps.append)
    client, session = _client(
        [
            _response(429, {}, headers={"Retry-After": "99"}),
            _response(200, []),
        ],
        retry_max_seconds=7.0,
    )

    result = client.get_json("https://example.test/resource")

    assert len(session.calls) == 2
    assert sleeps == [7.0]
    assert result.diagnostics.attempts == 2
    assert result.diagnostics.retries_performed == 1


def test_connection_and_timeout_failures_retry_with_backoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(http_module.time, "sleep", sleeps.append)
    client, session = _client(
        [
            requests.ConnectionError("connection"),
            requests.Timeout("timeout"),
            _response(200, []),
        ]
    )

    result = client.get_json("https://example.test/resource")

    assert len(session.calls) == 3
    assert sleeps == [1.0, 2.0]
    assert result.diagnostics.attempts == 3
    assert result.diagnostics.retries_performed == 2


def test_permanent_http_error_is_not_retried_and_redacts_secret_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(http_module.time, "sleep", sleeps.append)
    response_url = f"https://example.test/resource?apiKey={SECRET}&regions=us"
    client, session = _client(
        [
            _response(
                401,
                {"message": SECRET},
                headers={"x-requests-remaining": "88"},
                url=response_url,
            )
        ]
    )

    with pytest.raises(HttpError) as captured:
        client.get_json(
            "https://example.test/resource",
            params={"apiKey": SECRET, "regions": "us"},
        )

    assert len(session.calls) == 1
    assert sleeps == []
    assert SECRET not in str(captured.value)
    assert "%5BREDACTED%5D" in str(captured.value) or "[REDACTED]" in str(captured.value)
    assert captured.value.diagnostics is not None
    assert captured.value.diagnostics.quota_headers["requests_remaining"] == "88"


def test_invalid_json_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(http_module.time, "sleep", sleeps.append)
    response = _response(200, {})
    response._content = b"not-json"
    client, session = _client([response])

    with pytest.raises(HttpError, match="Invalid JSON"):
        client.get_json("https://example.test/resource")

    assert len(session.calls) == 1
    assert sleeps == []
