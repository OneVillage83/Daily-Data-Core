# TDL-03D HTTP exchange and redirect evidence

Updated: 2026-09-09T20:58:11-07:00 (America/Los_Angeles).

Branch `codex/ddc6-mlb-migration-20260909`; parent
`cbd365cb00c92fef286d1db930ef75c522fbe559`; draft PR #4.
Candidate **0.2.0.dev4**, unreleased. Published v0.1.0 and retained dev2/dev3 are immutable
and unchanged. This job repairs shared HTTP evidence; MLB remains unswitched.

## Reproduced defect and accepted hierarchy

The original exact-dev2 redirect gate was run before editing and exited 1. Two
synthetic transport exchanges, 302 then 200, produced one recorded attempt containing
only status 200. Redirect bytes and quota 10 were missing. Actual network calls: 0.

The hierarchy is now **LogicalCall -> PhysicalAttempt -> HttpExchange**. A redirect
does not increment the physical retry count. Exchange identity hashes its existing
parent attempt identity plus ordinal; no competing logical/attempt identity exists.
A 302-to-200 attempt has two exchanges and zero retries. A later retry starts a new
attempt at exchange ordinal 1. Diagnostics retain their physical-attempt semantics;
the call document separately reports exchange count. Per-exchange quota observations
remain independent and are never summed into invented provider charges.

## Transport and redirect policy

DDC owns GET-only redirect traversal. Requests adapters perform individual sends;
DDC does not use Session's automatic redirect handling or post-hoc response.history
as acquisition authority. Even Session.send with redirects disabled pre-processes
Location, so direct adapter invocation prevents malformed Location from discarding a
received response. The initial request preserves normal Session preparation/TLS/proxy
settings. Adapter-level automatic retries are prohibited because they bypass DDC
accounting. Explicitly injected custom/test Session.get implementations must honor
allow_redirects=False and the same one-send contract.

`RedirectPolicy` v1 handles 301, 302, 303, 307 and 308 as GET -> GET. Default policy
permits same-origin redirects and same-host default-port HTTP-to-HTTPS upgrades,
bounded to five hops (configurable 0..30). Cross-host redirects require an explicit
exact trusted-host set and HTTPS port 443. Arbitrary ports/hosts, HTTPS downgrade,
unsupported schemes, userinfo, malformed/blank Location, controls, backslashes,
loops and depth overflow fail closed before another send. Relative Location is
resolved against the current request. Provider callers may prohibit all redirects
with max_redirects=0. Default NWS cannot follow an untrusted host around its existing
forecast URL validation; any explicit trust expansion is caller-owned policy.

Redirected requests are independently prepared: no Session auth, netrc credentials,
cookies, response cookies, TLS client certificates, arbitrary original headers or original query parameters
are forwarded. Only User-Agent, Accept and Accept-Encoding are carried. Secret-bearing
Location query keys are rejected; only sanitized resolved target metadata is stored.
Authorization, Cookie, Set-Cookie and raw Location headers are never metadata fields.
Allowed response header evidence is canonical Date and bounded Retry-After seconds;
content type and numeric quota observations have their existing explicit fields.
Exact response bytes still require the caller's licensing/content retention policy;
raw evidence is not a sanitized public artifact.

## Durability, ordering and failure

Before each send, an immutable exchange-start intent is stored when authorized.
After a response body is received: raw bytes and a received-exchange receipt are
stored before redirect policy evaluation; a separate immutable decision receipt is
stored before any next hop. No completed record is overwritten. All writes retain
the existing atomic content-addressed store and identity bindings.

The completed exchange includes request/response clocks, method, safe URL, status,
raw payload hash, permitted headers, quota, sanitized target, policy decision and
safe error class. Original exception text is excluded. No-response transport failure
has no invented body. A body-read failure preserves known status/quota and prior
complete hops, with unavailable body explicitly absent. Availability is stamped only
after successful body retrieval. Final normalization/schema classification belongs
to the attempt/acquisition and does not reclassify a redirect body as normalized data.

`EvidenceLedger.exchange_state(call_id, attempt_ordinal, ordinal)` reads a known
identity without scanning or network access. It returns retained start/received/final
records and a terminal-attempt receipt when present. A start alone means ambiguous
execution, not proof of a completed exchange. An interrupted chain never becomes a
fabricated completed call. There is no automatic network resume: reconciliation must
retain incomplete evidence and authorize a new acquisition identity if reacquiring.
Reading or replaying history cannot silently resend an ambiguous hop.

## Versioning, strict replay and reprocess

New receipts: exchange-start-v1, exchange-received-v1 and exchange-v1; enclosing
physical-attempt-v2, logical-call-v2 and acquisition-history-v4. Existing raw/v2
response receipts remain readable. Old attempt-v1/call-v1/history-v3 reads preserve
their documents/identities and expose no invented exchanges. Strict current replay
requires complete exchange history plus matching package/code/parser identity and
the existing validator admission, scope and normalized-result checks.

