"""P53-02 — drawer typography polish + flatten approve hierarchy.

User feedback: the annotate/approve drawers still don't feel
Claude.app-grade. Two structural causes:
1. The approve drawer stacks FIVE headers (drawer header + inbox
   aside header + governance + plan-timeline + approval-center).
   The visual rhythm reads as "form filed in a folder filed in a
   folder" — Claude.app keeps a single header per drawer.
2. Tokens still tinted cyan everywhere (hairlines, drawer bg).
   Claude.app's dark mode is near-monochrome neutral; cyan is
   reserved for the accent (focus ring + primary CTA).
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")


# ─── 1. hairline token is neutral, not cyan-tinted ─────────────


def test_hairline_token_is_neutral():
    """The --wb-hairline token should be neutral white-tint, not
    cyan-tinted. Cyan-tinted hairlines visually scream "tech demo";
    Claude.app uses neutral grays for separators and reserves the
    accent for focus + active states only."""
    rule = re.search(
        r':root\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    hairline_match = re.search(
        r'--wb-hairline:\s*([^;]+);',
        body,
    )
    assert hairline_match is not None
    value = hairline_match.group(1).strip()
    # Neutral = either the legacy white-rgba OR the new alias chain
    # `var(--hairline)`, where `--hairline` is itself declared
    # as color-mix off --contrast (NOT --accent) — so the semantic
    # contract "hairline does NOT carry the brand tint" still holds.
    is_neutral = (
        "rgba(255, 255, 255" in value
        or "rgba(255,255,255" in value
        or "var(--hairline)" in value
    )
    assert is_neutral, (
        f"--wb-hairline should be neutral white-tint, got: {value}"
    )
    # If it's the alias chain, also confirm --hairline is declared
    # off --contrast (the strict contract for "neutral").
    if "var(--hairline)" in value:
        h_rule = re.search(r"^\s*--hairline\s*:\s*([^;]+);", CSS, re.MULTILINE)
        assert h_rule is not None, "--hairline alias target must be declared"
        h_value = h_rule.group(1).strip()
        assert "var(--contrast)" in h_value, (
            f"--hairline must derive from --contrast (neutral), got: {h_value}"
        )


# ─── 2. drawer h2 uses lighter weight ──────────────────────────


def test_drawer_h2_uses_medium_weight():
    """Drawer h2 should be weight 500 (medium), not 600 (semibold).
    Claude.app drawer titles are quiet, not declarative."""
    rule = re.search(
        r'\.workbench-tool-drawer-header\s+h2(?![\w-])[^{]*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    weight = re.search(r'font-weight:\s*(\d+)', body)
    assert weight is not None, (
        f"drawer h2 needs explicit font-weight; rule body: {body[:300]!r}"
    )
    w = int(weight.group(1))
    assert w <= 500, (
        f"drawer h2 weight should be ≤500; got {w}"
    )


# ─── 3. drawer eyebrow uses tighter letter-spacing ─────────────


def test_drawer_eyebrow_letter_spacing_loosened():
    """Eyebrow letter-spacing was 0.08em — feels like a 1990s
    architectural-firm logo. Claude.app uses 0.03–0.05em for
    uppercase eyebrows."""
    rule = re.search(
        r'\.workbench-tool-drawer-header\s+\.eyebrow\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    ls = re.search(r'letter-spacing:\s*([\d.]+)em', body)
    assert ls is not None
    val = float(ls.group(1))
    assert val <= 0.05, (
        f"eyebrow letter-spacing should be ≤0.05em; got {val}em"
    )


# ─── 4. close-button × is smaller ──────────────────────────────


def test_drawer_close_btn_is_smaller():
    """The × glyph at 1.15rem is too prominent — competes with
    the drawer title. Drop to ~1rem so it reads as ancillary."""
    rule = re.search(
        r'\.workbench-tool-drawer-close\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    fs = re.search(r'font-size:\s*([\d.]+)rem', body)
    assert fs is not None
    val = float(fs.group(1))
    assert val <= 1.05, (
        f"drawer close × font-size should be ≤1.05rem; got {val}rem"
    )


# ─── 5. approve drawer drops the redundant inbox aside header ──


def test_approve_drawer_inbox_aside_no_inner_header():
    """The drawer wrapper #workbench-tool-approve already announces
    "审批中心 · Approval Center" via its drawer header. The inner
    #annotation-inbox aside used to carry its OWN header (eyebrow
    + h2 "审核队列" + refresh button) — that's two-level hierarchy
    inside one drawer. P53-02 drops the inbox aside's <header>;
    the refresh button moves up into the drawer header (or floats
    inline above the list)."""
    aside_match = re.search(
        r'<aside[^>]*id="annotation-inbox"[^>]*>(.*?)</aside>',
        HTML,
        re.DOTALL,
    )
    assert aside_match is not None, "annotation-inbox aside missing"
    aside_block = aside_match.group(0)
    # The aside should NOT carry an immediate <header> child anymore.
    has_inner_header = re.search(
        r'<aside[^>]*>\s*<header\b',
        aside_block,
        re.DOTALL,
    )
    assert has_inner_header is None, (
        "annotation-inbox aside still has its own <header> — that "
        "duplicates the approve drawer's header. Drop it."
    )


def test_inbox_refresh_button_still_present():
    """The refresh button must survive the header removal — JS binds
    to its id."""
    assert 'id="annotation-inbox-refresh-btn"' in HTML, (
        "annotation-inbox-refresh-btn id must survive the P53-02 "
        "header simplification (workbench.js binds to it)"
    )


# ─── 6. textarea font matches button font (visual coherence) ───


def test_textarea_font_size_matches_buttons():
    """At 0.82rem the suggestion textarea reads bigger than the
    drawer-scoped buttons (0.78rem after P53-01). Bring it in line
    so the form has consistent visual weight."""
    rule = re.search(
        r'\.workbench-suggestion-input\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    fs = re.search(r'font-size:\s*([\d.]+)rem', body)
    assert fs is not None
    val = float(fs.group(1))
    assert val <= 0.8, (
        f"suggestion textarea font-size should be ≤0.8rem to match "
        f"drawer buttons; got {val}rem"
    )
