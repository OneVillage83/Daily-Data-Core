# Daily Data Core Source Extraction Map

This map records where the initial shared-core behavior originated and how ownership changes as consumers migrate.

| Source behavior | Original/current location | DDC target | Migration state |
|---|---|---|---|
| HTTP retries / Retry-After / diagnostics / safe URL reporting | `Daily-MLB/app/http.py` | `daily_data_core/http.py` | DDC implemented; MLB compatibility migration pending |
| raw provider capture / checksums / evidence | `Daily-MLB/app/raw_payloads.py`; newer generic pattern also exists in `Daily-NFL/daily_nfl/providers/raw_store.py` | `daily_data_core/providers.py`, `provenance.py`, `temporal.py` | DDC exact-byte evidence implemented; consumer artifact adapters pending |
| The Odds API acquisition | `Daily-MLB/app/collectors/odds_collector.py` | `daily_data_core/odds.py` | multi-sport DDC adapter implemented; MLB equivalence pending |
| implied probability / no-vig / hold / generic freshness | `Daily-MLB/app/processors/odds_processor.py` | `daily_data_core/markets.py` | DDC primitives implemented; mature MLB report processor remains local during DDC-6 |
| market/book quote timestamps | Daily-MLB provider payload/processor path | `daily_data_core/odds.py` | bookmaker + market timestamps preserved after DDC-6 review |
| NWS acquisition | `Daily-MLB/app/collectors/nws_weather_collector.py` | `daily_data_core/weather.py` | implemented; MLB adapter/equivalence pending |
| OpenWeather acquisition | `Daily-MLB/app/collectors/openweather_collector.py` | `daily_data_core/weather.py` | implemented including cloud cover/pressure; MLB adapter/equivalence pending |
| generic weather comparison | `Daily-MLB/app/processors/weather_processor.py::compare` | `daily_data_core/weather.py` | implemented; exact output adapter pending |
| baseball wind interpretation | `Daily-MLB/app/processors/weather_processor.py::wind_impact` | **stays Daily-MLB** | not extracted |
| venue coordinates / generic roof / bearing | MLB stadium metadata and future sport venue data | `daily_data_core/venues.py` | primitives implemented; sport team→venue identity stays local |
| neutral distance / timezone / rest | planned cross-sport travel work | `daily_data_core/travel.py` | implemented; sport recovery transforms stay local |
| generic provider capability/licensing metadata | newer Daily-NFL M3 provider layer | `daily_data_core/providers.py` | DDC implemented; NFL convergence deferred to DDC-7 |

## Evidence-layer distinction
Daily-MLB's existing Phase-1 raw artifact is sanitized canonical JSON and its recorded checksum is over those sanitized bytes. DDC's evidence layer preserves the exact provider response bytes. DDC-6 must keep both meanings explicit; it must not rewrite the MLB artifact contract simply because DDC evidence is stronger.

## Distribution distinction
Source extraction does not make sport repos depend on a DDC branch. Certified DDC code is distributed through a versioned wheel release and consumed through each sport repo's hashed dependency lock. See `PACKAGE_RELEASE_POLICY.md`.
