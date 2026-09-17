# Daily-Line-Core Architecture V1

**Status:** DOCUMENTED — PHYSICAL REPOSITORY CREATION PENDING  
**Date:** 2026-09-17  
**Target repository:** `OneVillage83/Daily-Line-Core`  
**Current staging home:** `OneVillage83/Daily-Data-Core/docs/daily_line_core/`

## 1. Mission

Daily-Line-Core (DLC) is The Daily Line's **cross-sport decision aggregation and product-assembly layer**.

Individual sport repositories remain responsible for producing trustworthy sport-native prediction and decision outputs. Daily-Data-Core remains responsible for shared point-in-time evidence and normalized market infrastructure. DLC consumes those sealed outputs and creates the single cross-sport Daily Line product state used by every customer-facing or marketing-facing downstream consumer.

DLC answers questions such as:

- What supported bets exist across all sports today?
- What does each sport's certified model stack say about each market?
- Which individual markets pass the sport's Recommendation Gate?
- Which 2-5 leg cross-game/cross-sport combinations offer the strongest probability/price relationship?
- Which recommendations should appear as Core, Value, or Upside EdgeStacks?
- What exact immutable facts should the report, infographic, website, and automation systems render?

DLC does **not** answer sport-native questions by re-modeling baseball, football, basketball, or other sports itself.

## 2. Position in The Daily Line system

```text
                         SHARED EVIDENCE
                    +---------------------+
                    |   Daily-Data-Core   |
                    | odds / market / PIT |
                    | provenance / facts  |
                    +----------+----------+
                               |
                               v
+----------------+   +----------------+   +----------------+
|   Daily-MLB    |   |   Daily-NFL    |   |  Daily-NCAAF   |   ...
| sport models   |   | sport models   |   | sport models   |
| Unified Line   |   | Unified Line   |   | Unified Line   |
| decision/gate  |   | decision/gate  |   | decision/gate  |
+-------+--------+   +-------+--------+   +-------+--------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                  sealed SportDecisionPackages
                             |
                             v
                  +-----------------------+
                  |    DAILY-LINE-CORE    |
                  | cross-sport assembly  |
                  +-----------+-----------+
                              |
        +---------------------+----------------------+
        |                     |                      |
        v                     v                      v
   All Bets Scanner      EdgeStack Engine       Product Index
        |                     |                      |
        +---------------------+----------------------+
                              |
                              v
                 DailyLinePublicationPackage
                              |
        +---------------------+----------------------+------------------+
        |                     |                      |                  |
        v                     v                      v                  v
   Daily Report          Infographic            Website/App      TDLA Automation
                                                                 video/social/etc.
```

## 3. Authority boundaries

### 3.1 Daily-Data-Core owns

- external provider acquisition;
- exact raw evidence and immutable provenance;
- odds/exchange/prediction-market observations;
- generic market math such as implied probability, no-vig, hold, freshness, and consensus;
- sport-agnostic market timelines and Line Intelligence evidence;
- weather, venue, travel/rest, and other certified shared neutral facts.

DDC may expose the market evidence DLC needs, but DDC does not decide what is a good wager and does not assemble the final Daily Line product recommendation set.

### 3.2 Daily-Model-Core owns

- shared independent-model research/governance infrastructure;
- generic model/evaluation/calibration machinery through the independent calibrated fair-view boundary, as defined by DMC architecture.

DMC does not own market comparison or final cross-sport product decisions.

### 3.3 Sport repositories own

Daily-MLB, Daily-NFL, Daily-NCAAF, and future Daily-* repositories own:

- canonical sport identity and sport state;
- sport-specific features and model inputs;
- sport-specific model zoo / ensemble / simulation;
- TDL Unified Line production for supported sport targets;
- sport-specific market-aware decision models;
- sport-specific Line Timing Models where applicable;
- fair-price/value/EV interpretation for individual markets;
- Recommendation Gate semantics and outputs;
- same-event simulation or joint-distribution evidence needed to model correlated markets;
- sport-specific explanation/evidence claims;
- settlement interpretation.

A sport must seal its outputs before DLC consumes them.

### 3.4 Daily-Line-Core owns

DLC owns:

- cross-sport ingestion/validation of sealed `SportDecisionPackage` artifacts;
- cross-sport joining with sealed DDC `MarketEvidenceBundle` artifacts;
- canonical supported-market catalog at the Daily Line product layer;
- **All Bets Prediction Scanner** assembly;
- candidate-pool construction from individually approved sport decisions;
- **EdgeStack Parlay Optimizer**;
- cross-game and cross-sport combination generation;
- combination quote comparison for Kalshi and supported sportsbook providers;
- cross-sport ranking views such as highest hit rate, best value, best balance, and best upside;
- final top-pick / product recommendation index derived from sealed sport decisions;
- final immutable `DailyLinePublicationPackage` sealing;
- product-level provenance linking every published claim back to sport and DDC authorities;
- distribution contracts to downstream renderers/consumers.

