# TDL-03B-FINAL governed release resume

Successor: `TDL03F_OPTIONAL_DESCRIPTION_20260910.md` locally clears this blocker
with new 0.2.2.dev1 bytes. Resume READY; no release/cutover. The failed checkpoint
below is retained unchanged as historical evidence, not current dispatch authority.

Updated: 2026-09-10T15:02:08-07:00 (America/Los_Angeles).

State: **BLOCKED on newly executed persisted odds equivalence; NOT RELEASED**.

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

## Final package preparation and executed local evidence

Prepared source: `9273b17a01529f949611a10b136c4e8446aa950a`.
Prepared source tree: `a4e18522cc0878ac8ed24c36e38b7707bf3f13e0`.
Wheel: `daily_data_core-0.2.1-py3-none-any.whl`.
SHA-256: `9c6a4e6132bfe6ce30244eea0f8d7bc666c9664c61221d173d1a10997f6c61b6`.
Two independent clean archive builds match under Python 3.12.10, pip 26.2,
pip-tools 7.6.1, build 1.5.0, setuptools 83.0.0, wheel 0.48.0 and epoch
1787788800. This is a prepared artifact identity, not a published release.

Source tests: 120 passed in 18.02 seconds; Ruff passed; strict mypy passed 27 files.
Fresh hash-locked isolated installation imported 0.2.1 from site-packages and
verified installed direct-url archive SHA-256, no editable/source fallback.
Copied tests outside the source tree, Python `-I` with importlib pytest mode:
120 passed in 15.01 seconds; pip check passed. Runtime/development lock
regeneration produced zero Git diff. Their hashes remain respectively
`7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af` and
`10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`.

Prior consumer gates passed on final bytes: weather window 13/13, weather
evaluation/persistence 23/23, redirects 8/8, failed acquisition/replay 10/10,
base admission 7/7, projection equivalence 80/80; offline counters zero.
Those scopes do not cover the new failing persisted odds case below.
Private consumer focused regression: 36 tests passed; full Ruff passed; strict
mypy passed 772 files. Tracked source scans with no local environment loaded
passed 62 DDC / 1,069 MLB files with zero findings/errors. No new vulnerability
audit/full MLB/Stats/Docker certification is claimed for this failed admission.

## New substantive stop condition

The private consumer now exercises selected normalized odds through its actual
existing persistence, close/reopen, integrity reconstruction and strict DDC replay.
The ordinary partial-market control passes with identical persisted rows/hashes.
The optional-description case does not: an otherwise valid outcome with an empty
optional description is retained by the legacy consumer but excluded by DDC's
`_parse_market` because `_string(description)` classifies the entire outcome as
malformed. The source bytes are preserved, yet normalized outcome membership,
ordinal and durable event identity differ. Both the certified 0.2.1.dev1 wheel
and prepared final 0.2.1 reproduce this discrepancy with zero network calls.
It is not caused by final packaging, CI capacity, or lost HTTP history.
Private probe implementation: `c8859abecea222fddc45109f71cc7b858b27c4a8`, tree
`95198476c020eb805416b5386eb476f33dfc1929`, in Daily-MLB PR #75. Subsequent
receipts change documentation only. DDC package source stays 9273b17 above;
later DDC receipt commits do not change the wheel bytes.

This is a synthetic malformed-input counterexample, not an assertion that a live
provider returned it. Private fixture/source/SQLite receipts remain in Daily-MLB;
they must not be copied into this public repository. The failed admission returns
exit 1 and is not an expected-pass release test.

Per the owner's explicit new-difference STOP gate, no main merge, tag, release,
consumer pin, adapter activation or cutover follows this failure. No ad-hoc
consumer reparse is used to restore the excluded outcome. A bounded successor
repair must reconcile optional descriptor validity with quote-fact retention,
retain diagnostics/raw paths, keep required description-based identity fail-closed,
and revalidate/re-certify changed source before resuming release. Do not weaken
validation or silently authorize a changed downstream contract.

DDC-6 remains pending that repair plus all final consumer admission/rehearsal/
cutover gates. Existing certification receipts retain their historical scope.
No hosted CI was run or polled. Docker is not applicable to the DDC wheel;
MLB's full release/Stats/Docker gates remain unexecuted for a cutover candidate
because no such candidate was admitted. No additional owner approval was found;
this is a substantive equivalence blocker, not OWNER-APPROVAL-REQUIRED.
