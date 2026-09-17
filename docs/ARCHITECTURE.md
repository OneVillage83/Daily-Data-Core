# Daily Data Core Architecture V1

Status: governing architecture for the shared data layer of The Daily Line.

## Purpose
Daily Data Core (DDC) centralizes facts and infrastructure that are meaningful across sports before sport rules, sport-specific feature engineering, or predictive interpretation are applied.

DDC is a library/service boundary, not a universal sports model. It supplies immutable evidence, normalized shared observations, and reusable calculations to Daily-MLB, Daily-NFL, Daily-NCAAF, and future sport engines.

## Architectural invariants
1. Raw evidence precedes normalization.
2. Every normalized observation retains lineage to provider evidence and temporal provenance.
3. `available_at` is the information-boundary clock used for point-in-time eligibility; later corrections never silently rewrite earlier observations.
4. Provider identifiers remain external identifiers. Sport repositories own canonical sport identity/reconciliation.
5. Shared facts remain semantically neutral. DDC does not encode sport-specific betting folklore or model assumptions.
6. Market snapshots are immutable and book-specific. Consensus/no-vig outputs are derived artifacts, never replacements for raw quotes.
7. Weather uses forecast snapshots for historical prediction contexts. Actual observed weather is a different evidence family and must never replace an earlier forecast in a PIT feature set.
8. All timestamps are timezone-aware. Stored canonical timestamps are UTC.
9. DDC may preserve and derive sport-agnostic market-timeline facts, but the TDL Unified Line, sport-specific Line Timing Models, market-residual models, EV decisions, and Recommendation Gate remain sport/model responsibilities.
10. Closing-market and result evidence are evaluation-only for any earlier prediction context unless that exact evidence was genuinely `available_at` the prediction cutoff.
11. Cross-sport product aggregation is a separate layer: **Daily-Line-Core (DLC)** consumes sealed sport decision packages plus DDC market evidence after sport prediction/decision is complete.
12. DDC does not own the All Bets product scanner, EdgeStack optimizer, cross-sport recommendation ranking, or final Daily Line publication package.

## Layer model

```text
External providers
    |
    v
HTTP / retry / request diagnostics
    |
    v
Immutable raw evidence + checksum + provenance clocks
    |
    v
Provider adapters
    |
    +--> sportsbook market snapshots
    +--> exchange / prediction-market snapshots
    +--> weather forecast snapshots
    +--> venue/geospatial observations
    +--> travel/geography primitives
    |
    v
Shared normalized contracts
    |
    +-------------------+--------------------+
    v                   v                    v
Daily-MLB           Daily-NFL            Daily-NCAAF
sport identity      sport identity       sport identity
sport features      sport features       sport features
models/simulation   models/simulation    models/simulation
Unified Ensemble    Unified Ensemble     Unified Ensemble
TDL fair line       TDL fair line        TDL fair line
sport LTM/decision  sport LTM/decision   sport LTM/decision
    |                   |                    |
    +-------------------+--------------------+
                        |
               sealed SportDecisionPackages
                        |
                        +<--------------------------+
                        |                           |
                        v                           |
                +------------------+                |
                | Daily-Line-Core  |<---------------+
                |  (DLC)           |     DDC sealed market evidence
                +--------+---------+
                         |
            +------------+-------------+
            |            |             |
            v            v             v
       All Bets       EdgeStack    Product Index
       Scanner        Optimizer    / Top Picks
            \            |             /
             +-----------+------------+
                         |
                         v
             DailyLinePublicationPackage
                         |
       +-----------------+------------------+
       |                 |                  |
       v                 v                  v
 Report/Infographic   Website/App       Automation
                                      video/social/etc.
```

`Daily-Line-Core` is a peer product layer, not a submodule of DDC. Its canonical repository is now `OneVillage83/Daily-Line-Core`. The former `docs/daily_line_core/` directory in DDC is historical staging only.

## Core domains

### Provider infrastructure
DDC owns provider descriptors, capability metadata, reliability/licensing fields, generic acquisition requests, source payload envelopes, checksums, and immutable raw storage.

Dataset keys are strings rather than a global sport enum. This permits shared keys such as `market.odds` and `weather.hourly_forecast` while allowing a sport repository adapter to declare a scoped key such as `nfl.play_by_play` without making DDC understand football ontology.

### Markets / odds
DDC owns odds conversion, hold/no-vig math, quote freshness, normalized bookmaker observations, line-aware grouping, consensus statistics, disagreement measures, and provider adapters for shared sportsbook sources.

