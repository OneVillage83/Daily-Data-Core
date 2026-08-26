"""Shared The Odds API adapter and normalized sportsbook snapshots."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast

from daily_data_core.http import HttpClient, HttpRequestDiagnostics
from daily_data_core.markets import TwoWayOffer
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance, require_aware

THE_ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"
PROVIDER_ID = "the_odds_api"
PARSER_VERSION = "ddc-the-odds-api-v1"

# Provider keys verified against The Odds API V4 sports catalogue.
SPORT_KEYS: dict[str, str] = {
    "MLB": "baseball_mlb",
    "NFL": "americanfootball_nfl",
    "NCAAF": "americanfootball_ncaaf",
    "NBA": "basketball_nba",
    "NCAAB": "basketball_ncaab",
    "WNBA": "basketball_wnba",
    "NHL": "icehockey_nhl",
    "MLS": "soccer_usa_mls",
}

_SUPPORTED_MARKETS = frozenset({"h2h", "spreads", "totals"})


class OddsProviderSchemaError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class OddsCollectionWarning:
    code: str
    message: str
    event_id: str | None = None
    bookmaker_key: str | None = None
    market_key: str | None = None


@dataclass(frozen=True, slots=True)
class OddsOutcomeSnapshot:
    name: str
    price: float
    point: float | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("outcome name cannot be blank")
        if not math.isfinite(self.price):
            raise ValueError("outcome price must be finite")
        if self.point is not None and not math.isfinite(self.point):
            raise ValueError("outcome point must be finite when present")


@dataclass(frozen=True, slots=True)
class OddsMarketSnapshot:
    key: str
    outcomes: tuple[OddsOutcomeSnapshot, ...]
    provider_updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("market key cannot be blank")
        if self.provider_updated_at is not None:
            require_aware(self.provider_updated_at, "provider_updated_at")


@dataclass(frozen=True, slots=True)
class BookmakerSnapshot:
    key: str
    title: str
    provider_updated_at: datetime | None
    markets: tuple[OddsMarketSnapshot, ...]

    def __post_init__(self) -> None:
        if not self.key.strip() or not self.title.strip():
            raise ValueError("bookmaker key and title cannot be blank")
        if self.provider_updated_at is not None:
            require_aware(self.provider_updated_at, "provider_updated_at")


@dataclass(frozen=True, slots=True)
class OddsEventSnapshot:
    provider_event_id: str
    sport_key: str
    commence_time: datetime
    home_participant: str
    away_participant: str
    bookmakers: tuple[BookmakerSnapshot, ...]
    observed_at: datetime
    available_at: datetime

    def __post_init__(self) -> None:
        for value, label in (
            (self.provider_event_id, "provider_event_id"),
            (self.sport_key, "sport_key"),
            (self.home_participant, "home_participant"),
            (self.away_participant, "away_participant"),
        ):
            if not value.strip():
                raise ValueError(f"{label} cannot be blank")
        if self.home_participant == self.away_participant:
            raise ValueError("home and away participants must differ")
        require_aware(self.commence_time, "commence_time")
        require_aware(self.observed_at, "observed_at")
        require_aware(self.available_at, "available_at")
        if self.available_at > self.observed_at:
            raise ValueError("available_at cannot be later than observed_at")


@dataclass(frozen=True, slots=True)
class OddsCollectionResult:
    events: tuple[OddsEventSnapshot, ...]
    raw_payload: ProviderPayload
    diagnostics: HttpRequestDiagnostics
    quota: dict[str, str | None]
    warnings: tuple[OddsCollectionWarning, ...] = ()


def provider_sport_key(sport: str) -> str:
    key = sport.strip().upper()
    try:
        return SPORT_KEYS[key]
    except KeyError as exc:
        raise ValueError(f"unsupported configured sport {sport!r}") from exc


def _object(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise OddsProviderSchemaError(f"{label} must be an object")
    return cast(dict[str, object], value)


def _list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise OddsProviderSchemaError(f"{label} must be a list")
    return cast(list[object], value)


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OddsProviderSchemaError(f"{label} must be a nonblank string")
    return value


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise OddsProviderSchemaError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise OddsProviderSchemaError(f"{label} must be finite")
    return result


def _optional_number(value: object, label: str) -> float | None:
    if value is None:
        return None
    return _number(value, label)


def _timestamp(value: object, label: str) -> datetime:
    source = _string(value, label)
    try:
        parsed = datetime.fromisoformat(source.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OddsProviderSchemaError(f"{label} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OddsProviderSchemaError(f"{label} must be timezone-aware")
    return parsed.astimezone(UTC)


def _optional_timestamp(value: object, label: str) -> datetime | None:
    if value is None:
        return None
    return _timestamp(value, label)


def _parse_market(
    raw: object,
    *,
    event_id: str,
    bookmaker_key: str,
    warnings: list[OddsCollectionWarning],
) -> OddsMarketSnapshot | None:
    try:
        market = _object(raw, "market")
        market_key = _string(market.get("key"), "market.key")
        provider_updated_at = _optional_timestamp(
            market.get("last_update"),
            "market.last_update",
        )
        outcome_items = _list(market.get("outcomes"), "market.outcomes")
    except OddsProviderSchemaError as exc:
        warnings.append(
            OddsCollectionWarning(
                "malformed_market",
                str(exc),
                event_id=event_id,
                bookmaker_key=bookmaker_key,
            )
        )
        return None

    outcomes: list[OddsOutcomeSnapshot] = []
    for raw_outcome in outcome_items:
        try:
            outcome = _object(raw_outcome, "outcome")
            outcomes.append(
                OddsOutcomeSnapshot(
                    name=_string(outcome.get("name"), "outcome.name"),
                    price=_number(outcome.get("price"), "outcome.price"),
                    point=_optional_number(outcome.get("point"), "outcome.point"),
                )
            )
        except OddsProviderSchemaError as exc:
            warnings.append(
                OddsCollectionWarning(
                    "malformed_outcome",
                    str(exc),
                    event_id=event_id,
                    bookmaker_key=bookmaker_key,
                    market_key=market_key,
                )
            )
    if not outcomes:
        return None
    return OddsMarketSnapshot(
        key=market_key,
        outcomes=tuple(outcomes),
        provider_updated_at=provider_updated_at,
    )


def _parse_bookmaker(
    raw: object,
    *,
    event_id: str,
    warnings: list[OddsCollectionWarning],
) -> BookmakerSnapshot | None:
    try:
        bookmaker = _object(raw, "bookmaker")
        bookmaker_key = _string(bookmaker.get("key"), "bookmaker.key")
        title = _string(bookmaker.get("title"), "bookmaker.title")
        provider_updated_at = _optional_timestamp(
            bookmaker.get("last_update"),
            "bookmaker.last_update",
        )
        market_items = _list(bookmaker.get("markets"), "bookmaker.markets")
    except OddsProviderSchemaError as exc:
        warnings.append(
            OddsCollectionWarning(
                "malformed_bookmaker",
                str(exc),
                event_id=event_id,
            )
        )
        return None

    parsed_markets: list[OddsMarketSnapshot] = []
    for item in market_items:
        parsed = _parse_market(
            item,
            event_id=event_id,
            bookmaker_key=bookmaker_key,
            warnings=warnings,
        )
        if parsed is not None:
            parsed_markets.append(parsed)
    if not parsed_markets:
        return None
    return BookmakerSnapshot(
        key=bookmaker_key,
        title=title,
        provider_updated_at=provider_updated_at,
        markets=tuple(parsed_markets),
    )


def _parse_event(
    raw: object,
    *,
    expected_sport_key: str,
    observed_at: datetime,
    warnings: list[OddsCollectionWarning],
) -> OddsEventSnapshot | None:
    event_id: str | None = None
    try:
        event = _object(raw, "event")
        raw_event_id = event.get("id")
        if isinstance(raw_event_id, str) and raw_event_id.strip():
            event_id = raw_event_id
        parsed_event_id = _string(raw_event_id, "event.id")
        sport_key = _string(event.get("sport_key"), "event.sport_key")
        if sport_key != expected_sport_key:
            raise OddsProviderSchemaError(
                "event.sport_key does not match the requested sport"
            )
        commence_time = _timestamp(
            event.get("commence_time"),
            "event.commence_time",
        )
        home = _string(event.get("home_team"), "event.home_team")
        away = _string(event.get("away_team"), "event.away_team")
        if home == away:
            raise OddsProviderSchemaError("event home and away teams must differ")
        bookmaker_items = _list(event.get("bookmakers"), "event.bookmakers")
    except OddsProviderSchemaError as exc:
        warnings.append(
            OddsCollectionWarning(
                "malformed_event",
                str(exc),
                event_id=event_id,
            )
        )
        return None

    parsed_bookmakers: list[BookmakerSnapshot] = []
    for item in bookmaker_items:
        parsed = _parse_bookmaker(
            item,
            event_id=parsed_event_id,
            warnings=warnings,
        )
        if parsed is not None:
            parsed_bookmakers.append(parsed)
    return OddsEventSnapshot(
        provider_event_id=parsed_event_id,
        sport_key=sport_key,
        commence_time=commence_time,
        home_participant=home,
        away_participant=away,
        bookmakers=tuple(parsed_bookmakers),
        observed_at=observed_at,
        available_at=observed_at,
    )


def group_two_way_offers(
    event: OddsEventSnapshot,
    market_key: str,
) -> dict[float | None, tuple[TwoWayOffer, ...]]:
    """Build line-aware two-way offers using raw provider participant strings."""

    grouped: dict[float | None, list[TwoWayOffer]] = {}
    for bookmaker in event.bookmakers:
        for market in bookmaker.markets:
            if market.key != market_key:
                continue
            by_name = {outcome.name: outcome for outcome in market.outcomes}
            line: float | None
            first_name: str
            second_name: str
            if market_key == "h2h":
                first_name = event.home_participant
                second_name = event.away_participant
                line = None
            elif market_key == "spreads":
                first_name = event.home_participant
                second_name = event.away_participant
                home = by_name.get(first_name)
                away = by_name.get(second_name)
                if (
                    home is None
                    or away is None
                    or home.point is None
                    or away.point is None
                ):
                    continue
                if not math.isclose(home.point, -away.point, abs_tol=1e-9):
                    continue
                line = 0.0 if home.point == 0 else home.point
            elif market_key == "totals":
                first_name = "Over"
                second_name = "Under"
                over = by_name.get(first_name)
                under = by_name.get(second_name)
                if (
                    over is None
                    or under is None
                    or over.point is None
                    or under.point is None
                ):
                    continue
                if not math.isclose(over.point, under.point, abs_tol=1e-9):
                    continue
                line = over.point
            else:
                raise ValueError(f"unsupported two-way market {market_key!r}")

            first = by_name.get(first_name)
            second = by_name.get(second_name)
            if first is None or second is None:
                continue
            offer = TwoWayOffer(
                bookmaker_key=bookmaker.key,
                first_side=first_name,
                second_side=second_name,
                first_price=first.price,
                second_price=second.price,
                line=line,
                provider_updated_at=(
                    market.provider_updated_at or bookmaker.provider_updated_at
                ),
            )
            grouped.setdefault(line, []).append(offer)
    return {line: tuple(offers) for line, offers in grouped.items()}


class TheOddsApiClient:
    def __init__(self, http: HttpClient) -> None:
        self.http = http

    def collect(
        self,
        *,
        sport_key: str,
        api_key: str,
        regions: tuple[str, ...] = ("us",),
        markets: tuple[str, ...] = ("h2h", "spreads", "totals"),
    ) -> OddsCollectionResult:
        if not sport_key.strip():
            raise ValueError("sport_key cannot be blank")
        if not api_key.strip():
            raise ValueError("api_key cannot be blank")
        if not regions or any(not region.strip() for region in regions):
            raise ValueError("regions must contain nonblank values")
        if not markets or any(
            market not in _SUPPORTED_MARKETS for market in markets
        ):
            raise ValueError(
                "markets must be a nonempty subset of h2h, spreads, totals"
            )
        if len(regions) != len(set(regions)):
            raise ValueError("regions cannot contain duplicates")
        if len(markets) != len(set(markets)):
            raise ValueError("markets cannot contain duplicates")

        result = self.http.get_json(
            f"{THE_ODDS_API_BASE}/{sport_key}/odds/",
            params={
                "apiKey": api_key,
                "regions": ",".join(regions),
                "markets": ",".join(markets),
                "oddsFormat": "american",
                "dateFormat": "iso",
            },
        )
        if not isinstance(result.payload, list):
            raise OddsProviderSchemaError(
                "The Odds API odds root must be a list"
            )
        observed_at = datetime.now(UTC)
        warnings: list[OddsCollectionWarning] = []
        parsed_events: list[OddsEventSnapshot] = []
        for item in result.payload:
            parsed = _parse_event(
                item,
                expected_sport_key=sport_key,
                observed_at=observed_at,
                warnings=warnings,
            )
            if parsed is not None:
                parsed_events.append(parsed)
        if result.payload and not parsed_events:
            raise OddsProviderSchemaError(
                "The Odds API payload contained no structurally valid events"
            )
        raw_payload = ProviderPayload(
            content=result.content,
            content_type=result.content_type,
            source_uri=result.response_url,
            provenance=TemporalProvenance(
                observed_at=observed_at,
                available_at=observed_at,
            ),
            provider_schema_version="v4",
        )
        return OddsCollectionResult(
            events=tuple(parsed_events),
            raw_payload=raw_payload,
            diagnostics=result.diagnostics,
            quota=result.diagnostics.quota_headers,
            warnings=tuple(warnings),
        )
