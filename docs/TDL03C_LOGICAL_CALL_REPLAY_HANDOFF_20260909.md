# TDL-03C logical-call and physical-attempt replay

Continuation: 2026-09-09T20:23:14-07:00 (America/Los_Angeles).
TDL-03B resume found a redirect physical-exchange gap outside the tests recorded
below. Release/cutover is withheld; see
[current blocker](TDL03B_RESUME_REDIRECT_EVIDENCE_BLOCKER_20260909.md).

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

## Completed local receipt

Implementation commit: `5bfab0e6eb8269ad1c90d657650375569bf5f702`.
New candidate: `daily_data_core-0.2.0.dev2-py3-none-any.whl`.
SHA-256: `f8831a6f4f1a726b41d1b72a4b7196cf1e100fd8b41d7137786452005a7e6a5a`.
Two independent empty build directories extracted from the committed Git archive
produced this identical digest with `SOURCE_DATE_EPOCH=1787788800`, Python 3.12.10,
pip 26.2, pip-tools 7.6.1, build 1.5.0, setuptools 83.0.0 and wheel 0.48.0.
Wheel contents contain only package code, py.typed and distribution metadata.

- DDC source: **85 passed**; Ruff pass; strict mypy **24 files**.
- Fresh hash-locked development environment plus exact wheel: install pass;
  `python -I -m pytest -q -c pytest.ini --import-mode=importlib` from an isolated
  tests-only directory: **85 passed**. A conftest assertion verifies imports come
  from site-packages and version 0.2.0.dev2, preventing source-tree fallback.
- `pip check`: no broken requirements. Pinned runtime/dev lock regeneration:
  zero Git diff. Hash-locked dev audit: no known vulnerabilities.
- MLB exact-wheel admission: **7/7**; current-legacy comparisons: **80/80**.
- Persisted replay admission v2: **10/10**, strict replay network calls **0**;
  successful 503-to-200 replay preserves two attempts and original evidence;
  schema-error replay preserves the same history, quota and diagnostics.
- Old dev1 recheck still exits **1**. The original five missing requirements are
  not waived; v2 adds error replay, identity and network enforcement assertions.
- Retained MLB oracle: **119 passed**; full Ruff pass; strict mypy **765 files**.
- Pre-commit DDC secret scan: **52 tracked files**, zero findings; final documentation
  does not add tracked files. Generated wheels/logs and synthetic receipts stay ignored.

MLB receipt paths (local ignored `.validation/`): `tdl03c-admission.json`,
`tdl03c-equivalence.json`, `tdl03c-replay.json`, `tdl03c-before.json` and
`tdl03c-old-wheel-control.json`. These are contract fixtures, not real provider data.
No Docker, live-provider check, remote Actions, release or cutover was executed.

## Exact next validation handoff

A lower-cost validation agent should verify this branch's final documentation head
descends from the implementation commit with documentation-only differences, then
run `.github/workflows/ci.yml` on that exact DDC head under Python 3.12 and its pinned
bootstrap/hashed locks. Record run/job IDs, lock regeneration, pytest/Ruff/strict-mypy
and security results. Rebuild from a clean Git archive with the toolchain/epoch above
and verify the wheel digest. In the private MLB validation checkout run the three
scripts below with `--wheel <rebuilt-wheel> --sha256 <digest-above>`:

```text
python -m scripts.check_ddc6_release
python -m scripts.compare_ddc6_candidate
python -m scripts.check_ddc6_failure_replay
```

Re-run the 119-test oracle group named in the private TDL-03C handoff. Do not retry
private Actions billing failures; never copy excluded MLB implementation/evidence
into a public CI mirror. Report exact scope and limitations. Return substantive
acquisition/PIT/evidence/security failures to Astra; handle mechanical runner issues
without changing production behavior. No merge/release/cutover is authorized here.

**TDL-03C COMPLETE locally. TDL-03B READY to resume** its existing certification,
immutable-release and consumer-adapter admission sequence. Release certification,
real-provider checks and eventual consumer migration remain future work.

## Exact-head operator validation — 2026-09-09T19:58:31-07:00

The operator revalidated authoritative source head
`7e476c6a06479ea16f1fb1d83616678a0e3153a8`, tree
`016d50e42aad77ec1841605fe97a1ddca69b769a`, from a clean worktree. The
implementation-to-head difference remains exactly the three previously recorded
documentation files. Dependency identities were unchanged:

- `requirements.in`: `02576af24c163c644a00692fbd719a6e93b8d8ffcdeea9ad7fb7ba1278e3ab5c`
- `requirements.txt`: `7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af`
- `requirements-dev.in`: `186408f6cc4966cab00d06019736f75b3f4fa863a8954ba12da6cc523dc027d9`
- `requirements-dev.txt`: `10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`

Two new clean Git-archive builds again produced version `0.2.0.dev2` and SHA-256
`f8831a6f4f1a726b41d1b72a4b7196cf1e100fd8b41d7137786452005a7e6a5a`.
The wheel contains only the 14 expected package files plus four distribution-metadata
files. A new clean hash-locked install imported version 0.2.0.dev2 from its isolated
`site-packages`, with no editable or source-tree fallback; `pip check` passed.

Fresh local results: DDC source **85 passed**, isolated installed wheel **85 passed**,
Ruff passed, strict mypy passed (**24 files**), lock regeneration produced zero diff,
the vulnerability audit found no known vulnerabilities, and the **52-file** secret
scan found nothing. Private consumer validation against this rebuilt wheel passed:
persisted replay **10/10** with actual strict-replay network calls **0**, admission
**7/7**, current-legacy equivalence **80/80**, retained oracle **119 passed**, full
Ruff passed, strict mypy passed (**765 files**), and the **1,055-file** secret scan
found nothing. MLB production dependencies and runtime remained unchanged.

The source head's `[skip ci]` message correctly suppressed a direct Actions run.
To exercise hosted CI without changing its tree, CI-only descendant
`25732fe44190dde48f76c6c493d889c4c8486988` was created on branch
`codex/tdl03c-ci-validation-20260909`. It has the exact authoritative tree above.
GitHub Actions workflow **CI**, run **34431413425**, quality job **102727522350**,
completed **SUCCESS** on Ubuntu/Python 3.12.14. Hash-locked installation, lock-drift
check, **85 tests**, Ruff, and mypy (**13 package source files**) all passed; no job
or required step was skipped.

DDC has no Dockerfile, Compose file, container workflow, or Docker release requirement.
Therefore Docker is **not applicable** to this pure-Python wheel gate; no container
certification is claimed. No public mirror was needed because validation ran in the
authoritative DDC repository. No live-provider request, release, tag, merge, consumer
switch, or model/scientific change occurred.

Disposition: **CERTIFIED-FOR-TDL-03B-RESUME**. The candidate's exact-source-tree,
package, replay, compatibility, security and hosted quality gates are green. This
certifies resumption of TDL-03B's controlled main/certification and immutable-release
sequence; it does not itself merge, publish 0.2.0, or authorize an MLB cutover before
the remaining release and consumer gates in PACKAGE_RELEASE_POLICY are completed.
