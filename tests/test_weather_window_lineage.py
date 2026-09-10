from __future__ import annotations

import io
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import requests

from daily_data_core.acquisition import AcquisitionReplayClient, EvidenceLedger
from daily_data_core.http import HttpClient
from daily_data_core.provenance import FileSystemRawEvidenceStore
from daily_data_core.weather import OpenWeatherClient, WeatherWindowRejected


@pytest.mark.parametrize("offset", [-7200, 0, 7200])
def test_window_retains_verified_evidence_and_replays(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    offset: int,
) -> None:
    target = datetime(2026, 7, 30, 16, tzinfo=UTC)
    body = json.dumps(
        {"hourly": [{"dt": (target + timedelta(seconds=offset)).timestamp(), "wind_gust": 0}]}
    ).encode()

    def response(*args: Any, **kwargs: Any) -> requests.Response:
        result = requests.Response()
        result.status_code = 200
        result.url = "https://api.openweathermap.org/data/3.0/onecall"
        result._content = body
        result.raw = io.BytesIO(body)
        result.headers["Content-Type"] = "application/json"
        return result

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", response)
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True, lambda _: True)
    original = OpenWeatherClient(HttpClient(), ledger).collect(1, 2, target, "synthetic")
    assert original.history is not None
    envelope = original.verified_evidence_document(ledger)
    decision = original.evaluate_window(target, 3600)
    assert (
        decision.reason
        == ({-7200: "forecast_before_window", 0: "accepted", 7200: "forecast_after_window"}[offset])
    )
    if offset:
        with pytest.raises(WeatherWindowRejected) as raised:
            original.require_window(target, 3600)
        assert raised.value.history == original.history
        assert raised.value.diagnostics == original.diagnostics
        assert raised.value.evaluation == decision
        assert raised.value.raw_payloads == original.raw_payloads
    else:
        original.require_window(target, 3600)
    assert original.history.disposition == "complete"

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("replay called provider")

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", forbidden)
    restored = ledger.read_history(original.history.receipt_id)
    replay = OpenWeatherClient(AcquisitionReplayClient(restored), ledger).collect(
        1, 2, target, "synthetic"
    )
    assert replay.verified_evidence_document(ledger) == envelope
    assert replay.evaluate_window(target, 3600) == decision
    assert json.loads(json.dumps(envelope)) == envelope
    assert replay.forecast.wind_gust_mph == 0
    changed = replace(original, forecast=replace(original.forecast, temperature_f=42))
    with pytest.raises(ValueError, match="mismatch"):
        changed.verified_evidence_document(ledger)


@pytest.mark.parametrize("limit", [-1, float("inf"), float("nan")])
def test_invalid_window(limit: float) -> None:
    from daily_data_core.weather import ForecastSnapshot, WeatherAcquisitionResult

    now = datetime.now(UTC)
    result = WeatherAcquisitionResult(
        ForecastSnapshot(
            "nws",
            now,
            now,
            now,
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (),
    )
    with pytest.raises(ValueError):
        result.require_window(now, limit)