DLC may calculate combination-level probability/value because that is a cross-sport product problem. It may not override a sport's individual probability or Recommendation Gate output.

### 3.5 Downstream consumers own

#### Daily report
Renders the sealed DLC publication package into the daily report. It must not recompute fair probabilities, edges, or EdgeStack rankings.

#### Infographic generator
Renders approved highlights/EdgeStacks from the sealed package. It must not invent recommendations.

#### Website/app
Owns customer-facing presentation, search, filtering, archive browsing, and result display. It must not become the authoritative decision engine.

#### The-Daily-Line-Automation (TDLA)
Consumes sealed publication/fact packages for downstream automation such as social/video/content/marketing workflows and other operational automation. TDLA must not own sport modeling, Recommendation Gate semantics, or EdgeStack optimization.

## 4. Canonical input contracts

### 4.1 `SportDecisionPackage`

Each sport repository emits a versioned sealed package containing at minimum:

- package ID/version/digest;
- sport/league/slate scope;
- prediction timestamp;
- data cutoff timestamp;
- model/config/release provenance;
- canonical event/market refs;
- TDL Unified Line outputs for every supported target;
- individual fair probabilities/fair lines;
- uncertainty/calibration metadata;
- sport market-aware decision outputs where certified;
- Recommendation Gate state/reason for every supported market;
- sport explanation/evidence refs safe for publication;
- settlement-rule version;
- optional same-event joint-distribution/simulation refs for correlated-market evaluation;
- explicit supported/unsupported market declarations.

The package is append-only/immutable once sealed. A later sport rerun creates a new package/revision.

### 4.2 `MarketEvidenceBundle`

DDC emits or exposes a sealed versioned bundle containing the market observations needed for the DLC decision snapshot:

- provider and market identity;
- point-in-time quote/line/threshold;
- bookmaker/exchange/prediction-market provenance;
- observed/available timestamps;
- implied probability / no-vig / hold where applicable;
- quote freshness;
- market history / movement refs;
- provider fee/execution metadata where available;
- exact evidence/digest refs.

DLC does not mutate DDC evidence.

## 5. All Bets Prediction Scanner

DLC joins sport decisions and market evidence into one `AllBetsSnapshot` for the requested slate/time cutoff.

For every supported/modelable market, the scanner should publish:

- sport / league / event;
- canonical market key;
- side/threshold/line;
- provider/venue;
- market price / multiplier;
- market-implied probability;
- no-vig/consensus reference where relevant;
- TDL fair probability / fair price;
- probability edge;
- expected value where calculable;
- uncertainty/calibration metadata;
- Recommendation Gate;
- concise reason/evidence refs;
- quote timestamp/freshness;
- model/data cutoff/version provenance;
- settlement rule version;
- supported/unsupported/degraded state.

This snapshot is a first-class product artifact, not merely an intermediate EdgeStack input.

## 6. EdgeStack

DLC owns the cross-sport EdgeStack layer because combination optimization occurs only after sport decisions are sealed.

EdgeStack:

- uses only individually eligible/approved sport-market legs;
- generates 2-5 leg combinations;
- prioritizes cross-game/cross-sport combinations as first-class candidates;
- models same-event correlation using sport-authoritative joint information;
- compares model joint probability against actual Kalshi/sportsbook combo/parlay quotes;
- exposes Core, Value, and Upside classes;
- ranks by hit probability, price/value, uncertainty, quote freshness, and correlation quality;
- never adds a weak leg merely to create an attractive multiplier.

The detailed contract is in `EDGESTACK_PARLAY_OPTIMIZER_V1.md`.

## 7. `DailyLinePublicationPackage`

DLC's primary output is an immutable sealed product package.

Minimum conceptual fields:

```text
publication_package_id
schema_version
created_at
data_cutoff
market_cutoff
sports_included
sport_package_refs[]
market_evidence_bundle_refs[]

all_bets_snapshot
recommended_picks[]
edgestack_catalog
  core[]
  value[]
  upside[]

report_claims[]
infographic_claims[]
website_views[]
automation_fact_refs[]

provenance_manifest
quality/degradation_state
supersedes_package_id?
```

The package may contain references rather than duplicating heavy simulation/evidence payloads, but every published fact must be traceable to immutable upstream authority.

## 8. Sealing and immutability

A publication package is sealed only when:

- required sport packages are present and compatible;
- required market evidence is present and fresh enough;
- package cutoff rules are satisfied;
- All Bets assembly validates;
- EdgeStack generation either passes or is explicitly marked degraded/unavailable;
- every included claim has provenance;
- schema/version compatibility checks pass.

