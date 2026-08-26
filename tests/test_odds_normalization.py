from __future__ import annotations

from datetime import UTC, datetime

from daily_data_core.odds import (
    BookmakerSnapshot,
    OddsEventSnapshot,
    OddsMarketSnapshot,
    OddsOutcomeSnapshot,
    group_two_way_offers,
)


def _event() -> OddsEventSnapshot:
    now = datetime(2026, 8, 26, 18, 0, tzinfo=UTC)
    return OddsEventSnapshot(
        provider_event_id="event-1",
        sport_key="americanfootball_nfl",
        commence_time=now,
        home_participant="Home",
        away_participant="Away",
        observed_at=now,
        available_at=now,
        bookmakers=(
            BookmakerSnapshot(
                key="book-a",
                title="Book A",
                provider_updated_at=now,
                markets=(
                    OddsMarketSnapshot(
                        key="h2h",
                        outcomes=(
                            OddsOutcomeSnapshot("Home", -120.0),
                            OddsOutcomeSnapshot("Away", 100.0),
                        ),
                    ),
                    OddsMarketSnapshot(
                        key="spreads",
                        outcomes=(
                            OddsOutcomeSnapshot("Home", -110.0, -3.0),
                            OddsOutcomeSnapshot("Away", -110.0, 3.0),
                        ),
                    ),
                    OddsMarketSnapshot(
                        key="totals",
                        outcomes=(
                            OddsOutcomeSnapshot("Over", -105.0, 47.5),
                            OddsOutcomeSnapshot("Under", -115.0, 47.5),
                        ),
                    ),
                ),
            ),
        ),
    )


def test_group_two_way_offers_is_line_aware() -> None:
    event = _event()
    h2h = group_two_way_offers(event, "h2h")
    spread = group_two_way_offers(event, "spreads")
    totals = group_two_way_offers(event, "totals")
    assert h2h[None][0].first_side == "Home"
    assert spread[-3.0][0].line == -3.0
    assert totals[47.5][0].first_side == "Over"
