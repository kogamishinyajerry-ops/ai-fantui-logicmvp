from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any
from uuid import uuid4


ANNOTATION_TOOLS = ("point", "area", "link", "text-range")
ANNOTATION_SURFACES = ("control", "document", "circuit")
PROPOSAL_STATUSES = ("pending", "accepted", "rejected")
_SAFE_PROPOSAL_ID = re.compile(r"^prop_[A-Za-z0-9_-]{3,96}$")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _proposal_id() -> str:
    return f"prop_{uuid4().hex}"


def _require_nonempty_string(payload: dict[str, Any], field: str) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _validate_proposal_id(proposal_id: str) -> None:
    if not isinstance(proposal_id, str) or not _SAFE_PROPOSAL_ID.fullmatch(proposal_id):
        raise ValueError("proposal id must be path-safe and start with 'prop_'")


def build_annotation_proposal(
    *,
    tool: str,
    surface: str,
    anchor: dict[str, Any],
    note: str,
    author: str,
    ticket_id: str,
    system_id: str,
    proposal_id: str | None = None,
    created_at: str | None = None,
    status: str = "pending",
    source: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observed_at = created_at or _utc_now()
    proposal = {
        "id": proposal_id or _proposal_id(),
        "tool": tool,
        "surface": surface,
        "anchor": copy.deepcopy(anchor),
        "note": note,
        "author": author,
        "ticket_id": ticket_id,
        "system_id": system_id,
        "status": status,
        "created_at": observed_at,
        "updated_at": observed_at,
        "source": copy.deepcopy(source or {}),
    }
    validate_annotation_proposal(proposal)
    return proposal


def validate_annotation_proposal(proposal: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(proposal, dict):
        raise ValueError("proposal must be a JSON object")

    for field in (
        "id",
        "tool",
        "surface",
        "anchor",
        "note",
        "author",
        "ticket_id",
        "system_id",
        "status",
        "created_at",
        "updated_at",
    ):
        if field not in proposal:
            raise ValueError(f"missing required field: {field}")

    _validate_proposal_id(proposal["id"])
    if proposal["tool"] not in ANNOTATION_TOOLS:
        raise ValueError(f"tool must be one of {', '.join(ANNOTATION_TOOLS)}")
    if proposal["surface"] not in ANNOTATION_SURFACES:
        raise ValueError(f"surface must be one of {', '.join(ANNOTATION_SURFACES)}")
    if proposal["status"] not in PROPOSAL_STATUSES:
        raise ValueError(f"status must be one of {', '.join(PROPOSAL_STATUSES)}")
    if not isinstance(proposal["anchor"], dict) or not proposal["anchor"]:
        raise ValueError("anchor must be a non-empty JSON object")

    for field in ("note", "author", "ticket_id", "system_id", "created_at", "updated_at"):
        _require_nonempty_string(proposal, field)

    if "source" in proposal and not isinstance(proposal["source"], dict):
        raise ValueError("source must be a JSON object when provided")

    return proposal


class ProposalStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _path_for(self, proposal_id: str) -> Path:
        _validate_proposal_id(proposal_id)
        return self.root / f"{proposal_id}.json"

    def save(self, proposal: dict[str, Any]) -> Path:
        validate_annotation_proposal(proposal)
        self.root.mkdir(parents=True, exist_ok=True)
        path = self._path_for(proposal["id"])
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(proposal, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(path)
        return path

    def load(self, proposal_id: str) -> dict[str, Any]:
        path = self._path_for(proposal_id)
        payload = json.loads(path.read_text(encoding="utf-8"))
        return validate_annotation_proposal(payload)

    def list_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        ids: list[str] = []
        for path in sorted(self.root.glob("*.json")):
            try:
                _validate_proposal_id(path.stem)
            except ValueError:
                continue
            ids.append(path.stem)
        return ids
