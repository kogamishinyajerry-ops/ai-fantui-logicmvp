"""P49-04 — dry-run pipeline tests.

Locks down: dry_run=True takes the orchestrator through
PLANNING/EDITING/TESTING, captures the file diff, reverts the
working tree, and ends at DRY_RUN_COMPLETE without any commit/
push/PR. dry_run=False keeps the legacy path intact. State
machine new transition is allowed.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.errors import InvalidExecutionTransitionError
from well_harness.skill_executor.orchestrator import execute_proposal
from well_harness.skill_executor.states import (
    ALLOWED_TRANSITIONS,
    ExecutionState,
    is_terminal,
    next_state,
)


# ─── Helpers ──────────────────────────────────────────────────────


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    """Same shape the P50-03 retry tests use — minimal git repo
    with one source file + smoke test + a proposal + brief."""
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "def test_pass(): assert 1 + 1 == 2\n", encoding="utf-8",
    )
    proposal = {
        "id": "PROP-dryrun-test",
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
    (tmp_path / "proposals" / "PROP-dryrun-test.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-dryrun-test.md").write_text(
        "# brief\n", encoding="utf-8",
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


def _plan_response_body() -> str:
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


# ─── 1. State machine: new transition allowed ────────────────────


def test_testing_to_dry_run_complete_allowed():
    assert next_state(
        ExecutionState.TESTING, "dry_run_complete",
    ) == ExecutionState.DRY_RUN_COMPLETE


def test_dry_run_complete_is_terminal():
    """Pipeline ends here — no further transitions out."""
    assert is_terminal(ExecutionState.DRY_RUN_COMPLETE) is True
    # No outgoing edges in the table
    outgoing = [
        e for (s, e) in ALLOWED_TRANSITIONS
        if s == ExecutionState.DRY_RUN_COMPLETE
    ]
    assert outgoing == []


def test_dry_run_complete_value_lockdown():
    """Wire string lockdown — audit JSONs serialize ExecutionState
    by .value; old audits won't drift."""
    assert ExecutionState.DRY_RUN_COMPLETE.value == "DRY_RUN_COMPLETE"


def test_state_machine_does_not_break_existing_transitions():
    """tests_pass → PR_OPEN still works. Adding the new edge
    didn't replace it."""
    assert next_state(
        ExecutionState.TESTING, "tests_pass",
    ) == ExecutionState.PR_OPEN


# ─── 2. Dry-run pipeline end-to-end ───────────────────────────────


def test_dry_run_terminates_before_pr(mini_repo, tmp_path):
    """dry_run=True takes the pipeline through EDITING + TESTING,
    captures the diff, reverts, terminates DRY_RUN_COMPLETE.
    NO PR_OPEN, NO commits."""
    result = execute_proposal(
        proposal_id="PROP-dryrun-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
    )
    assert result.error is None, result.error
    assert result.record.state == "DRY_RUN_COMPLETE"
    assert result.record.dry_run is True
    # The diff was captured
    assert result.record.dry_run_diff != ""
    assert "VAL = 1" in result.record.dry_run_diff
    assert "VAL = 2" in result.record.dry_run_diff
    # Working tree was reverted — controller.py back to original
    assert (mini_repo / "src" / "well_harness" / "controller.py").read_text() == "VAL = 1\n"
    # No commits beyond the initial one
    log = _git(mini_repo, "log", "--oneline").stdout.strip().splitlines()
    assert len(log) == 1


def test_dry_run_audit_event_logged(mini_repo, tmp_path):
    """The audit log includes a `dry_run_complete` event so a
    consumer can spot dry-runs without parsing the state value."""
    result = execute_proposal(
        proposal_id="PROP-dryrun-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
    )
    event_kinds = [e.kind for e in result.record.events]
    assert "dry_run_complete" in event_kinds
    # The init event also got tagged so pipeline observers see
    # dry-run nature even before it terminates
    init_event = next(e for e in result.record.events if e.kind == "init")
    assert "DRY-RUN" in init_event.note


