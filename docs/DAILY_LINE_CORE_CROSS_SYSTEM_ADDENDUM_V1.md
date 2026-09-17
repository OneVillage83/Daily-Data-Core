# Daily-Line-Core Cross-System Architecture Addendum V1

**Date:** 2026-09-17  
**Status:** DOCUMENTED CROSS-SYSTEM BOUNDARY — DOES NOT CHANGE DDC-0 THROUGH DDC-5 CERTIFICATION

## Decision

The Daily Line architecture now includes a distinct peer layer named **Daily-Line-Core (DLC)**.

DLC is downstream of sport-native prediction/decision systems and DDC market evidence, and upstream of all customer-facing/marketing-facing renderers.

This addendum supplements the existing cross-sport forecasting documentation without changing the scientific separation between the independent TDL Unified Line and market-aware sport decision logic.

## Canonical high-level topology

```text
Daily-Data-Core -> shared evidence / market timeline / PIT provenance
Daily-Model-Core -> shared independent modeling infrastructure

Daily-MLB -----+
Daily-NFL -----+--> sealed sport prediction/decision packages
Daily-NCAAF ---+
Future Daily-* +
                  \
                   +--> Daily-Line-Core
DDC market bundle -+      |
                          +--> All Bets Prediction Scanner
                          +--> EdgeStack Parlay Optimizer
                          +--> cross-sport product index
                          +--> DailyLinePublicationPackage
                                      |
                 +--------------------+--------------------+
                 |                    |                    |
              Report             Infographic          Website/App
                                                           |
                                                           v
                                                The-Daily-Line-Automation
                                                video/social/marketing
```

## Scientific boundary

The established forecasting rules remain:

1. sport independent models create the independent TDL fair view without market contamination;
2. sport market-aware layers may compare the independent fair view to DDC market evidence after the fair view exists;
3. sport repositories produce fair prices/value/EV decisions and Recommendation Gate outputs for individual sport markets;
4. only after those sport decisions are sealed does DLC perform cross-sport product assembly and combination optimization.

DLC may not rewrite or relabel the independent TDL Unified Line.

## Why DLC is separate from DDC

DDC's certified mission is evidence acquisition/normalization and generic market mathematics. EdgeStack requires cross-sport decision semantics, eligibility, joint-probability handling, quote-vs-model value comparison, ranking, and final product assembly.

Putting those responsibilities directly into DDC would violate DDC's existing `facts/evidence, not sport/product intelligence` boundary.

Therefore:

- DDC supplies market/evidence packages;
- sport repos supply sealed decision packages;
- DLC joins/optimizes/seals final product output.

## Why DLC is separate from TDLA

The-Daily-Line-Automation is downstream operational/content automation. It should receive sealed product truth and transform/distribute it, especially for video/social/marketing workflows.

The fact that the GrokBot-OpenAI-Bridge is currently being tested against TDLA is a proving-ground decision, not an ownership decision.

## Canonical staging documents

Until `OneVillage83/Daily-Line-Core` is created:

- `docs/daily_line_core/README.md`
- `docs/daily_line_core/DLC_ARCHITECTURE_V1.md`
- `docs/daily_line_core/EDGESTACK_PARLAY_OPTIMIZER_V1.md`
- `docs/daily_line_core/DLC_IMPLEMENTATION_HANDOFF_V1.md`
- `docs/daily_line_core/DLC_REPOSITORY_BOOTSTRAP.md`

Repository creation is tracked by `Daily-Data-Core#5`.

## No production authority

This addendum is architecture/documentation only. It creates no live service, no provider integration, no publication cutover, no automated wager placement, and no new DDC release authority.
