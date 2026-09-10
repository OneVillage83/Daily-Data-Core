# TDL-03F optional quote description contract and repair

Updated: 2026-09-10T15:15:00-07:00 (America/Los_Angeles).
Status: COMPLETE (local repair/admission) / UNRELEASED; no consumer authority switch.
Final local validation recorded 2026-09-10T15:33:00-07:00.

The exact prepared 0.2.1 wheel reproduces the private persisted 2-versus-1 quote
mismatch, with identical source hash and deterministic incorrect replay. New
generic regressions fail before repair: 8 failed, 16 passed. The responsible
predicate is the required nonblank `_string` applied to optional description
inside `_parse_market`'s whole-outcome validation block. Persistence and consumer
identity divergence follow quote exclusion; neither layer originally loses bytes.

## Governing interpretation

LOSSLESS_ACQUISITION_V2 separates required structural validity from optional
metadata and preserves independently valid siblings, raw values and participant
labels. The current consumer oracle accepts a quote with empty optional text;
the owner's TDL-03F instruction explicitly requires restoring that compatibility.
This clarification applies to OddsOutcomeSnapshot, not every optional text field:

| Provider field | Normalized participant_description | Quote treatment |
| --- | --- | --- |
| Absent | None | Retain if required fields valid |
| JSON null | None | Retain if required fields valid |
| Exactly empty string | None | Retain if required fields valid |
| Whitespace-only string | Invalid | Reject quote; diagnose source path |
| Non-string non-null | Invalid | Reject quote; diagnose source path |
| Nonempty nonblank string | Exact supplied string | Retain if required fields valid |

Whitespace around a nonblank label is not stripped: existing labels may bind
consumer identity. There is no conversion of numbers/booleans/objects to strings.
Required name/price/point validation remains unchanged. Normalized construction
enforces the same rule as provider decoding, so callers cannot bypass it.
Raw bytes, missing-vs-null-vs-empty distinctions and hashes are never modified.
The MLB compatibility projection preserves raw optional representation while
DDC's typed neutral object uses canonical None; these are distinct contracts.

## Identity and history

No identity algorithm changes. Descriptions are not universally human-readable
decoration: consumers can use participant labels for team/player binding. Keep
them in normalized fingerprints and retain existing sport subject/query rules.
Response/observation identity remains bound to original bytes/clocks/source path;
different raw payloads are not forced to share identities merely because their
normalized description is None. Restored outcomes recover their original source
ordinal and consumer event/row identity. Do not remove metadata from hashes.

Parser identity advances to ddc-the-odds-api-v3 because normalization changed.
Strict replay of old-parser history under new code must still fail closed;
explicit reprocessing may create linked interpretation while preserving old
calls/attempts/exchanges and clocks. Current-parser strict replay must reproduce
the repaired result without network. No HTTP/history/weather implementation changes.

## Artifact consequence

PACKAGE_RELEASE_POLICY's publication immutability alone does not declare every
unpublished filename permanently reserved. However, the current TDL-03B handoff
explicitly binds retained candidate bytes and requires a newly versioned successor
for changed semantics. Follow that stricter migration authority: 0.2.2.dev1.
Prepared 0.2.1 at hash
9c6a4e6132bfe6ce30244eea0f8d7bc666c9664c61221d173d1a10997f6c61b6 remains
retained, REJECTED BEFORE PUBLICATION; do not overwrite or publish it. Certified
dev1 and published 0.1.0 remain untouched. No tag/release/pin/cutover in TDL-03F.

## Exact corrected artifact and local validation

Branch: `codex/ddc6-mlb-migration-20260909`, draft PR #4.
Implementation: `13e9cf32a0be9dfec978f0d86215d428fd325e21`.
Source tree: `033fd06f0005b8f9faaa4071efd4449741c594af`.
Version: `0.2.2.dev1`; wheel: `daily_data_core-0.2.2.dev1-py3-none-any.whl`.
SHA-256: `4fda87bc841c0bf4e484d279a4334cbb69568ee1ca61483d4c59ba1895b21bed`.
Two clean Git-archive builds are byte-identical (SOURCE_DATE_EPOCH=1787788800;
CPython 3.12.10, build 1.5.0, setuptools 83.0.0, wheel 0.48.0).
Local retained outputs: `.validation/tdl03f-wheel-one/` and `tdl03f-wheel-two/`.
Later documentation commits do not change this artifact's implementation identity.

- Final source suite: 144 passed in 15.17s; Ruff passed; strict mypy 28 files passed.
- Exact hash-locked wheel in a new isolated environment, tests copied outside source:
  144 passed in 15.11s; isolated import/site-packages/direct_url digest verified.
- Permanent optional-description regression: 24 passed, versus 8 failed before repair.
- Runtime/development locks regenerated without drift; both environments' pip check
  passed; runtime pip-audit found no known vulnerabilities.
- Tracked-source secret scan: 64 files, no findings; configured-secret count 0,
  environment files deliberately not inspected. This is not a live credential test.
- Exact-wheel fresh-process consumer gates: package 7/7, comparison 80/80,
  failure replay 10/10, redirect history 8/8, forecast history 13/13,
  weather evaluation 23/23; zero network calls throughout.
- Private consumer persisted admission V2: four description variants, legacy 2 and
  candidate 2 quotes each; identical reopened SQLite rows, event/value identities,
  raw evidence, verified durable market inventory and Value-input evaluation.
  Strict retained-history replay reproduces the same persistence/Value payloads,
  network 0. SQLite integrity and foreign keys pass. Future observations remain
  rejected at prediction time; original acquisition clocks are retained.

The private consumer additionally corrected its existing A2 raw-offer constructor's
same premature required-text rejection, canonicalizing exactly empty to None before
unchanged subject binding. TEAM/PLAYER requirements remain fail-closed. This was
needed even on the legacy side of the newly exercised Value-input path; it is not
a DDC fallback or production activation. Private fixtures/code remain private.
Consumer focused suite: 68 passed; Ruff and strict mypy 774 files passed.

## Governed continuation

TDL-03B-FINAL resume: READY because persisted equivalence and bounded dual-path
admission now PASS. This is local repair certification, not new hosted/private CI
certification or production cutover certification. No hosted work was dispatched
or polled. Prior exact-source receipts do not certify these changed implementation
bytes. Sol must certify this successor and the exact private consumer successor;
the private handoff records checkout identities and explicit wheel-gate commands.
Do not reuse old default SHAs/artifacts. Keep immutable bad-candidate evidence.

Then resume the separately governed final-version/reproducibility certification,
immutable release, exact consumer hash pin, active adapter proof, migrated PIT/replay,
15-phase rehearsal, rollback proof and final private certification. A final-version
build has different bytes and requires its own hash and gates. Do not publish this
development candidate or rejected 0.2.1 as an implementation shortcut.
Scientific authority remains 0 AVAILABLE / 5 BLOCKED / 22 MISSING;
production remains LEGACY_ACTIVE_PRODUCTION_AUTHORITY. No full consumer suite,
Docker rebuild, live provider validation or cutover was claimed by this bounded job.