def test_dry_run_false_takes_normal_path(mini_repo, tmp_path):
    """dry_run=False (default) still goes through the legacy
    commit + PR path — adding the param didn't break the
    happy-path."""
    result = execute_proposal(
        proposal_id="PROP-dryrun-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        # dry_run not passed → defaults to False
    )
    assert result.record.state == "PR_OPEN"
    assert result.record.dry_run is False
    assert result.record.dry_run_diff == ""


# ─── 3. Dry-run honors the test gate ──────────────────────────────


def test_dry_run_aborts_when_tests_regress(mini_repo, tmp_path):
    """Even in dry-run mode, the test gate is authoritative.
    Failing tests → ABORTED, not DRY_RUN_COMPLETE — we don't
    pretend a broken plan would have shipped."""
    # Make the smoke test depend on controller.py contents — read
    # the file as text so we don't fight pytest's import machinery
    # in the temp repo. Then break it via an edit the planner is
    # allowed to make (logic_truth path → controller.py).
    (mini_repo / "tests" / "test_smoke.py").write_text(
        "from pathlib import Path\n"
        "def test_val_is_one():\n"
        "    text = (Path(__file__).parent.parent / 'src' / 'well_harness' / 'controller.py').read_text()\n"
        "    assert 'VAL = 1' in text\n",
        encoding="utf-8",
    )
    _git(mini_repo, "add", "tests/test_smoke.py")
    _git(mini_repo, "commit", "-q", "-m", "tighten smoke")
    plan = {
        "rationale": "break",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "VAL = 1",
                "new_snippet": "VAL = 99",
                "reason": "break",
            }
        ],
    }
    body = json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )
    result = execute_proposal(
        proposal_id="PROP-dryrun-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(body),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
    )
    # Abort — not DRY_RUN_COMPLETE. dry_run flag stays True so
    # the audit still records what was attempted.
    assert result.record.state == "ABORTED"
    assert result.record.dry_run is True
    # No diff captured — we aborted before the dry-run terminator
    assert result.record.dry_run_diff == ""
    # Working tree reverted (existing tests_regress path
    # already does revert_edits)
    assert (mini_repo / "src" / "well_harness" / "controller.py").read_text() == "VAL = 1\n"


# ─── 4. Diff capture failure is non-fatal ─────────────────────────


def test_dry_run_diff_capture_failure_does_not_abort(mini_repo, tmp_path):
    """If git diff somehow fails (rare), the dry-run still
    terminates DRY_RUN_COMPLETE — empty diff is the fallback,
    not a hard failure. The audit logs a dry_run_diff_error
    event so a consumer can spot the gap."""
    # Inject a git_runner that raises on `git diff`
    def exploding_runner(cmd, **kwargs):
        if cmd[:2] == ["git", "diff"]:
            raise OSError("simulated git diff failure")
        # delegate to the default for all other commands
        from well_harness.skill_executor.git_ops import _default_runner
        return _default_runner(cmd, **kwargs)

    result = execute_proposal(
        proposal_id="PROP-dryrun-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
        git_runner=exploding_runner,
    )
    # Still terminates dry-run
    assert result.record.state == "DRY_RUN_COMPLETE"
    assert result.record.dry_run_diff == ""
    # Audit captured the failure
    event_kinds = [e.kind for e in result.record.events]
    assert "dry_run_diff_error" in event_kinds


# ─── 5. JSON round-trip ──────────────────────────────────────────


def test_audit_json_round_trips_dry_run_fields(mini_repo, tmp_path):
    """ExecutionRecord.from_json/to_json preserve dry_run +
    dry_run_diff so a reload doesn't lose the preview."""
    from well_harness.skill_executor.audit import read_audit
    result = execute_proposal(
        proposal_id="PROP-dryrun-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
        dry_run=True,
    )
    # Read back from disk
    reloaded = read_audit(result.record.exec_id)
    assert reloaded.dry_run is True
    assert reloaded.dry_run_diff == result.record.dry_run_diff
    # JSON shape stable
    j = reloaded.to_json()
    assert "dry_run" in j
    assert "dry_run_diff" in j
    assert j["dry_run"] is True
