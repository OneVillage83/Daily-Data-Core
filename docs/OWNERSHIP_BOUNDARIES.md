# Daily Data Core Ownership Boundaries

## Principle
If a fact can be acquired/normalized once and interpreted differently by multiple sports, DDC should usually own the fact while the sport owns the interpretation.

Cross-sport product assembly is a separate responsibility. **Daily-Line-Core (DLC)** consumes sealed sport decisions plus DDC market evidence after sport prediction/decision is complete.

## DDC owns
- shared HTTP/retry/diagnostic primitives;
- provider capability/licensing metadata;
- exact immutable raw response evidence;
- generic temporal provenance;
- generic sportsbook quote acquisition and math;
- quote/book/market timestamps and freshness primitives;
- exchange and prediction-market evidence where supported;
- immutable full market-history snapshots;
- sport-agnostic Line Intelligence derivations such as open/current/consensus state, movement deltas, movement velocity/acceleration, book dispersion, sharp/soft divergence, quote freshness, and prediction-market divergence;
- weather forecast acquisition and normalized meteorological facts;
- generic venue coordinates/timezone/roof/reference geometry;
- neutral travel distance/timezone/rest facts;
- versioned shared-package release artifacts used by multiple sport repositories;
- versioned point-in-time market-evidence handoff contracts suitable for sport consumers and DLC.

## DDC does not own
- MLB/NFL/NCAAF permanent team/player/game identity;
- lineup/depth/injury interpretation specific to a sport;
- baseball field/weather performance semantics;
- football field/weather passing/kicking semantics;
- sport-specific feature registries/state engines;
- sport model training/inference;
- the TDL Model Zoo / sport model registry implementation;
- the dynamic Unified Ensemble or TDL Unified Line;
- simulation engines;
- sport-specific Line Timing Models;
- market-residual / market-aware decision models;
- model fair prices, edge/EV decisions, Recommendation Gate behavior;
- sport settlement/report interpretation;
- the cross-sport All Bets product scanner;
- EdgeStack candidate generation/ranking;
- cross-sport product recommendation ordering;
- final Daily Line publication-package assembly.

## Sport repositories own
Daily-MLB, Daily-NFL, Daily-NCAAF, and future Daily-* repositories retain:

- permanent sport-specific identity;
- sport state/features;
- sport-native model training/inference;
- TDL Unified Line and sport fair probabilities;
- simulation and same-event joint-distribution evidence;
- sport-specific Line Timing Models and market-aware decision models;
- individual-market fair-price/value/EV logic;
- Recommendation Gate semantics/output;
- sport-specific explanation claims;
- settlement interpretation;
- sealing/versioning of their sport decision package for downstream consumers.

## Daily-Line-Core owns
DLC is the cross-sport decision aggregation and product-assembly layer. It owns:

- admission/validation of sealed sport decision packages;
- admission/reference of sealed DDC market evidence;
- cross-sport canonical product-market assembly;
- the **All Bets Prediction Scanner**;
- construction of the pool of individually approved markets eligible for combination optimization;
- **EdgeStack** 2-5 leg candidate generation;
- cross-game and cross-sport combination optimization;
- provider combo/parlay quote comparison, including Kalshi Combo/RFQ where supported;
- combination-level joint probability/value calculations using sport-authoritative dependency information;
- cross-sport ranking views such as highest hit rate, best value, best balance, and best upside;
- final top-pick/product recommendation index derived from sport-approved decisions;
- immutable `DailyLinePublicationPackage` sealing;
- product-level provenance linking published facts back to sport and DDC authorities;
- versioned handoff contracts to report, infographic, website, and automation consumers.

DLC does **not** own raw provider acquisition, sport-native modeling, sport-specific feature interpretation, or the authority to overwrite an individual sport's probability/Recommendation Gate.

## Downstream consumer boundary

### Report / infographic
Render the sealed DLC package. They may format, summarize, and visualize approved data but do not recompute sport probabilities, Recommendation Gates, or EdgeStack rankings.

