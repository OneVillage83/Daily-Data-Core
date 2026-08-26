# Daily Data Core Decisions

## DDC-D001 — Shared core is a dependency, not a copy template
Decision: shared infrastructure is implemented once in Daily-Data-Core and consumed by sport repositories. Reason: copied implementations drift and create inconsistent PIT/market semantics.

## DDC-D002 — Dataset keys are extensible strings
Decision: generic provider contracts use validated string dataset keys instead of a universal sport enum. Reason: DDC must support both shared data families and sport-scoped provider payloads without knowing every sport ontology.

## DDC-D003 — Canonical sport identity stays outside DDC
Decision: DDC preserves provider participant strings/IDs but does not assign permanent cross-sport team/player/game identity. Reason: identity rules are sport- and provider-history-specific.

## DDC-D004 — `available_at` is mandatory for prediction eligibility
Decision: normalized evidence used in PIT workflows must have a defensible `available_at`. Reason: provider publication, observation, and correction times are not interchangeable.

## DDC-D005 — Forecast weather and observed weather are distinct evidence
Decision: historical prediction features may not substitute actual game weather for the forecast that existed at prediction time. Reason: substitution leaks future information.

## DDC-D006 — Market consensus never destroys book-level evidence
Decision: consensus/no-vig summaries are derived from immutable book quotes; all quotes remain available. Reason: line shopping, disagreement, stale-book detection, and historical audit require book-level snapshots.

## DDC-D007 — Travel core emits facts, not fatigue folklore
Decision: DDC computes distance, timezone shift, itinerary and elapsed rest but no sport-specific performance penalty. Reason: coefficients must be learned/validated within sport models.
