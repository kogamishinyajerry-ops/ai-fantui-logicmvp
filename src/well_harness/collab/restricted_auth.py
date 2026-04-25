from __future__ import annotations

from fnmatch import fnmatch
from typing import Any


class RestrictedAuthError(PermissionError):
    """Raised when a ticket-scoped push attempt is not authorized."""


def _normalize(path: str) -> str:
    return path.strip().lstrip("./")


def _matches_scope(path: str, pattern: str) -> bool:
    normalized_path = _normalize(path)
    normalized_pattern = _normalize(pattern)
    if not normalized_pattern:
        return False
    if normalized_path == normalized_pattern:
        return True
    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern[:-3]
        return normalized_path.startswith(prefix)
    if normalized_pattern.endswith("/"):
        return normalized_path.startswith(normalized_pattern)
    return fnmatch(normalized_path, normalized_pattern)


def validate_push_attempt(ticket: dict[str, Any], *, engineer: str, changed_files: list[str]) -> dict[str, Any]:
    authorized = str(ticket.get("Authorized Engineer") or "").strip()
    if engineer.strip() != authorized:
        raise RestrictedAuthError("Authorized Engineer does not match this ticket")
    scope_files = ticket.get("Scope Files")
    if not isinstance(scope_files, list) or not scope_files:
        raise RestrictedAuthError("Scope Files are required for restricted auth")
    if not changed_files:
        raise RestrictedAuthError("changed_files must not be empty")

    outside_scope = [
        path
        for path in changed_files
        if not any(_matches_scope(path, str(pattern)) for pattern in scope_files)
    ]
    if outside_scope:
        raise RestrictedAuthError(f"Changed files outside Scope Files: {outside_scope}")

    return {
        "allowed": True,
        "authorized_engineer": authorized,
        "changed_files": [_normalize(path) for path in changed_files],
        "scope_files": scope_files,
    }
