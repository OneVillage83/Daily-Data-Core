# TDL-03B-FINAL governed release resume

Updated: 2026-09-10T14:52:25-07:00 (America/Los_Angeles).

State: **PREPARING; NOT RELEASED; NOT CONSUMER-ADMITTED**.

The owner resumed release/cutover after private MLB certification run 34520833159
passed on 6dd7427eb1cc6bc71594ed7e93678ffce12ffcd8, tree
beb37a9744062fb22024de1dc57e90ccdccce18a. MLB's authoritative receipt head is
80c23ae6480a80d01d422cb28b36d2220a3b0a6a. This supersedes the external-CI
block in the earlier DDC certification document, not any consumer admission gate.

Authenticated PR #4 and remote branch verification still resolve to
9c9be91922813f627459d1020254bebcbfe487ef. Its delta from certified implementation
66673b279484497f04e5b8972db7d4affb44d9d1 (tree
e78b0e06627bfbe55f0bb38d99a714d4ef0ad843) is README/documentation only.
The latest certified candidate is 0.2.1.dev1, not the superseded dev4/prepared 0.2.0.

The final semantic version is **0.2.1**, retaining the successor patch identity.
Only project/package version metadata changes. New wheel
`daily_data_core-0.2.1-py3-none-any.whl` must receive its own SHA-256 and repeat
applicable source, installed-package and consumer admission validation. Candidate
digest 1bffac282d8de69ca63c555ba43ec31d1418c923defa9df143ffa7d96a22614e is
not the final-release digest. Existing artifacts, especially v0.1.0, stay immutable.

PACKAGE_RELEASE_POLICY.md still requires architecture-certified source on main,
then an exact versioned tag/release/wheel and consumer hash-locks. No additional
owner approval requirement is recorded; current rulesets are empty. Publication
remains withheld while final-artifact and consumer admission are incomplete.
No hosted CI will be triggered or polled by this implementation task; eventual
push/merge commits must retain CI-skip markers until the explicit validator handoff.

MLB legacy remains ACTIVE_PRODUCTION_AUTHORITY. No production dependency or
adapter has switched. Scientific permissions remain 0 AVAILABLE / 5 BLOCKED /
22 MISSING. Release preparation is not consumer admission, rehearsal or cutover.
