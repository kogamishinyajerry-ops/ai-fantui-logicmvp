"""P52-04 — annotate drawer deep polish.

Brings the annotate drawer in line with the post-P52-02 visual rhythm:
- standard drawer header (eyebrow + h2 + close button) — consistent
  with monitor/approve/new drawers
- outer card chrome (`.workbench-suggestion-flow` border+bg) is
  neutralized, since the drawer itself is the visual container now
- interpretation card uses 12px radius + var(--wb-hairline) border
- suggestion-status sits right-aligned in the actions row so it
  doesn't crowd the primary CTA
- form input/textarea border uses var(--wb-hairline); focus ring uses
  the accent token, not the legacy raw color
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


def _annotate_section() -> str:
    m = re.search(
        r'<section[^>]*id="workbench-suggestion-flow"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert m is not None, "workbench-suggestion-flow section missing"
    return m.group(0)


def test_annotate_drawer_uses_standard_header():
    """Annotate drawer must lead with the canonical drawer header
    (eyebrow + h2 + close button) so it visually matches the
    monitor/approve/new drawers."""
    block = _annotate_section()
    assert "workbench-tool-drawer-header" in block, (
        "annotate drawer must use .workbench-tool-drawer-header for "
        "consistency with the other tool drawers"
    )
    # eyebrow text uses the canonical 'annotate' label
    eyebrow = re.search(
        r'<p\s+class="eyebrow">([^<]+)</p>',
        block,
    )
    assert eyebrow is not None, "annotate drawer header missing eyebrow"
    assert "annotate" in eyebrow.group(1).lower(), (
        f"annotate drawer eyebrow should contain 'annotate'; got "
        f"{eyebrow.group(1)!r}"
    )


def test_annotate_drawer_has_close_button():
    block = _annotate_section()
    assert "data-dock-close" in block, (
        "annotate drawer must include the standard close button"
    )


def test_annotate_outer_card_chrome_neutralized():
    """Inside the drawer, the legacy `.workbench-suggestion-flow`
    outer border+bg becomes a card-in-card. Strip the chrome — the
    drawer itself is the container now. We assert it via a CSS
    rule that explicitly resets border/background when the suggestion
    flow is the dock-section host."""
    rule = re.search(
        r'\.workbench-suggestion-flow\.workbench-tool-drawer-section\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "expected a CSS rule scoped to "
        "`.workbench-suggestion-flow.workbench-tool-drawer-section` "
        "to neutralize the legacy card chrome"
    )
    body = rule.group(0)
    # Either border:none, background:transparent, or padding 0 must
    # appear — we don't pin exact tokens, just that the chrome is
    # being reset.
    assert (
        "border: none" in body
        or "border:none" in body
        or "background: transparent" in body
        or "background:transparent" in body
    ), f"chrome reset rule body too permissive: {body[:200]!r}"


def test_interpretation_card_uses_hairline_token():
    """Interpretation card must use var(--wb-hairline) for its
    border instead of the legacy raw amber rgba."""
    rule = re.search(
        r'\.workbench-suggestion-interpretation\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--wb-hairline)" in body, (
        f"interpretation card border must reference --wb-hairline; "
        f"rule was: {body[:300]!r}"
    )


def test_interpretation_card_uses_p52_radius():
    """North star: cards/drawers round at 12px, not the legacy 6px."""
    rule = re.search(
        r'\.workbench-suggestion-interpretation\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "border-radius: 12px" in body or "border-radius:12px" in body, (
        f"interpretation card radius should be 12px (P52-02 ladder); "
        f"rule was: {body[:300]!r}"
    )


def test_suggestion_status_right_aligned_in_actions_row():
    """The suggestion status text sits AFTER the interpret button in
    the markup but should be pushed to the row's right edge with
    margin-left:auto, so it doesn't crowd the primary CTA."""
    rule = re.search(
        r'\.workbench-suggestion-status\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "margin-left: auto" in body or "margin-left:auto" in body, (
        f"suggestion-status must use margin-left:auto so it sits at "
        f"the row's right edge; rule was: {body[:200]!r}"
    )


def test_textarea_border_uses_hairline_token():
    """Form input border should reference --wb-hairline for visual
    coherence with the rest of the workbench (monitor drawer, dock,
    drawer header divider all share this token)."""
    rule = re.search(
        r'\.workbench-suggestion-input\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--wb-hairline)" in body, (
        f"textarea border must use --wb-hairline; rule body: "
        f"{body[:300]!r}"
    )


def test_textarea_focus_ring_uses_accent_token():
    """Focus ring should derive from --accent (cyan) so a future
    accent rebrand updates the focus state without per-rule edits."""
    rule = re.search(
        r'\.workbench-suggestion-input:focus\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--accent" in body or "rgba(103, 232, 249" in body, (
        f"textarea focus ring should use --accent (or its raw cyan "
        f"rgba); rule body: {body[:300]!r}"
    )
