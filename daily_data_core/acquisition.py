"""Versioned acquisition evidence, policy-controlled persistence and offline replay.

Exact bytes are private evidence, never a public export. The caller must explicitly
authorize retention (including content inspection and licence rules) before any write.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Literal, cast
from uuid import uuid4

from daily_data_core.history import (
    HttpExchange,
    LogicalCall,
    PhysicalAttempt,
    ReplayMismatchError,
    canonical,
    code_identity,
    digest,
    read_payload,
)
from daily_data_core.http import (
    HttpClient,
    HttpError,
    HttpRequestDiagnostics,
    JsonHttpClient,
    JsonHttpResult,
    diagnostics_for_call,
    redact_url,
)
from daily_data_core.provenance import FileSystemRawEvidenceStore, sha256_bytes
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance, as_utc
from daily_data_core.version import __version__

type Disposition = Literal["received", "complete", "partial", "schema_error", "http_error"]


class ProviderAcquisitionError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.raw_payloads: tuple[ProviderPayload, ...] = ()
        self.evidence: tuple[AcquisitionEvidence, ...] = ()
        self.diagnostics: HttpRequestDiagnostics | None = None
        self.history: AcquisitionHistory | None = None

    @property
    def quota(self) -> dict[str, str | None]:
        return dict(self.diagnostics.quota_headers) if self.diagnostics else {}

    @property
    def raw_payload(self) -> ProviderPayload | None:
        return self.raw_payloads[-1] if self.raw_payloads else None


@dataclass(frozen=True, slots=True)
class AcquisitionEvidence:
    provider_id: str
    dataset_key: str
    parser_version: str
    payload: ProviderPayload
    disposition: Disposition
    evaluated_at: datetime
    diagnostic_codes: tuple[str, ...] = ()
    previous_receipt_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "payload",
            replace(
                self.payload,
                source_uri=redact_url(self.payload.source_uri) if self.payload.source_uri else None,
            ),
        )
        if self.disposition not in {
            "received",
            "complete",
            "partial",
            "schema_error",
            "http_error",
        }:
            raise ValueError("invalid evidence disposition")
        if not all(
            (self.provider_id.strip(), self.dataset_key.strip(), self.parser_version.strip())
        ):
            raise ValueError("evidence identities cannot be blank")
        if as_utc(self.evaluated_at) < as_utc(self.payload.provenance.observed_at):
            raise ValueError("evaluation cannot precede retrieval")

    def document(self) -> dict[str, object]:
        clocks = self.payload.provenance
        return {
            "schema": "ddc-acquisition-evidence-v2",
            "provider_id": self.provider_id,
            "dataset_key": self.dataset_key,
            "parser_version": self.parser_version,
            "sha256": sha256_bytes(self.payload.content),
            "content_type": self.payload.content_type,
            "source_uri": redact_url(self.payload.source_uri) if self.payload.source_uri else None,
            "provider_schema_version": self.payload.provider_schema_version,
            "response_status_code": self.payload.response_status_code,
            "clocks": {
                key: value.isoformat() if value else None for key, value in asdict(clocks).items()
            },
            "disposition": self.disposition,
            "evaluated_at": self.evaluated_at.isoformat(),
            "diagnostic_codes": list(self.diagnostic_codes),
            "previous_receipt_id": self.previous_receipt_id,
        }

    @property
    def receipt_id(self) -> str:
        return sha256_bytes(_canonical(self.document()))

    @property
    def response_id(self) -> str:
        """Source observation identity, independent of parser/processing revision."""
        document = self.document()
        return sha256_bytes(
            _canonical(
                {
                    key: document[key]
                    for key in (
                        "provider_id",
                        "dataset_key",
                        "sha256",
                        "source_uri",
                        "clocks",
                    )
                }
            )
        )

    def observation_id(self, source_path: str) -> str:
        """A source location is not a sport's canonical market/query identity."""
        if not source_path.startswith("/"):
            raise ValueError("source path must be a JSON pointer")
        return sha256_bytes(_canonical([self.response_id, source_path]))


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


