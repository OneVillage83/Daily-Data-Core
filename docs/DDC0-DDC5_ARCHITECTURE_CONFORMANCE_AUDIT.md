# DDC-0 through DDC-5 Architecture Conformance Audit

Date: 2026-08-26
Branch: `feature/ddc-core-bootstrap`
Status: **IMPLEMENTATION COMPLETE — CERTIFICATION PENDING QUALITY GATES**

## Audit scope
This audit compares the implemented Daily Data Core foundation against the governing DDC-0 through DDC-5 roadmap, ownership boundaries, integration contracts, and the Daily-MLB compatibility inventory discovered while preparing DDC-6.

## DDC-0 — Architecture & ownership contract
**Conforms.** Governing architecture, ownership boundaries, decisions, extraction map, implementation roadmap, and sport integration contracts are versioned in `docs/`.

Key invariant verified: DDC owns sport-agnostic facts/infrastructure only. Permanent sport identity, sport features, models, simulation, market-value interpretation, Recommendation Gate behavior, and sport settlement remain in consuming sport repositories.

## DDC-1 — Repo/runtime/provenance foundation
**Conforms, certification pending.** Implemented:
- Python 3.12 installable package metadata;
- generic temporal provenance with timezone awareness and `available_at <= observed_at`;
- extensible provider capability/descriptor/acquisition contracts;
- structural JSON HTTP-client protocol plus hardened concrete HTTP client;
- exact-byte `ProviderPayload` evidence envelope;
- SHA-256 content-addressed immutable filesystem evidence store;
- shared HTTP retries, Retry-After handling, diagnostics, quota headers, and safe URL redaction;
- provider schema/attribution validation;
- pytest/Ruff/strict-mypy configuration.

Remaining certification items:
- execute the current expanded pytest suite successfully;
- execute Ruff and strict mypy successfully;
- generate/validate compiled dependency locks under Python 3.12.

## DDC-2 — Generic Odds + Market Core
**Conforms, certification pending.** Implemented:
- American implied probability;
- hold calculation;
- two-way and proportional 2+ outcome no-vig math;
- best American price;
- freshness classification;
- cross-book two-way consensus and disagreement;
- configurable The Odds API V4 sport-key adapter;
- immutable book/market/outcome snapshots;
- bookmaker-level and market-level provider update timestamps;
- line-aware h2h/spread/total grouping;
- granular malformed provider-element warnings;
- requested-sport isolation and same-participant event rejection;
- exact raw response bytes retained independently of normalized snapshots;
- raw participant strings retained without DDC canonical team identity.

Freshness invariant: where a market-level provider timestamp exists, normalized offers retain that more specific timestamp; bookmaker timestamp is the fallback.

Boundary check: DDC does not calculate model edge, EV recommendation, sport fair probability, or permanent team/player identity.

## DDC-3 — Weather Core
**Conforms, certification pending.** Implemented:
- NWS point/hourly acquisition;
- OpenWeather One Call 3.0 hourly acquisition;
- exact raw source evidence;
- forecast snapshot timestamps/provenance;
- temperature, humidity, precipitation probability, wind speed/direction normalization;
- cloud-cover and pressure normalization;
- immutable provider-specific descriptive metadata for fields that do not belong in the cross-provider numeric schema;
- source comparison/disagreement;
- value/range and temporal validation.

DDC-6 compatibility inventory explicitly verified that the existing MLB OpenWeather path exposes cloud cover/pressure and the NWS path exposes `wind_speed_text`, `wind_direction_cardinal`, and `forecast_office`; the DDC contract was extended before certification so those values are not silently lost in migration.

Boundary check: baseball `blowing_in/out` and football passing/kicking effects are absent from DDC.

## DDC-4 — Venue/Geospatial Core
**Conforms, certification pending.** Implemented:
- finite validated coordinates;
- timezone name;
- generic roof type;
- finite generic reference bearing;
- haversine distance;
- initial bearing;
- angular difference;
- neutral longitudinal/cross-vector decomposition;
- NaN/infinite geometry inputs fail closed.

Boundary check: sport-specific venue geometry semantics remain outside DDC.

## DDC-5 — Travel/Rest Core
**Conforms, certification pending.** Implemented:
- neutral travel segment contract;
- travel distance;
- elapsed travel time;
- timezone validation and timezone shift at a specific timestamp;
- exact rest hours;
- finite/nonnegative recovery-context facts.

Boundary check: no hard-coded sport fatigue or betting penalty coefficients exist in DDC.

## DDC-6 pre-migration findings that affected core certification
Preparing the Daily-MLB regression oracle uncovered several shared-core requirements before any MLB runtime migration was allowed:
1. market-level odds timestamps must survive DDC normalization;
2. cloud cover and pressure must survive shared weather normalization;
3. NWS descriptive/source metadata must remain available to the MLB compatibility adapter;
4. exact provider bytes in DDC and sanitized canonical MLB artifact bytes are distinct evidence/output layers and must not be conflated;
5. cross-sport provider events must fail closed rather than entering the wrong consumer.

These findings are incorporated into the current DDC branch and regression suite.

## Verification evidence
An earlier foundation checkpoint produced:
- Python compilation: PASS;
- regression tests: **14 passed**.

That checkpoint predates the DDC-6 compatibility expansion and is historical evidence only. The current branch contains additional production hardening and compatibility tests, so a fresh final execution is required.

Manual architecture/static review has additionally identified and corrected:
- callable default arguments likely to violate Ruff B008;
- legacy `typing.TypeAlias` usage under Python 3.12/UP rules;
- unused imports in new compatibility tests;
- long lines in core modules under the configured Ruff line length;
- dropped market-level odds timestamp provenance;
- dropped MLB weather compatibility fields;
- non-finite geospatial input acceptance.

Hosted GitHub workflow/status checks are currently not being emitted despite the workflow existing on `main` and the feature branch. The isolated execution runner also cannot resolve external hosts. These are infrastructure/capability gaps, not passes.

## Certification decision
DDC-0 through DDC-5 are **not yet ARCHITECTURE-CERTIFIED**. Implementation is sufficiently complete to enter final quality-gate validation, but certification requires successful current-head pytest + Ruff + strict-mypy execution, reproducible hashed dependency locks, and final architecture review.

DDC-6 consumer migration may continue through documentation, baseline freezing, and side-by-side adapter preparation, but it must not delete Daily-MLB legacy shared implementations until DDC-0 through DDC-5 certification is complete and MLB regression equivalence is proven.
