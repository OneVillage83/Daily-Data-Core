"""Consumer admission regressions; all provider responses are synthetic."""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from daily_data_core.http import HttpRequestDiagnostics, JsonHttpResult
from daily_data_core.markets import FreshnessStatus, classify_freshness
from daily_data_core.temporal import TemporalProvenance
from daily_data_core.travel import TravelSegment, exact_rest_hours
from daily_data_core.venues import GeoPoint, Venue
from daily_data_core.weather import NwsWeatherClient, WeatherProviderSchemaError


class UntrustedPointHttp:
    def __init__(self, forecast_url: str) -> None:
        self.forecast_url = forecast_url
        self.calls: list[str] = []

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        self.calls.append(url)
        if len(self.calls) > 1:
            pytest.fail("untrusted provider-derived URL reached HTTP transport")
        return JsonHttpResult(
            payload={"properties": {"forecastHourly": self.forecast_url}},
            content=b'{"fixture":"synthetic-point"}',
            content_type="application/json",
            response_url=url,
            diagnostics=HttpRequestDiagnostics("success", 200, 1, 0, 0.0, None),
        )


@pytest.mark.parametrize(
    "forecast_url",
    [
        "https://example.invalid/forecast",
        "http://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly",
        "https://user:password@api.weather.gov/gridpoints/MTR/1,2/forecast/hourly",
        "https://api.weather.gov:444/gridpoints/MTR/1,2/forecast/hourly",
        "https://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly?token=fixture",
        "https://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly#fragment",
        "https://api.weather.gov/other/path",
        "https://api.weather.gov:invalid/gridpoints/MTR/1,2/forecast/hourly",
    ],
)
def test_nws_rejects_untrusted_followup_before_transport(forecast_url: str) -> None:
    http = UntrustedPointHttp(forecast_url)
    client = NwsWeatherClient(http, "DDC synthetic regression")
    with pytest.raises(WeatherProviderSchemaError, match="untrusted"):
        client.collect(1.0, 2.0, datetime(2026, 9, 9, tzinfo=UTC))
    assert len(http.calls) == 1


@pytest.mark.parametrize(
    ("start", "end", "expected"),
    [
        (datetime(2026, 3, 8, 1, 30), datetime(2026, 3, 8, 3, 30), 1.0),
        (datetime(2026, 11, 1, 0, 30), datetime(2026, 11, 1, 2, 30), 3.0),
    ],
)
def test_rest_and_travel_use_elapsed_utc_across_dst(
    start: datetime, end: datetime, expected: float
) -> None:
    zone = ZoneInfo("America/Los_Angeles")
    departed = start.replace(tzinfo=zone)
    arrived = end.replace(tzinfo=zone)
    assert exact_rest_hours(departed, arrived) == expected
    assert TravelSegment(
        GeoPoint(1.0, 2.0), GeoPoint(3.0, 4.0), departed, arrived,
        "America/Los_Angeles", "America/Los_Angeles",
    ).elapsed_hours == expected


def test_repeated_hour_cannot_reverse_actual_time() -> None:
    zone = ZoneInfo("America/Los_Angeles")
    departed = datetime(2026, 11, 1, 1, 15, tzinfo=zone, fold=1)
    arrived = datetime(2026, 11, 1, 1, 45, tzinfo=zone, fold=0)
    with pytest.raises(ValueError, match="precede"):
        exact_rest_hours(departed, arrived)
    with pytest.raises(ValueError, match="precede"):
        TravelSegment(
            GeoPoint(1.0, 2.0), GeoPoint(3.0, 4.0), departed, arrived,
            "America/Los_Angeles", "America/Los_Angeles",
        )


def test_venue_rejects_unknown_timezone() -> None:
    with pytest.raises(ValueError, match="timezone"):
        Venue("fixture", "Synthetic venue", GeoPoint(1.0, 2.0), "Unknown/Zone")


def test_temporal_eligibility_and_freshness_do_not_ignore_repeated_hour() -> None:
    zone = ZoneInfo("America/Los_Angeles")
    first = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=0)
    second = datetime(2026, 11, 1, 1, 30, tzinfo=zone, fold=1)
    provenance = TemporalProvenance(observed_at=second, available_at=second)
    assert not provenance.eligible_at(first)
    assert classify_freshness(first, second) == FreshnessStatus.STALE
    assert classify_freshness(second, first) == FreshnessStatus.UNKNOWN
    with pytest.raises(ValueError, match="later"):
        TemporalProvenance(observed_at=first, available_at=second)
