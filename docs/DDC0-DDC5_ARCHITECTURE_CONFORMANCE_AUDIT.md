# DDC-0 through DDC-5 Architecture Conformance Audit

Date: 2026-08-26
Branch: `feature/ddc-core-bootstrap`
Status: **ARCHITECTURE-CERTIFIED**

## Audit scope

This audit compares the implemented Daily Data Core foundation against the governing DDC-0 through DDC-5 roadmap, ownership boundaries, integration contracts, and the Daily-MLB compatibility inventory discovered while preparing DDC-6.

## DDC-0 — Architecture & ownership contract

**Conforms — ARCHITECTURE-CERTIFIED.** Governing architecture, ownership boundaries, decisions, extraction map, implementation roadmap, package policy, and sport integration contracts are versioned in `docs/`.

Key invariant: DDC owns sport-agnostic facts/infrastructure only. Permanent sport identity, sport features, models, simulation, market-value interpretation, Recommendation Gate behavior, and sport settlement remain in consuming sport repositories.

## DDC-1 — Runtime / provenance / provider / HTTP foundation

**Conforms — ARCHITECTURE-CERTIFIED.** Implemented and validated:
- Python 3.12 installable package metadata;
- generic temporal provenance with timezone awareness and `available_at <= observed_at`;
- extensible provider capability/descriptor/acquisition contracts;
- structural JSON HTTP-client protocol plus hardened concrete client;
- exact-byte `ProviderPayload` evidence envelope;
- SHA-256 content-addressed immutable filesystem evidence store;
- retries, Retry-After handling, request diagnostics, quota headers, and safe URL redaction;
- provider schema/attribution validation;
- reproducible SHA-256 dependency locks.

## DDC-2 — Generic odds + market core

**Conforms — ARCHITECTURE-CERTIFIED.** Implemented and validated:
- American implied probability;
- hold calculation;
- two-way and proportional 2+ outcome no-vig math;
- best American price;
- freshness classification;
- cross-book consensus/disagreement;
- configurable The Odds API V4 sport-key adapter;
- immutable event/book/market/outcome snapshots;
- bookmaker-level and market-level provider update timestamps;
- line-aware h2h/spread/total grouping;
- granular malformed provider-element warnings;
- requested-sport isolation and same-participant rejection;
- exact raw response bytes independent from normalized snapshots;
- raw participant strings without DDC-owned permanent team identity.

Freshness invariant: market-level provider timestamps are preferred when present; bookmaker timestamps are the fallback.

Boundary check: DDC does not calculate model edge, recommendation EV, sport-model fair probability, or permanent team/player identity.

## DDC-3 — Weather core

**Conforms — ARCHITECTURE-CERTIFIED.** Implemented and validated:
- NWS point/hourly acquisition;
- OpenWeather One Call hourly acquisition;
- exact raw source evidence;
- forecast point-in-time provenance;
- temperature, humidity, precipitation probability, wind speed/direction;
- cloud cover and pressure;
- immutable provider-specific descriptive metadata;
- source comparison/disagreement;
- value/range/finite validation.

The Daily-MLB compatibility inventory proved that cloud cover, pressure, `wind_speed_text`, `wind_direction_cardinal`, and `forecast_office` must remain available. DDC was extended before certification so those fields are not silently lost.

Boundary check: baseball `blowing_in/out` and football-specific passing/kicking effects remain outside DDC.

## DDC-4 — Venue / geospatial core

**Conforms — ARCHITECTURE-CERTIFIED.** Implemented and validated:
- finite coordinates;
- timezone name;
- neutral roof type;
- finite reference bearing;
- haversine distance;
- initial bearing;
- angular difference;
- neutral longitudinal/cross-vector decomposition;
- fail-closed NaN/infinite geometry validation.

Boundary check: sport-specific venue geometry interpretation remains outside DDC.

## DDC-5 — Travel / rest core

**Conforms — ARCHITECTURE-CERTIFIED.** Implemented and validated:
- neutral travel segment contract;
- travel distance;
- elapsed travel time;
- timezone validation and shift at a specific timestamp;
- exact rest hours;
- finite/nonnegative recovery-context facts.

Boundary check: DDC contains no hard-coded sport fatigue or betting penalty coefficients.

## DDC-6 findings incorporated before certification

Preparing the Daily-MLB regression oracle exposed and resolved these shared-core requirements:
1. market-level odds timestamps must survive normalization;
2. cloud cover and pressure must survive weather normalization;
3. NWS descriptive/source metadata must remain available to compatibility adapters;
4. DDC exact provider bytes and MLB sanitized canonical artifact bytes are distinct evidence/output layers;
5. cross-sport provider events must fail closed;
6. consumer dependency distribution must be immutable and hash-verifiable rather than a moving branch reference.

## Final verification evidence

Hosted GitHub Actions validation on 2026-08-26 used **CPython 3.12.14**.

Permanent CI verifies:
- pinned pip/pip-tools bootstrap;
- `pip install --require-hashes -r requirements-dev.txt`;
- regeneration of both compiled locks with zero diff;
- pytest;
- Ruff;
- strict mypy.

Final result from GitHub Actions run `33009126114`, job `98310500803`:
- hash-locked installation: **PASS**;
- dependency lock drift check: **PASS**;
- pytest: **28 passed in 0.66s**;
- Ruff: **All checks passed**;
- mypy: **Success: no issues found in 11 source files**.

Earlier 14-test execution remains historical evidence only; the certification decision is based on the final expanded 28-test branch plus the reproducibility and static-quality gates above.

## Certification decision

**DDC-0 through DDC-5 are ARCHITECTURE-CERTIFIED.** No unresolved architecture-boundary or quality-gate blocker remains for the shared foundation.

DDC-6 may now advance from baseline preparation into dependency introduction and side-by-side production compatibility adapters. Daily-MLB legacy shared implementations remain in place until cross-path equivalence, tiny real-provider validation, output/database compatibility, credential-safety checks, and Daily-MLB quality gates are all proven.
