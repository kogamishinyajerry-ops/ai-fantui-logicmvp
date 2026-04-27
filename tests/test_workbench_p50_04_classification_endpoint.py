"""P50-04 — failure_classification block in /metrics endpoint.

Locks down: the metrics response now carries a failure_classification
sidecar that aggregates abort_reasons by category. The frontend
will render this as a "what's been breaking lately" panel.
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


def _make_failed_audit(
    exec_id: str,
    *,
    abort_reason: str,
    state: str = ExecutionState.FAILED.value,
):
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-test",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:01:00Z",
        state=state,
        executor_version="0.1-test",
        abort_reason=abort_reason,
        plan=PlannedChange(rationale="x", file_edits=[]),
    )
    write_audit(rec)


# ─── 1. Block always present, even when zero failures ────────────


def test_classification_block_present_when_no_failures(server):
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert "failure_classification" in body
    assert body["failure_classification"]["total"] == 0
    assert body["failure_classification"]["by_category"] == []


# ─── 2. Categories grouped from real audits ──────────────────────


def test_classification_groups_planner_failures(server):
    _make_failed_audit(
        "EXEC-20260427T120000000001-aaaaaa",
        abort_reason="planner: minimax 503 service unavailable",
    )
    _make_failed_audit(
        "EXEC-20260427T120000000002-aaaaaa",
        abort_reason="planner: minimax 503 service unavailable",
    )
    _make_failed_audit(
        "EXEC-20260427T120000000003-aaaaaa",
        abort_reason="git: branch already exists",
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    fc = body["failure_classification"]
    assert fc["total"] == 3
    cats = {a["category"]: a for a in fc["by_category"]}
    assert cats["planner_error"]["count"] == 2
    assert cats["git_error"]["count"] == 1
    # Sample details deduped: same minimax 503 string twice → one sample
    assert "minimax 503 service unavailable" in cats["planner_error"]["sample_details"]


def test_classification_handles_aborted_with_cancel_reason(server):
    """Cancelled audits live in ABORTED state. Their reason
    starts with 'cancelled by ...' — must classify as USER_CANCEL."""
    _make_failed_audit(
        "EXEC-20260427T120000000001-aaaaaa",
        state=ExecutionState.ABORTED.value,
        abort_reason="cancelled by Kogami: changed mind",
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    fc = body["failure_classification"]
    assert fc["total"] == 1
    assert fc["by_category"][0]["category"] == "user_cancel"


def test_classification_only_counts_failed_and_aborted(server):
    """LANDED / PR_OPEN / etc. don't contribute to failure
    classification even if they happen to have an abort_reason
    (which they shouldn't, but be defensive)."""
    _make_failed_audit(
        "EXEC-20260427T120000000001-aaaaaa",
        state=ExecutionState.LANDED.value,
        abort_reason="planner: ignored — landed",
    )
    _make_failed_audit(
        "EXEC-20260427T120000000002-aaaaaa",
        state=ExecutionState.FAILED.value,
        abort_reason="planner: real failure",
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    fc = body["failure_classification"]
    assert fc["total"] == 1
    assert fc["by_category"][0]["sample_details"][0] == "real failure"


# ─── 3. Category JSON contract stable ────────────────────────────


def test_category_entries_have_expected_keys(server):
    _make_failed_audit(
        "EXEC-20260427T120000000001-aaaaaa",
        abort_reason="planner: minimax",
    )
    status, body = _get(server, "/api/skill-executions/metrics")
    fc = body["failure_classification"]
    for entry in fc["by_category"]:
        assert set(entry.keys()) == {
            "category", "count", "sample_details"
        }
        assert isinstance(entry["count"], int)
        assert isinstance(entry["sample_details"], list)
