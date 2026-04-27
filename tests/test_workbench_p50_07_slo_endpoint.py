"""P50-07 — GET /api/skill-executions/metrics surfaces SLO verdict.

Locks down the HTTP wire-up of the SLO field: the endpoint must
return a `slo_status` block with the same shape regardless of
empty / healthy / breaching audit datasets so the frontend can
render its color-coded indicator without conditional shape checks.
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


def _audit(exec_id, *, state, **kw):
    write_audit(
        ExecutionRecord(
            exec_id=exec_id,
            schema_version=AUDIT_SCHEMA_VERSION,
            proposal_id=kw.get("proposal_id", "PROP-x"),
            kind=ExecutionKind.MODIFY,
            audit_source=AuditSource.LIVE,
            started_at=kw.get("started_at", "2026-04-27T12:00:00Z"),
            finished_at=kw.get("finished_at", "2026-04-27T12:01:00Z"),
            state=state,
            executor_version="0.1-test",
            abort_reason=kw.get("abort_reason", ""),
            plan=PlannedChange(rationale="x", file_edits=[]),
        )
    )


# ─── 1. Empty audit dir → NO_DATA verdict ──────────────────────────


def test_empty_audits_returns_no_data_verdict(server):
    """No audits on disk → SLO returns NO_DATA, never GREEN."""
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    slo = body["slo_status"]
    assert slo["overall"] == "no_data"
    assert slo["breaches"] == []
    # Thresholds always present so the dashboard can show what
    # would have triggered an alert
    assert "pass_rate_yellow" in slo["thresholds"]


# ─── 2. Healthy dataset → GREEN ────────────────────────────────────


def test_healthy_dataset_returns_green(server):
    """6 LANDED audits = 100% pass rate, 0 failures → GREEN."""
    for i in range(6):
        _audit(
            f"EXEC-2026042{i}T120000000000-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    slo = body["slo_status"]
    assert slo["overall"] == "green"
    assert slo["breaches"] == []


# ─── 3. Breaching dataset → RED + breach detail ───────────────────


def test_breaching_dataset_returns_red_with_breaches(server):
    """High failure rate trips both SLOs. The endpoint exposes a
    breach list the dashboard can iterate over for an expanded view."""
    # 7 FAILED + 3 LANDED = 30% pass_rate (RED), 7 failures (RED)
    for i in range(7):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.FAILED.value,
            abort_reason=f"planner: error {i}",
        )
    for i in range(3):
        _audit(
            f"EXEC-20260427T12000100{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    slo = body["slo_status"]
    assert slo["overall"] == "red"
    breach_slos = {b["slo"] for b in slo["breaches"]}
    assert breach_slos == {"pass_rate", "active_failures_count"}
    # Each breach has actionable fields
    for breach in slo["breaches"]:
        assert breach["severity"] in {"yellow", "red"}
        assert "actual" in breach
        assert "threshold" in breach
        assert breach["note"]  # non-empty note


# ─── 4. Sparse dataset → NO_DATA, not GREEN ────────────────────────


def test_sparse_dataset_below_min_data_points(server):
    """4 audits is below default min_data_points=5 → NO_DATA even
    if every run failed. Avoids a false alarm on a fresh deploy."""
    for i in range(4):
        _audit(
            f"EXEC-2026042{i}T120000000000-cccccc",
            state=ExecutionState.FAILED.value,
            abort_reason="planner: 503",
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert body["slo_status"]["overall"] == "no_data"


# ─── 5. JSON shape stability ──────────────────────────────────────


def test_slo_status_json_shape_stable(server):
    """slo_status is always the same shape — empty or populated.
    Frontend doesn't have to branch on key presence."""
    # First check: empty
    _, body = _get(server, "/api/skill-executions/metrics")
    assert set(body["slo_status"].keys()) == {
        "overall", "breaches", "thresholds",
    }
    # Then populate
    for i in range(5):
        _audit(
            f"EXEC-2026042{i}T120000000000-dddddd",
            state=ExecutionState.LANDED.value,
        )
    _, body2 = _get(server, "/api/skill-executions/metrics")
    assert set(body2["slo_status"].keys()) == {
        "overall", "breaches", "thresholds",
    }
