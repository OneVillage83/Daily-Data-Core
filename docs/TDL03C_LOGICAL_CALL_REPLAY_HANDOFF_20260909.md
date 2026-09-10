# TDL-03C logical-call and physical-attempt replay

Updated: 2026-09-09T19:29:53-07:00 (America/Los_Angeles).

Branch: `codex/ddc6-mlb-migration-20260909`; parent
`b8145df93f8d6c18d39d6fc14a3ccff5b06dd28a`; existing draft PR #4.
This bounded repair supersedes the contract gap recorded in
TDL03B_PERSISTED_REPLAY_BLOCKER_20260909.md. That document remains historical
evidence for immutable candidate 0.2.0.dev1. Candidate 0.2.0.dev2 is unreleased;
neither existing wheel nor production release is overwritten.

## Shared contract

DDC owns transport history, not sport decisions. Each actual provider invocation
gets a logical-call identity; each physical attempt has a stable call/ordinal
identity. Acquisitions link ordered logical calls, allowing NWS points and forecast
requests to remain separate. Identical response bytes do not imply identical calls.
The source run reference binds a live call to its acquisition.

`ddc-physical-attempt-v1` records start/completion clocks, observed status, safe error
class, observed quota, retry eligibility/disposition/delay, and an optional immutable
payload reference. Timeout/connection failures have no invented body/status/quota.
Physical attempts count requests; quota headers describe provider observations, not
inferred charges. Unknown quota stays unknown. Response bytes are retained before
JSON/schema interpretation; completed attempts are persisted before the next retry.

`ddc-logical-call-v1` groups all attempts with the terminal outcome and diagnostics,
safe request identity, timeout/retry policy, validator version, package and code
identity. Retry policy v2 preserves existing default HTTP retry behavior. JSON and
schema failures are not retried by default. Explicit schema retry requires opt-in;
custom response validators require a version. Provider normalization errors retain
the successful transport history, final quota and all prior failed attempts.

`ddc-acquisition-history-v3` links calls, existing v2 response receipts, provider and
parser versions, acquisition outcome/error codes, normalized-content fingerprint,
code identity, clocks and optional previous-history reference. v2 remains readable;
response-only histories cannot be upgraded by guessing missing transport evidence.

Content-addressed JSON/raw artifacts and write-once identity bindings reject altered
attempt/call/acquisition history. Duplicate identical writes are idempotent. Reads
verify hashes, identity bindings, ordered attempts and payload metadata. Raw evidence
and history metadata each require explicit retention permission. No auth headers,
cookies or original exception messages enter history; safe URI redaction and numeric
quota filtering apply. Provider licensing/retention decisions remain caller-owned.
Incomplete interrupted calls are not fabricated into replayable completed histories.

## Replay and reprocess

`AcquisitionReplayClient` consumes durable v3 history. Strict mode requires matching
package/code/parser identity, explicit admission of custom validator versions,
matching request scope, all calls consumed and the same terminal interpretation and
normalization fingerprint. It returns original evidence identities and clocks;
retry failures are retained, not mistaken for the logical terminal result. It has
no network session or retry sleep. Error replay retains the same diagnostics/history.
The old `ReplayHttpClient` is only a compatible response decoder.

Explicit reprocess mode permits a new interpretation/version, creates new acquisition
lineage referencing the retained history, and preserves original calls/raw bytes and
source clocks. It is not strict replay or reacquisition. Existing PIT semantics are
unchanged. A custom validator version must identify the caller's actual implementation;
DDC does not independently certify external validator code.

## Local validation and release boundary

Source checkpoint: 85 tests passed, Ruff passed, strict mypy passed (24 files).
The added 19 cases cover error/quota history, timeout/connection failures, retries,
multi-call NWS, schema opt-in, restart, tamper/idempotency, retention/redaction,
strict zero-network replay, original clocks and explicit reprocess lineage.
Final wheel hashes, installed-wheel checks and consumer admission receipts are added
below after building from committed source. All fixtures are deterministic synthetic
contract evidence; no live provider validation is claimed.

MLB remains on legacy production authority. No sport production source, dependency
lock, model permission, registry, PIT rule or Recommendation Gate threshold changes.
Scientific inventory remains **0 AVAILABLE / 5 BLOCKED / 22 MISSING**.
Release policy still requires an architecture-certified main commit and immutable
published artifact before production adapters/cutover. Remote CI is delegated.
