# DDC Local Validation — 2026-08-26

Branch: `feature/ddc-core-bootstrap`
Status: **CURRENT EXPANDED SUITE PENDING FINAL LOCAL QUALITY GATES**

## Earlier direct-execution checkpoint
An earlier DDC-1 through DDC-5 checkpoint was reconstructed in an isolated Python environment and produced:

- Python module compilation (`compileall`): **PASS**;
- regression suite at that checkpoint: **14 passed in 0.15s**.

That result is retained as historical evidence only. It is **not** the final validation result for the current branch because additional compatibility tests and hardening changes were added afterward.

The earlier 14-test checkpoint covered:
- timezone-aware temporal provenance and `available_at <= observed_at` guards;
- content-addressed raw evidence write/idempotence and SHA-256 identity;
- credential query-string redaction;
- American odds conversion, hold, two-way no-vig, and proportional 2+ outcome no-vig;
- market freshness and cross-book consensus/disagreement;
- provider sport-key mapping for MLB/NFL/NCAAF;
- line-aware h2h/spread/total offer grouping;
- NWS wind-speed parsing and sport-neutral weather-source comparison;
- SF-to-LA haversine distance sanity and neutral vector geometry;
- exact rest, travel distance, elapsed travel time, and timezone-shift calculation.

## Hardening added after the 14-test checkpoint
The branch has since been strengthened for DDC-6 compatibility and strict-quality readiness.

### HTTP/transport
- Python 3.12 `type` alias syntax replaces legacy `typing.TypeAlias` usage;
- shared `JsonHttpClient` structural protocol added so provider adapters depend on capability rather than the concrete client;
- retry/redaction/diagnostic code reformatted for configured Ruff rules;
- compatibility regressions added for Retry-After caps, timeout/connection retry behavior, permanent-error behavior, invalid JSON, quota diagnostics, and secret redaction.

### Odds
- exact raw provider response bytes remain available through `ProviderPayload`;
- granular malformed event/bookmaker/market/outcome behavior is regression-tested against mature Daily-MLB expectations;
- requested-sport isolation is enforced so a mismatched provider event cannot leak across sports;
- home/away equality is rejected;
- bookmaker-level `last_update` is preserved;
- **market-level `last_update` is now also preserved**;
- line-aware offers use the market timestamp when available and fall back to bookmaker timestamp;
- multi-sport request construction is regression-tested.

### Weather
- cloud cover and pressure are retained as sport-neutral normalized fields;
- NWS provider-specific descriptive values (`wind_speed_text`, `wind_direction_cardinal`, `forecast_office`) survive in immutable source metadata;
- compatibility regressions preserve the current Daily-MLB normalized weather surface;
- weather values are range/finite validated.

### Venue/travel/provider metadata
- NaN/infinite coordinates, bearings, directions, and recovery values fail closed;
- timezone names are validated through `zoneinfo`;
- optional provider schema/attribution metadata cannot be silently blank;
- source/evidence modules were reformatted for strict lint readiness.

### DDC-6 preparation
- `docs/DDC6_MLB_MIGRATION_PLAN.md` defines the side-by-side migration/equivalence process;
- Daily-MLB has a separate baseline branch/PR containing no production runtime migration yet;
- legacy MLB shared code may not be removed before DDC certification and compatibility evidence.

## Current required final validation
Because the branch changed after the earlier execution checkpoint, all quality gates must be rerun on the current head under Python 3.12:

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy .
```

The current branch also requires compiled hashed locks before architecture certification:

```powershell
python -m piptools compile --resolver=backtracking --generate-hashes --strip-extras --allow-unsafe --output-file=requirements.txt requirements.in
python -m piptools compile --resolver=backtracking --generate-hashes --strip-extras --allow-unsafe --output-file=requirements-dev.txt requirements-dev.in
python -m pip install --require-hashes -r requirements-dev.txt
python -m pytest -q
python -m ruff check .
python -m mypy .
```

## Hosted-CI status
The GitHub Actions workflow exists on `main` and the feature branch, but GitHub is not emitting workflow/status checks for this repository/PR through the available integration. Attempts to use a separate isolated execution runner also failed because that environment cannot resolve external hosts, so it cannot clone the current branch or install missing lint/type-check dependencies.

This is treated as an infrastructure/capability gap, **not** as a green hosted build.

## Certification decision
DDC-0 through DDC-5 remain **IMPLEMENTATION COMPLETE — CERTIFICATION PENDING QUALITY GATES**. The earlier 14-pass checkpoint demonstrates that the original foundation executed successfully, but the current expanded branch is not architecture-certified until the fresh pytest, Ruff, strict-mypy, lock-generation/install, and final conformance review all pass.
