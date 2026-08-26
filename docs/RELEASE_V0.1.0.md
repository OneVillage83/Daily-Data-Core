# Daily Data Core Release Record — v0.1.0

Date: 2026-08-26
Status: **PUBLISHED — CERTIFIED PRODUCTION DEPENDENCY ARTIFACT**

## Identity

- Package: `daily-data-core`
- Version: `0.1.0`
- Tag: `v0.1.0`
- Certified source commit: `0e7e918b1a1157d48a4eecd2c6ca6e61554cc6b0`
- Wheel: `daily_data_core-0.1.0-py3-none-any.whl`
- Wheel size: `19686` bytes
- Wheel SHA-256: `5939e70fe5eab5d30b2c4875f50732cd3e94921561afbd0237320ef934ced1e5`
- Python support: `>=3.12,<3.13`

Release page:
`https://github.com/OneVillage83/Daily-Data-Core/releases/tag/v0.1.0`

Wheel URL:
`https://github.com/OneVillage83/Daily-Data-Core/releases/download/v0.1.0/daily_data_core-0.1.0-py3-none-any.whl`

Checksum asset URL:
`https://github.com/OneVillage83/Daily-Data-Core/releases/download/v0.1.0/daily_data_core-0.1.0-py3-none-any.whl.sha256`

## Source certification

DDC-0 through DDC-5 were architecture-certified before release. The final certification-head GitHub Actions run used CPython 3.12.14 and passed:

- hash-locked development dependency installation;
- dependency-lock regeneration with zero drift;
- pytest: 28 passed;
- Ruff: all checks passed;
- strict mypy: no issues in 11 source files.

The certified foundation was merged to `main` at source commit `0e7e918b1a1157d48a4eecd2c6ca6e61554cc6b0`.

## Release construction verification

The release workflow checked out the exact certified source commit rather than the release-helper branch head. It then:

1. built a pure-Python wheel;
2. required the exact filename `daily_data_core-0.1.0-py3-none-any.whl`;
3. installed the wheel into a fresh virtual environment;
4. asserted `daily_data_core.__version__ == "0.1.0"`;
5. verified the wheel contains every expected core package module;
6. calculated the wheel SHA-256;
7. published the wheel and checksum asset to tag `v0.1.0`.

Release workflow:
- run `33009682975`
- job `98312416283`
- wheel build: PASS
- wheel identity/installability/content verification: PASS
- SHA-256 generation: PASS
- GitHub release publication: PASS

GitHub's release API independently reports the wheel digest as:

```text
sha256:5939e70fe5eab5d30b2c4875f50732cd3e94921561afbd0237320ef934ced1e5
```

## Consumer contract

Production sport repositories consume this exact artifact, not a moving DDC branch:

```text
daily-data-core @ https://github.com/OneVillage83/Daily-Data-Core/releases/download/v0.1.0/daily_data_core-0.1.0-py3-none-any.whl
```

Each consumer must compile the direct artifact into its own `--require-hashes` dependency lock and verify that the resolved wheel hash matches:

```text
5939e70fe5eab5d30b2c4875f50732cd3e94921561afbd0237320ef934ced1e5
```

A consumer must not disable hash enforcement to accommodate DDC.

## Immutability policy

GitHub currently reports the release object's platform `immutable` flag as false. The Daily Line therefore enforces immutability by repository policy:

- do not move tag `v0.1.0`;
- do not replace its wheel asset;
- do not reuse version `0.1.0` for changed code;
- any correction requires a new semantic version and a new release;
- consumer upgrades are explicit and regenerate their own dependency locks.

## DDC-6 authorization

This release satisfies the DDC-6 package-release gate. Daily-MLB may introduce the exact `v0.1.0` wheel on a dedicated migration branch after the frozen pre-DDC regression baseline is recorded. Legacy MLB shared implementations remain in place until side-by-side equivalence, tiny real-provider validation, artifact/database compatibility, credential safety, and MLB quality gates all pass.
