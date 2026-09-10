# TDL-03B resume: redirect physical-evidence blocker

TDL-03D continuation: this historical dev2 defect is repaired in local dev4;
read `TDL03D_EXCHANGE_REDIRECT_HANDOFF_20260909.md` first. Release and MLB cutover
remain withheld pending the delegated validation and governed release sequence.

Updated: 2026-09-09T20:23:14-07:00 (America/Los_Angeles).

**BLOCKED before release or consumer migration.** The certified candidate's existing
tests remain valid within their exercised scope, but a new Requests redirect
counterexample demonstrates incomplete physical-exchange evidence. This is a shared
transport/evidence defect, not an owner-approval or remote-CI waiting condition.

## Exact authority and release reconciliation

Source branch: `codex/ddc6-mlb-migration-20260909`.
Starting documentation head: `e0ad42de53a3cf9a633381241482a0ed592e84d7`.
Previously tested implementation head: `7e476c6a06479ea16f1fb1d83616678a0e3153a8`,
tree `016d50e42aad77ec1841605fe97a1ddca69b769a`.
Candidate remains **0.2.0.dev2**, wheel SHA-256
`f8831a6f4f1a726b41d1b72a4b7196cf1e100fd8b41d7137786452005a7e6a5a`.
Draft PR #4 is retained. Published v0.1.0 is unchanged.

PACKAGE_RELEASE_POLICY requires a certified commit on main and an immutable versioned
GitHub Release wheel consumed through compiled hash locks. No additional owner
approval rule was found in that policy; GitHub reports main is not protected and
lists no rulesets. This is not permission to waive any source/conformance gate.
The current task authorizes controlled release after those gates pass. No final
version/tag was assigned, merged or published because conformance failed first.
Renaming dev2 would require a new artifact and repeated validation; it cannot fix
this defect or inherit unqualified certification.

## Deterministic counterexample

The private consumer now retains executable gate
`scripts/check_ddc6_redirect_history.py`, contract
`DDC6_REDIRECT_PHYSICAL_HISTORY_ADMISSION_V1`. It first hashes/imports the exact
wheel, then invokes its TheOddsApiClient with a real requests.Session. A synthetic
BaseAdapter replaces network sends, leaving Requests' real redirect machinery active.
The built-in network adapter is patched to fail if called. No live/provider request,
secret or licensed evidence is used.

The fixture sends HTTP 302 (body `redirect evidence`, quota remaining 10, same-origin
Location), then HTTP 200 (body `[]`, quota remaining 9). The second body is a valid
empty slate. EvidenceLedger explicitly permits raw and history retention and reloads
the persisted v3 history before strict replay.

Actual result, twice reproduced against the same wheel: **exit 1**.

| Fact | Transport fixture | Persisted DDC history |
| --- | --- | --- |
| Physical exchanges | 2 | 1 |
| Status sequence | 302, 200 | 200 |
| Response bodies | redirect evidence, [] | [] |
| Quota observations | 10, 9 | 9 |
| Diagnostics attempts | required to explain both exchanges | 1 |

Strict replay reproduces the retained incomplete history without network activity;
that does not recover the omitted redirect response. Three gate assertions fail:
every physical exchange persisted, every response body persisted, and redirect quota
observation persisted. Three fixture/replay controls pass; actual network calls: 0.

## Root cause and bounded repair boundary

HttpClient.get_json_recorded calls session.get with Requests' default automatic
redirect following. One call can therefore issue multiple lower-level HTTP exchanges.
DDC captures only the returned terminal Response; response.history is ignored.
The current attempt loop counts outer retry iterations, not every physical exchange.
Earlier tests replace Session.get directly, so they do not exercise this behavior.

The next DDC job must reconcile allowed redirects, exchange/attempt identity, limits,
raw bytes, quota, timestamps and safe target handling in the shared transport. It
must either reject redirects explicitly before another send or represent every
permitted exchange with immutable evidence; accepted provider behavior must decide
the policy. Do not guess historical clocks, silently drop redirect evidence, disable
the gate, or work around this in MLB. After a repair, use a new candidate identity,
rerun this counterexample plus all existing gates, and then resume release preparation.
This handoff does not choose or implement a new redirect architecture.

## Validation and production disposition

Fresh unchanged-source DDC suite: **85 passed**; Ruff passed; strict mypy **24 files**.
The previous persisted-replay gate still passes **10/10**, admission **7/7**, legacy
comparison **80/80**, and MLB oracle **119 passed**. These results do not include the
new redirect requirement. No prior assertion was weakened.

Full MLB Ruff passed; strict mypy passed **766 files**. Final source scans passed
**53 DDC / 1,057 MLB files**, zero findings. The private gate itself type-checks
without suppressions; it intentionally returns failure for the rejected candidate.

No DDC source or package metadata changed; only documentation records this blocker.
No release/tag/main merge or new remote workflow was performed. MLB remains on
legacy production authority with unchanged dependencies, adapters and persisted data.
No new DDC-backed 15-phase run or cutover proof is claimed. Scientific inventory
remains **0 AVAILABLE / 5 BLOCKED / 22 MISSING**.

Lower-cost validation can reproduce the gate with the exact wheel above; it must
remain red until shared evidence conformance is repaired. Do not poll old green
Actions run 34431413425 as if it covered redirects. Following the repair, validate
the new candidate with DDC CI, isolated installed-wheel tests, 7/7 admission, 10/10
retry replay, 80 comparisons, the redirect gate and MLB oracle before release.
