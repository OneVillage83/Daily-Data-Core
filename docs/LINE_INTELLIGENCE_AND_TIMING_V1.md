# Daily Data Core Line Intelligence and Timing Architecture V1

Status: **governing shared market-data architecture**

Date locked: 2026-09-12

## 1. Purpose

Daily Data Core (DDC) owns sport-agnostic acquisition, preservation, normalization, and reusable derivation of market evidence. Each sport repository owns the sport-specific interpretation of that evidence, including the actual Line Timing Model (LTM), fair price, edge, expected value, and Recommendation Gate.

This document defines the shared infrastructure needed to compare the independent **TDL Unified Line** against the market without contaminating the independent forecasting path.

## 2. Core principle

DDC may answer:

- What was available?
- From which source?
- At what time?
- At what price/line?
- How did the market move?
- How dispersed were books?
- What was the no-vig consensus at that moment?
- What did exchanges/prediction markets imply at that moment?

DDC does **not** answer:

- Who should win?
- What is the TDL fair probability?
- Is the bet +EV?
- Should TDL publish a play?
- Should a user bet now or wait?

Those are sport/model decision responsibilities.

## 3. Shared market timeline

DDC should preserve the complete market history rather than only open/current/close labels.

Representative timeline:

```text
OPEN
  |
5 min
  |
15 min
  |
1 hr
  |
6 hr
  |
24 hr
  |
GAME DAY
  |
1 hr before
  |
30 min
  |
5 min
  |
CLOSE / START CUTOFF
```

The labels above are derived views. The source of truth is immutable time-stamped quote evidence.

## 4. Canonical normalized market record

The shared record should support at least:

```text
event_external_id
sport_or_dataset_key
provider
sportsbook_or_venue
source_type
market_type
selection
line
odds
implied_probability
no_vig_probability_when_derivable
currency_or_contract_metadata_when_relevant
liquidity_when_available
volume_when_available
provider_market_updated_at
provider_book_updated_at
published_at
observed_at
available_at
scheduled_start_at
seconds_to_start
raw_evidence_ref
snapshot_id
```

Source types should support at minimum:

- `SPORTSBOOK`
- `EXCHANGE`
- `PREDICTION_MARKET`
- `CONSENSUS_DERIVED`

`TDL_INTERNAL` forecasts may be joined for evaluation in consumer systems but should not be inserted into provider market evidence as though they were market quotes.

## 5. DDC-derived market features

DDC may provide sport-agnostic derived artifacts such as:

```text
opening_line
opening_price
current_line
current_price
consensus_line
consensus_probability
sharp_consensus_line
sharp_consensus_probability
soft_consensus_line
book_dispersion
sharp_soft_divergence
line_delta_from_open
probability_delta_from_open
movement_velocity
movement_acceleration
quote_age
market_freshness
steam_candidate_flag
reverse_move_candidate_flag
prediction_market_divergence
```

These are generic evidence summaries. Sports decide whether and how they matter.

## 6. Opening, current, consensus, and closing views

For every TDL forecast, the consumer should be able to evaluate:

```text
TDL fair spread
    vs opening
    vs current
    vs consensus
    vs closing (post-event-start evaluation only)
```

Equivalent comparisons should exist for moneyline probability/price and totals.

### Opening
The first quote that satisfies the configured market/open definition for that source set.

### Current
The most recent PIT-eligible quote at prediction time `T`.

### Consensus
A versioned derived result from an explicitly defined eligible source set, weighting method, freshness rule, and no-vig method.

### Closing
A post-hoc evaluation view representing the configured final executable/sharp/consensus state before event start. Closing values are **never eligible for an earlier pregame prediction unless they had actually been available by that earlier cutoff**.

## 7. Point-in-time market eligibility

At prediction time `T`, any market feature may use only evidence with:

```text
available_at <= T
```

and any stricter source/market freshness rule.

A backtest must reconstruct the market as it was knowable at `T`, not query a current database view that already knows the close.

## 8. Line Timing Model boundary

The shared DDC layer provides the evidence/features. The sport repository owns the LTM because market behavior differs materially by sport.

Examples:

```text
DDC Line Intelligence
      |
      +--> MLB-LTM
      +--> NFL-LTM
      +--> NCAAF-LTM
      +--> NBA-LTM
      +--> NCAAB-LTM
      +--> NHL-LTM
      +--> Soccer-LTM
      +--> Tennis-LTM
      +--> future sport LTMs
```

An LTM may estimate outputs such as:

```text
expected_closing_line
expected_closing_probability
P(line crosses key threshold)
expected_price_change
expected_line_CLV_if_act_now
expected_price_CLV_if_act_now
recommended timing class
```

The LTM is a market-behavior model, not an independent sports-outcome model.

## 9. Timing decision example

```text
Current spread            SF -2.5
TDL Unified fair spread   SF -4.1
LTM expected close        SF -3.4
P(close <= -3.5)          64%
Expected line CLV now     +0.9 points
Timing                    BET_NOW
```

A second case may produce:

```text
Current spread            KC -6.5
TDL Unified fair spread   KC -7.2
LTM expected close        KC -6.0
Timing                    WAIT
```

TDL can like a side while still expecting a better execution price later.

## 10. Prediction-market integration

Prediction markets and exchanges are treated as independent market-information sources, not as automatic inputs to the TDL independent sports model.

The decision layer may compare:

```text
TDL Unified Line
sportsbook consensus
sharp-book consensus
exchange probability
prediction-market probability
```

This allows the system to measure confirmation, disagreement, liquidity effects, and relative information timing without contaminating the proprietary independent fair line.

## 11. Closing-Line Value

TDL should track both:

### Price CLV
Example:

```text
executed +110
closed   +102
```

### Line CLV
Example:

```text
executed +3.5
closed   +2.5
```

CLV must be calculated against explicitly defined closing references. A generic "close" with no source-set definition is not sufficient for scientific evaluation.

## 12. Market source hierarchy and multiple closes

There may be multiple legitimate closing references:

- sharp-book close;
- consensus close;
- exchange close;
- best executable close;
- same-book close.

Evaluation should preserve them separately instead of collapsing them into one ambiguous value.

## 13. Market-aware residual model

Sport repositories may train a separately labeled market-aware residual model using PIT-correct market state plus independent model outputs.

Conceptually:

```text
market_residual = observed_outcome - p_market
predicted_residual = f(
    TDL_independent_outputs,
    market_state,
    model_disagreement,
    context
)
```

The output may inform the decision estimate but must never overwrite the stored TDL Unified Line.

## 14. Immutable history

Quotes and derived market snapshots are append-only evidence. Repeated observations are valid even when numerically unchanged because they establish what was still being published and when it was observed.

Corrections create new evidence; they do not rewrite old PIT history.

## 15. Recommended shared evaluation views

DDC should make it straightforward for consumers to derive or persist:

```text
prediction_id
prediction_time
seconds_to_start
TDL_fair_probability
TDL_fair_spread
TDL_fair_total
market_open_probability
market_current_probability
market_consensus_probability
market_close_probability_posthoc
open_line
current_line
consensus_line
close_line_posthoc
line_delta_open_to_prediction
line_delta_prediction_to_close
price_CLV
line_CLV
```

The TDL probabilities remain sport-owned. DDC owns the market evidence and generic joins/keys needed to make this evaluation reproducible.

## 16. Architectural invariant

> **DDC records what the market knew and how the market moved. Sport repositories decide what that means. Closing evidence is evaluation data until the clock actually reaches the close.**
