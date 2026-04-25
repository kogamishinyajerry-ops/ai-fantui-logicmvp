"""E11-03 — three-column rename regression lock.

Locks the visible column titles, eyebrows, and boot status copy after
the E11-03 rename from technical nouns to engineer-task verbs:

  Scenario Control          → Probe & Trace · 探针与追踪
  Spec Review Surface       → Annotate & Propose · 标注与提案
  Logic Circuit Surface     → Hand off & Track · 移交与跟踪

Per E11-00-PLAN row E11-03: underlying IDs (data-column, panel ids,
data-annotation-surface) are intentionally stable so e2e selectors and
JS boot wiring don't break. Verify both invariants — new copy AND
preserved IDs — so a future "polish" pass can't silently regress
either side.
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


# ─── 1. New visible copy is present ──────────────────────────────────


@pytest.mark.parametrize(
    "title",
    [
        "Probe &amp; Trace · 探针与追踪",
        "Annotate &amp; Propose · 标注与提案",
        "Hand off &amp; Track · 移交与跟踪",
    ],
)
def test_workbench_html_carries_new_column_title(title: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert title in html, f"missing renamed column title: {title}"


@pytest.mark.parametrize(
    "eyebrow",
    ["probe &amp; trace", "annotate &amp; propose", "hand off &amp; track"],
)
def test_workbench_html_carries_new_eyebrow(eyebrow: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert eyebrow in html, f"missing renamed eyebrow: {eyebrow}"


# ─── 2. Old technical-noun copy removed ──────────────────────────────


@pytest.mark.parametrize(
    "stale",
    [
        "<h2>Scenario Control</h2>",
        "<h2>Spec Review Surface</h2>",
        "<h2>Logic Circuit Surface</h2>",
        ">control panel<",
        ">document<",
        ">circuit<",
        "Waiting for control panel boot.",
        "Waiting for document panel boot.",
        "Waiting for circuit panel boot.",
    ],
)
def test_workbench_html_does_not_carry_stale_column_title(stale: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert stale not in html, f"stale technical-noun copy still present: {stale}"


# ─── 3. Underlying IDs / data attributes preserved ──────────────────
#
# Per E11-00-PLAN row E11-03: rename touches *visible copy only*. The
# panel ids, data-column tokens, data-annotation-surface tokens, and
# status div ids are anchors for e2e selectors and JS boot wiring, so
# they MUST stay stable through the rename.


@pytest.mark.parametrize(
    "anchor",
    [
        'id="workbench-control-panel"',
        'id="workbench-document-panel"',
        'id="workbench-circuit-panel"',
        'data-column="control"',
        'data-column="document"',
        'data-column="circuit"',
        'data-annotation-surface="control"',
        'data-annotation-surface="document"',
        'data-annotation-surface="circuit"',
        'id="workbench-control-status"',
        'id="workbench-document-status"',
        'id="workbench-circuit-status"',
    ],
)
def test_workbench_html_preserves_stable_anchor(anchor: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert anchor in html, f"E11-03 broke stable anchor: {anchor}"


# ─── 4. JS boot status copy matches new column names ────────────────


@pytest.mark.parametrize(
    "boot_copy",
    [
        "Probe & Trace ready",
        "Annotate & Propose ready",
        "Hand off & Track ready",
    ],
)
def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert boot_copy in js, f"workbench.js boot status missing: {boot_copy}"


def test_workbench_js_boot_status_drops_stale_names() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # Old boot copy must NOT appear, otherwise the visible chrome and the
    # status messages will disagree.
    assert "Control panel ready" not in js
    assert "Document panel ready" not in js
    assert "Circuit panel ready" not in js


# ─── 5. Live-served /workbench reflects the rename end-to-end ───────


def test_workbench_route_serves_renamed_columns(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # New copy
    assert "Probe &amp; Trace · 探针与追踪" in html
    assert "Annotate &amp; Propose · 标注与提案" in html
    assert "Hand off &amp; Track · 移交与跟踪" in html
    # Stable anchors still served
    assert 'id="workbench-control-panel"' in html
    assert 'data-column="circuit"' in html
