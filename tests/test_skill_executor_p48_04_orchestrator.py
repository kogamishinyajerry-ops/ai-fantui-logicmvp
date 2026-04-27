"""P48-04 — orchestrator: full pipeline end-to-end.

The orchestrator is the integration of P48-01..03 + git_ops +
pr_maker. Tests build a self-contained mini-repo (real git init,
real pytest run, file:// remote) + mocked LLM + mocked gh.

Each test exercises ONE happy or failure path through the state
machine; together they cover every transition the orchestrator
can produce.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.audit import read_audit
from well_harness.skill_executor.models import AskResponse
from well_harness.skill_executor.orchestrator import (
    OrchestratorError,
    execute_proposal,
)
from well_harness.skill_executor.states import ExecutionState


# ─── Mini-repo fixture with everything the pipeline needs ─────────────


def _git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=check, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    """A tmp_path mini-repo:
      - src/pkg/controller.py, models.py (truth-engine namespace files
        per PANEL_NAMESPACES) — but we declare them under
        `logic_truth` namespace mapping below
      - tests/test_pass.py (passes)
      - .planning/proposals/PROP-test.json
      - .planning/dev_queue/PROP-test.md
      - git init + initial commit + file:// origin
    """
    # The orchestrator's namespace cross-check uses the canonical
    # PANEL_NAMESPACES which references real source paths. So we
    # mirror those paths under tmp_path. The test imports
    # controller.py via DIRECT FILE LOAD so the real well_harness
    # in the parent process's sys.path doesn't shadow the mini-repo's.
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    controller = tmp_path / "src" / "well_harness" / "controller.py"
    controller.write_text(
        "def step():\n"
        "    if condition:\n"
        "        return 1\n",
        encoding="utf-8",
    )
    # tests/ — load the controller.py from THIS repo's tree by
    # path, not by `import well_harness.controller`, so the real
    # project's well_harness package can't shadow it.
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "import os\n"
        "import importlib.util\n"
        "HERE = os.path.dirname(__file__)\n"
        "CTRL_PATH = os.path.join(HERE, '..', 'src', 'well_harness', 'controller.py')\n"
        "def _load():\n"
        "    spec = importlib.util.spec_from_file_location('mini_ctrl', CTRL_PATH)\n"
        "    mod = importlib.util.module_from_spec(spec)\n"
        "    spec.loader.exec_module(mod)\n"
        "    return mod\n"
        "def test_module_loads_step():\n"
        "    mod = _load()\n"
        "    assert hasattr(mod, 'step'), 'step function missing'\n",
        encoding="utf-8",
    )
    # Proposal + brief
    proposal = {
        "id": "PROP-test",
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "affected_gates": ["L2"],
            "target_signals": ["SW2"],
            "summary_zh": "test",
            "summary_en": "test",
        },
        "status": "ACCEPTED",
        "source_text": "tighten the condition",
    }
    (tmp_path / "proposals").mkdir()
    (tmp_path / "proposals" / "PROP-test.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-test.md").write_text(
        "# brief\n\n## Engineer's suggestion\n"
        "tighten condition on L2 SW2\n", encoding="utf-8"
    )

    # Git init
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "initial")
    # file:// remote
    bare = tmp_path.parent / f"{tmp_path.name}-remote.git"
    subprocess.run(
        ["git", "init", "--bare", "-q", str(bare)],
        check=True, capture_output=True,
    )
    _git(tmp_path, "remote", "add", "origin", f"file://{bare}")
    _git(tmp_path, "push", "-u", "origin", "main")
    return tmp_path


@pytest.fixture(autouse=True)
def _isolate_proposal_dirs(mini_repo, tmp_path, monkeypatch):
    """Point load_proposal/load_brief at the mini-repo's proposals/
    + queue/ directories. Also point read_audit at the test's
    audit_dir so test-side read_audit() finds what the orchestrator
    wrote."""
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(mini_repo / "queue"))
    # read_audit honors WORKBENCH_SKILL_EXECUTIONS_DIR; tests use
    # tmp_path/execs which is what they pass as audit_dir.
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


def _good_plan_response() -> str:
    """LLM mock — return a valid plan that targets controller.py
    (which is a logic_truth namespace file, per PANEL_NAMESPACES)."""
    plan = {
        "rationale": "tighten the condition for L2 SW2",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "estimated_loc": 1,
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "if condition:",
                "new_snippet": "if condition and tra > -5.5:",
                "reason": "tighten",
            }
        ],
        "test_changes": [],
    }
    return json.dumps(
        {"choices": [{"message": {"role": "assistant", "content": json.dumps(plan)}}]}
    )


def _make_post(*responses: str):
    """Returns a fake_post callable that pops queued responses."""
    iter_resp = iter(responses)

    def _fake_post(url, body, headers, timeout):
        try:
            return next(iter_resp)
        except StopIteration:
            raise AssertionError("post called more times than responses queued")

    return _fake_post


def _fake_gh(url: str = "https://github.com/o/r/pull/99"):
    """Mocked gh runner for pr_maker tests — always succeeds."""
    def _runner(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout=f"{url}\n", stderr=""
        )

    return _runner


# ─── 1. Happy path: full pipeline → PR_OPEN ──────────────────────────


def test_orchestrator_happy_path_reaches_pr_open(mini_repo, tmp_path):
    audit_dir = tmp_path / "execs"
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=audit_dir,
        auto_approve=True,
        request_post_for_llm=_make_post(_good_plan_response()),
        gh_runner=_fake_gh(),
    )
    assert result.error is None
    record = result.record
    assert record.state == ExecutionState.PR_OPEN.value
    assert record.pr_url == "https://github.com/o/r/pull/99"
    assert len(record.commits) == 1
    assert record.branch.startswith("feat/exec-PROP-test-")
    # Audit was persisted; reading it back must round-trip
    persisted = read_audit(record.exec_id)
    assert persisted.state == record.state
    assert persisted.pr_url == record.pr_url


# ─── 2. ASKING rejection → ABORTED ────────────────────────────────────


def test_orchestrator_user_reject_aborts_no_edits(mini_repo, tmp_path):
    audit_dir = tmp_path / "execs"

    def reject_callback(record, ask):
        return AskResponse.REJECTED

    pre_content = (mini_repo / "src/well_harness/controller.py").read_text(
        encoding="utf-8"
    )
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=audit_dir,
        approval_callback=reject_callback,
        request_post_for_llm=_make_post(_good_plan_response()),
    )
    assert result.record.state == ExecutionState.ABORTED.value
    # File NOT touched
    post_content = (mini_repo / "src/well_harness/controller.py").read_text(
        encoding="utf-8"
    )
    assert pre_content == post_content
    # Audit captured the rejection
    assert "user response: rejected" in result.record.abort_reason
    # No commits should exist on a feat/exec-* branch
    proc = subprocess.run(
        ["git", "branch", "--list", "feat/exec-*"],
        cwd=str(mini_repo), capture_output=True, text=True,
    )
    assert proc.stdout.strip() == ""


# ─── 3. Planner failure → FAILED ──────────────────────────────────────


def test_orchestrator_planner_failure_marks_failed(mini_repo, tmp_path):
    """Planner returns garbage twice → PlannerError → FAILED state.
    No edits, no branch, no PR."""
    bad_response = json.dumps(
        {"choices": [{"message": {"content": "not json at all"}}]}
    )
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        api_key_override="fake-key",
        request_post_for_llm=_make_post(bad_response, bad_response),
    )
    assert result.record.state == ExecutionState.FAILED.value
    assert "planner" in result.record.abort_reason
    assert result.record.commits == []
    assert result.record.branch == ""


# ─── 4. Test-gate regression → ABORTED + revert ──────────────────────


def test_orchestrator_test_regression_reverts_and_aborts(mini_repo, tmp_path):
    """LLM produces a plan that BREAKS the test (renames `step` →
    `step_renamed`, so the existing test_smoke's `hasattr(controller,
    'step')` assertion fails). Test gate fires; orchestrator
    reverts edits and transitions to ABORTED."""
    breaking_plan = {
        "rationale": "rename step to step_renamed",
        "affected_namespaces": ["logic_truth"],
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "def step():",
                "new_snippet": "def step_renamed():",
                "reason": "rename",
            }
        ],
    }
    response = json.dumps(
        {"choices": [{"message": {"content": json.dumps(breaking_plan)}}]}
    )
    pre_content = (mini_repo / "src/well_harness/controller.py").read_text(
        encoding="utf-8"
    )
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_make_post(response),
    )
    assert result.record.state == ExecutionState.ABORTED.value
    assert "test gate" in result.record.abort_reason
    # File reverted
    post_content = (mini_repo / "src/well_harness/controller.py").read_text(
        encoding="utf-8"
    )
    assert pre_content == post_content
    # No commits / no branch / no PR
    assert result.record.commits == []


# ─── 5. skip_pr stops short of gh but still commits ──────────────────


def test_orchestrator_skip_pr_still_commits(mini_repo, tmp_path):
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        skip_pr=True,
        request_post_for_llm=_make_post(_good_plan_response()),
    )
    # Reached PR_OPEN state machine-wise (we transitioned from
    # TESTING via tests_pass) but didn't open a PR
    assert result.record.state == ExecutionState.PR_OPEN.value
    assert result.record.pr_url == ""
    assert len(result.record.commits) == 1


# ─── 6. Audit invariants across the lifecycle ────────────────────────


def test_orchestrator_writes_audit_at_each_transition(mini_repo, tmp_path):
    audit_dir = tmp_path / "execs"
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=audit_dir,
        auto_approve=True,
        request_post_for_llm=_make_post(_good_plan_response()),
        gh_runner=_fake_gh(),
    )
    persisted = read_audit(result.record.exec_id)
    state_transitions = [
        (e.from_state, e.to_state)
        for e in persisted.events
        if e.kind == "state_transition"
    ]
    # Full happy-path walk:
    expected_walk = [
        ("INIT", "PLANNING"),
        ("PLANNING", "ASKING"),
        ("ASKING", "EDITING"),
        ("EDITING", "TESTING"),
        ("TESTING", "PR_OPEN"),
    ]
    assert state_transitions == expected_walk


def test_orchestrator_pr_body_contains_exec_stamp(mini_repo, tmp_path):
    """The PR body the orchestrator built must include the
    EXEC-id stamp the P48-05 gate parses."""
    captured: dict = {}

    def capture_gh(cmd, **kwargs):
        captured["body"] = kwargs.get("input", "")
        return subprocess.CompletedProcess(
            args=cmd, returncode=0,
            stdout="https://github.com/o/r/pull/1\n", stderr=""
        )

    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_make_post(_good_plan_response()),
        gh_runner=capture_gh,
    )
    body = captured["body"]
    assert "Exec-Id:" in body
    assert result.record.exec_id in body
    assert "Audit:" in body
    assert "Proposal: PROP-test" in body


# ─── 7. ApprovalCallback contract ─────────────────────────────────────


def test_orchestrator_raises_when_no_approval_callback_or_auto(mini_repo, tmp_path):
    """If neither approval_callback nor auto_approve is provided,
    we should NOT silently auto-approve. Per Q4(b), approval is
    mandatory; the orchestrator surfaces this."""
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        # no approval_callback, no auto_approve
        request_post_for_llm=_make_post(_good_plan_response()),
    )
    # The orchestrator caught the OrchestratorError and recorded
    # FAILED + abort_reason. (The contract is "never let an
    # exception escape"; the audit captures it.)
    assert result.error is not None
    assert isinstance(result.error, OrchestratorError)
    assert result.record.state == ExecutionState.FAILED.value


# ─── 8. Apply error → FAILED + revert ────────────────────────────────


def test_orchestrator_apply_error_transitions_to_failed(mini_repo, tmp_path):
    """LLM produces a plan whose old_snippet doesn't match the
    file. apply_edits() raises → FAILED state, no commits."""
    plan_with_bad_snippet = {
        "rationale": "this won't match",
        "affected_namespaces": ["logic_truth"],
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "this string is nowhere in the file",
                "new_snippet": "x",
                "reason": "wrong",
            }
        ],
    }
    response = json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan_with_bad_snippet)}}]}
    )
    result = execute_proposal(
        proposal_id="PROP-test",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_make_post(response),
    )
    assert result.record.state == ExecutionState.FAILED.value
    assert "apply" in result.record.abort_reason
    assert result.record.commits == []


# ─── 9. Intake error (missing proposal) ───────────────────────────────


def test_orchestrator_missing_proposal_raises(mini_repo, tmp_path):
    """If the proposal doesn't exist, no audit can be built —
    the orchestrator fails fast with OrchestratorError. No
    audit file written."""
    with pytest.raises(OrchestratorError):
        execute_proposal(
            proposal_id="PROP-does-not-exist",
            repo_root=mini_repo,
            audit_dir=tmp_path / "execs",
            auto_approve=True,
            request_post_for_llm=_make_post(_good_plan_response()),
        )
    # No audit files
    assert list((tmp_path / "execs").glob("EXEC-*.json")) == []
