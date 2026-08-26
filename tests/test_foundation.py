from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from daily_data_core.http import redact_url
from daily_data_core.provenance import FileSystemRawEvidenceStore, sha256_bytes
from daily_data_core.providers import ProviderPayload
from daily_data_core.temporal import TemporalProvenance


def test_temporal_provenance_enforces_awareness_and_order() -> None:
    observed = datetime(2026, 8, 26, 18, 0, tzinfo=UTC)
    provenance = TemporalProvenance(
        observed_at=observed,
        available_at=observed - timedelta(seconds=1),
    )
    assert provenance.eligible_at(observed)

    with pytest.raises(ValueError):
        TemporalProvenance(
            observed_at=observed,
            available_at=observed + timedelta(seconds=1),
        )

    with pytest.raises(ValueError):
        TemporalProvenance(
            observed_at=datetime(2026, 8, 26, 18, 0),
            available_at=observed,
        )


def test_raw_evidence_store_is_content_addressed_and_idempotent(tmp_path: Path) -> None:
    now = datetime(2026, 8, 26, 18, 0, tzinfo=UTC)
    payload = ProviderPayload(
        content=b'{"ok":true}',
        content_type="application/json",
        source_uri="https://example.test/data",
        provenance=TemporalProvenance(observed_at=now, available_at=now),
    )
    store = FileSystemRawEvidenceStore(tmp_path)
    first = store.put("provider", "market.odds", payload)
    second = store.put("provider", "market.odds", payload)

    assert first == second
    assert first.sha256 == sha256_bytes(payload.content)
    assert (tmp_path / first.relative_path).read_bytes() == payload.content


def test_redact_url_hides_credentials_but_preserves_nonsecret_query() -> None:
    safe = redact_url(
        "https://example.test/path?apiKey=secret&regions=us&access_token=abc"
    )
    assert "secret" not in safe
    assert "abc" not in safe
    assert "regions=us" in safe
    assert "%5BREDACTED%5D" in safe
