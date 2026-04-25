import json
from pathlib import Path

from well_harness.collab.merge_close import build_merge_close_plan, close_ticket_with_verdict
from well_harness.workbench.pr_review import extract_changed_files, review_pr_diff


def _ticket() -> dict:
    return {
        "Task": "WB-E10-REVIEW",
        "Type": "Workbench Annotation",
        "Source Proposal": "prop_review_001",
        "Authorized Engineer": "claude-code",
        "Scope Files": ["src/well_harness/workbench/**", "docs/workbench/**"],
        "Generated Prompt": "## anchor\nproposal\n\n## scope\nsrc/well_harness/workbench/**",
        "PR URL": "https://github.com/example/repo/pull/10",
        "Verdict": "Pending",
    }


def _diff_for(path: str) -> str:
    return f"""diff --git a/{path} b/{path}
index 1111111..2222222 100644
--- a/{path}
+++ b/{path}
@@ -1,1 +1,1 @@
-old
+new
"""


def _read_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_extract_changed_files_from_unified_diff():
    assert extract_changed_files(_diff_for("src/well_harness/workbench/pr_review.py")) == [
        "src/well_harness/workbench/pr_review.py"
    ]


def test_pr_review_accepts_in_scope_diff():
    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/workbench/pr_review.py"))

    assert report["verdict"] == "accepted"
    assert report["changed_files"] == ["src/well_harness/workbench/pr_review.py"]
    assert report["findings"] == []


def test_pr_review_rejects_out_of_scope_diff():
    report = review_pr_diff(_ticket(), _diff_for("src/well_harness/controller.py"))

    assert report["verdict"] == "rejected"
    assert "Scope Files" in report["findings"][0]["message"]


def test_merge_close_stub_appends_pr_and_ticket_events(tmp_path):
    ticket = _ticket()
    report = review_pr_diff(ticket, _diff_for("src/well_harness/workbench/pr_review.py"))
    plan = build_merge_close_plan(ticket, report, actor="Kogami")
    close_result = close_ticket_with_verdict(ticket, report, audit_path=tmp_path / "audit/events.jsonl", actor="Kogami")
    events = _read_events(tmp_path / "audit/events.jsonl")

    assert plan["mode"] == "stub"
    assert plan["actions"] == ["record_pr_acceptance", "record_ticket_close"]
    assert close_result["closed"] is True
    assert [event["type"] for event in events] == ["pr.accepted", "ticket.closed"]
    assert events[1]["previous_hash"] == events[0]["event_hash"]
