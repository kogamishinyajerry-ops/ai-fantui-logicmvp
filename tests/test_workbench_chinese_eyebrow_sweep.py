"""E11-15 — Chinese-first eyebrow sweep.

The 5 eyebrow labels that did NOT carry a bilingual h2 below them are
flipped from English-lowercase to pure Chinese, so that the page
reads Chinese-first at a glance. The 3 column-eyebrows (probe & trace,
annotate & propose, hand off & track) are explicitly out of scope —
they are positively locked by E11-03 tests and the bilingual h2 below
each already provides Chinese-first signal.

Default state preserves all existing IDs, classes, and h1/h2 strings.
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


def _get(server: ThreadingHTTPServer, path: str) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    connection.request("GET", path)
    response = connection.getresponse()
    return response.status, response.read().decode("utf-8")


@pytest.fixture
def server():
    s, t = _start_demo_server()
    try:
        yield s
    finally:
        s.shutdown()
        s.server_close()
        t.join(timeout=2)


# ─── 1. New Chinese eyebrows are POSITIVELY locked ───────────────────


@pytest.mark.parametrize(
    "eyebrow_html",
    [
        '<p class="eyebrow">控制逻辑工作台</p>',
        '<span class="workbench-sow-eyebrow">当前现状</span>',
        '<p class="eyebrow">主流场景</p>',
        '<p class="eyebrow">标注收件箱</p>',
        '<p class="eyebrow">审批中心</p>',
    ],
)
def test_workbench_html_carries_chinese_eyebrow(eyebrow_html: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert eyebrow_html in html, f"missing Chinese-first eyebrow: {eyebrow_html}"


# ─── 2. Old English-only eyebrows are gone ───────────────────────────


@pytest.mark.parametrize(
    "stale_eyebrow_html",
    [
        '<p class="eyebrow">control logic workbench</p>',
        '<span class="workbench-sow-eyebrow">state of world</span>',
        '<p class="eyebrow">canonical scenarios</p>',
        '<p class="eyebrow">annotation inbox</p>',
        '<p class="eyebrow">approval center</p>',
    ],
)
def test_workbench_html_does_not_carry_stale_english_eyebrow(stale_eyebrow_html: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale_eyebrow_html not in html, (
        f"stale English-only eyebrow still present: {stale_eyebrow_html}"
    )


# ─── 3. Out-of-scope eyebrows (E11-03 column trio) are PRESERVED ─────


@pytest.mark.parametrize(
    "preserved_eyebrow",
    [
        '<p class="eyebrow">probe &amp; trace</p>',
        '<p class="eyebrow">annotate &amp; propose</p>',
        '<p class="eyebrow">hand off &amp; track</p>',
    ],
)
def test_e11_03_column_eyebrows_preserved(preserved_eyebrow: str) -> None:
    """E11-15 explicitly does NOT touch the column-trio eyebrows.
    They live above bilingual h2s and are locked by test_workbench_column_rename."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert preserved_eyebrow in html, (
        f"E11-03 column eyebrow accidentally removed by E11-15 sweep: {preserved_eyebrow}"
    )


# ─── 4. Anchors and h1/h2 strings preserved ──────────────────────────


@pytest.mark.parametrize(
    "anchor",
    [
        # h1/h2 main titles untouched
        "<h1>Control Logic Workbench</h1>",
        # IDs of containing sections untouched
        'id="workbench-state-of-world-bar"',
        'id="workbench-wow-starters"',
        'id="annotation-inbox"',
        'id="approval-center-panel"',
        # Class hooks untouched (CSS still binds)
        'class="eyebrow"',
        'class="workbench-sow-eyebrow"',
    ],
)
def test_e11_15_preserves_structural_anchors(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-15 sweep accidentally broke structural anchor: {anchor}"


# ─── 5. Live-served route reflects the sweep ─────────────────────────


def test_workbench_route_serves_chinese_eyebrows(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    assert "控制逻辑工作台" in html
    assert "当前现状" in html
    assert "主流场景" in html
    assert "标注收件箱" in html
    assert "审批中心" in html


# ─── 6. Truth-engine red line ────────────────────────────────────────


def test_e11_15_only_touches_static_html() -> None:
    """The sweep is HTML-only — no JS, no CSS, no controller, no adapter.
    Verify by spot-checking that the 5 changed strings appear nowhere
    else in code-bearing files."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    # The new Chinese strings live only in HTML, not JS or CSS.
    for chinese in ["控制逻辑工作台", "当前现状", "主流场景", "标注收件箱", "审批中心"]:
        assert chinese not in js, f"unexpected Chinese eyebrow leaked into workbench.js: {chinese}"
        assert chinese not in css, f"unexpected Chinese eyebrow leaked into workbench.css: {chinese}"
