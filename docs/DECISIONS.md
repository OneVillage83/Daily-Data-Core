# Daily Data Core Decisions

## DDC-D001 — Shared-core ownership boundary
Sport-agnostic acquisition, provider/provenance infrastructure, generic market math, weather facts, venue/geospatial primitives, and neutral travel/rest facts belong in Daily Data Core. Sport identity, sport interpretation, modeling, simulation, recommendation, and settlement stay in sport repositories.

## DDC-D002 — Exact-byte evidence before normalization
DDC raw evidence preserves exact provider response bytes with provenance before parsing/normalization. Consumer-facing sanitized artifacts are a separate layer and may not silently replace exact evidence.

## DDC-D003 — Provider-neutral identity
DDC preserves provider participant identifiers/names but does not become the permanent MLB/NFL/NCAAF identity authority. Each sport repository owns its canonical sports ontology and provider crosswalks.

## DDC-D004 — Point-in-time clocks
Shared observations use explicit timezone-aware provenance. `available_at` must not be later than `observed_at`. Historical consumer features must respect their prediction cutoff.

## DDC-D005 — Weather interpretation boundary
DDC acquires/normalizes meteorological facts. Baseball/football-specific wind/weather effects remain in their sport repositories.

## DDC-D006 — Market interpretation boundary
DDC may calculate generic implied probability, no-vig, hold, freshness, consensus, and quote grouping. Model fair price, edge, EV decisions, Recommendation Gate behavior, and sport settlement remain outside DDC.

## DDC-D007 — Migration by equivalence, not replacement by assumption
A sport's legacy shared implementation remains available as a regression oracle until the DDC-backed path proves contract/output equivalence and real-provider validation. Shared legacy code is removed only after the relevant DDC contract is certified.

## DDC-D008 — Immutable versioned package distribution
Production sport repos do not depend on a moving DDC branch or an unhashed VCS requirement. Certified DDC commits are released as versioned pure-Python wheels with recorded source commit and SHA-256. Each sport repo consumes the exact release through its own compiled `--require-hashes` lock.

## DDC-D009 — Provider timestamp specificity
Where a provider supplies both bookmaker-level and market-level quote timestamps, DDC preserves both. Market-level timestamp is preferred for the specific normalized offer/freshness fact; bookmaker timestamp is the fallback.

## DDC-D010 — Weather compatibility without provider-schema pollution
Cross-provider numeric weather fields include source-neutral facts such as cloud cover and pressure when available. Provider-specific descriptive values that consumers still need are carried through immutable source metadata rather than promoted to universal semantics.
