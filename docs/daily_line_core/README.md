# Daily-Line-Core (DLC) — Staging Architecture Index

**Status:** DOCUMENTED — PHYSICAL REPOSITORY CREATION PENDING  
**Date:** 2026-09-17  
**Target repository:** `OneVillage83/Daily-Line-Core`  
**Tracking issue:** `Daily-Data-Core#5`

This directory is the temporary architecture home for **Daily-Line-Core (DLC)** until the dedicated repository is created. These documents are intentionally staged in Daily-Data-Core because DDC is the existing cross-sport evidence boundary and because the available repository tooling in the architecture session could modify existing repositories but could not create a new repository.

When `OneVillage83/Daily-Line-Core` exists, these documents should be copied/moved there as the repository seed, preserving Git references to this staging location and the extraction record.

## DLC mission

Daily-Line-Core is the **cross-sport decision aggregation and product-assembly layer** for The Daily Line.

It sits:

- **downstream** of Daily-MLB, Daily-NFL, Daily-NCAAF, and future sport engines after those sports have produced sealed prediction/decision packages;
- **alongside/downstream** of Daily-Data-Core market evidence and market-timeline packages;
- **downstream** of Daily-Model-Core only indirectly through the sport engines' certified model outputs;
- **upstream** of the daily report, infographic generator, website/app, and The-Daily-Line-Automation.

DLC is where The Daily Line becomes one cross-sport product rather than a set of independent sport pipelines.

## Canonical data flow

```text
Daily-Data-Core -------------------------------+
market/evidence/PIT                            |
                                               v
Daily-MLB ---------> sealed SportDecisionPackage \
Daily-NFL ---------> sealed SportDecisionPackage  +--> DAILY-LINE-CORE
Daily-NCAAF -------> sealed SportDecisionPackage /
Future Daily-* ----> sealed SportDecisionPackage/
                                                    |
                       +----------------------------+-------------------------+
                       |                            |                         |
                       v                            v                         v
                All Bets Scanner              EdgeStack                 Top Picks /
                                             Optimizer                  Gate Index
                       \                            |                         /
                        +---------------------------+------------------------+
                                                    |
                                                    v
                                      DailyLinePublicationPackage
                                                    |
                    +-------------------------------+-------------------------------+
                    |                               |                               |
                    v                               v                               v
               Daily Report                    Infographic                    Website/App
                                                                                    |
                                                                                    v
                                                                    The-Daily-Line-Automation
                                                                    video/social/marketing
```

## Governing documents

- `DLC_ARCHITECTURE_V1.md` — system purpose, ownership, contracts, pipeline placement, sealed publication package, consumer boundaries, and repository extraction plan.
- `EDGESTACK_PARLAY_OPTIMIZER_V1.md` — EdgeStack / All Bets architecture, 2–5 leg optimizer, joint probability/correlation, provider quote comparison, and publication behavior.
- `DLC_IMPLEMENTATION_HANDOFF_V1.md` — bounded implementation plan for GrokBot-OpenAI-Bridge / Codex once DLC is authorized and registered.
- `DLC_REPOSITORY_BOOTSTRAP.md` — exact seed layout and extraction steps for creation of `OneVillage83/Daily-Line-Core`.

## Locked boundaries

1. **DDC remains evidence infrastructure.** It does not become the cross-sport recommendation engine.
2. **Sport repositories remain sport-intelligence authorities.** They own sport-specific fair probabilities, market-aware decision models, Recommendation Gate semantics, same-game simulation/joint outputs, and settlement interpretation.
3. **DLC owns cross-sport assembly.** It joins sealed sport decisions with sealed market evidence, runs the All Bets Scanner, optimizes EdgeStacks, selects cross-sport product views, and seals the final Daily Line publication package.
4. **DLC does not retrain sport models or reinterpret raw sport data.**
5. **Downstream renderers do not recompute truth.** Report, infographic, website, and automation consume sealed DLC publication artifacts.
6. **The-Daily-Line-Automation is downstream.** It may transform approved sealed facts into videos/social/marketing outputs, but it does not calculate TDL probabilities, Recommendation Gates, or EdgeStacks.
7. **Bankroll/stake management is deferred.** It is not part of DLC/EdgeStack V1.
8. **No automated wagering/order placement is part of V1.**

## Product identity

Primary feature inside DLC:

> **The Daily Line EdgeStack Parlay Optimizer**  
> **Stack the Edge. Not the Odds.**

DLC also owns the cross-sport **All Bets Prediction Scanner**, which exposes every supported/modelable individual market before EdgeStack combination optimization.
