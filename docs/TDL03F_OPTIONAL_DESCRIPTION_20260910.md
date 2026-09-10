# TDL-03F optional quote description contract and repair

Updated: 2026-09-10T15:15:00-07:00 (America/Los_Angeles).
Status: IMPLEMENTING / UNRELEASED; no consumer authority switch.

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

Local validation, reproducible artifact identity and exact continuation will be
appended after execution. Scientific authority remains 0 AVAILABLE / 5 BLOCKED /
22 MISSING and MLB legacy remains ACTIVE_PRODUCTION_AUTHORITY.
