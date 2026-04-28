"""P55-03 — fan-in count badges on multi-input gates.

Stately Studio numbers transition guards next to their source state
so the engineer sees evaluation order at-a-glance. Combinational AND
gates don't have evaluation order, but they DO have fan-in arity —
"L3 is a 6-input AND" is the structural fact a reviewer wants to
absorb without counting wires.

P55-03 mirrors the P55-02 marker pattern (always-on, accent-toned,
top-corner) on the OPPOSITE corner so the two pieces of element-
level metadata don't collide:

  - top-RIGHT: P55-02 OPEN-proposal count (state-of-world, filled)
  - top-LEFT:  P55-03 fan-in count          (structural, outlined)

The badge is purely informational — outline-only, no click handler,
hidden when count ≤ 1 (single-input gates degenerate to passthroughs
and don't merit the noise).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
JS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js").read_text(
    encoding="utf-8"
)
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(
    encoding="utf-8"
)
CIRCUIT_HTML = (
    REPO_ROOT / "src" / "well_harness" / "static" / "fantui_circuit.html"
).read_text(encoding="utf-8")


# ─── 1. Source SVG carries fan-in metadata ───


@pytest.mark.parametrize(
    ("gate_id", "expected_count"),
    [
        ("L1", 4),
        ("L2", 5),
        ("L3", 6),
        ("L4", 4),
    ],
)
def test_thrust_reverser_gates_carry_data_input_count(
    gate_id: str, expected_count: int,
) -> None:
    """Each AND-gate <use data-gate-id="..."> in fantui_circuit.html
    must carry data-input-count so the JS layer doesn't have to
    geometrically detect input wires (fragile against future SVG
    edits). The values match the comments already on each L# ROW
    block."""
    pattern = re.compile(
        rf'<use[^/]*\bdata-gate-id="{re.escape(gate_id)}"[^/]*\bdata-input-count="(\d+)"[^/]*/>',
    )
    match = pattern.search(CIRCUIT_HTML)
    assert match is not None, (
        f"missing data-input-count on <use data-gate-id=\"{gate_id}\"/>"
    )
    assert int(match.group(1)) == expected_count, (
        f"{gate_id} should declare {expected_count} inputs, "
        f"got data-input-count=\"{match.group(1)}\""
    )


# ─── 2. JS renders the badge ───


def test_js_defines_apply_gate_fan_in_badges_function() -> None:
    """A dedicated function so tests + future debug surfaces can
    target it cleanly."""
    assert "function applyGateFanInBadges(" in JS


def test_apply_gate_fan_in_badges_emits_g_rect_text_title() -> None:
    """Same DOM shape as the P55-02 marker (group + outlined rect +
    monospace digit + tooltip) so users get a coherent visual
    language across both corners of the gate."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'createElementNS(NS, "g")' in body
    assert 'createElementNS(NS, "rect")' in body
    assert 'createElementNS(NS, "text")' in body
    assert 'createElementNS(NS, "title")' in body


def test_fan_in_badge_skips_low_arity_gates() -> None:
    """Single-input "gates" (passthroughs) shouldn't get a badge —
    a "1" decoration is just noise. The function must guard on
    count >= 2."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Either explicit `count < 2` skip or `count >= 2` guard.
    assert re.search(r"<\s*2\b", body) or re.search(r">=\s*2\b", body), (
        "applyGateFanInBadges must skip count < 2"
    )


def test_fan_in_badge_reads_data_input_count_from_use_element() -> None:
    """The badge derives its number from the gate <use>'s
    data-input-count attribute (single source of truth — the SVG
    file). No hard-coded gate→count map in JS."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "data-input-count" in body, (
        "applyGateFanInBadges must read data-input-count, not "
        "carry its own gate→count map"
    )


def test_fan_in_badge_has_data_attributes_for_test_hooks() -> None:
    """Expose target gate id + count so DOM-level tests can reach
    cleanly without parsing badge text content."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'setAttribute("data-fan-in-for"' in body
    assert 'setAttribute("data-fan-in-count"' in body


# ─── 3. Always-on; runs after circuit hydration, not gated by review-mode ───


def test_fan_in_badges_invoked_after_circuit_hydration() -> None:
    """The badge layer is a structural fact about the circuit —
    runs once when the SVG fragment hydrates, NOT when proposals
    refresh. Contract: applyGateFanInBadges() must be called from
    the circuit-hydration code path (alongside or near
    applyReviewAnchors)."""
    # The hydration block calls applyReviewAnchors after fragment
    # injection; applyGateFanInBadges must also appear in the same
    # hydration block.
    hydrate_block = re.search(
        r"async function loadCircuitFragment\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    if hydrate_block is None:
        # Fallback: function name may differ slightly across phases.
        # Just ensure the call appears alongside the hydration
        # applyReviewAnchors.
        anchor_call = re.search(
            r"applyReviewAnchors\(_latestProposals\)\s*;",
            JS,
        )
        assert anchor_call is not None
        nearby = JS[max(0, anchor_call.start() - 600): anchor_call.end() + 600]
        assert "applyGateFanInBadges(" in nearby
        return
    body = hydrate_block.group(1)
    assert "applyGateFanInBadges(" in body, (
        "applyGateFanInBadges must be called from circuit hydration"
    )


def test_fan_in_badge_function_does_not_consult_review_mode() -> None:
    """Structural facts are always-on. A review-mode gate would be
    a regression to the pre-Stately UX."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'getAttribute("data-review-mode")' not in body, (
        "applyGateFanInBadges must not gate on review-mode"
    )


