# Daily-Line-Core Repository Bootstrap

**Target:** `OneVillage83/Daily-Line-Core`  
**Status:** physical repository not yet created  
**Tracking:** `OneVillage83/Daily-Data-Core#5`

## Why a separate repository

Daily-Line-Core is neither shared evidence infrastructure (DDC) nor sport-native prediction logic (Daily-* repos) nor downstream content automation (TDLA).

It requires its own repository because it owns a distinct cross-sport product boundary:

- admission of sealed sport decision packages;
- cross-sport All Bets assembly;
- EdgeStack combination optimization;
- provider combo/parlay price comparison;
- final Daily Line publication package sealing;
- downstream consumer contracts.

## Seed layout

```text
Daily-Line-Core/
  README.md
  AGENTS.md
  CODEX_START_HERE.md
  pyproject.toml
  requirements.in
  requirements.txt
  requirements-dev.in
  requirements-dev.txt

  docs/
    ARCHITECTURE.md
    OWNERSHIP_BOUNDARIES.md
    INTEGRATION_CONTRACTS.md
    EDGESTACK_PARLAY_OPTIMIZER_V1.md
    IMPLEMENTATION_ROADMAP.md
    ARCHITECTURE_CERTIFICATION_LOG.md
    CHANGE_JOURNAL.md
    CURRENT_RESUME_POINT.md

  daily_line_core/
    __init__.py
    contracts/
    ingest/
    all_bets/
    edgestack/
    publication/
    provenance/

  tests/
```

## Seed source mapping

When the repository is created:

- `Daily-Data-Core/docs/daily_line_core/DLC_ARCHITECTURE_V1.md` -> `Daily-Line-Core/docs/ARCHITECTURE.md`
- `Daily-Data-Core/docs/daily_line_core/EDGESTACK_PARLAY_OPTIMIZER_V1.md` -> `Daily-Line-Core/docs/EDGESTACK_PARLAY_OPTIMIZER_V1.md`
- `Daily-Data-Core/docs/daily_line_core/DLC_IMPLEMENTATION_HANDOFF_V1.md` -> basis for `docs/IMPLEMENTATION_ROADMAP.md` and `docs/CURRENT_RESUME_POINT.md`
- this document -> extraction record / initial bootstrap notes

The new repository should retain a note that these files were first staged in DDC on 2026-09-17 before physical repository creation.

## Initial README mission text

Recommended:

> Daily-Line-Core is The Daily Line's cross-sport decision aggregation and product-assembly layer. It consumes sealed sport decision packages from Daily-MLB, Daily-NFL, Daily-NCAAF, and future Daily-* engines plus point-in-time market evidence from Daily-Data-Core. It produces the All Bets Prediction Scanner, EdgeStack Parlay Optimizer, cross-sport product recommendation index, and one immutable DailyLinePublicationPackage consumed by the report, infographic, website, and downstream automation systems.

## Initial AGENTS boundaries

The repository constitution should state:

- do not acquire raw provider data already owned by DDC;
- do not implement sport-native models/features/settlement;
- do not alter a sport's fair probability or Recommendation Gate output;
- do not let website/report/automation become decision authority;
- all cross-repository inputs are immutable/versioned contracts;
- all output packages preserve PIT cutoff/provenance;
- 2-5 leg EdgeStack limit in V1;
- same-event correlation requires certified sport-authoritative joint information;
- bankroll/stake management is deferred;
- no automated wagering in V1;
- every material architecture change updates change journal/resume point.

## First implementation checkpoint

After repo creation:

1. create the governing docs above;
2. add only contract skeletons/fixtures first;
3. freeze `SportDecisionPackage`, `AllBetsSnapshot`, EdgeStack contracts, and `DailyLinePublicationPackage`;
4. do not connect to live Kalshi/provider APIs yet;
5. do not build website UI yet;
6. do not move sport intelligence into DLC;
7. add DLC to the GrokBot-OpenAI-Bridge authorized catalog only after the bridge proving-ground test on TDLA is accepted.

## Extraction completion criteria

The staging copy in DDC may be demoted to historical pointers once:

- `OneVillage83/Daily-Line-Core` exists;
- all four staging documents have canonical equivalents in DLC;
- DDC `ARCHITECTURE.md`, `OWNERSHIP_BOUNDARIES.md`, and `INTEGRATION_CONTRACTS.md` point to the DLC repository;
- TDLA points to the DLC sealed publication contract instead of local EdgeStack docs;
- bridge catalog/workstream registration is deliberately approved.
