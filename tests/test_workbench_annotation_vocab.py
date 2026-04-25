"""E11-04 — annotation vocabulary upgrade regression lock.

Locks the domain-anchored annotation toolbar copy after the E11-04
relabel from generic UI types to engineer-domain verbs:

  Annotation toolbar label:  Annotation        → 标注
  Point                      → 标记信号
  Area                       → 圈选 logic gate
  Link                       → 关联 spec
  Text Range                 → 引用 requirement 段

Per E11-00-PLAN row E11-04: underlying type IDs (data-annotation-tool=
"point"/"area"/"link"/"text-range") stay stable so e2e selectors and the
annotation_overlay.js click handlers don't break. Verify both invariants —
new visible labels AND preserved IDs — so a future "polish" pass can't
silently regress either side.
"""

from __future__ import annotations

import http.client
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


# ─── 1. Domain-anchored visible labels are present ──────────────────


@pytest.mark.parametrize(
    "label",
    [
        ">标注<",  # toolbar header
        ">标记信号<",  # point button
        ">圈选 logic gate<",  # area button
        ">关联 spec<",  # link button
        ">引用 requirement 段<",  # text-range button
    ],
)
def test_workbench_html_carries_domain_label(label: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert label in html, f"missing domain-anchored label: {label}"


def test_workbench_html_default_active_tool_uses_domain_label() -> None:
    """Pre-hydration default in #workbench-annotation-active-tool must use
    the domain label rather than the generic "Point tool active"."""
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert "标记信号 工具激活" in html


# ─── 2. Generic UI-type labels removed ───────────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        ">Annotation<",
        ">Point<",
        ">Area<",
        ">Link<",
        ">Text Range<",
        "Point tool active",
    ],
)
def test_workbench_html_drops_stale_generic_label(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale generic label still present: {stale}"


# ─── 3. Underlying data-annotation-tool tokens preserved ────────────
#
# Per E11-00-PLAN row E11-04: relabel touches *visible copy only*. The
# data-annotation-tool tokens are anchors for annotation_overlay.js
# click handlers and any e2e selectors, so they MUST stay stable.


@pytest.mark.parametrize(
    "anchor",
    [
        'data-annotation-tool="point"',
        'data-annotation-tool="area"',
        'data-annotation-tool="link"',
        'data-annotation-tool="text-range"',
        'id="workbench-annotation-toolbar"',
        'id="workbench-annotation-active-tool"',
    ],
)
def test_workbench_html_preserves_stable_tool_anchor(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-04 broke stable annotation anchor: {anchor}"


# ─── 4. annotation_overlay.js status template uses domain labels ────


def test_annotation_overlay_uses_tool_domain_label_map() -> None:
    js = (STATIC_DIR / "annotation_overlay.js").read_text(encoding="utf-8")
    assert "TOOL_DOMAIN_LABEL" in js
    # Each tool ID must map to its domain label.
    assert '"point": "标记信号"' in js
    assert '"area": "圈选 logic gate"' in js
    assert '"link": "关联 spec"' in js
    assert '"text-range": "引用 requirement 段"' in js
    # The status template must use the label, not the raw tool ID.
    assert "${label} 工具激活" in js
    # The old generic template must not remain in the file.
    assert "${tool} tool active" not in js


# ─── 5. Live-served /workbench reflects the relabel end-to-end ──────


def test_workbench_route_serves_relabel(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # New domain labels
    assert ">标记信号<" in html
    assert ">圈选 logic gate<" in html
    assert ">关联 spec<" in html
    assert ">引用 requirement 段<" in html
    # Stable anchors still served
    assert 'data-annotation-tool="point"' in html
    assert 'data-annotation-tool="text-range"' in html
