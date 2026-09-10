"""Shared HTTP client with retries, diagnostics, and safe URL reporting."""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import uuid4

import requests

from daily_data_core.history import (
    HistoryObserver,
    HttpExchange,
    LogicalCall,
    PhysicalAttempt,
    SchemaValidationError,
    code_identity,
)
from daily_data_core.providers import ProviderPayload
from daily_data_core.redirects import REDIRECT_STATUSES, RedirectPolicy
from daily_data_core.temporal import TemporalProvenance

if TYPE_CHECKING:
    from daily_data_core.acquisition import AcquisitionEvidence, AcquisitionHistory

type JsonPayload = dict[str, object] | list[object]

_RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})
_RETRY_AFTER_STATUS_CODES = frozenset({429, 503})
_SENSITIVE_QUERY_TOKENS = (
    "key",
    "token",
    "secret",
    "password",
    "auth",
    "appid",
    "cookie",
    "session",
    "credential",
    "signature",
)


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
    call: LogicalCall | None = None


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
        call: LogicalCall | None = None,
    ) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics
        self.call = call
        self.raw_payloads = raw_payloads
        self.evidence: tuple[AcquisitionEvidence, ...] = ()
        self.history: AcquisitionHistory | None = None

    @property
    def raw_payload(self) -> ProviderPayload | None:
        return self.raw_payloads[-1] if self.raw_payloads else None

    @property
    def failure_kind(self) -> str:
        if self.call is not None:
            return self.call.terminal_outcome
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


def _safe_quota(value: str | None) -> str | None:
    return value if value is not None and value.isascii() and value.isdigit() else None


def _quota_headers(response: requests.Response) -> dict[str, str | None]:
    return {
        "requests_remaining": _safe_quota(response.headers.get("x-requests-remaining")),
        "requests_used": _safe_quota(response.headers.get("x-requests-used")),
        "requests_last": _safe_quota(response.headers.get("x-requests-last")),
    }


