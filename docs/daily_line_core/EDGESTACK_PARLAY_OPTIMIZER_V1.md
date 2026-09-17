# EdgeStack Parlay Optimizer V1

**Status:** DOCUMENTED — IMPLEMENTATION NOT YET AUTHORIZED  
**Date:** 2026-09-17  
**Canonical logical owner:** Daily-Line-Core (DLC)  
**Temporary staging home:** `Daily-Data-Core/docs/daily_line_core/`  
**Feature name:** **EdgeStack**  
**Tagline:** **Stack the Edge. Not the Odds.**

## 1. Purpose

EdgeStack is The Daily Line's probability-first, market-aware **parlay/combo optimizer**.

It consumes sealed sport-level predictions/recommendations plus point-in-time market evidence and searches for short 2-5 leg combinations that optimize the relationship between:

- joint hit probability;
- market-implied break-even probability;
- offered combo/parlay payout;
- cross-leg correlation;
- expected value;
- uncertainty/calibration quality;
- Recommendation Gate eligibility; and
- quote freshness/executability.

EdgeStack is explicitly **not** a lottery-ticket generator. It must not add weak legs merely to increase a displayed multiplier.

> **Stack the Edge. Not the Odds.**

## 2. Why EdgeStack belongs in DLC

Individual sports own their own predictions, fair probabilities, market-aware decision outputs, Recommendation Gates, and same-event simulation/joint information.

Daily-Data-Core owns market evidence and generic market mathematics.

EdgeStack is different: it chooses combinations **across already-sealed sport decisions**, potentially across different games and sports. That is a cross-sport product-level optimization problem and therefore belongs in Daily-Line-Core.

Neither DDC nor The-Daily-Line-Automation may become the hidden owner of EdgeStack mathematics.

## 3. Product differentiation

Most parlay products start with payout size and search for legs that create an attractive multiplier.

EdgeStack reverses the process:

1. each sport models every supported market it knows how to model;
2. each sport produces calibrated fair probabilities and Recommendation Gate outputs;
3. DLC joins those sealed decisions to current point-in-time market evidence;
4. DLC creates the **All Bets Prediction Scanner**;
5. individually eligible legs enter the EdgeStack candidate pool;
6. DLC enumerates valid 2-5 leg combinations;
7. joint probability is estimated with explicit dependency/correlation treatment;
8. the joint probability is compared with the actual provider combo/parlay quote;
9. candidates are ranked by hit probability, value, uncertainty, correlation quality, and quote freshness; and
10. only combinations that satisfy configured quality gates are published.

This creates two first-class subscription surfaces:

- **All Bets Prediction Scanner** — the model view of every supported individual bet;
- **EdgeStack Parlay Optimizer** — optimized short combinations built only from approved legs.

## 4. V1 scope

EdgeStack V1 covers:

- 2-5 leg combinations only;
- cross-game combinations;
- cross-sport combinations;
- same-game combinations only when correlation/joint behavior is explicitly modeled;
- Kalshi Combo/RFQ quote evaluation;
- sportsbook parlay quote evaluation where a supported provider exposes a valid quote;
- Core, Value, and Upside classifications;
- ranking by hit probability, value, balance, and upside;
- immutable publication artifacts suitable for report, infographic, website, and downstream automation;
- historical PIT evaluation and calibration of both legs and combinations.

## 5. Explicit V1 non-goals

The following are deliberately deferred:

- bankroll management;
- Kelly sizing;
- stake recommendations;
- daily loss limits / stop-loss rules;
- chase-prevention logic;
- wallet/account integration;
- automatic bet placement;
- autonomous wagering;
- personalized wagering amounts.

## 6. All Bets prerequisite

EdgeStack must never run directly from a hand-selected pick list.

The prerequisite is a sealed DLC `AllBetsSnapshot` containing every supported/modelable market available under the slate/cutoff policy.

Each row should expose at minimum:

- canonical bet/market key;
- sport / league / event / participant refs;
- market class / side / threshold;
- provider / venue;
- quote / multiplier / price;
- quote timestamp and freshness;
- market-implied probability;
- fee-aware break-even where available;
- TDL fair probability / fair price;
- uncertainty/calibration metadata;
- probability edge;
- expected value where calculable;
- Recommendation Gate state;
- reason/evidence refs;
- model/config/release provenance;
- data cutoff;
- settlement-rule version;
- supported/unsupported/degraded status.

## 7. Leg eligibility

A leg may enter the EdgeStack pool only when all required gates pass.

Minimum V1 requirements:

