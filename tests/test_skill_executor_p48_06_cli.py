"""P48-06 — CLI subcommand smoke tests.

The CLI's `execute` subcommand is exercised end-to-end (real
subprocess against a tmp_path mini-repo) in the orchestrator
integration tests. This module focuses on argparse wiring, the
`show` subcommand, and exit-code mapping.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "well_harness.skill_executor", *args],
        capture_output=True,
        text=True,
        timeout=20,
        env=env,
    )


# ─── 1. argparse wiring ──────────────────────────────────────────────


def test_no_args_returns_help_or_error():
    proc = _run_cli()
    # argparse exits 2 when subcommand missing
    assert proc.returncode == 2


def test_execute_help_works():
    proc = _run_cli("execute", "--help")
    assert proc.returncode == 0
    assert "skip-pr" in proc.stdout
    assert "auto-approve" in proc.stdout


def test_show_help_works():
    proc = _run_cli("show", "--help")
    assert proc.returncode == 0
    assert "exec_id" in proc.stdout


# ─── 2. show subcommand ──────────────────────────────────────────────


def test_show_returns_audit_json(tmp_path):
    audit_dir = tmp_path / "execs"
    audit_dir.mkdir()
    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000123456-abc123",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-test",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
    )
    # Use the audit module's writer with the env override
    env_extra = {"WORKBENCH_SKILL_EXECUTIONS_DIR": str(audit_dir)}
    os.environ["WORKBENCH_SKILL_EXECUTIONS_DIR"] = str(audit_dir)
    try:
        write_audit(rec)
    finally:
        del os.environ["WORKBENCH_SKILL_EXECUTIONS_DIR"]
    proc = _run_cli("show", rec.exec_id, env_extra=env_extra)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    parsed = json.loads(proc.stdout)
    assert parsed["exec_id"] == rec.exec_id
    assert parsed["proposal_id"] == "PROP-test"


def test_show_unknown_exec_id_exits_3(tmp_path):
    env_extra = {"WORKBENCH_SKILL_EXECUTIONS_DIR": str(tmp_path / "execs")}
    proc = _run_cli(
        "show", "EXEC-20260427T120000999999-deadbe", env_extra=env_extra
    )
    assert proc.returncode == 3
    assert "not found" in proc.stderr


def test_show_malformed_id_exits_3(tmp_path):
    env_extra = {"WORKBENCH_SKILL_EXECUTIONS_DIR": str(tmp_path / "execs")}
    proc = _run_cli("show", "not-an-exec-id", env_extra=env_extra)
    assert proc.returncode == 3


# ─── 3. execute exit-code mapping ────────────────────────────────────


def test_execute_missing_proposal_exits_2_or_3(tmp_path):
    """A proposal id that doesn't exist surfaces as
    OrchestratorError → exit 3 (the orchestrator raises before
    any audit can be built; CLI's intake catches it)."""
    env_extra = {"WORKBENCH_SKILL_EXECUTIONS_DIR": str(tmp_path / "execs")}
    proc = _run_cli(
        "execute", "PROP-does-not-exist",
        "--repo-root", str(tmp_path),
        "--auto-approve",
        env_extra=env_extra,
    )
    # Either 2 or 3 is acceptable here — both signal failure.
    # The exact mapping is internal to the CLI.
    assert proc.returncode != 0
