"""P53-01 — fix the default-state drawer leak + tighten button/input
sizing across all dock drawers to match Claude.app aesthetics.

Two issues the user reported on the post-P53-00 deploy:
1. The "新建" (new-circuit) drawer panel was painting at the top of
   the canvas in the default state, violating the pure-circuit rule.
   Root cause: `body[data-active-tool] [data-dock-section][hidden]`
   matches whenever body has the attribute *at all*, including when
   JS sets `data-active-tool=""` after a drawer closes (P52-07's
   auto-close timeout did exactly this).
2. The annotate/approve drawer CTAs were oversized, pill-shaped,
   gradient-filled — none of which match Claude.app's flat, square,
   solid-color button language.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


# ─── 1. the broken [hidden]-override rule is now scoped per pair ───


def test_hidden_override_rule_is_pair_specific():
    """The override rule that lifts the `hidden` attribute must
    only fire for the matching tool/section pair, not for
    body[data-active-tool] in general (which matches even when the
    attribute value is empty)."""
    bad = re.search(
        r'^body\[data-active-tool\]\s+\[data-dock-section\]\[hidden\]\s*\{',
        CSS,
        re.MULTILINE,
    )
    assert bad is None, (
        "The unscoped `body[data-active-tool] [data-dock-section]"
        "[hidden]` rule still exists. It matches body[data-active-tool="
        "''], so closing one drawer leaks ALL hidden drawers into the "
        "main flow. Replace with per-tool pairs."
    )


def test_hidden_override_rule_per_tool_pair_exists():
    """Each tool/section pair must explicitly override [hidden]
    when the matching tool is active. Confirms the fix is in place."""
    expected_pairs = [
        ('annotate', 'annotate'),
        ('approve', 'approve'),
        ('monitor', 'monitor'),
        ('new', 'new'),
    ]
    for tool, section in expected_pairs:
        pattern = re.compile(
            r'body\[data-active-tool="' + tool + r'"\]\s+'
            r'\[data-dock-section="' + section + r'"\]\[hidden\]',
        )
        assert pattern.search(CSS), (
            f"missing [hidden] override for tool={tool} section={section}"
        )


# ─── 2. tighter button sizing inside drawers ─────────────────────


def test_drawer_scoped_button_is_tightened():
    """Inside a dock drawer, `.workbench-toolbar-button` must be
    tighter than the global default (which uses 0.75rem 1rem padding
    + pill radius). Claude.app aesthetic: ~0.4rem padding, ~6-8px
    radius, font ≤0.85rem."""
    # Look for any rule whose selector list contains
    # `.workbench-tool-drawer-section .workbench-toolbar-button`. The
    # selector may be in a comma-separated group with related buttons.
    rule = re.search(
        r'(?:[^{}]*\.workbench-tool-drawer-section\s+\.workbench-toolbar-button[^{}]*)\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "expected a drawer-scoped override for .workbench-toolbar-button"
    )
    body = rule.group(0)
    # Padding shouldn't be larger than 0.55rem on the y-axis.
    pad_match = re.search(r'padding:\s*([\d.]+)rem', body)
    assert pad_match is not None, (
        f"drawer button padding must be set explicitly; rule body: "
        f"{body[:300]!r}"
    )
    pad_y = float(pad_match.group(1))
    assert pad_y <= 0.55, (
        f"drawer button y-padding should be ≤0.55rem (Claude.app "
        f"is ~6-7px); got {pad_y}rem"
    )
    # Border-radius should be square-ish, not pill (999px).
    assert "999px" not in body, (
        "drawer button must NOT use pill radius (999px); use 6-8px"
    )


def test_drawer_primary_button_loses_gradient():
    """Claude.app primaries are solid color, not gradients. The
    teal-on-teal `is-primary` gradient is too loud for the drawer."""
    rule = re.search(
        r'\.workbench-tool-drawer-section\s+\.workbench-toolbar-button\.is-primary\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "expected a drawer-scoped override for the primary CTA"
    )
    body = rule.group(0)
    assert "linear-gradient" not in body, (
        f"drawer primary button must use a solid background, not a "
        f"gradient; rule body: {body[:300]!r}"
    )


def test_drawer_button_uses_accent_token_not_raw_teal():
    rule = re.search(
        r'\.workbench-tool-drawer-section\s+\.workbench-toolbar-button\.is-primary\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert (
        "var(--accent" in body
        or "var(--wb-active-border" in body
        or "rgba(103, 232, 249" in body
    ), (
        f"drawer primary should derive from --accent (cyan); rule "
        f"body: {body[:300]!r}"
    )


# ─── 3. inputs/textareas in drawers stay compact ─────────────────


def test_textarea_height_is_compact():
    """The suggestion textarea defaults to rows=3 in HTML, but the
    CSS shouldn't add visual heft via excessive line-height or
    min-height."""
    rule = re.search(
        r'\.workbench-suggestion-input\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    # font-size must be ≤0.82rem
    fs = re.search(r'font-size:\s*([\d.]+)rem', body)
    assert fs is not None
    assert float(fs.group(1)) <= 0.85, (
        f"textarea font-size should be ≤0.85rem; got {fs.group(1)}rem"
    )
