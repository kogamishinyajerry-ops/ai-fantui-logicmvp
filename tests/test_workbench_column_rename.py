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
        # E11-15c flipped to Chinese-first to match the rest of the page;
        # English suffix preserved so substring locks still pass.
        "探针与追踪 · Probe &amp; Trace",
        "标注与提案 · Annotate &amp; Propose",
        "移交与跟踪 · Hand off &amp; Track",
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


# ─── 2b. New pre-hydration boot-status copy is POSITIVELY locked ──────
#
# P4 R1 IMPORTANT fix: rows 7/9/11 of the surface inventory cover the
# pre-hydration "Waiting for ... panel boot." strings. R1 only verified
# absence of the stale copy; R2 also asserts presence of the new copy
# so a drift to any other phrasing would fail the suite.


@pytest.mark.parametrize(
    "boot_status",
    [
        "Waiting for probe &amp; trace panel boot.",
        "Waiting for annotate &amp; propose panel boot.",
        "Waiting for hand off &amp; track panel boot.",
    ],
)
def test_workbench_html_carries_new_boot_status(boot_status: str) -> None:
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert boot_status in html, f"missing renamed pre-hydration boot status: {boot_status}"


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


# P4 R1 NIT fix: lock the FULL hydrated boot-status sentence (not just
# the "X ready" prefix), so future drift in the staging note is also
# caught. P5 R1 IMPORTANT fix: the strings must NOT contain internal
# roadmap tokens like "E07+" or "E07".


@pytest.mark.parametrize(
    "boot_copy",
    [
        "Probe & Trace ready. Scenario actions are staged for the next bundle.",
        "Annotate & Propose ready. Text-range annotation is staged for the next bundle.",
        "Hand off & Track ready. Overlay annotation is staged for the next bundle.",
    ],
)
def test_workbench_js_boot_status_uses_new_names(boot_copy: str) -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert boot_copy in js, f"workbench.js boot status missing exact string: {boot_copy}"


def test_workbench_js_boot_status_drops_stale_names() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # Old boot copy must NOT appear, otherwise the visible chrome and the
    # status messages will disagree.
    assert "Control panel ready" not in js
    assert "Document panel ready" not in js
    assert "Circuit panel ready" not in js


def test_workbench_js_boot_status_drops_internal_phase_tokens() -> None:
    """P5 R1 IMPORTANT fix: roadmap tokens like 'E07+'/'E07' must not
    leak into user-visible boot status strings."""
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # Scope the check to the three boot functions to avoid false
    # positives in unrelated comments/blocks.
    for fn in (
        "bootWorkbenchControlPanel",
        "bootWorkbenchDocumentPanel",
        "bootWorkbenchCircuitPanel",
    ):
        anchor = js.find(f"function {fn}")
        assert anchor != -1, f"missing function {fn}"
        slice_ = js[anchor : anchor + 600]
        assert "E07" not in slice_, (
            f"internal phase token 'E07' leaked into {fn} boot status"
        )


# P1 R1 NIT fix: failure-path fallback must use the engineer-task verb,
# not the internal columnName token.


def test_workbench_js_failure_fallback_uses_task_verb_label() -> None:
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    # WORKBENCH_COLUMN_LABEL maps control/document/circuit → task verbs
    assert "WORKBENCH_COLUMN_LABEL" in js
    assert '"control": "Probe & Trace"' in js or 'control: "Probe & Trace"' in js
    assert '"document": "Annotate & Propose"' in js or 'document: "Annotate & Propose"' in js
    assert '"circuit": "Hand off & Track"' in js or 'circuit: "Hand off & Track"' in js
    # Failure copy must reference the label, not the raw columnName.
    assert "${label} panel failed independently" in js, (
        "failure fallback should use the engineer-task verb label, not the raw column token"
    )


# ─── 5. Live-served /workbench reflects the rename end-to-end ───────


def test_workbench_route_serves_renamed_columns(server) -> None:
    status, html = _get(server, "/workbench")
    assert status == 200
    # E11-15c flipped these from English-first to Chinese-first.
    assert "探针与追踪 · Probe &amp; Trace" in html
    assert "标注与提案 · Annotate &amp; Propose" in html
    assert "移交与跟踪 · Hand off &amp; Track" in html
    # Stable anchors still served
    assert 'id="workbench-control-panel"' in html
    assert 'data-column="circuit"' in html
