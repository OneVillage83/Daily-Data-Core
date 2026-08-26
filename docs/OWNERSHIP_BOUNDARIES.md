# Daily Data Core Ownership Boundaries

## Principle
If a fact can be acquired/normalized once and interpreted differently by multiple sports, DDC should usually own the fact while the sport owns the interpretation.

## DDC owns
- shared HTTP/retry/diagnostic primitives;
- provider capability/licensing metadata;
- exact immutable raw response evidence;
- generic temporal provenance;
- generic sportsbook quote acquisition and math;
- quote/book/market timestamps and freshness primitives;
- weather forecast acquisition and normalized meteorological facts;
- generic venue coordinates/timezone/roof/reference geometry;
- neutral travel distance/timezone/rest facts;
- versioned shared-package release artifacts used by multiple sport repositories.

## DDC does not own
- MLB/NFL/NCAAF permanent team/player/game identity;
- lineup/depth/injury interpretation specific to a sport;
- baseball field/weather performance semantics;
- football field/weather passing/kicking semantics;
- sport-specific feature registries/state engines;
- sport model training/inference;
- simulation engines;
- model fair prices, edge/EV decisions, Recommendation Gate behavior;
- sport settlement/report interpretation.

## Identity boundary
A shared provider may call the same participant differently across products or over time. DDC preserves provider participant/event identity and raw values. Each sport repository maps those to its own canonical ontology/crosswalks.

DDC must not become a hidden universal sports-identity database merely because its odds adapter sees all sports.

## Evidence boundary
DDC exact-byte evidence is the internal source-evidence layer. A consumer may additionally maintain sanitized/canonical artifacts for its existing output contract. Those layers are distinct and both may be required during migration.

## Weather boundary
Shared schema includes neutral facts such as wind speed/direction, cloud cover, and pressure when supplied. Provider-specific descriptive fields may be carried in immutable source metadata. A sport-specific classification such as MLB `blowing_out` remains local.

## Market boundary
Shared schema/math includes generic quotes, lines, implied probability, no-vig, hold, quote freshness, and disagreement/consensus. Market-level provider timestamps are preferred for quote-specific freshness when available, with bookmaker-level timestamps as fallback. Model-derived fair price/edge/EV remain sport/model responsibilities.

## Package boundary
DDC source ownership does not imply consumers follow DDC `main`. Production consumers use explicit immutable released wheel versions through their own hashed dependency locks. This lets a sport upgrade DDC deliberately and regression-test the transition rather than inheriting every core commit immediately.

## Migration boundary
A legacy sport-local shared implementation is not removed merely because an equivalent DDC module exists. The consuming sport's current tests/output contract remain authoritative until the DDC-backed path is certified regression-equivalent.
