# Daily Data Core Integration Contracts

## Core rule
DDC normalizes shared facts. A sport consumer maps those facts into its own canonical identity/state/features.

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

## Venue consumer contract
DDC may own stable neutral venue facts such as coordinates, timezone, generic roof class, and generic reference bearings. Sport repos own team/franchise membership, sport-era applicability, and sport-specific venue interpretation.

## Travel consumer contract
DDC may calculate route-independent neutral facts such as haversine distance, timezone change, travel elapsed time, and exact rest. Sport repos decide how those facts enter player/team state or prediction features.

## Provider/evidence contract
Provider adapters emit exact bytes first. Normalization never becomes the only copy of source evidence. Sanitized/public/report artifacts are a separate concern and may have their own versioned compatibility contract.

## Package-consumption contract
Production sport consumers install DDC from an immutable versioned wheel release, not a moving branch. The released source commit and wheel SHA-256 are recorded, and each sport repo compiles the exact DDC artifact into its own normal `--require-hashes` dependency lock.

Temporary local/editable installs are development conveniences only and cannot be the production installation authority.

## Compatibility migration contract
When replacing a pre-existing sport-local shared implementation:
1. freeze the legacy behavior as a regression oracle;
2. run legacy and DDC-backed paths side-by-side;
3. preserve existing output/schema behavior unless an explicit versioned change is approved;
4. prove malformed-provider, secret-redaction, freshness, and raw-evidence behavior;
5. validate one tiny real-provider path where credentials/provider access are required;
6. remove duplicate legacy code only after DDC certification and equivalence.
