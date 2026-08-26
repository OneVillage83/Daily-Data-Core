# Ownership Boundaries V1

This document is authoritative when deciding whether code belongs in Daily Data Core or a sport repository.

| Concern | Daily Data Core owns | Sport repository owns |
|---|---|---|
| HTTP | retries, timeout, status diagnostics, quota headers, safe URL handling | provider-specific request semantics only when unique to sport source |
| Raw evidence | checksums, immutable storage, evidence IDs, generic clocks | sport-specific parsing and reconciliation |
| Provider metadata | reliability, licensing, cadence, PIT fidelity, schema/parser version | sport-domain capability meaning |
| Odds | acquisition, raw book quotes, American/decimal math, hold, no-vig, freshness, consensus, line grouping | team/player identity, sport labels, model fair probability, edge/EV interpretation, Recommendation Gate |
| Weather | NWS/OpenWeather acquisition, forecast snapshots, normalized meteorology, source disagreement | sport-specific effects and features |
| Venue | coordinates, timezone, roof class, generic orientation/bearing, source provenance | sport geometry/feature semantics not reusable elsewhere |
| Travel | distance, timezone shift, itinerary, elapsed rest | sport-specific fatigue/recovery transforms |
| Identity | provider/source IDs and raw participant strings | permanent canonical team/player/game identity |
| PIT | generic temporal provenance and eligibility helpers | sport-specific prediction cutoffs and leakage rules |
| Models | none | all sport prediction models, simulation, calibration, feature registries |
| Recommendations | none | BET/LEAN/PASS/AVOID and settlement/performance logic |

## Decision test
Code belongs in DDC only if it can be correctly executed without knowing the rules of the sport.

Examples:
- `american_to_probability(-120)` -> DDC.
- `wind_to_vector(240 degrees, 12 mph)` -> DDC.
- `haversine_distance(SF, LA)` -> DDC.
- `hours_between_arrival_and_kickoff` -> DDC.
- `wind is blowing out to center at Wrigley` -> Daily-MLB.
- `crosswind lowers deep-pass efficiency` -> Daily-NFL/NCAAF.
- `three games in four nights penalty` -> sport repository unless represented only as neutral schedule/rest facts.

## Anti-duplication rule
A consuming sport repository may temporarily retain legacy shared code during migration, but new shared behavior must be implemented in DDC first. Compatibility wrappers in the sport repository should be thin and explicitly marked for removal.
