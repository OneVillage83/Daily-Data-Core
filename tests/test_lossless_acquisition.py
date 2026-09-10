from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest
import requests

from daily_data_core.acquisition import (
    AcquisitionCapture,
    AcquisitionEvidence,
    EvidenceLedger,
    ProviderAcquisitionError,
    ReplayHttpClient,
)
from daily_data_core.http import HttpClient, HttpError, redact_url
from daily_data_core.odds import OddsProviderSchemaError, TheOddsApiClient
from daily_data_core.provenance import FileSystemRawEvidenceStore, RawEvidenceCollisionError
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance
from daily_data_core.weather import ForecastSnapshot, OpenWeatherClient, WeatherProviderSchemaError

NOW = datetime(2026, 7, 30, 14, tzinfo=UTC)


def payload(value: object, *, raw: bytes | None = None) -> ProviderPayload:
    return ProviderPayload(
        json.dumps(value).encode() if raw is None else raw,
        "application/json",
        "https://example.invalid/odds?apiKey=synthetic-secret&regions=us",
        TemporalProvenance(NOW, NOW, published_at=NOW - timedelta(minutes=1)),
    )


def event(markets: list[object]) -> dict[str, object]:
    return {
        "id": "synthetic",
        "sport_key": "baseball_mlb",
        "home_team": "Home",
        "away_team": "Away",
        "commence_time": "2026-07-30T20:00:00Z",
        "bookmakers": [{"key": "book", "title": "Book", "markets": markets}],
    }


def test_partial_siblings_duplicates_and_source_paths_survive() -> None:
    markets: list[object] = [
        {
            "key": "h2h",
            "outcomes": [{"name": "Home", "price": -110}, {"name": "Away", "price": "invalid"}],
        },
        {"key": "broken", "outcomes": None},
        {"key": "provider_future_family", "last_update": "invalid", "outcomes": []},
        {"key": "h2h", "outcomes": [{"name": "Home", "price": -115}]},
    ]
    result = TheOddsApiClient(ReplayHttpClient((payload([event(markets)]),))).collect(
        sport_key="baseball_mlb", api_key="synthetic"
    )
    actual = result.events[0].bookmakers[0].markets
    assert [m.key for m in actual] == ["h2h", "provider_future_family", "h2h"]
    assert [m.source_path for m in actual] == [
        "/0/bookmakers/0/markets/0",
        "/0/bookmakers/0/markets/2",
        "/0/bookmakers/0/markets/3",
    ]
    assert actual[0].outcomes[0].price == -110
    assert actual[1].outcomes == ()
    assert actual[2].outcomes[0].price == -115
    assert result.partial and result.evidence[0].disposition == "partial"
    assert {w.code for w in result.warnings} == {
        "malformed_outcome",
        "malformed_market",
        "invalid_optional_timestamp",
    }
    assert result.events[0].observed_at == NOW
    assert result.raw_payload.provenance.published_at == NOW - timedelta(minutes=1)


@pytest.mark.parametrize("value", [{}, [{"malformed": True}], [event([{"key": "x"}]), None]])
def test_schema_failure_or_partial_has_durable_raw_and_diagnostics(
    tmp_path: Path,
    value: object,
) -> None:
    source = payload(value)
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True)
    client = TheOddsApiClient(ReplayHttpClient((source,)), ledger)
    try:
        result = client.collect(sport_key="baseball_mlb", api_key="synthetic")
        evidence = result.evidence
        assert result.partial
    except OddsProviderSchemaError as exc:
        assert exc.raw_payload is not None
        assert exc.raw_payload.content == source.content
        evidence = exc.evidence
        assert evidence[0].disposition == "schema_error"
    assert len(evidence) == 1
    restored = ledger.read(evidence[0].receipt_id)
    assert restored == evidence[0]
    assert restored.payload.content == source.content
    assert restored.payload.provenance == source.provenance
    assert "synthetic-secret" not in json.dumps(restored.document())
    assert restored.previous_receipt_id is not None
    assert ledger.read(restored.previous_receipt_id).disposition == "received"


