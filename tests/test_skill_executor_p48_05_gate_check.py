"""P48-05 — PR audit gate logic.

Pure-function tests for `check_pr_audit_compliance`. Covers each
of the 7 verification rules + the cross-checks between stamp and
audit JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from well_harness.skill_executor.gate_check import (
    GateCheckResult,
    check_pr_audit_compliance,
)
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
)
from well_harness.skill_executor.pr_maker import build_exec_stamp
from well_harness.skill_executor.states import ExecutionState


# ─── Helpers ──────────────────────────────────────────────────────────


def _stamped_body(
    *,
    exec_id: str,
    proposal_id: str,
    audit_path: str,
    summary: str = "Implements proposal",
) -> str:
    stamp = build_exec_stamp(
        exec_id=exec_id,
        proposal_id=proposal_id,
        audit_path=audit_path,
        executor_version="0.1.0",
    )
    return f"## Summary\n\n{summary}\n\n{stamp}\n"


def _write_audit(
    *,
    repo_root: Path,
    exec_id: str,
    proposal_id: str,
    state: str = "PR_OPEN",
    audit_source: AuditSource = AuditSource.LIVE,
) -> str:
    """Materialize a valid audit JSON. Returns the rel path."""
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind.MODIFY,
        audit_source=audit_source,
        started_at="2026-04-27T12:00:00Z",
        state=state,
    )
    rel = f".planning/skill_executions/{exec_id}.json"
    path = repo_root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rec.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rel


# ─── 1. Gate not required (no namespace files touched) ───────────────


def test_doc_only_pr_skipped(tmp_path):
    result = check_pr_audit_compliance(
        pr_body="just docs",
        changed_files=["docs/random_doc.md", "README.md"],
        repo_root=tmp_path,
    )
    assert result.ok is True
    assert result.gate_required is False
    assert result.matched_files == []


def test_workflow_only_pr_skipped(tmp_path):
    result = check_pr_audit_compliance(
        pr_body="ci tweak",
        changed_files=[".github/workflows/x.yml", "Makefile"],
        repo_root=tmp_path,
    )
    assert result.ok is True
    assert result.gate_required is False


def test_test_only_pr_skipped(tmp_path):
    result = check_pr_audit_compliance(
        pr_body="add tests",
        changed_files=["tests/test_foo.py", "tests/test_bar.py"],
        repo_root=tmp_path,
    )
    assert result.ok is True
    assert result.gate_required is False


# ─── 2. Gate required — happy path ────────────────────────────────────


def test_logic_truth_pr_with_valid_stamp_passes(tmp_path):
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is True
    assert result.gate_required is True
    assert "src/well_harness/controller.py" in result.matched_files


def test_landed_state_also_passes(tmp_path):
    """A merged-and-recorded audit (state=LANDED) is mergeable
    too — covers the case of editing the audit AFTER merge to
    record landed_sha."""
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        state=ExecutionState.LANDED.value,
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is True


def test_requirements_namespace_also_gated(tmp_path):
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=[
            "docs/thrust_reverser/requirements_supplement.md",
            audit_rel,
        ],
        repo_root=tmp_path,
    )
    assert result.ok is True


# ─── 3. Stamp missing or malformed ────────────────────────────────────


def test_no_stamp_blocks(tmp_path):
    result = check_pr_audit_compliance(
        pr_body="## Summary\n\njust a refactor, trust me\n",
        changed_files=["src/well_harness/controller.py"],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "no EXEC-id stamp" in result.reasons[0]


def test_partial_stamp_blocks(tmp_path):
    body = (
        "## Summary\n\n---\n"
        "Exec-Id: EXEC-x\nProposal: P\n"
        # missing Audit + Skill-Executor-Version
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py"],
        repo_root=tmp_path,
    )
    assert result.ok is False


# ─── 4. Audit file missing / unreachable ─────────────────────────────


def test_audit_file_not_in_tree_blocks(tmp_path):
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=".planning/skill_executions/EXEC-20260427T120000123456-abc123.json",
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py"],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "Audit file not found" in result.reasons[0]


def test_audit_path_traversal_blocked(tmp_path):
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path="../../../../etc/passwd",
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py"],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "outside repo root" in result.reasons[0]


def test_audit_not_in_changed_files_blocks(tmp_path):
    """Audit file exists in tree but isn't in this PR's diff —
    replay-attack defense. Block."""
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        # audit_rel intentionally missing from changed_files
        changed_files=["src/well_harness/controller.py"],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "NOT in this PR's changed files" in result.reasons[0]


# ─── 5. Audit schema invalid ──────────────────────────────────────────


def test_audit_invalid_json_blocks(tmp_path):
    audit_rel = ".planning/skill_executions/EXEC-20260427T120000123456-abc123.json"
    audit_path = tmp_path / audit_rel
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text("{ not valid json", encoding="utf-8")
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "not valid JSON" in result.reasons[0]


def test_audit_wrong_schema_version_blocks(tmp_path):
    """Audit with schema_version != current is rejected. P48-05
    refuses cross-version audits to force migration discipline."""
    audit_rel = ".planning/skill_executions/EXEC-20260427T120000123456-abc123.json"
    audit_path = tmp_path / audit_rel
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps({
            "exec_id": "EXEC-20260427T120000123456-abc123",
            "schema_version": 999,
            "proposal_id": "PROP-test",
            "kind": "modify",
            "audit_source": "live",
            "started_at": "2026-04-27T12:00:00Z",
            "state": "PR_OPEN",
        }),
        encoding="utf-8",
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "schema" in result.reasons[0].lower()


# ─── 6. Cross-check failures ──────────────────────────────────────────


def test_stamp_exec_id_mismatch_blocks(tmp_path):
    """Stamp says EXEC-A; audit says EXEC-B. Block."""
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000111111-aaaaaa",
        proposal_id="PROP-test",
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000222222-bbbbbb",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "exec_id" in result.reasons[0]


def test_stamp_proposal_id_mismatch_blocks(tmp_path):
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-real",
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-impostor",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "proposal" in result.reasons[0].lower()


# ─── 7. Audit state must be mergeable ─────────────────────────────────


@pytest.mark.parametrize(
    "bad_state",
    ["INIT", "PLANNING", "ASKING", "EDITING", "TESTING", "ABORTED", "FAILED"],
)
def test_non_mergeable_audit_state_blocks(tmp_path, bad_state):
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        state=bad_state,
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is False
    assert "not mergeable" in result.reasons[0]


# ─── 8. Backfill audit accepted with note ─────────────────────────────


def test_backfill_audit_passes_with_warning_note(tmp_path):
    """Q7(a): backfill audits are valid but flagged so reviewers
    know the audit isn't first-hand."""
    audit_rel = _write_audit(
        repo_root=tmp_path,
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        state=ExecutionState.LANDED.value,
        audit_source=AuditSource.BACKFILL,
    )
    body = _stamped_body(
        exec_id="EXEC-20260427T120000123456-abc123",
        proposal_id="PROP-test",
        audit_path=audit_rel,
    )
    result = check_pr_audit_compliance(
        pr_body=body,
        changed_files=["src/well_harness/controller.py", audit_rel],
        repo_root=tmp_path,
    )
    assert result.ok is True
    assert any("backfill" in r.lower() for r in result.reasons)
