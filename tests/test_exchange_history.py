from __future__ import annotations

import io
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import requests

from daily_data_core.acquisition import AcquisitionCapture, AcquisitionReplayClient, EvidenceLedger
from daily_data_core.history import ReplayMismatchError, SchemaValidationError, digest
from daily_data_core.http import HttpClient, HttpError
from daily_data_core.odds import OddsProviderSchemaError, TheOddsApiClient
from daily_data_core.provenance import FileSystemRawEvidenceStore, RawEvidenceCollisionError
from daily_data_core.redirects import RedirectPolicy
from daily_data_core.weather import NwsWeatherClient

type ResponseSpec = tuple[int, bytes, dict[str, str]] | BaseException


class FixtureAdapter(requests.adapters.BaseAdapter):
    def __init__(self, values: list[ResponseSpec]) -> None:
        self.values = iter(values)
        self.requests: list[requests.PreparedRequest] = []
        self.before_send: Any = None

    def send(
        self, request: requests.PreparedRequest, *args: Any, **kwargs: Any
    ) -> requests.Response:
        if self.before_send is not None:
            self.before_send(len(self.requests), request)
        self.requests.append(request)
        value = next(self.values)
        if isinstance(value, BaseException):
            raise value
        status, body, headers = value
        response = requests.Response()
        response.request = request
        response.url = request.url or ""
        response.status_code = status
        response._content = body
        response.raw = io.BytesIO(body)
        response.headers.update({"Content-Type": "application/json", **headers})
        return response

    def close(self) -> None:
        pass


@pytest.fixture(autouse=True)
def forbid_network_and_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("unexpected real network")

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", forbidden)
    monkeypatch.setattr("daily_data_core.http.time.sleep", lambda _: None)


def setup(
    path: Path, values: list[ResponseSpec], **kwargs: Any
) -> tuple[HttpClient, FixtureAdapter, EvidenceLedger]:
    client = HttpClient(max_attempts=kwargs.pop("max_attempts", 1), **kwargs)
    client.session.trust_env = False
    adapter = FixtureAdapter(values)
    client.session.mount("https://", adapter)
    client.session.mount("http://", adapter)
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(path), lambda _: True, lambda _: True)
    return client, adapter, ledger


