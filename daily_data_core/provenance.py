"""Content-addressed immutable raw evidence storage."""

from __future__ import annotations

import hashlib
import os
import re
import tempfile
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
        raise ValueError(f"{label} must be a nonblank filesystem-safe identifier")


@dataclass(frozen=True, slots=True)
class FileSystemRawEvidenceStore:
    root: Path

    def bind_identity(self, namespace: str, identity: str, receipt: str) -> None:
        """One completed history identity can refer to exactly one immutable receipt."""
        if re.fullmatch(r"[0-9a-f]{64}", receipt) is None:
            raise ValueError("invalid receipt binding")
        path = self._path("ddc_history_bindings", namespace, identity)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(receipt.encode("ascii"))
                handle.flush()
                os.fsync(handle.fileno())
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != receipt.encode("ascii"):
                raise RawEvidenceCollisionError(
                    "completed acquisition identity cannot be rewritten"
                ) from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def verify_identity(self, namespace: str, identity: str, receipt: str) -> None:
        if self._path("ddc_history_bindings", namespace, identity).read_bytes() != receipt.encode(
            "ascii"
        ):
            raise RawEvidenceCollisionError("history identity binding mismatch")

    def resolve_identity(self, namespace: str, identity: str) -> str:
        receipt = self._path("ddc_history_bindings", namespace, identity).read_text("ascii")
        if re.fullmatch(r"[0-9a-f]{64}", receipt) is None:
            raise RawEvidenceCollisionError("invalid history binding")
        return receipt

    def _path(self, provider_id: str, dataset_key: str, digest: str) -> Path:
        _validate_segment(provider_id, "provider_id")
        _validate_segment(dataset_key, "dataset_key")
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
            raise ValueError("invalid content digest")
        root = self.root.resolve()
        path = root / provider_id / dataset_key / f"{digest}.raw"
        for component in (path.parent.parent, path.parent, path):
            if component.is_symlink() or component.is_junction():
                raise ValueError("evidence paths cannot redirect through links")
        if not path.resolve().is_relative_to(root):
            raise ValueError("evidence path escapes root")
        return path

    def read(self, provider_id: str, dataset_key: str, digest: str) -> bytes:
        content = self._path(provider_id, dataset_key, digest).read_bytes()
        if sha256_bytes(content) != digest:
            raise RawEvidenceCollisionError("raw evidence failed digest verification")
        return content

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
        object_path = self._path(provider_id, dataset_key, digest)
        object_path.parent.mkdir(parents=True, exist_ok=True)

        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(dir=object_path.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(payload.content)
                handle.flush()
                os.fsync(handle.fileno())
            # Link publishes the complete bytes atomically and never replaces history.
            os.link(temporary, object_path)
        except FileExistsError:
            existing = object_path.read_bytes()
            if existing != payload.content or sha256_bytes(existing) != digest:
                raise RawEvidenceCollisionError(
                    f"raw evidence collision at content-addressed path {object_path}"
                ) from None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

        return RawEvidenceArtifact(
            evidence_id=evidence_id_for(provider_id, dataset_key, digest),
            provider_id=provider_id,
            dataset_key=dataset_key,
            sha256=digest,
            relative_path=relative_path,
            size_bytes=len(payload.content),
            content_type=payload.content_type,
        )
