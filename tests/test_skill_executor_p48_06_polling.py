"""P48-06 — workbench polling callback.

Tests for the file-based approval signal:
  - signal write/read round-trip
  - signal is consumed (deleted) after read
  - polling callback returns the right AskResponse
  - timeout raises ApprovalTimeoutError
"""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from well_harness.skill_executor.errors import SkillExecutorError
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    Ask,
    AskResponse,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
)
from well_harness.skill_executor.workbench_polling import (
    ApprovalTimeoutError,
    WorkbenchApprovalCallback,
    approval_signal_path,
    read_and_clear_approval,
    write_approval_signal,
)


def _stub_record(exec_id: str = "EXEC-20260427T120000123456-abc123") -> ExecutionRecord:
    return ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-test",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
    )


# ─── 1. signal write / read round-trip ───────────────────────────────


def test_write_and_read_approved(tmp_path):
    write_approval_signal(audit_dir=tmp_path, exec_id="EXEC-x", response="approved")
    assert read_and_clear_approval(audit_dir=tmp_path, exec_id="EXEC-x") == "approved"


def test_write_and_read_rejected(tmp_path):
    write_approval_signal(audit_dir=tmp_path, exec_id="EXEC-x", response="rejected")
    assert read_and_clear_approval(audit_dir=tmp_path, exec_id="EXEC-x") == "rejected"


def test_signal_consumed_after_read(tmp_path):
    write_approval_signal(audit_dir=tmp_path, exec_id="EXEC-x", response="approved")
    read_and_clear_approval(audit_dir=tmp_path, exec_id="EXEC-x")
    # Second read returns None — signal was consumed
    assert read_and_clear_approval(audit_dir=tmp_path, exec_id="EXEC-x") is None


def test_no_signal_returns_none(tmp_path):
    assert read_and_clear_approval(audit_dir=tmp_path, exec_id="EXEC-empty") is None


def test_invalid_response_raises(tmp_path):
    with pytest.raises(SkillExecutorError):
        write_approval_signal(audit_dir=tmp_path, exec_id="EXEC-x", response="maybe")


def test_signal_path_lives_under_audit_dir(tmp_path):
    p = approval_signal_path(audit_dir=tmp_path, exec_id="EXEC-foo")
    assert p == tmp_path / "EXEC-foo.approval"


def test_atomic_write_no_tmp_left_behind(tmp_path):
    write_approval_signal(audit_dir=tmp_path, exec_id="EXEC-x", response="approved")
    tmps = list(tmp_path.glob("*.approval.tmp"))
    assert tmps == []


def test_corrupt_signal_returns_none(tmp_path):
    """A signal file with garbage content (not 'approved'/'rejected')
    should be ignored, not propagate as a fake approval."""
    sig = approval_signal_path(audit_dir=tmp_path, exec_id="EXEC-x")
    sig.write_text("totally-bogus-content", encoding="utf-8")
    assert read_and_clear_approval(audit_dir=tmp_path, exec_id="EXEC-x") is None


# ─── 2. WorkbenchApprovalCallback — happy paths ─────────────────────


def test_callback_returns_approved_on_signal(tmp_path):
    """Pre-write the signal so the very first poll picks it up."""
    record = _stub_record()
    write_approval_signal(audit_dir=tmp_path, exec_id=record.exec_id, response="approved")
    callback = WorkbenchApprovalCallback(audit_dir=tmp_path)
    response = callback(record, Ask(ask_id="ASK-1", question="approve?"))
    assert response == AskResponse.APPROVED


def test_callback_returns_rejected_on_signal(tmp_path):
    record = _stub_record()
    write_approval_signal(audit_dir=tmp_path, exec_id=record.exec_id, response="rejected")
    callback = WorkbenchApprovalCallback(audit_dir=tmp_path)
    response = callback(record, Ask(ask_id="ASK-1", question="?"))
    assert response == AskResponse.REJECTED


def test_callback_polls_and_consumes(tmp_path):
    """Signal arrives mid-polling. Use a fake clock so the test
    doesn't actually sleep."""
    record = _stub_record()
    sleeps: list[float] = []

    def fake_sleep(t):
        sleeps.append(t)
        # On the third sleep, write the signal — the next poll
        # will see it.
        if len(sleeps) == 2:
            write_approval_signal(
                audit_dir=tmp_path, exec_id=record.exec_id, response="approved"
            )

    callback = WorkbenchApprovalCallback(
        audit_dir=tmp_path,
        poll_interval_sec=0.5,
        timeout_sec=999,
        sleep=fake_sleep,
    )
    result = callback(record, Ask(ask_id="ASK-1", question="?"))
    assert result == AskResponse.APPROVED
    # We slept at least twice before the signal arrived
    assert len(sleeps) >= 2


def test_callback_consumes_signal_so_next_run_doesnt_reuse(tmp_path):
    """Once approved, the signal file is gone — a subsequent run
    of the same exec_id (replay scenario) shouldn't see a stale
    'approved'."""
    record = _stub_record()
    write_approval_signal(audit_dir=tmp_path, exec_id=record.exec_id, response="approved")
    callback = WorkbenchApprovalCallback(audit_dir=tmp_path)
    callback(record, Ask(ask_id="ASK-1", question="?"))
    # Verify the file is gone
    assert not approval_signal_path(audit_dir=tmp_path, exec_id=record.exec_id).is_file()


# ─── 3. Timeout ───────────────────────────────────────────────────────


def test_callback_raises_on_timeout(tmp_path):
    record = _stub_record()
    times = iter([0.0, 100.0, 200.0])

    callback = WorkbenchApprovalCallback(
        audit_dir=tmp_path,
        poll_interval_sec=10.0,
        timeout_sec=50.0,
        sleep=lambda t: None,
        now=lambda: next(times, 999.0),
    )
    with pytest.raises(ApprovalTimeoutError) as exc:
        callback(record, Ask(ask_id="ASK-1", question="?"))
    assert record.exec_id in str(exc.value)


# ─── 4. Concurrent simulation: writer + poller in threads ────────────


def test_callback_handles_concurrent_signal_write(tmp_path):
    """Realistic scenario: poller is running while a separate
    'workbench thread' writes the signal. Verify the poller picks
    it up without losing the response to a race."""
    record = _stub_record()

    def writer():
        time.sleep(0.05)
        write_approval_signal(
            audit_dir=tmp_path, exec_id=record.exec_id, response="approved"
        )

    threading.Thread(target=writer, daemon=True).start()

    callback = WorkbenchApprovalCallback(
        audit_dir=tmp_path,
        poll_interval_sec=0.02,
        timeout_sec=2.0,
    )
    response = callback(record, Ask(ask_id="ASK-1", question="?"))
    assert response == AskResponse.APPROVED