@dataclass(frozen=True, slots=True)
class AcquisitionHistory:
    acquisition_id: str
    provider_id: str
    dataset_key: str
    parser_version: str
    started_at: datetime
    completed_at: datetime
    calls: tuple[LogicalCall, ...]
    disposition: Disposition
    diagnostic_codes: tuple[str, ...]
    evidence: tuple[AcquisitionEvidence, ...]
    normalized_digest: str | None
    previous_history_id: str | None = None
    package_version: str = __version__
    source_code_identity: str = ""

    def __post_init__(self) -> None:
        if as_utc(self.completed_at) < as_utc(self.started_at):
            raise ValueError("acquisition history clocks run backwards")
        if len({call.call_id for call in self.calls}) != len(self.calls):
            raise ValueError("duplicate logical call in acquisition history")

    def document(self) -> dict[str, object]:
        return {
            "schema": "ddc-acquisition-history-v4"
            if any(c.redirect_policy for c in self.calls)
            else "ddc-acquisition-history-v3",
            "acquisition_id": self.acquisition_id,
            "provider_id": self.provider_id,
            "dataset_key": self.dataset_key,
            "parser_version": self.parser_version,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "call_receipts": [c.receipt_id for c in self.calls],
            "request_diagnostics": [c.diagnostics_document() for c in self.calls],
            "disposition": self.disposition,
            "diagnostic_codes": list(self.diagnostic_codes),
            "evidence_receipts": [e.receipt_id for e in self.evidence],
            "normalized_digest": self.normalized_digest,
            "previous_history_id": self.previous_history_id,
            "package_version": self.package_version,
            "source_code_identity": self.source_code_identity,
        }

    @property
    def receipt_id(self) -> str:
        return digest(self.document())


