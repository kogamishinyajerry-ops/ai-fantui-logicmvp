import json
from pathlib import Path

import pytest

from well_harness.workbench.approval import ApprovalCenter, WorkbenchPermissionError
from well_harness.workbench.proposals import build_annotation_proposal


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _proposal() -> dict:
    return build_annotation_proposal(
        proposal_id="prop_approval_001",
        tool="point",
        surface="control",
        anchor={"x": 0.2, "y": 0.4},
        note="Approve review of the control state handoff.",
        author="engineer-a",
        ticket_id="WB-E08-APPROVAL",
        system_id="thrust-reverser",
        created_at="2026-04-25T09:00:00Z",
    )


def _read_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_approval_center_submits_proposal_and_appends_audit_event(tmp_path):
    audit_path = tmp_path / "audit/events.jsonl"
    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=audit_path)

    result = center.submit(_proposal(), actor="engineer-a")

    assert result["status"] == "pending"
    assert result["proposal_id"] == "prop_approval_001"
    assert center.pending()[0]["id"] == "prop_approval_001"
    events = _read_events(audit_path)
    assert events[-1]["type"] == "proposal.submitted"
    assert events[-1]["proposal_id"] == "prop_approval_001"
    assert events[-1]["event_hash"]


def test_approval_center_rejects_non_kogami_triage(tmp_path):
    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=tmp_path / "audit/events.jsonl")
    center.submit(_proposal(), actor="engineer-a")

    with pytest.raises(WorkbenchPermissionError, match="Kogami"):
        center.accept("prop_approval_001", actor="engineer-a")


def test_approval_center_accepts_and_rejects_with_hash_chain(tmp_path):
    audit_path = tmp_path / "audit/events.jsonl"
    center = ApprovalCenter(proposal_root=tmp_path / "proposals", audit_path=audit_path)
    center.submit(_proposal(), actor="engineer-a")

    accepted = center.accept("prop_approval_001", actor="Kogami", reason="Scope is correct.")
    events = _read_events(audit_path)

    assert accepted["status"] == "accepted"
    assert events[-1]["type"] == "proposal.accepted"
    assert events[-1]["previous_hash"] == events[-2]["event_hash"]

    second = build_annotation_proposal(
        proposal_id="prop_approval_002",
        tool="text-range",
        surface="document",
        anchor={"selector": "#workbench-document-panel", "start_offset": 0, "end_offset": 12, "text_quote": "Reference"},
        note="Reject this duplicate document note.",
        author="engineer-a",
        ticket_id="WB-E08-APPROVAL",
        system_id="thrust-reverser",
        created_at="2026-04-25T09:01:00Z",
    )
    center.submit(second, actor="engineer-a")
    rejected = center.reject("prop_approval_002", actor="Kogami", reason="Duplicate.")

    assert rejected["status"] == "rejected"
    assert _read_events(audit_path)[-1]["type"] == "proposal.rejected"


def test_workbench_static_approval_center_exposes_triage_lanes():
    html = (PROJECT_ROOT / "src/well_harness/static/workbench.html").read_text(encoding="utf-8")

    assert 'id="approval-center-panel"' in html
    assert 'data-approval-role="KOGAMI"' in html
    for lane in ["pending", "accept", "reject"]:
        assert f'data-approval-lane="{lane}"' in html
