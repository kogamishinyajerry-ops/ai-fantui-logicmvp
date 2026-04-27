"""P49-01c — cancel signal IO + ExecutionCancelled exception.

Locks down: write_cancel_signal / read_and_clear_cancel mirror the
approval-signal pattern but carry structured payload (actor + ISO
timestamp + note) so the audit's abort_reason is informative.
ExecutionCancelled is raised by the polling callback when a cancel
signal beats an approval signal in the same poll cycle.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    Ask,
    AskResponse,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.states import ExecutionState
from well_harness.skill_executor.workbench_polling import (
    ApprovalTimeoutError,
    ExecutionCancelled,
    WorkbenchApprovalCallback,
    cancel_signal_path,
    check_cancel,
    read_and_clear_cancel,
    write_approval_signal,
    write_cancel_signal,
)


# ─── 1. Path helper ──────────────────────────────────────────────────


def test_cancel_signal_path_sibling_to_audit(tmp_path):
    p = cancel_signal_path(audit_dir=tmp_path, exec_id="EXEC-X")
    assert p == tmp_path / "EXEC-X.cancel"


# ─── 2. Write + read round-trip ─────────────────────────────────────


def test_write_cancel_signal_creates_file_with_actor(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path,
        exec_id="EXEC-test",
        actor="Kogami",
    )
    target = tmp_path / "EXEC-test.cancel"
    assert target.is_file()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["actor"] == "Kogami"
    assert payload["at"]  # non-empty ISO timestamp
    assert "T" in payload["at"]


def test_write_cancel_signal_carries_note(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path,
        exec_id="EXEC-test",
        actor="Kogami",
        note="planning got stuck on minimax timeout",
    )
    payload = json.loads((tmp_path / "EXEC-test.cancel").read_text())
    assert payload["note"] == "planning got stuck on minimax timeout"


def test_write_cancel_signal_creates_audit_dir_if_missing(tmp_path):
    audit_dir = tmp_path / "deep" / "nested"
    write_cancel_signal(
        audit_dir=audit_dir, exec_id="EXEC-test", actor="x"
    )
    assert (audit_dir / "EXEC-test.cancel").is_file()


def test_read_and_clear_cancel_removes_file(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", actor="Kogami",
    )
    info = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-test")
    assert info is not None
    assert info["actor"] == "Kogami"
    # Second call: file is gone, returns None
    assert read_and_clear_cancel(
        audit_dir=tmp_path, exec_id="EXEC-test"
    ) is None


def test_read_and_clear_returns_note(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path,
        exec_id="EXEC-test",
        actor="Kogami",
        note="abort, abort",
    )
    info = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-test")
    assert info["note"] == "abort, abort"


def test_no_signal_returns_none(tmp_path):
    assert read_and_clear_cancel(
        audit_dir=tmp_path, exec_id="EXEC-no-signal"
    ) is None


# ─── 3. Garbage handling ────────────────────────────────────────────


def test_corrupt_json_treated_as_no_signal_and_cleared(tmp_path):
    target = tmp_path / "EXEC-test.cancel"
    target.write_text("{ broken not json", encoding="utf-8")
    info = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-test")
    assert info is None
    # File should be cleared so a future legit signal isn't masked
    assert not target.exists()


def test_missing_actor_treated_as_no_signal(tmp_path):
    target = tmp_path / "EXEC-test.cancel"
    target.write_text(json.dumps({"note": "no actor"}), encoding="utf-8")
    info = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-test")
    assert info is None


def test_default_actor_when_blank(tmp_path):
    """write_cancel_signal called with actor='' should still write
    a usable signal — defaults to 'anonymous'."""
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", actor="",
    )
    info = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-test")
    assert info["actor"] == "anonymous"


# ─── 4. check_cancel alias ─────────────────────────────────────────


def test_check_cancel_is_alias_for_read_and_clear(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", actor="Kogami",
    )
    info = check_cancel(audit_dir=tmp_path, exec_id="EXEC-test")
    assert info is not None
    assert info["actor"] == "Kogami"


# ─── 5. Atomic write ───────────────────────────────────────────────


def test_atomic_write_no_tmp_file_left_behind(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", actor="Kogami",
    )
    leftover_tmps = list(tmp_path.glob("*.tmp"))
    assert leftover_tmps == []


# ─── 6. Different execs are isolated ────────────────────────────────


def test_signals_are_isolated_by_exec_id(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-A", actor="Alice",
    )
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-B", actor="Bob",
    )
    a = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-A")
    b = read_and_clear_cancel(audit_dir=tmp_path, exec_id="EXEC-B")
    assert a["actor"] == "Alice"
    assert b["actor"] == "Bob"


# ─── 7. ExecutionCancelled exception shape ──────────────────────────


def test_execution_cancelled_carries_actor_and_note():
    exc = ExecutionCancelled(actor="Kogami", note="stuck")
    assert exc.actor == "Kogami"
    assert exc.note == "stuck"
    assert "Kogami" in str(exc)
    assert "stuck" in str(exc)


def test_execution_cancelled_without_note():
    exc = ExecutionCancelled(actor="Kogami")
    assert exc.actor == "Kogami"
    assert exc.note == ""
    assert "Kogami" in str(exc)


# ─── 8. Polling callback honors cancel signal ───────────────────────


def _make_record(exec_id: str = "EXEC-test") -> ExecutionRecord:
    return ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-test",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T13:00:00Z",
        finished_at="",
        state=ExecutionState.ASKING.value,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="test", file_edits=[]),
    )


def _make_ask() -> Ask:
    return Ask(ask_id="ask-1", question="approve?")


def test_polling_callback_raises_on_cancel_signal(tmp_path):
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", actor="Kogami", note="abort",
    )
    cb = WorkbenchApprovalCallback(
        audit_dir=tmp_path,
        poll_interval_sec=0.0,
        timeout_sec=1.0,
        sleep=lambda _s: None,
    )
    with pytest.raises(ExecutionCancelled) as exc_info:
        cb(_make_record(), _make_ask())
    assert exc_info.value.actor == "Kogami"
    assert exc_info.value.note == "abort"


def test_polling_cancel_takes_precedence_over_approval(tmp_path):
    """If both signals appear in the same poll cycle, cancel wins —
    we never apply edits when the user wants to abort."""
    write_approval_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", response="approved",
    )
    write_cancel_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", actor="Kogami",
    )
    cb = WorkbenchApprovalCallback(
        audit_dir=tmp_path,
        poll_interval_sec=0.0,
        timeout_sec=1.0,
        sleep=lambda _s: None,
    )
    with pytest.raises(ExecutionCancelled):
        cb(_make_record(), _make_ask())


def test_polling_approval_still_works_without_cancel(tmp_path):
    """Sanity check: P48-06 approval flow isn't broken by P49-01c."""
    write_approval_signal(
        audit_dir=tmp_path, exec_id="EXEC-test", response="approved",
    )
    cb = WorkbenchApprovalCallback(
        audit_dir=tmp_path,
        poll_interval_sec=0.0,
        timeout_sec=1.0,
        sleep=lambda _s: None,
    )
    result = cb(_make_record(), _make_ask())
    assert result == AskResponse.APPROVED