# ─── 4. Position: top-LEFT (opposite corner from P55-02) ───


def test_fan_in_badge_anchors_top_left_of_gate() -> None:
    """P55-02 marker is at top-RIGHT (gate.x + width - margin).
    P55-03 fan-in badge belongs at top-LEFT (gate.x + margin) so
    the two pieces of metadata don't visually collide. The function
    must compute its x using gate.x without adding the gate width."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # The P55-02 marker uses `x + w - <something>` for top-right.
    # The fan-in badge anchor must NOT add the full gate width to
    # x, otherwise it lands on the right edge.
    assert re.search(r"\bw\s*-\s*", body) is None, (
        "fan-in badge must anchor at left edge — found x = ... + w "
        "expression which would place it on the right"
    )


# ─── 5. CSS — outlined only (structural, not state-of-world) ───


@pytest.mark.parametrize(
    "selector",
    [
        ".workbench-gate-fan-in-badge",
        ".workbench-gate-fan-in-badge-bg",
        ".workbench-gate-fan-in-badge-label",
    ],
)
def test_css_declares_fan_in_badge_styles(selector: str) -> None:
    assert selector in CSS, f"missing CSS rule: {selector}"


def test_fan_in_badge_bg_is_outline_only_not_filled() -> None:
    """The proposal marker (P55-02) is filled with --accent-tint-28
    because OPEN tickets are state-of-world demanding attention.
    The fan-in badge is structural metadata — outline-only, fill
    transparent or none, so it sits quietly without competing."""
    rule = re.search(
        r"\.workbench-gate-fan-in-badge-bg\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    # Either fill: none, fill: transparent, or no fill at all.
    fill_match = re.search(r"fill\s*:\s*([^;}]+)[;}]", body)
    if fill_match:
        fill_val = fill_match.group(1).strip()
        assert fill_val in ("none", "transparent"), (
            f"fan-in badge bg must be outline-only; got fill: {fill_val!r}"
        )
    # Stroke must derive from the contrast/hairline tokens (NOT the
    # accent — the accent is reserved for P55-02 + the active-gate
    # highlight per Linear's single-accent discipline).
    assert "stroke" in body
    assert "var(--accent)" not in body, (
        "fan-in badge stroke must NOT use --accent (reserved for "
        "state-of-world surfaces); use --hairline-strong or similar"
    )


def test_fan_in_badge_label_uses_monospace() -> None:
    """Same monospace face as P55-02 — keeps numeric metadata
    readable + visually consistent across both badge corners."""
    rule = re.search(
        r"\.workbench-gate-fan-in-badge-label\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert any(
        font in body for font in ("SF Mono", "Menlo", "Consolas")
    ), "fan-in digit must render in a monospace face"


def test_fan_in_badge_bg_uses_pointer_events_stroke() -> None:
    """Codex P55-03 round-1 P3: the badge group carries an SVG
    <title> child for the "N-input gate" tooltip. With
    pointer-events: none on the bg rect, the tooltip would never
    fire (no hover events captured). The fix is `pointer-events:
    stroke` on the rect — the outline catches hover (tooltip works)
    while the rect's transparent interior stays click-through so
    the 6px gate-overlap zone doesn't eat the gate's review-mode
    click."""
    rule = re.search(
        r"\.workbench-gate-fan-in-badge-bg\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "pointer-events: stroke" in body, (
        "fan-in badge bg must use pointer-events: stroke so the "
        "<title> tooltip fires on hover without eating gate clicks"
    )


def test_fan_in_badge_group_does_not_disable_pointer_events() -> None:
    """If a group-level `.workbench-gate-fan-in-badge { pointer-events:
    none }` rule reappears it would swallow hover on every child,
    re-introducing the round-1 P3 bug."""
    # Look for a rule that targets the group selector exactly (NOT
    # the -bg / -label children).
    rule = re.search(
        r"\.workbench-gate-fan-in-badge(?![-\w])\s*\{([^}]+)\}",
        CSS,
        re.DOTALL,
    )
    if rule is None:
        return  # No group-level rule = OK
    body = rule.group(1)
    assert "pointer-events: none" not in body, (
        "group-level pointer-events: none re-introduces the round-1 "
        "P3 tooltip-suppression bug"
    )


def test_fan_in_badge_label_uses_text_muted_or_contrast() -> None:
    """Outline-only badge needs a legible label color that's clearly
    *not* the accent (which would say "pay attention here"). Use
    --text-muted or --contrast."""
    rule = re.search(
        r"\.workbench-gate-fan-in-badge-label\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--accent)" not in body, (
        "fan-in label must not use --accent (reserved)"
    )
    assert (
        "var(--text-muted)" in body
        or "var(--contrast)" in body
        or "var(--text-main)" in body
    ), "fan-in label must use a contrast-derived token"


# ─── 6. Idempotency: re-hydration replaces, doesn't duplicate ───


def test_apply_gate_fan_in_badges_tears_down_prior_badges() -> None:
    """Re-hydration of the circuit fragment (system switch) calls
    applyGateFanInBadges again — the function must clear prior
    badge nodes first or we'd accumulate duplicates."""
    fn = re.search(
        r"function applyGateFanInBadges\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert (
        "querySelectorAll(\".workbench-gate-fan-in-badge\")" in body
        and ".remove()" in body
    ), (
        "applyGateFanInBadges must querySelectorAll prior badges and "
        "remove them so re-hydration is idempotent"
    )
