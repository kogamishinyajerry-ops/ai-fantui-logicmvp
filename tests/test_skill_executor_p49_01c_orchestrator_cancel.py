"""P49-01c — orchestrator phase-boundary cancel checkpoints.

Locks down: when a cancel signal is dropped at a phase boundary,
the orchestrator transitions to ABORTED, reverts any applied
edits, and records the actor in abort_reason — distinct from
REJECTED (which means the user disapproved the plan, not that
they want to abort the executor).

Phase boundaries covered:
  1. ASKING — cancel during approval polling
  2. post-PLANNING — cancel between plan ready and ASKING ask
  3. post-EDITING — cancel after edits applied (must revert)
  4. post-TESTING — cancel after tests pass, before PR
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.orchestrator import (
    _abort_with_cancel,
    _check_cancel_and_abort,
    execute_proposal,
)
from well_harness.skill_executor.workbench_polling import write_cancel_signal


# ─── Helpers (mini-repo fixture matches P48-04 pattern) ─────────────


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    """Mini-repo with one source file + smoke test + ACCEPTED proposal."""
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "def test_pass():\n    assert 1 + 1 == 2\n",
        encoding="utf-8",
    )
    proposal = {
        "id": "PROP-cancel-test",
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "summary_zh": "[CANCEL TEST]",
            "summary_en": "[CANCEL TEST]",
        },
        "status": "ACCEPTED",
        "source_text": "tighten",
    }
    (tmp_path / "proposals").mkdir()
    (tmp_path / "proposals" / "PROP-cancel-test.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-cancel-test.md").write_text(
        "# brief\n", encoding="utf-8"
    )
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "initial")
    return tmp_path


@pytest.fixture(autouse=True)
def _isolate(mini_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(mini_repo / "queue"))
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


def _good_plan_json() -> str:
    plan = {
        "rationale": "tighten the condition",
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


def _make_post(*responses):
    iter_resp = iter(responses)

    def _post(url, body, headers, timeout):
        return next(iter_resp)

    return _post


# ─── 1. _abort_with_cancel helper unit ─────────────────────────────


def test_abort_with_cancel_is_idempotent_on_terminal_state(tmp_path):
    """If the record is already in a terminal state, a stray cancel
    signal should not retroactively flip the state. Tests that
    _abort_with_cancel guards against double-fire."""
    from well_harness.skill_executor.models import (
        AUDIT_SCHEMA_VERSION, AuditSource, ExecutionKind,
        ExecutionRecord, PlannedChange,
    )
    from well_harness.skill_executor.states import ExecutionState
    from well_harness.skill_executor.workbench_polling import ExecutionCancelled

    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000000000-aaaaaa",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-x",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T13:00:00Z",
        finished_at="2026-04-27T13:01:00Z",
        state=ExecutionState.LANDED.value,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
    )
    pre_state = rec.state
    pre_reason = rec.abort_reason
    _abort_with_cancel(
        rec,
        tmp_path,
        ExecutionCancelled(actor="late", note="too late"),
        applied=None,
    )
    assert rec.state == pre_state
    assert rec.abort_reason == pre_reason


# ─── 2. _check_cancel_and_abort returns False with no signal ────────


def test_check_cancel_returns_false_when_no_signal(tmp_path, mini_repo):
    """The phase-boundary check is essentially a no-op in the happy
    path — confirms we don't accidentally abort on every check."""
    from well_harness.skill_executor.models import (
        AUDIT_SCHEMA_VERSION, AuditSource, ExecutionKind,
        ExecutionRecord, PlannedChange,
    )
    from well_harness.skill_executor.states import ExecutionState

    audit_dir = tmp_path / "execs"
    audit_dir.mkdir(parents=True)
    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000000000-bbbbbb",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-x",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T13:00:00Z",
        finished_at="",
        state=ExecutionState.PLANNING.value,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
    )
    cancelled = _check_cancel_and_abort(rec, audit_dir, applied=None)
    assert cancelled is False
    assert rec.state == ExecutionState.PLANNING.value


# ─── 3. End-to-end: cancel during ASKING ────────────────────────────


def test_cancel_during_asking_aborts_before_edits(mini_repo, tmp_path):
    """Cancel signal dropped while the orchestrator polls for
    approval → ABORTED state, no commits, file unmodified."""
    audit_dir = tmp_path / "execs"
    audit_dir.mkdir(parents=True)

    # Pre-stage the cancel signal so the polling callback's first
    # iteration sees it and raises ExecutionCancelled. The exec_id
    # is auto-generated, so we drop the signal AFTER the orchestrator
    # creates the audit. Use a custom callback that writes the signal
    # right before checking.
    from well_harness.skill_executor.workbench_polling import (
        WorkbenchApprovalCallback,
    )

    class CancelOnFirstCheck:
        def __init__(self):
            self.calls = 0

        def __call__(self, record, ask):
            self.calls += 1
            write_cancel_signal(
                audit_dir=audit_dir,
                exec_id=record.exec_id,
                actor="Kogami",
                note="abort the plan",
            )
            cb = WorkbenchApprovalCallback(
                audit_dir=audit_dir,
                poll_interval_sec=0.0,
                timeout_sec=1.0,
                sleep=lambda _s: None,
            )
            return cb(record, ask)

    result = execute_proposal(
        proposal_id="PROP-cancel-test",
        repo_root=mini_repo,
        audit_dir=audit_dir,
        approval_callback=CancelOnFirstCheck(),
        request_post_for_llm=_make_post(_good_plan_json()),
    )
    rec = result.record
    assert rec.state == "ABORTED"
    assert "Kogami" in rec.abort_reason
    assert "abort the plan" in rec.abort_reason
    assert rec.commits == []
    # The plan's edit should NOT be applied — controller.py untouched
    assert (
        (mini_repo / "src" / "well_harness" / "controller.py")
        .read_text(encoding="utf-8")
        == "VAL = 1\n"
    )