class HttpClient:
    def __init__(
        self,
        timeout: int = 30,
        max_attempts: int = 3,
        retry_max_seconds: float = 30.0,
        schema_validator: Callable[[JsonPayload], None] | None = None,
        validator_version: str | None = None,
        retry_schema_errors: bool = False,
        redirect_policy: RedirectPolicy | None = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least one")
        if not math.isfinite(retry_max_seconds) or retry_max_seconds < 0:
            raise ValueError("retry_max_seconds must be finite and nonnegative")
        if schema_validator is not None and not validator_version:
            raise ValueError("schema validator requires an explicit version")
        self.schema_validator = schema_validator
        self.validator_version = validator_version
        self.retry_schema_errors = retry_schema_errors
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.retry_max_seconds = retry_max_seconds
        self.session = requests.Session()
        self.redirect_policy = redirect_policy or RedirectPolicy()

    def _get_exchanges(
        self,
        url: str,
        params: dict[str, str] | None,
        headers: dict[str, str] | None,
        call_id: str,
        attempt: int,
        observer: HistoryObserver | None,
    ) -> tuple[
        requests.Response | None, tuple[HttpExchange, ...], requests.RequestException | None
    ]:
        current = requests.Request("GET", url, params=params).prepare().url or url
        visited = {current}
        exchanges: list[HttpExchange] = []
        for hop in range(1, self.redirect_policy.max_redirects + 2):
            started = datetime.now(UTC)
            safe = redact_url(current)
            start = {
                "schema": "ddc-http-exchange-start-v1",
                "call_id": call_id,
                "attempt_ordinal": attempt,
                "ordinal": hop,
                "method": "GET",
                "request_url": safe,
                "started_at": started.isoformat(),
            }
            hook = getattr(observer, "exchange_started", None)
            if hook is not None:
                hook(start)
            try:
                if hop == 1 and type(self.session).get is not requests.Session.get:
                    # Explicitly injected test/custom sessions must honor allow_redirects=False.
                    response = self.session.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                else:
                    if hop == 1:
                        prepared = self.session.prepare_request(
                            requests.Request("GET", current, headers=headers)
                        )
                    else:
                        # No Session auth/cookies/netrc or arbitrary headers on redirected requests.
                        safe_headers = {
                            k: v
                            for k, v in {**self.session.headers, **(headers or {})}.items()
                            if k.lower() in {"user-agent", "accept", "accept-encoding"}
                        }
                        prepared = requests.Request("GET", current, headers=safe_headers).prepare()
                    adapter = self.session.get_adapter(current)
                    if (
                        isinstance(adapter, requests.adapters.HTTPAdapter)
                        and adapter.max_retries.total != 0
                    ):
                        raise ValueError("adapter-level retries bypass DDC attempt accounting")
                    settings = self.session.merge_environment_settings(
                        current, {}, False, None, None
                    )
                    # Session.send pre-processes Location even with redirects disabled. Call its
                    # adapter directly so malformed Location cannot discard a received response.
                    response = adapter.send(
                        prepared,
                        timeout=self.timeout,
                        stream=bool(settings["stream"]),
                        verify=settings["verify"] if settings["verify"] is not None else True,
                        cert=settings["cert"] if hop == 1 else None,
                        proxies=settings["proxies"],
                    )
            except requests.RequestException as exc:
                exchange = HttpExchange(
                    call_id,
                    attempt,
                    hop,
                    safe,
                    started,
                    datetime.now(UTC),
                    None,
                    error_type=type(exc).__name__,
                )
                hook = getattr(observer, "exchanged", None)
                if hook is not None:
                    hook(exchange)
                exchanges.append(exchange)
                return None, tuple(exchanges), exc
            try:
                content = response.content
            except requests.RequestException as exc:
                exchange = HttpExchange(
                    call_id,
                    attempt,
                    hop,
                    safe,
                    started,
                    datetime.now(UTC),
                    None,
                    quota=tuple(sorted(_quota_headers(response).items())),
                    error_type=type(exc).__name__,
                    response_status=response.status_code,
                )
                hook = getattr(observer, "exchanged", None)
                if hook is not None:
                    hook(exchange)
                exchanges.append(exchange)
                return None, tuple(exchanges), exc
            received = datetime.now(UTC)
            date = _http_date_utc(response.headers.get("Date"))
            payload = ProviderPayload(
                content,
                response.headers.get("Content-Type") or "application/octet-stream",
                redact_url(response.url or current),
                TemporalProvenance(
                    received, received, published_at=datetime.fromisoformat(date) if date else None
                ),
                response_status_code=response.status_code,
            )
            if observer is not None:
                observer.received(payload)
            quota = tuple(sorted(_quota_headers(response).items()))
            # Canonical allowlisted headers; raw Location/Set-Cookie are never stored.
            safe_headers_evidence: dict[str, str] = {}
            if date:
                safe_headers_evidence["date"] = date
            delay = _retry_after_seconds(
                response.headers.get("Retry-After"), self.retry_max_seconds
            )
            if delay is not None:
                safe_headers_evidence["retry-after-seconds"] = str(delay)
            exchange = HttpExchange(
                call_id,
                attempt,
                hop,
                safe,
                started,
                received,
                payload,
                tuple(sorted(safe_headers_evidence.items())),
                quota,
                decision="received",
                response_status=response.status_code,
            )
            hook = getattr(observer, "exchange_received", None)
            if hook is not None:
                hook(exchange)  # Durable response receipt precedes any redirect policy transition.
            target: str | None = None
            decision = "terminal"
            if response.status_code in REDIRECT_STATUSES:
                target, decision = self.redirect_policy.resolve(
                    current, response.headers.get("Location"), visited
                )
                if decision == "follow" and hop > self.redirect_policy.max_redirects:
                    decision = "redirect_limit"
                if (
                    decision == "follow"
                    and target is not None
                    and any(
                        any(token in k.casefold() for token in _SENSITIVE_QUERY_TOKENS)
                        for k, _ in parse_qsl(urlsplit(target).query, keep_blank_values=True)
                    )
                ):
                    decision = "sensitive_redirect_query"
            exchange = replace(
                exchange, redirect_target=redact_url(target) if target else None, decision=decision
            )
            hook = getattr(observer, "exchanged", None)
            if hook is not None:
                hook(exchange)
            exchanges.append(exchange)
            if decision != "follow":
                return response, tuple(exchanges), None
            assert target is not None
            response.close()
            visited.add(target)
            current = target
        raise AssertionError("redirect bound exhausted without terminal disposition")

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        return self.get_json_recorded(url, params=params, headers=headers)

    def get_json_recorded(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        observer: HistoryObserver | None = None,
        provider_id: str = "http",
        operation: str = "get_json",
        source_run_id: str | None = None,
    ) -> JsonHttpResult:
        started = time.monotonic()
        started_at = datetime.now(UTC)
        call_id = uuid4().hex
        prepared_url = requests.Request("GET", url, params=params).prepare().url or url
        safe_request = redact_url(prepared_url)
        attempts: list[PhysicalAttempt] = []
        decoded: JsonPayload | None = None
        for ordinal in range(1, self.max_attempts + 1):
            requested_at = datetime.now(UTC)
            payload: ProviderPayload | None = None
            status: int | None = None
            quota: dict[str, str | None] = {}
            retryable = False
            delay = 0.0
            error_type: str | None = None
            retry_after: str | None = None
            exchanges: tuple[HttpExchange, ...] = ()
            try:
                response, exchanges, failure = self._get_exchanges(
                    url, params, headers, call_id, ordinal, observer
                )
                if failure is not None:
                    raise failure
            except requests.RequestException as exc:
                outcome = "transport_error"
                error_type = type(exc).__name__
                retryable = isinstance(exc, (requests.Timeout, requests.ConnectionError))
                if exchanges:
                    status = exchanges[-1].response_status
                    quota = dict(exchanges[-1].quota)
            else:
                assert response is not None
                status = response.status_code
                quota = _quota_headers(response)
                payload = exchanges[-1].payload
                retry_after = response.headers.get("Retry-After")
                if exchanges[-1].decision != "terminal":
                    outcome = "redirect_error"
                    error_type = exchanges[-1].decision
                elif not response.ok:
                    outcome = "http_status_error"
                    retryable = status in _RETRYABLE_STATUS_CODES
                else:
                    try:
                        raw: object = response.json()
                    except requests.JSONDecodeError:
                        outcome = "json_error"
                        retryable = self.retry_schema_errors
                    else:
                        if not isinstance(raw, (dict, list)):
                            outcome = "json_error"
                            retryable = self.retry_schema_errors
                        else:
                            decoded = raw
                            outcome = "success"
                            if self.schema_validator is not None:
                                try:
                                    self.schema_validator(decoded)
                                except SchemaValidationError:
                                    outcome = "schema_error"
                                    retryable = self.retry_schema_errors
                                    error_type = "SchemaValidationError"
                                except Exception as exc:
                                    outcome = "schema_error"
                                    error_type = type(exc).__name__
                                    retryable = False
            will_retry = retryable and ordinal < self.max_attempts
            if will_retry:
                override = (
                    _retry_after_seconds(retry_after, self.retry_max_seconds)
                    if status in _RETRY_AFTER_STATUS_CODES
                    else None
                )
                delay = override if override is not None else _backoff_seconds(ordinal)
            attempt = PhysicalAttempt(
                call_id,
                ordinal,
                requested_at,
                datetime.now(UTC),
                outcome,
                status,
                error_type,
                tuple(sorted(quota.items())),
                retryable,
                will_retry,
                delay,
                payload,
                exchanges,
            )
            attempts.append(attempt)
            if observer is not None:
                observer.attempted(attempt)
            if will_retry:
                time.sleep(delay)
                continue
            break

        call = LogicalCall(
            call_id,
            provider_id,
            operation,
            safe_request,
            started_at,
            datetime.now(UTC),
            self.timeout,
            self.max_attempts,
            self.retry_max_seconds,
            self.retry_schema_errors,
            self.validator_version,
            tuple(attempts),
            max(0.0, time.monotonic() - started),
            source_run_id,
            source_code_identity=code_identity(),
            redirect_policy=self.redirect_policy.document(),
        )
        if observer is not None:
            observer.completed(call)
        diagnostics = diagnostics_for_call(call)
        if call.terminal_outcome != "success":
            messages = {
                "transport_error": "Request failed",
                "http_status_error": f"HTTP {status}",
                "json_error": "Invalid JSON",
                "schema_error": "Response schema invalid",
                "redirect_error": "Redirect rejected",
            }
            error_class = RetryableHttpError if attempts[-1].retryable else HttpError
            raise error_class(
                messages[call.terminal_outcome] + " from " + safe_request,
                diagnostics,
                call.payloads,
                call,
            ) from None
        assert decoded is not None and payload is not None
        return JsonHttpResult(
            decoded,
            payload.content,
            payload.content_type,
            payload.source_uri or safe_request,
            diagnostics,
            call.payloads,
            call,
        )


def diagnostics_for_call(call: LogicalCall) -> HttpRequestDiagnostics:
    last = call.attempts[-1]
    source_date = last.payload.provenance.published_at if last.payload else None
    return HttpRequestDiagnostics(
        "success" if call.terminal_outcome == "success" else "failed",
        last.status_code,
        len(call.attempts),
        len(call.attempts) - 1,
        call.duration_seconds,
        source_date.isoformat() if source_date else None,
        dict(last.quota),
    )
