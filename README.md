# Daily Data Core

Daily Data Core is the shared, sport-agnostic data infrastructure for **The Daily Line**.

It exists so Daily-MLB, Daily-NFL, Daily-NCAAF, and future sport engines do not independently rebuild provider transport, immutable evidence, market math, weather acquisition, venue geometry, or neutral travel/rest primitives.

## Current status

Latest, 2026-09-17 (America/Los_Angeles): the cross-sport product architecture now explicitly includes a planned **Daily-Line-Core (DLC)** peer layer downstream of sealed sport decision packages and DDC market evidence. DLC will own the All Bets Prediction Scanner, EdgeStack Parlay Optimizer, cross-sport product assembly, and sealed `DailyLinePublicationPackage`. This does **not** transfer DLC product logic into DDC; the architecture is temporarily staged under `docs/daily_line_core/` until `OneVillage83/Daily-Line-Core` is created. Repository extraction is tracked in issue #5.

Latest DDC package/release work, 2026-09-10T19:14:49-07:00 (America/Los_Angeles): TDL-03B-FINAL-B resolves the prepublication ordering in `docs/PACKAGE_RELEASE_POLICY.md`. Stage A certifies exact final artifact bytes and an inactive consumer without a public URL; Stage B verifies publication transport and the production lock only after separate owner approval. Final 0.2.2 bytes remain unchanged and unpublished. Private certification of the new inactive consumer remains required; no cutover.

Earlier DDC release/migration checkpoints remain documented in the referenced handoff files and certification log.

- DDC-0 Architecture & ownership contract: **ARCHITECTURE-CERTIFIED**
- DDC-1 Runtime / provenance / provider / HTTP foundation: **ARCHITECTURE-CERTIFIED**
- DDC-2 Generic odds + market core: **ARCHITECTURE-CERTIFIED**
- DDC-3 Weather core: **ARCHITECTURE-CERTIFIED**
- DDC-4 Venue / geospatial core: **ARCHITECTURE-CERTIFIED**
- DDC-5 Travel / rest core: **ARCHITECTURE-CERTIFIED**
- DDC-6 Daily-MLB migration: **BLOCKED — current-consumer release admission exposes provider/evidence gaps; safe core repairs prepared, consumer not switched**
- DDC-7 Daily-NFL migration: planned after DDC-6 compatibility proof
- DDC-8 Daily-NCAAF integration: planned as the first sport implementation built against certified DDC from day one

The authoritative DDC milestone record is `docs/ARCHITECTURE_CERTIFICATION_LOG.md`.

## Ownership rule

DDC owns shared facts and shared acquisition infrastructure. Sport repositories own sport intelligence. Daily-Line-Core is a separate downstream cross-sport product layer.

### DDC owns
- HTTP transport, retries, diagnostics, and safe URL reporting;
- generic provider metadata/capability contracts;
- immutable exact-byte raw evidence and SHA-256 identity;
- temporal/provenance clocks;
- sportsbook acquisition and generic market mathematics;
- full market-history evidence and sport-agnostic Line Intelligence derivations;
- weather acquisition and normalized meteorological facts;
- venue/geospatial primitives;
- travel, timezone-shift, and exact-rest primitives;
- versioned point-in-time market-evidence handoffs for consumers.

### Sport repositories retain
- permanent sport-specific team/player/game identity;
- sport-specific state/features;
- sport-specific interpretation of shared facts;
- model training/inference;
- Unified Ensemble / TDL Unified Line production;
- simulation;
- sport-specific Line Timing Models;
- market-residual / market-aware decision models;
- fair-price/value/EV decisions;
- Recommendation Gate behavior;
- settlement and sport-specific reporting logic;
- sealed sport decision packages for downstream product assembly.

