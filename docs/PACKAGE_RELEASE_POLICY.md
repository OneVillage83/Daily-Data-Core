# Daily Data Core Package Release Policy

Date: 2026-08-26
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

Before certification, the sport repo must switch to the released wheel dependency and regenerate its hashed locks.

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
