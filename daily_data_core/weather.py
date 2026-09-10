"""Shared weather forecast acquisition and comparison."""

from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import cast
from urllib.parse import urlsplit

from daily_data_core.acquisition import (
    AcquisitionCapture,
    AcquisitionEvidence,
    AcquisitionHistory,
    EvidenceLedger,
    ProviderAcquisitionError,
    normalized_fingerprint,
)
from daily_data_core.http import JsonHttpClient
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import as_utc, require_aware

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


class WeatherProviderSchemaError(ProviderAcquisitionError):
    pass


def validated_nws_hourly_url(value: object) -> str:
    """Restrict provider-directed requests to the NWS hourly endpoint."""
    if not isinstance(value, str) or not value.strip():
        raise WeatherProviderSchemaError("NWS point response missing forecastHourly")
    url = value.strip()
    try:
        parts = urlsplit(url)
        trusted = (
            parts.scheme == "https"
            and parts.hostname == "api.weather.gov"
            and parts.username is None
            and parts.password is None
            and parts.port in {None, 443}
            and not parts.query
            and not parts.fragment
            and re.fullmatch(r"/gridpoints/[A-Z0-9]{3}/[0-9]+,[0-9]+/forecast/hourly", parts.path)
            is not None
        )
    except ValueError:
        trusted = False
    if not trusted:
        # Never echo provider-controlled URLs, userinfo, or query credentials.
        raise WeatherProviderSchemaError("NWS point response has untrusted forecastHourly URL")
    return url


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
    wind_gust_mph: float | None = None
    wind_gust_status: str = "not_supplied"

    def to_json(self) -> str:
        document = asdict(self)
        for key in ("forecast_time", "observed_at", "available_at", "provider_updated_at"):
            value = document[key]
            document[key] = value.isoformat() if value is not None else None
        return json.dumps(
            {"schema": "ddc-forecast-v2", "forecast": document}, sort_keys=True, allow_nan=False
        )

    @classmethod
    def from_json(cls, value: str) -> ForecastSnapshot:
        document = json.loads(value)
        if document["schema"] != "ddc-forecast-v2":
            raise ValueError("unsupported forecast schema")
        facts = document["forecast"]
        for key in ("forecast_time", "observed_at", "available_at", "provider_updated_at"):
            facts[key] = datetime.fromisoformat(facts[key]) if facts[key] is not None else None
        facts["source_metadata"] = tuple(tuple(pair) for pair in facts["source_metadata"])
        return cls(**facts)

    def __post_init__(self) -> None:
        if self.wind_gust_mph is not None and self.wind_gust_status == "not_supplied":
            object.__setattr__(self, "wind_gust_status", "reported")
        if (self.wind_gust_status == "reported") != (self.wind_gust_mph is not None):
            raise ValueError("wind gust status must agree with value presence")
        if not self.provider_id.strip():
            raise ValueError("provider_id cannot be blank")
        for timestamp_value, label in (
            (self.forecast_time, "forecast_time"),
            (self.observed_at, "observed_at"),
            (self.available_at, "available_at"),
            (self.provider_updated_at, "provider_updated_at"),
        ):
            if timestamp_value is not None:
                require_aware(timestamp_value, label)
        if as_utc(self.available_at) > as_utc(self.observed_at):
            raise ValueError("available_at cannot be later than observed_at")

        for numeric_value, label in (
            (self.temperature_f, "temperature_f"),
            (self.humidity_pct, "humidity_pct"),
            (self.precipitation_probability_pct, "precipitation_probability_pct"),
            (self.wind_speed_mph, "wind_speed_mph"),
            (self.wind_gust_mph, "wind_gust_mph"),
            (self.wind_direction_deg, "wind_direction_deg"),
            (self.cloud_cover_pct, "cloud_cover_pct"),
            (self.pressure_hpa, "pressure_hpa"),
        ):
            _validate_optional_finite(numeric_value, label)

        for percentage_value, label in (
            (self.humidity_pct, "humidity_pct"),
            (self.precipitation_probability_pct, "precipitation_probability_pct"),
            (self.cloud_cover_pct, "cloud_cover_pct"),
        ):
            if percentage_value is not None and not 0.0 <= percentage_value <= 100.0:
                raise ValueError(f"{label} must be in [0, 100]")
        if self.wind_gust_mph is not None and self.wind_gust_mph < 0:
            raise ValueError("wind_gust_mph cannot be negative")
        if self.wind_gust_status not in {"not_supplied", "unsupported", "reported", "invalid"}:
            raise ValueError("invalid wind gust status")
        if self.wind_speed_mph is not None and self.wind_speed_mph < 0:
            raise ValueError("wind_speed_mph cannot be negative")
        if self.wind_direction_deg is not None and not 0.0 <= self.wind_direction_deg < 360.0:
            raise ValueError("wind_direction_deg must be in [0, 360)")
        if self.pressure_hpa is not None and self.pressure_hpa <= 0:
            raise ValueError("pressure_hpa must be positive when present")
        if self.short_forecast is not None and not self.short_forecast.strip():
            raise ValueError("short_forecast cannot be blank when present")

        metadata_keys = [key for key, _ in self.source_metadata]
        if any(not key.strip() or not value.strip() for key, value in self.source_metadata):
            raise ValueError("source_metadata keys and values must be nonblank")
        if len(metadata_keys) != len(set(metadata_keys)):
            raise ValueError("source_metadata keys must be unique")

    def metadata_value(self, key: str) -> str | None:
        """Return one provider-specific metadata value without exposing mutability."""

        return next(
            (value for metadata_key, value in self.source_metadata if metadata_key == key),
            None,
        )


