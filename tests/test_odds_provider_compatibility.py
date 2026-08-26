from __future__ import annotations

import json

import pytest

from daily_data_core.http import HttpRequestDiagnostics, JsonHttpResult
from daily_data_core.odds import OddsProviderSchemaError, TheOddsApiClient


class SingleResultHttp:
    def __init__(self, result: JsonHttpResult) -> None:
        self.result = result
        self.calls: list[tuple[str, dict[str, str] | None, dict[str, str] | None]] = []

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> JsonHttpResult:
        self.calls.append((url, params, headers))
        return self.result


def _result(payload: object, *, raw: bytes | None = None) -> JsonHttpResult:
    content = raw if raw is not None else json.dumps(payload, separators=(",", ":")).encode()
    assert isinstance(payload, (dict, list))
    return JsonHttpResult(
        payload=payload,
        content=content,
        content_type="application/json",
        response_url="https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/",
        diagnostics=HttpRequestDiagnostics(
            request_status="success",
            status_code=200,
            attempts=1,
            retries_performed=0,
            duration_seconds=0.01,
            response_date_utc="2026-08-26T18:00:00+00:00",
            quota_headers={
                "requests_remaining": "498",
                "requests_used": "2",
                "requests_last": "1",
            },
        ),
    )


def _valid_event() -> dict[str, object]:
    return {
        "id": "event-1",
        "sport_key": "baseball_mlb",
        "commence_time": "2026-08-26T20:10:00Z",
        "home_team": "Los Angeles Dodgers",
        "away_team": "San Francisco Giants",
        "bookmakers": [
            {
                "key": "book-a",
                "title": "Book A",
                "last_update": "2026-08-26T20:00:00Z",
                "markets": [
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": -110, "point": 8.5},
                            {"name": "Under", "price": -105, "point": 8.5},
                        ],
                    }
                ],
            }
        ],
    }


def test_empty_list_is_valid_empty_slate_and_preserves_raw_bytes() -> None:
    raw = b"[ ]\n"
    http = SingleResultHttp(_result([], raw=raw))
    client = TheOddsApiClient(http)  # type: ignore[arg-type]

    result = client.collect(sport_key="baseball_mlb", api_key="test-key")

    assert result.events == ()
    assert result.warnings == ()
    assert result.raw_payload.content == raw
    assert result.quota["requests_remaining"] == "498"


def test_malformed_nested_elements_are_excluded_with_granular_warnings() -> None:
    event = _valid_event()
    bookmakers = event["bookmakers"]
    assert isinstance(bookmakers, list)
    valid_book = bookmakers[0]
    assert isinstance(valid_book, dict)
    markets = valid_book["markets"]
    assert isinstance(markets, list)
    totals = markets[0]
    assert isinstance(totals, dict)
    outcomes = totals["outcomes"]
    assert isinstance(outcomes, list)

    outcomes.append({"name": "Over", "price": "bad", "point": 9.0})
    markets.append({"key": "broken-market", "outcomes": "not-a-list"})
    bookmakers.append({"key": "broken-book", "title": "Broken", "markets": "not-a-list"})

    raw = json.dumps([event], separators=(",", ":")).encode()
    http = SingleResultHttp(_result([event], raw=raw))
    client = TheOddsApiClient(http)  # type: ignore[arg-type]

    result = client.collect(sport_key="baseball_mlb", api_key="test-key")

    assert len(result.events) == 1
    parsed = result.events[0]
    assert len(parsed.bookmakers) == 1
    assert len(parsed.bookmakers[0].markets) == 1
    assert len(parsed.bookmakers[0].markets[0].outcomes) == 2
    assert [warning.code for warning in result.warnings] == [
        "malformed_outcome",
        "malformed_market",
        "malformed_bookmaker",
    ]
    assert result.raw_payload.content == raw


def test_malformed_event_is_skipped_when_another_event_is_valid() -> None:
    payload: list[object] = [{"id": "broken"}, _valid_event()]
    client = TheOddsApiClient(SingleResultHttp(_result(payload)))  # type: ignore[arg-type]

    result = client.collect(sport_key="baseball_mlb", api_key="test-key")

    assert len(result.events) == 1
    assert [warning.code for warning in result.warnings] == ["malformed_event"]


def test_nonempty_all_invalid_payload_is_fatal() -> None:
    payload: list[object] = [{"id": "broken"}, "not-an-event"]
    client = TheOddsApiClient(SingleResultHttp(_result(payload)))  # type: ignore[arg-type]

    with pytest.raises(OddsProviderSchemaError, match="no structurally valid events"):
        client.collect(sport_key="baseball_mlb", api_key="test-key")


def test_request_contract_is_sport_configurable_and_american() -> None:
    http = SingleResultHttp(_result([]))
    client = TheOddsApiClient(http)  # type: ignore[arg-type]

    client.collect(
        sport_key="americanfootball_ncaaf",
        api_key="test-key",
        regions=("us", "us2"),
        markets=("h2h", "spreads", "totals"),
    )

    url, params, headers = http.calls[0]
    assert url.endswith("/americanfootball_ncaaf/odds/")
    assert headers is None
    assert params == {
        "apiKey": "test-key",
        "regions": "us,us2",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
        "dateFormat": "iso",
    }
