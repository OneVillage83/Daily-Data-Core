"""GET-only redirect policy; no implicit trust or credential forwarding."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})


@dataclass(frozen=True, slots=True)
class RedirectPolicy:
    max_redirects: int = 5
    trusted_hosts: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not 0 <= self.max_redirects <= 30:
            raise ValueError("redirect bound must be between zero and thirty")
        if any(
            not h or h != h.lower() or any(c in h for c in "/:@?#\\") for h in self.trusted_hosts
        ):
            raise ValueError("trusted redirect hosts must be explicit lowercase hostnames")

    def document(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                (
                    ("version", "ddc-get-redirect-policy-v1"),
                    ("max_redirects", str(self.max_redirects)),
                    ("trusted_hosts", ",".join(sorted(self.trusted_hosts))),
                    ("credentials", "never-forward-on-redirect"),
                )
            )
        )

    def resolve(
        self, current: str, location: str | None, visited: set[str]
    ) -> tuple[str | None, str]:
        if not location:
            return None, "missing_location"
        if any(ord(c) < 33 or ord(c) == 127 for c in location) or "\\" in location:
            return None, "malformed_location"
        try:
            target = urljoin(current, location)
            old, new = urlsplit(current), urlsplit(target)
            if new.scheme not in {"http", "https"}:
                return None, "unsupported_scheme"
            if not new.hostname or new.username is not None or new.password is not None:
                return None, "malformed_location"
            old_port = old.port or (443 if old.scheme == "https" else 80)
            new_port = new.port or (443 if new.scheme == "https" else 80)
            if old.scheme == "https" and new.scheme == "http":
                return target, "https_downgrade"
            upgrade = (
                old.scheme == "http"
                and new.scheme == "https"
                and old_port == 80
                and new_port == 443
            )
            same = old.hostname == new.hostname and (old_port == new_port or upgrade)
            if not same and not (
                new.scheme == "https" and new_port == 443 and new.hostname in self.trusted_hosts
            ):
                return target, "untrusted_target"
            target = new._replace(fragment="").geturl()
            if target in visited:
                return target, "redirect_loop"
            return target, "follow"
        except ValueError:
            return None, "malformed_location"
