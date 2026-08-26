# Daily Data Core Architecture Certification Log

This file is the authoritative milestone certification record for Daily Data Core. Implementation completion does not equal certification.

| Milestone | Scope | Implementation | Certification | Evidence / blocker |
|---|---|---|---|---|
| DDC-0 | Architecture & ownership contract | Complete | PENDING | `DDC0-DDC5_ARCHITECTURE_CONFORMANCE_AUDIT.md`; final quality gates outstanding |
| DDC-1 | Runtime, provenance, provider, HTTP foundation | Complete | PENDING | Python compile + tests pass; Ruff/mypy and compiled locks outstanding |
| DDC-2 | Generic odds + market core | Complete | PENDING | Regression coverage present; Ruff/mypy outstanding |
| DDC-3 | Weather core | Complete | PENDING | Regression coverage present; Ruff/mypy outstanding |
| DDC-4 | Venue/geospatial core | Complete | PENDING | Regression coverage present; Ruff/mypy outstanding |
| DDC-5 | Travel/rest core | Complete | PENDING | Regression coverage present; Ruff/mypy outstanding |
| DDC-6 | Daily-MLB compatibility migration | Not started | NOT ELIGIBLE | Requires certified core and MLB regression equivalence plan |
| DDC-7 | Daily-NFL integration migration | Not started | NOT ELIGIBLE | Follows DDC-6 compatibility proof; certified NFL contracts must be preserved |
| DDC-8 | Daily-NCAAF integration | Architecture contract complete; implementation not started | NOT ELIGIBLE | Daily-NCAAF should consume certified DDC from its first implementation milestone |

## Current blockers — 2026-08-26
1. Ruff has not executed against the final branch in the available isolated runner.
2. strict mypy has not executed against the final branch in the available isolated runner.
3. compiled/hash-locked requirements have not yet been generated under the pinned Python 3.12/pip-tools toolchain.
4. GitHub Actions workflow files are present, but GitHub currently reports no workflow/status checks for PR #1 or its head commits.

## Promotion rule
A row may move to `ARCHITECTURE-CERTIFIED` only after all required local/hosted quality gates pass and the conformance audit contains no unresolved architecture violations. Consumer migrations may use compatibility wrappers during transition, but duplicated legacy shared code is not removed until its relevant DDC contract is certified and regression-equivalent.
