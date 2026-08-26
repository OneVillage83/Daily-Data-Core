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
```

## Core domains

### Provider infrastructure
DDC owns provider descriptors, capability metadata, reliability/licensing fields, generic acquisition requests, source payload envelopes, checksums, and immutable raw storage.

Dataset keys are strings rather than a global sport enum. This permits shared keys such as `market.odds` and `weather.hourly_forecast` while allowing a sport repository adapter to declare a scoped key such as `nfl.play_by_play` without making DDC understand football ontology.

### Markets / odds
DDC owns odds conversion, hold/no-vig math, quote freshness, normalized bookmaker observations, line-aware grouping, consensus statistics, disagreement measures, and provider adapters for shared sportsbook sources.

DDC does not decide whether an outcome is a good bet, estimate a football/baseball win probability, or reconcile provider participant names to permanent sport identity.

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

## Persistence
V1 uses content-addressed filesystem raw evidence plus normalized contracts that can be persisted by a consuming application. DDC will add its own shared SQLite schema in a later persistence milestone only where central shared storage is operationally required. The contracts are intentionally storage-neutral.

## Versioning
Public contract changes require semantic versioning. Provider parser versions and provider schema versions are tracked separately from the DDC package version. Breaking contract changes require explicit migration notes for every consuming sport repository.
