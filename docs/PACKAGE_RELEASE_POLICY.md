# Daily Data Core Package Release Policy

Last updated: 2026-09-10T18:48:47-07:00 (America/Los_Angeles)
Status: **GOVERNING**

## Purpose
Daily-Data-Core is a shared library consumed by separate sport repositories. A consumer must be able to reproduce the exact DDC code it used without depending on a moving branch or an unhashed VCS checkout.

The Daily Line quality baseline also requires compiled dependency locks installed with `--require-hashes`. Therefore a raw dependency such as:

```text
git+https://github.com/OneVillage83/Daily-Data-Core.git@main
```

is **not** an acceptable production dependency.

## Distribution decision
Certified DDC versions are distributed as versioned pure-Python wheel artifacts attached to a versioned GitHub Release/tag and treated as immutable by repository policy.

Initial certified foundation release:

```text
release: v0.1.0
wheel:   daily_data_core-0.1.0-py3-none-any.whl
sha256:  5939e70fe5eab5d30b2c4875f50732cd3e94921561afbd0237320ef934ced1e5
source:  0e7e918b1a1157d48a4eecd2c6ca6e61554cc6b0
```

The complete published artifact record is `RELEASE_V0.1.0.md`.

A release is created only from an architecture-certified commit on `main`.

## Consumer requirement form
A sport repository consumes an exact released wheel URL, for example:

```text
daily-data-core @ https://github.com/OneVillage83/Daily-Data-Core/releases/download/v0.1.0/daily_data_core-0.1.0-py3-none-any.whl
```

The sport repository then compiles its normal Python 3.12 lock with `pip-tools --generate-hashes`. The compiled lock, not the moving GitHub branch, is the runtime installation authority.

The compiled consumer lock must resolve the expected wheel digest recorded in the release record. If the resolver/toolchain cannot emit a hash for the direct wheel URL, the migration stops and the release/distribution mechanism is corrected before production integration. `--require-hashes` is not disabled to make the dependency easier to install.

## Release construction
From the exact certified commit under Python 3.12 with a pinned build toolchain, build a pure-Python wheel and verify it in a clean environment before publication.

Required release verification includes:
- exact package version and wheel filename;
- clean-environment installation;
- imported `daily_data_core.__version__` equals the release version;
- expected package modules are present in the wheel;
- wheel SHA-256 is calculated and recorded;
- source commit is architecture-certified;
- release publication targets that exact source commit.

The release record must include:
- DDC version;
- source commit SHA;
- tag;
- wheel filename;
- wheel SHA-256;
- Python support contract;
- pytest/Ruff/mypy results;
- architecture-certification evidence;
- release workflow evidence.

## Immutability rules
Once a release/tag is used by a consumer:
- do not move the tag;
- do not replace the wheel asset in place;
- do not reuse the version number;
- corrections require a new version and release;
- consumer repos upgrade explicitly and regenerate their own hash locks.

GitHub's platform-level release `immutable` flag may be unavailable or false. The Daily Line's immutability guarantee is therefore an explicit repository/release policy and must be enforced operationally unless GitHub platform immutability is later enabled.

## Versioning policy
DDC uses semantic versioning.

During `0.x` development:
- patch release: bug fix or compatibility-preserving implementation correction;
- minor release: meaningful new shared capability or contract evolution;
- any breaking contract change must be called out explicitly even before 1.0 and requires coordinated consumer migration.

A future `1.0.0` is appropriate only after the shared contracts have been exercised by multiple production sport consumers and the compatibility/versioning process is stable.

## Development use
A local sibling checkout or editable install may be used temporarily for development/equivalence testing, but it is never the committed production dependency authority.

Example temporary local development:

```powershell
python -m pip install -e ..\Daily-Data-Core
```

Before production activation (Stage B), the sport repo must switch to the released
wheel dependency and regenerate its hashed locks. Stage A does not require publication.

## Two-stage release certification — TDL-03B-FINAL-B

This explicitly supersedes the prepublication ordering that blocked FINAL-A;
the original FINAL-A record remains historical evidence. Requiring a released-URL
lock before certification while forbidding publication before certification was circular.

**Stage A: prepublication artifact certification.** Bind package name, final version,
wheel filename and SHA-256, exact source SHA/tree, reproducible-build evidence,
hashed dependency graph, Python/environment constraints, and exact inactive consumer
SHA/tree in a PREPUBLICATION_RELEASE_BINDING_MANIFEST. Governed private artifact
delivery is allowed: verify the wheel digest, install the compiled validation lock
with --require-hashes, and verify installed package bytes/origin. No released URL is
required. This manifest and validation lock are certification evidence ONLY, never
production installation/activation authority. The consumer must default to legacy.

**Stage B: postpublication release binding.** Only after successful Stage A and a
separate owner authorization identifying the exact artifact, publish those certified
bytes under the canonical release coordinate. Existing source-on-main and tag rules
still apply; do not rebuild after a merge or retarget the source identity silently.
Retrieve the canonical URL, verify package/version metadata and exact certified
SHA-256 BEFORE compiling the released-URL production lock. The production-lock
commit is separately identified and privately certified. Compare every executable
dependency name/version/hash, transitive dependency, environment marker and Python
constraint with Stage A; only the DDC transport-source representation may differ.
Any unexplained drift blocks cutover. A complete 15-phase admission/rehearsal,
rollback verification and explicit owner-authorized authority switch remain required.

SHA-256 is immutable byte identity; the URL is a verified distribution location.
For 0.2.2 the only authorized prepared hash is
`d18b1d30a343517b85d125c590aec2aace9bee3ab233ce8ba88a28a2c826c0ea`, wheel
`daily_data_core-0.2.2-py3-none-any.whl`, source
`e877c852ba98c4742b6f9f5be55ba906eb9c0f38`, tree
`779960bb4328ed812c24b1e9d70114bd9d7e3f67`.
If downloaded bytes differ, STOP: do not update the expected hash, silently rebuild,
overwrite the release, or compile against altered bytes. A new governed identity is
required. Stage-A success itself authorizes neither publication nor cutover.

## DDC-6 implication
Daily-MLB DDC-6 production dependency introduction requires:
1. DDC-0 through DDC-5 architecture certification — **COMPLETE**;
2. merge to `main` — **COMPLETE**;
3. version/tag creation — **COMPLETE: `v0.1.0`**;
4. wheel build and SHA-256 verification — **COMPLETE**;
5. release publication — **COMPLETE**;
6. frozen Daily-MLB pre-DDC baseline — **IN PROGRESS**;
7. successful hash-locked wheel resolution in Daily-MLB — **NEXT AFTER BASELINE**.

The same release mechanism applies to Daily-NFL and Daily-NCAAF.
