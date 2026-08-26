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
Certified DDC versions are distributed as versioned pure-Python wheel artifacts attached to an immutable GitHub Release/tag.

Initial certified foundation target:

```text
release: v0.1.0
wheel:   daily_data_core-0.1.0-py3-none-any.whl
```

The release is created only from an architecture-certified commit on `main`.

## Consumer requirement form
A sport repository consumes an exact released wheel URL in its dependency input, for example:

```text
daily-data-core @ https://github.com/OneVillage83/Daily-Data-Core/releases/download/v0.1.0/daily_data_core-0.1.0-py3-none-any.whl
```

The sport repository then compiles its normal Python 3.12 lock with `pip-tools --generate-hashes`. The compiled lock, not the moving GitHub branch, is the runtime installation authority.

If the resolver/toolchain cannot emit a hash for the direct wheel URL, the migration stops and the release/distribution mechanism is corrected before production integration. `--require-hashes` is not disabled to make the dependency easier to install.

## Release construction
From the exact certified commit under Python 3.12 with the pinned pip toolchain:

```powershell
python -m pip wheel --no-deps . --wheel-dir dist
```

Required release verification:

```powershell
python -m pip install --force-reinstall --no-deps .\dist\daily_data_core-0.1.0-py3-none-any.whl
python -c "import daily_data_core; print(daily_data_core.__version__)"
python -m pytest -q
python -m ruff check .
python -m mypy .
```

Calculate and record the wheel SHA-256 before upload. The release record must include:
- DDC version;
- source commit SHA;
- tag;
- wheel filename;
- wheel SHA-256;
- Python support contract;
- pytest/Ruff/mypy results;
- architecture-certification evidence.

## Immutability rules
Once a release/tag is used by a consumer:
- do not move the tag;
- do not replace the wheel asset in place;
- do not reuse the version number;
- corrections require a new version and release;
- consumer repos upgrade explicitly and regenerate their own hash locks.

## Versioning policy
DDC uses semantic versioning.

During `0.x` development:
- patch release: bug fix or compatibility-preserving implementation correction;
- minor release: meaningful new shared capability or contract evolution;
- any breaking contract change must be called out explicitly even before 1.0 and requires coordinated consumer migration.

A future `1.0.0` is appropriate only after the shared contracts have been exercised by multiple production sport consumers and the compatibility/versioning process is stable.

## Development use
A local sibling checkout or editable install may be used temporarily for development/equivalence testing, but it is never the committed production dependency authority.

Examples of acceptable temporary local development:

```powershell
python -m pip install -e ..\Daily-Data-Core
```

Before certification, the sport repo must switch to the immutable released wheel dependency and regenerate its hashed locks.

## DDC-6 implication
Daily-MLB DDC-6 may build side-by-side adapters before the release exists, but the committed production dependency is introduced only after:
1. DDC-0 through DDC-5 architecture certification;
2. merge to `main`;
3. version/tag creation;
4. wheel build and SHA-256 verification;
5. release publication;
6. successful hashed-lock compilation in Daily-MLB.

The same release mechanism applies to Daily-NFL and Daily-NCAAF.
