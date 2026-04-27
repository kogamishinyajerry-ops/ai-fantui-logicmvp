"""P48-07 — backfill audits for Q7(a).

Locks down: synthesize_backfill_audit produces a valid audit JSON
that passes the P48-05 schema validator + gate, with
audit_source=backfill so the gate flags it as reconstructed."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from well_harness.skill_executor.audit import read_audit
from well_harness.skill_executor.backfill import (
    BackfillError,
    synthesize_backfill_audit,
)
from well_harness.skill_executor.models import AuditSource, ExecutionKind
from well_harness.skill_executor.schema import validate_audit_dict
from well_harness.skill_executor.states import ExecutionState


@pytest.fixture(autouse=True)
def _isolate_audit_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


@pytest.fixture
def repo(tmp_path):
    """A real git repo so `git show <sha>` actually returns
    something."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(
        ["git", "config", "user.email", "t@x"],
        cwd=str(tmp_path), check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=str(tmp_path), check=True,
    )
    (tmp_path / "f.py").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "f.py"], cwd=str(tmp_path), check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "feat: original change"],
        cwd=str(tmp_path), check=True,
    )
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(tmp_path), capture_output=True, text=True, check=True,
    ).stdout.strip()
    return tmp_path, sha


# ─── 1. Happy path ─────────────────────────────────────────────────────


def test_backfill_produces_valid_audit(repo):
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test",
        landed_sha=sha,
        repo_root=repo_root,
    )
    assert record.audit_source == AuditSource.BACKFILL
    assert record.kind == ExecutionKind.BACKFILL
    assert record.state == ExecutionState.LANDED.value
    assert record.landed_sha == sha
    assert record.commits == [sha]


def test_backfill_record_is_persisted(repo):
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test",
        landed_sha=sha,
        repo_root=repo_root,
    )
    persisted = read_audit(record.exec_id)
    assert persisted.exec_id == record.exec_id
    assert persisted.proposal_id == "PROP-test"


def test_backfill_record_passes_schema_validator(repo):
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test",
        landed_sha=sha,
        repo_root=repo_root,
    )
    # Round-trip through validator — should pass without raising
    validate_audit_dict(record.to_json())


def test_backfill_finished_at_uses_commit_time(repo):
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test",
        landed_sha=sha,
        repo_root=repo_root,
    )
    # Same as the commit's authored time (started_at == finished_at
    # for backfills since there's no real lifecycle to span)
    assert record.finished_at == record.started_at
    # And it's an ISO 8601 timestamp (allow timezone variants)
    assert "T" in record.finished_at


def test_backfill_event_records_synthesis_marker(repo):
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test",
        landed_sha=sha,
        repo_root=repo_root,
        note="custom note for the audit log",
    )
    kinds = [e.kind for e in record.events]
    assert "backfill_synthesized" in kinds
    notes = [e.note for e in record.events if e.kind == "backfill_synthesized"]
    assert notes and "custom note" in notes[0]


# ─── 2. Idempotency ───────────────────────────────────────────────────


def test_backfill_same_inputs_produce_same_exec_id(repo):
    repo_root, sha = repo
    a = synthesize_backfill_audit(
        proposal_id="PROP-test", landed_sha=sha, repo_root=repo_root,
    )
    b = synthesize_backfill_audit(
        proposal_id="PROP-test", landed_sha=sha, repo_root=repo_root,
    )
    assert a.exec_id == b.exec_id


def test_backfill_different_proposals_produce_different_exec_id(repo):
    repo_root, sha = repo
    a = synthesize_backfill_audit(
        proposal_id="PROP-A", landed_sha=sha, repo_root=repo_root,
    )
    b = synthesize_backfill_audit(
        proposal_id="PROP-B", landed_sha=sha, repo_root=repo_root,
    )
    assert a.exec_id != b.exec_id


# ─── 3. Validation errors ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "bad_sha",
    [
        "",
        "abc1234",        # too short
        "z" * 40,         # not hex
        "abc",
        "abc1234ef",      # 9 chars, not 40
    ],
)
def test_backfill_rejects_non_full_sha(repo, bad_sha):
    repo_root, _ = repo
    with pytest.raises(BackfillError):
        synthesize_backfill_audit(
            proposal_id="PROP-test",
            landed_sha=bad_sha,
            repo_root=repo_root,
        )


def test_backfill_handles_unknown_sha_via_runner(repo, tmp_path):
    repo_root, _ = repo
    # Use a fake git_runner that fails — backfill should raise.
    def fail_runner(cmd, **kwargs):
        return subprocess.CompletedProcess(
            args=cmd, returncode=1, stdout="", stderr="bad object",
        )
    with pytest.raises(BackfillError) as exc:
        synthesize_backfill_audit(
            proposal_id="PROP-test",
            landed_sha="0" * 40,
            repo_root=repo_root,
            git_runner=fail_runner,
        )
    assert "git show" in str(exc.value)


# ─── 4. Plan stub honest about limitations ────────────────────────────


def test_backfill_plan_rationale_says_so(repo):
    """A reviewer reading the audit needs to know the plan
    wasn't really produced by an LLM. The rationale must
    explicitly say so."""
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test", landed_sha=sha, repo_root=repo_root,
    )
    assert "backfill" in record.plan.rationale.lower()


def test_backfill_plan_planner_response_captures_commit_subject(repo):
    repo_root, sha = repo
    record = synthesize_backfill_audit(
        proposal_id="PROP-test", landed_sha=sha, repo_root=repo_root,
    )
    # The synthetic planner_response holds the commit subject
    assert "feat: original change" in record.plan.planner_response


# ─── 5. Runbook exists ────────────────────────────────────────────────


def test_runbook_exists():
    runbook = (
        Path(__file__).resolve().parents[1]
        / "docs" / "runbooks" / "p48_first_live_run.md"
    )
    assert runbook.is_file()


def test_runbook_documents_step_1_backfill():
    runbook = (
        Path(__file__).resolve().parents[1]
        / "docs" / "runbooks" / "p48_first_live_run.md"
    )
    body = runbook.read_text(encoding="utf-8")
    assert "synthesize_backfill_audit" in body


def test_runbook_documents_pass_criteria():
    runbook = (
        Path(__file__).resolve().parents[1]
        / "docs" / "runbooks" / "p48_first_live_run.md"
    )
    body = runbook.read_text(encoding="utf-8")
    assert "Pass criteria" in body
    # Critical gates that must show up in the table
    assert "P48-05" in body
    assert "landed_truth_sha" in body
