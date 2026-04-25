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


# ─── P1+P2+P4 R2 BLOCKER fix: lock exact canonical card payloads ─────
#
# The exact payloads are FROZEN via these literals. If workbench.js drifts
# (e.g. n_trials → 50, max_results → 5, n1k → 0.5), the test below catches
# it before it reaches a live demo.
WOW_A_FROZEN_PAYLOAD = {
    "tra_deg": -35,
    "radio_altitude_ft": 2,
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
    "n1k": 0.92,
    "feedback_mode": "auto_scrubber",
    "deploy_position_percent": 95,
}
WOW_B_FROZEN_PAYLOAD = {"system_id": "thrust-reverser", "n_trials": 1000, "seed": 42}
WOW_C_FROZEN_PAYLOAD = {
    "system_id": "thrust-reverser",
    "outcome": "deploy_confirmed",
    "max_results": 10,
}


def _extract_wow_scenarios_payloads_from_js() -> dict[str, dict]:
    """Parse the WOW_SCENARIOS block out of workbench.js so the exact card
    literals can be compared against the frozen e2e contracts."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    for wow_id, frozen in (
        ("wow_a", WOW_A_FROZEN_PAYLOAD),
        ("wow_b", WOW_B_FROZEN_PAYLOAD),
        ("wow_c", WOW_C_FROZEN_PAYLOAD),
    ):
        # Each scenario is keyed by `<wow_id>: { ... }` inside WOW_SCENARIOS.
        # We don't need a full JS parser: assert each frozen field appears
        # in the file in a payload key:value form near the wow_id.
        anchor = js.find(f"{wow_id}:")
        assert anchor != -1, f"WOW_SCENARIOS missing entry for {wow_id}"
        # Take a slice large enough to contain the whole payload object.
        slice_ = js[anchor : anchor + 1200]
        for k, v in frozen.items():
            if isinstance(v, bool):
                literal = "true" if v else "false"
            elif isinstance(v, str):
                literal = f'"{v}"'
            else:
                literal = str(v)
            assert (
                f"{k}: {literal}" in slice_
            ), f"{wow_id}.{k} drift: expected `{k}: {literal}` near {wow_id}: in workbench.js"
        out[wow_id] = frozen
    return out


def test_workbench_js_freezes_exact_canonical_payloads() -> None:
    """Lock every shipped wow_a/b/c payload literal against the e2e contract.

    P1+P2+P4 R2 BLOCKER fix — without this, n_trials/seed/max_results/n1k
    can silently drift in workbench.js and the cards would no longer match
    `tests/e2e/test_wow_a_causal_chain.py:51`,
    `tests/e2e/test_wow_b_monte_carlo.py:_run`, or
    `tests/e2e/test_wow_c_reverse_diagnose.py:test_wow_c_deploy_confirmed`.
    """
    _extract_wow_scenarios_payloads_from_js()


def test_wow_a_live_endpoint_with_exact_card_payload(server) -> None:
    """wow_a card POSTs the EXACT BEAT_DEEP_PAYLOAD; assert e2e contract."""
    status, body = _post(server, "/api/lever-snapshot", WOW_A_FROZEN_PAYLOAD)
    assert status == 200
    assert isinstance(body.get("nodes"), list)
    assert len(body["nodes"]) > 0
    # P1+P2+P5 R2 BLOCKER fix: the card no longer overstates "L1–L4
    # latched"; verify the actual e2e contract holds — under auto_scrubber
    # BEAT_DEEP must latch logic2+logic3+logic4 (logic1 may drop out).
    logic = body.get("logic", {}) or {}
    assert isinstance(logic, dict), "wow_a response must expose `logic` dict"
    active = {k for k, v in logic.items() if isinstance(v, dict) and v.get("active") is True}
    assert {"logic2", "logic3", "logic4"} <= active, (
        f"BEAT_DEEP must latch at least logic2+logic3+logic4, got {active}"
    )


def test_wow_b_live_endpoint_with_exact_card_payload(server) -> None:
    """wow_b card POSTs n_trials=1000, seed=42 — probe with the SAME values."""
    status, body = _post(server, "/api/monte-carlo/run", WOW_B_FROZEN_PAYLOAD)
    assert status == 200
    assert body["n_trials"] == 1000  # exact card value, not 100
    assert "success_rate" in body
    assert "n_failures" in body


def test_wow_c_live_endpoint_with_exact_card_payload(server) -> None:
    """wow_c card POSTs max_results=10 — probe with the SAME value."""
    status, body = _post(server, "/api/diagnosis/run", WOW_C_FROZEN_PAYLOAD)
    assert status == 200
    assert body["outcome"] == "deploy_confirmed"
    assert "total_combos_found" in body
    assert "grid_resolution" in body
    assert isinstance(body.get("results"), list)
    assert len(body["results"]) <= 10  # bounded by max_results


# ─── P4 R2 IMPORTANT fix: lock selector contract ─────────────────────


@pytest.mark.parametrize("wow_id", ["wow_a", "wow_b", "wow_c"])
def test_workbench_html_card_has_run_button_selector(wow_id: str) -> None:
    """The click handler binds via .workbench-wow-run-button[data-wow-action="run"];
    if the selector contract drifts the card becomes inert."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    # Each card must have a button with class workbench-wow-run-button,
    # data-wow-action="run", and matching data-wow-id.
    pattern = re.compile(
        r'<button[^>]*?class="workbench-wow-run-button"[^>]*?'
        r'data-wow-action="run"[^>]*?data-wow-id="' + re.escape(wow_id) + r'"',
        re.DOTALL,
    )
    alt_pattern = re.compile(
        r'<button[^>]*?data-wow-id="' + re.escape(wow_id) + r'"[^>]*?'
        r'class="workbench-wow-run-button"[^>]*?data-wow-action="run"',
        re.DOTALL,
    )
    assert pattern.search(html) or alt_pattern.search(html), (
        f"wow card {wow_id} is missing the click-binding selector contract"
    )


