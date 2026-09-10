# TDL-03E exact-source certification

Updated: 2026-09-09T23:24:02-07:00 (America/Los_Angeles).

## Disposition

DDC candidate **0.2.1.dev1 is exact-source certified** for the scope of TDL-03E.
The combined DDC/MLB migration checkpoint disposition is
**LOCALLY-VALIDATED-REMOTE-CERTIFICATION-BLOCKED** because the required private
Daily-MLB exact-head workflow could not start any job steps under the account
billing/spending restriction. Therefore TDL-03B-FINAL resume is **NOT READY**.
No source failure was found. No release, tag, merge, dependency switch or cutover occurred.

## Exact source and artifact mapping

- Branch: `codex/ddc6-mlb-migration-20260909`; draft PR #4.
- Authoritative implementation: `66673b279484497f04e5b8972db7d4affb44d9d1`.
- Implementation tree: `e78b0e06627bfbe55f0bb38d99a714d4ef0ad843`.
- TDL-03E documentation head: `3dd739a0748b7f94cceb86eb4e9b7b79ab1d14e6`.
- Documentation tree: `a8c38930253feebff292fd56b906838d3be6bbf1`.
- Hosted-CI validation commit: `027fd100cc562184ca2f217bfaafcd24a423faae`.
- CI validation tree: `a8c38930253feebff292fd56b906838d3be6bbf1`.

The delta from implementation to documentation head is exactly README plus four
files under `docs/`. The validation commit is empty and tree-identical to the
documentation head. Excluding README/docs, implementation, documentation and CI
validation commits have no differences. Candidate executable/package source is
therefore exactly the implementation at `66673b2`.

Candidate wheel: `daily_data_core-0.2.1.dev1-py3-none-any.whl`.
SHA-256: **`1bffac282d8de69ca63c555ba43ec31d1418c923defa9df143ffa7d96a22614e`**.
Two fresh independent Git-archive builds of the implementation commit reproduced
that expected digest exactly. Build authority: Python 3.12.10, pip 26.2,
pip-tools 7.6.1, build 1.5.0, setuptools 83.0.0, wheel 0.48.0,
`SOURCE_DATE_EPOCH=1787788800`. Operator artifacts are retained in ignored paths
`.validation/tdl03e-ci-wheel-one/` and `tdl03e-ci-wheel-two/`.

Runtime lock SHA-256: `7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af`.
Development lock SHA-256: `10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`.
Regeneration under the governed command/toolchain produced zero Git diff.

## Independent local validation

- Clean `--require-hashes` installation from the newly rebuilt wheel: PASS.
  Version `0.2.1.dev1`; import resolved under the isolated environment's
  `Lib/site-packages`; no editable/source fallback; `pip check` PASS.
- DDC source suite: **120 passed** in 15.66 s.
- Isolated installed-wheel suite: **120 passed** in 21.12 s, `-I` and importlib mode.
- Forecast-window lineage: **13/13 PASS**.
- Private MLB persisted weather/lineage: **23/23 PASS**.
- Redirect/exchange: **8/8 PASS**.
- Persisted failure replay: **10/10 PASS**.
- Base DDC-6 admission: **7/7 PASS**.
- Legacy/wheel equivalence: **80/80 PASS**.
- All six final gate network counters: **0**.
- DDC Ruff PASS; strict mypy PASS, **27 source files** locally.
- DDC dependency consistency, runtime audit and secret scan PASS; no known
  vulnerabilities and no secret findings across **61 tracked files** (`--skip-env`).

The corrected gates made no provider calls. The earlier three synthetic-key 401
requests remain a historical harness incident documented in the implementation
handoff and are excluded from the final zero-network gate receipts.

## Hosted DDC CI

Workflow `CI` passed twice on exact validation commit
`027fd100cc562184ca2f217bfaafcd24a423faae`, tree
`a8c38930253feebff292fd56b906838d3be6bbf1`, CPython **3.12.14**:

- Pull-request run **`34440886749`**, quality job **`102755498146`**: SUCCESS.
- Push run **`34440884123`**, quality job **`102755490255`**: SUCCESS.

Both jobs executed Checkout, Python setup, pinned bootstrap, hash-locked dependency
installation, zero-drift lock regeneration, pytest (**120 passed**), Ruff and mypy
(**14 reported source files**) successfully. No required step was skipped.

DDC is a pure-Python wheel project. Docker remains **NOT APPLICABLE** under current
release authority.

## Private MLB limitation and exact handoff

Private MLB validation commit `4a7c182716a0d2140021a1310e1adb0224a823d4`, tree
`91441fab2e9c31ba6c075ef640b49e3e9ade7184`, is empty and tree-identical to
TDL-03E receipt head `acedf2231930b18df4d84b2500f03aaf29e8c23c`.
It retains the tested implementation `61944cc2d4c1974c6b3a92a6d790cf9b5b128e80`;
the intervening commit changes the handoff only.

Workflow `quality` run **`34440983309`** failed before steps on all four jobs:
docker-runtime `102755785676`, python-quality `102755785871`, linux-security
`102755785937`, stats-quality `102755785944`. Each job has `steps=[]`. GitHub's
failure annotation says the job did not start because recent account payments
failed or the spending limit must be increased. This is infrastructure evidence,
not a Docker, test, source or security failure. It was attempted once and not retried.

Private MLB local evidence on exact tree `91441f`: complete development suite
**2,912 passed, 12 skipped, 1 warning** in 2,800.25 s. The warning is the existing
Starlette/httpx test-client deprecation. Skips: two optional Stats-profile tests,
eight Windows symlink-privilege cases and two additional symlink-unavailable cases.
The clean hash-locked Stats environment then passed **326/326** focused tests in
258.80 s; offline pybaseball compatibility passed with network requests 0.
Separately: retained oracle **119 passed**, affected suite **238 passed**, final
TDL-03E tests **14 passed**. MLB Ruff/mypy (770 files), dev/stats dependency checks,
audits, hash-locked dry runs, schema v17 integrity/foreign keys and secret scan passed.

No public mirror can certify the new private MLB evaluation/persistence source, so
none was used. When private Actions capacity is restored, rerun the exact-tree MLB
workflow and require all declared jobs/steps to execute successfully. If green,
append its run/job receipt and change the combined disposition to
`CERTIFIED-FOR-TDL-03B-FINAL-RESUME`; do not repeat DDC architecture work. Return
substantive source/PIT/evidence/security failures to Astra. Production locks remain
unchanged, legacy remains ACTIVE_PRODUCTION_AUTHORITY and scientific authority
remains 0 AVAILABLE / 5 BLOCKED / 22 MISSING.