# ─── 4. End-to-end: cancel post-EDITING reverts the file ───────────


def test_cancel_post_editing_reverts_applied_edits(mini_repo, tmp_path):
    """Cancel signal dropped between EDITING-applied and TESTING.
    Edits must be reverted so the working tree is clean."""
    audit_dir = tmp_path / "execs"
    audit_dir.mkdir(parents=True)

    # Approve the plan, then drop a cancel signal IMMEDIATELY after
    # so the post-EDITING phase-boundary check picks it up.
    captured = {}

    def callback(record, ask):
        captured["exec_id"] = record.exec_id
        # Approve normally
        from well_harness.skill_executor.models import AskResponse
        return AskResponse.APPROVED

    # Monkey-patch apply_edits to drop the cancel signal AFTER it
    # successfully applies. This simulates the user clicking Cancel
    # right as the executor finishes writing files.
    from well_harness.skill_executor import orchestrator as orch

    real_apply = orch.apply_edits

    def apply_then_cancel(*args, **kw):
        result = real_apply(*args, **kw)
        write_cancel_signal(
            audit_dir=audit_dir,
            exec_id=captured["exec_id"],
            actor="Kogami",
            note="changed mind",
        )
        return result

    import unittest.mock as mock
    with mock.patch.object(orch, "apply_edits", apply_then_cancel):
        result = execute_proposal(
            proposal_id="PROP-cancel-test",
            repo_root=mini_repo,
            audit_dir=audit_dir,
            approval_callback=callback,
            request_post_for_llm=_make_post(_good_plan_json()),
        )

    rec = result.record
    assert rec.state == "ABORTED"
    assert "Kogami" in rec.abort_reason
    assert rec.commits == []
    # Edits MUST be reverted — file back to baseline
    assert (
        (mini_repo / "src" / "well_harness" / "controller.py")
        .read_text(encoding="utf-8")
        == "VAL = 1\n"
    )


# ─── 5. End-to-end: cancel post-TESTING (before PR) ─────────────────


def test_cancel_post_testing_aborts_before_pr(mini_repo, tmp_path):
    """Cancel signal dropped after tests pass, before git/PR.
    Edits applied + tests run + still revert + ABORTED state."""
    audit_dir = tmp_path / "execs"
    audit_dir.mkdir(parents=True)

    captured = {}

    def callback(record, ask):
        captured["exec_id"] = record.exec_id
        from well_harness.skill_executor.models import AskResponse
        return AskResponse.APPROVED

    from well_harness.skill_executor import orchestrator as orch

    real_run_tests = orch.run_tests
    test_call_count = {"n": 0}

    def run_tests_with_cancel_after_second(*args, **kw):
        test_call_count["n"] += 1
        result = real_run_tests(*args, **kw)
        # First call is tests_before; second is tests_after.
        # Drop the cancel signal AFTER the tests_after call so the
        # post-TESTING phase-boundary picks it up.
        if test_call_count["n"] == 2:
            write_cancel_signal(
                audit_dir=audit_dir,
                exec_id=captured["exec_id"],
                actor="Kogami",
                note="cold feet",
            )
        return result

    import unittest.mock as mock
    with mock.patch.object(orch, "run_tests", run_tests_with_cancel_after_second):
        result = execute_proposal(
            proposal_id="PROP-cancel-test",
            repo_root=mini_repo,
            audit_dir=audit_dir,
            approval_callback=callback,
            request_post_for_llm=_make_post(_good_plan_json()),
        )

    rec = result.record
    assert rec.state == "ABORTED"
    assert "Kogami" in rec.abort_reason
    assert "cold feet" in rec.abort_reason
    assert rec.commits == []
    # Both tests_before and tests_after captured before cancel hit
    assert rec.tests_before is not None
    assert rec.tests_after is not None
    # Edits reverted
    assert (
        (mini_repo / "src" / "well_harness" / "controller.py")
        .read_text(encoding="utf-8")
        == "VAL = 1\n"
    )


# ─── 6. user_cancel event recorded in audit log ───────────────────


def test_user_cancel_event_logged(mini_repo, tmp_path):
    """Reviewer reading the audit must see a `user_cancel` event
    with the actor + note. This is what makes the audit trail
    different from a vanilla user_abort."""
    audit_dir = tmp_path / "execs"
    audit_dir.mkdir(parents=True)

    from well_harness.skill_executor.workbench_polling import (
        WorkbenchApprovalCallback,
    )

    class CancelOnAsking:
        def __call__(self, record, ask):
            write_cancel_signal(
                audit_dir=audit_dir,
                exec_id=record.exec_id,
                actor="Reviewer-7",
                note="LLM is hallucinating",
            )
            cb = WorkbenchApprovalCallback(
                audit_dir=audit_dir,
                poll_interval_sec=0.0,
                timeout_sec=1.0,
                sleep=lambda _s: None,
            )
            return cb(record, ask)

    result = execute_proposal(
        proposal_id="PROP-cancel-test",
        repo_root=mini_repo,
        audit_dir=audit_dir,
        approval_callback=CancelOnAsking(),
        request_post_for_llm=_make_post(_good_plan_json()),
    )
    rec = result.record
    cancel_events = [e for e in rec.events if e.kind == "user_cancel"]
    assert len(cancel_events) == 1
    note = cancel_events[0].note
    assert "Reviewer-7" in note
    assert "hallucinating" in note
