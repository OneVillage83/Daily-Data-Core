# AGENTS.md — Daily Data Core

## Mission
Daily Data Core provides sport-agnostic data infrastructure for The Daily Line. It must reduce duplication across sport engines without absorbing sport intelligence or cross-sport product-decision authority.

## Required reading before changes
1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/OWNERSHIP_BOUNDARIES.md`
4. `docs/INTEGRATION_CONTRACTS.md`
5. `docs/IMPLEMENTATION_ROADMAP.md`
6. `docs/PACKAGE_RELEASE_POLICY.md`
7. `docs/ARCHITECTURE_CERTIFICATION_LOG.md`
8. active migration/conformance documents relevant to the task
9. for work touching cross-sport product assembly, `docs/daily_line_core/README.md` and `docs/DAILY_LINE_CORE_CROSS_SYSTEM_ADDENDUM_V1.md`

## Non-negotiable boundaries
- DDC owns shared acquisition, transport, provenance, generic market/weather/venue/travel facts.
- DDC does not own permanent MLB/NFL/NCAAF team/player/game ontology.
- DDC does not own sport-specific features, models, simulation, edge/EV decisions, Recommendation Gate behavior, or sport settlement.
- DDC does not own the All Bets Prediction Scanner, EdgeStack optimizer, cross-sport recommendation ranking, or final Daily Line publication-package assembly.
- **Daily-Line-Core (DLC)** is the planned peer layer for cross-sport decision aggregation/product assembly after sport decisions are sealed. Its architecture is temporarily staged under `docs/daily_line_core/` until `OneVillage83/Daily-Line-Core` is created.
- Exact provider evidence is retained before normalization.
- Point-in-time timestamps are timezone-aware and explicit.
- A consumer migration must preserve its existing public/output contract until a versioned change is intentionally approved.

## DLC handoff boundary
- DDC may provide versioned point-in-time `MarketEvidenceBundle`-style outputs or references to DLC.
- Sport repositories, not DDC, provide sealed fair probabilities, Recommendation Gates, same-event joint information, and sport settlement meaning to DLC.
- DLC may join those sealed authorities for All Bets/EdgeStack/product assembly, but that downstream responsibility must not be implemented inside `daily_data_core`.
- Downstream report/infographic/website/automation consumers should consume the sealed DLC publication package rather than ask DDC to compute recommendations.

## Engineering rules
- Python 3.12.
- pytest, Ruff, and strict mypy are mandatory quality gates.
- Do not mark a milestone architecture-certified merely because code exists.
- Do not hand-edit compiled hash-lock files.
- Dependency inputs are compiled under the pinned Python/pip-tools toolchain.
- Production consumers must use an immutable versioned DDC release artifact through their normal hashed locks; moving Git branches are not production dependency authorities.
- Never commit credentials, `.env`, local databases, generated model artifacts, local raw provider data, or build outputs.

## Migration safety
- Prefer side-by-side compatibility adapters before deleting legacy implementations.
- Treat the consuming sport repo's existing regression suite/output contract as the migration oracle.
- Do not weaken redaction, provenance, freshness, or malformed-provider handling simply to share code.
- DDC-6 Daily-MLB baseline preparation may proceed while DDC certification is pending, but the MLB legacy shared path cannot be removed until DDC is certified and equivalence is proven.
- The presence of staged DLC architecture documents does not change any DDC release/cutover authority.

## Default execution hierarchy
1. Direct, well-scoped repository edits with explicit contracts/tests.
2. User-local execution when the missing capability is environment/provider access.
3. Codex only for broad, execution-heavy loops after contracts are stable.

## Required validation before certification
From the repository root under Python 3.12:

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy .
```

For release/certification, generate and install the compiled hash locks, then rerun the gates.
