from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
import requests

from daily_data_core.acquisition import (
    AcquisitionCapture,
    AcquisitionReplayClient,
    EvidenceLedger,
    normalized_fingerprint,
)
from daily_data_core.history import ReplayMismatchError, SchemaValidationError
from daily_data_core.http import HttpClient, HttpError
from daily_data_core.odds import OddsProviderSchemaError, TheOddsApiClient
from daily_data_core.provenance import FileSystemRawEvidenceStore, RawEvidenceCollisionError
from daily_data_core.weather import NwsWeatherClient


class SequenceSession(requests.Session):
    def __init__(self, values: list[tuple[int, bytes] | Exception]) -> None:
        super().__init__()
        self.values = iter(values)
        self.count = 0

    def get(self, url: Any, **kwargs: Any) -> requests.Response:
        self.count += 1
        value = next(self.values)
        if isinstance(value, Exception):
            raise value
        status, content = value
        response = requests.Response()
        response.url = str(url)
        response.status_code = status
        response._content = content
        response.headers.update(
            {
                "Content-Type": "application/json",
                "Retry-After": "0",
                "x-requests-remaining": "9",
                "x-requests-used": "1",
            }
        )
        return response


def client(values: list[tuple[int, bytes] | Exception], **kwargs: Any) -> HttpClient:
    http = HttpClient(max_attempts=len(values), **kwargs)
    http.session = SequenceSession(values)
    return http


def ledger_at(path: Path) -> EvidenceLedger:
    return EvidenceLedger(FileSystemRawEvidenceStore(path), lambda _: True, lambda _: True)


def collect(http: Any, ledger: EvidenceLedger | None = None) -> Any:
    return TheOddsApiClient(http, ledger).collect(sport_key="baseball_mlb", api_key="synthetic")


def test_retry_success_persists_replays_and_never_uses_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ledger = ledger_at(tmp_path)
    original = collect(client([(503, b"temporary"), (200, b"[]")]), ledger)
    assert original.history is not None
    restored = ledger_at(tmp_path).read_history(original.history.receipt_id)
    assert restored == original.history
    call = restored.calls[0]
    assert [a.outcome for a in call.attempts] == ["http_status_error", "success"]
    assert [a.ordinal for a in call.attempts] == [1, 2]
    assert call.attempts[0].attempt_id != call.attempts[1].attempt_id
    assert call.attempts[0].will_retry and not call.attempts[1].will_retry
    network: list[bool] = []

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        network.append(True)
        raise AssertionError("strict replay invoked network")

    monkeypatch.setattr(requests.Session, "request", forbidden)
    monkeypatch.setattr("daily_data_core.http.time.sleep", forbidden)
    replay = AcquisitionReplayClient(restored)
    before = set(tmp_path.rglob("*.raw"))
    repeated = collect(replay, ledger)
    assert replay.network_calls == 0 and network == []
    assert repeated.history == original.history
    assert repeated.evidence == original.evidence
    assert repeated.diagnostics == original.diagnostics
    assert repeated.raw_payload == original.raw_payload
    assert before == set(tmp_path.rglob("*.raw"))


def test_schema_error_preserves_attempt_quota_and_replays(tmp_path: Path) -> None:
    ledger = ledger_at(tmp_path)
    with pytest.raises(OddsProviderSchemaError) as caught:
        collect(client([(503, b"temporary"), (200, b"[{}]")]), ledger)
    original = caught.value
    assert original.diagnostics is not None and original.diagnostics.attempts == 2
    assert original.quota["requests_remaining"] == "9"
    assert original.history is not None
    restored = ledger_at(tmp_path).read_history(original.history.receipt_id)
    assert restored.disposition == "schema_error"
    assert restored.document()["request_diagnostics"]
    with pytest.raises(OddsProviderSchemaError) as replayed:
        collect(AcquisitionReplayClient(restored))
    assert replayed.value.history == original.history
    assert replayed.value.diagnostics == original.diagnostics
    assert replayed.value.quota == original.quota


