"""P50-12 — end-to-end suppressed-events digest.

Drives a 3× rapid red flap through the metrics endpoint, then
a clean steady poll after the throttle window expires, and
asserts: the live webhook fired ONCE (P50-11 throttling), the
suppressed events accumulated in state, and the digest webhook
fires once-per-severity once the window passes.

Uses a tiny throttle window (1s) so the test runs in real time
without sleeps measured in minutes.
"""

from __future__ import annotations

import http.client
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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
from well_harness.skill_executor.slo_webhook import WEBHOOK_URL_ENV
from well_harness.skill_executor.slo_webhook_throttle import (
    THROTTLE_INTERVAL_ENV,
    read_state,
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
    # Throttle window short enough to wait through in-test, large
    # enough that the audit-creation loops + capture polling don't
    # accidentally exceed it (a 1s window flaked because writing
    # 60+ audit JSONs + waiting for capture pushed past 1s).
    monkeypatch.setenv(THROTTLE_INTERVAL_ENV, "3")
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


def _wait_for(min_count: int, *, timeout: float = 3.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and len(_CAPTURED) < min_count:
        time.sleep(0.05)


def _wait_quiet(seconds: float = 0.3) -> None:
    time.sleep(seconds)


# ─── 1. Suppressed events accumulate, then digest fires ───────────


def test_flap_burst_produces_digest_after_window(
    server, webhook_listener, tmp_path,
):
    """Drive: red#1 (fires) → green#1 (fires) → red#2 (suppressed
    by red's throttle) → wait past the window → poll again →
    digest fires covering red#2.

    Only red is exercised in the digest path; green is included
    just to set up the red#2 transition (need a green→red flip
    for record_transition to write a real transition entry)."""
    # red#1 — 8 aborted, pass_rate=0 → RED
    for i in range(8):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for(1)

    # green#1 — add enough LANDED to push pass_rate over 70%
    for i in range(25):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for(2)

    # red#2 — add aborted entries to push pass_rate below 50%
    # 25 LANDED among 33 total = 0.76; add 18 aborted → 25/51 = 0.49
    for i in range(18):
        _audit(
            f"EXEC-20260427T12000002{i:04d}-cccccc",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_quiet()

    # At this point only the first two transitions reached the
    # listener; red#2 is pending in state.
    captured_mid = webhook_listener["captured"]
    assert len(captured_mid) == 2
    assert [c["to_severity"] for c in captured_mid] == ["red", "green"]
    audit_root = tmp_path / "execs"
    state_mid = read_state(audit_root)
    assert "red" in state_mid.pending_suppressed
    assert len(state_mid.pending_suppressed["red"]) == 1

    # Wait past the 3s throttle window so red's digest is due.
    time.sleep(3.5)

    # Trigger another poll. take_digest_due fires the digest at
    # the start of the handler. The poll itself produces no new
    # transition (steady-state RED at this point).
    _get(server, "/api/skill-executions/metrics")
    _wait_for(3)

    # One more event: red digest
    captured = webhook_listener["captured"]
    assert len(captured) == 3
    digest = captured[2]
    assert digest["event_type"] == "slo_digest"
    assert digest["severity"] == "red"
    assert digest["suppressed_count"] == 1
    assert "transitions" in digest
    # The suppressed transition is a green→red event
    assert digest["transitions"][0]["from_severity"] == "green"
    assert digest["transitions"][0]["to_severity"] == "red"

    # State should be cleared of pending entries after the digest
    state_after = read_state(audit_root)
    assert state_after.pending_suppressed == {}


# ─── 2. No flap → no digest ───────────────────────────────────────


def test_clean_path_does_not_fire_digest(server, webhook_listener):
    """Single transition with no follow-on suppressed events →
    only the live alert fires; no digest ever follows."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _wait_for(1)
    # Wait past the window
    time.sleep(3.5)
    # Another poll — no new transition, no pending events → no digest
    _get(server, "/api/skill-executions/metrics")
    _wait_quiet()
    captured = webhook_listener["captured"]
    assert len(captured) == 1
    assert captured[0]["event_type"] == "slo_transition"


# ─── 3. State file shows the lifecycle ────────────────────────────


def test_state_lifecycle_visible_on_disk(
    server, webhook_listener, tmp_path,
):
    """Pending events accumulate to disk, then drain. Verifies the
    persistence path independently of the webhook receiver."""
    audit_root = tmp_path / "execs"

    # First fire: red lands in last_dispatched
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    state_1 = read_state(audit_root)
    assert "red" in state_1.last_dispatched
    assert state_1.pending_suppressed == {}

    # Recovery + re-breach within window: red#2 suppressed
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
    state_2 = read_state(audit_root)
    assert "red" in state_2.pending_suppressed
    assert len(state_2.pending_suppressed["red"]) == 1

    # After window, next poll drains the digest
    time.sleep(3.5)
    _get(server, "/api/skill-executions/metrics")
    state_3 = read_state(audit_root)
    assert state_3.pending_suppressed == {}