DDC does not decide whether an outcome is a good bet, estimate a football/baseball win probability, reconcile provider participant names to permanent sport identity, or optimize cross-sport parlays/combos.

### Line Intelligence
DDC owns the shared evidence and sport-agnostic derivations required to reconstruct the full market timeline at any prediction cutoff. This includes open/current/consensus state, quote history, movement deltas, movement velocity/acceleration where defined, book dispersion, sharp/soft divergence, source freshness, and exchange/prediction-market evidence when available.

The source of truth remains immutable time-stamped quote evidence. Labels such as `opening`, `current`, `consensus`, and `closing` are versioned derived views with explicit source-set and cutoff definitions.

DDC does not own sport-specific Line Timing Models. Daily-MLB, Daily-NFL, Daily-NCAAF, and future sport repositories may consume the same normalized market timeline while learning different timing behavior.

### Forecasting support boundary
DDC is not the TDL model registry, ensemble trainer, calibrator, simulator, or recommendation engine. Those remain sport-owned. However, DDC provides the cross-sport temporal and market-evidence contracts required for those systems to remain point-in-time correct and comparable.

The canonical cross-sport forecasting rules are documented in:

- `TDL_UNIFIED_FORECASTING_ARCHITECTURE_V1.md`;
- `LINE_INTELLIGENCE_AND_TIMING_V1.md`;
- `MODEL_REGISTRY_EVALUATION_NO_CONTAMINATION_V1.md`.

After a sport has produced its sealed fair/decision outputs, those outputs may flow to **Daily-Line-Core**, which joins them with DDC market evidence for cross-sport product assembly. DLC may optimize combinations at the product layer, but it may not rewrite sport-authoritative probabilities or Recommendation Gate states.

### Daily-Line-Core handoff boundary

DDC's responsibility toward DLC is to provide/reference point-in-time, immutable, provider-attributed market evidence suitable for a `MarketEvidenceBundle` or equivalent versioned handoff.

DLC then owns:

- the cross-sport All Bets product snapshot;
- EdgeStack 2–5 leg candidate generation and provider quote comparison;
- cross-sport product ranking views;
- final sealed `DailyLinePublicationPackage` consumed by report, infographic, website, and automation systems.

Canonical DLC architecture now lives in `OneVillage83/Daily-Line-Core`, beginning with `README.md` and `docs/ARCHITECTURE.md`.

### Weather
DDC owns NWS/OpenWeather acquisition, normalized forecast values, forecast issue/update times, source comparison, and immutable forecast snapshots.

Sport repositories derive effects such as baseball outfield wind component or football field-relative passing/kicking exposure.

### Venues / geospatial
DDC owns coordinates, timezone, roof class, generic orientation/bearing, distance calculations, and venue-source provenance. Sport repositories may extend venue metadata with sport-specific geometry.

### Travel / recovery
DDC owns itinerary events, geodesic distance, timezone shift, exact elapsed rest, and travel segment primitives. Sport repositories transform those facts into sport/player/unit fatigue features.

## Temporal contract
Every evidence-backed observation may carry:
- `effective_at`: when the real-world state became true, if known;
- `published_at`: when the source claims it published the information, if known;
- `observed_at`: when The Daily Line observed/fetched it;
- `available_at`: earliest defensible time the pipeline may treat the information as available.

All clocks must be timezone-aware. `available_at` may not be later than `observed_at`. A sport feature snapshot at prediction time `T` may consume only observations satisfying `available_at <= T` and any stricter sport-specific cutoff.

A historical prediction run at `T` must behave as though `T` is literally the present. Later injury/lineup/weather/market information, closing lines, final statistics, and outcomes must be inaccessible to that prediction path.

DLC must preserve the same point-in-time boundary when joining sealed sport outputs with market evidence; it cannot substitute a later quote into an earlier publication package.

## Persistence
V1 uses content-addressed filesystem raw evidence plus normalized contracts that can be persisted by a consuming application. DDC will add its own shared SQLite schema in a later persistence milestone only where central shared storage is operationally required. The contracts are intentionally storage-neutral.

Market history must remain append-only. Repeated numerically identical quotes remain valid evidence because they preserve publication/observation state through time.

## Versioning
Public contract changes require semantic versioning. Provider parser versions and provider schema versions are tracked separately from the DDC package version. Breaking contract changes require explicit migration notes for every consuming sport repository.

A future DDC-to-DLC contract must also be immutable/versioned; DLC must not depend on DDC `main` as a production authority.