@pytest.mark.parametrize(
    "exception",
    [
        requests.Timeout("secret"),
        requests.ConnectionError("secret"),
        requests.RequestException("secret"),
    ],
)
def test_no_response_attempt_has_no_invented_body(tmp_path: Path, exception: Exception) -> None:
    ledger = ledger_at(tmp_path)
    with pytest.raises(HttpError) as caught:
        collect(client([exception]), ledger)
    error = caught.value
    assert error.raw_payloads == () and error.history is not None
    restored = ledger_at(tmp_path).read_history(error.history.receipt_id)
    assert restored.calls[0].attempts[0].payload is None
    assert restored.calls[0].attempts[0].outcome == "transport_error"
    assert dict(restored.calls[0].attempts[0].quota) == {}
    assert "secret" not in json.dumps(restored.calls[0].document())
    with pytest.raises(type(error)) as repeated:
        collect(AcquisitionReplayClient(restored))
    assert repeated.value.history == error.history
    assert repeated.value.diagnostics == error.diagnostics


@pytest.mark.parametrize(
    "status,body,kind",
    [
        (401, b"denied", "http_status_error"),
        (200, b"not-json", "json_error"),
        (200, b"null", "json_error"),
    ],
)
def test_terminal_errors_replay_same_classification(
    tmp_path: Path, status: int, body: bytes, kind: str
) -> None:
    with pytest.raises(HttpError) as caught:
        collect(client([(status, body)]), ledger_at(tmp_path))
    original = caught.value
    assert original.history is not None and original.failure_kind == kind
    restored = ledger_at(tmp_path).read_history(original.history.receipt_id)
    with pytest.raises(type(original)) as repeated:
        collect(AcquisitionReplayClient(restored))
    assert repeated.value.failure_kind == original.failure_kind
    assert repeated.value.raw_payloads == original.raw_payloads


