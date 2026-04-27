"""P49-01c — POST /api/skill-executions/<exec_id>/cancel.

Locks down: the cancel endpoint accepts an HTTP POST, writes a
cancel signal file the orchestrator picks up at its next phase
boundary, and surfaces clear error states (404 missing, 409
terminal) so the workbench UI can render correct feedback.
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
from well_harness.skill_executor.workbench_polling import cancel_signal_path


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"),
    )
    monkeypatch.setenv(
        "WORKBENCH_PROPOSALS_DIR", str(tmp_path / "proposals"),
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
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    payload = json.dumps(body) if body is not None else ""
    headers = {"Content-Type": "application/json"} if body is not None else {}
    conn.request("POST", path, body=payload, headers=headers)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8") if resp.length is not None else ""
    conn.close()
    if not raw:
        return resp.status, None
    try:
        return resp.status, json.loads(raw)
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _make_audit(
    exec_id: str,
    *,
    state: str = ExecutionState.PLANNING.value,
    proposal_id: str = "PROP-test",
) -> ExecutionRecord:
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T13:00:00Z",
        finished_at="",
        state=state,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
    )
    write_audit(rec)
    return rec


# ─── 1. Happy path — cancel a PLANNING audit ────────────────────────


def test_cancel_writes_signal_and_returns_202(server, tmp_path):
    audit = _make_audit("EXEC-20260427T120000000001-aaaaaa")
    status, body = _post(
        server,
        f"/api/skill-executions/{audit.exec_id}/cancel",
        {"actor": "Kogami", "note": "stuck on minimax"},
    )
    assert status == 202
    assert body["exec_id"] == audit.exec_id
    assert body["action"] == "cancel"
    assert body["actor"] == "Kogami"
    assert body["note"] == "stuck on minimax"
    assert body["current_state"] == "PLANNING"
    # Signal file was written
    target = cancel_signal_path(
        audit_dir=tmp_path / "execs", exec_id=audit.exec_id
    )
    assert target.is_file()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["actor"] == "Kogami"
    assert payload["note"] == "stuck on minimax"


# ─── 2. Cancel works for every non-terminal state ─────────────────


@pytest.mark.parametrize(
    "idx,state",
    [
        (1, "PLANNING"),
        (2, "ASKING"),
        (3, "EDITING"),
        (4, "TESTING"),
        (5, "PR_OPEN"),
    ],
)
def test_cancel_works_for_all_non_terminal_states(server, idx, state):
    """Cancel must be valid in every non-terminal state — that's
    its whole point. Compare to /reject which only works in ASKING."""
    audit = _make_audit(
        f"EXEC-20260427T12000000000{idx}-aaaaaa", state=state,
    )
    status, body = _post(
        server,
        f"/api/skill-executions/{audit.exec_id}/cancel",
        {"actor": "x"},
    )
    assert status == 202, f"failed for state={state}: {body}"
    assert body["current_state"] == state


# ─── 3. Cancel rejected in terminal states ─────────────────────────


@pytest.mark.parametrize(
    "idx,state", [(6, "LANDED"), (7, "ABORTED"), (8, "FAILED")],
)
def test_cancel_rejected_in_terminal_states_with_409(server, idx, state):
    audit = _make_audit(
        f"EXEC-20260427T12000000000{idx}-aaaaaa", state=state,
    )
    status, body = _post(
        server,
        f"/api/skill-executions/{audit.exec_id}/cancel",
        {"actor": "x"},
    )
    assert status == 409
    assert body["error"] == "execution_already_terminal"
    assert body["current_state"] == state


# ─── 4. Cancel for missing exec returns 404 ────────────────────────


def test_cancel_missing_audit_returns_404(server):
    status, body = _post(
        server,
        "/api/skill-executions/EXEC-20260427T120000000000-deadbe/cancel",
        {"actor": "x"},
    )
    assert status == 404
    assert body["error"] == "audit_not_found"


def test_cancel_invalid_exec_id_returns_404(server):
    """The schema validator rejects malformed exec_ids; surface as
    404 (caller's path is wrong, not their JSON)."""
    status, body = _post(
        server,
        "/api/skill-executions/EXEC-bogus/cancel",
        {"actor": "x"},
    )
    assert status == 404


# ─── 5. Body parsing ──────────────────────────────────────────────


def test_cancel_without_body_uses_anonymous_actor(server, tmp_path):
    audit = _make_audit("EXEC-20260427T120000000009-aaaaaa")
    status, body = _post(
        server, f"/api/skill-executions/{audit.exec_id}/cancel"
    )
    assert status == 202
    assert body["actor"] == "anonymous"


def test_cancel_with_invalid_json_returns_400(server):
    audit = _make_audit("EXEC-20260427T120000000010-aaaaaa")
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    conn.request(
        "POST",
        f"/api/skill-executions/{audit.exec_id}/cancel",
        body="not json {",
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    assert resp.status == 400
    assert json.loads(raw)["error"] == "invalid_json"


def test_cancel_with_oversized_body_returns_400(server):
    audit = _make_audit("EXEC-20260427T120000000011-aaaaaa")
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    payload = "x" * 60_000
    conn.request(
        "POST",
        f"/api/skill-executions/{audit.exec_id}/cancel",
        body=payload,
        headers={"Content-Type": "application/json"},
    )
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    assert resp.status == 400
    assert json.loads(raw)["error"] == "oversized_body"


# ─── 6. Approve/reject still work post-merge ──────────────────────


def test_approve_endpoint_still_works(server):
    """Sanity check: P48-06 approval flow isn't broken by adding
    cancel. Cancel and approve dispatch on different suffix ends
    of the same path so the routing must still split correctly."""
    audit = _make_audit("EXEC-20260427T120000000012-aaaaaa", state="ASKING")
    status, body = _post(
        server,
        f"/api/skill-executions/{audit.exec_id}/approve",
        {"actor": "x"},
    )
    assert status == 202
    assert body["action"] == "approve"
