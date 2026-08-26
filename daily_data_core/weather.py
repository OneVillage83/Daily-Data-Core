"""Shared weather forecast acquisition and comparison."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import cast

from daily_data_core.http import JsonHttpClient
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance, require_aware

CARDINAL_DEGREES: dict[str, float] = {
    "N": 0.0,
    "NNE": 22.5,
    "NE": 45.0,
    "ENE": 67.5,
    "E": 90.0,
    "ESE": 112.5,
    "SE": 135.0,
    "SSE": 157.5,
    "S": 180.0,
    "SSW": 202.5,
    "SW": 225.0,
    "WSW": 247.5,
    "W": 270.0,
    "WNW": 292.5,
    "NW": 315.0,
    "NNW": 337.5,
}


class WeatherProviderSchemaError(RuntimeError):
    pass


def _validate_optional_finite(value: float | None, label: str) -> None:
    if value is not None and not math.isfinite(value):
        raise ValueError(f"{label} must be finite when present")


@dataclass(frozen=True, slots=True)
class ForecastSnapshot:
    """Sport-neutral normalized forecast observation.

    `source_metadata` carries provider-specific descriptive fields that are useful
    to consumers but do not belong in the cross-provider numeric schema. The
    tuple form keeps the snapshot immutable and serializable without allowing a
    provider-specific dictionary to redefine core semantics.
    """

    provider_id: str
    forecast_time: datetime
    observed_at: datetime
    available_at: datetime
    provider_updated_at: datetime | None
    temperature_f: float | None
    humidity_pct: float | None
    precipitation_probability_pct: float | None
    wind_speed_mph: float | None
    wind_direction_deg: float | None
    short_forecast: str | None = None
    cloud_cover_pct: float | None = None
    pressure_hpa: float | None = None
    source_metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.provider_id.strip():
            raise ValueError("provider_id cannot be blank")
        for value, label in (
            (self.forecast_time, "forecast_time"),
            (self.observed_at, "observed_at"),
            (self.available_at, "available_at"),
            (self.provider_updated_at, "provider_updated_at"),
        ):
            if value is not None:
                require_aware(value, label)
        if self.available_at > self.observed_at:
            raise ValueError("available_at cannot be later than observed_at")

        for value, label in (
            (self.temperature_f, "temperature_f"),
            (self.humidity_pct, "humidity_pct"),
            (self.precipitation_probability_pct, "precipitation_probability_pct"),
            (self.wind_speed_mph, "wind_speed_mph"),
            (self.wind_direction_deg, "wind_direction_deg"),
            (self.cloud_cover_pct, "cloud_cover_pct"),
            (self.pressure_hpa, "pressure_hpa"),
        ):
            _validate_optional_finite(value, label)

        for value, label in (
            (self.humidity_pct, "humidity_pct"),
            (self.precipitation_probability_pct, "precipitation_probability_pct"),
            (self.cloud_cover_pct, "cloud_cover_pct"),
        ):
            if value is not None and not 0.0 <= value <= 100.0:
                raise ValueError(f"{label} must be in [0, 100]")
        if self.wind_speed_mph is not None and self.wind_speed_mph < 0:
            raise ValueError("wind_speed_mph cannot be negative")
        if (
            self.wind_direction_deg is not None
            and not 0.0 <= self.wind_direction_deg < 360.0
        ):
            raise ValueError("wind_direction_deg must be in [0, 360)")
        if self.pressure_hpa is not None and self.pressure_hpa <= 0:
            raise ValueError("pressure_hpa must be positive when present")
        if self.short_forecast is not None and not self.short_forecast.strip():
            raise ValueError("short_forecast cannot be blank when present")

        metadata_keys = [key for key, _ in self.source_metadata]
        if any(
            not key.strip() or not value.strip()
            for key, value in self.source_metadata
        ):
            raise ValueError("source_metadata keys and values must be nonblank")
        if len(metadata_keys) != len(set(metadata_keys)):
            raise ValueError("source_metadata keys must be unique")

    def metadata_value(self, key: str) -> str | None:
        """Return one provider-specific metadata value without exposing mutability."""

        return next(
            (
                value
                for metadata_key, value in self.source_metadata
                if metadata_key == key
            ),
            None,
        )


@dataclass(frozen=True, slots=True)
class WeatherAcquisitionResult:
    forecast: ForecastSnapshot
    raw_payloads: tuple[ProviderPayload, ...]


@dataclass(frozen=True, slots=True)
class WeatherComparison:
    agreement: str
    temperature_difference_f: float | None
    precipitation_difference_points: float | None
    wind_speed_difference_mph: float | None


def parse_wind_speed(text: str | None) -> float | None:
    if not text:
        return None
    numbers = [float(value) for value in re.findall(r"\d+(?:\.\d+)?", text)]
    if not numbers:
        return None
    return sum(numbers[:2]) / min(len(numbers), 2)


def _timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise WeatherProviderSchemaError(f"{label} must be a timestamp string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise WeatherProviderSchemaError(f"{label} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise WeatherProviderSchemaError(f"{label} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise WeatherProviderSchemaError(f"{label} must be an object")
    return cast(dict[str, object], value)


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise WeatherProviderSchemaError(f"{label} must be a list")
    return cast(list[object], value)


def _optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _nested_value(container: object) -> float | None:
    if not isinstance(container, dict):
        return None
    return _optional_float(cast(dict[str, object], container).get("value"))


def _raw_payload(
    result_content: bytes,
    content_type: str,
    source_uri: str,
    observed_at: datetime,
) -> ProviderPayload:
    return ProviderPayload(
        content=result_content,
        content_type=content_type,
        source_uri=source_uri,
        provenance=TemporalProvenance(
            observed_at=observed_at,
            available_at=observed_at,
        ),
    )


def _metadata_pairs(**values: object) -> tuple[tuple[str, str], ...]:
    metadata: list[tuple[str, str]] = []
    for key, value in values.items():
        if isinstance(value, str) and value.strip():
            metadata.append((key, value))
    return tuple(metadata)


class NwsWeatherClient:
    def __init__(self, http: JsonHttpClient, user_agent: str) -> None:
        if not user_agent.strip():
            raise ValueError("NWS user_agent cannot be blank")
        self.http = http
        self.headers = {"User-Agent": user_agent, "Accept": "application/geo+json"}

    def collect(
        self, latitude: float, longitude: float, target_time: datetime
    ) -> WeatherAcquisitionResult:
        require_aware(target_time, "target_time")
        point_result = self.http.get_json(
            f"https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}",
            headers=self.headers,
        )
        point_observed_at = datetime.now(timezone.utc)
        point = _object(point_result.payload, "NWS point response")
        point_properties = _object(point.get("properties"), "NWS point properties")
        forecast_url = point_properties.get("forecastHourly")
        if not isinstance(forecast_url, str) or not forecast_url:
            raise WeatherProviderSchemaError("NWS point response missing forecastHourly")

        forecast_result = self.http.get_json(forecast_url, headers=self.headers)
        forecast_observed_at = datetime.now(timezone.utc)
        forecast = _object(forecast_result.payload, "NWS forecast response")
        properties = _object(forecast.get("properties"), "NWS forecast properties")
        periods = [
            _object(item, "NWS period")
            for item in _list(properties.get("periods"), "NWS periods")
        ]
        if not periods:
            raise WeatherProviderSchemaError("NWS hourly forecast contains no periods")

        target_utc = target_time.astimezone(timezone.utc)
        selected = min(
            periods,
            key=lambda period: abs(
                (
                    _timestamp(period.get("startTime"), "period.startTime") - target_utc
                ).total_seconds()
            ),
        )
        direction = selected.get("windDirection")
        wind_speed_text = selected.get("windSpeed")
        short_forecast = selected.get("shortForecast")
        provider_updated_at = None
        updated = properties.get("updated")
        if isinstance(updated, str) and updated.strip():
            provider_updated_at = _timestamp(updated, "forecast.updated")
        temperature = _optional_float(selected.get("temperature"))
        if selected.get("temperatureUnit") != "F":
            temperature = None

        snapshot = ForecastSnapshot(
            provider_id="nws",
            forecast_time=_timestamp(selected.get("startTime"), "period.startTime"),
            observed_at=forecast_observed_at,
            available_at=forecast_observed_at,
            provider_updated_at=provider_updated_at,
            temperature_f=temperature,
            humidity_pct=_nested_value(selected.get("relativeHumidity")),
            precipitation_probability_pct=_nested_value(
                selected.get("probabilityOfPrecipitation")
            ),
            wind_speed_mph=parse_wind_speed(
                wind_speed_text if isinstance(wind_speed_text, str) else None
            ),
            wind_direction_deg=(
                CARDINAL_DEGREES.get(direction) if isinstance(direction, str) else None
            ),
            short_forecast=short_forecast if isinstance(short_forecast, str) else None,
            source_metadata=_metadata_pairs(
                wind_speed_text=wind_speed_text,
                wind_direction_cardinal=direction,
                forecast_office=point_properties.get("cwa"),
            ),
        )
        return WeatherAcquisitionResult(
            forecast=snapshot,
            raw_payloads=(
                _raw_payload(
                    point_result.content,
                    point_result.content_type,
                    point_result.response_url,
                    point_observed_at,
                ),
                _raw_payload(
                    forecast_result.content,
                    forecast_result.content_type,
                    forecast_result.response_url,
                    forecast_observed_at,
                ),
            ),
        )


class OpenWeatherClient:
    def __init__(self, http: JsonHttpClient) -> None:
        self.http = http

    def collect(
        self, latitude: float, longitude: float, target_time: datetime, api_key: str
    ) -> WeatherAcquisitionResult:
        require_aware(target_time, "target_time")
        if not api_key.strip():
            raise ValueError("OpenWeather api_key cannot be blank")
        result = self.http.get_json(
            "https://api.openweathermap.org/data/3.0/onecall",
            params={
                "lat": str(latitude),
                "lon": str(longitude),
                "appid": api_key,
                "units": "imperial",
                "exclude": "minutely,daily,alerts",
            },
        )
        observed_at = datetime.now(timezone.utc)
        root = _object(result.payload, "OpenWeather response")
        hourly = [
            _object(item, "OpenWeather hourly item")
            for item in _list(root.get("hourly"), "OpenWeather hourly")
        ]
        if not hourly:
            raise WeatherProviderSchemaError(
                "OpenWeather response contains no hourly forecasts"
            )
        target_epoch = target_time.astimezone(timezone.utc).timestamp()
        selected = min(
            hourly,
            key=lambda item: abs(
                (_optional_float(item.get("dt")) or 0.0) - target_epoch
            ),
        )
        epoch = _optional_float(selected.get("dt"))
        if epoch is None:
            raise WeatherProviderSchemaError("OpenWeather hourly item missing dt")
        pop = _optional_float(selected.get("pop"))
        short_forecast = None
        weather_items = selected.get("weather")
        if isinstance(weather_items, list) and weather_items:
            first = weather_items[0]
            if isinstance(first, dict):
                description = cast(dict[str, object], first).get("description")
                short_forecast = description if isinstance(description, str) else None
        snapshot = ForecastSnapshot(
            provider_id="openweather",
            forecast_time=datetime.fromtimestamp(epoch, tz=timezone.utc),
            observed_at=observed_at,
            available_at=observed_at,
            provider_updated_at=None,
            temperature_f=_optional_float(selected.get("temp")),
            humidity_pct=_optional_float(selected.get("humidity")),
            precipitation_probability_pct=pop * 100.0 if pop is not None else None,
            wind_speed_mph=_optional_float(selected.get("wind_speed")),
            wind_direction_deg=_optional_float(selected.get("wind_deg")),
            short_forecast=short_forecast,
            cloud_cover_pct=_optional_float(selected.get("clouds")),
            pressure_hpa=_optional_float(selected.get("pressure")),
        )
        return WeatherAcquisitionResult(
            forecast=snapshot,
            raw_payloads=(
                _raw_payload(
                    result.content,
                    result.content_type,
                    result.response_url,
                    observed_at,
                ),
            ),
        )


def compare_forecasts(first: ForecastSnapshot, second: ForecastSnapshot) -> WeatherComparison:
    def delta(a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return abs(a - b)

    temperature = delta(first.temperature_f, second.temperature_f)
    precipitation = delta(
        first.precipitation_probability_pct,
        second.precipitation_probability_pct,
    )
    wind = delta(first.wind_speed_mph, second.wind_speed_mph)
    disagreements = 0
    if temperature is not None and temperature > 5.0:
        disagreements += 1
    if precipitation is not None and precipitation > 25.0:
        disagreements += 1
    if wind is not None and wind > 6.0:
        disagreements += 1
    if disagreements == 0:
        agreement = "strong"
    elif disagreements == 1:
        agreement = "moderate"
    else:
        agreement = "weak"
    return WeatherComparison(
        agreement=agreement,
        temperature_difference_f=temperature,
        precipitation_difference_points=precipitation,
        wind_speed_difference_mph=wind,
    )
