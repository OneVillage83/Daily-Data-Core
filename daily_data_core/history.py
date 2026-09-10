"""Immutable logical HTTP calls and physical attempts; no transport or sport policy."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from importlib.resources import files
from typing import Any, Protocol

from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance, as_utc
from daily_data_core.version import __version__


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def code_identity() -> str:
    root = files("daily_data_core")
    return digest(
        {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.iterdir(), key=lambda p: p.name)
            if p.name.endswith(".py")
        }
    )


class SchemaValidationError(RuntimeError):
    """A versioned optional response validator rejected this physical response."""


class ReplayMismatchError(RuntimeError):
    """Recorded history is incomplete, incompatible or differs from strict replay."""


def payload_document(payload: ProviderPayload) -> dict[str, object]:
    return {
        "sha256": hashlib.sha256(payload.content).hexdigest(),
        "content_type": payload.content_type,
        "source_uri": payload.source_uri,
        "provider_schema_version": payload.provider_schema_version,
        "response_status_code": payload.response_status_code,
        "clocks": {k: v.isoformat() if v else None for k, v in asdict(payload.provenance).items()},
    }


def read_payload(document: dict[str, Any], content: bytes) -> ProviderPayload:
    if hashlib.sha256(content).hexdigest() != document["sha256"]:
        raise ReplayMismatchError("recorded response digest mismatch")
    clocks = document["clocks"]
    return ProviderPayload(
        content,
        document["content_type"],
        document["source_uri"],
        TemporalProvenance(
            datetime.fromisoformat(clocks["observed_at"]),
            datetime.fromisoformat(clocks["available_at"]),
            datetime.fromisoformat(clocks["effective_at"]) if clocks["effective_at"] else None,
            datetime.fromisoformat(clocks["published_at"]) if clocks["published_at"] else None,
        ),
        document["provider_schema_version"],
        document["response_status_code"],
    )


@dataclass(frozen=True, slots=True)
class PhysicalAttempt:
    call_id: str
    ordinal: int
    started_at: datetime
    completed_at: datetime
    outcome: str
    status_code: int | None
    error_type: str | None
    quota: tuple[tuple[str, str | None], ...]
    retryable: bool
    will_retry: bool
    delay_seconds: float
    payload: ProviderPayload | None = None

    def __post_init__(self) -> None:
        if self.ordinal < 1 or as_utc(self.completed_at) < as_utc(self.started_at):
            raise ValueError("invalid physical attempt ordering")
        if self.outcome not in {
            "success",
            "transport_error",
            "http_status_error",
            "json_error",
            "schema_error",
        }:
            raise ValueError("unknown attempt outcome")
        if self.outcome == "transport_error" and self.payload is not None:
            raise ValueError("no-response failure cannot contain invented response bytes")
        if self.outcome != "transport_error" and self.payload is None:
            raise ValueError("received response requires raw evidence")
        if self.payload is not None and self.status_code != self.payload.response_status_code:
            raise ValueError("response status disagrees with attempt")
        if self.delay_seconds < 0 or (not self.will_retry and self.delay_seconds != 0):
            raise ValueError("invalid retry delay")
        if self.will_retry and not self.retryable:
            raise ValueError("retry requires an explicit retryable outcome")

    @property
    def attempt_id(self) -> str:
        return digest([self.call_id, self.ordinal])

    def document(self) -> dict[str, object]:
        return {
            "schema": "ddc-physical-attempt-v1",
            "call_id": self.call_id,
            "attempt_id": self.attempt_id,
            "ordinal": self.ordinal,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "outcome": self.outcome,
            "status_code": self.status_code,
            "error_type": self.error_type,
            "quota": dict(self.quota),
            "retryable": self.retryable,
            "will_retry": self.will_retry,
            "delay_seconds": self.delay_seconds,
            "payload": payload_document(self.payload) if self.payload is not None else None,
        }


@dataclass(frozen=True, slots=True)
class LogicalCall:
    call_id: str
    provider_id: str
    operation: str
    safe_request: str
    started_at: datetime
    completed_at: datetime
    timeout_seconds: int
    max_attempts: int
    retry_cap_seconds: float
    retry_schema_errors: bool
    validator_version: str | None
    attempts: tuple[PhysicalAttempt, ...]
    duration_seconds: float
    source_run_id: str | None = None
    package_version: str = __version__
    source_code_identity: str = ""

    def __post_init__(self) -> None:
        if not self.call_id or not self.provider_id or not self.operation:
            raise ValueError("logical call identities cannot be blank")
        if not self.attempts or len(self.attempts) > self.max_attempts:
            raise ValueError("logical call requires bounded attempt history")
        previous = as_utc(self.started_at)
        for ordinal, attempt in enumerate(self.attempts, 1):
            if attempt.call_id != self.call_id or attempt.ordinal != ordinal:
                raise ValueError("attempt history identity/order mismatch")
            if as_utc(attempt.started_at) < previous:
                raise ValueError("physical attempts overlap or run backwards")
            if attempt.will_retry != (ordinal < len(self.attempts)):
                raise ValueError("attempt terminal/retry disposition mismatch")
            previous = as_utc(attempt.completed_at)
        if as_utc(self.completed_at) < previous:
            raise ValueError("logical completion precedes attempts")

    @property
    def terminal_outcome(self) -> str:
        return self.attempts[-1].outcome

    @property
    def payloads(self) -> tuple[ProviderPayload, ...]:
        return tuple(a.payload for a in self.attempts if a.payload is not None)

    def diagnostics_document(self) -> dict[str, object]:
        last = self.attempts[-1]
        source_date = last.payload.provenance.published_at if last.payload else None
        return {
            "request_status": "success" if self.terminal_outcome == "success" else "failed",
            "status_code": last.status_code,
            "attempts": len(self.attempts),
            "retries_performed": len(self.attempts) - 1,
            "duration_seconds": self.duration_seconds,
            "response_date_utc": source_date.isoformat() if source_date else None,
            "quota_headers": dict(last.quota),
        }

    def document(self) -> dict[str, object]:
        return {
            "schema": "ddc-logical-call-v1",
            "call_id": self.call_id,
            "provider_id": self.provider_id,
            "operation": self.operation,
            "safe_request": self.safe_request,
            "request_identity": digest(self.safe_request),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "timeout_seconds": self.timeout_seconds,
            "max_attempts": self.max_attempts,
            "retry_cap_seconds": self.retry_cap_seconds,
            "retry_schema_errors": self.retry_schema_errors,
            "retry_policy_version": "ddc-http-retry-v2",
            "validator_version": self.validator_version,
            "attempts": [a.document() for a in self.attempts],
            "duration_seconds": self.duration_seconds,
            "terminal_outcome": self.terminal_outcome,
            "terminal_attempt_id": self.attempts[-1].attempt_id,
            "request_diagnostics": self.diagnostics_document(),
            "source_run_id": self.source_run_id,
            "package_version": self.package_version,
            "source_code_identity": self.source_code_identity,
        }

    @property
    def receipt_id(self) -> str:
        return digest(self.document())


class HistoryObserver(Protocol):
    def received(self, payload: ProviderPayload) -> None: ...
    def attempted(self, attempt: PhysicalAttempt) -> None: ...
    def completed(self, call: LogicalCall) -> None: ...
