# Daily Data Core Integration Contracts

Current optional quote-label clarification and parser-v3 successor:
`TDL03F_OPTIONAL_DESCRIPTION_20260910.md`. Exactly empty/absent/null normalize to
None; whitespace-only/non-string remain invalid; raw bytes and subject identity
requirements remain unchanged. Candidate 0.2.2.dev1 is unreleased.

Updated: 2026-09-17 (America/Los_Angeles).

Unreleased v2 acquisition/forecast evolution and migration notes:
[LOSSLESS_ACQUISITION_V2.md](LOSSLESS_ACQUISITION_V2.md).

## Core rule
DDC normalizes shared facts. A sport consumer maps those facts into its own canonical identity/state/features.

After a sport has produced a sealed prediction/decision package, **Daily-Line-Core (DLC)** may consume that sport package together with sealed DDC market evidence for cross-sport product assembly. DDC remains evidence authority; DLC is a downstream product/decision assembly peer.

## Shared provenance contract
Every external-data integration must retain enough lineage to answer:
- which provider produced the source;
- which immutable raw evidence object backs the normalized record;
- when DDC observed it;
- when it was defensibly available;
- provider/effective/published time where available;
- parser/schema version where relevant.

## Odds consumer contract
DDC provides:
- provider sport/event identity;
- raw participant names/IDs as supplied;
- commence time;
- bookmaker identity;
- bookmaker-level update time;
- market-level update time;
- market/outcome/line/price facts;
- exact raw evidence;
- acquisition diagnostics/quota metadata;
- generic implied/no-vig/hold/freshness/consensus primitives.

DDC rejects cross-sport events whose returned sport key does not match the requested sport. For quote freshness, a market-level timestamp is more specific and is preferred when present; bookmaker timestamp is fallback evidence.

The sport repo resolves provider participants/events into its permanent canonical identity before sport features/models use the record.

## Sport -> DLC `SportDecisionPackage` contract

Daily-MLB, Daily-NFL, Daily-NCAAF, and future Daily-* repositories should eventually expose a sealed, versioned `SportDecisionPackage` (or equivalent contract) for DLC.

Minimum conceptual content:

- package ID/version/digest;
- sport/league/slate scope;
- prediction timestamp;
- data cutoff timestamp;
- model/config/release provenance;
- sport-canonical event/market refs;
- TDL Unified Line outputs for every supported target;
- fair probabilities/fair lines;
- uncertainty/calibration metadata;
- sport market-aware decision outputs where certified;
- Recommendation Gate state/reason per supported market;
- publication-safe reason/evidence refs;
- settlement rule/version;
- same-event joint-distribution/simulation refs when required for correlated EdgeStacks;
- explicit unsupported/degraded market declarations.

DLC may consume but must not silently alter the sport's probability or Recommendation Gate authority.

## DDC -> DLC `MarketEvidenceBundle` contract

DDC should eventually expose or seal a versioned market-evidence bundle suitable for DLC product snapshots.

Minimum conceptual content:

- provider/venue identity;
- provider sport/event/market refs;
- line/threshold/outcome/price;
- bookmaker/exchange/prediction-market timestamps;
- observed/available timestamps;
- implied probability;
- no-vig/hold/consensus refs where meaningful;
- quote freshness;
- market-history/Line-Intelligence refs;
- fee/execution metadata where provider-supported;
- immutable evidence/digest refs.

The DDC bundle does **not** contain DLC recommendations, EdgeStack rankings, sport fair probabilities, or sport Recommendation Gates.

## DLC join/reconciliation contract

DLC must join sport-canonical markets with DDC provider-market evidence through explicit versioned mapping/identity contracts.

Requirements:

- no display-name-only identity inference;
- every joined quote retains DDC provenance;
- every joined model/gate result retains sport provenance;
- point-in-time cutoffs must be compatible;
- stale/incompatible quotes fail closed;
- later market data cannot replace an earlier publication snapshot;
- missing mapping yields unsupported/degraded output rather than guessed reconciliation.

