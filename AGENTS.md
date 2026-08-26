# Daily Data Core Agent Policy

## Mission
Daily Data Core is the sport-agnostic shared data foundation for The Daily Line. It owns shared acquisition, provenance, market, weather, venue/geospatial, and travel/rest primitives. It must not accumulate MLB-, NFL-, NCAAF-, or other sport-specific modeling logic.

## Non-negotiable boundaries
- Preserve immutable raw source evidence before normalization.
- Preserve provider, parser/schema version, source URI, and temporal provenance.
- Point-in-time safety is mandatory: shared snapshots must support defensible `available_at` semantics.
- Provider IDs are external identities, not permanent cross-sport canonical identities.
- Market math is shared; sport-specific participant reconciliation and model pricing live in sport repositories.
- Weather acquisition is shared; sport-specific weather effects live in sport repositories.
- Venue geography/orientation is shared; sport-specific field/play interpretation lives in sport repositories.
- Travel distance, timezone shift, itinerary, and exact rest intervals are shared; sport-specific fatigue transforms live in sport repositories.
- Do not copy a shared subsystem into a sport repository when an explicit Data Core contract can serve it.

## Engineering baseline
- Python 3.12.
- Typed public contracts.
- Deterministic pure functions where practical.
- pytest, Ruff, and strict mypy gates.
- No committed secrets, local databases, provider payloads, or generated artifacts.
- Runtime dependency inputs and compiled locks remain explicit and reproducible.

## Change policy
Any new feature must answer two questions before implementation:
1. Is this fact/operation meaningful across multiple sports without knowing sport rules? If yes, Data Core may own it.
2. Does it interpret the fact through a sport rule, feature, model, or betting thesis? If yes, the sport repository owns it.

Cross-repository compatibility changes must be documented in `docs/INTEGRATION_CONTRACTS.md` and remain backward-compatible until the consuming sport repository is migrated.
