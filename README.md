# Daily Data Core

Daily Data Core is the shared, sport-agnostic data infrastructure for **The Daily Line**.

It exists so Daily-MLB, Daily-NFL, Daily-NCAAF, and future sport engines do not independently rebuild provider transport, immutable evidence, market math, weather acquisition, venue geometry, or neutral travel/rest primitives.

## Current status

- DDC-0 Architecture & ownership contract: **ARCHITECTURE-CERTIFIED**
- DDC-1 Runtime / provenance / provider / HTTP foundation: **ARCHITECTURE-CERTIFIED**
- DDC-2 Generic odds + market core: **ARCHITECTURE-CERTIFIED**
- DDC-3 Weather core: **ARCHITECTURE-CERTIFIED**
- DDC-4 Venue / geospatial core: **ARCHITECTURE-CERTIFIED**
- DDC-5 Travel / rest core: **ARCHITECTURE-CERTIFIED**
- DDC-6 Daily-MLB migration: **IN PROGRESS — baseline frozen; package release and side-by-side runtime migration next**
- DDC-7 Daily-NFL migration: planned after DDC-6 compatibility proof
- DDC-8 Daily-NCAAF integration: planned as the first sport implementation built against certified DDC from day one

The authoritative milestone record is `docs/ARCHITECTURE_CERTIFICATION_LOG.md`.

## Ownership rule

DDC owns shared facts and shared acquisition infrastructure. Sport repositories own sport intelligence.

### DDC owns
- HTTP transport, retries, diagnostics, and safe URL reporting;
- generic provider metadata/capability contracts;
- immutable exact-byte raw evidence and SHA-256 identity;
- temporal/provenance clocks;
- sportsbook acquisition and generic market mathematics;
- weather acquisition and normalized meteorological facts;
- venue/geospatial primitives;
- travel, timezone-shift, and exact-rest primitives.

### Sport repositories retain
- permanent sport-specific team/player/game identity;
- sport-specific state/features;
- sport-specific interpretation of shared facts;
- model training/inference;
- simulation;
- fair-price/value/EV decisions;
- Recommendation Gate behavior;
- settlement and sport-specific reporting logic.

Example: DDC can expose wind direction, speed, and a venue reference bearing. Daily-MLB decides whether that means `blowing_out`; Daily-NFL/NCAAF derive their own football-specific field/wind effects.

## Package/release rule

Production consumers do **not** depend on a moving Git branch. Certified DDC is distributed as a versioned pure-Python wheel attached to an immutable release/tag. Each sport repository consumes the exact wheel and compiles it into that repo's normal `--require-hashes` dependency lock.

See `docs/PACKAGE_RELEASE_POLICY.md`.

## Engineering baseline

- Python 3.12
- pytest
- Ruff (`E`, `F`, `I`, `UP`, `B`)
- strict mypy
- reproducible SHA-256 dependency locks
- immutable provider evidence before normalization
- explicit point-in-time semantics
- provider-neutral core contracts

## Certified validation

Final hosted certification ran under **CPython 3.12.14** with the permanent CI contract:

1. pinned pip/pip-tools bootstrap;
2. `pip install --require-hashes -r requirements-dev.txt`;
3. dependency-lock regeneration with zero-diff enforcement;
4. pytest;
5. Ruff;
6. strict mypy.

Certification result:
- hash-locked install: **PASS**;
- lock-drift verification: **PASS**;
- pytest: **28 passed**;
- Ruff: **PASS**;
- strict mypy: **PASS — 11 source files**.

See `docs/DDC_LOCAL_VALIDATION_20260826.md` and `docs/DDC0-DDC5_ARCHITECTURE_CONFORMANCE_AUDIT.md`.

## Governing documents

- `docs/ARCHITECTURE.md`
- `docs/OWNERSHIP_BOUNDARIES.md`
- `docs/INTEGRATION_CONTRACTS.md`
- `docs/SOURCE_EXTRACTION_MAP.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/PACKAGE_RELEASE_POLICY.md`
- `docs/DDC6_MLB_MIGRATION_PLAN.md`
- `docs/DDC0-DDC5_ARCHITECTURE_CONFORMANCE_AUDIT.md`
- `docs/ARCHITECTURE_CERTIFICATION_LOG.md`
- `docs/DDC_LOCAL_VALIDATION_20260826.md`

## Consumer migration safety

Daily-MLB's legacy shared implementation remains the regression oracle during DDC-6. DDC-backed adapters may be developed side-by-side, but legacy MLB shared code is not removed until the immutable DDC package release is hash-locked by MLB, fixture equivalence is proven, a tiny real-provider validation passes, artifact/database contracts remain compatible, credential-safety checks pass, and the MLB quality gates remain green.
