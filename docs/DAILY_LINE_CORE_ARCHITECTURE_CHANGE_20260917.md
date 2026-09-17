# Daily-Line-Core Architecture Change Record — 2026-09-17

- **Timestamp:** 2026-09-17T19:43:00Z
- **Area:** cross-system architecture / ownership / documentation
- **Summary:** Added **Daily-Line-Core (DLC)** as a distinct cross-sport decision aggregation and product-assembly layer. DLC sits downstream of sealed sport prediction/decision packages and DDC market evidence, and upstream of report, infographic, website, and The-Daily-Line-Automation consumers. Moved the canonical EdgeStack / All Bets planning authority out of TDLA and into the DLC architecture staging area.
- **Reason:** The cross-sport All Bets scanner and EdgeStack optimizer are neither DDC evidence infrastructure nor sport-native prediction logic nor downstream marketing automation. They require their own product-level boundary so each sport can finish and seal its decisions before The Daily Line performs cross-sport optimization and publication assembly.
- **Files affected:** `README.md`; `docs/ARCHITECTURE.md`; `docs/OWNERSHIP_BOUNDARIES.md`; `docs/INTEGRATION_CONTRACTS.md`; `docs/DAILY_LINE_CORE_CROSS_SYSTEM_ADDENDUM_V1.md`; `docs/daily_line_core/*`; issue #5.
- **Authority impact:** DDC remains evidence/market infrastructure. Sport repositories retain sport-native probabilities, fair-price/value/EV logic, Recommendation Gates, same-event simulation/joint information, and settlement. DLC owns cross-sport All Bets assembly, EdgeStack optimization, cross-sport ranking, and final `DailyLinePublicationPackage` sealing. TDLA is downstream for video/social/marketing and other approved automation workflows.
- **Certification impact:** None. DDC-0 through DDC-5 certification is unchanged. DLC is documented/planned only and has no production authority.
- **Data/migration impact:** None. No runtime schema, package, migration, service, API, or cutover was created.
- **Operational impact:** None. Existing DDC release/migration work remains unchanged.
- **Validation/evidence:** Placement was checked against DDC `AGENTS.md`, `ARCHITECTURE.md`, `OWNERSHIP_BOUNDARIES.md`, `INTEGRATION_CONTRACTS.md`, the cross-sport Unified Forecasting architecture, and Daily-Model-Core's independent-model boundary.
- **Risks/open questions:** The physical `OneVillage83/Daily-Line-Core` repository does not yet exist. The available connector cannot create a repository, so canonical planning docs are temporarily staged under `docs/daily_line_core/`. Exact contract schemas and package/runtime technology remain to be frozen in DLC-0/DLC-1.
- **Rollback/recovery:** If DLC placement changes, preserve this record and supersede the staged architecture rather than silently moving product intelligence back into DDC or TDLA.
- **Next exact step:** Create `OneVillage83/Daily-Line-Core`, seed it from `docs/daily_line_core/DLC_REPOSITORY_BOOTSTRAP.md`, then begin DLC-0 after the GrokBot-OpenAI-Bridge proving-ground work in TDLA is accepted and DLC is deliberately added to the authorized repository catalog.
