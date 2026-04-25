"""E11-05 — wow_a/b/c canonical-scenario starter cards regression lock.

Locks the contract for the top-of-/workbench wow starter cards so future
shell edits don't silently regress the demo presenter's one-click 走读
entrypoint. Per E11-00-PLAN row E11-05.

Three contracts validated:
  1. /workbench static HTML carries the three starter cards (one per
     wow_id) with run buttons and result panes.
  2. workbench.js declares WOW_SCENARIOS with all three endpoints and
     payload-shape sentinels (BEAT_DEEP_PAYLOAD-equivalent for wow_a,
     n_trials/seed for wow_b, outcome for wow_c).
  3. The three POST endpoints behind the cards return 200 with the
     contract fields the cards' summarize() functions read.

Truth-engine red line: this is a thin UI affordance over already-public
endpoints; no controller/runner/models/adapters changes.
"""

from __future__ import annotations

import http.client
import json
import re
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


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
    body = response.read().decode("utf-8")
    return response.status, body


def _post(server: ThreadingHTTPServer, path: str, payload: dict) -> tuple[int, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    connection.request(
        "POST",
        path,
        body=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    response = connection.getresponse()
    body = json.loads(response.read().decode("utf-8") or "{}")
    return response.status, body


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. Static HTML carries all three starter cards ──────────────────


def test_workbench_html_has_wow_starters_section() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-wow-starters"' in html
    assert "起手卡" in html


@pytest.mark.parametrize("wow_id", ["wow_a", "wow_b", "wow_c"])
def test_workbench_html_has_card_for_each_wow(wow_id: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    # card article + run button + result pane all keyed by data-wow-id
    assert f'data-wow-id="{wow_id}"' in html, f"missing card for {wow_id}"
    assert (
        f'data-wow-result-for="{wow_id}"' in html
    ), f"missing result pane for {wow_id}"


# ─── 2. workbench.js wires the three scenarios ───────────────────────


def test_workbench_js_declares_wow_scenarios() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # The constants object is the single source of truth.
    assert "const WOW_SCENARIOS" in js
    # wow_a → /api/lever-snapshot with BEAT_DEEP_PAYLOAD shape.
    assert "/api/lever-snapshot" in js
    assert "tra_deg" in js and "deploy_position_percent" in js
    # wow_b → /api/monte-carlo/run with seed.
    assert "/api/monte-carlo/run" in js
    assert "n_trials" in js
    # wow_c → /api/diagnosis/run with outcome.
    assert "/api/diagnosis/run" in js
    assert "deploy_confirmed" in js


def test_workbench_js_installWowStarters_wired_to_dom() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert "function installWowStarters" in js
    # Hooked into DOMContentLoaded (alongside the existing init calls).
    assert re.search(r"installWowStarters\s*\(\s*\)", js) is not None


# ─── 3. Live endpoint contracts the cards depend on ──────────────────


def test_wow_a_live_endpoint_returns_nodes(server) -> None:
    """wow_a card summarize() reads body.nodes — must be a list on 200."""
    status, body = _post(server, "/api/lever-snapshot", {
        "tra_deg": -35,
        "radio_altitude_ft": 2,
        "engine_running": True,
        "aircraft_on_ground": True,
        "reverser_inhibited": False,
        "eec_enable": True,
        "n1k": 0.92,
        "feedback_mode": "auto_scrubber",
        "deploy_position_percent": 95,
    })
    assert status == 200
    assert isinstance(body.get("nodes"), list)
    assert len(body["nodes"]) > 0


def test_wow_b_live_endpoint_returns_success_rate(server) -> None:
    """wow_b card summarize() reads body.success_rate / n_failures / n_trials."""
    status, body = _post(server, "/api/monte-carlo/run", {
        "system_id": "thrust-reverser",
        "n_trials": 100,
        "seed": 42,
    })
    assert status == 200
    assert "success_rate" in body
    assert "n_failures" in body
    assert "n_trials" in body
    assert body["n_trials"] == 100


def test_wow_c_live_endpoint_returns_results(server) -> None:
    """wow_c card summarize() reads body.outcome / total_combos_found / results / grid_resolution."""
    status, body = _post(server, "/api/diagnosis/run", {
        "system_id": "thrust-reverser",
        "outcome": "deploy_confirmed",
        "max_results": 5,
    })
    assert status == 200
    assert body["outcome"] == "deploy_confirmed"
    assert "total_combos_found" in body
    assert "grid_resolution" in body
    assert isinstance(body.get("results"), list)


def test_workbench_html_serves_with_wow_section(server) -> None:
    """Live-served /workbench page includes the wow starters section."""
    status, html = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-wow-starters"' in html
    assert 'data-wow-id="wow_a"' in html
    assert 'data-wow-id="wow_b"' in html
    assert 'data-wow-id="wow_c"' in html
