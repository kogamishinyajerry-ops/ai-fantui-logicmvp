"""P50-02c — per-proposal phase-timings HTTP endpoints.

Locks down:
  /execution             → audit + phase_timings sidecar
  /execution/timings     → just the timings (lightweight tooltip)

Both share the same lookup; the timings-only variant lets the
inbox tooltip fetch only what it needs without pulling the full
plan + events log.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor.audit import write_audit
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionEvent,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.states import ExecutionState


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


def _get(server, path):
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1]
    )
    conn.request("GET", path)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8") if resp.length is not None else ""
    conn.close()
    if not raw:
        return resp.status, None
    try:
        return resp.status, json.loads(raw)
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _trans(at: str, from_state: str, to_state: str) -> ExecutionEvent:
    return ExecutionEvent(
        at=at, kind="state_transition",
        from_state=from_state, to_state=to_state,
    )


def _make_audit_with_timings(
    proposal_id: str = "PROP-test",
) -> ExecutionRecord:
    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000000001-aaaaaa",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:30:00Z",
        state=ExecutionState.PR_OPEN.value,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
        events=[
            _trans("2026-04-27T12:00:05Z", "INIT", "PLANNING"),
            _trans("2026-04-27T12:00:15Z", "PLANNING", "ASKING"),
            _trans("2026-04-27T12:25:15Z", "ASKING", "EDITING"),
            _trans("2026-04-27T12:25:20Z", "EDITING", "TESTING"),
            _trans("2026-04-27T12:25:30Z", "TESTING", "PR_OPEN"),
        ],
    )
    write_audit(rec)
    return rec


# ─── 1. Full audit response now carries phase_timings sidecar ────


def test_execution_endpoint_includes_phase_timings_sidecar(server):
    _make_audit_with_timings()
    status, body = _get(server, "/api/proposals/PROP-test/execution")
    assert status == 200
    # Original audit fields still present
    assert body["state"] == "PR_OPEN"
    assert body["proposal_id"] == "PROP-test"
    # New phase_timings block
    assert "phase_timings" in body
    pt = body["phase_timings"]
    assert "timings" in pt
    assert "current_phase" in pt
    assert pt["current_phase"] == "PR_OPEN"


def test_phase_timings_in_execution_response_correct():
    rec = _make_audit_with_timings()
    # Query through the server
    srv = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    try:
        _, body = _get(srv, "/api/proposals/PROP-test/execution")
        timings = {t["phase"]: t for t in body["phase_timings"]["timings"]}
        # Spot-check ASKING is the longest phase (25 min)
        assert timings["ASKING"]["duration_sec"] == 1500.0
        assert timings["INIT"]["duration_sec"] == 5.0
    finally:
        srv.shutdown()
        srv.server_close()


# ─── 2. /timings sub-route — just the timings ────────────────────


def test_timings_only_endpoint_returns_timings_block(server):
    _make_audit_with_timings()
    status, body = _get(
        server, "/api/proposals/PROP-test/execution/timings"
    )
    assert status == 200
    # Top-level keys are the timings block, NOT the wrapped audit
    assert set(body.keys()) == {
        "timings", "current_phase", "total_duration_sec"
    }


def test_timings_only_no_audit_returns_204(server):
    status, body = _get(
        server, "/api/proposals/PROP-no-exec/execution/timings"
    )
    assert status == 204
    assert body is None


# ─── 3. Robustness — different states ───────────────────────────


def test_in_flight_audit_returns_partial_timings(server):
    """ASKING-state audit (still in flight) — current phase has
    None duration but earlier phases have real durations."""
    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000000002-aaaaaa",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-inflight",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        finished_at="",  # in flight
        state=ExecutionState.ASKING.value,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
        events=[
            _trans("2026-04-27T12:00:05Z", "INIT", "PLANNING"),
            _trans("2026-04-27T12:00:15Z", "PLANNING", "ASKING"),
        ],
    )
    write_audit(rec)
    status, body = _get(
        server, "/api/proposals/PROP-inflight/execution/timings"
    )
    assert status == 200
    timings = {t["phase"]: t for t in body["timings"]}
    assert timings["INIT"]["duration_sec"] == 5.0
    assert timings["PLANNING"]["duration_sec"] == 10.0
    # ASKING still in progress
    assert timings["ASKING"]["duration_sec"] is None
    assert body["current_phase"] == "ASKING"
    assert body["total_duration_sec"] is None


# ─── 4. Empty proposal id rejected ────────────────────────────


def test_timings_endpoint_rejects_empty_proposal_id(server):
    status, body = _get(server, "/api/proposals//execution/timings")
    assert status == 400
    assert body["error"] == "invalid_proposal_id"


# ─── 5. Original /execution endpoint behavior unchanged ─────


def test_execution_endpoint_still_returns_204_when_no_audit(server):
    status, body = _get(server, "/api/proposals/PROP-no-exec/execution")
    assert status == 204
    assert body is None


def test_execution_endpoint_top_level_keys_include_phase_timings(server):
    _make_audit_with_timings()
    status, body = _get(server, "/api/proposals/PROP-test/execution")
    assert "phase_timings" in body
    # Ensure existing audit keys still there (smoke)
    assert "exec_id" in body
    assert "state" in body
    assert "events" in body
