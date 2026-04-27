"""P48-07 — revert kind branch + PR title naming.

Locks down: revert proposals get `revert/...` branch + `revert(...)` PR
title, modify proposals stay `feat/...` + `feat(...)`. Commit message
already handled (P48-04); this slice covers the surfaces the user
sees in GitHub UI.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.models import (
    ExecutionKind,
    PlannedChange,
)
from well_harness.skill_executor.orchestrator import (
    _branch_name_for,
    _pr_title_for,
)


# ─── Branch-name helper ────────────────────────────────────────────────


def test_branch_name_modify_default():
    name = _branch_name_for(
        "PROP-test", "EXEC-20260427T120000123456-abc123",
    )
    assert name == "feat/exec-PROP-test-abc123"


def test_branch_name_revert_uses_revert_prefix():
    name = _branch_name_for(
        "PROP-test", "EXEC-20260427T120000123456-abc123",
        kind=ExecutionKind.REVERT,
    )
    assert name == "revert/exec-PROP-test-abc123"


def test_branch_name_modify_explicit_kind():
    name = _branch_name_for(
        "PROP-test", "EXEC-20260427T120000123456-abc123",
        kind=ExecutionKind.MODIFY,
    )
    assert name == "feat/exec-PROP-test-abc123"


# ─── PR title helper ───────────────────────────────────────────────────


def _modify_proposal() -> dict:
    return {
        "id": "PROP-test",
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {"change_kind": "tighten_condition"},
    }


def _revert_proposal() -> dict:
    return {
        "id": "PROP-revert-test",
        "system_id": "thrust-reverser",
        "kind": "revert",
        "revert_target_sha": "ec6f4fc94188fb3a7e68ef3763c3002b14ee105b",
        "revert_of_proposal_id": "PROP-original",
        "interpretation": {"change_kind": "revert"},
    }


def _stub_plan() -> PlannedChange:
    return PlannedChange(rationale="r", file_edits=[])


def test_pr_title_modify_uses_feat_prefix():
    title = _pr_title_for(_modify_proposal(), _stub_plan())
    assert title.startswith("feat(thrust-reverser):")
    assert "tighten_condition" in title


def test_pr_title_revert_uses_revert_prefix():
    title = _pr_title_for(_revert_proposal(), _stub_plan())
    assert title.startswith("revert(thrust-reverser):")


def test_pr_title_revert_includes_short_target_sha():
    """Reviewers reading the PR list view should see what SHA is
    being undone without opening the PR body."""
    title = _pr_title_for(_revert_proposal(), _stub_plan())
    assert "ec6f4fc" in title
    assert "undo" in title.lower()


def test_pr_title_truncated_to_70_chars():
    """Long proposal ids shouldn't blow up the title; the GitHub
    UI truncates anything past 70 chars."""
    long_proposal = {
        **_revert_proposal(),
        "id": "PROP-" + "X" * 80,
    }
    title = _pr_title_for(long_proposal, _stub_plan())
    assert len(title) <= 70


# ─── End-to-end orchestrator with revert kind ────────────────────────


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def revert_mini_repo(tmp_path):
    """Mini-repo + accepted revert proposal + brief."""
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "def step():\n    if condition:\n        return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "import os, importlib.util\n"
        "HERE = os.path.dirname(__file__)\n"
        "CTRL = os.path.join(HERE, '..', 'src', 'well_harness', 'controller.py')\n"
        "def test_step_present():\n"
        "    spec = importlib.util.spec_from_file_location('mc', CTRL)\n"
        "    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)\n"
        "    assert hasattr(mod, 'step')\n",
        encoding="utf-8",
    )
    proposal = {
        "id": "PROP-revert-test",
        "system_id": "thrust-reverser",
        "kind": "revert",
        "interpretation": {
            "change_kind": "revert",
            "summary_zh": "[REVERT]",
            "summary_en": "[REVERT]",
        },
        "status": "ACCEPTED",
        "source_text": "revert PR #48",
        "revert_of_proposal_id": "PROP-original",
        "revert_target_sha": "ec6f4fc94188fb3a7e68ef3763c3002b14ee105b",
    }
    (tmp_path / "proposals").mkdir()
    (tmp_path / "proposals" / "PROP-revert-test.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-revert-test.md").write_text(
        "# brief · REVERT\n\nundo ec6f4fc...\n", encoding="utf-8"
    )
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "initial")
    bare = tmp_path.parent / f"{tmp_path.name}-remote.git"
    subprocess.run(
        ["git", "init", "--bare", "-q", str(bare)],
        check=True, capture_output=True,
    )
    _git(tmp_path, "remote", "add", "origin", f"file://{bare}")
    _git(tmp_path, "push", "-u", "origin", "main")
    return tmp_path


@pytest.fixture(autouse=True)
def _isolate_env(revert_mini_repo, tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(revert_mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(revert_mini_repo / "queue"))
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


def _good_revert_plan_json() -> str:
    plan = {
        "rationale": "undo the conditional tightening",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "if condition:",
                "new_snippet": "if condition:  # reverted",
                "reason": "undo PR #48 line",
            }
        ],
    }
    return json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )


def _make_post(*responses):
    iter_resp = iter(responses)

    def _post(url, body, headers, timeout):
        try:
            return next(iter_resp)
        except StopIteration:
            raise AssertionError("post called more than expected")

    return _post


def _fake_gh(url="https://github.com/o/r/pull/100"):
    def _runner(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=0, stdout=f"{url}\n", stderr=""
        )

    return _runner


def test_orchestrator_revert_uses_revert_branch(revert_mini_repo, tmp_path):
    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id="PROP-revert-test",
        repo_root=revert_mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_make_post(_good_revert_plan_json()),
        gh_runner=_fake_gh(),
    )
    assert result.error is None, result.error
    assert result.record.branch.startswith("revert/exec-PROP-revert-test-")


def test_orchestrator_revert_pr_title_starts_with_revert(revert_mini_repo, tmp_path):
    from well_harness.skill_executor.orchestrator import execute_proposal

    captured = {}

    def capture_gh(cmd, **kwargs):
        # gh pr create --title <title> ...
        if "--title" in cmd:
            idx = cmd.index("--title")
            captured["title"] = cmd[idx + 1]
        return subprocess.CompletedProcess(
            args=cmd, returncode=0,
            stdout="https://github.com/o/r/pull/100\n", stderr=""
        )

    execute_proposal(
        proposal_id="PROP-revert-test",
        repo_root=revert_mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=_make_post(_good_revert_plan_json()),
        gh_runner=capture_gh,
    )
    assert "title" in captured
    assert captured["title"].startswith("revert(thrust-reverser):")


def test_orchestrator_revert_commit_uses_revert_subject(revert_mini_repo, tmp_path):
    """Commit message subject already used `revert(...)` for kind=revert
    in P48-04; this test pins it down so future refactors don't break it."""
    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id="PROP-revert-test",
        repo_root=revert_mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        skip_pr=True,
        request_post_for_llm=_make_post(_good_revert_plan_json()),
    )
    assert len(result.record.commits) == 1
    log = subprocess.run(
        ["git", "log", "-1", "--format=%s", result.record.commits[0]],
        cwd=str(revert_mini_repo),
        capture_output=True, text=True,
    )
    assert log.stdout.startswith("revert(thrust-reverser):"), log.stdout
