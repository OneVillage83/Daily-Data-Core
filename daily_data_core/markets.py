"""Sport-agnostic market contracts and odds mathematics."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from statistics import fmean, pstdev

from daily_data_core.temporal import require_aware


class MarketKind(StrEnum):
    H2H = "h2h"
    SPREAD = "spreads"
    TOTAL = "totals"


class FreshnessStatus(StrEnum):
    FRESH = "fresh"
    AGING = "aging"
    STALE = "stale"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FreshnessThresholds:
    fresh_seconds: int = 120
    stale_seconds: int = 300
    future_tolerance_seconds: int = 30

    def __post_init__(self) -> None:
        if not 0 <= self.fresh_seconds < self.stale_seconds:
            raise ValueError("freshness thresholds must be nonnegative and ordered")
        if self.future_tolerance_seconds < 0:
            raise ValueError("future_tolerance_seconds must be nonnegative")


@dataclass(frozen=True, slots=True)
class ConsensusThresholds:
    minimum_books: int = 2
    moderate_books: int = 4
    high_books: int = 7

    def __post_init__(self) -> None:
        if not 1 <= self.minimum_books <= self.moderate_books <= self.high_books:
            raise ValueError("consensus thresholds must be positive and ordered")


def _american_price(value: float) -> float:
    if not math.isfinite(value) or abs(value) < 100.0:
        raise ValueError("American odds must be finite with absolute value >= 100")
    return float(value)


def american_to_probability(price: float) -> float:
    normalized = _american_price(price)
    if normalized > 0:
        return 100.0 / (normalized + 100.0)
    return abs(normalized) / (abs(normalized) + 100.0)


def proportional_no_vig_from_american(prices: tuple[float, ...]) -> tuple[float, ...]:
    """Remove vig by proportional normalization for a 2+-outcome market."""

    if len(prices) < 2:
        raise ValueError("at least two prices are required")
    implied = tuple(american_to_probability(price) for price in prices)
    total = sum(implied)
    if not math.isfinite(total) or total <= 0:
        raise ValueError("implied-probability sum must be finite and positive")
    return tuple(probability / total for probability in implied)


def no_vig_probabilities(
    first_probability: float, second_probability: float
) -> tuple[float, float]:
    if first_probability <= 0 or second_probability <= 0:
        raise ValueError("probabilities must be positive")
    total = first_probability + second_probability
    if not math.isfinite(total) or total <= 0:
        raise ValueError("probability sum must be finite and positive")
    return first_probability / total, second_probability / total


def no_vig_from_american(first_price: float, second_price: float) -> tuple[float, float]:
    normalized = proportional_no_vig_from_american((first_price, second_price))
    return normalized[0], normalized[1]


def calculate_hold(first_price: float, second_price: float) -> float:
    return american_to_probability(first_price) + american_to_probability(second_price) - 1.0


def best_american_price(prices: tuple[float, ...]) -> float:
    if not prices:
        raise ValueError("at least one price is required")
    normalized = tuple(_american_price(price) for price in prices)
    return max(normalized)


def classify_freshness(
    provider_updated_at: datetime | None,
    observed_at: datetime,
    thresholds: FreshnessThresholds | None = None,
) -> FreshnessStatus:
    require_aware(observed_at, "observed_at")
    active_thresholds = thresholds or FreshnessThresholds()
    if provider_updated_at is None:
        return FreshnessStatus.UNKNOWN
    require_aware(provider_updated_at, "provider_updated_at")
    age = (observed_at - provider_updated_at).total_seconds()
    if age < -active_thresholds.future_tolerance_seconds:
        return FreshnessStatus.UNKNOWN
    age = max(age, 0.0)
    if age <= active_thresholds.fresh_seconds:
        return FreshnessStatus.FRESH
    if age <= active_thresholds.stale_seconds:
        return FreshnessStatus.AGING
    return FreshnessStatus.STALE


@dataclass(frozen=True, slots=True)
class TwoWayOffer:
    bookmaker_key: str
    first_side: str
    second_side: str
    first_price: float
    second_price: float
    line: float | None = None
    provider_updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.bookmaker_key.strip():
            raise ValueError("bookmaker_key cannot be blank")
        if not self.first_side.strip() or not self.second_side.strip():
            raise ValueError("offer sides cannot be blank")
        if self.first_side == self.second_side:
            raise ValueError("two-way offer sides must differ")
        _american_price(self.first_price)
        _american_price(self.second_price)
        if self.line is not None and not math.isfinite(self.line):
            raise ValueError("line must be finite when present")
        if self.provider_updated_at is not None:
            require_aware(self.provider_updated_at, "provider_updated_at")


@dataclass(frozen=True, slots=True)
class ConsensusSummary:
    book_count: int
    first_fair_probability: float
    second_fair_probability: float
    disagreement_stddev: float
    confidence: str


def consensus_two_way(
    offers: tuple[TwoWayOffer, ...],
    thresholds: ConsensusThresholds | None = None,
) -> ConsensusSummary:
    if not offers:
        raise ValueError("at least one two-way offer is required")
    active_thresholds = thresholds or ConsensusThresholds()
    first_name = offers[0].first_side
    second_name = offers[0].second_side
    line = offers[0].line
    if any(
        offer.first_side != first_name or offer.second_side != second_name or offer.line != line
        for offer in offers
    ):
        raise ValueError("consensus offers must describe the same ordered sides and line")

    fair_first = [
        no_vig_from_american(offer.first_price, offer.second_price)[0] for offer in offers
    ]
    first_mean = fmean(fair_first)
    count = len(offers)
    if count < active_thresholds.minimum_books:
        confidence = "insufficient"
    elif count < active_thresholds.moderate_books:
        confidence = "low"
    elif count < active_thresholds.high_books:
        confidence = "moderate"
    else:
        confidence = "high"
    return ConsensusSummary(
        book_count=count,
        first_fair_probability=first_mean,
        second_fair_probability=1.0 - first_mean,
        disagreement_stddev=pstdev(fair_first) if count > 1 else 0.0,
        confidence=confidence,
    )
