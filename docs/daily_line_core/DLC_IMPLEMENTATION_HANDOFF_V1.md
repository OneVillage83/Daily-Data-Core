# Daily-Line-Core Implementation Handoff V1

**Status:** FUTURE IMPLEMENTATION PLAN  
**Date:** 2026-09-17  
**Target repository:** `OneVillage83/Daily-Line-Core`  
**Governing architecture:** `DLC_ARCHITECTURE_V1.md`

## Purpose

This handoff gives GrokBot-OpenAI-Bridge / Codex an implementation-ready sequence for Daily-Line-Core without reconstructing product intent from chat history.

DLC is the cross-sport product brain that consumes sealed sport decision packages plus DDC market evidence, builds the All Bets Prediction Scanner, optimizes EdgeStacks, and emits one sealed `DailyLinePublicationPackage` for report, infographic, website, and automation consumers.

## Bridge constraint

The GrokBot-OpenAI-Bridge currently executes one repository per Codex turn. Preserve that rule unless the bridge protocol is intentionally changed later.

DLC work that requires sport/DDC/website/automation changes must be split into explicit repository-specific turns with versioned contracts between them.

## DLC-0 — Repository bootstrap and governing contracts

- create `OneVillage83/Daily-Line-Core`;
- seed README/AGENTS/CODEX_START_HERE/docs structure from `DLC_REPOSITORY_BOOTSTRAP.md`;
- preserve extraction provenance back to DDC staging docs and issue #5;
- define package/release baseline;
- define immutable contract/versioning rules;
- freeze DDC / DMC / sport / DLC / website / TDLA ownership boundaries.

## DLC-1 — Canonical cross-repository contracts

Implement schemas/fixtures for:

- `SportDecisionPackage`;
- `MarketEvidenceBundleRef`;
- `AllBetsSnapshot`;
- `EdgeStackLeg`;
- `EdgeStackQuote`;
- `EdgeStackCandidate`;
- `EdgeStackRecommendation`;
- `EdgeStackCatalog`;
- `DailyLinePublicationPackage`;
- provenance/supersession envelopes.

Acceptance: no sport-specific probability logic appears in DLC contracts; no bankroll/stake fields appear in V1.

## DLC-2 — Sport package admission

- validate package schema/version/digest;
- validate PIT cutoffs;
- preserve sport authority and unsupported-market declarations;
- deterministic package admission/rejection reason codes;
- support multiple sport package revisions without overwriting history.

## DLC-3 — DDC market-evidence admission

- ingest/reference DDC market snapshots and quote provenance;
- reconcile canonical sport market refs through approved mappings;
- preserve quote timestamps/freshness/provider identity;
- reject stale/incompatible market evidence;
- do not duplicate DDC provider acquisition logic.

## DLC-4 — All Bets Prediction Scanner

- enumerate every supported/modelable market across admitted sport packages;
- join sport fair probabilities/gates to DDC market prices;
- calculate product-layer comparison fields without altering sport probabilities;
- emit deterministic `AllBetsSnapshot`;
- expose filtering/ranking metadata for downstream report/website.

Required views include probability, market probability/price, edge, EV where valid, gate, reason, uncertainty, quote time, and provenance.

## DLC-5 — EdgeStack candidate engine

- implement deterministic 2-5 leg enumeration;
- support cross-game and cross-sport combinations;
- detect contradiction/duplicate exposure;
- apply bounded/prunable search;
- require sport-approved legs only;
- preserve deterministic candidate IDs.

## DLC-6 — Joint probability / dependency engine

- independent-event product path;
- sport-authoritative simulation/joint-sample adapter;
- calibrated dependency/correlation adapter;
- uncertainty output;
- fail closed when same-event dependency is unsupported.

## DLC-7 — Provider combo/parlay quote adapters

Priority:

1. Kalshi Combo/RFQ;
2. supported sportsbook parlay quote sources.

- normalize quote identity/multiplier/price;
- preserve timestamp/expiry;
- fee-aware break-even where supported;
- compare actual quote with model joint probability;
- retain standalone-price product only as diagnostic.

## DLC-8 — EdgeStack optimizer and classifications

Implement:

- `CORE`;
- `VALUE`;
- `UPSIDE`;
- `HIGHEST_HIT_RATE`;
- `BEST_VALUE`;
- `BEST_BALANCE`;
- `BEST_UPSIDE`.

Underlying metrics remain visible: hit probability, break-even, EV, uncertainty, correlation quality, freshness, leg count, multiplier.

## DLC-9 — Publication package sealing

Build immutable `DailyLinePublicationPackage` containing:

- admitted sport package refs;
- market evidence refs;
- All Bets snapshot;
- individual recommendation/top-pick index;
- EdgeStack catalog;
- report/infographic claims;
- website views/refs;
- automation-safe fact refs;
- full provenance/degradation state;
- supersession lineage.

No renderer may become the authority for a value calculation.

## DLC-10 — Downstream consumer contracts

Repository-specific follow-up turns:

- report generator consumes sealed package;
- infographic renderer consumes sealed package;
- website ingests/displays sealed package;
- TDLA consumes approved facts for video/social/marketing automation.

Downstream consumers may transform presentation but may not recompute probabilities/gates/EdgeStacks.

## DLC-11 — PIT historical evaluation / certification

- replay exact historical cutoffs;
- evaluate individual-market calibration;
- evaluate Gate performance;
- evaluate EdgeStack calibration by class/leg count;
- same-game vs cross-game;
- cross-sport vs same-sport;
- quote break-even vs realized results;
- gross/net EV where defensible;
- stale/availability audit;
- settlement correctness;
- promotion thresholds locked before production authority.

## DLC-12 — Bridge + operational onboarding

After DLC manual behavior is certified:

- register DLC in the bridge authorized repository catalog;
- add DLC workstreams;
- prove one-repo-per-turn routing;
- define handoffs from sport repos/DDC to DLC and DLC to website/automation;
- later integrate operational orchestration only through certified versioned contracts.

## Explicit V1 exclusions

Do not implement during DLC-0 through DLC-12:

- bankroll manager;
- stake/Kelly sizing;
- stop-loss/chase controls;
- automated order placement;
- account/wallet execution.

## Exact resume point

Once the `Daily-Line-Core` repository exists and the owner says to begin:

> Start **DLC-0** by seeding the repository from `DLC_REPOSITORY_BOOTSTRAP.md`, then freeze canonical ownership/contracts before writing EdgeStack business logic.