# ─── P4 R2 IMPORTANT fix: lock workbench_start.html [REWRITE] copy ───


def test_workbench_start_reflects_e11_05_shipped() -> None:
    """The 3 [REWRITE] lines on workbench_start.html must claim E11-05 has shipped,
    not the stale 'not yet shipped' text."""
    html = (STATIC_DIR / "workbench_start.html").read_text(encoding="utf-8")
    # Positive claim (must appear): cards are live on /workbench.
    assert "wow_a/b/c 起手卡片已上线（E11-05）" in html
    # Negative claim (must NOT appear): the stale "not yet shipped" line.
    assert "wow_a/b/c 起手卡片是 E11-05 范围，本期暂未上线" not in html
    # Negative claim (must NOT appear): "no UI 走读 surface".
    assert "没有 UI 走读 surface" not in html


# ─── P1 R2 IMPORTANT fix: error-path UI assertions ──────────────────


def test_workbench_js_runWowScenario_handles_http_error_and_timeout() -> None:
    """The click handler must render HTTP-error and abort/timeout failures
    distinctly, never a stuck `POST ... ` placeholder.

    P1 R2 BLOCKER fix — without bounded timeout + abort path, the card
    freezes mid-demo when an endpoint stalls.
    """
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # AbortController + bounded timeout
    assert "AbortController" in js, "no abort path; stalled requests freeze the card"
    assert "WOW_REQUEST_TIMEOUT_MS" in js, "no bounded timeout constant"
    assert "AbortError" in js, "AbortError branch must render distinct copy"
    # HTTP-error branch
    assert 'data-wow-state", "error"' in js
    # Re-enable the button on every exit (success / error / abort)
    assert "button.disabled = false" in js
    # Sanity: the timeout constant has a real numeric value, not 0.
    m = re.search(r"WOW_REQUEST_TIMEOUT_MS\s*=\s*(\d+)", js)
    assert m and int(m.group(1)) >= 1000, "timeout must be ≥ 1000ms"


def test_workbench_html_serves_with_wow_section(server) -> None:
    """Live-served /workbench page includes the wow starters section."""
    status, html = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-wow-starters"' in html
    assert 'data-wow-id="wow_a"' in html
    assert 'data-wow-id="wow_b"' in html
    assert 'data-wow-id="wow_c"' in html