### Daily-Line-Core will own
- admission of sealed sport decision packages;
- joining those packages to DDC point-in-time market evidence;
- the cross-sport **All Bets Prediction Scanner**;
- the **EdgeStack Parlay Optimizer**;
- cross-game and cross-sport 2–5 leg combination optimization;
- final product recommendation/index assembly;
- immutable `DailyLinePublicationPackage` sealing;
- handoff contracts to report, infographic, website, and downstream automation consumers.

DLC is a planned peer repository, not a DDC module. The current staging architecture is under `docs/daily_line_core/` only until `OneVillage83/Daily-Line-Core` is physically created.

Example: DDC can expose wind direction, speed, and a venue reference bearing. Daily-MLB decides whether that means `blowing_out`; Daily-NFL/NCAAF derive their own football-specific field/wind effects. Once those sport decisions are sealed, DLC may aggregate them into cross-sport product outputs without reinterpreting the raw weather itself.

## Unified forecasting architecture

The cross-sport production target is a **dynamic learned mixture-of-experts** rather than a single universal model. Sport repositories preserve rating, statistical, Bayesian, supervised-ML, simulation, specialist, component-expert, and future model families in a governed registry. Only signal that earns forward point-in-time evidence receives production influence.

The calibrated independent result is the **TDL Unified Line**. Sportsbook, exchange, prediction-market, line-movement, and closing-line evidence are kept out of that independent forecast path and enter only the separately labeled Market Intelligence / Decision layer.

DDC supports that architecture by preserving market timelines, PIT provenance, and evaluation evidence; it does not become the universal sports predictor.

After individual sports finish prediction/decision and seal their outputs, DLC becomes the cross-sport product assembly layer.

See:
- `docs/TDL_UNIFIED_FORECASTING_ARCHITECTURE_V1.md`
- `docs/LINE_INTELLIGENCE_AND_TIMING_V1.md`
- `docs/MODEL_REGISTRY_EVALUATION_NO_CONTAMINATION_V1.md`
- `docs/daily_line_core/README.md`
- `docs/daily_line_core/DLC_ARCHITECTURE_V1.md`
- `docs/daily_line_core/EDGESTACK_PARLAY_OPTIMIZER_V1.md`

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
- `docs/TDL_UNIFIED_FORECASTING_ARCHITECTURE_V1.md`
- `docs/LINE_INTELLIGENCE_AND_TIMING_V1.md`
- `docs/MODEL_REGISTRY_EVALUATION_NO_CONTAMINATION_V1.md`
- `docs/SOURCE_EXTRACTION_MAP.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/PACKAGE_RELEASE_POLICY.md`
- `docs/DDC6_MLB_MIGRATION_PLAN.md`
- `docs/DDC0-DDC5_ARCHITECTURE_CONFORMANCE_AUDIT.md`
- `docs/ARCHITECTURE_CERTIFICATION_LOG.md`
- `docs/DDC_LOCAL_VALIDATION_20260826.md`
- `docs/daily_line_core/README.md` — temporary DLC staging index
- `docs/daily_line_core/DLC_ARCHITECTURE_V1.md` — planned DLC system architecture
- `docs/daily_line_core/EDGESTACK_PARLAY_OPTIMIZER_V1.md` — planned DLC EdgeStack architecture
- `docs/daily_line_core/DLC_IMPLEMENTATION_HANDOFF_V1.md` — future Bridge/Codex implementation sequence
- `docs/daily_line_core/DLC_REPOSITORY_BOOTSTRAP.md` — extraction plan for `OneVillage83/Daily-Line-Core`

## Consumer migration safety

Daily-MLB's legacy shared implementation remains the regression oracle during DDC-6. DDC-backed adapters may be developed side-by-side, but legacy MLB shared code is not removed until the immutable DDC package release is hash-locked by MLB, fixture equivalence is proven, a tiny real-provider validation passes, artifact/database contracts remain compatible, credential-safety checks pass, and the MLB quality gates remain green.

The DLC architecture addition does not change the current DDC-6 release/cutover status and grants no new production authority.
