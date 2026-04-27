"""P52-01 — left tool dock + drawer layout.

Locks down: workbench.html carries a fixed left-side <nav class=
"workbench-dock"> with 4 tool buttons (新建/批注/审批/监控). Each
existing collaboration section (suggestion-flow, annotation-inbox,
bottom-bar, pending-signoff, approval-center, live-log) is tagged
`data-dock-section=...` and `hidden`, so the page renders as a
clean canvas (just topbar + circuit hero) until a dock button
activates a tool. CSS supplies the slide-in drawer; JS toggles
body[data-active-tool].

Pure-text assertions over the static files — no live HTTP server
needed. Live-server smoke is covered by the existing P44-01 test.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def _html():
    return HTML_PATH.read_text(encoding="utf-8")


def _css():
    return CSS_PATH.read_text(encoding="utf-8")


def _js():
    return JS_PATH.read_text(encoding="utf-8")


# ─── 1. dock element + 4 buttons ─────────────────────────────────


def test_dock_nav_present():
    html = _html()
    assert 'id="workbench-dock"' in html
    assert 'class="workbench-dock"' in html


@pytest.mark.parametrize(
    "target,label",
    [
        ("new", "新建"),
        ("annotate", "批注"),
        ("approve", "审批"),
        ("monitor", "监控"),
    ],
)
def test_dock_button_for_each_tool(target, label):
    html = _html()
    needle = f'data-dock-target="{target}"'
    assert needle in html, f"workbench.html missing dock button for {target}"
    # Label must appear too — operator reads it on hover, but it's also
    # always-visible under the icon at this dock width.
    assert label in html, f"workbench.html missing dock label {label}"


def test_body_carries_active_tool_attribute():
    """body[data-active-tool=""] is the initial state. JS will set it
    when the user clicks a dock button. Without the attribute the CSS
    selector body[data-active-tool="X"] never matches."""
    html = _html()
    assert 'data-active-tool=""' in html


# ─── 2. existing sections are tagged + hidden by default ─────────


@pytest.mark.parametrize(
    "section_id,tool",
    [
        ("workbench-suggestion-flow", "annotate"),
        ("annotation-inbox", "approve"),
        ("workbench-bottom-bar", "approve"),
        ("workbench-pending-signoff-affordance", "approve"),
        ("approval-center-panel", "approve"),
        ("workbench-live-log-panel", "monitor"),
        ("workbench-tool-new", "new"),
    ],
)
def test_section_tagged_with_dock_section(section_id, tool):
    """Every panel that should live behind a dock button MUST carry
    data-dock-section=<tool>. Without it the CSS rule
    `body[data-active-tool="X"] [data-dock-section="X"]` doesn't
    match and the section never appears."""
    html = _html()
    # Find the opening tag of the section by id and assert both
    # data-dock-section AND hidden appear within it.
    pattern = re.compile(
        r'(<\w+[^>]*\bid="' + re.escape(section_id) + r'"[^>]*>)',
        re.DOTALL,
    )
    match = pattern.search(html)
    assert match is not None, f"section #{section_id} missing"
    opening = match.group(1)
    assert f'data-dock-section="{tool}"' in opening, (
        f"section #{section_id} missing data-dock-section={tool!r}; "
        f"opening tag was: {opening[:200]}"
    )
    assert "hidden" in opening, (
        f"section #{section_id} must be `hidden` by default so the "
        f"page renders clean until a dock tool is activated"
    )


# ─── 3. CSS provides drawer styling + dock layout ────────────────


def test_css_declares_dock_layout():
    css = _css()
    # Dock is a fixed left strip — these are the load-bearing rules.
    assert ".workbench-dock {" in css
    assert "position: fixed" in css
    # Body must reserve space for the dock so canvas content doesn't
    # slide under it.
    assert "padding-left: var(--workbench-dock-width)" in css


def test_css_drawer_activation_rules():
    """The slide-in CSS that says `when active-tool=X is set on
    body, show the matching section as a fixed-position drawer`.
    Without these the dock buttons would tag body but nothing would
    render."""
    css = _css()
    for tool in ("annotate", "approve", "monitor", "new"):
        needle = (
            f'body[data-active-tool="{tool}"] [data-dock-section="{tool}"]'
        )
        assert needle in css, (
            f"CSS missing slide-in rule for tool={tool!r}"
        )


def test_css_drawer_close_button_styled():
    css = _css()
    assert ".workbench-tool-drawer-close" in css


# ─── 4. JS wires dock clicks ─────────────────────────────────────


def test_js_attaches_dock_handler():
    js = _js()
    # IIFE with the boot name is the load-bearing entry point.
    assert "_wbDockBoot" in js
    # Click handler must read data-dock-target and write
    # body.dataset.activeTool.
    assert 'getAttribute("data-dock-target")' in js
    assert "dataset.activeTool" in js


def test_js_toggles_aria_pressed_on_buttons():
    """For accessibility, the active dock button MUST set aria-pressed=true.
    Screen readers rely on this; visual tests caught regressions before
    in P49-02b. The handler also resets the others to false."""
    js = _js()
    assert 'aria-pressed' in js
    assert '"true"' in js and '"false"' in js


def test_js_handles_close_via_data_attribute():
    """Each drawer's × button has data-dock-close. Event delegation
    on document keeps this O(1) regardless of how many drawers
    exist."""
    js = _js()
    assert 'data-dock-close' in js


def test_js_supports_escape_to_close():
    """Esc is the standard dismiss key for overlays. Skipping it
    feels janky to keyboard users."""
    js = _js()
    assert '"Escape"' in js or "'Escape'" in js


# ─── 5. Canvas stays visually intact ─────────────────────────────


def test_circuit_hero_remains_in_main_canvas():
    """The whole point of P52-01: when no tool is active, the
    circuit panel is the only thing the user sees in the canvas.
    The hero MUST NOT have been wrapped into a dock-section."""
    html = _html()
    pattern = re.compile(
        r'<\w+[^>]*\bid="workbench-circuit-hero"[^>]*>',
        re.DOTALL,
    )
    match = pattern.search(html)
    assert match is not None, "circuit hero opening tag missing"
    opening = match.group(0)
    assert "data-dock-section" not in opening, (
        "circuit-hero must NOT be a dock-section — it's the always-"
        "visible canvas; the dock drawer slides over it."
    )


def test_topbar_stays_outside_dock_sections():
    """Same logic as circuit-hero: the topbar carries identity +
    truth-engine SHA + ticket number; hiding it behind a dock
    button would force the operator to click a tool just to
    confirm what version they're looking at."""
    html = _html()
    pattern = re.compile(
        r'<section[^>]*\bid="workbench-topbar"[^>]*>',
        re.DOTALL,
    )
    match = pattern.search(html)
    assert match is not None, "topbar missing"
    assert "data-dock-section" not in match.group(0)
