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

## DDC-D011 — Independent TDL fair line is market-isolated
The canonical TDL Unified Line is produced from independent sport models and calibration without sportsbook, exchange, prediction-market, future line-movement, or closing-price features. Market evidence is compared only after the independent fair view exists.

## DDC-D012 — Dynamic learned mixture-of-experts
Sport repositories maintain a broad model registry and may combine generalists, specialists, component experts, rating systems, simulators, regime detectors, and meta-models. Production influence is earned from forward point-in-time evidence and may vary by sport, target, context, horizon, uncertainty, and data quality.

## DDC-D013 — DDC owns Line Intelligence evidence; sports own Line Timing Models
DDC acquires and preserves complete market histories and may derive sport-agnostic features such as open/current/consensus state, movement, dispersion, sharp/soft divergence, and prediction-market divergence. Each sport repository owns the sport-specific Line Timing Model and any BET_NOW/WAIT interpretation.

## DDC-D014 — Immutable prediction ledger and closing-line firewall
Every model prediction is an append-only scientific observation. Later reruns create new records. Closing-line and result evidence are linked only for post-hoc evaluation and may never be made visible to an earlier prediction context unless they were genuinely available by that cutoff.

## DDC-D015 — Out-of-fold stackers and isolated calibration
Meta-ensembles train only on frozen forward/out-of-fold base-model predictions. Calibration uses out-of-sample evidence distinct from prohibited final-test evidence. Randomly shuffled validation is not the primary sports-forecasting validation framework.

## DDC-D016 — Model value includes specialist and unique-signal contribution
A model is not judged only by aggregate accuracy. Registry evaluation includes proper scoring, calibration, contextual skill, prediction diversity, residual correlation, ablation value, unique residual signal, uncertainty, sample support, and target-specific contribution. A globally mediocre model may remain active as a validated specialist.
