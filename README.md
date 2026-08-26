# Daily Data Core

Daily Data Core is the shared, sport-agnostic data infrastructure for **The Daily Line**.

It exists so Daily-MLB, Daily-NFL, Daily-NCAAF, and future sport engines do not independently rebuild provider transport, immutable evidence, market math, weather acquisition, venue geometry, or neutral travel/rest primitives.

## Current status

- DDC-0 Architecture & ownership contract: **IMPLEMENTED — CERTIFICATION PENDING**
- DDC-1 Runtime / provenance / provider / HTTP foundation: **IMPLEMENTED — CERTIFICATION PENDING**
- DDC-2 Generic odds + market core: **IMPLEMENTED — CERTIFICATION PENDING**
- DDC-3 Weather core: **IMPLEMENTED — CERTIFICATION PENDING**
- DDC-4 Venue / geospatial core: **IMPLEMENTED — CERTIFICATION PENDING**
- DDC-5 Travel / rest core: **IMPLEMENTED — CERTIFICATION PENDING**
- DDC-6 Daily-MLB migration: **BASELINE / COMPATIBILITY PREPARATION IN PROGRESS; NO MLB RUNTIME REPLACEMENT YET**
- DDC-7 Daily-NFL migration: planned after DDC-6 compatibility proof
- DDC-8 Daily-NCAAF integration: planned as the first sport implementation built against certified DDC from day one

The authoritative certification status is `docs/ARCHITECTURE_CERTIFICATION_LOG.md`. Implementation completion is not architecture certification.

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

Production consumers do **not** depend on a moving Git branch. After architecture certification, DDC is released as a versioned pure-Python wheel attached to an immutable release/tag. Each sport repository consumes the exact wheel and compiles it into that repo's normal `--require-hashes` dependency lock.

See `docs/PACKAGE_RELEASE_POLICY.md`.

## Engineering baseline

- Python 3.12
- pytest
- Ruff (`E`, `F`, `I`, `UP`, `B`)
- strict mypy
- reproducible dependency inputs/compiled hash locks
- immutable provider evidence before normalization
- explicit point-in-time semantics
- provider-neutral core contracts

## Current validation requirement

The original DDC-1 through DDC-5 foundation had an earlier direct-execution checkpoint with Python compilation passing and 14 tests passing. The branch has since been expanded/hardened for Daily-MLB compatibility, so that earlier checkpoint is historical evidence only.

Before certification, rerun on the current branch under Python 3.12:

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy .
```

Then generate/install the compiled hash locks and rerun the same gates. See `docs/DDC_LOCAL_VALIDATION_20260826.md` for the exact certification sequence.

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

Daily-MLB's legacy shared implementation remains the regression oracle during DDC-6. DDC-backed adapters may be developed side-by-side, but legacy MLB shared code is not removed until DDC is certified, the immutable package release is hash-locked by MLB, fixture equivalence is proven, a tiny real-provider validation passes, and the MLB quality gates remain green.
