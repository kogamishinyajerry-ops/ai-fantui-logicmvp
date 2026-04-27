"""P52-07 — new-circuit creation flow.

Replaces the "Coming soon" placeholder in the new-circuit drawer with
a real template picker + name field + submit. Wiring to a backend is
deliberately stubbed for this slice (the user feedback was that the
drawer felt like a dead end; meaningful UI is the unlock, not a new
endpoint). Future work can land the /api/circuits POST.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")
JS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js").read_text(encoding="utf-8")


def _drawer() -> str:
    m = re.search(
        r'<section[^>]*id="workbench-tool-new"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert m is not None, "#workbench-tool-new drawer missing"
    return m.group(0)


def test_drawer_no_longer_says_coming_soon():
    block = _drawer()
    assert "Coming soon" not in block, (
        "P52-07 must replace the placeholder copy with a real "
        "creation flow"
    )


def test_drawer_lists_three_template_options():
    """Three-card template picker: blank / single-input AND / two-
    stage chain. Encoded via data-template-id so the JS click
    handler can read the selection back."""
    block = _drawer()
    template_ids = re.findall(
        r'data-template-id="([^"]+)"',
        block,
    )
    assert "blank" in template_ids, "blank template option missing"
    assert "single-and" in template_ids, "single-AND template option missing"
    assert "two-stage" in template_ids, "two-stage chain template option missing"


def test_drawer_has_derive_from_existing_action():
    """Power-user shortcut: if a circuit is already loaded, let the
    user clone its structure as the starting point."""
    block = _drawer()
    assert 'data-circuit-action="derive-from-current"' in block, (
        "missing 'derive from current' affordance"
    )


def test_drawer_has_circuit_name_field():
    block = _drawer()
    assert 'id="workbench-new-circuit-name"' in block, (
        "circuit name input field missing"
    )
    # And it's wired to a label for a11y.
    assert 'for="workbench-new-circuit-name"' in block, (
        "circuit name field needs an associated <label for=...>"
    )


def test_drawer_has_create_submit_button():
    block = _drawer()
    assert 'id="workbench-new-circuit-create-btn"' in block, (
        "create-submit button id missing"
    )
    # Primary CTA — should carry .is-primary modifier
    btn_match = re.search(
        r'<button[^>]*id="workbench-new-circuit-create-btn"[^>]*>',
        block,
    )
    assert btn_match is not None
    assert "is-primary" in btn_match.group(0), (
        "create button must use the primary CTA modifier"
    )


def test_template_card_uses_p52_radius():
    """Template cards round at 12px to match the drawer ladder."""
    rule = re.search(
        r'\.workbench-new-circuit-template-card\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "expected .workbench-new-circuit-template-card CSS rule"
    )
    body = rule.group(0)
    assert (
        "border-radius: 12px" in body
        or "border-radius:12px" in body
        or "border-radius: 10px" in body
        or "border-radius:10px" in body
    ), f"template card radius should be 10–12px; rule was: {body[:300]!r}"


def test_template_card_uses_hairline_token():
    rule = re.search(
        r'\.workbench-new-circuit-template-card\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    assert "var(--wb-hairline)" in rule.group(0), (
        "template card border must use --wb-hairline"
    )


def test_template_card_active_state_uses_accent_token():
    """Selected template highlights with accent color (cyan), so the
    user can see at a glance which template they're about to create."""
    rule = re.search(
        r'\.workbench-new-circuit-template-card\[data-template-selected="true"\]\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "missing active-state rule for selected template card"
    )
    body = rule.group(0)
    assert (
        "var(--accent" in body
        or "rgba(103, 232, 249" in body
        or "var(--wb-active-border" in body
    ), f"selected template should highlight with accent; rule was: {body[:300]!r}"


def test_js_wires_new_circuit_drawer():
    """workbench.js must register click handlers for the template
    cards + create button. We grep for the boot anchor name."""
    assert "_wbNewCircuitBoot" in JS or "workbench-new-circuit-create-btn" in JS, (
        "no boot/handler reference for the new-circuit drawer in "
        "workbench.js — the buttons would be inert without it"
    )
