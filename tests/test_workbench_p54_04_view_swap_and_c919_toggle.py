"""P54-04 — fix view mapping + hide iframe nav + add C919 toggle.

Three user-reported issues from P54-03:

(1) sim/cockpit mapping was wrong:
    - 仿真 (simulation) was pointing at timeline-sim.html (a generic
      timeline simulator) — should point at fan_console.html (the
      real-time operator console with adjustable parameters)
    - 演示 (cockpit) was pointing at fan_console.html — should point
      at demo.html (the actual 反推逻辑演示舱 with lever + condition
      panels — the original "control logic workstation")

(2) Iframe pages still painted their own unified-nav at the top,
    exposing extra page-level navigation that doesn't belong inside
    the workbench. Each embedded page now hides its nav when loaded
    inside the workbench iframe.

(3) The circuit view only exposed the thrust-reverser SVG — the
    C919 E-TRAS circuit had no entry. P54-04 surfaces a small
    pill toggle in the top-right of the circuit canvas to switch
    between the two systems (driving the legacy
    #workbench-system-select that was hidden in P53-00).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")
JS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js").read_text(encoding="utf-8")


# ─── 1. sim/cockpit mapping is correct ───────────────────────


@pytest.mark.parametrize(
    "panel_id,expected_iframe_src",
    [
        # 仿真 (simulation) → fan_console.html (real-time operator
        # console with parameters). Was pointing at timeline-sim.
        ("workbench-sim-panel", "/fan_console.html"),
        # 演示 (cockpit demo) → demo.html (反推逻辑演示舱 with the
        # lever + condition panels — the original "control logic
        # workstation" the user was asking for). Was pointing at
        # fan_console.
        ("workbench-cockpit-panel", "/demo.html"),
        # P54-05: spec view repointed to /workbench_spec.html (the
        # workbench-native rebuild with KPIs + REQ cards + matrix).
        # The legacy /fantui_requirements.html keeps its standalone
        # route for direct visitors.
        ("workbench-spec-panel", "/workbench_spec.html"),
    ],
)
def test_canvas_view_iframe_src_corrected(panel_id, expected_iframe_src):
    block = re.search(
        r'<section[^>]*id="' + re.escape(panel_id) + r'"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(0)
    iframe = re.search(
        r'<iframe[^>]*src="' + re.escape(expected_iframe_src) + r'(?:\?[^"]*)?"[^>]*>',
        body,
    )
    assert iframe is not None, (
        f"#{panel_id} must embed {expected_iframe_src} via <iframe>; "
        f"body sample: {body[:400]!r}"
    )


# ─── 2. embedded pages hide unified-nav when iframed ─────────


@pytest.mark.parametrize(
    "page_path",
    [
        "src/well_harness/static/fan_console.html",
        "src/well_harness/static/demo.html",
        "src/well_harness/static/fantui_requirements.html",
    ],
)
def test_embedded_page_hides_nav_when_iframed(page_path):
    """Each embedded page must include the nav-hide guard: an
    `is-iframe-embed` class added to <html> when window.self !==
    window.top OR ?embed=1 is in the URL, plus a CSS rule that
    hides .unified-nav under that class.

    P56-01 (2026-04-28): the CSS rule moved from inline <style> to
    the shared /etras_chrome.css. The check now follows the linked
    stylesheet."""
    html = (REPO_ROOT / page_path).read_text(encoding="utf-8")
    # Detection script
    assert "window.self !== window.top" in html and "is-iframe-embed" in html, (
        f"{page_path} missing the iframe-embed detection script"
    )
    # CSS hide rule — inline OR in a linked /etras_chrome.css.
    # Codex P56-01 round-1 P3: only follow the link when the page
    # actually <link>s the shared sheet, otherwise an unmigrated page
    # like demo.html could lose its inline rule and silently pass on
    # the strength of someone else's stylesheet.
    haystack = html
    if 'href="/etras_chrome.css"' in html or 'href="etras_chrome.css"' in html:
        chrome_css = (
            REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
        )
        if chrome_css.exists():
            haystack = html + "\n" + chrome_css.read_text(encoding="utf-8")
    assert (
        "html.is-iframe-embed .unified-nav" in haystack
        or ".is-iframe-embed .unified-nav" in haystack
    ), (
        f"{page_path} missing CSS rule that hides .unified-nav under "
        f".is-iframe-embed"
    )


def test_workbench_iframe_passes_embed_querystring():
    """The two legacy iframe srcs (fan_console + demo) include
    ?embed=1 — a defense-in-depth signal so the embedded page can
    suppress its unified-nav. /workbench_spec.html is workbench-
    native and has no nav to hide, so it doesn't need the param."""
    for src_base in ("/fan_console.html", "/demo.html"):
        match = re.search(
            r'<iframe[^>]*src="' + re.escape(src_base) + r'\?embed=1"[^>]*>',
            HTML,
        )
        assert match is not None, (
            f"iframe for {src_base} must use ?embed=1 querystring"
        )


# ─── 3. C919 / Thrust-Reverser circuit toggle ────────────────


def test_circuit_canvas_has_system_toggle():
    """A visible pill toggle with both system options (反推 / C919
    E-TRAS) must exist somewhere in the workbench shell. P54-06
    promoted it from inside #workbench-circuit-hero to a canvas-
    level #workbench-system-toggle so the same pill drives all 4
    surfaces (circuit + sim + cockpit + spec)."""
    assert (
        'id="workbench-system-toggle"' in HTML
        or 'id="workbench-circuit-system-toggle"' in HTML
    ), "workbench must contain the system toggle group (canvas-level after P54-06)"
    for system in ("thrust-reverser", "c919-etras"):
        assert f'data-circuit-system="{system}"' in HTML, (
            f"missing toggle pill for system={system}"
        )


def test_system_toggle_active_state_styled():
    """The active pill (`aria-pressed=\"true\"`) must use the accent
    token so the user can see at a glance which system is loaded.
    P54-06 grouped both .workbench-system-toggle-btn (canvas-level)
    and .workbench-circuit-system-btn (legacy alias) under one rule."""
    rule = re.search(
        r'\.workbench-(?:circuit-)?system(?:-toggle)?-btn[^{]*'
        r'\[aria-pressed="true"\][^{]*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "no `.workbench-*system-*-btn[aria-pressed=true]` rule found"
    )
    body = rule.group(0)
    assert "var(--accent" in body or "rgba(103, 232, 249" in body, (
        f"active pill should derive from --accent; rule body: "
        f"{body[:200]!r}"
    )


def test_js_wires_system_toggle_to_legacy_select():
    """Toggle clicks must update the legacy #workbench-system-select
    and dispatch its change event so the existing reload path fires
    unchanged."""
    has_wiring = (
        "_wbCircuitSystemToggleBoot" in JS
        and "workbench-system-select" in JS
        and 'new Event("change"' in JS
    )
    assert has_wiring, (
        "JS must include a boot block that bridges the toggle to the "
        "legacy system-select and dispatches `change`"
    )
