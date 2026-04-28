"""P52-02 — workbench dock visual polish.

Locks in the design tokens borrowed from Claude.app:
- inline SVG icons (no emoji on dock buttons)
- 168ms cubic-bezier(.32,.72,0,1) transitions
- 12% accent fill + 28% accent border for active state
- 0 12px 28px @ 32% drawer shadow (was 8px 0 32px @ 45%)
- hairline borders 0.10 alpha
- dock label 0.7rem (~11px)
- slide-in opacity + translateX(-12px → 0) keyframe animation
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


# ─── 1. inline SVG icons replace emoji ───────────────────────────


@pytest.mark.parametrize("target", ["new", "annotate", "approve", "monitor"])
def test_dock_button_uses_inline_svg(target):
    """Each dock button MUST carry an SVG icon, not an emoji span.
    Emoji rendering varies wildly across OS/browser; SVG owns its
    look and inherits currentColor for active-state tinting."""
    pattern = re.compile(
        r'data-dock-target="' + re.escape(target) + r'".*?<svg',
        re.DOTALL,
    )
    assert pattern.search(HTML) is not None, (
        f"dock button for {target} must contain an inline <svg>; "
        f"emoji-based icons no longer pass design review"
    )


@pytest.mark.parametrize("target", ["new", "annotate", "approve", "monitor"])
def test_dock_button_no_emoji_in_icon_slot(target):
    """Specifically reject the original emoji set so a regression
    catches a "I'll just put back 🆕" mistake at PR time."""
    forbidden = ("🆕", "✏️", "✅", "📊")
    pattern = re.compile(
        r'data-dock-target="' + re.escape(target) + r'"(.*?)</button>',
        re.DOTALL,
    )
    match = pattern.search(HTML)
    assert match is not None, f"dock button {target} not found"
    block = match.group(1)
    for emoji in forbidden:
        assert emoji not in block, (
            f"dock button {target} carries forbidden emoji {emoji!r}; "
            f"swap to inline SVG (P52-02 north star)"
        )


def test_dock_svg_uses_currentcolor_stroke():
    """Icons MUST inherit currentColor so the active-state recolor
    works without per-state SVG variants."""
    # All four dock SVGs in a single check — at least one
    # `stroke="currentColor"` must appear inside the dock nav block.
    nav_match = re.search(
        r'<nav id="workbench-dock"[^>]*>(.*?)</nav>',
        HTML, re.DOTALL,
    )
    assert nav_match is not None, "dock nav not found"
    block = nav_match.group(1)
    assert 'stroke="currentColor"' in block, (
        "dock SVG icons must use stroke=currentColor for theme inheritance"
    )


# ─── 2. CSS tokens match the north star ──────────────────────────


def test_css_declares_motion_token():
    assert "--wb-ease-out" in CSS
    assert "cubic-bezier(0.32, 0.72, 0, 1)" in CSS
    assert "--wb-duration-drawer" in CSS
    assert "168ms" in CSS


def test_css_declares_warm_dock_bg():
    """Dock bg must be a faintly-warm dark surface. P55-01 migrated
    the literal #0E1320 to a color-mix derivation off --base, so the
    contract is now "the token is declared + resolves to something
    near-base (not pure black, not random)" — the literal-hex check
    locked in P52-02 belonged to the pre-LCH world."""
    rule = re.search(r"--wb-dock-bg:\s*([^;]+);", CSS)
    assert rule is not None, "--wb-dock-bg must be declared"
    value = rule.group(1).strip()
    # Either the original literal (compat) OR the LCH derivation.
    is_valid = (
        "#0E1320" in value
        or ("color-mix" in value and "var(--base)" in value)
    )
    assert is_valid, f"--wb-dock-bg should be near-base; got: {value}"


def test_css_active_fill_and_border():
    """Active state = 12% accent fill + 28% accent border (subdued
    per Claude.app). P55-01 expressed both via --accent-tint-12 /
    --accent-tint-28 derivations of the new --accent token; either
    spelling satisfies the contract."""
    has_12 = (
        "rgba(103, 232, 249, 0.12)" in CSS
        or "--accent-tint-12" in CSS
        or "color-mix(in lch, var(--accent) 12%" in CSS
    )
    has_28 = (
        "rgba(103, 232, 249, 0.28)" in CSS
        or "--accent-tint-28" in CSS
        or "color-mix(in lch, var(--accent) 28%" in CSS
    )
    assert has_12, "12% accent fill must be expressed via token or literal"
    assert has_28, "28% accent border must be expressed via token or literal"


def test_css_drawer_shadow_softened():
    """Drawer shadow must be the soft 0 12px 28px @ 32%, not the
    theatrical 8px 0 32px @ 45% from v1."""
    assert "0 12px 28px rgba(0, 0, 0, 0.32)" in CSS
    # Also assert the v1 shadow is gone.
    assert "8px 0 32px rgba(0, 0, 0, 0.45)" not in CSS


def test_css_drawer_uses_motion_tokens():
    """The drawer activation rules MUST use the new motion tokens
    (not the `--duration-fast` / `--ease-standard` defaults)."""
    # The drawer animation block specifically:
    match = re.search(
        r"animation:\s*wbDrawerEnter\s+var\(--wb-duration-drawer\)\s+var\(--wb-ease-out\)",
        CSS,
    )
    assert match is not None, (
        "drawer activation must use --wb-duration-drawer + --wb-ease-out"
    )


def test_css_drawer_keyframe_present():
    """The slide-in keyframe must define both opacity + translateX."""
    keyframe_match = re.search(
        r"@keyframes\s+wbDrawerEnter\s*\{[^}]*from\s*\{[^}]*opacity\s*:\s*0[^}]*translateX\(-12px\)",
        CSS,
        re.DOTALL,
    )
    assert keyframe_match is not None, (
        "wbDrawerEnter keyframe must fade in from opacity:0 + translateX(-12px)"
    )


def test_css_dock_label_is_readable_size():
    """The v1 dock label was 0.62rem (~9.92px) — too small to read
    quickly. v2 ladder calls for 0.7rem (~11px) so the labels are
    actually usable without hover tooltips."""
    # Look specifically inside .workbench-dock-btn-label rule
    rule = re.search(
        r"\.workbench-dock-btn-label\s*\{[^}]*\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "0.7rem" in body, (
        f"dock label should be 0.7rem; found rule: {body[:200]!r}"
    )


def test_css_hairline_border_token():
    """Hairlines use the --wb-hairline token. P53-02 made the token
    neutral (not cyan-tinted); P55-01 derived it from --contrast at
    8% via color-mix(in lch, ...) so the contract is now
    "derives from contrast, not accent" — the semantic guarantee
    that hairlines aren't tinted by the brand color."""
    rule = re.search(r"--wb-hairline:\s*([^;]+);", CSS)
    assert rule is not None, "--wb-hairline must remain declared"
    value = rule.group(1).strip()
    # Accept either the original literal OR the new derivation chain.
    is_neutral = (
        "rgba(255, 255, 255" in value
        or "var(--hairline)" in value  # alias chain → derives from --contrast
    )
    assert is_neutral, (
        f"--wb-hairline must be neutral (contrast-derived, not accent); "
        f"got {value!r}"
    )
    # The drawer + dock now reference --wb-hairline (not the old
    # raw rgba values). Spot-check by hunting inside the dock rule.
    dock_rule = re.search(
        r"\.workbench-dock\s*\{[^}]*\}",
        CSS,
        re.DOTALL,
    )
    assert dock_rule is not None
    assert "var(--wb-hairline)" in dock_rule.group(0)


