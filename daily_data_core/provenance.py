"""Content-addressed immutable raw evidence storage."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from daily_data_core.providers import ProviderPayload

_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9_.-]+$")


class RawEvidenceCollisionError(RuntimeError):
    """Existing content-addressed object did not match its digest/content."""


@dataclass(frozen=True, slots=True)
class RawEvidenceArtifact:
    evidence_id: str
    provider_id: str
    dataset_key: str
    sha256: str
    relative_path: Path
    size_bytes: int
    content_type: str


@runtime_checkable
class RawEvidenceStore(Protocol):
    def put(
        self,
        provider_id: str,
        dataset_key: str,
        payload: ProviderPayload,
    ) -> RawEvidenceArtifact: ...


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def evidence_id_for(
    provider_id: str,
    dataset_key: str,
    content_sha256: str,
) -> str:
    identity = f"{provider_id}\0{dataset_key}\0{content_sha256}".encode()
    return hashlib.sha256(identity).hexdigest()


def _validate_segment(value: str, label: str) -> None:
    if _SAFE_SEGMENT.fullmatch(value) is None or value in {".", ".."}:
        raise ValueError(
            f"{label} must be a nonblank filesystem-safe identifier"
        )


@dataclass(frozen=True, slots=True)
class FileSystemRawEvidenceStore:
    root: Path

    def put(
        self,
        provider_id: str,
        dataset_key: str,
        payload: ProviderPayload,
    ) -> RawEvidenceArtifact:
        _validate_segment(provider_id, "provider_id")
        _validate_segment(dataset_key, "dataset_key")
        digest = sha256_bytes(payload.content)
        relative_path = Path(provider_id) / dataset_key / f"{digest}.raw"
        object_path = self.root / relative_path
        object_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with object_path.open("xb") as handle:
                handle.write(payload.content)
        except FileExistsError:
            existing = object_path.read_bytes()
            if existing != payload.content or sha256_bytes(existing) != digest:
                raise RawEvidenceCollisionError(
                    "raw evidence collision at content-addressed path "
                    f"{object_path}"
                ) from None

        return RawEvidenceArtifact(
            evidence_id=evidence_id_for(provider_id, dataset_key, digest),
            provider_id=provider_id,
            dataset_key=dataset_key,
            sha256=digest,
            relative_path=relative_path,
            size_bytes=len(payload.content),
            content_type=payload.content_type,
        )