@dataclass(frozen=True, slots=True)
class EvidenceLedger:
    store: FileSystemRawEvidenceStore
    retention_allowed: Callable[[AcquisitionEvidence], bool]
    history_retention_allowed: Callable[[dict[str, object]], bool] | None = None

    def put_exchange(
        self,
        exchange: HttpExchange,
        provider: str,
        dataset: str,
        parser: str,
        *,
        received: bool = False,
    ) -> str | None:
        if exchange.payload is not None:
            evidence = AcquisitionEvidence(
                provider, dataset, parser, exchange.payload, "received", exchange.completed_at
            )
            if not self.retention_allowed(evidence):
                return None
            self.store.put(provider, dataset, exchange.payload)
        document = exchange.document()
        document["provider_id"] = provider
        document["operation"] = dataset
        return self._history_put(
            "exchange_received_v1" if received else "exchange_v1",
            exchange.exchange_id,
            document,
            exchange.completed_at,
        )

    def exchange_state(self, call_id: str, attempt_ordinal: int, ordinal: int) -> dict[str, object]:
        """Read known exchange identity only; never resumes ambiguous external work."""
        identity = digest(digest([digest([call_id, attempt_ordinal]), ordinal]))
        result: dict[str, object] = {}
        for kind in ("exchange_start_v1", "exchange_received_v1", "exchange_v1"):
            try:
                receipt = self.store.resolve_identity(kind, identity)
            except FileNotFoundError:
                continue
            result[kind] = json.loads(self.store.read("ddc_receipts", kind, receipt))
        try:
            terminal = self.store.resolve_identity(
                "attempt_v2", digest(digest([call_id, attempt_ordinal]))
            )
        except FileNotFoundError:
            pass
        else:
            self.store.read("ddc_receipts", "attempt_v2", terminal)
            result["attempt_terminal_receipt"] = terminal
        return result

    def _history_put(
        self, kind: str, identity: str, document: dict[str, object], timestamp: datetime
    ) -> str | None:
        if self.history_retention_allowed is None or not self.history_retention_allowed(document):
            return None
        receipt = digest(document)
        self.store.bind_identity(kind, digest(identity), receipt)
        self.store.put(
            "ddc_receipts",
            kind,
            ProviderPayload(
                canonical(document),
                "application/json",
                None,
                TemporalProvenance(timestamp, timestamp),
            ),
        )
        return receipt

    def put_attempt(
        self, attempt: PhysicalAttempt, provider: str, dataset: str, parser_version: str
    ) -> str | None:
        if any(
            self.put_exchange(e, provider, dataset, parser_version) is None
            for e in attempt.exchanges
        ):
            return None
        if attempt.payload is not None:
            evidence = AcquisitionEvidence(
                provider, dataset, parser_version, attempt.payload, "received", attempt.completed_at
            )
            if not self.retention_allowed(evidence):
                return None
            self.store.put(provider, dataset, attempt.payload)
        return self._history_put(
            "attempt_v2" if attempt.exchanges else "attempt_v1",
            attempt.attempt_id,
            attempt.document(),
            attempt.completed_at,
        )

    def put_call(self, call: LogicalCall, parser_version: str) -> str | None:
        if any(
            self.put_attempt(a, call.provider_id, call.operation, parser_version) is None
            for a in call.attempts
        ):
            return None
        return self._history_put(
            "call_v2" if call.redirect_policy else "call_v1",
            call.call_id,
            call.document(),
            call.completed_at,
        )

    def put_history(self, history: AcquisitionHistory) -> str | None:
        if not history.calls:
            return None  # A response-only client cannot invent physical request history.
        if history.previous_history_id is not None:
            self.read_history(history.previous_history_id)
        if any(self.put_call(c, history.parser_version) is None for c in history.calls):
            return None
        if any(self.put(e) is None for e in history.evidence):
            return None
        return self._history_put(
            "history_v4" if any(c.redirect_policy for c in history.calls) else "history_v3",
            history.acquisition_id,
            history.document(),
            history.completed_at,
        )

    def _read_exchange(self, item: dict[str, Any], provider: str, dataset: str) -> HttpExchange:
        body = item["payload"]
        exchange = HttpExchange(
            item["call_id"],
            item["attempt_ordinal"],
            item["ordinal"],
            item["request_url"],
            datetime.fromisoformat(item["started_at"]),
            datetime.fromisoformat(item["completed_at"]),
            None
            if body is None
            else read_payload(body, self.store.read(provider, dataset, body["sha256"])),
            tuple(sorted(item["headers"].items())),
            tuple(sorted(item["quota"].items())),
            item["redirect_target"],
            item["decision"],
            item["error_type"],
            item["response_status"],
        )
        if exchange.document() != item:
            raise ReplayMismatchError("exchange identity mismatch")
        expected = {**item, "provider_id": provider, "operation": dataset}
        receipt = digest(expected)
        if json.loads(self.store.read("ddc_receipts", "exchange_v1", receipt)) != expected:
            raise ReplayMismatchError("exchange receipt mismatch")
        self.store.verify_identity("exchange_v1", digest(exchange.exchange_id), receipt)
        return exchange

    def read_call(self, receipt_id: str) -> LogicalCall:
        kind = "call_v2"
        try:
            doc = json.loads(self.store.read("ddc_receipts", kind, receipt_id))
        except FileNotFoundError:
            kind = "call_v1"
            doc = json.loads(self.store.read("ddc_receipts", kind, receipt_id))
        if doc["schema"] not in {"ddc-logical-call-v1", "ddc-logical-call-v2"}:
            raise ReplayMismatchError("unsupported logical call schema")
        attempts: list[PhysicalAttempt] = []
        for item in doc["attempts"]:
            attempt_kind = "attempt_v2" if "exchanges" in item else "attempt_v1"
            recorded = self.store.read("ddc_receipts", attempt_kind, digest(item))
            if json.loads(recorded) != item:
                raise ReplayMismatchError("attempt reference mismatch")
            body = item["payload"]
            payload = (
                None
                if body is None
                else read_payload(
                    body, self.store.read(doc["provider_id"], doc["operation"], body["sha256"])
                )
            )
            attempt = PhysicalAttempt(
                item["call_id"],
                item["ordinal"],
                datetime.fromisoformat(item["started_at"]),
                datetime.fromisoformat(item["completed_at"]),
                item["outcome"],
                item["status_code"],
                item["error_type"],
                tuple(sorted(item["quota"].items())),
                item["retryable"],
                item["will_retry"],
                item["delay_seconds"],
                payload,
                tuple(
                    self._read_exchange(e, doc["provider_id"], doc["operation"])
                    for e in item.get("exchanges", [])
                ),
            )
            if attempt.document() != item:
                raise ReplayMismatchError("attempt identity mismatch")
            self.store.verify_identity(attempt_kind, digest(attempt.attempt_id), digest(item))
            attempts.append(attempt)
        call = LogicalCall(
            doc["call_id"],
            doc["provider_id"],
            doc["operation"],
            doc["safe_request"],
            datetime.fromisoformat(doc["started_at"]),
            datetime.fromisoformat(doc["completed_at"]),
            doc["timeout_seconds"],
            doc["max_attempts"],
            doc["retry_cap_seconds"],
            doc["retry_schema_errors"],
            doc["validator_version"],
            tuple(attempts),
            doc["duration_seconds"],
            doc["source_run_id"],
            doc["package_version"],
            doc["source_code_identity"],
            tuple(sorted(doc.get("redirect_policy", {}).items())),
        )
        if call.receipt_id != receipt_id:
            raise ReplayMismatchError("logical call identity mismatch")
        self.store.verify_identity(kind, digest(call.call_id), receipt_id)
        return call

    def read_history(self, receipt_id: str) -> AcquisitionHistory:
        kind = "history_v4"
        try:
            doc = json.loads(self.store.read("ddc_receipts", kind, receipt_id))
        except FileNotFoundError:
            kind = "history_v3"
            try:
                doc = json.loads(self.store.read("ddc_receipts", kind, receipt_id))
            except FileNotFoundError:
                raise ReplayMismatchError(
                    "missing history; response-only receipts cannot reconstruct calls"
                ) from None
        if doc["schema"] not in {"ddc-acquisition-history-v3", "ddc-acquisition-history-v4"}:
            raise ReplayMismatchError("strict replay requires versioned logical-call history")
        history = AcquisitionHistory(
            doc["acquisition_id"],
            doc["provider_id"],
            doc["dataset_key"],
            doc["parser_version"],
            datetime.fromisoformat(doc["started_at"]),
            datetime.fromisoformat(doc["completed_at"]),
            tuple(self.read_call(ref) for ref in doc["call_receipts"]),
            doc["disposition"],
            tuple(doc["diagnostic_codes"]),
            tuple(self.read(ref) for ref in doc["evidence_receipts"]),
            doc["normalized_digest"],
            doc["previous_history_id"],
            doc["package_version"],
            doc["source_code_identity"],
        )
        if history.receipt_id != receipt_id:
            raise ReplayMismatchError("acquisition history identity mismatch")
        self.store.verify_identity(kind, digest(history.acquisition_id), receipt_id)
        return history

    def put(self, evidence: AcquisitionEvidence) -> str | None:
        # Denied means no bytes, hash or metadata are written. No implicit licence grant.
        if not self.retention_allowed(evidence):
            return None
        self.store.put(evidence.provider_id, evidence.dataset_key, evidence.payload)
        receipt = ProviderPayload(
            _canonical(evidence.document()),
            "application/json",
            None,
            evidence.payload.provenance,
            "ddc-acquisition-evidence-v2",
        )
        artifact = self.store.put("ddc_receipts", "acquisition_v2", receipt)
        return artifact.sha256

    def read(self, receipt_id: str) -> AcquisitionEvidence:
        if len(receipt_id) != 64 or any(c not in "0123456789abcdef" for c in receipt_id):
            raise ValueError("invalid receipt digest")
        data = self.store.read("ddc_receipts", "acquisition_v2", receipt_id)
        doc = json.loads(data)
        if doc["schema"] != "ddc-acquisition-evidence-v2":
            raise ValueError("unsupported evidence schema")
        content = self.store.read(doc["provider_id"], doc["dataset_key"], doc["sha256"])
        clocks = doc["clocks"]
        evidence = AcquisitionEvidence(
            doc["provider_id"],
            doc["dataset_key"],
            doc["parser_version"],
            ProviderPayload(
                content,
                doc["content_type"],
                doc["source_uri"],
                TemporalProvenance(
                    datetime.fromisoformat(clocks["observed_at"]),
                    datetime.fromisoformat(clocks["available_at"]),
                    datetime.fromisoformat(clocks["effective_at"])
                    if clocks["effective_at"]
                    else None,
                    datetime.fromisoformat(clocks["published_at"])
                    if clocks["published_at"]
                    else None,
                ),
                doc["provider_schema_version"],
                doc["response_status_code"],
            ),
            doc["disposition"],
            datetime.fromisoformat(doc["evaluated_at"]),
            tuple(doc["diagnostic_codes"]),
            doc["previous_receipt_id"],
        )
        if evidence.receipt_id != receipt_id:
            raise ValueError("evidence receipt integrity mismatch")
        return evidence


