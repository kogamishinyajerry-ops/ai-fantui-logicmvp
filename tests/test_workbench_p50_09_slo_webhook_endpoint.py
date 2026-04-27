"""P50-09 — end-to-end: metrics endpoint fires a real webhook
when an SLO transition is recorded.

Stands up TWO HTTP servers in the test:
  1. The DemoRequestHandler (system under test)
  2. A second listener that receives the webhook POST so we can
     inspect what was sent and confirm the wire shape

Locks down: real network round-trip, env-var URL config,
GREEN→RED triggers a fire, GREEN→GREEN steady-state does NOT,
webhook listener crash doesn't break /metrics.
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
from well_harness.skill_executor.states import ExecutionState


# ─── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "WORKBENCH_SKILL_EXECUTIONS_DIR", str(tmp_path / "execs"),
    )
    yield


# Module-level mutable container so the handler class can append
# captured bodies. Reset between tests via the `webhook_listener`
# fixture.
_CAPTURED_REQUESTS: list[dict] = []


class _CapturingHandler(BaseHTTPRequestHandler):
    """Receives webhook POSTs and stashes them for assertion."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else b""
        try:
            parsed = json.loads(body.decode("utf-8")) if body else {}
        except json.JSONDecodeError:
            parsed = {"_raw": body.decode("utf-8", errors="replace")}
        _CAPTURED_REQUESTS.append({
            "path": self.path,
            "headers": dict(self.headers),
            "body": parsed,
        })
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, *args, **kwargs):
        # Quiet noise during the test
        pass


@pytest.fixture
def webhook_listener(monkeypatch):
    """Start a capturing HTTP listener on a free port and point
    the WEBHOOK_URL env at it. Cleans up requests + server after
    each test."""
    _CAPTURED_REQUESTS.clear()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _CapturingHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/hook"
    monkeypatch.setenv(WEBHOOK_URL_ENV, url)
    monkeypatch.setenv("WORKBENCH_SLO_WEBHOOK_TIMEOUT", "2")
    try:
        yield {"url": url, "captured": _CAPTURED_REQUESTS}
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


# ─── 1. End-to-end: RED transition fires real webhook ─────────────


def test_red_transition_posts_to_webhook(server, webhook_listener):
    """Seed enough ABORTED audits to trip RED → poll metrics →
    listener sees one POST with the right wire shape."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    status, _ = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    # The capturing server is on the same loopback interface, so
    # round-trip should be sub-second; give it a small grace
    # window in case scheduling is unlucky.
    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and not webhook_listener["captured"]:
        time.sleep(0.05)
    captured = webhook_listener["captured"]
    assert len(captured) == 1
    body = captured[0]["body"]
    assert body["event_type"] == "slo_transition"
    assert body["to_severity"] == "red"
    assert body["from_severity"] == "none"
    assert "snapshot" in body
    assert body["snapshot"]["total"] == 6
    # Request hit the configured path
    assert captured[0]["path"] == "/hook"


# ─── 2. Steady-state polls don't fire ─────────────────────────────


def test_steady_state_does_not_fire(server, webhook_listener):
    """First poll fires (none → red). Subsequent polls with the
    same dataset do NOT — record_transition dedupes upstream and
    no transition reaches the webhook."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    _get(server, "/api/skill-executions/metrics")
    _get(server, "/api/skill-executions/metrics")
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline:
        time.sleep(0.05)
    captured = webhook_listener["captured"]
    assert len(captured) == 1


# ─── 3. First-call GREEN does not fire ────────────────────────────


def test_first_green_does_not_fire(server, webhook_listener):
    """A clean dataset on first poll → record_transition skips it
    (silent first-GREEN), and therefore the webhook also stays
    silent."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        time.sleep(0.05)
    assert webhook_listener["captured"] == []


# ─── 4. Recovery (red → green) fires ──────────────────────────────


def test_recovery_transition_fires(server, webhook_listener):
    """RED → GREEN is news: the operator wants to know things
    healed. Both transitions in the sequence land at the listener."""
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # → red

    for i in range(20):
        _audit(
            f"EXEC-20260427T12000001{i:04d}-bbbbbb",
            state=ExecutionState.LANDED.value,
        )
    _get(server, "/api/skill-executions/metrics")  # red → green

    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline and len(webhook_listener["captured"]) < 2:
        time.sleep(0.05)
    captured = webhook_listener["captured"]
    assert len(captured) == 2
    assert captured[0]["body"]["to_severity"] == "red"
    assert captured[1]["body"]["from_severity"] == "red"
    assert captured[1]["body"]["to_severity"] == "green"


# ─── 5. Webhook listener down doesn't break /metrics ──────────────


def test_unreachable_webhook_does_not_break_metrics(
    server, monkeypatch
):
    """If the webhook URL points to a closed port, /metrics must
    still return 200. Alerting failures are best-effort."""
    # Pick a port that's almost certainly closed (high range, no
    # listener) — connection refused will trip URLError.
    monkeypatch.setenv(WEBHOOK_URL_ENV, "http://127.0.0.1:1/hook")
    monkeypatch.setenv("WORKBENCH_SLO_WEBHOOK_TIMEOUT", "1")
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert body["slo_status"]["overall"] == "red"


# ─── 6. No URL configured → metrics still works ──────────────────


def test_no_webhook_url_metrics_works_normally(
    server, monkeypatch
):
    """Default deployment doesn't set the URL. /metrics must
    behave exactly as it did before P50-09 — just no webhook fire."""
    monkeypatch.delenv(WEBHOOK_URL_ENV, raising=False)
    for i in range(6):
        _audit(
            f"EXEC-20260427T12000000{i:04d}-aaaaaa",
            state=ExecutionState.ABORTED.value,
        )
    status, body = _get(server, "/api/skill-executions/metrics")
    assert status == 200
    assert body["slo_status"]["overall"] == "red"
