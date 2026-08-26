"""Shared temporal provenance primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


def require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")


def as_utc(value: datetime) -> datetime:
    require_aware(value, "timestamp")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class TemporalProvenance:
    """Source clocks required to reason about point-in-time eligibility."""

    observed_at: datetime
    available_at: datetime
    effective_at: datetime | None = None
    published_at: datetime | None = None

    def __post_init__(self) -> None:
        for value, label in (
            (self.observed_at, "observed_at"),
            (self.available_at, "available_at"),
            (self.effective_at, "effective_at"),
            (self.published_at, "published_at"),
        ):
            if value is not None:
                require_aware(value, label)
        if self.available_at > self.observed_at:
            raise ValueError("available_at cannot be later than observed_at")

    def eligible_at(self, cutoff: datetime) -> bool:
        require_aware(cutoff, "cutoff")
        return self.available_at <= cutoff
