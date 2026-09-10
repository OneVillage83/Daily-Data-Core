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
from typing import Literal, cast

from daily_data_core.http import (
    HttpError,
    HttpRequestDiagnostics,
    JsonHttpClient,
    JsonHttpResult,
    redact_url,
)
from daily_data_core.provenance import FileSystemRawEvidenceStore, sha256_bytes
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance, as_utc

type Disposition = Literal["received", "complete", "partial", "schema_error", "http_error"]


class ProviderAcquisitionError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.raw_payloads: tuple[ProviderPayload, ...] = ()
        self.evidence: tuple[AcquisitionEvidence, ...] = ()

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
class EvidenceLedger:
    store: FileSystemRawEvidenceStore
    retention_allowed: Callable[[AcquisitionEvidence], bool]

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

    def __enter__(self) -> AcquisitionCapture:
        return self

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
        try:
            result = self.http.get_json(url, params=params, headers=headers)
        except HttpError as exc:
            for payload in exc.raw_payloads:
                self._capture(payload)
            raise
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
        self, disposition: Disposition, diagnostic_codes: tuple[str, ...] = ()
    ) -> tuple[AcquisitionEvidence, ...]:
        receipts = tuple(
            replace(
                item,
                disposition="http_error"
                if (item.payload.response_status_code or 200) >= 400
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
        return receipts

    def __exit__(
        self,
        kind: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if isinstance(exc, Exception):
            disposition: Disposition = (
                "http_error" if isinstance(exc, HttpError) else "schema_error"
            )
            code = exc.failure_kind if isinstance(exc, HttpError) else type(exc).__name__
            evidence = self.finish(disposition, self.diagnostic_codes + (code,))
            if isinstance(exc, (ProviderAcquisitionError, HttpError)):
                exc.raw_payloads = tuple(self.payloads)
                exc.evidence = evidence
            else:
                failure = ProviderAcquisitionError(
                    "Provider normalization failed: " + type(exc).__name__
                )
                failure.raw_payloads = tuple(self.payloads)
                failure.evidence = evidence
                raise failure from None


class ReplayHttpClient:
    """Explicit offline transport preserves original source clocks, including failed JSON."""

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
