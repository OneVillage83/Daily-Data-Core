# Source Extraction Map V1

## Daily-MLB candidates
- `app/http.py` -> generalize into DDC HTTP/retry diagnostics.
- `app/raw_payloads.py` -> generalize provider/endpoint literals into extensible provenance contracts.
- `app/redaction.py` -> shared safe logging/redaction behavior.
- `app/collectors/odds_collector.py` -> replace hard-coded `baseball_mlb` endpoint with configurable The Odds API sport key.
- `app/processors/odds_processor.py` -> extract odds math, freshness, no-vig, book consensus and disagreement; retain MLB identity hooks in Daily-MLB.
- `app/collectors/nws_weather_collector.py` -> shared NWS forecast adapter.
- `app/collectors/openweather_collector.py` -> shared OpenWeather forecast adapter.
- `app/processors/weather_processor.py` -> source comparison is shared; baseball wind classification remains MLB.
- `app/data/mlb_stadiums.json` / `app/stadiums.py` -> generic venue fields may move to DDC; MLB-specific stadium geometry remains MLB.

## Daily-NFL candidates
- `daily_nfl/providers/raw_store.py` -> DDC content-addressed raw evidence store.
- generic portions of `daily_nfl/providers/contracts.py` -> DDC provider descriptor/capability/provenance contracts.
- generic portions of provider metadata/licensing -> DDC.

Remain in Daily-NFL:
- NFL dataset taxonomy;
- nflverse adapters;
- football normalization/reconciliation;
- NFL PIT/leakage engine and football-specific persistence schemas.

## Extraction method
Do not delete legacy code first. Introduce DDC, add compatibility wrappers/imports in the sport repo, run regression/architecture certification, then remove duplicate implementation in a separate change.
