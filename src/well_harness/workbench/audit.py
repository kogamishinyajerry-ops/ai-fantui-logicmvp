from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


PROPOSAL_AUDIT_EVENT_TYPES = ("proposal.submitted", "proposal.accepted", "proposal.rejected")
PR_AUDIT_EVENT_TYPES = ("pr.submitted", "pr.accepted", "pr.rejected", "ticket.closed")
WORKBENCH_AUDIT_EVENT_TYPES = PROPOSAL_AUDIT_EVENT_TYPES + PR_AUDIT_EVENT_TYPES


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class AuditEventLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def _last_event_hash(self) -> str:
        if not self.path.exists():
            return ""
        lines = [line for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if not lines:
            return ""
        try:
            payload = json.loads(lines[-1])
        except json.JSONDecodeError:
            return hashlib.sha256(lines[-1].encode("utf-8")).hexdigest()
        if isinstance(payload, dict) and isinstance(payload.get("event_hash"), str):
            return payload["event_hash"]
        return hashlib.sha256(lines[-1].encode("utf-8")).hexdigest()

    def append(
        self,
        *,
        event_type: str,
        actor: str,
        proposal_id: str,
        payload: dict[str, Any] | None = None,
        observed_at: str | None = None,
    ) -> dict[str, Any]:
        if event_type not in WORKBENCH_AUDIT_EVENT_TYPES:
            raise ValueError(f"unsupported audit event type: {event_type}")
        event = {
            "id": f"evt_{uuid4().hex}",
            "type": event_type,
            "actor": actor,
            "proposal_id": proposal_id,
            "observed_at": observed_at or _utc_now(),
            "previous_hash": self._last_event_hash(),
            "payload": payload or {},
        }
        event["event_hash"] = _canonical_hash(event)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event