1. canonical settlement definition exists;
2. provider quote is current enough;
3. sport emits a calibrated fair probability;
4. cutoff is valid and contains no post-start leakage;
5. sport Recommendation Gate permits EdgeStack use;
6. model/calibration quality clears configured minimums;
7. quote is executable/realistic enough for publication mode;
8. required same-event joint/correlation evidence exists when needed; and
9. no policy/exclusion block applies.

A bad individual leg cannot be rescued by placing it in a parlay.

## 8. Candidate generation

EdgeStack enumerates valid combinations of 2 through 5 eligible legs.

Rules:

- cross-game candidates are first-class;
- cross-sport candidates are first-class;
- same-game candidates require explicit dependency handling;
- contradictory legs are rejected;
- duplicate/equivalent exposures are rejected;
- stale/expired quotes are rejected;
- unsupported settlement dependencies are rejected;
- configurable concentration limits may restrict repeated exposure to one event/player/root outcome;
- candidate identity is deterministic for identical semantic inputs;
- no leg may be added solely because it raises payout.

The production search may use pruning, branch-and-bound, top-K, or other bounded methods, but pruning must be reproducible and independent of provider UI ordering.

## 9. Joint probability and correlation

### 9.1 Unrelated events

For effectively independent legs from unrelated events, the baseline may be:

`P(combo) = product(P(leg_i))`

provided each input probability is calibrated and the independence assumption is explicit.

### 9.2 Correlated legs

Same-game/dependent legs must not be treated as independent.

Preferred authority order:

1. sport-authoritative joint samples from a certified simulation;
2. empirically calibrated joint-distribution model;
3. approved pairwise/higher-order dependency model with documented limits;
4. otherwise the correlated combination is not authoritative and must not publish as an EdgeStack.

Examples include quarterback passing yards + receiver yards, game total + individual scoring props, or multiple outcomes driven by the same starting-pitcher/lineup state.

### 9.3 Uncertainty

The joint result should retain confidence/uncertainty metadata. Ranking may use both point estimates and conservative estimates so fragile disagreement is not presented as false precision.

## 10. Pricing and value

For decimal multiplier `M`:

`break_even_probability = 1 / M`

Before fees/slippage:

`gross_expected_return = P(combo) * M`

`gross_EV = (P(combo) * M) - 1`

When a provider exposes fees, spread, RFQ cost, or execution cost, DLC should compute fee-aware/net break-even and EV where defensible.

Required comparison fields:

- quoted multiplier / contract price;
- raw break-even probability;
- net break-even probability when calculable;
- model joint probability;
- probability edge;
- gross EV;
- net EV when calculable;
- quote timestamp / expiry;
- correlation method / confidence;
- upstream sport + DDC provenance.

## 11. Kalshi Combo behavior

A Kalshi Combo quote is a real market observation and may contain correlation adjustments similar to same-game sportsbook parlays.

Workflow:

1. DLC creates a valid candidate from approved legs;
2. the actual Kalshi Combo/RFQ quote is obtained or ingested;
3. DLC computes break-even probability from the quote;
4. DLC compares it with the correlation-adjusted joint probability;
5. expired/stale quotes fail closed;
6. the quote identity/timestamp/provenance are stored with the recommendation.

The product of standalone contract multipliers may be kept as a diagnostic reference, but it never substitutes for an available real Combo quote.

## 12. EdgeStack classes

### Core EdgeStack

Goal: highest realistic hit probability while retaining favorable model-vs-price value.

Typical properties:

- 2-3 legs;
- lower alternate thresholds may be preferred;
- lower variance;
- cross-game/cross-sport construction is encouraged where it avoids unnecessary correlation haircut.

### Value EdgeStack

Goal: strongest balance of probability, net EV, payout, and model confidence.

Typical properties:

- 2-4 legs;
- positive net model edge required;
- moderate payout;
- likely default showcase class.

### Upside EdgeStack

Goal: larger payout while retaining strict value/quality requirements.

Typical properties:

- 3-5 legs;
- higher variance;
- stronger minimum EV/confidence requirements than an ordinary longshot;
- all legs still individually eligible.

A giant lottery parlay is not automatically an EdgeStack merely because estimated EV is positive.

## 13. Ranking views

DLC must preserve separate dimensions rather than hiding all behavior in one opaque score.

Required metrics:

- joint hit probability;
- probability edge vs break-even;
- gross/net EV;
- multiplier/payout;
- calibration quality;
- correlation quality;
- uncertainty width;
- quote freshness;
- leg count.

Required user/product views:

- `HIGHEST_HIT_RATE`;
- `BEST_VALUE`;
- `BEST_BALANCE`;
- `BEST_UPSIDE`.

