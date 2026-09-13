# Daily Data Core Implementation Roadmap V1

## DDC-0 — Architecture & ownership contract
Deliverables: architecture, ownership boundaries, extraction map, integration contracts, decisions. Exit: shared-vs-sport boundary is explicit and reviewable.

## DDC-1 — Repo/runtime/provenance foundation
Deliverables: Python 3.12 package, quality gates, temporal provenance, provider contracts, immutable raw evidence store, HTTP diagnostics/retry client. Exit: generic provider payload can be acquired and content-addressed without sport knowledge.

## DDC-2 — Generic Odds + Market Core
Deliverables: market contracts, American odds math, no-vig/hold, freshness, line-aware book observations, consensus/disagreement, The Odds API shared adapter, configurable sport keys. Exit: MLB/NFL/NCAAF odds payloads can be represented by one shared contract without participant canonicalization.

## DDC-3 — Weather Core
Deliverables: weather forecast contract, NWS adapter, OpenWeather adapter contract/client, source comparison, forecast timestamp provenance. Exit: outdoor forecast acquisition works independently of sport interpretation.

## DDC-4 — Venue/Geospatial Core
Deliverables: venue contract, coordinates, roof type, timezone/orientation fields, haversine distance, bearing helpers. Exit: sport repos can reference shared venue facts and calculate field-relative transforms themselves.

## DDC-5 — Travel/Rest Core foundation
Deliverables: itinerary/travel segment contracts, distance, timezone shift, elapsed rest, recovery-context primitives. Exit: neutral travel/rest facts are reproducible without embedding sport fatigue coefficients.

## DDC-6 — Daily-MLB compatibility adapter + regression contract
Work occurs primarily in Daily-MLB. Replace direct ownership of shared HTTP/raw evidence/odds/weather primitives with DDC calls while preserving current outputs and all-book snapshot behavior. MLB-specific wind/baseball interpretation stays in Daily-MLB.

## DDC-7 — Daily-NFL integration contract
Work occurs primarily in Daily-NFL. M3 generic raw-store/provider metadata should converge on DDC while NFL dataset kinds, nflverse adapter, football normalization, reconciliation, PIT engine, and football features stay in Daily-NFL. M8 and M13 consume DDC weather/travel/odds contracts rather than duplicating acquisition.

## DDC-8 — Daily-NCAAF integration contract
Daily-NCAAF begins against DDC from its first implementation milestone. College-football provider identity, conference/team history, rules, features, and models remain local; shared odds/weather/venue/travel and generic provider/provenance infrastructure come from DDC.

## DDC-9 — Line Intelligence Core (future, after current migration contracts)
Deliverables: append-only multi-source market history; sportsbook/exchange/prediction-market source typing; reusable open/current/consensus/close views; sharp/soft grouping contracts; movement delta/velocity/acceleration primitives; book dispersion; prediction-market divergence; time-to-start normalization; price and line CLV reference contracts; point-in-time market reconstruction helpers.

DDC-9 does **not** implement sport-specific Line Timing Models, the TDL Unified Line, market-residual decision models, EV, or the Recommendation Gate. Those remain in sport repositories.

Exit: any sport consumer can reconstruct the eligible market state at timestamp `T`, compare a sport-owned TDL fair line to opening/current/consensus evidence, and later attach clearly defined closing references for evaluation without leaking future data into the prediction context.

## DDC-10 — Cross-sport forecast-evaluation support contracts (future)
Deliverables: storage-neutral schemas/keys needed to join immutable sport-owned prediction records to DDC market evidence for evaluation; standardized time-horizon buckets; shared CLV calculation primitives where they are truly sport-agnostic; validation hooks for `available_at` cutoff enforcement and closing-line firewalls.

DDC-10 must not centralize sport model training, ensemble weighting, calibration, specialist discovery, or promotion logic. The goal is reproducible cross-sport evidence plumbing, not a universal model service.

Exit: Daily-MLB, Daily-NFL, Daily-NCAAF, and future sports can produce comparable PIT/CLV evaluation packets while retaining sport-owned model semantics.

## Certification sequence
Each DDC milestone requires:
1. architecture conformance review;
2. unit tests;
3. Ruff;
4. strict mypy;
5. small real-provider validation where applicable;
6. compatibility validation before a sport repository deletes legacy shared code;
7. for DDC-9/DDC-10, explicit point-in-time replay tests proving no closing/future-market leakage.
