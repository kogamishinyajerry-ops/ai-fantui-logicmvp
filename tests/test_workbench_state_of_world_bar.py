"""E11-06 — state-of-the-world status bar regression lock.

Locks the contract for the top-of-/workbench advisory status bar that
shows truth-engine SHA · recent e2e · adversarial · open known-issues.

Per E11-00-PLAN row E11-06: read-only aggregation of evidence; the
fields are *advisory* and never claim to be a live truth-engine
reading. Verify both invariants — endpoint shape AND HTML/JS wiring —
so future polish passes don't silently regress either side.
"""

from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import (
    DemoRequestHandler,
    workbench_state_of_world_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    return response.status, response.read().decode("utf-8")


def _get_json(server: ThreadingHTTPServer, path: str) -> tuple[int, dict]:
    status, body = _get(server, path)
    return status, json.loads(body) if body else {}


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. Payload contract (direct) ────────────────────────────────────


def test_state_of_world_payload_has_required_fields() -> None:
    payload = workbench_state_of_world_payload()
    for field in (
        "kind",
        "truth_engine_sha",
        "truth_engine_sha_source",
        "recent_e2e_label",
        "recent_e2e_source",
        "adversarial_label",
        "adversarial_source",
        "open_known_issues_count",
        "open_known_issues_source",
        "last_executed_evidence",
        "generated_at",
    ):
        assert field in payload, f"missing field: {field}"


def test_state_of_world_kind_is_advisory() -> None:
    """The bar is read-only and must NEVER claim to be a live truth-engine
    reading. The 'advisory' kind is the contract."""
    payload = workbench_state_of_world_payload()
    assert payload["kind"] == "advisory"


def test_state_of_world_open_issues_is_int() -> None:
    payload = workbench_state_of_world_payload()
    assert isinstance(payload["open_known_issues_count"], int)
    assert payload["open_known_issues_count"] >= 0


def test_state_of_world_truth_engine_sha_is_short() -> None:
    """git rev-parse --short HEAD returns 7-12 chars for typical repos.
    If git is missing, the function falls back to "unknown" — also OK."""
    payload = workbench_state_of_world_payload()
    sha = payload["truth_engine_sha"]
    assert isinstance(sha, str) and sha
    assert sha == "unknown" or 4 <= len(sha) <= 40


def test_state_of_world_generated_at_is_iso() -> None:
    payload = workbench_state_of_world_payload()
    ts = payload["generated_at"]
    assert isinstance(ts, str) and ts.endswith("Z")
    assert "T" in ts


# ─── 2. Live-served endpoint contract ────────────────────────────────


def test_state_of_world_endpoint_returns_200(server) -> None:
    status, body = _get_json(server, "/api/workbench/state-of-world")
    assert status == 200
    assert body.get("kind") == "advisory"


# ─── 3. /workbench HTML carries the bar ──────────────────────────────


def test_workbench_html_has_state_of_world_bar() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-state-of-world-bar"' in html
    assert 'data-status-kind="advisory"' in html


@pytest.mark.parametrize(
    "field",
    [
        "truth_engine_sha",
        "recent_e2e_label",
        "adversarial_label",
        "open_known_issues_count",
    ],
)
def test_workbench_html_bar_has_field_slot(field: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert f'data-sow-value="{field}"' in html, f"missing bar slot: {field}"


def test_workbench_html_bar_has_advisory_flag() -> None:
    """The bar must visibly disclose its advisory nature so a presenter
    or customer reading the line never mistakes it for a live truth-engine
    reading."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert "advisory · not a live truth-engine reading" in html


# ─── 4. JS hydration is wired to DOMContentLoaded ───────────────────


def test_workbench_js_hydrate_state_of_world_bar_wired() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert "function hydrateStateOfWorldBar" in js
    assert "/api/workbench/state-of-world" in js
    # Hooked into DOMContentLoaded alongside the existing init calls.
    assert "hydrateStateOfWorldBar()" in js


# ─── 5. Live-served /workbench includes the bar HTML ────────────────


def test_workbench_route_serves_state_of_world_bar(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-state-of-world-bar"' in html
    assert 'data-sow-value="truth_engine_sha"' in html
    assert 'data-sow-value="recent_e2e_label"' in html
    assert 'data-sow-value="adversarial_label"' in html
    assert 'data-sow-value="open_known_issues_count"' in html


# ─── 6. Truth-engine red line check ─────────────────────────────────


def test_state_of_world_endpoint_is_read_only(server) -> None:
    """A POST to /api/workbench/state-of-world must NOT be silently
    accepted — the endpoint is GET-only by design. Either 404 or 405
    is acceptable; what's NOT acceptable is a 200 that mutates state."""
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request(
        "POST",
        "/api/workbench/state-of-world",
        body=b"{}",
        headers={"Content-Type": "application/json"},
    )
    response = connection.getresponse()
    response.read()
    assert response.status in (404, 405), (
        f"state-of-world POST returned {response.status}; must be 404/405"
    )
