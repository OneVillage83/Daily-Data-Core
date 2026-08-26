from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from daily_data_core.markets import (
    ConsensusThresholds,
    FreshnessStatus,
    FreshnessThresholds,
    TwoWayOffer,
    american_to_probability,
    best_american_price,
    calculate_hold,
    classify_freshness,
    consensus_two_way,
    no_vig_from_american,
)


def test_american_odds_math() -> None:
    assert american_to_probability(150.0) == pytest.approx(0.4)
    assert american_to_probability(-150.0) == pytest.approx(0.6)
    assert calculate_hold(-110.0, -110.0) == pytest.approx(0.0476190476)
    first, second = no_vig_from_american(-110.0, -110.0)
    assert first == pytest.approx(0.5)
    assert second == pytest.approx(0.5)
    assert best_american_price((-120.0, -115.0, 105.0)) == 105.0


def test_consensus_preserves_book_count_and_disagreement() -> None:
    offers = (
        TwoWayOffer("book-a", "Home", "Away", -110.0, -110.0),
        TwoWayOffer("book-b", "Home", "Away", -120.0, 100.0),
        TwoWayOffer("book-c", "Home", "Away", -105.0, -115.0),
        TwoWayOffer("book-d", "Home", "Away", -108.0, -112.0),
    )
    summary = consensus_two_way(
        offers,
        ConsensusThresholds(minimum_books=2, moderate_books=4, high_books=7),
    )
    assert summary.book_count == 4
    assert summary.confidence == "moderate"
    assert summary.first_fair_probability + summary.second_fair_probability == pytest.approx(1.0)
    assert summary.disagreement_stddev > 0


def test_freshness_classification() -> None:
    observed = datetime(2026, 8, 26, 18, 0, tzinfo=timezone.utc)
    thresholds = FreshnessThresholds(fresh_seconds=120, stale_seconds=300)
    assert classify_freshness(observed - timedelta(seconds=30), observed, thresholds) is FreshnessStatus.FRESH
    assert classify_freshness(observed - timedelta(seconds=180), observed, thresholds) is FreshnessStatus.AGING
    assert classify_freshness(observed - timedelta(seconds=600), observed, thresholds) is FreshnessStatus.STALE
    assert classify_freshness(None, observed, thresholds) is FreshnessStatus.UNKNOWN
