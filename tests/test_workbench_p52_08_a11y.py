"""P52-08 — accessibility audit for the dock + drawer surfaces.

Covers:
- Drawer regions are labelled (aria-labelledby points at the h2)
- Close buttons have accessible names (× alone is unreadable to SR)
- Dock buttons + close buttons + template cards have :focus-visible
- No positive tabindex anywhere (would break logical tab order)
- JS drawer activation moves focus into the drawer (so keyboard
  users land where their click would have)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")
JS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js").read_text(encoding="utf-8")


# ─── 1. drawer regions are labelled ──────────────────────────────


@pytest.mark.parametrize(
    "section_id,heading_id",
    [
        ("workbench-tool-monitor", "workbench-tool-monitor-title"),
        ("workbench-tool-approve", "workbench-tool-approve-title"),
        ("workbench-tool-new", "workbench-tool-new-title"),
        ("workbench-suggestion-flow", "workbench-suggestion-flow-title"),
    ],
)
def test_drawer_uses_aria_labelledby(section_id, heading_id):
    """Each drawer's <section> must declare aria-labelledby pointing
    at its h2 id, so screen readers announce the region by name on
    focus entry."""
    open_tag = re.search(
        r'<section[^>]*\bid="' + re.escape(section_id) + r'"[^>]*>',
        HTML,
    )
    assert open_tag is not None, f"section #{section_id} missing"
    tag = open_tag.group(0)
    assert (
        f'aria-labelledby="{heading_id}"' in tag
    ), (
        f"section #{section_id} must declare "
        f"aria-labelledby=\"{heading_id}\"; opening tag was: "
        f"{tag[:200]}"
    )


# ─── 2. close buttons have accessible names ──────────────────────


def test_drawer_close_buttons_have_aria_label():
    """× by itself is unreadable to screen readers. Each close
    button (data-dock-close) must declare aria-label="关闭抽屉" or
    similar so SR users hear what the X does."""
    matches = re.findall(
        r'<button[^>]*data-dock-close[^>]*>',
        HTML,
    )
    assert len(matches) >= 4, (
        f"expected at least 4 drawer close buttons; found "
        f"{len(matches)}"
    )
    for tag in matches:
        assert "aria-label" in tag, (
            f"close button missing aria-label: {tag}"
        )


# ─── 3. focus-visible coverage on key interactive surfaces ───────


@pytest.mark.parametrize(
    "selector",
    [
        ".workbench-dock-btn",
        ".workbench-tool-drawer-close",
        ".workbench-new-circuit-template-card",
        ".workbench-suggestion-input",
        ".workbench-new-circuit-input",
    ],
)
def test_focus_visible_rule_exists(selector):
    """Every interactive surface MUST have a :focus-visible rule
    so keyboard navigation is visible. We don't pin exact colors;
    just that the rule exists."""
    pattern = re.compile(
        re.escape(selector) + r':focus(?:-visible)?\s*\{[^}]*\}',
        re.DOTALL,
    )
    rules = pattern.findall(CSS)
    assert len(rules) > 0, (
        f"no :focus or :focus-visible rule for {selector}"
    )


# ─── 4. no positive tabindex (would break logical tab order) ─────


def test_no_positive_tabindex_in_html():
    """Positive tabindex (e.g. tabindex=1) hijacks the natural
    document order and is an accessibility footgun. Allowed values:
    -1 (programmatically focusable, not in tab order) and 0."""
    matches = re.findall(r'tabindex="(-?\d+)"', HTML)
    for v in matches:
        assert int(v) <= 0, (
            f"workbench.html uses tabindex=\"{v}\" — positive values "
            f"break the natural tab order; use 0 or -1 instead"
        )


# ─── 5. drawer activation moves focus into the drawer ────────────


def test_drawer_activation_moves_focus():
    """When a dock button activates a drawer, JS must move focus
    into the drawer — typically to the close button or the first
    interactive child. Otherwise keyboard users open a drawer and
    are stranded outside it."""
    # Look for either a focus() call inside the dock activation
    # function or a dedicated focus-trap helper.
    focus_in_dock = (
        "drawer.focus()" in JS
        or 'querySelector("[data-dock-close]")' in JS
        or "_wbDrawerFocusEntry" in JS
        or 'firstFocusable' in JS
    )
    assert focus_in_dock, (
        "no evidence of focus management when a drawer activates; "
        "expected something like `drawer.focus()` or "
        "`drawer.querySelector('[data-dock-close]').focus()` in "
        "the dock boot"
    )
