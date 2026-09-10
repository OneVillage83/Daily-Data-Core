# TDL-03B final release preparation

Updated: 2026-09-09T21:26:32-07:00 (America/Los_Angeles).

Starting head `0ea51d2ec798b64ae6376603d9e0a72201b2ab64`; branch
`codex/ddc6-mlb-migration-20260909`; PR #4. Certified dev4 source
`3ec5b7a1d39abadac7fa76348f0c2f943f882e7e` remains unchanged in history.

The prepared final identity is **0.2.0**, a minor release for the shared provider
and versioned acquisition/exchange contracts, under PACKAGE_RELEASE_POLICY.md.
Only project/package version metadata changes from certified dev4; no transport,
normalizer, evidence, replay, security, dependency or scientific behavior changes.
The new wheel must receive its own digest and final-artifact admission; dev4's
digest is not reused. Dev4 and published v0.1.0 remain immutable.

Current GitHub main has no branch protection or rulesets. No additional owner
approval requirement was found in DDC's release/migration authority. This task
authorizes the governed release actions when their validation prerequisites pass.
Release remains **PREPARED**, unpublished, while final artifact and actual MLB
adapter/persistence admission are checked. No main merge, tag, release, MLB pin or
consumer cutover has occurred. Remote CI is delegated at the task boundary.

Initial final-version source validation: 114 tests passed; Ruff passed; strict
mypy passed 26 files. Further release/package and consumer receipts follow in the
continuation. The existing tiny real-provider, persisted-equivalence, PIT, rollback
and complete manual runtime requirements remain mandatory for migration completion.
