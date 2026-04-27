"""P48-05 — gate_check_cli end-to-end via subprocess.

Each test writes a body file + changed-files file + (sometimes) an
audit JSON in a tmp_path, then runs the CLI as a subprocess and
asserts on exit code + stdout.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
)
from well_harness.skill_executor.pr_maker import build_exec_stamp
from well_harness.skill_executor.states import ExecutionState


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args, repo_root: Path) -> subprocess.CompletedProcess:
    """Invoke the CLI module as the workflow does."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "well_harness.skill_executor.gate_check_cli", *args],
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _write_audit(*, repo_root: Path, exec_id: str, proposal_id: str, state: str) -> str:
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        state=state,
    )
    rel = f".planning/skill_executions/{exec_id}.json"
    target = repo_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(rec.to_json(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return rel


# ─── 1. Subcommand wiring ─────────────────────────────────────────────


def test_no_args_returns_help(tmp_path):
    proc = _run_cli(repo_root=tmp_path)
    # argparse exits 2 when required subcommand is missing.
    assert proc.returncode == 2


# ─── 2. Doc-only PR — exit 0 + "gate not required" ────────────────────


def test_doc_only_pr_exits_zero(tmp_path):
    body = tmp_path / "body.txt"
    changed = tmp_path / "changed.txt"
    body.write_text("just docs\n", encoding="utf-8")
    changed.write_text("docs/foo.md\nREADME.md\n", encoding="utf-8")
    proc = _run_cli(
        "verify-pr",
        "--body-file", str(body),
        "--changed-files-file", str(changed),
        "--repo-root", str(tmp_path),
        repo_root=tmp_path,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "gate not required" in proc.stdout


# ─── 3. Truth-engine PR with valid stamp + audit — exit 0 ─────────────


def test_valid_truth_engine_pr_exits_zero(tmp_path):
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        state=ExecutionState.PR_OPEN.value,
    )
    stamp = build_exec_stamp(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
        executor_version="0.1.0",
    )
    body_text = f"## Summary\n\nimplementing\n\n{stamp}\n"
    body = tmp_path / "body.txt"
    body.write_text(body_text, encoding="utf-8")
    changed = tmp_path / "changed.txt"
    changed.write_text(f"src/well_harness/controller.py\n{audit_rel}\n", encoding="utf-8")
    proc = _run_cli(
        "verify-pr",
        "--body-file", str(body),
        "--changed-files-file", str(changed),
        "--repo-root", str(tmp_path),
        repo_root=tmp_path,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Pass — audit chain validated" in proc.stdout


# ─── 4. Truth-engine PR without stamp — exit 1 ────────────────────────


def test_no_stamp_pr_exits_one(tmp_path):
    body = tmp_path / "body.txt"
    body.write_text("trust me bro\n", encoding="utf-8")
    changed = tmp_path / "changed.txt"
    changed.write_text("src/well_harness/controller.py\n", encoding="utf-8")
    proc = _run_cli(
        "verify-pr",
        "--body-file", str(body),
        "--changed-files-file", str(changed),
        "--repo-root", str(tmp_path),
        repo_root=tmp_path,
    )
    assert proc.returncode == 1
    assert "Block" in proc.stdout
    assert "no EXEC-id stamp" in proc.stdout


# ─── 5. Audit not in changed files — exit 1 ───────────────────────────


def test_replay_attack_blocked(tmp_path):
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        state=ExecutionState.PR_OPEN.value,
    )
    stamp = build_exec_stamp(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
        executor_version="0.1.0",
    )
    body = tmp_path / "body.txt"
    body.write_text(f"## Summary\n\n{stamp}\n", encoding="utf-8")
    changed = tmp_path / "changed.txt"
    # NOTE: audit_rel intentionally absent from changed list
    changed.write_text("src/well_harness/controller.py\n", encoding="utf-8")
    proc = _run_cli(
        "verify-pr",
        "--body-file", str(body),
        "--changed-files-file", str(changed),
        "--repo-root", str(tmp_path),
        repo_root=tmp_path,
    )
    assert proc.returncode == 1
    assert "NOT in this PR's changed files" in proc.stdout


# ─── 6. Failure modes surface in stdout for PR comment ────────────────


def test_failure_output_human_readable(tmp_path):
    body = tmp_path / "body.txt"
    body.write_text("missing stamp\n", encoding="utf-8")
    changed = tmp_path / "changed.txt"
    changed.write_text("src/well_harness/models.py\n", encoding="utf-8")
    proc = _run_cli(
        "verify-pr",
        "--body-file", str(body),
        "--changed-files-file", str(changed),
        "--repo-root", str(tmp_path),
        repo_root=tmp_path,
    )
    out = proc.stdout
    # Stable header so the workflow comment looks tidy
    assert out.startswith("# Skill-Executor PR Audit Gate")
    assert "**Files matched against PANEL_NAMESPACES:**" in out
    assert "src/well_harness/models.py" in out
    assert "**Reasons:**" in out


# ─── 7. Missing input files surface useful error ──────────────────────


def test_missing_body_file_error(tmp_path):
    proc = _run_cli(
        "verify-pr",
        "--body-file", str(tmp_path / "does-not-exist.txt"),
        "--changed-files-file", str(tmp_path / "changed.txt"),
        "--repo-root", str(tmp_path),
        repo_root=tmp_path,
    )
    assert proc.returncode == 2
    assert "cannot read body file" in proc.stderr


# ─── 8. Workflow YAML schema sanity ───────────────────────────────────


def test_workflow_yaml_exists():
    wf = REPO_ROOT / ".github" / "workflows" / "exec-audit-gate.yml"
    assert wf.is_file(), "PR audit gate workflow missing"


def test_workflow_yaml_pinned_to_main_only():
    """Gate runs on PRs targeting main, not other branches."""
    wf = (REPO_ROOT / ".github" / "workflows" / "exec-audit-gate.yml").read_text(encoding="utf-8")
    assert "branches:" in wf
    assert "main" in wf


def test_workflow_yaml_invokes_cli_module():
    wf = (REPO_ROOT / ".github" / "workflows" / "exec-audit-gate.yml").read_text(encoding="utf-8")
    assert "well_harness.skill_executor.gate_check_cli" in wf
    assert "verify-pr" in wf


def test_workflow_yaml_uses_pr_head_sha_for_diff():
    wf = (REPO_ROOT / ".github" / "workflows" / "exec-audit-gate.yml").read_text(encoding="utf-8")
    # Without checking out the head SHA we'd diff against an old
    # tree; ensure the workflow does the right thing.
    assert "github.event.pull_request.head.sha" in wf
    assert "github.event.pull_request.base.sha" in wf
