"""P49-02a — orchestrator integration with governance gate.

End-to-end: the orchestrator routes through GOVERNANCE_HOLD when
the planner produces a sensitive plan, waits for an approve/
reject signal, and ABORTs cleanly on cancel + timeout. Low-risk
plans skip the gate entirely.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.governance import GOVERNANCE_ENABLED_ENV
from well_harness.skill_executor.orchestrator import execute_proposal
from well_harness.skill_executor.states import ExecutionState


@pytest.fixture(autouse=True)
def _enable_governance(monkeypatch):
    """conftest disables the gate globally for the test suite;
    these tests explicitly opt back in to exercise the orchestrator
    integration."""
    monkeypatch.setenv(GOVERNANCE_ENABLED_ENV, "1")


# ─── Helpers ──────────────────────────────────────────────────────


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    """Minimal git-tracked repo with one source file + smoke test
    + a proposal + brief, ready for the orchestrator to chew on.

    Includes a `requirements`-namespace file (docs/...) so the
    'safe plan' test has a non-guarded namespace to edit without
    tripping the governance gate."""
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    # Requirements-namespace file for the safe-plan test path
    (tmp_path / "docs" / "thrust_reverser").mkdir(parents=True)
    (
        tmp_path / "docs" / "thrust_reverser"
        / "requirements_supplement.md"
    ).write_text("# requirements\n- old_value: 1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "def test_pass(): assert 1 + 1 == 2\n", encoding="utf-8",
    )
    proposal = {
        "id": "PROP-gov-test",
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "summary_zh": "x",
            "summary_en": "x",
        },
        "status": "ACCEPTED",
        "source_text": "x",
    }
    (tmp_path / "proposals").mkdir()
    (tmp_path / "proposals" / "PROP-gov-test.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-gov-test.md").write_text(
        "# brief\n", encoding="utf-8"
    )
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@x")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "initial")
    return tmp_path


@pytest.fixture(autouse=True)
def _isolate(mini_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(mini_repo / "queue"))
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


def _safe_plan_response_body() -> str:
    """Plan with no governance triggers — single yellow-risk
    namespace, no logic_truth, modify kind. Edits a requirements
    file so the namespace validator + governance gate both pass."""
    plan = {
        "rationale": "tighten",
        "affected_namespaces": ["requirements"],
        "risk_assessment": {"requirements": "yellow"},
        "file_edits": [
            {
                "path": "docs/thrust_reverser/requirements_supplement.md",
                "old_snippet": "old_value: 1",
                "new_snippet": "old_value: 2",
                "reason": "tighten",
            }
        ],
    }
    return json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )


def _gated_plan_response_body() -> str:
    """Plan that touches logic_truth — governance gate fires."""
    plan = {
        "rationale": "tighten",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "VAL = 1",
                "new_snippet": "VAL = 2",
                "reason": "tighten",
            }
        ],
    }
    return json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )


def _post_returns(body: str):
    def post(url, body_, headers, timeout):
        return body
    return post


# ─── 1. Low-risk plan skips the gate ───────────────────────────────


def test_safe_plan_skips_governance(mini_repo, tmp_path):
    """No governance triggers → execution sails through to PR_OPEN
    without ever entering GOVERNANCE_HOLD."""
    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_safe_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    assert result.error is None, result.error
    assert result.record.state == "PR_OPEN"
    # No governance state events
    event_kinds = [e.kind for e in result.record.events]
    assert "governance_required" not in event_kinds
    assert "governance_approved" not in event_kinds
    # No review payload set
    assert result.record.governance_review is None


# ─── 2. Sensitive plan goes through GOVERNANCE_HOLD on approve ─────


def test_gated_plan_advances_when_approved(mini_repo, tmp_path):
    """logic_truth-touching plan trips the gate; an injected
    poll_fn that returns 'approved' lets the orchestrator
    continue to ASKING (and on through to PR_OPEN)."""
    def fake_poll(*, audit_dir, exec_id):
        return ("approved", {
            "actor": "test-reviewer",
            "at": "2026-04-27T13:00:00Z",
            "note": "verified",
        })

    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        # Explicitly disable the auto-approve-governance default
        # (which mirrors auto_approve) so we exercise the real
        # poll-fn path.
        auto_approve_governance=False,
        request_post_for_llm=_post_returns(_gated_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        governance_poll_fn=fake_poll,
        governance_poll_interval_sec=0.0,
    )
    assert result.error is None, result.error
    assert result.record.state == "PR_OPEN"
    event_kinds = [e.kind for e in result.record.events]
    assert "governance_required" in event_kinds
    assert "governance_approved" in event_kinds
    # Review payload populated
    review = result.record.governance_review
    assert review is not None
    assert review["required"] is True
    assert review["decision"] == "approved"
    assert review["decided_by"] == "test-reviewer"


# ─── 3. Reject aborts cleanly ──────────────────────────────────────


def test_gated_plan_rejected_aborts(mini_repo, tmp_path):
    """Reviewer hits reject → ABORTED with a governance: prefix
    on abort_reason so the audit + dashboard distinguish it from
    user-rejected ASKING and other aborts."""
    def fake_poll(*, audit_dir, exec_id):
        return ("rejected", {
            "actor": "test-reviewer",
            "at": "2026-04-27T13:00:00Z",
            "note": "edits stray outside policy",
        })

    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        auto_approve_governance=False,  # exercise the gate path
        request_post_for_llm=_post_returns(_gated_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        governance_poll_fn=fake_poll,
        governance_poll_interval_sec=0.0,
    )
    assert result.record.state == ExecutionState.ABORTED.value
    assert result.record.abort_reason.startswith("governance:")
    assert "test-reviewer" in result.record.abort_reason
    event_kinds = [e.kind for e in result.record.events]
    assert "governance_required" in event_kinds
    assert "governance_rejected" in event_kinds
    review = result.record.governance_review
    assert review["decision"] == "rejected"


# ─── 4. Timeout aborts cleanly ─────────────────────────────────────


def test_gated_plan_times_out(mini_repo, tmp_path):
    """No signal arrives within timeout → ABORTED with governance
    timeout reason. Bias toward abort: silently advancing past a
    sensitive gate is unsafe."""
    def fake_poll(*, audit_dir, exec_id):
        return None  # always "no signal yet"

    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        auto_approve_governance=False,  # exercise the gate path
        request_post_for_llm=_post_returns(_gated_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        governance_poll_fn=fake_poll,
        governance_poll_interval_sec=0.0,
        # Very short timeout; the fake poll returns None on every
        # call, so we want this to wrap up quickly.
        governance_timeout_sec=0.05,
    )
    assert result.record.state == ExecutionState.ABORTED.value
    assert "governance" in result.record.abort_reason.lower()
    assert result.record.governance_review["decision"] == "timeout"


# ─── 5. auto_approve_governance bypasses signal ──────────────────


def test_auto_approve_governance_bypasses_signal(mini_repo, tmp_path):
    """Power-user flag for testing / scripted runs: the gate fires
    (audit records 'governance_required') but the signal step is
    skipped and execution continues. Must NOT erase the verdict
    from the audit — operator should still see what would have
    needed review."""
    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_gated_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        auto_approve_governance=True,
    )
    assert result.record.state == "PR_OPEN"
    review = result.record.governance_review
    assert review["required"] is True
    assert review["decision"] == "approved"
    assert "auto-approve" in review["decided_by"]


# ─── 6. Cancel during gate aborts ──────────────────────────────────


def test_cancel_during_governance_aborts(mini_repo, tmp_path):
    """A cancel signal that arrives during GOVERNANCE_HOLD must
    win over any pending approval — operator pressing the
    workbench Cancel button should stop everything."""
    from well_harness.skill_executor.workbench_polling import (
        write_cancel_signal,
    )

    audit_root = tmp_path / "execs"

    # First poll: no signal. Second poll: write a cancel signal,
    # then return None (the cancel check at the top of the loop
    # will pick it up before the next poll_fn call). We use a
    # closure to mutate the cancel state from inside fake_poll.
    state = {"polls": 0}

    def fake_poll(*, audit_dir, exec_id):
        state["polls"] += 1
        if state["polls"] == 1:
            # On the second loop iteration, the orchestrator will
            # see this cancel signal first.
            write_cancel_signal(
                audit_dir=audit_dir, exec_id=exec_id,
                actor="test-cancel", note="pressing cancel",
            )
        return None

    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=audit_root,
        auto_approve=True,
        auto_approve_governance=False,  # exercise the gate path
        request_post_for_llm=_post_returns(_gated_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        governance_poll_fn=fake_poll,
        governance_poll_interval_sec=0.0,
        governance_timeout_sec=5.0,
    )
    assert result.record.state == ExecutionState.ABORTED.value
    # Cancel path: abort_reason set by _abort_with_cancel, NOT
    # the governance-rejected branch
    assert "test-cancel" in result.record.abort_reason


# ─── 7. Real signal-file path also works ──────────────────────────


def test_real_signal_file_advances_governance(mini_repo, tmp_path):
    """End-to-end via the actual file IPC: write a
    .governance_approval marker before the orchestrator polls.
    The default poll_fn (read_and_clear_governance) should pick
    it up and approve."""
    from well_harness.skill_executor.workbench_polling import (
        write_governance_approval,
    )

    audit_root = tmp_path / "execs"
    audit_root.mkdir(parents=True, exist_ok=True)

    # We don't know the exec_id ahead of time. The orchestrator
    # generates it; we pre-write the signal under an exec_id we
    # synthesize via a sleep_fn that, on its first call, finds
    # the audit file and writes the signal.
    state = {"signal_written": False}

    def sleep_fn(seconds):
        if state["signal_written"]:
            return
        # Find the audit file and write a governance-approval
        # signal next to it
        audits = sorted(audit_root.glob("EXEC-*.json"))
        for audit_path in audits:
            exec_id = audit_path.stem
            # Only write once per run
            write_governance_approval(
                audit_dir=audit_root, exec_id=exec_id,
                actor="real-flow-test",
                note="signal via file",
            )
            state["signal_written"] = True
            break

    result = execute_proposal(
        proposal_id="PROP-gov-test",
        repo_root=mini_repo,
        audit_dir=audit_root,
        auto_approve=True,
        auto_approve_governance=False,  # exercise the gate path
        request_post_for_llm=_post_returns(_gated_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=sleep_fn,
        governance_poll_interval_sec=0.0,
        governance_timeout_sec=5.0,
    )
    assert result.record.state == "PR_OPEN"
    review = result.record.governance_review
    assert review["decision"] == "approved"
    assert review["decided_by"] == "real-flow-test"