def test_css_drawer_radius_right_edge_only():
    """Drawer is anchored to dock's right edge; only its RIGHT
    corners round (12px). Top-left/bottom-left stay flush against
    the dock for that 'continuation' feel."""
    activation = re.search(
        r"body\[data-active-tool=\"annotate\"\][^{]*\{[^}]*\}",
        CSS,
        re.DOTALL,
    )
    assert activation is not None
    # `border-radius: 0 12px 12px 0` = top-right + bottom-right rounded only.
    assert "border-radius: 0 12px 12px 0" in activation.group(0)


# ─── 3. Drawer header typography ─────────────────────────────────


def test_drawer_header_eyebrow_is_uppercase_small():
    """P53-02 retuned the eyebrow: 0.7rem → 0.65rem font (matches
    the inbox toolbar label) + 0.08em → 0.04em letter-spacing
    (Claude.app eyebrows use loose-but-not-architectural tracking)."""
    rule = re.search(
        r"\.workbench-tool-drawer-header\s+\.eyebrow\s*\{[^}]*\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "text-transform: uppercase" in body
    # Either 0.65rem or 0.7rem (the next sub-phase may revisit), but
    # not larger.
    assert "0.65rem" in body or "0.7rem" in body
    # Letter-spacing tightened — 0.04em is the new default.
    assert "letter-spacing: 0.04em" in body or "letter-spacing: 0.05em" in body


def test_drawer_header_close_button_focusable():
    """A11y hard requirement: close button MUST have focus-visible
    outline so keyboard users can dismiss the drawer."""
    rule = re.search(
        r"\.workbench-tool-drawer-close:focus-visible\s*\{[^}]*\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "drawer close button missing :focus-visible outline"
    )
    assert "outline" in rule.group(0)
