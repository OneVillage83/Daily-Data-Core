# DDC-6 — Daily-MLB Compatibility Migration Plan

Date: 2026-08-26
Status: **PLANNED — MAY PREPARE, MUST NOT DELETE LEGACY SHARED CODE BEFORE DDC-0–DDC-5 CERTIFICATION**

## Goal
Move Daily-MLB from owning sport-agnostic acquisition/transport primitives to consuming `daily-data-core` while preserving every current Daily-MLB production contract, historical behavior, regression expectation, and artifact shape.

DDC-6 is a compatibility migration, not a redesign of Daily-MLB.

## Non-negotiable migration rule
During DDC-6, old and new paths run side-by-side until equivalence is demonstrated. Legacy MLB implementations are not deleted simply because a DDC equivalent exists.

Deletion is allowed only after:
1. DDC-0 through DDC-5 are architecture-certified;
2. a certified versioned DDC wheel release exists and its SHA-256/source commit are recorded;
3. Daily-MLB compiles a hashed lock containing that immutable DDC release;
4. Daily-MLB quality gates pass with DDC installed from the locked dependency;
5. compatibility tests show equivalent behavior for the current MLB contracts;
6. one tiny real-provider validation succeeds for odds and weather;
7. raw evidence/provenance differences are explicitly reconciled;
8. output-contract snapshots remain compatible.

The package/distribution authority is `PACKAGE_RELEASE_POLICY.md`. A moving branch or unhashed VCS dependency is not an acceptable production dependency.

## Current Daily-MLB source → DDC ownership map

| Current Daily-MLB source | DDC target | DDC-6 action | MLB remains responsible for |
|---|---|---|---|
| `app/http.py` | `daily_data_core.http` | Replace implementation with compatibility wrapper/re-export after equivalence | MLB service orchestration/error staging only |
| `app/raw_payloads.py` | `daily_data_core.providers`, `daily_data_core.provenance`, `daily_data_core.temporal` | Adapt exact-byte DDC payload into existing MLB sanitized-artifact contract | MLB artifact layout, DB rows, event/run association |
| `app/redaction.py` URL/query behavior | `daily_data_core.http.redact_url` | Share URL sanitization; keep richer MLB value/text redaction until DDC contract intentionally expands | MLB artifact/output secret scrubbing |
| `app/collectors/odds_collector.py` | `daily_data_core.odds.TheOddsApiClient` | Add MLB compatibility adapter that emits the existing `OddsCollectionResult`/warning behavior | MLB date filtering, team identity, stadium lookup |
| `app/processors/odds_processor.py` math primitives | `daily_data_core.markets` | Replace duplicated basic math/freshness helpers only after regression parity | MLB consensus output contract, team canonicalization, line movement, persisted warnings, report-facing structure |
| `app/collectors/nws_weather_collector.py` | `daily_data_core.weather.NwsWeatherClient` | Adapt DDC forecast snapshot to existing MLB weather dict | Baseball interpretation |
| `app/collectors/openweather_collector.py` | `daily_data_core.weather.OpenWeatherClient` | Adapt DDC forecast snapshot to existing MLB weather dict | Baseball interpretation |
| `app/processors/weather_processor.py::compare` | `daily_data_core.weather.compare_forecasts` | Replace with adapter after exact threshold/output parity | none beyond compatibility shape |
| `app/processors/weather_processor.py::wind_impact` | none | **Keep in Daily-MLB** | baseball-specific blowing-in/out and outfield/crosswind semantics |
| `app/stadiums.py` + MLB team→stadium mapping | DDC venue primitives only | Convert selected stadium facts to `Venue`; do not move team identity/mapping in DDC-6 | MLB team-to-venue relationship and baseball field semantics |

## Compatibility surfaces that must remain stable

### Odds acquisition
Existing MLB behavior to preserve:
- sport key `baseball_mlb`;
- American odds only;
- configurable unique regions;
- supported market subset `h2h`, `spreads`, `totals`;
- exact request diagnostics and retry counts;
- Retry-After handling/cap;
- quota header capture;
- empty list is a valid empty slate;
- non-list root is fatal;
- non-empty payload with zero valid events is fatal;
- malformed event/bookmaker/market/outcome entries are excluded individually and generate warnings;
- a malformed element must not mutate the retained raw provider evidence;
- provider event/book/market fields needed downstream remain available;
- bookmaker-level and market-level provider timestamps remain available for freshness/provenance;
- a returned event whose sport key differs from the requested sport fails closed;
- API keys never appear in errors, manifests, URLs, or committed artifacts.

### Odds normalization
DDC may own generic math, but Daily-MLB V2 output must continue to preserve:
- every bookmaker quote;
- alternate spread/total points;
- exact signed home-relative spread semantics;
- per-book implied/no-vig probabilities;
- best price and tied best-price books;
- hold;
- freshness classifications;
- consensus/disagreement;
- warnings;
- stored line movement;
- `odds-consensus-v2` report-facing contract.

DDC-6 must not replace the mature MLB output processor wholesale. First migrate low-level primitives, then prove the higher-level MLB output is unchanged.

### Weather acquisition
Existing MLB normalized weather fields must remain available to the compatibility layer:
- `forecast_time`;
- `temperature_f`;
- `humidity_pct`;
- `precipitation_probability_pct`;
- `wind_speed_mph`;
- `wind_direction_deg`;
- `short_forecast`;
- NWS `wind_speed_text` and `wind_direction_cardinal` where currently exported;
- NWS `forecast_office` where currently exported;
- OpenWeather `clouds_pct` where currently exported;
- OpenWeather `pressure_hpa` where currently exported.