### Website/app
Own presentation, filtering, archive/search, and customer-facing state. The website consumes sealed DLC product outputs rather than becoming the decision engine.

### The-Daily-Line-Automation
Consumes sealed DLC publication/fact outputs for downstream automation such as video, social, content, marketing, and other operational workflows. It does not own EdgeStack or cross-sport prediction logic.

## Identity boundary
A shared provider may call the same participant differently across products or over time. DDC preserves provider participant/event identity and raw values. Each sport repository maps those to its own canonical ontology/crosswalks.

DDC must not become a hidden universal sports-identity database merely because its odds adapter sees all sports.

DLC consumes sport-canonical refs from sealed sport packages and provider/market refs from DDC through explicit versioned crosswalk/handoff contracts; it must not infer identity by display-name string matching.

## Evidence boundary
DDC exact-byte evidence is the internal source-evidence layer. A consumer may additionally maintain sanitized/canonical artifacts for its existing output contract. Those layers are distinct and both may be required during migration.

DLC publication packages reference immutable sport/DDC evidence; they are not replacements for source evidence.

## Weather boundary
Shared schema includes neutral facts such as wind speed/direction, cloud cover, and pressure when supplied. Provider-specific descriptive fields may be carried in immutable source metadata. A sport-specific classification such as MLB `blowing_out` remains local.

DLC receives the sport's resulting interpretation/decision output, not raw weather semantics that DLC would reinterpret itself.

## Market boundary
Shared schema/math includes generic quotes, lines, implied probability, no-vig, hold, quote freshness, disagreement/consensus, and sport-agnostic market-timeline derivations. Market-level provider timestamps are preferred for quote-specific freshness when available, with bookmaker timestamp as fallback evidence.

DDC can reconstruct what the market knew at prediction time. It does not decide what that information means for an MLB, NFL, NCAAF, or future-sport forecast.

Model-derived fair price, the independent TDL Unified Line, sport-specific Line Timing Models, edge/EV, market-aware decision probabilities, and Recommendation Gate behavior remain sport/model responsibilities.

After those sport decisions are sealed, DLC may compare/aggregate them at the cross-sport product layer and calculate combination-level EdgeStack value against real combo/parlay quotes.

## Independent/market-aware boundary
The canonical TDL Unified Line is an independent sport forecast. DDC market evidence must not be silently injected into that independent model path. Sports may consume DDC market evidence only in explicitly market-aware layers after the independent fair view exists, or in separately labeled historical research/evaluation workflows.

Closing lines and event outcomes are post-hoc evaluation evidence for any earlier prediction timestamp. They may never leak backward into pregame inference.

DLC exists **after** sport independent and sport market-aware decision outputs have been produced. DLC must preserve that lineage and may not relabel a market-aware product output as the independent TDL Unified Line.

## Model-registry boundary
The cross-sport documentation defines common governance for model roles, prediction contracts, point-in-time evaluation, champion/challenger promotion, dynamic learned ensemble importance, specialist discovery, diversity, ablation, and calibration. The actual models and sport-specific registries remain in the sport repositories unless a later, separately approved shared service is created.

Daily-Model-Core owns generic independent-model research/governance infrastructure through its defined fair-view boundary; DLC remains downstream of that independent modeling layer.

## Package boundary
DDC source ownership does not imply consumers follow DDC `main`. Production consumers use explicit immutable released wheel versions through their own hashed dependency locks. This lets a sport upgrade DDC deliberately and regression-test the transition rather than inheriting every core commit immediately.

The future DDC-to-DLC market-evidence handoff must likewise be versioned/immutable; DLC must not treat the moving DDC branch as product authority.

## Migration boundary
A legacy sport-local shared implementation is not removed merely because an equivalent DDC module exists. The consuming sport's current tests/output contract remain authoritative until the DDC-backed path is certified regression-equivalent.

The staged DLC architecture currently lives under `docs/daily_line_core/` only until `OneVillage83/Daily-Line-Core` is physically created and seeded. That staging location does not transfer DLC product authority into DDC.
