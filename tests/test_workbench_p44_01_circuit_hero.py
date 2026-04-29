"""P44-01 — control logic panel is the /workbench page hero.

Background: prior /workbench was an empty 3-column placeholder grid
(Probe & Trace / Annotate & Propose / Hand off & Track) — the actual
L1→L4 control-logic panel was missing entirely from the page. This
slice mounts the existing fantui_circuit.html SVG as the workbench
hero via a fragment endpoint so the SVG has a single source of truth
and /workbench never drifts from /fantui_circuit.html.

Lockstep contract:
- workbench.html carries the #workbench-circuit-hero placeholder with
  the data-circuit-fragment-endpoint attribute.
- /api/workbench/circuit-fragment serves the SVG block from
  fantui_circuit.html with all four data-gate-id="L1..L4" anchors
  intact, so annotation (P44-02) can bind by gate id.
- The previous WOW starter cards + 3-column collab grid are gone. The
  removal sentinels exist so a regression silently re-introducing them
  is caught.
- Truth-engine red line preserved: controller.py / runner.py / models.py
  / adapters/ / demo_server.py only adds a read-only fragment endpoint
  that EXTRACTS from the static file; no mutation of truth-engine state.
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


def _start_demo_server() -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str, dict]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read().decode("utf-8")
    return response.status, body, dict(response.getheaders())


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. workbench.html mounts the circuit hero ───────────────────────


@pytest.mark.parametrize(
    "html_anchor",
    [
        'id="workbench-circuit-hero"',
        'id="workbench-circuit-hero-mount"',
        'data-circuit-fragment-endpoint="/api/workbench/circuit-fragment"',
        'data-circuit-fragment-status="pending"',
        # NOTE (2026-04-26): `data-annotation-surface="circuit"` was the
        # binding hook for the legacy point/area/link/text-range overlay
        # that produced stray green-dot markers when the panel was clicked.
        # The overlay was unloaded from /workbench in the
        # `test_workbench_no_annotation_overlay_2026_04_26.py` contract,
        # so this anchor is intentionally no longer required here.
        'id="workbench-circuit-hero-title"',
        # JER-158 pivot copy: the circuit hero is now the editable
        # sandbox workbench. The original SVG still mounts below as a
        # read-only reference sample pack.
        "可编辑控制工作台 · EDITABLE CONTROL WORKBENCH",
        "Sandbox Draft Canvas · Baseline Diff Workbench",
        "Sandbox candidate canvas",
        "Reference sample pack · read-only SVG circuit",
        "正在加载控制逻辑面板",
    ],
)
def test_workbench_html_mounts_circuit_hero_placeholder(html_anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert html_anchor in html, f"missing P44-01 hero placeholder anchor: {html_anchor}"


# ─── 2. The wrong-abstraction sections are gone ──────────────────────


@pytest.mark.parametrize(
    "removed",
    [
        # Old 3-column shell
        '<section class="workbench-collab-grid"',
        'id="workbench-control-panel"',
        'id="workbench-document-panel"',
        'id="workbench-circuit-panel"',
        'data-column="control"',
        'data-column="document"',
        'data-column="circuit"',
        'workbench-collab-control-list',
        'workbench-collab-document',
        'workbench-collab-circuit',
        # Old column h2 / eyebrow text
        "<h2>探针与追踪 · Probe",
        "<h2>标注与提案 · Annotate",
        "<h2>移交与跟踪 · Hand off",
        # Reference packet boilerplate
        "Reference packet, clarification notes",
        "Intake -&gt; Clarification -&gt; Playback -&gt; Diagnosis -&gt; Knowledge",
        # WOW starter cards (moved off /workbench)
        '<h3 id="workbench-wow-a-title">',
        '<h3 id="workbench-wow-b-title">',
        '<h3 id="workbench-wow-c-title">',
        'data-wow-action="run"',
        "一键运行 wow_a",
    ],
)
def test_workbench_html_no_longer_carries_wrong_abstraction(removed: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert removed not in html, (
        f"P44-01 expected to remove `{removed}` from /workbench but it is still present"
    )


# ─── 3. Removal sentinel for WOW grid stays a hidden, empty section ──


def test_workbench_html_keeps_wow_removal_sentinel_hidden() -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert 'id="workbench-wow-starters-removed-by-p44-01"' in html
    # The sentinel section must be hidden so it does not render visible
    # whitespace or appear in the accessibility tree.
    assert 'hidden' in html.split('id="workbench-wow-starters-removed-by-p44-01"')[1].split('</section>')[0]


# ─── 4. workbench.js boots the hero via fetch ────────────────────────


@pytest.mark.parametrize(
    "js_anchor",
    [
        "function bootWorkbenchCircuitHero",
        '"/api/workbench/circuit-fragment"',
        "data-circuit-fragment-endpoint",
        "workbench-circuit-hero-mount",
        # Sanity-check loop in the hydrator that asserts gate anchors travel
        'data-gate-id="${gateId}"',
    ],
)
def test_workbench_js_hydrates_circuit_hero(js_anchor: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert js_anchor in js, f"missing P44-01 hero hydrator anchor: {js_anchor}"


def test_workbench_js_no_longer_boots_3_column_shell() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # The old per-column boot functions and their hardcoded ready strings
    # must be gone; their existence implies the wrong abstraction is back.
    assert "function bootWorkbenchControlPanel" not in js
    assert "function bootWorkbenchDocumentPanel" not in js
    assert "function bootWorkbenchCircuitPanel" not in js
    assert "Probe & Trace ready. Scenario actions are staged" not in js
    assert "Annotate & Propose ready. Text-range annotation is staged" not in js
    assert "Hand off & Track ready. Overlay annotation is staged" not in js


# ─── 5. /api/workbench/circuit-fragment endpoint contract ────────────


def test_circuit_fragment_endpoint_returns_svg(server) -> None:
    status, body, headers = _get(server, "/api/workbench/circuit-fragment")
    assert status == 200
    assert "text/html" in headers.get("Content-Type", "")
    # Should start with the <svg> open tag and end with </svg>; no nav, no
    # info-row, no footer carried over from fantui_circuit.html.
    body_stripped = body.strip()
    assert body_stripped.startswith('<svg viewBox="0 0 1000 640"'), (
        f"fragment must start with the canonical <svg> tag, got: {body_stripped[:80]!r}"
    )
    assert body_stripped.endswith("</svg>"), (
        f"fragment must end with </svg>, got tail: {body_stripped[-80:]!r}"
    )
    assert "<header" not in body, "fragment should not carry the standalone page header"
    assert "<nav" not in body, "fragment should not carry the unified-nav"
    assert 'class="info-row"' not in body, "fragment should not carry info-row cards"
    assert "<footer" not in body, "fragment should not carry the page footer"


@pytest.mark.parametrize("gate_id", ["L1", "L2", "L3", "L4"])
def test_circuit_fragment_carries_logic_gate_anchor(server, gate_id: str) -> None:
    status, body, _ = _get(server, "/api/workbench/circuit-fragment")
    assert status == 200
    needle = f'data-gate-id="{gate_id}"'
    assert needle in body, (
        f"circuit fragment must carry annotation anchor `{needle}` for gate {gate_id}"
    )
    # Each gate id should also carry the `logic_gate` annotation-anchor type
    # so future annotation logic can filter by anchor kind.
    assert 'data-annotation-anchor="logic_gate"' in body


def test_circuit_fragment_source_is_fantui_circuit_html(server) -> None:
    """The fragment must literally come from fantui_circuit.html so the two
    surfaces never drift. We compare a stable signature substring."""
    status, body, _ = _get(server, "/api/workbench/circuit-fragment")
    assert status == 200
    source = (STATIC_DIR / "fantui_circuit.html").read_text(encoding="utf-8")
    # Authority-chain annotation text in the SVG is a unique stable marker.
    signature = (
        "Controller Chain: L1 → tls_115vac_cmd · L2 → etrac_540vdc_cmd"
    )
    assert signature in source
    assert signature in body


# ─── 6. fantui_circuit.html itself has the gate anchors ──────────────


@pytest.mark.parametrize("gate_id", ["L1", "L2", "L3", "L4"])
def test_fantui_circuit_static_page_carries_gate_anchor(gate_id: str) -> None:
    html = (STATIC_DIR / "fantui_circuit.html").read_text(encoding="utf-8")
    assert f'data-gate-id="{gate_id}"' in html, (
        f"fantui_circuit.html must carry data-gate-id={gate_id!r} so the fragment "
        "endpoint can serve gate-anchored SVG to /workbench"
    )


# ─── 7. /workbench live-served route still serves the new shell ──────


def test_workbench_route_serves_new_hero_shell(server) -> None:
    status, body, _ = _get(server, "/workbench")
    assert status == 200
    assert 'id="workbench-circuit-hero"' in body
    assert 'id="workbench-editable-shell"' in body
    assert 'id="workbench-evidence-inspector"' in body
    assert 'data-circuit-fragment-endpoint="/api/workbench/circuit-fragment"' in body
    assert "Sandbox Draft Canvas · Baseline Diff Workbench" in body
    assert "Reference sample pack · read-only SVG circuit" in body
    # Old wrong-abstraction sentinels must not appear in the live response.
    assert 'class="workbench-collab-grid"' not in body
    assert "一键运行 wow_a" not in body


# ─── 8. Truth-engine red line — backend untouched by display copy ────


def test_p44_01_does_not_leak_display_copy_into_truth_engine() -> None:
    """P44-01 only added a read-only fragment endpoint to demo_server.py;
    no truth-engine module (controller / runner / models / adapters/)
    receives the new display copy."""
    repo_root = Path(__file__).resolve().parents[1]
    well_harness_dir = repo_root / "src" / "well_harness"
    backend_paths: list[Path] = [
        well_harness_dir / "controller.py",
        well_harness_dir / "runner.py",
        well_harness_dir / "models.py",
    ]
    adapters_dir = well_harness_dir / "adapters"
    if adapters_dir.is_dir():
        backend_paths.extend(
            p for p in adapters_dir.rglob("*.py") if "__pycache__" not in p.parts
        )
    new_display_copy = [
        "控制逻辑面板 · CONTROL LOGIC PANEL",
        "反推逻辑链路 L1 → L4",
        "点击逻辑门 (L1/L2/L3/L4) 或输入信号即可发起标注",
        "正在加载控制逻辑面板",
        "控制逻辑面板加载失败",
    ]
    for backend in backend_paths:
        text = backend.read_text(encoding="utf-8")
        for phrase in new_display_copy:
            assert phrase not in text, (
                f"P44-01 display copy {phrase!r} unexpectedly leaked into "
                f"{backend.relative_to(repo_root)} — truth-engine red-line breach"
            )
