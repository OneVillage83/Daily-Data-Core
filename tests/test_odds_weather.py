from __future__ import annotations

from datetime import datetime, timezone

import pytest

from daily_data_core.odds import provider_sport_key
from daily_data_core.weather import ForecastSnapshot, compare_forecasts, parse_wind_speed


def test_provider_sport_keys_cover_initial_daily_line_sports() -> None:
    assert provider_sport_key("MLB") == "baseball_mlb"
    assert provider_sport_key("nfl") == "americanfootball_nfl"
    assert provider_sport_key("NCAAF") == "americanfootball_ncaaf"


def test_parse_wind_speed_averages_nws_ranges() -> None:
    assert parse_wind_speed("10 to 20 mph") == pytest.approx(15.0)
    assert parse_wind_speed("12 mph") == pytest.approx(12.0)
    assert parse_wind_speed(None) is None


def test_weather_comparison_is_sport_neutral() -> None:
    now = datetime(2026, 8, 26, 18, 0, tzinfo=timezone.utc)
    first = ForecastSnapshot(
        provider_id="nws",
        forecast_time=now,
        observed_at=now,
        available_at=now,
        provider_updated_at=now,
        temperature_f=70.0,
        humidity_pct=50.0,
        precipitation_probability_pct=10.0,
        wind_speed_mph=8.0,
        wind_direction_deg=270.0,
    )
    second = ForecastSnapshot(
        provider_id="openweather",
        forecast_time=now,
        observed_at=now,
        available_at=now,
        provider_updated_at=None,
        temperature_f=72.0,
        humidity_pct=55.0,
        precipitation_probability_pct=12.0,
        wind_speed_mph=10.0,
        wind_direction_deg=265.0,
    )
    comparison = compare_forecasts(first, second)
    assert comparison.agreement == "strong"
    assert comparison.temperature_difference_f == 2.0
