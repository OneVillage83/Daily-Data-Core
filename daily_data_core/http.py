"""Shared HTTP client with retries, diagnostics, and safe URL reporting."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance

if TYPE_CHECKING:
    from daily_data_core.acquisition import AcquisitionEvidence

type JsonPayload = dict[str, object] | list[object]

_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
_RETRY_AFTER_STATUS_CODES = frozenset({429, 503})
_SENSITIVE_QUERY_TOKENS = ("key", "token", "secret", "password", "auth", "appid")


@dataclass(frozen=True, slots=True)
class HttpRequestDiagnostics:
    request_status: str
    status_code: int | None
    attempts: int
    retries_performed: int
    duration_seconds: float
    response_date_utc: str | None
    quota_headers: dict[str, str | None] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class JsonHttpResult:
    payload: JsonPayload
    content: bytes = field(repr=False)
    content_type: str
    response_url: str
    diagnostics: HttpRequestDiagnostics
    raw_payloads: tuple[ProviderPayload, ...] = field(default=(), repr=False)


@runtime_checkable
class JsonHttpClient(Protocol):
    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult: ...


class HttpError(RuntimeError):
    def __init__(
        self,
        message: str,
        diagnostics: HttpRequestDiagnostics | None = None,
        raw_payloads: tuple[ProviderPayload, ...] = (),
    ) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics
        self.raw_payloads = raw_payloads
        self.evidence: tuple[AcquisitionEvidence, ...] = ()

    @property
    def raw_payload(self) -> ProviderPayload | None:
        return self.raw_payloads[-1] if self.raw_payloads else None

    @property
    def failure_kind(self) -> str:
        if self.diagnostics is not None and self.diagnostics.status_code is None:
            return "transport_error"
        if self.raw_payload is None:
            return "transport_error"
        if (self.raw_payload.response_status_code or 200) >= 400:
            return "http_status_error"
        return "json_error"


class RetryableHttpError(HttpError):
    pass


def redact_url(url: str) -> str:
    parts = urlsplit(url)
    query: list[tuple[str, str]] = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        lowered = key.casefold()
        safe_value = (
            "[REDACTED]" if any(token in lowered for token in _SENSITIVE_QUERY_TOKENS) else value
        )
        query.append((key, safe_value))
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc.rsplit("@", 1)[-1],
            parts.path,
            urlencode(query),
            "",
        )
    )


def _http_date_utc(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat()


def _retry_after_seconds(value: str | None, maximum: float) -> float | None:
    if not value:
        return None
    try:
        delay = float(value.strip())
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=UTC)
        delay = (retry_at.astimezone(UTC) - datetime.now(UTC)).total_seconds()
    if not math.isfinite(delay):
        return None
    return min(max(delay, 0.0), maximum)


def _backoff_seconds(attempt: int) -> float:
    return float(min(2 ** (attempt - 1), 8))


def _quota_headers(response: requests.Response) -> dict[str, str | None]:
    return {
        "requests_remaining": response.headers.get("x-requests-remaining"),
        "requests_used": response.headers.get("x-requests-used"),
        "requests_last": response.headers.get("x-requests-last"),
    }


class HttpClient:
    def __init__(
        self,
        timeout: int = 30,
        max_attempts: int = 3,
        retry_max_seconds: float = 30.0,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if not math.isfinite(retry_max_seconds) or retry_max_seconds < 0:
            raise ValueError("retry_max_seconds must be finite and nonnegative")
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.retry_max_seconds = retry_max_seconds
        self.session = requests.Session()

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        started = time.monotonic()
        prepared_url = requests.Request("GET", url, params=params).prepare().url or url
        safe_prepared_url = redact_url(prepared_url)
        evidence: list[ProviderPayload] = []

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            except (requests.Timeout, requests.ConnectionError) as exc:
                if attempt < self.max_attempts:
                    time.sleep(_backoff_seconds(attempt))
                    continue
                diagnostics = self._diagnostics(
                    started,
                    "failed",
                    None,
                    attempt,
                    None,
                    {},
                )
                raise RetryableHttpError(
                    (f"Request failed for {safe_prepared_url}: {type(exc).__name__}"),
                    diagnostics,
                    tuple(evidence),
                ) from None
            except requests.RequestException as exc:
                diagnostics = self._diagnostics(
                    started,
                    "failed",
                    None,
                    attempt,
                    None,
                    {},
                )
                raise HttpError(
                    (f"Request failed for {safe_prepared_url}: {type(exc).__name__}"),
                    diagnostics,
                    tuple(evidence),
                ) from None

            response_date = _http_date_utc(response.headers.get("Date"))
            quota = _quota_headers(response)
            safe_response_url = redact_url(response.url or prepared_url)
            retrieved_at = datetime.now(UTC)
            evidence.append(
                ProviderPayload(
                    content=response.content,
                    content_type=response.headers.get("Content-Type") or "application/octet-stream",
                    source_uri=safe_response_url,
                    provenance=TemporalProvenance(
                        observed_at=retrieved_at,
                        available_at=retrieved_at,
                        published_at=datetime.fromisoformat(response_date)
                        if response_date
                        else None,
                    ),
                    response_status_code=response.status_code,
                )
            )
            if response.status_code in _RETRYABLE_STATUS_CODES:
                if attempt < self.max_attempts:
                    delay = None
                    if response.status_code in _RETRY_AFTER_STATUS_CODES:
                        delay = _retry_after_seconds(
                            response.headers.get("Retry-After"),
                            self.retry_max_seconds,
                        )
                    time.sleep(delay if delay is not None else _backoff_seconds(attempt))
                    continue
                diagnostics = self._diagnostics(
                    started,
                    "failed",
                    response.status_code,
                    attempt,
                    response_date,
                    quota,
                )
                raise RetryableHttpError(
                    (f"Temporary HTTP {response.status_code} from {safe_response_url}"),
                    diagnostics,
                    tuple(evidence),
                )
            if not response.ok:
                diagnostics = self._diagnostics(
                    started,
                    "failed",
                    response.status_code,
                    attempt,
                    response_date,
                    quota,
                )
                raise HttpError(
                    f"HTTP {response.status_code} from {safe_response_url}",
                    diagnostics,
                    tuple(evidence),
                )

            try:
                raw_payload: object = response.json()
            except requests.JSONDecodeError:
                diagnostics = self._diagnostics(
                    started,
                    "failed",
                    response.status_code,
                    attempt,
                    response_date,
                    quota,
                )
                raise HttpError(
                    f"Invalid JSON from {safe_response_url}",
                    diagnostics,
                    tuple(evidence),
                ) from None
            if not isinstance(raw_payload, (dict, list)):
                diagnostics = self._diagnostics(
                    started,
                    "failed",
                    response.status_code,
                    attempt,
                    response_date,
                    quota,
                )
                raise HttpError(
                    f"JSON root must be object or list from {safe_response_url}",
                    diagnostics,
                    tuple(evidence),
                )

            diagnostics = self._diagnostics(
                started,
                "success",
                response.status_code,
                attempt,
                response_date,
                quota,
            )
            return JsonHttpResult(
                payload=raw_payload,
                content=response.content,
                content_type=response.headers.get(
                    "Content-Type",
                    "application/json",
                ),
                response_url=safe_response_url,
                diagnostics=diagnostics,
                raw_payloads=tuple(evidence),
            )

        raise AssertionError("HTTP retry loop exited unexpectedly")

    def _diagnostics(
        self,
        started: float,
        request_status: str,
        status_code: int | None,
        attempts: int,
        response_date_utc: str | None,
        quota_headers: dict[str, str | None],
    ) -> HttpRequestDiagnostics:
        return HttpRequestDiagnostics(
            request_status=request_status,
            status_code=status_code,
            attempts=attempts,
            retries_performed=max(0, attempts - 1),
            duration_seconds=max(0.0, time.monotonic() - started),
            response_date_utc=response_date_utc,
            quota_headers=quota_headers,
        )