class AcquisitionCapture:
    """Per-call scope: no shared mutable collector state; captures before normalization."""

    def __init__(
        self,
        http: JsonHttpClient,
        provider_id: str,
        dataset_key: str,
        parser_version: str,
        ledger: EvidenceLedger | None = None,
        provider_schema_version: str | None = None,
    ) -> None:
        self.http = http
        self.provider_id = provider_id
        self.dataset_key = dataset_key
        self.parser_version = parser_version
        self.ledger = ledger
        self.provider_schema_version = provider_schema_version
        self.payloads: list[ProviderPayload] = []
        self.evidence: list[AcquisitionEvidence] = []
        self.diagnostic_codes: tuple[str, ...] = ()
        self.acquisition_id = uuid4().hex
        self.started_at = datetime.now(UTC)
        self.calls: list[LogicalCall] = []
        self.diagnostics: HttpRequestDiagnostics | None = None
        self.history: AcquisitionHistory | None = None
        if isinstance(http, AcquisitionReplayClient):
            http.bind(provider_id, dataset_key, parser_version)

    def __enter__(self) -> AcquisitionCapture:
        return self

    def received(self, payload: ProviderPayload) -> None:
        if isinstance(self.http, AcquisitionReplayClient) and self.http.mode == "strict":
            self.payloads.append(
                replace(
                    payload,
                    provider_schema_version=self.provider_schema_version
                    or payload.provider_schema_version,
                )
            )
            return
        self._capture(payload)

    def attempted(self, attempt: PhysicalAttempt) -> None:
        if self.ledger:
            self.ledger.put_attempt(
                attempt, self.provider_id, self.dataset_key, self.parser_version
            )

    def exchange_started(self, document: dict[str, object]) -> None:
        if self.ledger:
            identity = digest(
                [digest([document["call_id"], document["attempt_ordinal"]]), document["ordinal"]]
            )
            self.ledger._history_put(
                "exchange_start_v1",
                identity,
                document,
                datetime.fromisoformat(str(document["started_at"])),
            )

    def exchange_received(self, exchange: HttpExchange) -> None:
        if self.ledger:
            self.ledger.put_exchange(
                exchange, self.provider_id, self.dataset_key, self.parser_version, received=True
            )

    def exchanged(self, exchange: HttpExchange) -> None:
        if self.ledger:
            self.ledger.put_exchange(
                exchange, self.provider_id, self.dataset_key, self.parser_version
            )

    def completed(self, call: LogicalCall) -> None:
        self.calls.append(call)
        self.diagnostics = diagnostics_for_call(call)
        if self.ledger and not (
            isinstance(self.http, AcquisitionReplayClient) and self.http.mode == "strict"
        ):
            self.ledger.put_call(call, self.parser_version)

    def _capture(self, payload: ProviderPayload) -> None:
        payload = replace(
            payload,
            source_uri=redact_url(payload.source_uri) if payload.source_uri else None,
            provider_schema_version=self.provider_schema_version or payload.provider_schema_version,
        )
        self.payloads.append(payload)
        receipt = AcquisitionEvidence(
            self.provider_id,
            self.dataset_key,
            self.parser_version,
            payload,
            "received",
            datetime.now(UTC),
        )
        self.evidence.append(receipt)
        if self.ledger:
            self.ledger.put(receipt)

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        recorded = isinstance(self.http, (HttpClient, AcquisitionReplayClient))
        try:
            if isinstance(self.http, (HttpClient, AcquisitionReplayClient)):
                result = self.http.get_json_recorded(
                    url,
                    params=params,
                    headers=headers,
                    observer=self,
                    provider_id=self.provider_id,
                    operation=self.dataset_key,
                    source_run_id=self.acquisition_id,
                )
            else:
                result = self.http.get_json(url, params=params, headers=headers)
        except HttpError as exc:
            self.diagnostics = exc.diagnostics
            if not recorded:
                for payload in exc.raw_payloads:
                    self._capture(payload)
            raise
        self.diagnostics = result.diagnostics
        if recorded:
            return result
        if result.raw_payloads:
            for payload in result.raw_payloads:
                self._capture(payload)
        else:
            now = datetime.now(UTC)
            source_date = result.diagnostics.response_date_utc
            self._capture(
                ProviderPayload(
                    result.content,
                    result.content_type,
                    result.response_url,
                    TemporalProvenance(
                        now,
                        now,
                        published_at=datetime.fromisoformat(source_date) if source_date else None,
                    ),
                )
            )
        return replace(result, raw_payloads=(self.payloads[-1],))

    def finish(
        self,
        disposition: Disposition,
        diagnostic_codes: tuple[str, ...] = (),
        normalized_digest: str | None = None,
    ) -> tuple[AcquisitionEvidence, ...]:
        if isinstance(self.http, AcquisitionReplayClient) and self.http.mode == "strict":
            self.http.verify(disposition, diagnostic_codes, normalized_digest)
            self.history = self.http.history
            return self.history.evidence
        receipts = tuple(
            replace(
                item,
                disposition="http_error"
                if (item.payload.response_status_code or 200) >= 400
                else "received"
                if 300 <= (item.payload.response_status_code or 200) < 400
                else disposition,
                evaluated_at=datetime.now(UTC),
                diagnostic_codes=diagnostic_codes,
                previous_receipt_id=item.receipt_id,
            )
            for item in self.evidence
        )
        if self.ledger:
            for receipt in receipts:
                self.ledger.put(receipt)
        self.history = AcquisitionHistory(
            self.acquisition_id,
            self.provider_id,
            self.dataset_key,
            self.parser_version,
            self.started_at,
            datetime.now(UTC),
            tuple(self.calls),
            disposition,
            diagnostic_codes,
            receipts,
            normalized_digest,
            self.http.history.receipt_id
            if isinstance(self.http, AcquisitionReplayClient)
            else None,
            source_code_identity=code_identity(),
        )
        if self.ledger:
            self.ledger.put_history(self.history)
        return receipts

    def __exit__(
        self,
        kind: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if isinstance(exc, Exception):
            if isinstance(exc, ReplayMismatchError):
                return
            disposition: Disposition = (
                "http_error" if isinstance(exc, HttpError) else "schema_error"
            )
            code = exc.failure_kind if isinstance(exc, HttpError) else type(exc).__name__
            evidence = self.finish(disposition, self.diagnostic_codes + (code,))
            if isinstance(exc, (ProviderAcquisitionError, HttpError)):
                exc.raw_payloads = tuple(self.payloads)
                exc.evidence = evidence
                exc.diagnostics = self.diagnostics
                exc.history = self.history
            else:
                failure = ProviderAcquisitionError(
                    "Provider normalization failed: " + type(exc).__name__
                )
                failure.raw_payloads = tuple(self.payloads)
                failure.evidence = evidence
                failure.diagnostics = self.diagnostics
                failure.history = self.history
                raise failure from None


def normalized_fingerprint(value: object) -> str:
    """Deterministic interpretation digest, separate from exact provider bytes."""

    def encode(item: object) -> object:
        if isinstance(item, datetime):
            return as_utc(item).isoformat()
        raise TypeError("unsupported normalized fingerprint value")

    return sha256_bytes(
        json.dumps(
            value, default=encode, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    )


class AcquisitionReplayClient:
    """Recorded logical-call playback. No session, sleep, transport or reacquisition path."""

    def __init__(
        self,
        history: AcquisitionHistory,
        *,
        mode: Literal["strict", "reprocess"] = "strict",
        validator_versions: frozenset[str] = frozenset(),
    ) -> None:
        if not isinstance(history, AcquisitionHistory) or not history.calls:
            raise ReplayMismatchError("strict acquisition replay requires complete v3 call history")
        if mode not in {"strict", "reprocess"}:
            raise ValueError("unknown replay mode")
        if mode == "strict" and (
            history.package_version != __version__
            or history.source_code_identity != code_identity()
        ):
            raise ReplayMismatchError("strict replay package/code identity mismatch")
        if mode == "strict" and any(
            not c.redirect_policy or any(not a.exchanges for a in c.attempts) for c in history.calls
        ):
            raise ReplayMismatchError(
                "strict replay requires complete exchange history; legacy hops cannot be inferred"
            )
        if mode == "strict" and any(
            c.validator_version is not None and c.validator_version not in validator_versions
            for c in history.calls
        ):
            raise ReplayMismatchError("recorded response validator version not admitted")
        self.history = history
        self.mode = mode
        self.index = 0
        self.network_calls = 0

    def bind(self, provider: str, dataset: str, parser: str) -> None:
        if (provider, dataset) != (self.history.provider_id, self.history.dataset_key):
            raise ReplayMismatchError("replay provider/operation mismatch")
        if self.mode == "strict" and parser != self.history.parser_version:
            raise ReplayMismatchError("strict replay parser version mismatch")

    def verify(
        self, disposition: Disposition, codes: tuple[str, ...], fingerprint: str | None
    ) -> None:
        if self.index != len(self.history.calls):
            raise ReplayMismatchError("strict replay left logical calls unconsumed")
        if (disposition, codes, fingerprint) != (
            self.history.disposition,
            self.history.diagnostic_codes,
            self.history.normalized_digest,
        ):
            raise ReplayMismatchError("strict replay interpretation differs from retained evidence")

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
        observer: Any = None,
        provider_id: str = "http",
        operation: str = "get_json",
        source_run_id: str | None = None,
    ) -> JsonHttpResult:
        from requests import Request

        from daily_data_core.http import RetryableHttpError

        if self.index >= len(self.history.calls):
            raise ReplayMismatchError("recorded logical-call sequence exhausted")
        call = self.history.calls[self.index]
        safe = redact_url(Request("GET", url, params=params).prepare().url or url)
        if safe != call.safe_request:
            raise ReplayMismatchError("strict replay requested scope differs from recorded call")
        self.index += 1
        if observer is not None:
            for retained_payload in call.payloads:
                observer.received(retained_payload)
            observer.completed(call)
        diagnostics = diagnostics_for_call(call)
        if call.terminal_outcome != "success":
            error_class = RetryableHttpError if call.attempts[-1].retryable else HttpError
            raise error_class("Recorded " + call.terminal_outcome, diagnostics, call.payloads, call)
        payload = call.attempts[-1].payload
        assert payload is not None
        try:
            decoded: object = json.loads(payload.content)
        except (ValueError, UnicodeError):
            raise ReplayMismatchError("recorded successful response no longer decodes") from None
        if not isinstance(decoded, (dict, list)):
            raise ReplayMismatchError("recorded successful response has invalid root")
        return JsonHttpResult(
            cast(dict[str, object] | list[object], decoded),
            payload.content,
            payload.content_type,
            payload.source_uri or safe,
            diagnostics,
            call.payloads,
            call,
        )


class ReplayHttpClient:
    """Legacy response-only decoder; use AcquisitionReplayClient for strict call replay."""

    def __init__(self, payloads: tuple[ProviderPayload, ...]) -> None:
        self._payloads = iter(payloads)

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        payload = next(self._payloads)
        if payload.response_status_code is not None and payload.response_status_code >= 400:
            raise HttpError("Recorded HTTP failure during replay", raw_payloads=(payload,))
        try:
            decoded: object = json.loads(payload.content)
        except (ValueError, UnicodeError):
            raise HttpError(
                "Invalid JSON during evidence replay", raw_payloads=(payload,)
            ) from None
        if not isinstance(decoded, (dict, list)):
            raise HttpError("JSON root must be object or list", raw_payloads=(payload,))
        return JsonHttpResult(
            cast(dict[str, object] | list[object], decoded),
            payload.content,
            payload.content_type,
            payload.source_uri or url,
            HttpRequestDiagnostics("replay", None, 0, 0, 0, None),
            (payload,),
        )