def collect(client: Any, ledger: EvidenceLedger | None = None) -> Any:
    return TheOddsApiClient(client, ledger).collect(sport_key="baseball_mlb", api_key="synthetic")


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_redirect_is_two_exchanges_one_attempt_and_replays(
    tmp_path: Path, status: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, adapter, ledger = setup(
        tmp_path,
        [
            (status, b"redirect bytes", {"Location": "/next", "x-requests-remaining": "10"}),
            (200, b"[]", {"x-requests-remaining": "9"}),
        ],
    )
    original = collect(client, ledger)
    restored = EvidenceLedger(ledger.store, lambda _: True, lambda _: True).read_history(
        original.history.receipt_id
    )
    assert restored == original.history
    call = restored.calls[0]
    assert original.diagnostics.attempts == 1 and original.diagnostics.retries_performed == 0
    assert len(call.attempts) == 1 and len(call.attempts[0].exchanges) == 2
    first, last = call.attempts[0].exchanges
    assert first.payload is not None and last.payload is not None
    assert first.attempt_id == last.attempt_id and first.exchange_id != last.exchange_id
    assert first.payload.content == b"redirect bytes" and last.payload.content == b"[]"
    assert dict(first.quota)["requests_remaining"] == "10"
    assert dict(last.quota)["requests_remaining"] == "9"
    assert first.redirect_target == last.request_url == "https://api.the-odds-api.com/next"
    assert first.decision == "follow" and last.decision == "terminal"
    assert [r.method for r in adapter.requests] == ["GET", "GET"]
    assert len(restored.evidence) == 2 and call.document()["exchange_count"] == 2
    calls = 0

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        raise AssertionError("strict replay attempted HTTP")

    monkeypatch.setattr(requests.Session, "request", forbidden)
    monkeypatch.setattr(FixtureAdapter, "send", forbidden)
    before = set(tmp_path.rglob("*.raw"))
    replay = AcquisitionReplayClient(restored)
    repeated = collect(replay, ledger)
    assert repeated == original and calls == replay.network_calls == 0
    assert before == set(tmp_path.rglob("*.raw"))


@pytest.mark.parametrize(
    ("location", "reason"),
    [
        ("https://evil.invalid/x", "untrusted_target"),
        ("http://api.the-odds-api.com/x", "https_downgrade"),
        ("ftp://api.the-odds-api.com/x", "unsupported_scheme"),
        ("https://user:password@example.invalid/x", "malformed_location"),
        ("https://[broken", "malformed_location"),
        ("/bad path", "malformed_location"),
        ("/next?apiKey=secret", "sensitive_redirect_query"),
        ("", "missing_location"),
    ],
)
def test_rejected_redirect_retains_body_before_blocking(
    tmp_path: Path, location: str, reason: str
) -> None:
    client, adapter, ledger = setup(tmp_path, [(302, b"blocked redirect", {"Location": location})])
    with pytest.raises(HttpError) as caught:
        collect(client, ledger)
    assert caught.value.history is not None
    history = ledger.read_history(caught.value.history.receipt_id)
    assert len(adapter.requests) == 1
    exchange = history.calls[0].attempts[0].exchanges[0]
    assert exchange.payload is not None
    assert exchange.decision == reason and exchange.payload.content == b"blocked redirect"
    assert history.calls[0].terminal_outcome == "redirect_error"
    assert "secret" not in str(history.document()) and "password" not in str(exchange.document())
    with pytest.raises(HttpError) as repeated:
        collect(AcquisitionReplayClient(history))
    assert repeated.value.history == history


def test_trusted_cross_host_strips_all_credentials(tmp_path: Path) -> None:
    client, adapter, ledger = setup(
        tmp_path,
        [
            (
                302,
                b"hop",
                {"Location": "https://trusted.invalid/next", "Set-Cookie": "private-cookie"},
            ),
            (200, b"[]", {}),
        ],
        redirect_policy=RedirectPolicy(trusted_hosts=frozenset({"trusted.invalid"})),
    )
    client.session.auth = ("private-user", "private-password")
    client.session.headers.update(
        {"Authorization": "private-auth", "X-Api-Key": "private-key", "Cookie": "private-cookie"}
    )
    original = collect(client, ledger)
    assert len(adapter.requests) == 2
    forwarded = str(dict(adapter.requests[1].headers)) + str(adapter.requests[1].url)
    assert "private-" not in forwarded and "synthetic" not in forwarded
    for path in tmp_path.rglob("*.raw"):
        assert b"private-" not in path.read_bytes()
    assert len(original.history.calls[0].attempts[0].exchanges) == 2


def test_upgrade_and_provider_neutrality(tmp_path: Path) -> None:
    client, adapter, ledger = setup(
        tmp_path, [(301, b"hop", {"Location": "https://neutral.invalid/secure"}), (200, b"{}", {})]
    )
    with AcquisitionCapture(client, "neutral", "facts", "test-v1", ledger) as capture:
        capture.get_json("http://neutral.invalid/start")
        capture.finish("complete")
    assert [r.url for r in adapter.requests] == [
        "http://neutral.invalid/start",
        "https://neutral.invalid/secure",
    ]
    assert capture.history is not None
    assert ledger.read_history(capture.history.receipt_id) == capture.history


@pytest.mark.parametrize("limit", [0, 1])
def test_redirect_depth_limit(tmp_path: Path, limit: int) -> None:
    client, adapter, ledger = setup(
        tmp_path,
        [(302, b"one", {"Location": "/two"}), (302, b"two", {"Location": "/three"})],
        redirect_policy=RedirectPolicy(max_redirects=limit),
    )
    with pytest.raises(HttpError) as caught:
        collect(client, ledger)
    assert len(adapter.requests) == limit + 1
    assert caught.value.history is not None
    assert caught.value.history.calls[0].attempts[0].exchanges[-1].decision == "redirect_limit"


def test_loop_is_terminal_without_extra_send(tmp_path: Path) -> None:
    client, adapter, ledger = setup(
        tmp_path, [(302, b"one", {"Location": "/two"}), (302, b"two", {"Location": "/two"})]
    )
    with pytest.raises(HttpError) as caught:
        collect(client, ledger)
    assert len(adapter.requests) == 2
    assert caught.value.history is not None
    assert caught.value.history.calls[0].attempts[0].exchanges[-1].decision == "redirect_loop"


@pytest.mark.parametrize(
    "failure", [requests.Timeout("private-token"), requests.ConnectionError("private-token")]
)
def test_transport_failure_after_redirect_preserves_received_hop(
    tmp_path: Path, failure: Exception
) -> None:
    client, adapter, ledger = setup(tmp_path, [(302, b"hop", {"Location": "/next"}), failure])
    with pytest.raises(HttpError) as caught:
        collect(client, ledger)
    assert caught.value.history is not None
    restored = ledger.read_history(caught.value.history.receipt_id)
    attempt = restored.calls[0].attempts[0]
    assert len(adapter.requests) == len(attempt.exchanges) == 2
    assert attempt.outcome == "transport_error" and attempt.payload is None
    assert attempt.exchanges[0].payload is not None
    assert attempt.exchanges[0].payload.content == b"hop"
    assert attempt.exchanges[1].payload is None
    assert "private-token" not in str(attempt.document())
    with pytest.raises(HttpError) as repeated:
        collect(AcquisitionReplayClient(restored))
    assert repeated.value.history == restored


def test_provider_schema_error_after_redirect(tmp_path: Path) -> None:
    client, _, ledger = setup(tmp_path, [(302, b"hop", {"Location": "/next"}), (200, b"[{}]", {})])
    with pytest.raises(OddsProviderSchemaError) as caught:
        collect(client, ledger)
    assert caught.value.history is not None
    history = ledger.read_history(caught.value.history.receipt_id)
    assert history.disposition == "schema_error" and len(history.evidence) == 2
    with pytest.raises(OddsProviderSchemaError) as repeated:
        collect(AcquisitionReplayClient(history))
    assert repeated.value.history == history


def test_schema_retry_starts_new_attempt_not_third_hop(tmp_path: Path) -> None:
    def validator(value: object) -> None:
        if value != []:
            raise SchemaValidationError("invalid")

    client, adapter, ledger = setup(
        tmp_path,
        [(302, b"hop", {"Location": "/next"}), (200, b"[{}]", {}), (200, b"[]", {})],
        max_attempts=2,
        schema_validator=validator,
        validator_version="test-v1",
        retry_schema_errors=True,
    )
    original = collect(client, ledger)
    attempts = original.history.calls[0].attempts
    assert [len(a.exchanges) for a in attempts] == [2, 1]
    assert [a.outcome for a in attempts] == ["schema_error", "success"]
    assert adapter.requests[0].url == adapter.requests[2].url
    replay = AcquisitionReplayClient(
        ledger.read_history(original.history.receipt_id), validator_versions=frozenset({"test-v1"})
    )
    assert collect(replay).history == original.history


def test_crash_leaves_durable_hop_and_ambiguous_next_start(tmp_path: Path) -> None:
    client, adapter, ledger = setup(
        tmp_path, [(302, b"durable hop", {"Location": "/next"}), KeyboardInterrupt()]
    )
    identities: list[tuple[str, int]] = []

    def before_send(index: int, request: requests.PreparedRequest) -> None:
        if index == 1:
            paths = list(tmp_path.glob("ddc_receipts/exchange_v1/*.raw"))
            assert len(paths) == 1
            import json

            doc = json.loads(paths[0].read_bytes())
            identities.append((doc["call_id"], doc["attempt_ordinal"]))

    adapter.before_send = before_send
    with pytest.raises(KeyboardInterrupt):
        collect(client, ledger)
    call, attempt = identities[0]
    restarted = EvidenceLedger(ledger.store, lambda _: True, lambda _: True)
    first = restarted.exchange_state(call, attempt, 1)
    second = restarted.exchange_state(call, attempt, 2)
    assert set(first) == {"exchange_start_v1", "exchange_received_v1", "exchange_v1"}
    assert set(second) == {"exchange_start_v1"}
    assert not list(tmp_path.glob("ddc_receipts/history_v4/*.raw"))
    assert len(adapter.requests) == 2  # Reading state did not reacquire or resume.


def test_reprocess_and_old_history_do_not_invent_hops(tmp_path: Path) -> None:
    client, _, ledger = setup(tmp_path, [(302, b"hop", {"Location": "/next"}), (200, b"[]", {})])
    original = collect(client, ledger)
    processed = collect(AcquisitionReplayClient(original.history, mode="reprocess"), ledger)
    assert processed.history.previous_history_id == original.history.receipt_id
    assert processed.history.calls == original.history.calls
    call = original.history.calls[0]
    old_call = replace(
        call, redirect_policy=(), attempts=tuple(replace(a, exchanges=()) for a in call.attempts)
    )
    old = replace(original.history, acquisition_id="legacy", calls=(old_call,))
    ledger.put_history(old)
    assert ledger.read_history(old.receipt_id) == old
    with pytest.raises(ReplayMismatchError, match="exchange history"):
        AcquisitionReplayClient(old)
    assert ledger.read_history(old.receipt_id).calls[0].attempts[0].exchanges == ()


def test_exchange_identity_cannot_be_rewritten(tmp_path: Path) -> None:
    client, _, ledger = setup(tmp_path, [(200, b"[]", {})])
    history = collect(client, ledger).history
    exchange = history.calls[0].attempts[0].exchanges[0]
    with pytest.raises(RawEvidenceCollisionError):
        ledger.put_exchange(
            replace(exchange, headers=(("date", "changed"),)), "the_odds_api", "odds", "test-v1"
        )
    receipt = ledger.store.resolve_identity("exchange_v1", digest(exchange.exchange_id))
    assert receipt


def test_nws_redirect_does_not_bypass_host_validation(tmp_path: Path) -> None:
    client, adapter, ledger = setup(
        tmp_path, [(302, b"hop", {"Location": "https://evil.invalid/hourly"})]
    )
    with pytest.raises(HttpError) as caught:
        NwsWeatherClient(client, "fixture", ledger).collect(
            1, 2, datetime(2026, 7, 30, 14, tzinfo=UTC)
        )
    assert len(adapter.requests) == 1 and caught.value.history is not None
    assert caught.value.history.calls[0].attempts[0].exchanges[0].decision == "untrusted_target"


def test_raw_and_exchange_receipt_precede_policy_and_pit_is_not_backdated(tmp_path: Path) -> None:
    class InspectPolicy(RedirectPolicy):
        def resolve(
            self, current: str, location: str | None, visited: set[str]
        ) -> tuple[str | None, str]:
            assert len(list(tmp_path.glob("ddc_receipts/exchange_received_v1/*.raw"))) == 1
            assert any(p.read_bytes() == b"hop" for p in tmp_path.glob("the_odds_api/odds/*.raw"))
            return super().resolve(current, location, visited)

    client, _, ledger = setup(
        tmp_path,
        [(302, b"hop", {"Location": "/next"}), (200, b"[]", {})],
        redirect_policy=InspectPolicy(),
    )
    history = collect(client, ledger).history
    first, last = history.calls[0].attempts[0].exchanges
    assert first.payload is not None and last.payload is not None
    assert last.payload.provenance.available_at >= first.completed_at
    assert not last.payload.provenance.eligible_at(first.started_at)
    assert last.payload.provenance.eligible_at(last.completed_at)
    state = ledger.exchange_state(first.call_id, first.attempt_ordinal, first.ordinal)
    assert "attempt_terminal_receipt" in state


def test_retention_denial_does_not_write_response_or_exchange(tmp_path: Path) -> None:
    client, _, _ = setup(tmp_path, [(302, b"hop", {"Location": "/next"}), (200, b"[]", {})])
    ledger = EvidenceLedger(FileSystemRawEvidenceStore(tmp_path), lambda _: False, lambda _: False)
    result = collect(client, ledger)
    assert len(result.history.calls[0].attempts[0].exchanges) == 2
    assert not list(tmp_path.rglob("*.raw"))


def test_response_body_failure_retains_prior_hop_and_known_status(tmp_path: Path) -> None:
    class BrokenBody(requests.Response):
        @property
        def content(self) -> bytes:
            raise requests.ConnectionError("private-body-error")

    class BodyFailureAdapter(FixtureAdapter):
        def send(
            self, request: requests.PreparedRequest, *args: Any, **kwargs: Any
        ) -> requests.Response:
            if not self.requests:
                return super().send(request, *args, **kwargs)
            self.requests.append(request)
            response = BrokenBody()
            response.status_code = 200
            response.headers["x-requests-remaining"] = "7"
            return response

    client, _, ledger = setup(tmp_path, [])
    adapter = BodyFailureAdapter([(302, b"hop", {"Location": "/next"})])
    client.session.mount("https://", adapter)
    with pytest.raises(HttpError) as caught:
        collect(client, ledger)
    assert caught.value.history is not None
    history = ledger.read_history(caught.value.history.receipt_id)
    first, last = history.calls[0].attempts[0].exchanges
    assert first.payload is not None and first.payload.content == b"hop"
    assert last.payload is None and last.response_status == 200
    assert dict(last.quota)["requests_remaining"] == "7"
    with pytest.raises(HttpError) as repeated:
        collect(AcquisitionReplayClient(history))
    assert repeated.value.history == history