@dataclass(frozen=True, slots=True)
class WeatherAcquisitionResult:
    forecast: ForecastSnapshot
    raw_payloads: tuple[ProviderPayload, ...]
    evidence: tuple[AcquisitionEvidence, ...] = ()
    warnings: tuple[str, ...] = ()
    history: AcquisitionHistory | None = None

    def require_window(self, target: datetime, maximum_seconds: float) -> None:
        if not math.isfinite(maximum_seconds) or maximum_seconds < 0:
            raise ValueError("forecast window must be finite and nonnegative")
        if (
            abs((as_utc(self.forecast.forecast_time) - as_utc(target)).total_seconds())
            > maximum_seconds
        ):
            error = WeatherProviderSchemaError("forecast outside requested selection window")
            error.raw_payloads = self.raw_payloads
            error.evidence = self.evidence
            raise error


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
    return parsed.astimezone(UTC)


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


def _metadata_pairs(**values: object) -> tuple[tuple[str, str], ...]:
    metadata: list[tuple[str, str]] = []
    for key, value in values.items():
        if isinstance(value, str) and value.strip():
            metadata.append((key, value))
    return tuple(metadata)


class NwsWeatherClient:
    def __init__(
        self, http: JsonHttpClient, user_agent: str, ledger: EvidenceLedger | None = None
    ) -> None:
        if not user_agent.strip():
            raise ValueError("NWS user_agent cannot be blank")
        self.http = http
        self.ledger = ledger
        self.headers = {"User-Agent": user_agent, "Accept": "application/geo+json"}

    def collect(
        self, latitude: float, longitude: float, target_time: datetime
    ) -> WeatherAcquisitionResult:
        require_aware(target_time, "target_time")
        with AcquisitionCapture(self.http, "nws", "weather", "ddc-nws-v2", self.ledger) as capture:
            point_result = capture.get_json(
                f"https://api.weather.gov/points/{latitude:.4f},{longitude:.4f}",
                headers=self.headers,
            )
            point = _object(point_result.payload, "NWS point response")
            point_properties = _object(point.get("properties"), "NWS point properties")
            forecast_url = validated_nws_hourly_url(point_properties.get("forecastHourly"))

            forecast_result = capture.get_json(forecast_url, headers=self.headers)
            forecast_observed_at = capture.payloads[-1].provenance.observed_at
            forecast = _object(forecast_result.payload, "NWS forecast response")
            properties = _object(forecast.get("properties"), "NWS forecast properties")
            raw_periods = _list(properties.get("periods"), "NWS periods")
            periods = [
                _object(item, "NWS period") for item in raw_periods if isinstance(item, dict)
            ]
            capture.diagnostic_codes = tuple(
                f"malformed_period:/properties/periods/{index}"
                for index, item in enumerate(raw_periods)
                if not isinstance(item, dict)
            )
            if not periods:
                raise WeatherProviderSchemaError("NWS hourly forecast contains no periods")

            target_utc = target_time.astimezone(UTC)
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
                wind_gust_status="unsupported",
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
                    CARDINAL_DEGREES.get(direction.strip().upper())
                    if isinstance(direction, str)
                    else None
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
                raw_payloads=tuple(capture.payloads),
                evidence=capture.finish(
                    "partial" if capture.diagnostic_codes else "complete",
                    capture.diagnostic_codes,
                    normalized_fingerprint(asdict(snapshot)),
                ),
                history=capture.history,
                warnings=capture.diagnostic_codes,
            )