def test_timeout_then_success_counts_physical_not_invented_quota(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("daily_data_core.http.time.sleep", lambda _: None)
    result = collect(client([requests.Timeout(), (200, b"[]")]), ledger_at(tmp_path))
    first, last = result.history.calls[0].attempts
    assert first.payload is None and dict(first.quota) == {}
    assert dict(last.quota)["requests_used"] == "1"
    assert result.diagnostics.attempts == 2
    assert collect(AcquisitionReplayClient(result.history)).history == result.history


def test_explicit_schema_retry_retains_rejected_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("daily_data_core.http.time.sleep", lambda _: None)

    def validator(value: object) -> None:
        if value != []:
            raise SchemaValidationError("secret provider detail")

    http = client(
        [(200, b"[{}]"), (200, b"[]")],
        schema_validator=validator,
        validator_version="fixture-schema-v1",
        retry_schema_errors=True,
    )
    result = collect(http, ledger_at(tmp_path))
    assert [a.outcome for a in result.history.calls[0].attempts] == ["schema_error", "success"]
    assert "secret provider detail" not in json.dumps(result.history.calls[0].document())
    restored = ledger_at(tmp_path).read_history(result.history.receipt_id)
    replay = AcquisitionReplayClient(restored, validator_versions=frozenset({"fixture-schema-v1"}))
    assert collect(replay).history == restored
    with pytest.raises(ReplayMismatchError, match="validator"):
        AcquisitionReplayClient(restored)


def test_schema_retry_default_remains_disabled(tmp_path: Path) -> None:
    http = client([(200, b"not-json"), (200, b"[]")])
    with pytest.raises(HttpError) as error:
        collect(http, ledger_at(tmp_path))
    assert error.value.diagnostics is not None and error.value.diagnostics.attempts == 1


def test_idempotent_writes_distinct_requests_and_conflicting_rewrite(tmp_path: Path) -> None:
    ledger = ledger_at(tmp_path)
    first = collect(client([(503, b"same"), (200, b"[]")]), ledger).history
    receipt = ledger.put_history(first)
    files = set(tmp_path.rglob("*.raw"))
    assert ledger.put_history(first) == receipt
    assert set(tmp_path.rglob("*.raw")) == files
    second = collect(client([(200, b"[]")]), ledger).history
    assert second.acquisition_id != first.acquisition_id
    assert second.calls[0].call_id != first.calls[0].call_id
    with pytest.raises(RawEvidenceCollisionError):
        ledger.put_call(replace(first.calls[0], duration_seconds=1234), first.parser_version)


def test_reprocess_links_original_without_backdating(tmp_path: Path) -> None:
    ledger = ledger_at(tmp_path)
    original = collect(client([(200, b"[]")]), ledger).history
    different_parser = replace(original, parser_version="older-parser")
    with pytest.raises(ReplayMismatchError, match="parser"):
        collect(AcquisitionReplayClient(different_parser))
    replay = AcquisitionReplayClient(original, mode="reprocess")
    result = collect(replay, ledger)
    assert result.history.previous_history_id == original.receipt_id
    assert result.history.calls == original.calls
    assert result.raw_payload.provenance == original.evidence[-1].payload.provenance
    assert result.history.acquisition_id != original.acquisition_id


def test_strict_replay_refuses_code_or_scope_changes(tmp_path: Path) -> None:
    original = collect(client([(200, b"[]")]), ledger_at(tmp_path)).history
    with pytest.raises(ReplayMismatchError, match="code identity"):
        AcquisitionReplayClient(replace(original, source_code_identity="invalid"))
    replay = AcquisitionReplayClient(original)
    with pytest.raises(ReplayMismatchError, match="scope"):
        replay.get_json("https://example.invalid/different")
    with pytest.raises(ReplayMismatchError, match="interpretation"):
        modified = replace(original, normalized_digest="0" * 64)
        collect(AcquisitionReplayClient(modified))


def test_response_only_evidence_not_promoted_to_complete_history() -> None:
    with pytest.raises(ReplayMismatchError, match="complete v3"):
        AcquisitionReplayClient(())  # type: ignore[arg-type]


def test_nws_two_logical_calls_keep_independent_retry_groups(tmp_path: Path) -> None:
    target = datetime(2026, 7, 30, 14, tzinfo=UTC)
    point = {
        "properties": {
            "forecastHourly": "https://api.weather.gov/gridpoints/MTR/1,2/forecast/hourly"
        }
    }
    forecast = {
        "properties": {"periods": [{"startTime": target.isoformat(), "temperatureUnit": "F"}]}
    }
    http = client(
        [
            (503, b"temporary"),
            (200, json.dumps(point).encode()),
            (200, json.dumps(forecast).encode()),
        ]
    )
    result = NwsWeatherClient(http, "fixture", ledger_at(tmp_path)).collect(1, 2, target)
    assert result.history is not None
    assert [len(c.attempts) for c in result.history.calls] == [2, 1]
    restored = ledger_at(tmp_path).read_history(result.history.receipt_id)
    repeated = NwsWeatherClient(AcquisitionReplayClient(restored), "fixture").collect(1, 2, target)
    assert repeated.history == result.history and repeated.forecast == result.forecast


def test_raw_receipt_exists_before_validator_and_clock_integrity(tmp_path: Path) -> None:
    ledger = ledger_at(tmp_path)

    def validator(_: object) -> None:
        assert list((tmp_path / "the_odds_api" / "odds").glob("*.raw"))
        raise SchemaValidationError("invalid")

    with pytest.raises(HttpError) as error:
        collect(
            client([(200, b"{}")], schema_validator=validator, validator_version="fixture"), ledger
        )
    assert error.value.history is not None
    attempt = error.value.history.calls[0].attempts[0]
    assert attempt.payload is not None
    assert attempt.payload.provenance.available_at <= attempt.completed_at
    with pytest.raises(ValueError):
        replace(attempt, completed_at=attempt.started_at - timedelta(seconds=1))


def test_explicit_history_retention_denial(tmp_path: Path) -> None:
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: False, lambda _: False)
    result = collect(client([(200, b"[]")]), ledger)
    assert result.history is not None
    assert list(tmp_path.rglob("*.raw")) == []


def test_generic_capture_not_tied_to_odds_provider(tmp_path: Path) -> None:
    with AcquisitionCapture(
        client([(200, b'{"value":1}')]), "neutral", "facts", "v1", ledger_at(tmp_path)
    ) as capture:
        result = capture.get_json(
            "https://example.invalid/facts",
            params={"apiKey": "sensitive"},
            headers={"Authorization": "sensitive", "Cookie": "sensitive"},
        )
        capture.finish("complete", normalized_digest=normalized_fingerprint(result.payload))
    assert capture.history is not None
    text = json.dumps(capture.history.calls[0].document())
    assert "sensitive" not in text and "Authorization" not in text and "Cookie" not in text
    stored = ledger_at(tmp_path).read_history(capture.history.receipt_id)
    assert stored == capture.history
