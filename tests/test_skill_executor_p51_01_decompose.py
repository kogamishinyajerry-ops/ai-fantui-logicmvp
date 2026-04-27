"""P51-01 — rule-based task decomposition tests.

Locks down: decompose(text) returns a 5-step PlanStep list covering
PLANNING→ASKING→EDITING→TESTING→PR_OPEN. Three keyword templates
(修改参数 / 加测试 / 修复 bug) plus a default fallback. Steps round-
trip through ExecutionRecord JSON. Orchestrator wires decompose() at
INIT and emits plan_step_started / plan_step_completed events on
state transitions.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.models import (
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlanStep,
)
from well_harness.skill_executor.orchestrator import execute_proposal
from well_harness.skill_executor.planner import decompose


# ─── 1. Template classification ──────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "修改参数到 0.5",
        "调整参数 deploy_threshold",
        "修参数",
        "modify parameter X to 1.0",
        "tune deploy controller",
        "tweak settle delay",
    ],
)
def test_modify_param_template_match(text):
    steps = decompose(text)
    assert steps[0].description.startswith("LLM"), steps[0]
    # Modify-param edits land in src/, not tests/
    edit = next(s for s in steps if s.phase_name == "EDITING")
    assert any("src" in t for t in edit.target_files), edit.target_files


@pytest.mark.parametrize(
    "text",
    [
        "加测试 for governance",
        "增加测试 cover regression",
        "补测试 coverage",
        "add tests for new flow",
        "write test for edge case",
        "regression test missing",
    ],
)
def test_add_test_template_match(text):
    steps = decompose(text)
    edit = next(s for s in steps if s.phase_name == "EDITING")
    assert any("tests" in t for t in edit.target_files), edit.target_files
    # No src/ in modify list — pure test add
    assert not any("src" in t for t in edit.target_files), edit.target_files


@pytest.mark.parametrize(
    "text",
    [
        "修复 bug X 在 controller",
        "修bug regression",
        "修复缺陷",
        "fix bug in deploy logic",
        "patch broken assertion",
    ],
)
def test_fix_bug_template_match(text):
    steps = decompose(text)
    edit = next(s for s in steps if s.phase_name == "EDITING")
    # Fix-bug edits BOTH src AND tests (test-first regression)
    assert any("src" in t for t in edit.target_files)
    assert any("tests" in t for t in edit.target_files)


def test_default_fallback_for_unknown_text():
    """Anything that doesn't match a keyword still produces a usable
    timeline — never returns []."""
    steps = decompose("unrelated description without any keywords")
    assert len(steps) == 5
    assert [s.phase_name for s in steps] == [
        "PLANNING", "ASKING", "EDITING", "TESTING", "PR_OPEN",
    ]


def test_decompose_handles_none_and_empty():
    """Defensive: don't crash on None / empty input — emit default
    timeline so the UI never has to handle an empty list."""
    assert len(decompose("")) == 5
    assert len(decompose(None)) == 5  # type: ignore[arg-type]


# ─── 2. Step shape lockdown ──────────────────────────────────────


def test_every_template_covers_required_phases():
    """No matter the template, the UI relies on these 5 phases
    being present — drop any one and the timeline has a gap."""
    for q in ["修改参数", "加测试", "修复 bug", "default fallback"]:
        steps = decompose(q)
        names = [s.phase_name for s in steps]
        for required in ("PLANNING", "ASKING", "EDITING", "TESTING", "PR_OPEN"):
            assert required in names, (q, names)


def test_estimated_seconds_positive_on_every_step():
    for q in ["修改参数", "加测试", "修复 bug", "x"]:
        for s in decompose(q):
            assert s.estimated_seconds > 0, (q, s)


def test_decompose_returns_fresh_instances():
    """Caller mutates started_at / completed_at — must NOT bleed
    into the next call's template."""
    a = decompose("修改参数")
    a[0].started_at = "2026-04-27T10:00:00Z"
    b = decompose("修改参数")
    assert b[0].started_at == ""


# ─── 3. JSON round-trip ──────────────────────────────────────────


def test_planstep_round_trips():
    step = PlanStep(
        phase_name="EDITING",
        description="改写常量",
        estimated_seconds=8.0,
        target_files=["src/foo.py"],
        started_at="2026-04-27T10:00:00Z",
        completed_at="2026-04-27T10:00:08Z",
        actual_duration_sec=8.0,
    )
    j = step.to_json()
    re = PlanStep.from_json(j)
    assert re == step


