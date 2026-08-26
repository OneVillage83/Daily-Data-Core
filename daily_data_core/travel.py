"""Neutral travel, timezone-shift, and exact-rest primitives."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from daily_data_core.temporal import require_aware
from daily_data_core.venues import GeoPoint, haversine_miles


def _zone(name: str, label: str) -> ZoneInfo:
    if not name.strip():
        raise ValueError(f"{label} cannot be blank")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"{label} is not a known timezone") from exc


@dataclass(frozen=True, slots=True)
class TravelSegment:
    origin: GeoPoint
    destination: GeoPoint
    departed_at: datetime
    arrived_at: datetime
    origin_timezone: str
    destination_timezone: str

    def __post_init__(self) -> None:
        require_aware(self.departed_at, "departed_at")
        require_aware(self.arrived_at, "arrived_at")
        if self.arrived_at < self.departed_at:
            raise ValueError("arrived_at cannot precede departed_at")
        _zone(self.origin_timezone, "origin_timezone")
        _zone(self.destination_timezone, "destination_timezone")

    @property
    def distance_miles(self) -> float:
        return haversine_miles(self.origin, self.destination)

    @property
    def elapsed_hours(self) -> float:
        return (self.arrived_at - self.departed_at).total_seconds() / 3600.0


@dataclass(frozen=True, slots=True)
class RecoveryContext:
    exact_rest_hours: float
    travel_distance_miles: float
    timezone_shift_hours: float
    travel_elapsed_hours: float

    def __post_init__(self) -> None:
        for value, label in (
            (self.exact_rest_hours, "exact_rest_hours"),
            (self.travel_distance_miles, "travel_distance_miles"),
            (self.timezone_shift_hours, "timezone_shift_hours"),
            (self.travel_elapsed_hours, "travel_elapsed_hours"),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{label} must be finite")
        if self.exact_rest_hours < 0:
            raise ValueError("exact_rest_hours cannot be negative")
        if self.travel_distance_miles < 0:
            raise ValueError("travel_distance_miles cannot be negative")
        if self.travel_elapsed_hours < 0:
            raise ValueError("travel_elapsed_hours cannot be negative")


def timezone_shift_hours(
    origin_timezone: str,
    destination_timezone: str,
    at: datetime,
) -> float:
    require_aware(at, "at")
    origin_offset = at.astimezone(_zone(origin_timezone, "origin_timezone")).utcoffset()
    destination_offset = at.astimezone(
        _zone(destination_timezone, "destination_timezone")
    ).utcoffset()
    if origin_offset is None or destination_offset is None:
        raise ValueError("timezone offset unavailable")
    return (destination_offset - origin_offset).total_seconds() / 3600.0


def exact_rest_hours(
    previous_event_end: datetime,
    next_event_start: datetime,
) -> float:
    require_aware(previous_event_end, "previous_event_end")
    require_aware(next_event_start, "next_event_start")
    if next_event_start < previous_event_end:
        raise ValueError("next_event_start cannot precede previous_event_end")
    return (next_event_start - previous_event_end).total_seconds() / 3600.0


def build_recovery_context(
    *,
    previous_event_end: datetime,
    next_event_start: datetime,
    segment: TravelSegment | None = None,
) -> RecoveryContext:
    rest = exact_rest_hours(previous_event_end, next_event_start)
    if segment is None:
        return RecoveryContext(
            exact_rest_hours=rest,
            travel_distance_miles=0.0,
            timezone_shift_hours=0.0,
            travel_elapsed_hours=0.0,
        )
    shift = timezone_shift_hours(
        segment.origin_timezone,
        segment.destination_timezone,
        segment.arrived_at,
    )
    return RecoveryContext(
        exact_rest_hours=rest,
        travel_distance_miles=segment.distance_miles,
        timezone_shift_hours=shift,
        travel_elapsed_hours=segment.elapsed_hours,
    )
