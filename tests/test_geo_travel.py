from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from daily_data_core.travel import TravelSegment, build_recovery_context, exact_rest_hours
from daily_data_core.venues import GeoPoint, haversine_miles, vector_components


def test_haversine_distance_is_reasonable_for_sf_to_la() -> None:
    sf = GeoPoint(37.7749, -122.4194)
    la = GeoPoint(34.0522, -118.2437)
    distance = haversine_miles(sf, la)
    assert 340.0 < distance < 360.0


def test_vector_components_are_neutral_geometry() -> None:
    longitudinal, cross = vector_components(10.0, 90.0, 90.0)
    assert longitudinal == pytest.approx(10.0)
    assert cross == pytest.approx(0.0, abs=1e-10)


def test_travel_and_exact_rest_context() -> None:
    departed = datetime(2026, 9, 10, 18, 0, tzinfo=timezone.utc)
    arrived = departed + timedelta(hours=2)
    next_start = departed + timedelta(hours=48)
    segment = TravelSegment(
        origin=GeoPoint(37.7749, -122.4194),
        destination=GeoPoint(40.7128, -74.0060),
        departed_at=departed,
        arrived_at=arrived,
        origin_timezone="America/Los_Angeles",
        destination_timezone="America/New_York",
    )
    context = build_recovery_context(
        previous_event_end=departed,
        next_event_start=next_start,
        segment=segment,
    )
    assert exact_rest_hours(departed, next_start) == 48.0
    assert context.exact_rest_hours == 48.0
    assert context.travel_distance_miles > 2500.0
    assert context.timezone_shift_hours == 3.0
    assert context.travel_elapsed_hours == 2.0