@pytest.mark.parametrize("raw", [b"not-json\n", b"", b"null", b"\xff"])
def test_failed_json_replay_retains_exact_bytes(tmp_path: Path, raw: bytes) -> None:
    source = payload(None, raw=raw)
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True)
    with pytest.raises(HttpError) as error:
        TheOddsApiClient(ReplayHttpClient((source,)), ledger).collect(
            sport_key="baseball_mlb", api_key="synthetic"
        )
    assert error.value.raw_payload is not None
    assert error.value.raw_payload.content == raw
    assert raw not in str(error.value).encode() if raw else True
    receipts = list((tmp_path / "ddc_receipts" / "acquisition_v2").glob("*.raw"))
    assert len(receipts) == 2
    for receipt in receipts:
        restored = ledger.read(receipt.stem)
        assert restored.payload.content == raw


def test_retention_denial_writes_nothing(tmp_path: Path) -> None:
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: False)
    with pytest.raises(OddsProviderSchemaError):
        TheOddsApiClient(ReplayHttpClient((payload({}),)), ledger).collect(
            sport_key="baseball_mlb", api_key="synthetic"
        )
    assert list(tmp_path.iterdir()) == []


def test_unexpected_normalization_exception_is_evidence_backed(tmp_path: Path) -> None:
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True)
    with pytest.raises(ProviderAcquisitionError) as error:
        with AcquisitionCapture(
            ReplayHttpClient((payload({}),)), "synthetic", "facts", "v2", ledger
        ) as capture:
            capture.get_json("https://example.invalid")
            raise ValueError("provider-controlled-secret")
    assert error.value.raw_payload is not None
    assert "provider-controlled-secret" not in str(error.value)
    assert ledger.read(error.value.evidence[0].receipt_id).disposition == "schema_error"


def test_new_parser_receipt_does_not_rewrite_history_or_availability(tmp_path: Path) -> None:
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True)
    original = AcquisitionEvidence("synthetic", "facts", "v1", payload({}), "schema_error", NOW)
    old_id = ledger.put(original)
    assert old_id is not None
    revised = replace(
        original,
        parser_version="v2",
        disposition="complete",
        evaluated_at=NOW + timedelta(days=1),
        previous_receipt_id=old_id,
    )
    new_id = ledger.put(revised)
    assert new_id is not None and new_id != old_id
    assert ledger.read(old_id) == original
    assert ledger.read(new_id).payload.provenance.available_at == NOW
    assert revised.response_id == original.response_id
    assert revised.observation_id("/0") == original.observation_id("/0")
    assert original.observation_id("/0") != original.observation_id("/1")
    with pytest.raises(ValueError, match="precede retrieval"):
        replace(revised, evaluated_at=NOW - timedelta(seconds=1))
    raw = next((tmp_path / "synthetic" / "facts").glob("*.raw"))
    raw.write_bytes(b"tampered")
    with pytest.raises(RawEvidenceCollisionError):
        ledger.read(old_id)


@pytest.mark.parametrize(
    "gust,status", [(17, "reported"), (0, "reported"), (None, "not_supplied"), ("bad", "invalid")]
)
def test_wind_gust_round_trip(gust: object, status: str) -> None:
    source = payload({"hourly": [{"dt": NOW.timestamp(), "wind_speed": 8, "wind_gust": gust}]})
    result = OpenWeatherClient(ReplayHttpClient((source,))).collect(1, 2, NOW, "synthetic")
    assert result.forecast.wind_gust_mph == (gust if isinstance(gust, int) else None)
    assert result.forecast.wind_speed_mph == 8
    assert result.forecast.wind_gust_status == status
    assert ForecastSnapshot.from_json(result.forecast.to_json()) == result.forecast
    assert result.raw_payloads[0].provenance == source.provenance


