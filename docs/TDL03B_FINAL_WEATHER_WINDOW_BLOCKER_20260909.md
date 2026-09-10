# TDL-03B final: forecast-window rejection lineage blocker

Continuation (2026-09-09T22:06:11-07:00, America/Los_Angeles): TDL-03E repairs this
blocker locally; read `TDL03E_FORECAST_WINDOW_LINEAGE_HANDOFF_20260909.md` first.
The failure receipts below remain historical and unchanged.

Updated: 2026-09-09T21:35:21-07:00 (America/Los_Angeles).

**BLOCKED before publication, dependency introduction or production cutover.**
This is a newly executed consumer-admission failure, not a remote-CI wait or an
owner-approval issue. It does not erase the earlier passing certification receipts.

## Exact prepared release

DDC branch `codex/ddc6-mlb-migration-20260909`, PR #4; parent
`0ea51d2ec798b64ae6376603d9e0a72201b2ab64`.
Prepared source **`c756f0a6595542cc4890eec206587ddd7128c50f`** changes package/project
version from dev4 to **0.2.0**, plus release-preparation documentation only.
No acquisition/normalization/replay implementation or dependency changed.
Prepared source tree: `838a158db835318799afd7c637b6fd1f5e992407`.
Wheel `daily_data_core-0.2.0-py3-none-any.whl`, SHA-256
**`4f9104e57a26bdcc85cb1f2b32a944e84661ee6dfce5199f2b91d9b35db8fe16`**.
Two independent clean Git-archive builds matched. Retained local artifact:
`.validation/tdl03b-final-wheel-one/`; duplicate in `tdl03b-final-wheel-two/`.
Tooling: Python 3.12.10, pip 26.2, pip-tools 7.6.1, build 1.5.0, setuptools 83.0.0,
wheel 0.48.0, SOURCE_DATE_EPOCH=1787788800, build --wheel --no-isolation.
The prepared artifact remains unreleased; planned tag v0.2.0 does not exist.
Do not overwrite the retained dev4 or prepared 0.2.0 bytes when repairing source.
Choose a new candidate identity under the existing immutable-artifact policy.

The certified dev4 source/tree/run mapping remains unchanged:
`3ec5b7a1d39abadac7fa76348f0c2f943f882e7e` /
`829ac070b2e11993346a119dcc5b6ad169845e9a` / CI run `34436406742`.
That run did not exercise the new forecast-window rejection case. Dev4's artifact
hash cannot certify the differently versioned 0.2.0 wheel.

## Reproducer and observed failure

The actual consumer rule is MLB's retained 60-minute forecast-selection window.
Synthetic fixture: target **2026-07-30T16:00:00+00:00**, nearest forecast
**2026-07-30T14:00:00+00:00**. No historical/provider evidence is fabricated or
backdated; retrieval clocks remain actual execution clocks. Fixture values are
only a deterministic contract test, not a live weather claim.

The candidate projection calls DDC's `WeatherAcquisitionResult.require_window`
with the MLB-owned window constant. Both NWS and OpenWeather reject the 120-minute
offset correctly. However, weather.py lines 200-210 construct a
`WeatherProviderSchemaError` with raw payloads/evidence only; `history` and
`diagnostics` remain None. The completed source acquisition is durably readable,
but the thrown failure cannot directly identify its logical calls, attempts or
exchanges. A strict replay followed by the same window check loses those references
again. No source repair or MLB workaround was applied.

This does **not** mean raw bytes were lost, a completed acquisition was wrong to be
marked complete, or replay made a network call. Acquisition success and consumer
forecast-admission rejection are distinct outcomes. The repair must preserve that
separation rather than rewrite completed acquisition history to schema_error.

Private executable gate: `scripts/check_ddc6_weather_window_history.py` in MLB.
Contract `DDC6_WEATHER_WINDOW_HISTORY_ADMISSION_V1`:

- **7/13 pass, exit 1** against both exact dev4 and prepared 0.2.0 wheels.
- Correct window rejection, raw/evidence preservation, and persisted-history read
  pass for both providers; actual external network calls are **0**.
- **6 failures:** history reference, request diagnostics and replayed rejection
  history linkage for each of NWS and OpenWeather.
- NWS: two source calls/exchanges, two raw payloads retained; error history absent.
- OpenWeather: one source call/exchange, one raw payload retained; error history absent.
- The original red pytest assertion was `DDC window rejection drops acquisition-history
  reference`; the committed CLI retains the failing acceptance checks and exits 1.

The public DDC repo contains this generic description only; private MLB code,
fixtures, logs, source data and implementation are not copied here.

## Safe completed work and limits

Final-version source: **114 tests passed**, Ruff passed, strict mypy **26 files**
passed. Both prepared-wheel builds matched. Existing exact-wheel gates still pass:
redirect **8/8**, replay **10/10**, admission **7/7**, comparison **80/80**;
external/replay network counters remain zero. Pinned lock regeneration has zero
diff; hash-locked vulnerability audit reports no known vulnerabilities.
Isolated hash-installed wheel suite: **114 passed** (13.18 s), import/version
asserted from site-packages, dependency consistency passed. MLB oracle **119 passed**
(10.17 s); MLB Ruff and nonincremental strict mypy **767 files** passed.
Runtime lock SHA-256: `7519ae45a78d9a4a490071a070ca1f72081990439bcf925c9ec5a8bba86ff2af`.
Development lock SHA-256: `10fe722048eae1881dffb1ae48c804cd953667b163ebd8ba446a4ba676071e2f`.
Repository secret scans passed: DDC **58 tracked files**, MLB **1,060 tracked
files**, no findings; environment files excluded (`--skip-env`). Staged diff check
passed. No live credential validation is claimed.

Only release identity/preparation and executable admission/documentation are retained.
An experimental odds projection passed two synthetic partial-sibling/redirect replay
checks, but was not registered or retained as production code: it does not constitute
complete adapter/persistence/runtime admission. No production pin, adapter switch,
15-phase DDC rehearsal, tiny real-provider run or legacy retirement is claimed.
The current MLB legacy implementation remains **ACTIVE_PRODUCTION_AUTHORITY**.
No production rollback is needed because no cutover occurred.

GitHub main protection/rulesets were checked read-only: no protection/rulesets and
no separate owner approval requirement in current DDC policy. Publication is
withheld for the evidence failure, not for missing owner permission. Docker remains
not applicable to DDC; no hosted CI or Docker job was run in this task.

## Next bounded production repair / validator handoff

Reconcile forecast-window rejection as an explicit versioned validation decision
referencing the unchanged acquisition history, exact target/window policy, original
raw evidence and request diagnostics. Keep MLB's 60-minute rule in MLB. Preserve
success versus rejection, strict replay versus reprocess, and immutable original
clocks. Do not patch only the caller or relabel completed acquisition history.
Add regression coverage at the actual MLB exception/persistence boundary and make
the new exact-wheel gate pass **13/13** before resuming release/cutover work.

After source repair and local proof, a lower-cost validator should verify exact
source/tree and new artifact digest, reproduce clean builds, isolated wheel tests,
all five admission gates, MLB oracle, hashes/security and hosted CI. Do not use a
green old workflow to waive this gate. Current remote CI is deliberately not run.

Science remains **0 AVAILABLE / 5 BLOCKED / 22 MISSING**. No model/registry/PIT/Gate
permission, threshold or production architecture was changed by this checkpoint.
