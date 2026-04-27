"""P50-02a — GET /api/skill-executions/metrics endpoint.

Locks down the HTTP wire-up: list_audits → compute_metrics →
JSON. Verifies empty-state, populated-state, and that the
endpoint reflects audits added at runtime (no stale caching).
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


def _make_audit(
    exec_id: str,
    *,
    proposal_id: str = "PROP-test",
    state: str = ExecutionState.LANDED.value,
    started_at: str = "2026-04-27T12:00:00Z",
    finished_at: str = "2026-04-27T12:01:00Z",
    abort_reason: str = "",
    audit_source: AuditSource = AuditSource.LIVE,
    kind: ExecutionKind = ExecutionKind.MODIFY,
) -> ExecutionRecord:
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=kind,
        audit_source=audit_source,
        started_at=started_at,
        finished_at=finished_at,
        state=state,
        executor_version="0.1-test",
        abort_reason=abort_reason,
        plan=PlannedChange(rationale="test", file_edits=[]),
    )
    write_audit(rec)
    return rec


# ─── 1. Empty input → all-zero metrics ──────────────────────────────


def test_metrics_endpoint_returns_200_with_empty_metrics(server):
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert body["total"] == 0
    assert body["pass_rate"] == 0.0
    assert body["completed_count"] == 0
    assert body["recent_failures"] == []
    # Must include all 9 state buckets even with zero data
    for state in [
        "INIT", "PLANNING", "ASKING", "EDITING", "TESTING",
        "PR_OPEN", "LANDED", "ABORTED", "FAILED",
    ]:
        assert state in body["by_state"]
        assert body["by_state"][state] == 0


# ─── 2. Populated audits → reflected in metrics ─────────────────────


def test_metrics_endpoint_reflects_audits(server):
    _make_audit("EXEC-20260427T120000000001-aaaaaa", state="LANDED")
    _make_audit("EXEC-20260427T120000000002-aaaaaa", state="LANDED")
    _make_audit("EXEC-20260427T120000000003-aaaaaa", state="FAILED",
                abort_reason="planner crashed")
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert body["total"] == 3
    assert body["by_state"]["LANDED"] == 2
    assert body["by_state"]["FAILED"] == 1
    # 2 LANDED out of 3 → 0.666...
    assert abs(body["pass_rate"] - (2 / 3)) < 0.001


# ─── 3. Endpoint sees audits added at runtime ──────────────────────


def test_metrics_endpoint_picks_up_new_audits_without_restart(server):
    """Each call re-reads list_audits — no in-memory cache."""
    s1, body1 = _get(server, "/api/skill-executions/metrics")
    assert body1["total"] == 0

    _make_audit("EXEC-20260427T120000000001-aaaaaa", state="LANDED")

    s2, body2 = _get(server, "/api/skill-executions/metrics")
    assert body2["total"] == 1


# ─── 4. Recent failures populated correctly ────────────────────────


def test_recent_failures_carry_abort_reason(server):
    _make_audit("EXEC-20260427T120000000001-aaaaaa", state="LANDED")
    _make_audit(
        "EXEC-20260427T120000000002-aaaaaa",
        state="ABORTED",
        abort_reason="cancelled by Kogami",
    )
    _make_audit(
        "EXEC-20260427T120000000003-aaaaaa",
        state="FAILED",
        abort_reason="planner: minimax 503",
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert len(body["recent_failures"]) == 2
    reasons = [f["abort_reason"] for f in body["recent_failures"]]
    assert "cancelled by Kogami" in reasons
    assert "planner: minimax 503" in reasons


# ─── 5. Duration computed from started/finished pair ──────────────


def test_duration_summary_present_when_completed(server):
    _make_audit(
        "EXEC-20260427T120000000001-aaaaaa",
        state="LANDED",
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:01:30Z",  # 90s
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert body["completed_count"] == 1
    assert body["median_duration_sec"] == 90.0
    assert body["p95_duration_sec"] == 90.0


# ─── 6. Backfill counter ──────────────────────────────────────────


def test_backfill_count_present(server):
    _make_audit(
        "EXEC-20260427T120000000001-aaaaaa",
        state="LANDED",
        audit_source=AuditSource.BACKFILL,
        kind=ExecutionKind.BACKFILL,
    )
    _make_audit(
        "EXEC-20260427T120000000002-aaaaaa",
        state="LANDED",
        audit_source=AuditSource.LIVE,
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert body["backfill_count"] == 1


# ─── 7. Top-level shape stable ────────────────────────────────────


def test_metrics_endpoint_returns_stable_top_level_keys(server):
    """Lock down the JSON contract the frontend will rely on."""
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    expected = {
        "total", "by_state", "pass_rate", "completed_count",
        "median_duration_sec", "p95_duration_sec",
        "recent_failures", "backfill_count",
    }
    assert set(body.keys()) == expected
