"""P49-02b — governance approve/reject HTTP bridge tests.

Locks down the wire-up: POST writes the right signal file, 404
when no audit, 409 when audit isn't in GOVERNANCE_HOLD, and the
file contents (actor / note / timestamp) round-trip correctly so
the orchestrator's poller can consume them.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.states import ExecutionState
from well_harness.skill_executor.workbench_polling import (
    governance_approval_path,
    governance_reject_path,
)


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"),
    )
    yield


@pytest.fixture
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        yield srv
    finally:
        srv.shutdown()
        srv.server_close()


def _post(server, path, body=None):
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    headers = {"Content-Type": "application/json"}
    raw = json.dumps(body or {}).encode("utf-8")
    conn.request("POST", path, body=raw, headers=headers)
    resp = conn.getresponse()
    text = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(text) if text else None


def _audit(exec_id, *, state):
    write_audit(
        ExecutionRecord(
            exec_id=exec_id,
            schema_version=AUDIT_SCHEMA_VERSION,
            proposal_id="PROP-x",
            kind=ExecutionKind.MODIFY,
            audit_source=AuditSource.LIVE,
            started_at="2026-04-27T12:00:00Z",
            finished_at="",
            state=state,
            executor_version="0.1-test",
            plan=PlannedChange(rationale="x", file_edits=[]),
        )
    )


# ─── 1. Approve writes the signal file ────────────────────────────


def test_approve_writes_signal(server, tmp_path):
    exec_id = "EXEC-20260427T120000000000-aaaaaa"
    _audit(exec_id, state=ExecutionState.GOVERNANCE_HOLD.value)
    status, body = _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-approve",
        {"actor": "test-reviewer", "note": "verified"},
    )
    assert status == 202
    assert body["action"] == "governance-approve"
    assert body["actor"] == "test-reviewer"
    audit_root = tmp_path / "execs"
    sig = governance_approval_path(audit_dir=audit_root, exec_id=exec_id)
    assert sig.is_file()
    payload = json.loads(sig.read_text(encoding="utf-8"))
    assert payload["actor"] == "test-reviewer"
    assert payload["note"] == "verified"
    assert "at" in payload


# ─── 2. Reject writes the reject file ─────────────────────────────


def test_reject_writes_signal(server, tmp_path):
    exec_id = "EXEC-20260427T120000000001-bbbbbb"
    _audit(exec_id, state=ExecutionState.GOVERNANCE_HOLD.value)
    status, body = _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-reject",
        {"actor": "test-reviewer", "note": "policy violation"},
    )
    assert status == 202
    assert body["action"] == "governance-reject"
    audit_root = tmp_path / "execs"
    sig = governance_reject_path(audit_dir=audit_root, exec_id=exec_id)
    assert sig.is_file()
    # Approval signal file should NOT exist (separate file)
    assert not governance_approval_path(
        audit_dir=audit_root, exec_id=exec_id,
    ).is_file()


# ─── 3. Empty body → defaults to anonymous ───────────────────────


def test_empty_body_defaults_to_anonymous(server, tmp_path):
    """A reviewer hitting the button without an actor identity
    still gets through — actor defaults to 'anonymous'."""
    exec_id = "EXEC-20260427T120000000002-cccccc"
    _audit(exec_id, state=ExecutionState.GOVERNANCE_HOLD.value)
    status, body = _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-approve",
        {},
    )
    assert status == 202
    assert body["actor"] == "anonymous"


# ─── 4. 404 when no audit ─────────────────────────────────────────


def test_unknown_exec_id_returns_404(server):
    status, body = _post(
        server,
        "/api/skill-executions/EXEC-20260427T120000000099-zzzzzz/governance-approve",
        {"actor": "x"},
    )
    assert status == 404
    assert body["error"] == "audit_not_found"


def test_malformed_exec_id_returns_404(server):
    """An exec_id that doesn't match the regex shape is rejected
    by read_audit before any signal file is touched."""
    status, body = _post(
        server,
        "/api/skill-executions/not-a-real-exec-id/governance-approve",
        {"actor": "x"},
    )
    assert status == 404


# ─── 5. 409 when audit isn't in GOVERNANCE_HOLD ──────────────────


def test_409_when_in_asking_state(server):
    """Trying to govern-approve a run that's already past the gate
    (or never hit it) is a state mismatch — surface 409 instead of
    silently writing a signal file no one will read."""
    exec_id = "EXEC-20260427T120000000003-dddddd"
    _audit(exec_id, state=ExecutionState.ASKING.value)
    status, body = _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-approve",
        {"actor": "x"},
    )
    assert status == 409
    assert body["error"] == "not_in_governance_hold"
    assert body["current_state"] == "ASKING"


def test_409_when_terminal(server):
    """Same logic for terminal states — no point writing a signal
    that'll never fire."""
    exec_id = "EXEC-20260427T120000000004-eeeeee"
    _audit(exec_id, state=ExecutionState.LANDED.value)
    status, _ = _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-reject",
        {"actor": "x"},
    )
    assert status == 409


# ─── 6. Malformed body → 400 ──────────────────────────────────────


def test_invalid_json_body_returns_400(server):
    """Garbled body content doesn't crash the handler; the
    bridge returns a clean 400."""
    exec_id = "EXEC-20260427T120000000005-ffffff"
    _audit(exec_id, state=ExecutionState.GOVERNANCE_HOLD.value)
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    conn.request(
        "POST",
        f"/api/skill-executions/{exec_id}/governance-approve",
        body=b"this is not json {",
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    text = resp.read().decode("utf-8")
    conn.close()
    assert resp.status == 400
    assert json.loads(text)["error"] == "invalid_json"


def test_oversized_body_returns_400(server):
    """50KB cap on the bridge — operators wouldn't send anything
    that large for an actor + note."""
    exec_id = "EXEC-20260427T120000000006-aaaa11"
    _audit(exec_id, state=ExecutionState.GOVERNANCE_HOLD.value)
    huge_body = json.dumps({
        "actor": "x", "note": "a" * 60_000,
    }).encode("utf-8")
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    conn.request(
        "POST",
        f"/api/skill-executions/{exec_id}/governance-approve",
        body=huge_body,
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    text = resp.read().decode("utf-8")
    conn.close()
    assert resp.status == 400


# ─── 7. Distinct files: approve and reject don't clobber each ────


def test_approve_and_reject_use_separate_files(server, tmp_path):
    """If a reviewer accidentally hits both buttons quickly,
    each lands in its own file. The orchestrator's
    read_and_clear_governance prefers reject (safer default)."""
    exec_id = "EXEC-20260427T120000000007-bbbb22"
    _audit(exec_id, state=ExecutionState.GOVERNANCE_HOLD.value)
    _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-approve",
        {"actor": "x"},
    )
    _post(
        server,
        f"/api/skill-executions/{exec_id}/governance-reject",
        {"actor": "y"},
    )
    audit_root = tmp_path / "execs"
    assert governance_approval_path(
        audit_dir=audit_root, exec_id=exec_id,
    ).is_file()
    assert governance_reject_path(
        audit_dir=audit_root, exec_id=exec_id,
    ).is_file()