class OpenWeatherClient:
    def __init__(self, http: JsonHttpClient, ledger: EvidenceLedger | None = None) -> None:
        self.http = http
        self.ledger = ledger

    def collect(
        self, latitude: float, longitude: float, target_time: datetime, api_key: str
    ) -> WeatherAcquisitionResult:
        require_aware(target_time, "target_time")
        if not api_key.strip():
            raise ValueError("OpenWeather api_key cannot be blank")
        if not math.isfinite(latitude) or not -90 <= latitude <= 90:
            raise ValueError("latitude outside supported range")
        if not math.isfinite(longitude) or not -180 <= longitude <= 180:
            raise ValueError("longitude outside supported range")
        with AcquisitionCapture(
            self.http, "openweather", "weather", "ddc-openweather-v2", self.ledger
        ) as capture:
            result = capture.get_json(
                "https://api.openweathermap.org/data/3.0/onecall",
                params={
                    "lat": str(latitude),
                    "lon": str(longitude),
                    "appid": api_key,
                    "units": "imperial",
                    "exclude": "minutely,daily,alerts",
                },
            )
            observed_at = capture.payloads[-1].provenance.observed_at
            root = _object(result.payload, "OpenWeather response")
            hourly = [
                _object(item, "OpenWeather hourly item")
                for item in _list(root.get("hourly"), "OpenWeather hourly")
            ]
            if not hourly:
                raise WeatherProviderSchemaError(
                    "OpenWeather response contains no hourly forecasts"
                )
            target_epoch = target_time.astimezone(UTC).timestamp()
            if any(_optional_float(item.get("dt")) is None for item in hourly):
                raise WeatherProviderSchemaError("OpenWeather hourly item missing or invalid dt")
            selected = min(
                hourly,
                key=lambda item: abs((_optional_float(item.get("dt")) or 0.0) - target_epoch),
            )
            epoch = _optional_float(selected.get("dt"))
            if epoch is None:
                raise WeatherProviderSchemaError("OpenWeather hourly item missing dt")
            pop = _optional_float(selected.get("pop"))
            if selected.get("pop") is not None and (pop is None or not 0 <= pop <= 1):
                raise WeatherProviderSchemaError("OpenWeather pop must be between zero and one")
            short_forecast = None
            weather_items = selected.get("weather")
            if weather_items is not None and not (
                isinstance(weather_items, list)
                and weather_items
                and isinstance(weather_items[0], dict)
            ):
                raise WeatherProviderSchemaError("OpenWeather weather details invalid")
            if isinstance(weather_items, list) and weather_items:
                first = weather_items[0]
                if isinstance(first, dict):
                    description = cast(dict[str, object], first).get("description")
                    short_forecast = description if isinstance(description, str) else None
            snapshot = ForecastSnapshot(
                provider_id="openweather",
                forecast_time=datetime.fromtimestamp(epoch, tz=UTC),
                observed_at=observed_at,
                available_at=observed_at,
                provider_updated_at=None,
                temperature_f=_optional_float(selected.get("temp")),
                humidity_pct=_optional_float(selected.get("humidity")),
                precipitation_probability_pct=pop * 100.0 if pop is not None else None,
                wind_speed_mph=_optional_float(selected.get("wind_speed")),
                wind_gust_mph=_optional_float(selected.get("wind_gust")),
                wind_gust_status=(
                    "not_supplied"
                    if selected.get("wind_gust") is None
                    else "reported"
                    if _optional_float(selected.get("wind_gust")) is not None
                    else "invalid"
                ),
                wind_direction_deg=_optional_float(selected.get("wind_deg")),
                short_forecast=short_forecast,
                cloud_cover_pct=_optional_float(selected.get("clouds")),
                pressure_hpa=_optional_float(selected.get("pressure")),
            )
            return WeatherAcquisitionResult(
                forecast=snapshot,
                raw_payloads=tuple(capture.payloads),
                evidence=capture.finish(
                    "complete", normalized_digest=normalized_fingerprint(asdict(snapshot))
                ),
                history=capture.history,
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
