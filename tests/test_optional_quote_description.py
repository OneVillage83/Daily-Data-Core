from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from daily_data_core.acquisition import EvidenceLedger, ReplayHttpClient
from daily_data_core.odds import OddsOutcomeSnapshot, TheOddsApiClient
from daily_data_core.provenance import FileSystemRawEvidenceStore
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance

NOW = datetime(2026, 7, 30, 14, tzinfo=UTC)


def payload(value: object) -> ProviderPayload:
    return ProviderPayload(
        json.dumps(value).encode(), "application/json", "https://example.invalid/odds",
        TemporalProvenance(NOW, NOW, published_at=NOW - timedelta(minutes=1)),
    )


def event(markets: list[object]) -> dict[str, object]:
    return {
        "id": "synthetic", "sport_key": "baseball_mlb", "home_team": "Home",
        "away_team": "Away", "commence_time": "2026-07-30T20:00:00Z",
        "bookmakers": [{"key": "book", "title": "Book", "markets": markets}],
    }


@pytest.mark.parametrize("description", [None, "", "Participant", " Participant "])
def test_normalized_constructor_canonical_optional_description(description: str | None) -> None:
    quote = OddsOutcomeSnapshot("Home", -120, participant_description=description)
    assert quote.participant_description == (None if description == "" else description)


@pytest.mark.parametrize("description", [" ", "\t\n", 1, False, [], {}])
def test_normalized_constructor_rejects_malformed_description(description: object) -> None:
    with pytest.raises(ValueError, match="description"):
        OddsOutcomeSnapshot("Home", -120, participant_description=description)  # type: ignore[arg-type]


@pytest.mark.parametrize("fields,expected", [
    ({}, None), ({"description": None}, None), ({"description": ""}, None),
    ({"description": "Participant"}, "Participant"),
    ({"description": " Participant "}, " Participant "),
])
def test_optional_description_retains_quote_siblings_raw_identity_and_pit(
    tmp_path: Path, fields: dict[str, object], expected: str | None,
) -> None:
    first = {"name": "Home", "price": -120, **fields}
    source_value = [event([
        {"key": "h2h", "outcomes": [first, {"name": "Away", "price": 110},
                                    {"name": "Invalid", "price": "bad"}]},
        {"key": "totals", "outcomes": "malformed"},
    ])]
    before = deepcopy(source_value)
    source = payload(source_value)
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: True)
    result = TheOddsApiClient(ReplayHttpClient((source,)), ledger).collect(
        sport_key="baseball_mlb", api_key="synthetic",
    )
    quotes = result.events[0].bookmakers[0].markets[0].outcomes
    assert [(q.name, q.price) for q in quotes] == [("Home", -120), ("Away", 110)]
    assert quotes[0].participant_description == expected
    assert quotes[0].source_path == "/0/bookmakers/0/markets/0/outcomes/0"
    assert [w.code for w in result.warnings] == ["malformed_outcome", "malformed_market"]
    assert source_value == before
    assert result.raw_payload.content == source.content
    assert result.raw_payload.provenance == source.provenance
    assert result.events[0].observed_at == result.events[0].available_at == NOW
    assert not result.raw_payload.provenance.eligible_at(NOW - timedelta(microseconds=1))
    assert result.raw_payload.provenance.eligible_at(NOW)
    retained = ledger.read(result.evidence[0].receipt_id)
    assert retained.response_id == result.evidence[0].response_id
    assert retained.observation_id(quotes[0].source_path) == result.evidence[0].observation_id(
        quotes[0].source_path
    )
    replay = TheOddsApiClient(ReplayHttpClient((retained.payload,))).collect(
        sport_key="baseball_mlb", api_key="synthetic",
    )
    assert [asdict(e) for e in replay.events] == [asdict(e) for e in result.events]


@pytest.mark.parametrize("invalid", [
    {"name": ""}, {"name": None}, {"price": "-120"}, {"price": True},
    {"price": float("inf")}, {"point": "1.5"}, {"point": False},
    {"description": " "}, {"description": 123},
])
def test_invalid_fields_still_reject_only_their_quote(invalid: dict[str, object]) -> None:
    result = TheOddsApiClient(ReplayHttpClient((payload([event([
        {"key": "h2h", "outcomes": [
            {"name": "Home", "price": -120, "description": "", **invalid},
            {"name": "Away", "price": 110},
        ]},
    ])]),))).collect(sport_key="baseball_mlb", api_key="synthetic")
    assert [q.name for q in result.events[0].bookmakers[0].markets[0].outcomes] == ["Away"]
    assert [w.code for w in result.warnings] == ["malformed_outcome"]
