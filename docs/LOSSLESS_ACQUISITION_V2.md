# Lossless acquisition contract v2

TDL-03A evolves the unreleased candidate to `0.2.0.dev1`. This minor development
version reflects a new shared evidence contract. Published 0.1.0 and the retained
0.1.1.dev1 artifact are unchanged. No production release or consumer switch is authorized.

## Atomicity and identity

An odds event, bookmaker, market and outcome each have their own structural
validation boundary. Invalid required structure rejects that entry, with a warning
and original JSON-pointer location; independently valid siblings survive. Empty
valid bookmakers/markets survive, including those emptied by rejected children.
Unknown market keys are provider facts, not permissions to model or recommend them.
Invalid optional update timestamps become unknown with a diagnostic, not the loss
of an otherwise valid quote. Raw timestamps, extensions and rejected fields remain
in exact evidence. Lists retain source order and duplicate/revised observations.

`AcquisitionEvidence.response_id` hashes provider/dataset, exact content digest,
sanitized request URI and source clocks. `observation_id(source_path)` identifies a
location in that observation. Parser changes do not change these source identities.
Receipt identity additionally includes parser version, disposition, evaluation
time, diagnostic codes and previous receipt. A quote revision therefore creates
new source evidence, never a sport prediction identity. Canonical sport event,
market-family, query, settlement and prediction identities remain consumer-owned.
Normalized outcome descriptions preserve provider participant labels where supplied.

## Capture, persistence and replay

HTTP captures immutable received bytes and retrieval clocks before JSON parsing,
including empty bodies, invalid JSON and unsuccessful HTTP responses. Retry bodies
are retained in order. An eventual no-response transport failure is distinguished
by diagnostics and `HttpError.failure_kind`; any earlier response evidence remains.
No received response is represented by an empty evidence tuple, not by empty bytes.

Per-call `AcquisitionCapture` persists received evidence through the existing
content-addressed store before provider normalization. Schema errors retain
`raw_payloads`, `raw_payload` and evidence receipts, including NWS's preceding point
response when its hourly response fails. Unexpected normalization exceptions become
safe evidence-backed errors without copying provider-controlled exception text.
Complete/partial/schema/HTTP dispositions create separate receipts and refer to the
received receipt; they never overwrite it. Failure codes and rejected odds paths
remain durable. Original HTTP status and source-date fallback survive replay.

`EvidenceLedger` writes `ddc-acquisition-evidence-v2` canonical JSON receipts into
the existing raw store's `ddc_receipts/acquisition_v2` namespace, alongside unchanged
provider/dataset content-addressed bodies. This is not a second database or sport
schema. Store publication uses complete temporary files, fsync and non-overwriting
atomic links; reads verify SHA-256. Linked/junction descendants and escaping paths
are rejected. The configured root must remain access-controlled and must not be
concurrently modified by untrusted processes.

Durable retention is opt-in: callers supply an explicit `retention_allowed` policy
that checks provider/dataset licensing, body content and secret restrictions before
any write. Denied retention writes nothing, including no digest receipt. In-memory
error evidence is not permission to log, export or publish it. Request headers are
not persisted. Known credential query keys (including OpenWeather appid), userinfo
and URL fragments are redacted. Exact bodies are never sanitized in place: if a
body contains credentials or prohibited content, the policy must deny its retention.
Consumer sanitized/canonical artifacts remain a separate compatibility layer.

`ReplayHttpClient` accepts explicitly ordered retained payloads, never makes a
network call, preserves raw bytes and original provenance, and reproduces invalid
JSON/HTTP status failures. It is an offline replay tool, not a production fallback.
A new parser produces a new evaluation receipt; explicit historical reprocessing
can reference the old receipt with `previous_receipt_id`. Retrieval/availability
remain original; evaluation may not precede retrieval. Unknown effective/source
times remain unknown, and HTTP Date is only the recorded source-date fallback.
Consumer snapshot/game-start constraints remain mandatory and unchanged.

## Weather contract

`ForecastSnapshot` v2 adds optional finite nonnegative `wind_gust_mph` separately
from sustained wind. OpenWeather's requested imperial unit supplies mph directly;
no gust is inferred. `wind_gust_status` distinguishes reported (including zero),
not supplied, invalid numeric representation and unsupported provider contract.
NWS hourly text does not supply a certified gust field, so its status is unsupported.
`to_json`/`from_json` use the explicit `ddc-forecast-v2` envelope and preserve clocks,
nulls, metadata and gust. Values round-trip without rounding. Provider issue time
and forecast effective time remain distinct from retrieval.

NWS non-object period siblings are retained in raw evidence and diagnosed while
valid period objects remain selectable, matching the current consumer. OpenWeather
invalid hourly timestamps/details/population of precipitation probability fail
explicitly with retained evidence. Forecast selection remains nearest-hour; callers
can enforce their required window through `WeatherAcquisitionResult.require_window`.
MLB's 60-minute policy is not a universal DDC default. Reporting offset formatting,
canonical participant resolution, sanitized artifact shapes and model science remain
consumer responsibilities; this candidate does not claim a completed consumer adapter.

## Compatibility and validation boundary

Existing constructor fields remain in order with appended defaults. Intentional
changes: empty received bytes are now valid ProviderPayload evidence; error types
retain evidence; stronger URL redaction; invalid optional odds timestamps retain
quotes with warnings; normalized records carry source locations; explicit v2 forecast
serialization. Provider raw objects do not replace typed normalized contracts.
Prior released artifacts and legacy consumer source are untouched.

Development/compiler locks are regenerated with Python 3.12, pip 26.2, pip-tools
7.6.1 and setuptools 83.0.0. Colorama is explicit across supported developer
platforms; dev lock annotations are disabled to avoid platform-dependent comments.
The repository CI command uses the same compiler flags. A green candidate still
requires reviewed-main architecture/release certification before a production pin.
