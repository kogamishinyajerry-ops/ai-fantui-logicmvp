from __future__ import annotations

import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .audit import AuditEventLog
from .proposals import ProposalStore, validate_annotation_proposal


class WorkbenchPermissionError(PermissionError):
    """Raised when a Workbench approval action is not authorized."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _require_kogami(actor: str) -> None:
    if actor.strip().lower() != "kogami":
        raise WorkbenchPermissionError("Kogami approval authority is required for proposal triage")


class ApprovalCenter:
    def __init__(self, *, proposal_root: str | Path, audit_path: str | Path):
        self.store = ProposalStore(proposal_root)
        self.audit = AuditEventLog(audit_path)

    def submit(self, proposal: dict[str, Any], *, actor: str) -> dict[str, Any]:
        payload = copy.deepcopy(proposal)
        payload["status"] = "pending"
        payload["updated_at"] = _utc_now()
        validate_annotation_proposal(payload)
        path = self.store.save(payload)
        event = self.audit.append(
            event_type="proposal.submitted",
            actor=actor,
            proposal_id=payload["id"],
            payload={"path": str(path), "tool": payload["tool"], "surface": payload["surface"]},
        )
        return {"status": payload["status"], "proposal_id": payload["id"], "audit_event_hash": event["event_hash"]}

    def pending(self) -> list[dict[str, Any]]:
        proposals = [self.store.load(proposal_id) for proposal_id in self.store.list_ids()]
        return [proposal for proposal in proposals if proposal.get("status") == "pending"]

    def accept(self, proposal_id: str, *, actor: str, reason: str = "") -> dict[str, Any]:
        return self._triage(proposal_id, actor=actor, status="accepted", reason=reason)

    def reject(self, proposal_id: str, *, actor: str, reason: str = "") -> dict[str, Any]:
        return self._triage(proposal_id, actor=actor, status="rejected", reason=reason)

    def _triage(self, proposal_id: str, *, actor: str, status: str, reason: str) -> dict[str, Any]:
        _require_kogami(actor)
        proposal = self.store.load(proposal_id)
        proposal["status"] = status
        proposal["updated_at"] = _utc_now()
        validate_annotation_proposal(proposal)
        self.store.save(proposal)
        event_type = f"proposal.{status}"
        event = self.audit.append(
            event_type=event_type,
            actor=actor,
            proposal_id=proposal_id,
            payload={"reason": reason, "ticket_id": proposal["ticket_id"], "system_id": proposal["system_id"]},
        )
        return {"status": status, "proposal_id": proposal_id, "audit_event_hash": event["event_hash"]}
