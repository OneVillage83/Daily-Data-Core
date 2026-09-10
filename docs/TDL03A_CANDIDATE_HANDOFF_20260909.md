# TDL-03A admitted candidate handoff

## Disposition

**TDL-03A COMPLETE: locally admitted unreleased candidate; no consumer switch.**
This supersedes the three-gap BLOCKED disposition in the retained TDL-03 receipt.
Production release certification, deployment and complete sport consumer adapter
equivalence are not claimed.

Branch: `codex/ddc6-mlb-migration-20260909`.
Starting parent: `c16e905a88eabaab398ab55111ace6352ae8154f`.
Original branch parent: `c4eee2245753aff22f5968da08db62b8259905a0`.
Implementation source: `0e49e98d636addc5e3150816ea4c596f64b34a81`.
Draft PR: https://github.com/OneVillage83/Daily-Data-Core/pull/4 (base main).
Final receipt successor changes documentation and generated lock-command comments/
CI compiler environment only; the final branch SHA is the Git/PR head, not a release tag.

## Reproduction and repair

Before editing, exact retained 0.1.1.dev1 wheel
`cb9a533aa126829bc2918988181ecbb126ba0e5e8a4167d98aeef1bf636b675f`
again failed partial-market retention, schema-error evidence and gust preservation;
the other four admission checks passed. No original admission assertion was weakened.

- Empty normalized children previously caused valid market/book containers to be
  discarded. Containers now survive, independently invalid siblings retain explicit
  source-path diagnostics, and source ordering/duplicate observations are preserved.
- HTTP/provider validation previously preceded construction of evidence envelopes.
  Exact received bodies now precede parsing; provider normalization and exceptions
  use a per-call evidence scope and append immutable versioned receipts. Replay,
  hash verification, retention denial, retry evidence and safe error boundaries are tested.
- ForecastSnapshot omitted OpenWeather gusts. The neutral mph field, explicit
  missing/unsupported/invalid/reported status and v2 JSON round-trip now preserve them.

The complete identity, atomicity, rights, serialization, clock and compatibility
contract is [LOSSLESS_ACQUISITION_V2.md](LOSSLESS_ACQUISITION_V2.md).
Additional bounded oracle reconciliation retained NWS valid period objects beside
non-object siblings and made OpenWeather invalid timestamps/details/pop fail explicitly.
No sport ontology, Value, Gate, model registry or scientific permission entered DDC.

## Artifact and installation

Candidate: `0.2.0.dev1` (unreleased minor contract evolution).
Wheel: `daily_data_core-0.2.0.dev1-py3-none-any.whl`.
SHA-256: `c9e5f44213146437bd8928ef705550acde817e8434fe3864b00e79db1cad5b0f`.
Source archive: implementation SHA above, extracted independently into two empty
build directories; both builds produced identical wheel hashes. Build command:
`python -m build --wheel --no-isolation --outdir <separate-output-directory>` with
`SOURCE_DATE_EPOCH=1787788800`, Python 3.12, build 1.5.0, setuptools 83.0.0,
wheel 0.48.0. Build inputs use the compiled DDC development lock.

Clean venv install used `--require-hashes`, the development lock and an explicit
local wheel URL/hash manifest. `python -I` imported version 0.2.0.dev1 from
site-packages. All 66 tests passed again from a separate tests-only directory with
`-I`, isolated pytest configuration, importlib mode and an assertion that the
package path is site-packages. No editable/source fallback is used in this evidence.

Compiled locks use pip 26.2/pip-tools 7.6.1. Both regenerate byte-identically in
the clean environment. A compiler-header difference (`--no-index` inferred by one
environment) was resolved with the same explicit CUSTOM_COMPILE_COMMAND in CI and
local compilation, without hand-editing hashes. Runtime dependency versions are unchanged.
Windows compiler-output SHA-256:

- requirements.txt: `7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af`.
- requirements-dev.txt: `10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`.

The 0.1.0 release and retained 0.1.1.dev1 wheel were not replaced or republished.

## Validation

- DDC full source suite: **66 passed** (41 inherited plus 25 additional cases).
- Installed wheel full suite: **66 passed**, 0.57 seconds.
- Ruff passed; strict mypy passed **22 source/test files**.
- Clean hash-locked installation and `pip check` passed.
- Runtime/development lock audit: **no known vulnerabilities**.
- Public source scan: **48 tracked files**, zero findings/errors; no configured
  secret values supplied. Only generic source and synthetic tests entered DDC.
- Exact-wheel MLB admission: **7/7 passed**, zero provider requests.
- Current MLB legacy oracle group: **119 passed**, 8.51 seconds.
- Direct wheel-vs-current-MLB comparison: **80 checks passed**, including provider
  identities, normalized values, duplicate/order/partial behavior, errors/raw semantics,
  gust null/zero/value, clocks, NWS metadata and implied/no-vig/hold math.
- MLB Ruff passed; full mypy passed **764 files**. No MLB runtime/lock changed.

No remote CI, Docker, live-provider or production migration certification is claimed.

## Intentional differences and consumer boundary

DDC exact bytes and typed facts remain distinct from MLB sanitized canonical export
bytes. UTC timestamps compare by instant; legacy display-offset strings stay in raw
evidence. Source-path diagnostics add auditability rather than reproducing the legacy
warning envelope. Invalid optional odds timestamps become unknown with warnings,
not quote rejection. Empty HTTP bodies and malformed JSON now remain evidence.
The inherited UTC/DST and URL/timezone safety fixes remain in force.

MLB's 60-minute window, output formatting, canonical identity, field-relative wind,
publication and scientific permissions remain consumer policy. DDC exposes explicit
window validation; it does not impose MLB's window universally. Full persisted
consumer adapter/replay equivalence remains TDL-03B work, not a claimed result here.
Scientific authority remains **0 AVAILABLE / 5 BLOCKED / 22 MISSING**.

## Lower-cost validation / exact resume

Validate the final recorded PR head and confirm packaged source equals implementation
SHA above. Run DDC `CI` / `quality` in `.github/workflows/ci.yml`: Python 3.12,
pinned bootstrap, hash install, lock regeneration with the workflow's compiler env,
pytest, Ruff and strict mypy. Rebuild from the exact source and verify the recorded
wheel digest. Repeat isolated wheel installation/tests and the private MLB commands
recorded in its TDL-03A handoff. Record actual run/job/source IDs; none are supplied
by this local implementation job. Do not replace a release or merge without authority.

DDC has no container runtime to certify in this job. MLB private Docker/runtime/
schema certification belongs to the later approved consumer switch and remains
subject to its private CI restriction. Never copy private MLB source, data, fixtures,
logs, A1/A2/V17 artifacts or credentials into this public repository or its public mirror.
Return substantive provider/evidence/schema/PIT/package/security/equivalence failures
to Astra; ordinary runner/lock mechanics remain validation work.

Next: TDL-03B resumes the certified-release gate and bounded MLB compatibility
adapters, hash-locked consumption and complete persisted/replay equivalence before
retiring the legacy implementation.
