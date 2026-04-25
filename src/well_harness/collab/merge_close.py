from __future__ import annotations

from pathlib import Path
from typing import Any

from well_harness.workbench.audit import AuditEventLog


def build_merge_close_plan(ticket: dict[str, Any], verdict_report: dict[str, Any], *, actor: str) -> dict[str, Any]:
    accepted = verdict_report.get("verdict") == "accepted"
    actions = ["record_pr_acceptance", "record_ticket_close"] if accepted else ["record_pr_rejection"]
    return {
        "mode": "stub",
        "actor": actor,
        "ticket_id": ticket.get("Task", ""),
        "source_proposal": ticket.get("Source Proposal", ""),
        "pr_url": ticket.get("PR URL", verdict_report.get("pr_url", "")),
        "verdict": verdict_report.get("verdict", "rejected"),
        "actions": actions,
        "live_merge_performed": False,
    }


def close_ticket_with_verdict(
    ticket: dict[str, Any],
    verdict_report: dict[str, Any],
    *,
    audit_path: str | Path,
    actor: str,
) -> dict[str, Any]:
    audit = AuditEventLog(audit_path)
    accepted = verdict_report.get("verdict") == "accepted"
    pr_event_type = "pr.accepted" if accepted else "pr.rejected"
    pr_event = audit.append(
        event_type=pr_event_type,
        actor=actor,
        proposal_id=str(ticket.get("Source Proposal", "")),
        payload={
            "ticket_id": ticket.get("Task", ""),
            "pr_url": ticket.get("PR URL", verdict_report.get("pr_url", "")),
            "changed_files": verdict_report.get("changed_files", []),
            "findings": verdict_report.get("findings", []),
        },
    )
    closed = False
    close_event = None
    if accepted:
        close_event = audit.append(
            event_type="ticket.closed",
            actor=actor,
            proposal_id=str(ticket.get("Source Proposal", "")),
            payload={"ticket_id": ticket.get("Task", ""), "pr_event_hash": pr_event["event_hash"]},
        )
        closed = True
    return {
        "closed": closed,
        "mode": "stub",
        "pr_event_hash": pr_event["event_hash"],
        "ticket_close_event_hash": close_event["event_hash"] if close_event else "",
        "live_merge_performed": False,
    }
