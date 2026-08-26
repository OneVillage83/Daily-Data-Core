# Daily Data Core

Daily Data Core is the shared, sport-agnostic acquisition and market-data foundation for **The Daily Line**.

It owns infrastructure that should not be reimplemented separately in Daily-MLB, Daily-NFL, Daily-NCAAF, or future sport engines: provider-neutral acquisition contracts, immutable raw evidence/provenance, HTTP/retry diagnostics, sportsbook market acquisition and normalization, weather acquisition, venue/geospatial primitives, and travel/rest primitives.

Sport repositories own sport ontology, sport-specific normalization, feature engineering, models, simulation, recommendation logic, and sport-specific interpretations of shared data.

## Status

Repository bootstrap in progress. The governing implementation sequence is:

1. DDC-0 — Architecture & ownership contract
2. DDC-1 — Repo/runtime/provenance foundation
3. DDC-2 — Generic Odds + Market Core extracted/generalized from Daily-MLB
4. DDC-3 — Weather Core extracted/generalized from Daily-MLB
5. DDC-4 — Venue/Geospatial Core
6. DDC-5 — Travel/Rest Core foundation
7. DDC-6 — Daily-MLB compatibility adapter + regression contract
8. DDC-7 — Daily-NFL integration contract
9. DDC-8 — Daily-NCAAF integration contract

Implementation must preserve strict point-in-time semantics and immutable source evidence. Shared acquisition is not allowed to leak sport-specific model assumptions into the core.