Strict replay retains all original exchanges, decisions, quotas, clocks, receipts and
terminal outcome without following Location or calling a transport. Reprocess creates
new interpretation lineage referencing prior history while preserving its existing
calls/exchanges; it cannot manufacture absent historical hops. Serialization verifies
raw hashes, content-addressed receipts, parent/ordinal/target continuity and immutable
bindings. Body/history retention remain independently explicit caller permissions.

## Local checkpoint and continuation

Source suite: **114 passed** (85 retained plus 29 new cases); Ruff passed; strict mypy
passed **26 files**. Tests cover all supported redirect statuses, relative/upgrade/
trusted-host targets, rejection cases, credentials, loops/depth, body/quota retention,
NWS trust, transport/body/schema failures, retry hierarchy, strict zero-network replay,
restart, crash ambiguity, retention denial, legacy reads, reprocess, PIT and tamper
rejection. The only retained test-double change explicitly accepts/asserts disabled
automatic redirects; its prior retry/error assertions remain intact.

The private redirect admission tool uses the new exchange layer while preserving
all original missing-evidence assertions. Its new hierarchy assertion requires one
attempt, two exchanges and zero retries, so treating redirects as retries cannot pass.
Final committed-source wheel, installed-wheel, consumer and security receipts follow.

Final review extended the credential regression to Session TLS client certificates.
It failed against the first local dev3 build: adapter send options carried the initial
client certificate to an explicitly trusted redirect. The repair strips that setting
on every redirected send while retaining initial-request behavior. No real certificate
or network was used. Dev3 at source `807a12f7be0759ec25d3ad44c8d11852a0deb227`,
SHA-256 `712b2cdfb3e636c4c953da23283d5d2d4b71e782fbf0b79dab1697d790239dd7`,
remains an immutable superseded local checkpoint, not the admitted candidate.

No production release, merge, MLB dependency/adapter change, remote CI or Docker was
performed. Science remains **0 AVAILABLE / 5 BLOCKED / 22 MISSING**. After local
candidate admission, delegate exact-source CI; then resume the governed TDL-03B
release and consumer integration sequence. Do not infer release/cutover authorization
from completion of this bounded repair.

## Final candidate and exact local evidence

Implementation source: **`642f5e62ecb4ab4d21909cff1c04f74bd8e8e828`**.
Subsequent TDL-03D DDC commits are documentation-only. Verify that delta before
relying on this receipt; the final documentation head is also recorded by MLB.

Wheel: `daily_data_core-0.2.0.dev4-py3-none-any.whl`.
SHA-256: **`3a3cf828b9e858e2aaba1dc2b41832109c278a435b3952285a43c9d17bc5169e`**.
Two separate clean Git-archive builds produced identical bytes. Local retained path:
`.validation/tdl03d-dev4-wheel-one/` (second build in `tdl03d-dev4-wheel-two/`).
Python 3.12.10; pip 26.2; pip-tools 7.6.1; build 1.5.0; setuptools 83.0.0;
wheel 0.48.0; `SOURCE_DATE_EPOCH=1787788800`; `python -m build --wheel --no-isolation`.
The wheel contains only the shared package and distribution metadata.

Unchanged runtime lock SHA-256:
`7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af`.
Unchanged development lock SHA-256:
`10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`.
Both locks regenerated with CI's pinned compile command and zero Git diff.

Final source suite: **114 passed** (85 retained plus 29 new); Ruff passed; strict
mypy passed **26 files**. Consumer Ruff passed and strict mypy passed **766 files**.
The exact dev4 wheel passed redirect admission **8/8**, persisted replay **10/10**,
release admission **7/7**, legacy comparison **80/80**; all actual network counters
were **0**. The retained dev2 wheel still exits **1** under the strengthened gate,
retaining only status 200 and failing body/quota/hierarchy/target checks.
Current MLB oracle: **119 passed**, no production source or lock delta.
Fresh environment installed dev4 and every dependency with `--require-hashes`.
The copied test suite ran outside the source checkout with Python isolated mode,
importlib import mode and an assertion of site-packages / version 0.2.0.dev4:
**114 passed in 11.36s**. `pip check` passed in both isolated DDC and MLB environments.
Dependency audit: no known vulnerabilities. Tracked-file secret scans passed with
zero findings/errors across **56 DDC / 1,058 MLB files** (`--skip-env`; no configured
secret values loaded). Final diff inspected; DDC locks and MLB production files
are unchanged. Scan scope is tracked files, not private runtime evidence.

## Lower-cost validation instructions and TDL-03B resume

1. Verify branch HEAD, ancestry from `cbd365cb00c92fef286d1db930ef75c522fbe559`,
   and documentation-only delta from `642f5e62ecb4ab4d21909cff1c04f74bd8e8e828`.
   Do not reuse dev2 certification as dev4 evidence.
