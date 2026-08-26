"""Provider-neutral acquisition contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable

from daily_data_core.temporal import TemporalProvenance


class PointInTimeFidelity(StrEnum):
    STRONG = "STRONG"
    PARTIAL = "PARTIAL"
    CURRENT_STATE_ONLY = "CURRENT_STATE_ONLY"
    UNKNOWN = "UNKNOWN"


class HistoricalAvailability(StrEnum):
    ARCHIVAL = "ARCHIVAL"
    PARTIAL_ARCHIVE = "PARTIAL_ARCHIVE"
    CURRENT_ONLY = "CURRENT_ONLY"
    UNKNOWN = "UNKNOWN"


class ReliabilityTier(StrEnum):
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"
    EXPERIMENTAL = "EXPERIMENTAL"
    UNKNOWN = "UNKNOWN"


class CostClass(StrEnum):
    FREE = "FREE"
    PAID = "PAID"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


def _nonblank(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} cannot be blank")


@dataclass(frozen=True, slots=True)
class ProviderCapability:
    dataset_key: str
    point_in_time_fidelity: PointInTimeFidelity
    cadence: str
    license_class: str
    cost_class: CostClass = CostClass.UNKNOWN
    historical_availability: HistoricalAvailability = (
        HistoricalAvailability.UNKNOWN
    )
    reliability_tier: ReliabilityTier = ReliabilityTier.UNKNOWN
    schema_version: str | None = None
    expected_latency: str | None = None
    attribution_required: bool = False
    attribution_text: str | None = None

    def __post_init__(self) -> None:
        _nonblank(self.dataset_key, "dataset_key")
        _nonblank(self.cadence, "cadence")
        _nonblank(self.license_class, "license_class")
        if self.schema_version is not None:
            _nonblank(self.schema_version, "schema_version")
        if self.expected_latency is not None:
            _nonblank(self.expected_latency, "expected_latency")
        if self.attribution_text is not None:
            _nonblank(self.attribution_text, "attribution_text")
        if self.attribution_required and self.attribution_text is None:
            raise ValueError(
                "attribution_text is required when attribution is required"
            )


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    provider_id: str
    name: str
    provider_type: str
    parser_version: str
    provider_schema_version: str | None = None
    capabilities: tuple[ProviderCapability, ...] = ()

    def __post_init__(self) -> None:
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.name, "name"),
            (self.provider_type, "provider_type"),
            (self.parser_version, "parser_version"),
        ):
            _nonblank(value, label)
        if self.provider_schema_version is not None:
            _nonblank(
                self.provider_schema_version,
                "provider_schema_version",
            )
        keys = [capability.dataset_key for capability in self.capabilities]
        if len(keys) != len(set(keys)):
            raise ValueError("provider capabilities cannot repeat dataset_key")


@dataclass(frozen=True, slots=True)
class AcquisitionRequest:
    dataset_key: str
    parameters: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _nonblank(self.dataset_key, "dataset_key")
        keys = [key for key, _ in self.parameters]
        if any(not key.strip() for key in keys):
            raise ValueError("acquisition parameter keys cannot be blank")
        if len(keys) != len(set(keys)):
            raise ValueError("acquisition parameter keys must be unique")


@dataclass(frozen=True, slots=True)
class ProviderPayload:
    content: bytes = field(repr=False)
    content_type: str
    source_uri: str | None
    provenance: TemporalProvenance
    provider_schema_version: str | None = None

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError("provider payload cannot be empty")
        _nonblank(self.content_type, "content_type")
        if self.source_uri is not None:
            _nonblank(self.source_uri, "source_uri")
        if self.provider_schema_version is not None:
            _nonblank(
                self.provider_schema_version,
                "provider_schema_version",
            )


@runtime_checkable
class ProviderAdapter(Protocol):
    @property
    def descriptor(self) -> ProviderDescriptor: ...

    def acquire(
        self,
        request: AcquisitionRequest,
    ) -> tuple[ProviderPayload, ...]: ...
