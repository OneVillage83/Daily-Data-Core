# Sport Integration Contracts V1

## Dependency direction
Sport repositories may depend on Daily Data Core. Daily Data Core must never import Daily-MLB, Daily-NFL, Daily-NCAAF, or another sport engine.

```text
Daily-Data-Core <- Daily-MLB
Daily-Data-Core <- Daily-NFL
Daily-Data-Core <- Daily-NCAAF
```

## Daily-MLB
DDC supplies shared HTTP, raw evidence, market acquisition/math, weather acquisition, venue/geospatial, and travel/rest facts.

Daily-MLB retains:
- MLB team/game/player canonical identity;
- MLB Stats API / Statcast / Retrosheet adapters and domain normalization;
- stadium baseball geometry extensions;
- baseball wind interpretation;
- pitcher/lineup/bullpen/player state;
- feature registry, models, simulation, recommendation, settlement.

Migration rule: existing MLB outputs remain regression fixtures until the DDC-backed path is proven equivalent or a deliberate contract change is documented.

## Daily-NFL
DDC supplies generic provider metadata/provenance primitives, raw evidence storage, shared odds/weather/venue/travel facts.

Daily-NFL retains:
- `NFLDatasetKind` or equivalent football dataset taxonomy;
- nflverse/nflreadpy adapter behavior;
- GSIS/team/player/game identity reconciliation;
- football bitemporal/PIT reconstruction and football leakage checks;
- play/drive normalization;
- injury/player/unit/team state;
- football-specific weather/recovery transforms;
- models/simulation/market pricing/recommendations.

Migration rule: generic M3 objects may move behind DDC compatibility imports, but certified football contracts cannot be silently changed.

## Daily-NCAAF
Daily-NCAAF should not copy the existing MLB/NFL shared implementations. Its first production code should consume DDC shared contracts.

Daily-NCAAF retains college-football-specific identity and history, conference membership, roster/player identity, rules, overtime semantics, provider adapters, features, models, and simulation.

## Contract stability
DDC normalized observations expose provider identity, source/raw evidence identity, source timestamps, `available_at`, and parser/schema version where available. Consuming repositories must store enough lineage to reproduce any prediction input snapshot.