2. Run repository-authoritative `.github/workflows/ci.yml` on the exact DDC source
   with Python 3.12, pinned bootstrap and hash locks. Commits use `[skip ci]` to
   respect this task's remote-CI boundary; the workflow has no manual dispatch.
   The established validation-only empty descendant trigger is acceptable only
   with exact tree equality recorded, as in the TDL-03C operator receipt. Record
   authoritative SHA -> tree-identical CI SHA -> run/job IDs. Do not alter source
   to obtain a green run. Expected source tests: 114; Ruff/mypy/lock drift green.
3. Rebuild from a clean archive using the toolchain/epoch above, verify the wheel
   hash, and install it with `--require-hashes` plus `requirements-dev.txt` into a
   fresh environment. Copy tests outside the checkout; assert import comes from
   site-packages at version 0.2.0.dev4; run `python -I -m pytest -q --import-mode=importlib`
   with a test-only pytest.ini (no repository pythonpath). Expected: 114 tests.
   Run `pip check`, dependency audit, tracked-file secret scan and lock regeneration.
4. In the private MLB validation checkout, run all four commands with
   `--wheel <exact-dev4-wheel> --sha256 3a3cf828b9e858e2aaba1dc2b41832109c278a435b3952285a43c9d17bc5169e`:

   ```text
   python -m scripts.check_ddc6_redirect_history
   python -m scripts.check_ddc6_failure_replay
   python -m scripts.check_ddc6_release
   python -m scripts.compare_ddc6_candidate
   ```

   Expected: 8/8, 10/10, 7/7, 80/80 and actual external/replay calls 0. Run the
   retained 119-test MLB oracle command in its TDL-03D validation handoff.
5. DDC has no Dockerfile/container workflow or container release requirement;
   Docker is not applicable to this wheel repair. No Docker execution is claimed.
   Do not retry private Actions billing failures or copy private MLB implementation,
   evidence, provider data, logs or databases into the public DDC repository/mirror.
6. Return substantive HTTP/evidence/PIT/security failures to Astra with exact logs;
   handle mechanical validation issues in the operator task. Record certification
   before the governed TDL-03B main/release/consumer-admission sequence resumes.

**TDL-03B-RESUME: READY for delegated candidate validation and the existing governed
continuation, not authorized for immediate release/cutover.** No new architectural
blocker remains. No live-provider, remote-CI, Docker, full MLB-suite, release or
production-migration certification is claimed here. Scientific permissions, model
promotion, PIT authority, Recommendation Gate thresholds and registries are unchanged.

## Operator certification receipt — 2026-09-09T21:16:47-07:00

**Disposition: CERTIFIED-FOR-TDL-03B-RESUME.** The authoritative DDC source is
`3ec5b7a1d39abadac7fa76348f0c2f943f882e7e`, exact Git tree
`829ac070b2e11993346a119dcc5b6ad169845e9a`. Branch, clean worktree, dev4 metadata,
ancestry and recorded lock hashes were independently verified. The tree-identical
CI-only descendant is `895a6546d5754b5052215cfaaeedcceabc1fb000`; its tree is also
`829ac070b2e11993346a119dcc5b6ad169845e9a`. It changes no candidate content.

Two new clean Git-archive builds from the authoritative source reproduced wheel
`daily_data_core-0.2.0.dev4-py3-none-any.whl`, SHA-256
`3a3cf828b9e858e2aaba1dc2b41832109c278a435b3952285a43c9d17bc5169e`.
Fresh `--require-hashes` installation imported version 0.2.0.dev4 from isolated
site-packages with no editable/source fallback; **114 installed-wheel tests** and
`pip check` passed. Source validation passed **114 tests**, Ruff, workflow-scope
strict mypy **14 files**, and expanded strict mypy **26 files**.

Exact-wheel gates passed: redirect **8/8** with statuses 302,200, one attempt, two
exchanges and network calls 0; persisted replay **10/10** with replay calls 0;
admission **7/7** and legacy/wheel equivalence **80/80**, both with provider calls 0.
The retained private MLB oracle passed **119 tests**; full MLB Ruff and strict mypy
**766 files** passed. Lock regeneration produced zero diff. Vulnerability audit found
no known vulnerabilities. Secret scans passed 56 DDC and 1,058 MLB tracked files
with no findings/errors and no configured secret values loaded.

Hosted DDC workflow **CI** run **34436406742**, quality job **102742266899**, tested
CI commit `895a6546d5754b5052215cfaaeedcceabc1fb000` on Ubuntu with CPython 3.12.14.
Hash-locked dependency installation, both lock regenerations/diff check, **114 tests
in 3.44s**, Ruff and strict mypy **14 source files** all completed successfully; no
required workflow step was skipped. Run:
`https://github.com/OneVillage83/Daily-Data-Core/actions/runs/34436406742`.

Docker is **NOT APPLICABLE**: DDC remains a pure-Python wheel project with no
Dockerfile, Compose file, container workflow or container requirement in its release
policy. This receipt certifies the dev4 candidate for the existing TDL-03B governed
main/certification/release and consumer-admission sequence. It does not itself merge,
release or authorize an immediate MLB switch. MLB production code/dependencies remain
unchanged. Scientific authority remains **0 AVAILABLE / 5 BLOCKED / 22 MISSING**.