def test_weather_schema_error_keeps_evidence() -> None:
    source = payload({"hourly": []})
    with pytest.raises(WeatherProviderSchemaError) as error:
        OpenWeatherClient(ReplayHttpClient((source,))).collect(1, 2, NOW, "synthetic")
    assert error.value.raw_payload is not None
    assert error.value.raw_payload.content == source.content


class Session:
    def __init__(self, responses: list[requests.Response | Exception]) -> None:
        self.responses = iter(responses)

    def get(self, *args: object, **kwargs: object) -> requests.Response:
        item = next(self.responses)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.mark.parametrize("status,body", [(200, b"not-json"), (401, b"error"), (200, b"")])
def test_http_captures_before_json_and_errors(status: int, body: bytes) -> None:
    response = requests.Response()
    response.status_code = status
    response._content = body
    response.url = "https://user:secret@example.invalid/?appid=secret#secret"
    client = HttpClient(max_attempts=1)
    client.session = cast(requests.Session, Session([response]))
    with pytest.raises(HttpError) as error:
        client.get_json("https://example.invalid")
    assert error.value.raw_payload is not None
    assert error.value.raw_payload.content == body
    assert error.value.raw_payload.response_status_code == status
    assert "secret" not in (error.value.raw_payload.source_uri or "")


def test_transport_failure_has_no_response_evidence() -> None:
    client = HttpClient(max_attempts=1)
    client.session = cast(requests.Session, Session([requests.ConnectionError("secret")]))
    with pytest.raises(HttpError) as error:
        client.get_json("https://example.invalid")
    assert error.value.raw_payload is None and error.value.raw_payloads == ()
    assert "secret" not in str(error.value)


def test_redaction_retains_nonsecret_query_dimensions() -> None:
    assert "markets=totals" in redact_url("https://example.invalid?markets=totals&appid=secret")
    assert "secret" not in redact_url("https://user:secret@example.invalid?appid=secret#secret")


def test_empty_book_and_empty_market_remain_distinct() -> None:
    result = TheOddsApiClient(
        ReplayHttpClient(
            (
                payload(
                    [
                        event([]),
                        event([{"key": "h2h", "outcomes": []}]),
                    ]
                ),
            )
        )
    ).collect(sport_key="baseball_mlb", api_key="synthetic")
    assert result.events[0].bookmakers[0].markets == ()
    assert result.events[1].bookmakers[0].markets[0].outcomes == ()
    assert not result.partial


def test_retries_retain_prior_responses_on_eventual_transport_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("daily_data_core.http.time.sleep", lambda _: None)
    response = requests.Response()
    response.status_code = 503
    response._content = b"temporary unavailable"
    client = HttpClient(max_attempts=2)
    client.session = cast(requests.Session, Session([response, requests.ConnectionError()]))
    with pytest.raises(HttpError) as error:
        client.get_json("https://example.invalid")
    assert error.value.failure_kind == "transport_error"
    assert error.value.raw_payload is not None
    assert error.value.raw_payload.content == b"temporary unavailable"
    assert error.value.raw_payload.response_status_code == 503


def test_nws_second_response_failure_retains_both_responses(tmp_path: Path) -> None:
    from daily_data_core.weather import NwsWeatherClient

    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True)
    point = payload(
        {
            "properties": {
                "forecastHourly": "https://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly"
            }
        }
    )
    forecast = payload({"properties": {"periods": []}})
    with pytest.raises(WeatherProviderSchemaError) as error:
        NwsWeatherClient(ReplayHttpClient((point, forecast)), "synthetic", ledger).collect(
            1, 2, NOW
        )
    assert len(error.value.raw_payloads) == 2
    assert [e.payload.content for e in error.value.evidence] == [point.content, forecast.content]
    assert all(ledger.read(e.receipt_id) == e for e in error.value.evidence)


def test_http_status_failure_replay_does_not_promote_error_body() -> None:
    source = replace(payload([]), response_status_code=401)
    with pytest.raises(HttpError) as error:
        TheOddsApiClient(ReplayHttpClient((source,))).collect(
            sport_key="baseball_mlb", api_key="synthetic"
        )
    assert error.value.failure_kind == "http_status_error"
