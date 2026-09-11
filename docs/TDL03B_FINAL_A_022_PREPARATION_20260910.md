# TDL-03B-FINAL-A: immutable 0.2.2 artifact preparation

Updated: 2026-09-10T18:19:18-07:00 (America/Los_Angeles).

**Final artifact locally validated; combined checkpoint BLOCKED.** No final
private CI was dispatched, no runner was polled, and no release/tag/merge occurred.
The production dependency URL cannot yet resolve because publication is withheld;
the private consumer also has not frozen executable production adapters/rollback.
Do not interpret successful final-wheel tests as completion of those requirements.

## Version and source authority

`PACKAGE_RELEASE_POLICY.md` governs semantic versioning, immutable GitHub Release
wheels, and architecture-certified release source on `main`. The TDL-03F migration
authority additionally preserves prepared 0.2.1 as rejected historical evidence.
Its compatibility-preserving optional-description correction uses the next patch
line, 0.2.2.dev1. Final **0.2.2** is the single selected production release identity:
it supersedes rejected 0.2.1, keeps the certified repair, and removes the development
suffix without a further contract change. Authenticated tag/release inventory at
preparation showed only published v0.1.0; v0.2.2 was unused. It is not published here.

- Certified development source: `13e9cf32a0be9dfec978f0d86215d428fd325e21`;
  tree `033fd06f0005b8f9faaa4071efd4449741c594af`.
- Certified dev wheel SHA-256:
  `4fda87bc841c0bf4e484d279a4334cbb69568ee1ca61483d4c59ba1895b21bed`.
- Private TDL-03F certification: workflow `TDL-MLB-PRIVATE-CERT`, ID 355211236,
  successful run 34540868207. This certifies the development artifact only.
- Final artifact source: `e877c852ba98c4742b6f9f5be55ba906eb9c0f38`;
  tree `779960bb4328ed812c24b1e9d70114bd9d7e3f67`.
- Final wheel: `daily_data_core-0.2.2-py3-none-any.whl`.
- Build A and build B SHA-256:
  `d18b1d30a343517b85d125c590aec2aace9bee3ab233ce8ba88a28a2c826c0ea`.
- Reproducible build: PASS, actual full-byte equality asserted.

Two separate clean Git-archive workspaces and fresh virtual environments installed
the pinned development lock independently. Both used CPython 3.12.10, pip 26.2,
pip-tools 7.6.1, build 1.5.0, setuptools 83.0.0, wheel 0.48.0, and
SOURCE_DATE_EPOCH=1787788800. Build isolation was disabled only after installing
that complete pinned toolchain. Wheels remain under ignored local
`.validation/final-a-wheel-one/` and `.validation/final-a-wheel-two/`.

## Exact delta from the certified implementation

Executable/package input delta is two lines only:

- `daily_data_core/version.py:1`: `0.2.2.dev1` becomes `0.2.2`.
- `pyproject.toml:7`: `0.2.2.dev1` becomes `0.2.2`.

The intervening f10786f documentation checkpoint also changes README.md,
docs/ARCHITECTURE_CERTIFICATION_LOG.md, docs/INTEGRATION_CONTRACTS.md,
docs/LOSSLESS_ACQUISITION_V2.md, docs/TDL03B_FINAL_RESUME_20260910.md, and
docs/TDL03F_OPTIONAL_DESCRIPTION_20260910.md. These are historical local-admission
documentation, not additional implementation changes. The complete source delta
is retained in Git. ZIP-member comparison asserts that all daily_data_core package
members are byte-identical except version.py; generated dist-info version/name and
RECORD changes are expected release metadata. No transport/parser/identity/PIT or
weather implementation changed.

## Executed local gates

- Final source suite: 144 passed (21.92 seconds).
- Clean hash-checked installation: version 0.2.2, direct_url wheel SHA-256 matched,
  import inside isolated site-packages; no editable or checkout fallback.
- Complete installed suite copied outside the checkout, isolated Python/importlib
  mode: 144 passed (15.26 seconds).
- Optional-description matrix passes in both full suites: absent/null/exact empty
  normalize to None; whitespace-only/non-string invalid; nonblank preserved.
  Required fields and exact raw evidence remain strict and unchanged.
- Ruff PASS; strict mypy across package/tests PASS, 28 files; pip check PASS.
- Runtime/dev lock regeneration: zero drift. Runtime digest
  `7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af`;
  dev digest `10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`.
- Runtime dependency audit: no known vulnerabilities.
- Final tracked-source secret scan: 65 files, no findings/errors; configured-secret
  count 0 and environment-file inspection disabled. No live credential test claimed.
- Private installed-final-wheel admission: four cases with two legacy/two DDC
  persisted quotes, quote/event/market/Value/raw-hash/clock equality, replay zero
  network calls, PIT, and SQLite integrity/foreign keys PASS. Six current conformance
  surfaces passed: 7 base, 80 comparison, 10 failure replay, 8 redirects,
  13 forecast-window/history, 23 weather-evaluation checks.

Private source/fixtures/receipts stay in Daily-MLB. No full new hosted MLB/Stats/
Linux/Docker certification is claimed for the differently versioned final artifact.

## Blocking release-distribution sequence

The governed final URL is:
`https://github.com/OneVillage83/Daily-Data-Core/releases/download/v0.2.2/daily_data_core-0.2.2-py3-none-any.whl`.

The private consumer's pinned pip-tools compiler was executed against this exact
URL/hash and returned HTTP 404 (exit 1). This is expected while publication is
prohibited, but it is not a successful production-lock resolution. The normal
production locks remain unchanged. An independently compiled, hash-pinned offline
validation lock installed the exact version by package name from a verified
wheelhouse; it is explicitly not the published-URL production authority.

The preparation request requires final certification before publication, whereas
the current package policy requires the released URL to compile the consumer's
production lock. Resolve that prepublication staging/production-lock boundary
explicitly before calling the complete cutover candidate READY. Do not fabricate
a successful URL fetch, hand-edit a compiled lock, publish early, or treat a local
wheelhouse as an already published GitHub Release.

The repaired private consumer contains admission projections and injectable legacy
collectors, not production DDC collector wiring or a runtime authority selector.
Its executable activation and rollback candidate therefore remains unfrozen.

## Preserved rejected lineage and next boundary

Prepared 0.2.1 source `9273b17a01529f949611a10b136c4e8446aa950a`, wheel SHA-256
`9c6a4e6132bfe6ce30244eea0f8d7bc666c9664c61221d173d1a10997f6c61b6`, remains
REJECTED BEFORE PUBLICATION, unchanged. No version/tag/asset was overwritten.
Production remains LEGACY_ACTIVE_PRODUCTION_AUTHORITY; scientific authority
remains 0 AVAILABLE / 5 BLOCKED / 22 MISSING.

The final artifact is frozen for a future Sol handoff, but the combined dispatch is
on HOLD until the missing production dependency and adapter/rollback candidate is
resolved. Then Sol must certify these final bytes and that exact consumer SHA/tree,
including full MLB/Stats/Linux/Docker V17 gates, and STOP. Subsequent owner/release
authorization, source-on-main verification, publication/tag, production pin,
adapter activation, migrated admission, 15-phase rehearsal, rollback proof, explicit
authority switch, legacy status transition, and final record remain separate steps.