Once sealed, a package is immutable. Late information creates a new package/revision; it does not silently rewrite the original.

## 9. Distribution/fan-out model

DLC owns the **sealed product package and consumer handoff contract**, not every rendering side effect.

Recommended flow:

1. DLC seals `DailyLinePublicationPackage`.
2. Report generator consumes the package and renders PDF/HTML report.
3. Infographic generator consumes the same package and renders approved visual summaries.
4. Website ingests the package for user-facing pages/archive.
5. TDLA receives the package or a derivative `PublishableFactPackage` for downstream social/video/marketing automation.

All consumers should preserve `publication_package_id` and source provenance in their output receipts.

## 10. Timing and multiple snapshots

The system may create multiple valid DLC publication packages for the same event/slate when new legitimate pre-start information arrives.

Examples:

- morning slate package;
- lineup-confirmed MLB refresh;
- late NFL inactive/injury refresh;
- market-price refresh.

Each package must retain its own cutoff and supersession lineage. Historical evaluation must use the package actually available at the evaluation timestamp.

## 11. Failure/degradation behavior

DLC fails closed for any claim or combination that lacks required authority.

Examples:

- missing sport package -> affected sport omitted/degraded, not guessed;
- stale quote -> market/EdgeStack leg excluded;
- unsupported market -> labeled unsupported;
- same-game dependency without valid joint model -> correlated EdgeStack suppressed;
- one sport pipeline degraded -> other valid sports may still publish if product policy allows;
- EdgeStack failure -> All Bets/singles may still publish;
- downstream renderer failure -> sealed DLC package remains valid and can be retried by the consumer.

## 12. Historical evaluation

DLC must retain or reference enough PIT evidence to evaluate:

- All Bets calibration by sport/market class;
- Recommendation Gate results;
- top-pick performance;
- EdgeStack hit rate and calibration by leg count/class;
- quoted break-even versus realized hit rate;
- same-game vs cross-game performance;
- cross-sport vs single-sport performance;
- gross/net EV where calculable;
- quote freshness and execution availability;
- publication-package timing effects.

No future closing/result information may leak into an earlier DLC snapshot.

## 13. Repository model

Target repository:

`OneVillage83/Daily-Line-Core`

Recommended initial package/repo responsibilities:

```text
Daily-Line-Core/
  README.md
  AGENTS.md
  CODEX_START_HERE.md
  docs/
    ARCHITECTURE.md
    OWNERSHIP_BOUNDARIES.md
    INTEGRATION_CONTRACTS.md
    EDGESTACK_PARLAY_OPTIMIZER_V1.md
    IMPLEMENTATION_ROADMAP.md
    CHANGE_JOURNAL.md
    CURRENT_RESUME_POINT.md
  daily_line_core/
    contracts/
    ingest/
    all_bets/
    edgestack/
    publication/
    provenance/
  tests/
```

Until this repository exists, the canonical planning documents are staged under `Daily-Data-Core/docs/daily_line_core/` and tracked by issue `Daily-Data-Core#5`.

## 14. Relationship to TDLA bridge proving ground

The current GrokBot-OpenAI-Bridge is intentionally being proven first against The-Daily-Line-Automation because that repository is near completion and provides a constrained test environment.

This does not make TDLA the owner of DLC/EdgeStack intelligence.

After the bridge is proven and its authorized repository catalog expands, DLC should become its own registered repository/workstream. Cross-repository changes must preserve the bridge's one-repository-per-Codex-turn rule unless that protocol is intentionally superseded later.

## 15. Explicit V1 non-goals

DLC V1 does not include:

- bankroll management;
- stake sizing / Kelly sizing;
- stop-loss or chase-prevention logic;
- personalized wagering amounts;
- wallet/account management;
- automatic wagering/order placement.

Those are future separately governed capabilities.

## 16. Architectural invariants

1. DDC evidence is not DLC recommendation logic.
2. DMC independent modeling infrastructure is not DLC market decision logic.
3. Sport repositories remain authoritative for sport probabilities and Recommendation Gates.
4. DLC consumes sealed sport decisions; it does not reinterpret raw sport data.
5. All Bets is built before EdgeStack optimization.
6. An EdgeStack leg cannot bypass its sport-level eligibility/gate.
7. Same-event correlation requires sport-authoritative joint evidence or the combo fails closed.
8. Real provider combo/parlay quote beats synthetic standalone-price multiplication.
9. DLC seals one canonical publication package consumed by all downstream presentation/automation channels.
10. Downstream channels render/transform sealed truth; they do not recompute it.
11. Historical packages remain immutable and PIT-correct.
12. Bankroll/stake logic remains outside V1.
13. No automated wagering is authorized by this architecture.
