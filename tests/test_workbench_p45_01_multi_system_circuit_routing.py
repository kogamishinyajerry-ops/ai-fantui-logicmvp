"""P45-01 — multi-system circuit routing.

The /workbench dropdown advertises 4 systems (thrust-reverser /
landing-gear / bleed-air-valve / c919-etras) but only thrust-reverser
ships a wired SVG circuit. P45-01 parameterizes the existing
/api/workbench/circuit-fragment endpoint with ?system=<id> so:

  - thrust-reverser → fantui_circuit.html (existing L1..L4 SVG)
  - any other system → placeholder SVG that says "circuit not yet
    wired" but still renders cleanly + tells the engineer how to
    wire one (drop a circuit HTML file under static/ + register it
    in _CIRCUIT_SOURCE_BY_SYSTEM)

Truth-engine red line preserved: the placeholder is a server-side
constant, no controller/runner/models/adapters changes needed to
support a new system at the workbench layer.
"""

from __future__ import annotations

import http.client
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.demo_server import DemoRequestHandler


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
SRC_DIR = REPO_ROOT / "src" / "well_harness"


# ─── Server fixture ─────────────────────────────────────────────────


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


def _get(server, path: str) -> tuple[int, str]:
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    conn.close()
    return resp.status, body


# ─── 1. Endpoint contract ───────────────────────────────────────────


def test_thrust_reverser_returns_l1_l4_circuit(server):
    """Default behavior + explicit ?system=thrust-reverser must keep
    serving the L1..L4 fragment unchanged so P44-01..06 wiring keeps
    binding correctly."""
    for path in (
        "/api/workbench/circuit-fragment",
        "/api/workbench/circuit-fragment?system=thrust-reverser",
    ):
        status, body = _get(server, path)
        assert status == 200, f"{path} returned {status}"
        for gate_id in ("L1", "L2", "L3", "L4"):
            assert f'data-gate-id="{gate_id}"' in body, (
                f"{path} fragment missing {gate_id}"
            )


def test_landing_gear_returns_placeholder_svg(server):
    status, body = _get(server, "/api/workbench/circuit-fragment?system=landing-gear")
    assert status == 200
    assert '<svg viewBox="0 0 1000 640"' in body
    assert 'data-circuit-system="placeholder"' in body
    assert 'data-circuit-system-id="landing-gear"' in body
    # Placeholder carries the bilingual "not yet wired" copy + the
    # invitation to file a ticket.
    assert "Circuit not yet wired" in body
    assert "尚未接入" in body
    assert "system: landing-gear" in body
    # Placeholder MUST NOT carry the L1..L4 anchors — review-mode +
    # interpreter need to gracefully no-op on this surface.
    for gate_id in ("L1", "L2", "L3", "L4"):
        assert f'data-gate-id="{gate_id}"' not in body, (
            f"placeholder leaked {gate_id} anchor"
        )


def test_bleed_air_still_gets_placeholder(server):
    """bleed-air-valve has no circuit file → still placeholder. P54-07
    wired c919-etras to a real circuit so it no longer fits this case;
    test_c919_etras_serves_real_circuit_fragment below replaces the
    obsolete c919 half of this assertion."""
    status, body = _get(server, "/api/workbench/circuit-fragment?system=bleed-air-valve")
    assert status == 200
    assert 'data-circuit-system="placeholder"' in body
    assert 'data-circuit-system-id="bleed-air-valve"' in body
    assert "system: bleed-air-valve" in body


def test_c919_etras_serves_real_circuit_fragment(server):
    """P54-07 (2026-04-28): c919-etras now maps to
    c919_etras_panel/circuit.html. The fragment must be the real
    SVG (with the C919-specific viewBox 0 0 1020 560), NOT the
    "circuit not yet wired" placeholder."""
    status, body = _get(server, "/api/workbench/circuit-fragment?system=c919-etras")
    assert status == 200
    assert 'data-circuit-system="placeholder"' not in body, (
        "C919 must serve real circuit, not placeholder"
    )
    assert "<svg" in body
    assert 'viewBox="0 0 1020 560"' in body
    # C919 has no L1..L4 anchors — review-mode + interpreter must
    # still gracefully no-op on this surface.
    for gate_id in ("L1", "L2", "L3", "L4"):
        assert f'data-gate-id="{gate_id}"' not in body, (
            f"C919 fragment unexpectedly carries {gate_id} anchor"
        )


def test_unknown_system_falls_through_to_placeholder(server):
    """Defensive default: a typo or future system in the URL still
    renders a usable page rather than a 404. This matters because
    the dropdown choice flows straight into the URL — a renamed
    option shouldn't blow the panel up."""
    status, body = _get(server, "/api/workbench/circuit-fragment?system=qantas-experimental-007")
    assert status == 200
    assert 'data-circuit-system="placeholder"' in body
    assert "qantas-experimental-007" in body


def test_placeholder_html_escapes_dangerous_system_id(server):
    """The placeholder embeds the system_id in <text> elements;
    naive interpolation would let a crafted ?system=<script>...
    inject markup. Verify the two angle brackets are escaped."""
    status, body = _get(
        server,
        "/api/workbench/circuit-fragment?system=%3Cscript%3Ealert(1)%3C/script%3E",
    )
    assert status == 200
    assert "<script>" not in body
    assert "&lt;script&gt;" in body


# ─── 2. Frontend wiring (HTML/JS anchors) ──────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Helper that reads the dropdown value into the fetch URL.
        "function currentWorkbenchSystem()",
        # Re-fetch entry-point wired to the dropdown's change event.
        "async function reloadWorkbenchCircuitHero()",
        # Boot wiring — the listener must install on first paint.
        "function installSystemSelectorReload()",
        "installSystemSelectorReload();",
        # The system param must travel in the fetch URL.
        '`${endpointBase}?system=${encodeURIComponent(system)}`',
        # Mount records which system the SVG belongs to so review-mode
        # and the interpreter can stay in sync.
        'mount.setAttribute("data-circuit-system", system);',
        # Per-system gate sanity-check is thrust-reverser-only — the
        # placeholder system intentionally has no gates.
        'if (system === "thrust-reverser")',
    ],
)
def test_workbench_js_wires_system_routing(needle):
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert needle in js, f"workbench.js missing P45-01 wiring: {needle}"


# ─── 3. Truth-engine red line ───────────────────────────────────────


def test_p45_01_does_not_leak_into_truth_engine():
    """Multi-system routing is a workbench-layer concern. Adding a
    new system to the dropdown + circuit map MUST NOT require any
    edit to controller / runner / models / adapters — those modules
    stay system-agnostic and the workbench plugs them in via the
    existing adapter interface."""
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "_CIRCUIT_SOURCE_BY_SYSTEM",
        "_circuit_placeholder_fragment",
        "currentWorkbenchSystem",
        "reloadWorkbenchCircuitHero",
        "installSystemSelectorReload",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P45-01 token "
                f"'{token}' — multi-system routing must stay in the "
                f"workbench layer (demo_server + workbench.js)"
            )
