from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from daily_data_core.http import HttpRequestDiagnostics, JsonHttpResult
from daily_data_core.weather import NwsWeatherClient, OpenWeatherClient


class SequenceHttp:
    def __init__(self, results: list[JsonHttpResult]) -> None:
        self.results = results
        self.calls: list[tuple[str, dict[str, str] | None, dict[str, str] | None]] = []

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        self.calls.append((url, params, headers))
        return self.results.pop(0)


def _result(payload: dict[str, object], url: str) -> JsonHttpResult:
    content = json.dumps(payload, separators=(",", ":")).encode()
    return JsonHttpResult(
        payload=payload,
        content=content,
        content_type="application/json",
        response_url=url,
        diagnostics=HttpRequestDiagnostics(
            request_status="success",
            status_code=200,
            attempts=1,
            retries_performed=0,
            duration_seconds=0.01,
            response_date_utc=None,
        ),
    )


def test_nws_preserves_mlb_compatibility_metadata_and_exact_evidence() -> None:
    point_payload: dict[str, object] = {
        "properties": {
            "forecastHourly": "https://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly",
            "cwa": "MTR",
        }
    }
    forecast_payload: dict[str, object] = {
        "properties": {
            "updated": "2026-08-26T18:00:00Z",
            "periods": [
                {
                    "startTime": "2026-08-26T20:00:00-07:00",
                    "temperature": 74,
                    "temperatureUnit": "F",
                    "relativeHumidity": {"value": 52},
                    "probabilityOfPrecipitation": {"value": 10},
                    "windSpeed": "10 to 20 mph",
                    "windDirection": "W",
                    "shortForecast": "Mostly Clear",
                }
            ],
        }
    }
    point = _result(point_payload, "https://api.weather.gov/points/1.0000,2.0000")
    forecast = _result(
        forecast_payload,
        "https://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly",
    )
    http = SequenceHttp([point, forecast])
    client = NwsWeatherClient(http, "TheDailyLine/1.0 test@example.com")  # type: ignore[arg-type]

    result = client.collect(
        1.0,
        2.0,
        datetime(2026, 8, 27, 3, 0, tzinfo=timezone.utc),
    )

    snapshot = result.forecast
    assert snapshot.wind_speed_mph == pytest.approx(15.0)
    assert snapshot.wind_direction_deg == 270.0
    assert snapshot.metadata_value("wind_speed_text") == "10 to 20 mph"
    assert snapshot.metadata_value("wind_direction_cardinal") == "W"
    assert snapshot.metadata_value("forecast_office") == "MTR"
    assert result.raw_payloads[0].content == point.content
    assert result.raw_payloads[1].content == forecast.content


def test_openweather_preserves_cloud_cover_pressure_and_exact_evidence() -> None:
    payload: dict[str, object] = {
        "hourly": [
            {
                "dt": 1787799600,
                "temp": 68.5,
                "humidity": 61,
                "pop": 0.25,
                "wind_speed": 9.2,
                "wind_deg": 245,
                "clouds": 37,
                "pressure": 1014,
                "weather": [{"description": "scattered clouds"}],
            }
        ]
    }
    raw = _result(payload, "https://api.openweathermap.org/data/3.0/onecall")
    http = SequenceHttp([raw])
    client = OpenWeatherClient(http)  # type: ignore[arg-type]

    result = client.collect(
        38.58,
        -121.49,
        datetime.fromtimestamp(1787799600, tz=timezone.utc),
        "test-key",
    )

    snapshot = result.forecast
    assert snapshot.temperature_f == 68.5
    assert snapshot.precipitation_probability_pct == 25.0
    assert snapshot.cloud_cover_pct == 37.0
    assert snapshot.pressure_hpa == 1014.0
    assert snapshot.short_forecast == "scattered clouds"
    assert result.raw_payloads[0].content == raw.content


def test_weather_snapshot_rejects_invalid_provider_values() -> None:
    now = datetime(2026, 8, 26, 18, 0, tzinfo=timezone.utc)
    from daily_data_core.weather import ForecastSnapshot

    with pytest.raises(ValueError, match="cloud_cover_pct"):
        ForecastSnapshot(
            provider_id="test",
            forecast_time=now,
            observed_at=now,
            available_at=now,
            provider_updated_at=None,
            temperature_f=70.0,
            humidity_pct=50.0,
            precipitation_probability_pct=0.0,
            wind_speed_mph=1.0,
            wind_direction_deg=0.0,
            cloud_cover_pct=101.0,
        )
