# DDC-6 current-consumer release admission

Current disposition: the TDL-03A successor resolves the three gaps below and admits
the unreleased 0.2.0.dev1 candidate locally. See
[TDL03A_CANDIDATE_HANDOFF_20260909.md](TDL03A_CANDIDATE_HANDOFF_20260909.md).
The remainder of this file is the retained pre-TDL-03A evidence record.

Updated: 2026-09-09T16:49:00-07:00 (America/Los_Angeles).

## Disposition

**TDL-03 BLOCKED on shared provider/evidence contract compatibility.** DDC-6 has
not switched the MLB runtime. The published foundation's historical DDC-0–5
certification remains a retained record, but it does not prove conformance to the
September consumer or the newly tested temporal/security cases below.

DDC parent: `c4eee2245753aff22f5968da08db62b8259905a0` (`main`). Work branch:
`codex/ddc6-mlb-migration-20260909`. Locally tested implementation:
`fdfddcf710248a0836d9501648e42e3945330685`; draft PR
https://github.com/OneVillage83/Daily-Data-Core/pull/4. The final receipt is a
documentation-only successor; its SHA is available from Git/PR head. A rebuild
from the committed source retained the candidate wheel hash below. Tracked source
scan passed 44 files with zero findings/errors and no configured secrets supplied.
MLB work is a descendant of its current
documentation receipt, preserving its unmerged PR stack; no production release,
tag move, asset replacement, model permission or consumer switch occurred.

## Exact existing release

The release API and downloaded bytes agree:

- Tag `v0.1.0`; source `0e7e918b1a1157d48a4eecd2c6ca6e61554cc6b0`.
- Wheel `daily_data_core-0.1.0-py3-none-any.whl`, 19686 bytes.
- SHA-256 `5939e70fe5eab5d30b2c4875f50732cd3e94921561afbd0237320ef934ced1e5`.
- Existing release run `33009682975`, job `98312416283`; these are inherited
  records, not new validation of this branch.

The offline consumer admission command imports the verified wheel directly,
without a sibling-source fallback or a provider request. The v0.1.0 wheel failed
all seven new necessary admission checks. These are counterexamples, not an
exhaustive equivalence claim.

## Safe repairs completed

The candidate fixes four admission failures:

1. NWS validates the provider-directed hourly URL before transport: HTTPS, exact
   NWS hostname, allowed hourly path, no userinfo/query/fragment, valid port.
   Invalid URL values are not echoed into errors.
2. Exact rest/travel arithmetic uses UTC instants across DST; reversed instants
   during a repeated local hour fail closed.
3. Provenance eligibility, observation ordering and quote age compare UTC
   instants rather than ignoring repeated-hour offsets.
4. Neutral venue timezone names must resolve through ZoneInfo.

Odds transport now accepts the existing structural HTTP protocol, as weather
already did. This changes typing, not provider selection. The package includes a
PEP 561 marker, pins setuptools 83.0.0 for wheel construction and uses development
version `0.1.1.dev1`. It is **not released or certified**. Existing v0.1.0 assets
and tags remain untouched. Generated build/validation directories are excluded
from source type discovery, not from runtime validation.

## Exact unresolved compatibility boundary

Three necessary admission checks still fail against the candidate wheel:

- A partly malformed odds market loses its empty market/book structures in the
  normalized result. The consumer preserves them, granular warnings and raw
  evidence to distinguish invalid input from a valid empty result.
- A provider schema failure exposes no raw payload/evidence handle. The required
  evidence-before-normalization boundary must cover invalid/non-list/all-invalid
  payloads and HTTP/JSON failures, not only successful parsed results.
- OpenWeather's shared forecast contract drops wind gust, a current consumer fact.

Additional adapter equivalence remains required for exact timestamp strings,
forecast-window policy, provider update/fallback fields, all-book ordering,
diagnostics, provider extras and persisted compatibility artifacts. MLB's 60-minute
forecast selection policy remains a consumer requirement; it is not a universal
DDC default. Existing provider-specific exception types alone do not fulfill the
durable error-evidence requirement.

The remaining repair is a versioned shared result/error-evidence contract, followed
by a new certified immutable release and consumer adapters. Re-parsing provider
payloads permanently inside MLB or dropping evidence to fit v0.1.0 would violate
the migration ownership/equivalence gate. Publishing this partial candidate as a
certified production package would also violate PACKAGE_RELEASE_POLICY.md.

## Local validation and build evidence

- Initial 12 new regressions failed against unchanged source before repair;
  `.validation/ddc6-release-boundaries-before.log` records exact failures.
- After repairs: **41 tests passed**, including the original 28; strict
  `python -m mypy .` passed **20 source/test files**; Ruff passed.
- Runtime hash-locked audit: no known vulnerabilities.
- Two Python 3.12 builds with `SOURCE_DATE_EPOCH=1787788800`, build 1.5.0,
  setuptools 83.0.0 and wheel 0.47.0 produced identical candidate wheel bytes:
  `daily_data_core-0.1.1.dev1-py3-none-any.whl`, SHA-256
  `cb9a533aa126829bc2918988181ecbb126ba0e5e8a4167d98aeef1bf636b675f`.
- Clean environment hash-locked runtime plus candidate-wheel installation passed;
  `pip check` passed and isolated import reported `0.1.1.dev1` from site-packages.
  The local install manifest is validation-only, not a consumer production lock.
- Candidate admission: four passed, three failed, zero network requests. Failed
  admission is deliberately nonzero and is not converted to a passing test.

DDC tests ran using the existing Python 3.12 MLB development toolchain; this is not
a claim of a fresh DDC development-lock installation or lock-regeneration proof.
Those release checks remain with the validator. The current DDC bootstrap lock
still records pip 26.1.2; the release job must reconcile its known tooling advisory
through compiled locks rather than hand-editing hashes. Runtime locks are unchanged.

## Handoff and next bounded work

Complete the shared raw-response/evidence/error contract and lossless provider
normalization before the consumer switch. Extend synthetic tests in DDC and the
retained consumer oracle; do not import sport identity, Value, Gate or model policy.
After conformance passes, follow the existing reviewed-main/certified-release gate
with a new version, record its immutable artifact hash, then compile the actual
consumer runtime/development/Stats locks and finish the adapters/replay regression.

This public DDC repository contains only generic source and synthetic tests. MLB
fixtures, evidence, databases, provider captures, logs and proprietary source must
remain private. No remote CI was run or polled. A lower-cost validator may validate
the safety patch with the repository `CI` workflow, but a green patch run cannot
waive the three remaining admission failures or certify DDC-6. Return substantive
provider/evidence/PIT/package/security failures to the architecture agent.