## DLC output contract

DLC's principal output is a sealed immutable `DailyLinePublicationPackage` containing or referencing:

- admitted sport decision package IDs;
- DDC market evidence bundle IDs;
- cross-sport `AllBetsSnapshot`;
- product recommendation/top-pick index;
- EdgeStack catalog (`CORE`, `VALUE`, `UPSIDE`);
- report-safe claims;
- infographic-safe claims;
- website views/refs;
- automation-safe publishable fact refs;
- quality/degradation state;
- full provenance and supersession lineage.

The report, infographic, website, and The-Daily-Line-Automation consume the sealed DLC package. They do not recompute sport probabilities, Recommendation Gates, or EdgeStack rankings.

## EdgeStack provider-quote contract

EdgeStack is owned by DLC, but provider quote evidence must preserve the same PIT/provenance discipline as other market evidence.

For Kalshi Combo/RFQ or supported sportsbook parlay quotes, the normalized quote should preserve:

- candidate/leg-set identity;
- provider quote ID where available;
- quoted multiplier/price;
- quote timestamp;
- expiry/freshness;
- fee/execution metadata where available;
- provider response/evidence reference;
- correlation-adjustment diagnostics if inferable, without assuming the provider formula.

The actual combo quote is authoritative market evidence for comparison; multiplying standalone prices is diagnostic only.

## Weather consumer contract
DDC provides sport-neutral normalized facts:
- forecast target time;
- observation/availability/provider-update timestamps;
- temperature;
- humidity;
- precipitation probability;
- wind speed/direction;
- short forecast;
- optional cloud cover;
- optional pressure;
- immutable provider-specific descriptive metadata when a consumer must preserve a provider field that is not universal;
- exact raw evidence.

The sport repo derives sport semantics. Examples:
- MLB may derive field-relative blowing-in/out components;
- NFL/NCAAF may derive field-relative passing/kicking effects.

DLC receives the sealed sport interpretation/decision output rather than reinterpreting raw weather itself.

## Venue consumer contract
DDC may own stable neutral venue facts such as coordinates, timezone, generic roof class, and generic reference bearings. Sport repos own team/franchise membership, sport-era applicability, and sport-specific venue interpretation.

## Travel consumer contract
DDC may calculate route-independent neutral facts such as haversine distance, timezone change, travel elapsed time, and exact rest. Sport repos decide how those facts enter player/team state or prediction features.

## Provider/evidence contract
Provider adapters emit exact bytes first. Normalization never becomes the only copy of source evidence. Sanitized/public/report artifacts are a separate concern and may have their own versioned compatibility contract.

## Package-consumption contract
Production sport consumers install DDC from an immutable versioned wheel release, not a moving branch. The released source commit and wheel SHA-256 are recorded, and each sport repo compiles the exact DDC artifact into its own normal `--require-hashes` dependency lock.

Temporary local/editable installs are development conveniences only and cannot be the production installation authority.

A future DLC consumer must likewise bind to an immutable DDC contract/release or sealed evidence artifact; it must not use a moving DDC branch as production decision authority.

## Compatibility migration contract
When replacing a pre-existing sport-local shared implementation:
1. freeze the legacy behavior as a regression oracle;
2. run legacy and DDC-backed paths side-by-side;
3. preserve existing output/schema behavior unless an explicit versioned change is approved;
4. prove malformed-provider, secret-redaction, freshness, and raw-evidence behavior;
5. validate one tiny real-provider path where credentials/provider access are required;
6. remove duplicate legacy code only after DDC certification and equivalence.

## DLC staging note

The planned DLC architecture is temporarily staged under `docs/daily_line_core/` until `OneVillage83/Daily-Line-Core` is created. The staging location does not transfer DLC product authority into DDC. Repository creation/extraction is tracked in `Daily-Data-Core#5`.
