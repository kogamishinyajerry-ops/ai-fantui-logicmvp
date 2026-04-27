"""P50-11 — end-to-end: rapid SLO flapping fires only one
webhook per severity per window.

Stands up the same dual-server pattern as P50-09: the workbench
HTTP server (system under test) plus a capturing webhook
listener. Drives a flap pattern through the metrics endpoint,
asserts the listener receives the throttled subset.
"""

from __future__ import annotations

import http.client
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from well_harness.demo_server import DemoRequestHandler
from well_harness.skill_executor.audit import audit_dir, write_audit
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.slo_webhook import WEBHOOK_URL_ENV
from well_harness.skill_executor.slo_webhook_throttle import (
    THROTTLE_INTERVAL_ENV,
    read_state,
    state_path,
)
from well_harness.skill_executor.states import ExecutionState


# ─── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"),
    )
    yield


_CAPTURED: list[dict] = []


class _CapturingHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        try:
            parsed = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            parsed = {}
        _CAPTURED.append(parsed)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, *args, **kwargs):
        pass


@pytest.fixture
def webhook_listener(monkeypatch):
    _CAPTURED.clear()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _CapturingHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/hook"
    monkeypatch.setenv(WEBHOOK_URL_ENV, url)
    monkeypatch.setenv("WORKBENCH_SLO_WEBHOOK_TIMEOUT", "2")
    try:
        yield {"url": url, "captured": _CAPTURED}
    finally:
        srv.shutdown()
        srv.server_close()


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


def _audit(exec_id, *, state):
    write_audit(
        ExecutionRecord(
            exec_id=exec_id,
            schema_version=AUDIT_SCHEMA_VERSION,
            proposal_id="PROP-x",
            kind=ExecutionKind.MODIFY,
            audit_source=AuditSource.LIVE,
            started_at="2026-04-27T12:00:00Z",
            finished_at="2026-04-27T12:01:00Z",
            state=state,
            executor_version="0.1-test",
            plan=PlannedChange(rationale="x", file_edits=[]),
        )
    )


def _wait_for_capture(min_count: int, *, timeout: float = 2.0) -> None:
    """Loopback round-trips are sub-second but give a small grace
    window in case of unlucky scheduling."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and len(_CAPTURED) < min_count:
        time.sleep(0.05)


def _wait_quiet(seconds: float = 0.5) -> None:
    """Brief drain: confirm no late requests sneak in."""
    time.sleep(seconds)


# ─── 1. Throttle state file is written on first fire ─────────────


def test_first_red_writes_throttle_state(server, webhook_listener, tmp_path):
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for_capture(1)
    assert len(webhook_listener["captured"]) == 1
    # State file exists under the audit dir override
    audit_root = tmp_path / "execs"
    assert state_path(audit_root).is_file()
    state = read_state(audit_root)
    assert "red" in state.last_dispatched


# ─── 2. Rapid same-severity repeat is suppressed ─────────────────


def test_rapid_red_repeat_is_throttled(server, webhook_listener, monkeypatch):
    """RED → GREEN → RED within a 5-min throttle window: only the
    FIRST red fires, the second is suppressed.

    Use the default throttle window (5 min). The whole test runs
    in <1 sec so even with sub-second clock drift we're well
    inside the window."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # red fires
    _wait_for_capture(1)
    # Recovery: enough LANDED to flip to green
    for i in range(20):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # green fires
    _wait_for_capture(2)
    # Re-breach: more aborted entries → flip back to red
    for i in range(60):
        _audit(
            f"EXEC-20260427T12000002{i:04d}-cccccc",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # red#2 SHOULD be throttled
    _wait_quiet()
    captured = webhook_listener["captured"]
    # Exactly two: the first red and the first green. The second
    # red is within red's throttle window.
    assert len(captured) == 2
    assert [c["to_severity"] for c in captured] == ["red", "green"]


# ─── 3. Independent clocks: green throttle doesn't block red ────


def test_independent_clocks(server, webhook_listener):
    """First red fires + first green fires (different clocks).
    Re-firing red is throttled; re-firing green also throttled.
    But the green throttle does NOT delay red, and vice-versa.

    This test verifies the red#1 → green#1 path both fire because
    they use independent severity clocks."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    for i in range(20):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for_capture(2)
    captured = webhook_listener["captured"]
    assert len(captured) == 2
    assert captured[0]["to_severity"] == "red"
    assert captured[1]["to_severity"] == "green"


# ─── 4. Zero interval disables the throttle ──────────────────────


def test_zero_interval_disables_throttle(
    server, webhook_listener, monkeypatch
):
    """Setting min-interval=0 means every transition fires
    regardless of recency. Useful for debugging or temporarily
    forcing every event through to a logging endpoint."""
    monkeypatch.setenv(THROTTLE_INTERVAL_ENV, "0")
    # Force red → green → red (would normally be throttled)
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    for i in range(20):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    for i in range(60):
        _audit(
            f"EXEC-20260427T12000002{i:04d}-cccccc",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for_capture(3)
    captured = webhook_listener["captured"]
    assert len(captured) == 3
    assert [c["to_severity"] for c in captured] == ["red", "green", "red"]


# ─── 5. Throttle never breaks the metrics response ───────────────


def test_throttle_failure_does_not_break_metrics(
    server, webhook_listener, monkeypatch, tmp_path
):
    """Force the throttle state path to be unwritable. /metrics
    must still return 200 — the safety net catches any throttle
    write failure."""
    audit_root = tmp_path / "execs"
    audit_root.mkdir(parents=True, exist_ok=True)
    # Pre-create a directory at the state file path so the atomic
    # rename can't replace it. write_state will hit OSError; the
    # demo_server wrapper swallows that.
    sp = state_path(audit_root)
    sp.mkdir(parents=True, exist_ok=True)
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert body["slo_status"]["overall"] == "red"


# ─── 6. Throttle config persists across server restarts ──────────


def test_throttle_state_persists_across_polls(
    server, webhook_listener, tmp_path
):
    """State file is the source of truth — nothing in-memory.
    A new request hitting the endpoint reads the file fresh, so
    the throttle clock survives a server restart (which we
    simulate via fresh _get calls)."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for_capture(1)
    audit_root = tmp_path / "execs"
    state_before = read_state(audit_root)
    red_ts = state_before.last_dispatched["red"]
    # Same-severity transition would re-trip without throttle —
    # but no actual transition happens here (record_transition
    # dedupes). So we just verify the timestamp is stable across
    # additional polls.
    _get(server, "/api/skill-executions/metrics")
    _get(server, "/api/skill-executions/metrics")
    state_after = read_state(audit_root)
    assert state_after.last_dispatched["red"] == red_ts
