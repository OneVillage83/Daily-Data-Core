# TDL-03E forecast-window lineage repair

Certification continuation: read `TDL03E_CI_CERTIFICATION_20260909.md`. DDC exact
source and candidate passed hosted CI; required private MLB exact-head CI remains
blocked before steps by account billing/spending limits. TDL-03B-FINAL is not ready.

Updated: 2026-09-09T22:06:11-07:00 (America/Los_Angeles).

DDC branch `codex/ddc6-mlb-migration-20260909`, draft PR #4; parent documentation
head `8ce1a62a348d42da428e4cc928668de069703415`.
Implementation **`66673b279484497f04e5b8972db7d4affb44d9d1`**, tree
`e78b0e06627bfbe55f0bb38d99a714d4ef0ad843`.
Candidate **0.2.1.dev1**, unpublished; wheel `daily_data_core-0.2.1.dev1-py3-none-any.whl`,
SHA-256 **`1bffac282d8de69ca63c555ba43ec31d1418c923defa9df143ffa7d96a22614e`**.
Two clean archives of the implementation commit built byte-identically under
Python 3.12.10, pip 26.2, build 1.5.0, setuptools 83.0.0, wheel 0.48.0,
SOURCE_DATE_EPOCH=1787788800. Local artifacts: `.validation/tdl03e-wheel-one/`
and `tdl03e-wheel-two/`. The prepared 0.2.0 and dev4 artifacts remain unchanged.
This compatibility-preserving correction uses a new patch-development identity;
no tag, release, merge or sport-consumer switch occurs in this task.

## Reproduction and ownership

Before repair the unchanged private weather admission gate reproduced **7/13**
against prepared 0.2.0. For each of NWS/OpenWeather, error history, diagnostics and
replayed-error history linkage failed (six failures). Raw evidence was intact.
DDC's `require_window` created a new exception after acquisition completed without
attaching the existing result history and request diagnostics.

DDC now exposes `WeatherWindowRejected`, retaining the historical exception base
for compatibility while distinguishing a consumer constraint from provider schema
failure. It carries the original history, raw/evidence tuples, request diagnostics
and immutable neutral `ForecastWindowEvaluation`. The latter binds forecast and
history IDs, target, caller-supplied duration, signed offset and before/after/accepted
reason under `ddc-forecast-window-evaluation-v1`. It does not select an MLB policy.
No completed acquisition history is rewritten and no new provider identity is made.

`ddc-weather-evidence-v1` is a reference-only envelope: forecast, source clocks,
fact identity, raw/evidence IDs, package/parser/code references, history,
LogicalCall/Attempt/Exchange references and per-call diagnostic digests.
`verified_evidence_document(ledger)` reopens retained history/raw evidence and
checks the normalized fingerprint before consumer admission. Accepted and rejected
paths use this same contract. Existing history/forecast schemas are unchanged;
missing older lineage is not invented. Exact raw bytes stay in the authorized ledger.

The private MLB layer now owns a separate immutable evaluation with game/snapshot,
first-pitch target, evaluation timestamp, policy/version, wheel/code identities,
explicit disposition/reasons and prior-decision lineage. It uses additive private
SQLite evidence storage and the existing atomic artifact publication boundary.
DDC contains no game identity, sport freshness threshold or prediction-readiness rule.

## Local evidence

- DDC source **120 passed** (12.26 s), Ruff passed, strict mypy **27 files** passed.
- Fresh hash-installed wheel **120 passed** (11.60 s), outside the checkout using
  isolated import mode and assertions for site-packages/version; pip check passed.
- Original weather gate **13/13**, redirect **8/8**, persisted replay **10/10**,
  base admission **7/7**, legacy/wheel comparison **80/80**.
- Additional private consumer evaluation/persistence gate **23/23**: both providers,
  accepted/before/after, restart/replay, acquisition hierarchy and linked reprocess.
- All final offline gate actual network counters **0**.
- Dependency locks regenerate with zero diff using pip-tools 7.6.1; hash-locked
  vulnerability audit reports no known vulnerabilities.
- Private affected weather/Data Quality/controller tests **238 passed**; final
  evaluation tests **14 passed**; retained MLB oracle **119 passed**. Focused Stats
  under the development environment **324 passed, 2 skipped** (optional installed
  profile checks). MLB Ruff and strict mypy **770 files** passed.
- Optional full MLB suite was stopped at roughly 4% due to slow unrelated tests;
  no completed full-suite certification is claimed.
- Tracked-file secret scans passed: DDC **60**, MLB **1,065** files, no findings;
  `--skip-env` excludes local environment files. Final diff checks passed.

Test-harness incident: an initial new unit test mocked Session.get while the
transport used its adapter. Three synthetic-key OpenWeather requests returned 401.
No real credential was supplied and no live validation success is claimed. The
test now intercepts HTTPAdapter.send; corrected source/installed suites and final
admission/replay checks use offline fixtures. The 401 attempts are not included in
the final gates' zero-network claim.

## Disposition and operator handoff

The forecast-window blocker is repaired locally. TDL-03B-FINAL may resume its
governed release and actual consumer-admission work after delegated exact-source
validation. This is not completed DDC-6 migration or release certification.
Legacy remains ACTIVE_PRODUCTION_AUTHORITY; scientific inventory stays
0 AVAILABLE / 5 BLOCKED / 22 MISSING. No PIT, registry, model or Gate permission changes.

Lower-cost validator: verify the implementation SHA/tree and documentation-only
head delta, build twice and verify the digest above, hash-install outside checkout,
run the source/installed suites, original five gates plus the new private consumer
gate, MLB regression, static checks, lock regeneration and security checks; then
run authoritative exact-head hosted CI. Preserve private/public boundaries: do not
copy MLB code, the new consumer gate, private evidence or raw data into public DDC
or expand the public-CI allowlist. Old dev4 hosted CI is historical only.
No remote CI or Docker ran here; Docker is not a DDC wheel release requirement.
