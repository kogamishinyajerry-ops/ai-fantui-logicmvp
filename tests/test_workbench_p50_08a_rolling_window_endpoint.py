"""P50-08a — endpoint surfaces rolling-window pass_rate + SLO.

Locks down: GET /api/skill-executions/metrics returns the
`recent_window` block and the SLO chip flips RED when the freshest
runs degrade even though lifetime is healthy. This is the wire-up
test for the end-to-end rolling-window scenario.
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
    raw = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(raw) if raw else None


def _audit(exec_id, *, state, started_at="2026-04-27T12:00:00Z"):
    write_audit(
        ExecutionRecord(
            exec_id=exec_id,
            schema_version=AUDIT_SCHEMA_VERSION,
            proposal_id="PROP-x",
            kind=ExecutionKind.MODIFY,
            audit_source=AuditSource.LIVE,
            started_at=started_at,
            finished_at="2026-04-27T12:01:00Z",
            state=state,
            executor_version="0.1-test",
            plan=PlannedChange(rationale="x", file_edits=[]),
        )
    )


# ─── 1. recent_window block always present ────────────────────────


def test_endpoint_emits_recent_window_block_when_empty(server):
    """No audits → recent_window block present, all-zero/null. The
    frontend doesn't have to special-case the empty state."""
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert "recent_window" in body
    rw = body["recent_window"]
    assert set(rw.keys()) == {
        "pass_rate_recent", "window_size", "passing", "total",
    }
    assert rw["pass_rate_recent"] is None


def test_endpoint_emits_recent_window_when_under_window(server):
    """Below window_size → pass_rate_recent stays null but the
    block shape is unchanged."""
    for i in range(5):
        _audit(
            f"EXEC-2026042{i}T120000000000-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
    _, body = _get(server, "/api/skill-executions/metrics")
    rw = body["recent_window"]
    assert rw["pass_rate_recent"] is None
    assert rw["total"] == 0  # under-windowed → not evaluated


# ─── 2. recent regression with healthy lifetime → RED ────────────


def test_recent_regression_flips_slo_red(server):
    """30 LANDED (oldest) + 20 FAILED (newest) → lifetime 60% (yellow)
    but recent 0% (red) → overall RED with pass_rate_recent breach."""
    # Older successes — exec_id timestamp earlier so they sort to tail
    for i in range(30):
        _audit(
            f"EXEC-20260427T0{i:011d}-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
    # Newer failures — later timestamp → head of list_audits()
    for i in range(20):
        _audit(
            f"EXEC-20260427T9{i:011d}-bbbbbb",
            state=ExecutionState.FAILED.value,
            started_at="2026-04-27T15:00:00Z",
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    slo = body["slo_status"]
    # Recent 20 are all FAILED → 0% pass_rate_recent → RED
    breach_slos = {b["slo"] for b in slo["breaches"]}
    assert "pass_rate_recent" in breach_slos
    assert slo["overall"] == "red"
    # The recent breach note should mention the window size so an
    # operator understands "20 runs", not "lifetime"
    recent_breach = next(
        b for b in slo["breaches"] if b["slo"] == "pass_rate_recent"
    )
    assert "20" in recent_breach["note"]


def test_recent_recovery_does_not_flip_lifetime_red(server):
    """20 newest LANDED + 30 oldest FAILED → recent 100% but
    lifetime still 40% (RED). The SLO must stay RED on lifetime
    even though recent is healthy — recovery is in progress, not
    complete."""
    for i in range(30):
        _audit(
            f"EXEC-20260427T0{i:011d}-aaaaaa",
            state=ExecutionState.FAILED.value,
        )
    for i in range(20):
        _audit(
            f"EXEC-20260427T9{i:011d}-bbbbbb",
            state=ExecutionState.LANDED.value,
            started_at="2026-04-27T15:00:00Z",
        )
    _, body = _get(server, "/api/skill-executions/metrics")
    slo = body["slo_status"]
    assert slo["overall"] == "red"
    breach_slos = {b["slo"] for b in slo["breaches"]}
    assert "pass_rate" in breach_slos  # lifetime breach
    assert "pass_rate_recent" not in breach_slos  # recent is fine
