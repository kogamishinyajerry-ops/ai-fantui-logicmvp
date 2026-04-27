"""P51-03 — One-Click Demo Script + Governance persistence.

Locks down four canonical scenarios reach their expected terminal
state, governance decisions persist to a JSONL history file
(restart-safe), and the GET /api/workbench/governance/history
endpoint returns those decisions newest-first.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor import governance_history


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_GOVERNANCE_HISTORY_PATH",
        str(tmp_path / "gov_history.jsonl"),
    )
    governance_history.clear()
    yield
    governance_history.clear()


# ─── 1. governance_history pure-function tests ──────────────────


def test_record_and_read_round_trip():
    governance_history.record_decision(
        exec_id="EXEC-A",
        proposal_id="PROP-1",
        decision="approved",
        decided_at="2026-04-27T12:00:00Z",
        decided_by="kogami",
        decision_note="ok",
        verdict={"required": True, "matches": []},
    )
    history = governance_history.read_history()
    assert len(history) == 1
    e = history[0]
    assert e.exec_id == "EXEC-A"
    assert e.decision == "approved"
    assert e.decided_by == "kogami"


def test_history_returns_newest_first():
    for i in range(5):
        governance_history.record_decision(
            exec_id=f"EXEC-{i}",
            proposal_id=f"PROP-{i}",
            decision="approved",
            decided_at=f"2026-04-27T12:0{i}:00Z",
            decided_by="kogami",
            decision_note="",
            verdict={"required": True, "matches": []},
        )
    history = governance_history.read_history()
    # Newest-first: EXEC-4 ... EXEC-0
    assert [e.exec_id for e in history] == [
        f"EXEC-{i}" for i in (4, 3, 2, 1, 0)
    ]


def test_history_limit_truncates():
    for i in range(10):
        governance_history.record_decision(
            exec_id=f"EXEC-{i}",
            proposal_id=f"PROP-{i}",
            decision="approved",
            decided_at="2026-04-27T12:00:00Z",
            decided_by="x",
            decision_note="",
            verdict={},
        )
    assert len(governance_history.read_history(limit=3)) == 3
    assert len(governance_history.read_history(limit=999)) == 10


def test_missing_file_returns_empty_list(tmp_path, monkeypatch):
    """Fresh deploy with no history file yet: read_history → []."""
    monkeypatch.setenv(
        "WORKBENCH_GOVERNANCE_HISTORY_PATH",
        str(tmp_path / "never_created.jsonl"),
    )
    assert governance_history.read_history() == []


def test_history_skips_malformed_lines(tmp_path, monkeypatch):
    """Partial-write recovery: a corrupt last line MUST NOT crash
    the reader."""
    p = tmp_path / "history.jsonl"
    monkeypatch.setenv("WORKBENCH_GOVERNANCE_HISTORY_PATH", str(p))
    governance_history.record_decision(
        exec_id="EXEC-good",
        proposal_id="PROP-1",
        decision="approved",
        decided_at="t",
        decided_by="x",
        decision_note="",
        verdict={},
    )
    # Append a corrupt line
    with p.open("a", encoding="utf-8") as fh:
        fh.write("{not valid json\n")
    history = governance_history.read_history()
    assert len(history) == 1
    assert history[0].exec_id == "EXEC-good"


def test_history_survives_process_restart(tmp_path, monkeypatch):
    """Persistence semantics: a separate read after the writer
    process exits sees the same data. Simulated here by clearing
    the in-memory state and re-reading from disk."""
    p = tmp_path / "restart.jsonl"
    monkeypatch.setenv("WORKBENCH_GOVERNANCE_HISTORY_PATH", str(p))
    governance_history.record_decision(
        exec_id="EXEC-restart",
        proposal_id="PROP-X",
        decision="rejected",
        decided_at="t",
        decided_by="kogami",
        decision_note="not safe",
        verdict={"required": True},
    )
    # Simulate "process restart" — module state is just the file
    # path env, so reading again yields the same data.
    history = governance_history.read_history()
    assert len(history) == 1
    assert history[0].decision == "rejected"


# ─── 2. /api/workbench/governance/history endpoint ──────────────


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
        "127.0.0.1", server.server_address[1], timeout=5,
    )
    conn.request("GET", path)
    resp = conn.getresponse()
    raw = resp.read().decode("utf-8")
    conn.close()
    return resp.status, json.loads(raw)


def test_history_endpoint_returns_persisted_decisions(server):
    governance_history.record_decision(
        exec_id="EXEC-endpoint",
        proposal_id="PROP-Z",
        decision="approved",
        decided_at="2026-04-27T12:00:00Z",
        decided_by="kogami",
        decision_note="ok",
        verdict={"required": True},
    )
    status, body = _get(server, "/api/workbench/governance/history")
    assert status == 200
    assert "decisions" in body
    assert len(body["decisions"]) == 1
    assert body["decisions"][0]["exec_id"] == "EXEC-endpoint"
    assert body["decisions"][0]["decision"] == "approved"


def test_history_endpoint_respects_limit_query(server):
    for i in range(4):
        governance_history.record_decision(
            exec_id=f"EXEC-{i}",
            proposal_id=f"PROP-{i}",
            decision="approved",
            decided_at="t",
            decided_by="x",
            decision_note="",
            verdict={},
        )
    status, body = _get(
        server, "/api/workbench/governance/history?limit=2"
    )
    assert status == 200
    assert len(body["decisions"]) == 2
    # Newest-first: EXEC-3, EXEC-2
    assert body["decisions"][0]["exec_id"] == "EXEC-3"


def test_history_endpoint_empty_returns_200_with_empty_list(server):
    status, body = _get(server, "/api/workbench/governance/history")
    assert status == 200
    assert body == {"decisions": []}


# ─── 3. Demo scenarios ─────────────────────────────────────────


import sys


# Make scripts/ importable as a module
sys.path.insert(0, str(REPO_ROOT / "scripts"))


def test_nominal_scenario_completes_dry_run():
    import workbench_demo
    out = workbench_demo.run_scenario("nominal")
    assert out["final_state"] == "DRY_RUN_COMPLETE"
    assert out["dry_run"] is True
    assert out["plan_steps_total"] == 5
    assert out["abort_reason"] == ""


def test_governance_hold_scenario_records_approval():
    import workbench_demo
    governance_history.clear()
    out = workbench_demo.run_scenario("governance-hold")
    assert out["final_state"] == "DRY_RUN_COMPLETE"
    assert out["governance_decision"] == "approved"
    # The decision MUST have been persisted to the history file
    history = governance_history.read_history()
    assert len(history) >= 1
    assert history[0].decision == "approved"
    assert history[0].proposal_id == "PROP-demo-governance"


def test_transient_retry_scenario_completes_after_retry():
    import workbench_demo
    out = workbench_demo.run_scenario("transient-retry")
    assert out["final_state"] == "DRY_RUN_COMPLETE"
    # The flaky_post fixture answered the first call with a
    # transient error — at least 2 LLM calls must have been made.
    assert out["llm_calls_made"] >= 2


def test_hard_failure_scenario_ends_failed_with_abort_reason():
    import workbench_demo
    out = workbench_demo.run_scenario("hard-failure")
    assert out["final_state"] == "FAILED"
    assert out["abort_reason"]  # non-empty


def test_unknown_scenario_raises():
    import workbench_demo
    with pytest.raises(ValueError):
        workbench_demo.run_scenario("not-a-real-scenario")
