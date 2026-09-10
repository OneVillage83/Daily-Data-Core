# Daily Data Core Architecture Certification Log

This file is the authoritative milestone certification record for Daily Data Core. Implementation completion does not equal certification.

TDL-03B resume update: 2026-09-09T20:23:14-07:00 (America/Los_Angeles).
**Release/cutover BLOCKED** by a new physical-exchange evidence counterexample:
Requests automatically follows a 302 to 200, but DDC retains only the final exchange,
losing the redirect body and quota observation. Earlier certification remains scoped
to its executed tests and does not cover this path. See
`TDL03B_RESUME_REDIRECT_EVIDENCE_BLOCKER_20260909.md`. No release or consumer
switch was performed; fix the shared contract and revalidate a new candidate first.

TDL-03C operator update: 2026-09-09T19:58:31-07:00 (America/Los_Angeles).
Candidate 0.2.0.dev2 source tree `016d50e42aad77ec1841605fe97a1ddca69b769a`
passed reproducible-wheel, persisted replay, DDC-6 compatibility and hosted Linux
quality validation. GitHub Actions run `34431413425`, quality job `102727522350`,
tested the identical tree through CI-only descendant
`25732fe44190dde48f76c6c493d889c4c8486988`; all required steps passed. TDL-03C is
**CERTIFIED-FOR-TDL-03B-RESUME**. DDC-6 remains IN PROGRESS: main merge, immutable
release, real-provider validation and consumer cutover retain their existing gates.
See `TDL03C_LOGICAL_CALL_REPLAY_HANDOFF_20260909.md`.

Continuation update: 2026-09-09T18:40:55-07:00 (America/Los_Angeles).
TDL-03A's necessary candidate checks passed, but TDL-03B demonstrated a new durable
logical-acquisition/error replay gap. Current release/migration remains uncertified;
see `TDL03B_PERSISTED_REPLAY_BLOCKER_20260909.md`. Historical certifications below
do not cover that new counterexample.

Updated: 2026-09-09T16:49:00-07:00 (America/Los_Angeles).
The historical certifications below remain recorded; newly demonstrated NWS URL,
DST/temporal and venue validation defects require a new release. Candidate fixes
are locally tested, not certified. Current DDC-6 is blocked on provider/evidence
admission; see `DDC6_RELEASE_ADMISSION_20260909.md`. Do not interpret the historical
"no unresolved violations" statement as covering the newly discovered cases.

| Milestone | Scope | Implementation | Certification | Evidence / blocker |
|---|---|---|---|---|
| DDC-0 | Architecture & ownership contract | Complete | **ARCHITECTURE-CERTIFIED** | Final conformance audit; hosted current-head quality/reproducibility gates passed 2026-08-26 |
| DDC-1 | Runtime, provenance, provider, HTTP foundation | Complete | **ARCHITECTURE-CERTIFIED** | Python 3.12.14; exact-byte evidence; hash-locked install; pytest/Ruff/strict-mypy green |
| DDC-2 | Generic odds + market core | Complete | **ARCHITECTURE-CERTIFIED** | MLB-derived compatibility suite; market/book timestamps; sport isolation; current-head gates green |
| DDC-3 | Weather core | Complete | **ARCHITECTURE-CERTIFIED** | NWS/OpenWeather compatibility coverage including cloud/pressure/source metadata; current-head gates green |
| DDC-4 | Venue/geospatial core | Complete | **ARCHITECTURE-CERTIFIED** | finite-input hardening and geometry regression coverage; current-head gates green |
| DDC-5 | Travel/rest core | Complete | **ARCHITECTURE-CERTIFIED** | timezone/value hardening and recovery regression coverage; current-head gates green |
| DDC-6 | Daily-MLB compatibility migration | Baseline frozen; runtime migration may begin | **IN PROGRESS** | `DDC6_MLB_MIGRATION_PLAN.md`; Daily-MLB draft PR #65 is the pre-DDC regression oracle |
| DDC-7 | Daily-NFL integration migration | Not started | NOT ELIGIBLE | Begins after DDC-6 proves consumer compatibility; certified NFL contracts must be preserved |
| DDC-8 | Daily-NCAAF integration | Architecture contract complete; implementation not started | NOT ELIGIBLE | Daily-NCAAF consumes certified DDC from its first implementation milestone |

## Certification evidence — 2026-08-26

Final hosted PR validation ran on GitHub Actions under **CPython 3.12.14**.

Permanent CI contract:
1. installs pinned bootstrap tooling (`pip==26.1.2`, `pip-tools==7.6.0`);
2. installs `requirements-dev.txt` with `pip --require-hashes`;
3. recompiles both dependency locks and requires zero Git diff;
4. runs the complete pytest suite;
5. runs Ruff;
6. runs strict mypy.

Final certification result:
- hash-locked dependency installation: **PASS**;
- runtime/development lock regeneration and drift check: **PASS**;
- pytest: **28 passed**;
- Ruff: **PASS — All checks passed**;
- strict mypy: **PASS — no issues in 11 source files**.

GitHub Actions run: `33009126114`, quality job `98310500803`.

No unresolved DDC-0 through DDC-5 architecture violations remain in the final conformance audit.

## Release gate

Architecture certification authorizes packaging; it does not authorize consumers to track a moving Git branch. DDC must now be released as an immutable versioned wheel with its source commit and wheel SHA-256 recorded. Each sport repository consumes that exact artifact through its normal hash-locked dependency process. See `PACKAGE_RELEASE_POLICY.md`.

## DDC-6 transition rule

With DDC-0 through DDC-5 certified, DDC-6 may begin the production compatibility-adapter phases. Daily-MLB legacy shared code remains the regression oracle and must not be deleted until fixture equivalence, tiny real-provider validation, artifact/database compatibility, credential-safety checks, and Daily-MLB quality gates all pass.

## Promotion rule

Future milestones move to `ARCHITECTURE-CERTIFIED` only after their own required implementation, compatibility, point-in-time, quality, and conformance gates pass. Certification of the shared core does not waive sport-specific certification requirements.
