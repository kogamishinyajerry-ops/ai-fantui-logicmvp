"""P51-02 — workbench Live Log Panel SSE.

Locks down: in-memory ring buffer holds the last 500 entries and
respects FIFO eviction; the SSE endpoint streams those entries in
chronological order, supports a `since` cursor for reconnects,
emits text/event-stream content-type, and never blocks the
executor when log_stream itself errors.

The endpoint runs against ThreadingHTTPServer like other workbench
HTTP tests. Bounded session length (set low here) keeps tests fast.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor import log_stream


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "skill_executions")
    )
    # Tighten the SSE session window so tests don't sit on a thread
    # for 60s. 1.5s is enough to drain the buffer and observe one
    # heartbeat before the handler closes.
    monkeypatch.setenv("WORKBENCH_LOG_STREAM_DURATION_SEC", "1.5")
    monkeypatch.setenv("WORKBENCH_LOG_STREAM_POLL_SEC", "0.1")
    log_stream.clear()
    yield
    log_stream.clear()


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


# ─── 1. Ring buffer pure-function tests ────────────────────────


def test_push_increments_seq_and_appends():
    log_stream.clear()
    a = log_stream.push(phase="PLANNING", level="info", message="x")
    b = log_stream.push(phase="EDITING", level="info", message="y")
    assert a.seq == 1
    assert b.seq == 2
    assert log_stream.buffer_size() == 2


def test_buffer_evicts_oldest_at_500():
    log_stream.clear()
    for i in range(550):
        log_stream.push(phase="P", level="info", message=str(i))
    # Ring is bounded at 500 — only the last 500 survived
    assert log_stream.buffer_size() == 500
    surviving = log_stream.events_since(0)
    assert surviving[0].seq == 51   # 0..50 evicted
    assert surviving[-1].seq == 550


def test_events_since_filters_by_cursor():
    log_stream.clear()
    log_stream.push(phase="P", level="info", message="a")
    log_stream.push(phase="P", level="info", message="b")
    log_stream.push(phase="P", level="info", message="c")
    after = log_stream.events_since(2)
    assert len(after) == 1
    assert after[0].message == "c"


def test_message_is_truncated_to_500_chars():
    log_stream.clear()
    long_msg = "x" * 5000
    e = log_stream.push(phase="P", level="info", message=long_msg)
    assert len(e.message) == 500


def test_log_entry_round_trips_to_json():
    log_stream.clear()
    e = log_stream.push(phase="EDITING", level="warn", message="m")
    j = e.to_json()
    assert j["phase"] == "EDITING"
    assert j["level"] == "warn"
    assert j["message"] == "m"
    assert j["seq"] == e.seq
    assert "ts" in j


# ─── 2. SSE endpoint tests ─────────────────────────────────────


def _stream_for(server, query=""):
    """Open the SSE endpoint, drain until the handler closes
    (which happens after WORKBENCH_LOG_STREAM_DURATION_SEC), then
    return the raw body. Tests configure DURATION=1.5s so this is
    bounded."""
    conn = http.client.HTTPConnection(
        "127.0.0.1", server.server_address[1], timeout=10
    )
    conn.request("GET", "/api/workbench/log-stream" + query)
    resp = conn.getresponse()
    body = resp.read().decode("utf-8", errors="replace")
    conn.close()
    return resp, body


def test_sse_endpoint_returns_event_stream_content_type(server):
    log_stream.push(phase="INIT", level="info", message="hello")
    resp, _body = _stream_for(server)
    assert resp.status == 200
    assert resp.getheader("Content-Type") == "text/event-stream"


def test_sse_endpoint_streams_buffer_contents(server):
    log_stream.push(phase="PLANNING", level="info", message="msg-A")
    log_stream.push(phase="EDITING", level="info", message="msg-B")
    _resp, body = _stream_for(server)
    # The SSE body is multiple `data: <json>\n\n` blocks. Both
    # messages must appear.
    assert "msg-A" in body
    assert "msg-B" in body


def test_sse_endpoint_respects_since_cursor(server):
    log_stream.push(phase="P", level="info", message="old")
    log_stream.push(phase="P", level="info", message="new")
    # Cursor=1 → only seq>1 entries should be sent (i.e. "new")
    _resp, body = _stream_for(server, query="?since=1")
    assert "new" in body
    assert "old" not in body


def test_sse_endpoint_emits_heartbeat_comment(server):
    """Reverse-proxy + browser EventSource both depend on
    periodic activity to avoid timing out an idle connection.
    The handler MUST emit at least one `: cursor=…\\n\\n` heartbeat."""
    _resp, body = _stream_for(server)
    assert ": cursor=" in body


def test_sse_payload_is_valid_json_per_event(server):
    log_stream.push(phase="ASKING", level="info", message="payload-check")
    _resp, body = _stream_for(server)
    data_lines = [
        l[len("data: "):]
        for l in body.splitlines()
        if l.startswith("data: ")
    ]
    assert data_lines, body
    parsed = json.loads(data_lines[-1])
    for required in ("seq", "ts", "phase", "level", "message"):
        assert required in parsed
    assert parsed["message"] == "payload-check"


def test_sse_endpoint_works_with_empty_buffer(server):
    """No events queued → endpoint still returns 200 + heartbeat;
    never 4xx and never hangs forever (DURATION cap)."""
    _resp, body = _stream_for(server)
    assert _resp.status == 200
    assert ": cursor=0" in body  # cursor stays 0 with empty buffer


# ─── 3. Orchestrator integration ───────────────────────────────


import subprocess


def _git(repo_root, *args):
    return subprocess.run(
        ["git", *args], cwd=str(repo_root),
        check=True, capture_output=True, text=True,
    )


@pytest.fixture
def mini_repo(tmp_path):
    (tmp_path / "src" / "well_harness").mkdir(parents=True)
    (tmp_path / "src" / "well_harness" / "controller.py").write_text(
        "VAL = 1\n", encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_smoke.py").write_text(
        "def test_pass(): assert 1 + 1 == 2\n", encoding="utf-8",
    )
    proposal = {
        "id": "PROP-p51-02",
        "system_id": "thrust-reverser",
        "kind": "modify",
        "interpretation": {
            "change_kind": "tighten_condition",
            "summary_zh": "x",
            "summary_en": "x",
        },
        "status": "ACCEPTED",
        "source_text": "x",
    }
    (tmp_path / "proposals").mkdir()
    (tmp_path / "proposals" / "PROP-p51-02.json").write_text(
        json.dumps(proposal), encoding="utf-8"
    )
    (tmp_path / "queue").mkdir()
    (tmp_path / "queue" / "PROP-p51-02.md").write_text(
        "# brief\n", encoding="utf-8",
    )
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "config", "user.email", "t@x")
    _git(tmp_path, "config", "user.name", "t")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "i")
    return tmp_path


def test_orchestrator_pushes_to_log_stream(mini_repo, tmp_path, monkeypatch):
    """Running execute_proposal end-to-end populates the ring
    buffer with state-transition messages. The Live Log Panel
    relies on this — without it the panel is permanently empty."""
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(mini_repo / "queue"))
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    log_stream.clear()
    plan = {
        "rationale": "r",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "VAL = 1",
                "new_snippet": "VAL = 2",
                "reason": "tighten",
            }
        ],
    }
    body = json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )
    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id="PROP-p51-02",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=lambda *a, **kw: body,
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    assert result.error is None, result.error
    events = log_stream.events_since(0)
    # Must include a state_transition push for INIT → PLANNING
    transition_msgs = [e.message for e in events if "→" in e.message]
    assert any("INIT" in m and "PLANNING" in m for m in transition_msgs), (
        "expected INIT→PLANNING in stream, got: "
        + ", ".join(transition_msgs[:8])
    )
    # Phase tagging is not blank (used by the panel for coloring)
    assert any(e.phase for e in events)


def test_log_stream_failure_does_not_break_orchestrator(
    mini_repo, tmp_path, monkeypatch
):
    """If log_stream.push raises, the executor MUST keep running.
    We rely on this: log_stream is a transient demo aid, not a
    safety-critical artifact."""
    monkeypatch.setenv("WORKBENCH_PROPOSALS_DIR", str(mini_repo / "proposals"))
    monkeypatch.setenv("WORKBENCH_DEV_QUEUE_DIR", str(mini_repo / "queue"))
    monkeypatch.setenv("WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"))
    monkeypatch.setattr(
        log_stream, "push",
        lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("simulated")),
    )
    plan = {
        "rationale": "r",
        "affected_namespaces": ["logic_truth"],
        "risk_assessment": {"logic_truth": "yellow"},
        "file_edits": [
            {
                "path": "src/well_harness/controller.py",
                "old_snippet": "VAL = 1",
                "new_snippet": "VAL = 2",
                "reason": "tighten",
            }
        ],
    }
    body = json.dumps(
        {"choices": [{"message": {"content": json.dumps(plan)}}]}
    )
    from well_harness.skill_executor.orchestrator import execute_proposal
    result = execute_proposal(
        proposal_id="PROP-p51-02",
        repo_root=mini_repo,
        audit_dir=tmp_path / "execs",
        auto_approve=True,
        request_post_for_llm=lambda *a, **kw: body,
        skip_pr=True,
        skip_push=True,
        sleep_fn=lambda _s: None,
    )
    # Pipeline still completed despite log_stream raising
    assert result.error is None, result.error
    assert result.record.state == "PR_OPEN"
