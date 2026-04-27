"""P50-08b — SLO history endpoint + side-effect recording.

Locks down: GET /api/skill-executions/metrics records a
transition when the verdict changes; GET /api/skill-executions/
slo-history returns the timeline; steady-state polls don't bloat
the log.
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
from well_harness.skill_executor.slo_history import history_path
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


# ─── 1. Empty audit dir → empty history endpoint ───────────────────


def test_history_empty_when_no_polls(server):
    """Fresh deploy, history endpoint hit before metrics endpoint."""
    status, body = _get(server, "/api/skill-executions/slo-history")
    assert status == 200
    assert body == {"transitions": [], "count": 0}


# ─── 2. Metrics endpoint records first transition ─────────────────


def test_metrics_endpoint_records_first_red(server, tmp_path):
    """Hit /metrics with a dataset that should be RED.
    /slo-history must show one transition: none → red."""
    # 6 FAILED → above min_data_points + RED pass_rate
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.FAILED.value,
        )
    s1, b1 = _get(server, "/api/skill-executions/metrics")
    assert s1 == 200
    assert b1["slo_status"]["overall"] == "red"

    s2, b2 = _get(server, "/api/skill-executions/slo-history")
    assert s2 == 200
    assert b2["count"] == 1
    t = b2["transitions"][0]
    assert t["from_severity"] == "none"
    assert t["to_severity"] == "red"
    # Snapshot captures the lifetime numbers
    assert t["snapshot"]["total"] == 6
    assert t["snapshot"]["failed_count"] == 6


def test_first_green_is_silent(server):
    """A clean dataset on first poll → no log entry. Only real
    'something changed' moments belong on the timeline."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
    s1, b1 = _get(server, "/api/skill-executions/metrics")
    assert b1["slo_status"]["overall"] == "green"
    s2, b2 = _get(server, "/api/skill-executions/slo-history")
    assert b2["count"] == 0


# ─── 3. Steady-state polls don't bloat the log ─────────────────────


def test_repeat_polls_no_extra_entries(server):
    """Same RED state polled five times → still one entry."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.FAILED.value,
        )
    for _ in range(5):
        _get(server, "/api/skill-executions/metrics")
    _, body = _get(server, "/api/skill-executions/slo-history")
    assert body["count"] == 1


# ─── 4. Real GREEN ↔ RED transitions captured ──────────────────────


def test_recovery_logged(server, tmp_path):
    """Start ABORTED (drops lifetime pass_rate, no FAILED-count
    breach) → poll records RED. Add LANDED audits → pass_rate
    recovers above 70% → poll again, GREEN. Timeline shows both.

    Why ABORTED not FAILED: FAILED also trips the
    active_failures_count SLO which stays RED forever (we can't
    remove audits to bring it back below 3). ABORTED counts as
    non-pass for pass_rate but doesn't pollute the failure count,
    so a recovery is achievable in-test."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # records: → red

    # Recovery: lots of successes brings pass rate up
    for i in range(20):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # records: red → green

    _, body = _get(server, "/api/skill-executions/slo-history")
    assert body["count"] == 2
    seq = [t["to_severity"] for t in body["transitions"]]
    assert seq == ["red", "green"]
    assert body["transitions"][1]["from_severity"] == "red"


# ─── 5. limit query param ─────────────────────────────────────────


def test_history_limit_returns_tail(server):
    """?limit=N returns at most N transitions, newest-last."""
    # Force three transitions: red → green → red.
    # Use ABORTED for non-passing audits so we can flip back to
    # GREEN by adding enough LANDED to lift the lifetime pass_rate
    # over 70% (FAILED-state count would stay RED forever).
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # red (pass_rate=0)
    for i in range(20):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # green
    # 60 more aborted → pass_rate = 20 / (6+20+60) = 23% → RED
    for i in range(60):
        _audit(
            f"EXEC-20260427T12000002{i:04d}-cccccc",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # red again
    _, body_full = _get(server, "/api/skill-executions/slo-history")
    assert body_full["count"] == 3
    _, body_2 = _get(
        server, "/api/skill-executions/slo-history?limit=2"
    )
    assert body_2["count"] == 2
    # Newest two: green then red
    assert [t["to_severity"] for t in body_2["transitions"]] == [
        "green", "red",
    ]


# ─── 6. JSONL file actually written ───────────────────────────────


def test_jsonl_file_lives_under_audit_dir(server, tmp_path):
    """Filesystem effect: slo_history.jsonl ends up in the audit
    dir override, not the global cwd."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.FAILED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    audit_root = tmp_path / "execs"
    history_file = history_path(audit_root)
    assert history_file.is_file()
    lines = history_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["to_severity"] == "red"
