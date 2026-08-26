# Daily Data Core

Daily Data Core is the shared, sport-agnostic acquisition and market-data foundation for **The Daily Line**.

It owns infrastructure that should not be reimplemented separately in Daily-MLB, Daily-NFL, Daily-NCAAF, or future sport engines: provider-neutral acquisition contracts, immutable raw evidence/provenance, HTTP/retry diagnostics, sportsbook market acquisition and normalization, weather acquisition, venue/geospatial primitives, and travel/rest primitives.

Sport repositories own sport ontology, sport-specific normalization, feature engineering, models, simulation, recommendation logic, and sport-specific interpretations of shared data.

## Current implementation status

- DDC-0 Architecture & ownership contract: implemented; certification pending final quality gates
- DDC-1 Repo/runtime/provenance foundation: implemented; certification pending final quality gates
- DDC-2 Generic Odds + Market Core: implemented; certification pending final quality gates
- DDC-3 Weather Core: implemented; certification pending final quality gates
- DDC-4 Venue/Geospatial Core: implemented; certification pending final quality gates
- DDC-5 Travel/Rest Core foundation: implemented; certification pending final quality gates
- DDC-6 Daily-MLB compatibility migration: next after core certification
- DDC-7 Daily-NFL integration migration: follows MLB compatibility proof
- DDC-8 Daily-NCAAF integration: use DDC from first implementation milestone

Final direct execution of the hardened DDC-1 through DDC-5 branch passes Python compilation and **14 regression tests**. Ruff/strict mypy remain required before certification; hosted GitHub checks are currently not being emitted and that gap is documented in `docs/DDC_LOCAL_VALIDATION_20260826.md`.

The governing documents live in `docs/`. The active bootstrap work is reviewed in draft PR #1.

## Engineering baseline

- Python 3.12
- immutable raw evidence before normalization
- explicit source and temporal provenance
- point-in-time `available_at` semantics
- all-book market snapshots retained beneath derived consensus
- pytest / Ruff / strict mypy quality gates
- sport-specific identity/model interpretation prohibited from the shared core

## Local quality gates

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "pip==26.1.2" "pip-tools==7.6.0"
python -m pip install -r requirements-dev.in
python -m pytest -q
python -m ruff check .
python -m mypy
```

Compiled hashed dependency locks will be generated and committed as part of DDC-1 certification; do not hand-edit them.
