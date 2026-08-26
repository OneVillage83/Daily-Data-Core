"""Shared venue and geospatial primitives."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum


class RoofType(StrEnum):
    OPEN = "OPEN"
    RETRACTABLE = "RETRACTABLE"
    FIXED = "FIXED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class GeoPoint:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.latitude) or not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be finite and between -90 and 90")
        if (
            not math.isfinite(self.longitude)
            or not -180.0 <= self.longitude <= 180.0
        ):
            raise ValueError("longitude must be finite and between -180 and 180")


@dataclass(frozen=True, slots=True)
class Venue:
    venue_id: str
    name: str
    location: GeoPoint
    timezone_name: str
    roof_type: RoofType = RoofType.UNKNOWN
    reference_bearing_deg: float | None = None

    def __post_init__(self) -> None:
        if (
            not self.venue_id.strip()
            or not self.name.strip()
            or not self.timezone_name.strip()
        ):
            raise ValueError("venue_id, name, and timezone_name cannot be blank")
        if self.reference_bearing_deg is not None and (
            not math.isfinite(self.reference_bearing_deg)
            or not 0.0 <= self.reference_bearing_deg < 360.0
        ):
            raise ValueError(
                "reference_bearing_deg must be finite and in [0, 360)"
            )


def haversine_miles(first: GeoPoint, second: GeoPoint) -> float:
    radius_miles = 3958.7613
    lat1 = math.radians(first.latitude)
    lat2 = math.radians(second.latitude)
    delta_lat = math.radians(second.latitude - first.latitude)
    delta_lon = math.radians(second.longitude - first.longitude)
    a = (
        math.sin(delta_lat / 2.0) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2.0) ** 2
    )
    return 2.0 * radius_miles * math.asin(min(1.0, math.sqrt(a)))


def initial_bearing_deg(first: GeoPoint, second: GeoPoint) -> float:
    lat1 = math.radians(first.latitude)
    lat2 = math.radians(second.latitude)
    delta_lon = math.radians(second.longitude - first.longitude)
    x = math.sin(delta_lon) * math.cos(lat2)
    y = (
        math.cos(lat1) * math.sin(lat2)
        - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    )
    return (math.degrees(math.atan2(x, y)) + 360.0) % 360.0


def angular_difference_deg(first: float, second: float) -> float:
    if not math.isfinite(first) or not math.isfinite(second):
        raise ValueError("angles must be finite")
    return (first - second + 180.0) % 360.0 - 180.0


def vector_components(
    magnitude: float,
    direction_to_deg: float,
    reference_bearing_deg: float,
) -> tuple[float, float]:
    if magnitude < 0 or not math.isfinite(magnitude):
        raise ValueError("magnitude must be finite and nonnegative")
    if not math.isfinite(direction_to_deg) or not math.isfinite(
        reference_bearing_deg
    ):
        raise ValueError("directions must be finite")
    difference = math.radians(
        angular_difference_deg(direction_to_deg, reference_bearing_deg)
    )
    longitudinal = magnitude * math.cos(difference)
    cross = magnitude * math.sin(difference)
    return longitudinal, cross
