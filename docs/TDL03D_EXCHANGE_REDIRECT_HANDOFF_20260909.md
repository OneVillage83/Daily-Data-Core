# TDL-03D HTTP exchange and redirect evidence

Updated: 2026-09-09T20:49:17-07:00 (America/Los_Angeles).

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