This inventory exposed a DDC-3 extension requirement: the base `ForecastSnapshot` carries source-neutral optional cloud cover and pressure, while provider-specific display metadata lives in an immutable metadata envelope. No existing MLB field may silently disappear.

### Raw evidence/provenance
Daily-MLB currently stores sanitized canonical JSON artifacts and calculates the recorded checksum over those sanitized bytes. DDC's internal `ProviderPayload` intentionally preserves exact response bytes.

DDC-6 therefore uses two distinct layers:
1. **DDC evidence layer:** exact provider response bytes + temporal provenance, suitable for immutable evidence and reproducibility;
2. **MLB compatibility artifact layer:** parsed/redacted/canonical JSON bytes retaining the existing Phase-1 artifact/checksum contract.

These must not be conflated. DDC exact bytes are not automatically written into user-facing/report artifacts.

## Migration phases

### DDC-6A — Contract freeze and equivalence fixtures
- snapshot current MLB collector/processor outputs for representative odds payloads;
- snapshot NWS/OpenWeather normalized dictionaries;
- snapshot malformed provider behavior;
- snapshot retry/redaction diagnostics;
- record current artifact/checksum semantics;
- add explicit tests for every compatibility surface above.

Exit: legacy behavior is executable as a regression oracle.

### DDC-6B — Certified package release & dependency introduction
DDC dependency introduction is a release event, not a branch reference.

Required order:
1. certify DDC-0 through DDC-5 on the final current head;
2. merge the certified foundation to `main`;
3. create a semantic version/tag (initial target `v0.1.0`);
4. build `daily_data_core-0.1.0-py3-none-any.whl` from that exact certified commit;
5. calculate/record the wheel SHA-256 and source commit;
6. publish the wheel as an immutable release asset without moving/replacing the version later;
7. add the exact versioned wheel URL to Daily-MLB's dependency input;
8. regenerate Daily-MLB Python 3.12 hashed locks;
9. verify `pip install --require-hashes -r requirements-dev.txt` accepts the DDC dependency;
10. import DDC behind MLB compatibility modules; do not change the pipeline API yet.

A temporary local editable/sibling install may be used for equivalence development before release, but it is never the committed production dependency authority.

Exit: existing MLB pipeline still calls the same MLB interfaces, those interfaces can delegate internally to an immutable certified DDC build, and Daily-MLB's compiled lock is the installation authority.

### DDC-6C — HTTP and evidence adaptation
- adapt `HttpClient` diagnostics/retry behavior;
- adapt DDC exact-byte `ProviderPayload` into MLB's sanitized raw-artifact persistence;
- prove secret redaction and checksum behavior;
- preserve failure-stage diagnostics.

Exit: HTTP/raw tests pass with the DDC implementation under the MLB interface.

### DDC-6D — Odds acquisition migration
- delegate The Odds API request to DDC;
- transform DDC snapshots/warnings to current MLB collector shape;
- preserve full raw provider payload for existing exports;
- preserve bookmaker/market freshness timestamps;
- run the entire existing odds collector suite plus new cross-path equivalence tests.

Exit: old-path and DDC-path normalized event/warning behavior are equivalent for the locked fixtures.

### DDC-6E — Generic odds math migration
- replace only generic probability/hold/no-vig/freshness helpers with DDC equivalents;
- keep `process_game`, line selection, MLB identity resolution, line movement, and the V2 output contract local initially;
- compare complete `odds_consensus.json` fixture outputs.

Exit: report-facing odds contract unchanged except intentionally documented optional additions.

### DDC-6F — Weather acquisition migration
- delegate NWS/OpenWeather acquisition to DDC;
- adapt DDC `ForecastSnapshot` to the current MLB weather dict;
- preserve provider-specific optional fields required by existing output;
- keep `wind_impact` local;
- compare full `weather.json` fixture outputs.

Exit: weather acquisition shared; baseball weather interpretation unchanged.

### DDC-6G — Real-provider tiny validation
Run one small current MLB collection with production credentials locally:
- verify all-book odds acquisition;
- verify raw evidence creation;
- verify NWS;
- verify OpenWeather if enabled;
- verify artifacts and database rows;
- verify no credential leakage;
- compare legacy/DDC counts and normalized summaries.

Exit: no unexplained divergence.

### DDC-6H — Legacy removal
Only after all gates above:
- remove duplicated implementations rather than compatibility wrappers where safe;
- retain MLB-specific adapters/interpretation;
- update architecture/readmes/source maps;
- add migration certification evidence.

## Required quality gates
From Daily-MLB under Python 3.12:

```powershell
python -m pytest -q
python -m ruff check .
python -m mypy .
```

DDC itself must separately remain green under its own gates, and Daily-MLB must install the released DDC dependency from its normal hashed lock before migration certification.

## Definition of done
DDC-6 is complete when Daily-MLB no longer owns generic HTTP/odds/weather acquisition primitives, the same MLB-facing contracts and outputs are preserved, raw evidence lineage is stronger rather than weaker, the exact certified DDC package is reproducibly installed through Daily-MLB's hash lock, legacy duplicate code is removed only after equivalence, and the migration has a versioned architecture-conformance/local-validation record.
