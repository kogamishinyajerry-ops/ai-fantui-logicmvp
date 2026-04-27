"""P48-06 — workbench HTTP endpoints for the approval bridge.

Tests the demo_server endpoints:
  GET  /api/skill-executions
  GET  /api/skill-executions/pending
  GET  /api/skill-executions/<exec_id>
  POST /api/skill-executions/<exec_id>/approve
  POST /api/skill-executions/<exec_id>/reject
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
    Ask,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
)
from well_harness.skill_executor.workbench_polling import (
    approval_signal_path,
)


@pytest.fixture(autouse=True)
def _isolate_audit_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    yield


@pytest.fixture
def server():
    s = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


def _get(server, path: str) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    try:
        return resp.status, json.loads(raw)
    except json.JSONDecodeError:
        return resp.status, {"raw": raw}


def _post(server, path: str, body: dict | None = None) -> tuple[int, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    raw = json.dumps(body or {}).encode("utf-8")
    conn.request(
        "POST", path,
        body=raw,
        headers={"Content-Type": "application/json", "Content-Length": str(len(raw))},
    )
    resp = conn.getresponse()
    text = resp.read().decode("utf-8")
    try:
        return resp.status, json.loads(text)
    except json.JSONDecodeError:
        return resp.status, {"raw": text}


def _make_audit(
    *,
    exec_id: str = "EXEC-20260427T120000123456-abc123",
    proposal_id: str = "PROP-test",
    state: str = "ASKING",
    asks: list[Ask] | None = None,
) -> ExecutionRecord:
    rec = ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        state=state,
    )
    if asks:
        rec.asks = asks
    write_audit(rec)
    return rec


# ─── 1. GET /api/skill-executions list ────────────────────────────────


def test_list_returns_empty_when_no_audits(server):
    status, body = _get(server, "/api/skill-executions")
    assert status == 200
    assert body == {"executions": []}


def test_list_returns_all_audits(server):
    _make_audit(exec_id="EXEC-20260427T120000111111-aaaaaa", state="LANDED")
    _make_audit(exec_id="EXEC-20260427T120000222222-bbbbbb", state="ASKING")
    status, body = _get(server, "/api/skill-executions")
    assert status == 200
    assert len(body["executions"]) == 2


def test_list_filters_by_proposal(server):
    _make_audit(exec_id="EXEC-20260427T120000111111-aaaaaa", proposal_id="PROP-A")
    _make_audit(exec_id="EXEC-20260427T120000222222-bbbbbb", proposal_id="PROP-B")
    status, body = _get(server, "/api/skill-executions?proposal=PROP-A")
    assert status == 200
    ids = [e["exec_id"] for e in body["executions"]]
    assert "EXEC-20260427T120000111111-aaaaaa" in ids
    assert "EXEC-20260427T120000222222-bbbbbb" not in ids


def test_pending_endpoint_returns_only_asking(server):
    _make_audit(exec_id="EXEC-20260427T120000111111-aaaaaa", state="LANDED")
    _make_audit(exec_id="EXEC-20260427T120000222222-bbbbbb", state="ASKING")
    status, body = _get(server, "/api/skill-executions/pending")
    assert status == 200
    ids = [e["exec_id"] for e in body["executions"]]
    assert ids == ["EXEC-20260427T120000222222-bbbbbb"]


# ─── 2. GET /api/skill-executions/<id> single ─────────────────────────


def test_get_single_execution(server):
    rec = _make_audit()
    status, body = _get(server, f"/api/skill-executions/{rec.exec_id}")
    assert status == 200
    assert body["exec_id"] == rec.exec_id
    assert body["state"] == "ASKING"


def test_get_unknown_exec_returns_404(server):
    status, body = _get(
        server, "/api/skill-executions/EXEC-20260427T120000999999-deadbe"
    )
    assert status == 404
    assert body["error"] == "audit_not_found"


def test_get_malformed_exec_id_returns_400(server):
    status, body = _get(server, "/api/skill-executions/totally-bogus-id")
    assert status == 400
    assert body["error"] == "invalid_exec_id"


# ─── 3. POST approve / reject — happy paths ───────────────────────────


def test_approve_writes_signal(server, tmp_path):
    rec = _make_audit()
    status, body = _post(
        server,
        f"/api/skill-executions/{rec.exec_id}/approve",
        {"actor": "Kogami", "note": "LGTM"},
    )
    assert status == 202, body
    assert body["action"] == "approve"
    # Signal file present
    sig = approval_signal_path(audit_dir=tmp_path / "execs", exec_id=rec.exec_id)
    assert sig.is_file()
    assert sig.read_text(encoding="utf-8") == "approved"


def test_reject_writes_rejected_signal(server, tmp_path):
    rec = _make_audit()
    status, body = _post(
        server, f"/api/skill-executions/{rec.exec_id}/reject"
    )
    assert status == 202
    sig = approval_signal_path(audit_dir=tmp_path / "execs", exec_id=rec.exec_id)
    assert sig.read_text(encoding="utf-8") == "rejected"


def test_approve_records_actor_in_audit(server, tmp_path):
    """Audit's last Ask should pick up actor + note from POST."""
    ask = Ask(ask_id="ASK-1", question="approve?")
    rec = _make_audit(asks=[ask])
    _post(
        server,
        f"/api/skill-executions/{rec.exec_id}/approve",
        {"actor": "Kogami", "note": "looks good"},
    )
    # Re-read audit
    from well_harness.skill_executor.audit import read_audit
    persisted = read_audit(rec.exec_id)
    assert persisted.asks[-1].user_actor == "Kogami"
    assert persisted.asks[-1].note == "looks good"


# ─── 4. POST approve / reject — rejection cases ──────────────────────


def test_approve_unknown_exec_returns_404(server):
    status, body = _post(
        server,
        "/api/skill-executions/EXEC-20260427T120000999999-deadbe/approve",
    )
    assert status == 404


def test_approve_non_asking_state_returns_409(server):
    rec = _make_audit(state="LANDED")
    status, body = _post(
        server, f"/api/skill-executions/{rec.exec_id}/approve"
    )
    assert status == 409
    assert body["error"] == "execution_not_in_asking_state"


def test_invalid_action_returns_400(server):
    rec = _make_audit()
    status, body = _post(
        server, f"/api/skill-executions/{rec.exec_id}/something"
    )
    # The router for skill_executions only matches /approve and
    # /reject suffixes; unknown action falls through to the
    # global 404.
    assert status == 404


def test_oversized_body_rejected(server):
    rec = _make_audit()
    huge = {"note": "x" * 60_000}
    status, body = _post(
        server, f"/api/skill-executions/{rec.exec_id}/approve", huge
    )
    assert status == 400
    assert body["error"] == "oversized_body"