A future composite score may be added, but the component metrics remain visible/auditable.

## 14. Publication contract

Each EdgeStack publication should include:

- stable `edgestack_id`;
- parent `DailyLinePublicationPackage` ID;
- slate/date/sport scope;
- class (`CORE`, `VALUE`, `UPSIDE`);
- semantic leg-set identity;
- display ordering;
- each leg's sport fair probability, quote, edge, gate, and provenance;
- combo quote/multiplier;
- break-even probability;
- joint model probability;
- uncertainty/confidence;
- gross/net EV where calculable;
- correlation method/summary;
- quote timestamp / expiry;
- concise explanation;
- sport/model/config/data-cutoff IDs;
- publication timestamp;
- settlement/result fields after completion.

Historical publications preserve the exact quote/model snapshot used at publication rather than substituting current prices.

## 15. Report / infographic / website behavior

The sealed DLC publication package should expose:

- **Core EdgeStack**;
- **Value EdgeStack**;
- **Upside EdgeStack**;
- optional ranked alternates;
- each candidate's hit probability, break-even probability, multiplier, edge, EV, leg count, correlation status, and quote timestamp.

Downstream renderers may choose different layouts but may not recalculate or silently alter the ranking.

## 16. Historical evaluation

Required evaluation includes:

- point-in-time market snapshots only;
- no post-start contamination;
- per-leg calibration by sport/market class;
- joint probability calibration by EdgeStack class and leg count;
- Brier/log-loss or other approved probability metrics;
- predicted-vs-realized hit-rate bins;
- quoted break-even vs realized performance;
- gross and fee-aware EV tracking;
- same-game vs cross-game performance;
- cross-sport vs single-sport performance;
- calibration drift;
- settlement correctness;
- stale/unavailable quote audit.

## 17. Failure/degradation behavior

Fail closed when:

- required leg probability is missing;
- quote is stale/malformed;
- settlement semantics are ambiguous;
- model/cutoff/provenance is incomplete;
- same-game dependency cannot be modeled;
- Recommendation Gate authority is missing;
- combo quote cannot be reconciled to the candidate;
- any required input contains post-start information.

EdgeStack failure must not invalidate valid All Bets/single-bet publication. The EdgeStack section may be marked degraded/unavailable while other DLC output remains valid.

## 18. Pipeline placement

```text
Daily-MLB / Daily-NFL / Daily-NCAAF / future sports
        |
        v
sealed SportDecisionPackages
        |
        +-----------------------------+
                                      v
DDC MarketEvidenceBundle ----> DAILY-LINE-CORE
                                      |
                               All Bets Snapshot
                                      |
                               EdgeStack Engine
                             2-5 leg candidate search
                             joint/correlation model
                              real quote comparison
                               ranking / classes
                                      |
                                      v
                           DailyLinePublicationPackage
                                      |
          +---------------------------+---------------------------+
          |                           |                           |
          v                           v                           v
      Report/Infographic          Website/App                  TDLA
                                                       video/social/marketing
```

## 19. Required invariants

1. Prediction != market != value != recommendation.
2. All supported/modelable individual bets are assembled before combination optimization.
3. A high payout is not evidence of value.
4. A high hit probability is not evidence of value unless the price is favorable enough.
5. Positive-value singles do not guarantee a positive-value combination after provider pricing/correlation.
6. Same-game correlation must be modeled or the combo fails closed.
7. Cross-game independence is an explicit testable assumption.
8. Every published number binds to PIT quote and model/data cutoff provenance.
9. No weak leg is added for payout optics.
10. V1 contains 2-5 legs only.
11. Every leg independently satisfies sport eligibility/Recommendation Gate requirements.
12. Unsupported markets are labeled unsupported, not guessed.
13. EdgeStack optimizes recommendations; it does not place bets.
14. Bankroll/stake logic is outside V1.

## 20. Production-authority prerequisites

EdgeStack cannot become production-authoritative until:

- canonical sport decision and market-evidence contracts exist;
- every supported sport emits calibrated per-market probabilities;
- Recommendation Gate integration is versioned/deterministic;
- DDC supplies PIT normalized quote provenance;
- deterministic 2-5 leg generation is implemented;
- dependency/correlation handling is validated for every published class;
- provider combo/parlay quote identity is preserved;
- gross and fee-aware break-even/EV calculations are tested;
- PIT backtests clear defined calibration/promotion thresholds;
- same-game/cross-game/cross-sport evaluation is separately reported;
- DLC publication contracts are stable;
- downstream consumers display model probability and market break-even distinctly;
- settlement/audit verifies outcomes correctly.
