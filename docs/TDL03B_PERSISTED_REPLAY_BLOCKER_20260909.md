# TDL-03B persisted acquisition replay blocker

Historical finding for 0.2.0.dev1. The bounded repair and new candidate evidence are
recorded in [TDL-03C](TDL03C_LOGICAL_CALL_REPLAY_HANDOFF_20260909.md); the original
counterexample below remains valid for the retained old artifact.

Updated: 2026-09-09T18:40:55-07:00 (America/Los_Angeles).

**TDL-03B BLOCKED on a newly demonstrated shared acquisition/error/replay contract
gap.** This is not a remote-CI waiting condition. TDL-03A's seven necessary admission
checks and their retained results remain valid, but do not certify this additional
production-consumer requirement.

## Exact source and release disposition

Branch: `codex/ddc6-mlb-migration-20260909`.
Starting/source head: `2d8abda662541acee53b2d78bd08c337fa01822d`.
Implementation: `0e49e98d636addc5e3150816ea4c596f64b34a81`.
Draft PR: https://github.com/OneVillage83/Daily-Data-Core/pull/4.
Candidate remains **0.2.0.dev1**, unreleased, wheel SHA-256
`c9e5f44213146437bd8928ef705550acde817e8434fe3864b00e79db1cad5b0f`.
No version, artifact, tag, production dependency or published 0.1.0 asset changed.

PACKAGE_RELEASE_POLICY requires an architecture-certified commit on main, immutable
versioned release artifact and recorded digest, followed by the consumer's compiled
hash lock. The new counterexample prevents claiming a release-ready production
contract even before remote certification. No main merge, release publication,
consumer cutover or remote workflow was performed.

## Executed counterexample

Synthetic transport, zero provider network requests:

1. First response: HTTP 503, Retry-After 0, body `temporary`.
2. Second response: HTTP 200, body `[{}]`, quota remaining 9 / used 1.
3. The provider parser correctly rejects the structurally invalid event.

The current consumer's error retains final request diagnostics: attempts 2,
retries 1, status 200, quota remaining 9. DDC's OddsProviderSchemaError retains both
raw bodies and error receipts but exposes neither the final request diagnostics nor
quota. Reading those receipts from EvidenceLedger does not recover them.

A second acquisition uses the same retry pattern but final body `[]`. Live synthetic
acquisition succeeds with attempts 2. Passing the persisted ordered response payloads
to ReplayHttpClient produces `http_status_error` on the first retained 503 instead
of replaying the successful logical acquisition. Selecting only the final payload
can replay normalization, but still cannot recover original attempt/quota history.
Thus the existing replay primitive is a response decoder, not a persisted logical
transport-call replay contract. It must not be advertised as the latter.

## Root boundary

- ProviderAcquisitionError has payloads/receipts, but no final request diagnostics.
- AcquisitionCapture captures raw payloads from JsonHttpResult but drops that
  result's diagnostics when provider normalization raises.
- `ddc-acquisition-evidence-v2` receipts contain response status/content/clocks,
  but no logical-call identity, attempt grouping/final request outcome or quota.
- ReplayHttpClient consumes one response per get_json and cannot reconstruct a
  logical retry sequence or attempts that received no body.

Adding an exception field alone would not complete durable replay. The bounded next
shared work needs a versioned logical acquisition/attempt receipt with safe diagnostic
metadata, body/no-body attempt identity, terminal outcome and request grouping, linked
to the existing immutable raw evidence. Error results and offline replay must consume
that same contract. Retained v2 receipts must remain readable without inventing missing
history. No quota, attempt count or final outcome may be guessed from body ordering.

An MLB transport recorder or a private alternate attempt ledger would duplicate DDC
ownership and hide the missing shared contract. Production adapters/cutover were
therefore withheld, rather than installing a candidate or discarding failure lineage.
No separate production persistence model or speculative migration was introduced.

## Local evidence and resumption

The private consumer has committed an exact-wheel executable gate:
`scripts/check_ddc6_failure_replay.py`, contract
`TDL03B_FAILED_ACQUISITION_REPLAY_ADMISSION_V1`. It verifies the candidate digest
before importing it. Result: **exit 1**, five failing requirements (error attempts,
error quota, durable diagnostics, successful retry replay, replayed attempt count).
The legacy diagnostic control and exact raw-body retention controls pass.

Rechecked DDC source: **66 tests passed**, Ruff passed, strict mypy **22 files**.
The existing seven admission checks and 80 current-consumer comparison checks still
pass. This does not supersede the new failure. Source dependencies are unchanged;
the prior installed-wheel/build/audit evidence remains inherited, not re-certified.

The next architecture job must implement and test the shared logical-call evidence
contract, including retry-success, retry-terminal-error, no-response failures and
NWS multi-request grouping. Then build a new immutable candidate according to release
policy and rerun both old and new admissions before resuming TDL-03B adapters and
persisted/manual-runtime equivalence. Retain the current artifacts as counterexamples.

Remote CI remains delegated, but a green ordinary suite cannot override this gate.
No Docker certification is claimed. Public DDC may contain only generic source and
synthetic fixtures; private consumer data, logs and implementation remain excluded.
Scientific authority remains 0 AVAILABLE / 5 BLOCKED / 22 MISSING.