def test_execution_record_round_trips_plan_steps():
    r = ExecutionRecord(
        exec_id="x",
        schema_version=1,
        proposal_id="p",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T10:00:00Z",
    )
    r.plan_steps = decompose("修改参数")
    j = r.to_json()
    assert "plan_steps" in j
    assert len(j["plan_steps"]) == 5
    r2 = ExecutionRecord.from_json(j)
    assert len(r2.plan_steps) == 5
    assert r2.plan_steps[0].phase_name == "PLANNING"


def test_execution_record_handles_missing_plan_steps():
    """Backwards-compat: pre-P51 audits don't have plan_steps; load
    them as empty list so the dashboard doesn't crash."""
    j = {
        "exec_id": "x",
        "schema_version": 1,
        "proposal_id": "p",
        "kind": "modify",
        "audit_source": "live",
        "started_at": "2026-04-27T10:00:00Z",
    }
    r = ExecutionRecord.from_json(j)
    assert r.plan_steps == []


# ─── 4. Orchestrator integration ─────────────────────────────────


def _git(repo_root, *args):
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "def test_pass(): assert 1 + 1 == 2\n", encoding="utf-8",
    )
    proposal = {
        "id": "PROP-p51-01",
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "summary_zh": "修改参数",
            "summary_en": "modify parameter",
        },
        "status": "ACCEPTED",
        "source_text": "x",
    }
    (tmp_path / "proposals").mkdir()
    (tmp_path / "proposals" / "PROP-p51-01.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-p51-01.md").write_text(
        "# brief — modify parameter\n", encoding="utf-8",
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


def test_orchestrator_populates_plan_steps_at_init(mini_repo, tmp_path):
    """plan_steps appears on the audit record from INIT — before
    the LLM has been called. The Plan Timeline UI relies on this
    timing."""
    result = execute_proposal(
        proposal_id="PROP-p51-01",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    assert result.error is None, result.error
    assert len(result.record.plan_steps) == 5
    # interpretation summary said "修改参数" → modify_param template
    edit_step = next(
        s for s in result.record.plan_steps if s.phase_name == "EDITING"
    )
    assert any("src" in t for t in edit_step.target_files)


def test_orchestrator_emits_plan_step_started_and_completed(mini_repo, tmp_path):
    result = execute_proposal(
        proposal_id="PROP-p51-01",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    kinds = [e.kind for e in result.record.events]
    started = [k for k in kinds if k == "plan_step_started"]
    completed = [k for k in kinds if k == "plan_step_completed"]
    # We pass through PLANNING, ASKING, EDITING, TESTING, PR_OPEN —
    # five steps, each gets started + completed (PR_OPEN may be
    # still in-flight at LANDED, which is fine — we test ≥1 here).
    assert len(started) >= 4, (started, kinds)
    assert len(completed) >= 4, (completed, kinds)


def test_orchestrator_records_actual_duration_on_completed_steps(mini_repo, tmp_path):
    result = execute_proposal(
        proposal_id="PROP-p51-01",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(_plan_response_body()),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    completed = [
        s for s in result.record.plan_steps if s.completed_at
    ]
    assert len(completed) >= 4
    for s in completed:
        assert s.actual_duration_sec is not None
        assert s.actual_duration_sec >= 0


def test_failed_run_still_has_plan_steps_in_audit(mini_repo, tmp_path):
    """Even if the run aborts in EDITING (or earlier), plan_steps
    stay in the audit. The dashboard renders the failure point —
    seeing which step was in flight is the whole point."""
    bad_plan = {
        "rationale": "x",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "NONEXISTENT_OLD",
                "new_snippet": "x",
                "reason": "x",
            }
        ],
    }
    body = json.dumps(
        {"choices": [{"message": {"content": json.dumps(bad_plan)}}]}
    )
    result = execute_proposal(
        proposal_id="PROP-p51-01",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_post_returns(body),
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    assert result.record.state == "FAILED"
    assert len(result.record.plan_steps) == 5
    # The first step (PLANNING) was started + completed; later
    # ones may be untouched.
    planning_step = next(
        s for s in result.record.plan_steps if s.phase_name == "PLANNING"
    )
    assert planning_step.started_at != ""
    assert planning_step.completed_at != ""
