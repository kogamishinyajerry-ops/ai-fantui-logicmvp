"""P55-04 — Figma-style hover preview on gate proposal markers.

Figma's pin-comment pattern: a hover over a comment pin reveals the
authors + first lines of the threaded comments without forcing a
click into the side panel. The engineer absorbs "who's queued and
roughly what about" before deciding to dive in.

P55-02's marker today says only "3 OPEN proposals" — to learn
*which* 3, the engineer must click the marker which opens the full
approve drawer. P55-04 adds a hover-preview popover keyed to each
marker:

  - Header: "{gateId} · N OPEN proposals"
  - One row per OPEN proposal:
      avatar-circle (colored by author hash)
      author name · role · relative age
      one-line summary (interpretation.summary_zh or source_text)
  - Click a row → opens the approve drawer AND spotlights that
    specific proposal card (not just any one matching the gate).

Implementation shape (locked by these contract tests):
  - One shared `#workbench-gate-marker-popover` element in
    workbench.html, hidden by default.
  - JS function `installGateMarkerHoverPreviews()` wires
    mouseenter/mouseleave on every marker on every refresh.
  - Helper `renderGateMarkerPopover(gateId)` + helpers for the
    avatar, role, and relative age.
  - 200ms hide delay so users can move pointer marker → popover
    without losing it.
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
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(
    encoding="utf-8"
)


# ─── 1. HTML carries the shared popover element ───


def test_html_declares_shared_popover_element() -> None:
    """A single, page-level element keeps positioning + lifecycle
    simple (vs creating one popover per marker). Hidden by default
    via the hidden attribute; JS unhides + positions on hover."""
    assert 'id="workbench-gate-marker-popover"' in HTML, (
        "workbench.html must declare #workbench-gate-marker-popover"
    )
    # Must default to hidden so it doesn't appear on initial page
    # load before any hover.
    pop_match = re.search(
        r'<div[^>]*id="workbench-gate-marker-popover"[^>]*>',
        HTML,
    )
    assert pop_match is not None
    tag = pop_match.group(0)
    assert " hidden" in tag or 'aria-hidden="true"' in tag, (
        "popover must default hidden"
    )


def test_popover_has_aria_role_dialog_or_tooltip() -> None:
    """A11y: the popover is a transient context surface — `tooltip`
    fits since it's hover-triggered + non-interactive-by-default
    (rows are clickable but the popover doesn't trap focus)."""
    pop_match = re.search(
        r'<div[^>]*id="workbench-gate-marker-popover"[^>]*>',
        HTML,
    )
    assert pop_match is not None
    tag = pop_match.group(0)
    assert 'role="tooltip"' in tag or 'role="dialog"' in tag, (
        "popover must declare an a11y role"
    )


# ─── 2. JS installs the hover wiring ───


def test_js_defines_install_gate_marker_hover_previews() -> None:
    assert "function installGateMarkerHoverPreviews(" in JS


def test_js_defines_render_gate_marker_popover() -> None:
    assert "function renderGateMarkerPopover(" in JS


def test_install_called_after_every_marker_render() -> None:
    """Markers are torn down + rebuilt on every applyGateProposalMarkers
    refresh, so any hover wiring on prior markers is dead. The
    install function must run AS PART of (or right after) the
    marker render so each new marker gets a fresh listener."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "installGateMarkerHoverPreviews(" in body, (
        "applyGateProposalMarkers must call installGateMarkerHoverPreviews "
        "(or do its work inline) so refreshed markers stay hover-wired"
    )


def test_install_wires_mouseenter_and_mouseleave() -> None:
    """Hover preview needs both edges: enter to show, leave to
    schedule hide. A click-only flow would lose the Figma 'preview
    without commit' feel."""
    fn = re.search(
        r"function installGateMarkerHoverPreviews\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert '"mouseenter"' in body
    assert '"mouseleave"' in body


def test_hide_delay_is_at_least_150ms() -> None:
    """Mouseleave must defer the hide so the user can move the
    pointer from marker to popover without it vanishing. 150–250ms
    is the Figma/Linear range."""
    fn = re.search(
        r"function installGateMarkerHoverPreviews\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Locate setTimeout(... , N) closing patterns. The arg-1 may
    # contain commas (multi-statement arrow body), so match the
    # closing ", N)" form across all setTimeout occurrences.
    delays = [int(m) for m in re.findall(r"\}\s*,\s*(\d+)\s*\)", body)]
    assert delays, "no setTimeout(... , N) hide-delay literal found"
    in_range = [d for d in delays if 150 <= d <= 400]
    assert in_range, (
        f"none of the setTimeout delays {delays} fall in the "
        f"150–400ms Figma/Linear range"
    )


def test_popover_hover_keeps_it_visible() -> None:
    """If the user moves cursor INTO the popover after pointer-out
    of the marker, the hide-timer must cancel — otherwise the
    popover dies under their cursor."""
    fn = re.search(
        r"function installGateMarkerHoverPreviews\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Either the popover gets its own mouseenter that clearTimeouts,
    # or there's a unified entered-flag that survives marker leave.
    assert "clearTimeout" in body, (
        "hide timer must be cancellable when pointer enters popover"
    )


# ─── 3. Popover renders proposal rows ───


def test_render_popover_emits_one_row_per_open_proposal() -> None:
    """The popover lists every OPEN proposal for the hovered gate,
    not just a count. A class hook lets DOM tests target rows."""
    fn = re.search(
        r"function renderGateMarkerPopover\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "workbench-gate-marker-popover-row" in body, (
        "renderGateMarkerPopover must emit rows with the hook class"
    )
    # Must filter to OPEN status only.
    assert 'p.status === "OPEN"' in body or 'status === "OPEN"' in body, (
        "popover rows must include OPEN proposals only"
    )
    # Must filter to the affected gate (the hovered gate).
    assert "affected_gates" in body, (
        "rows filtered by interpretation.affected_gates membership"
    )


def test_popover_row_carries_proposal_id_for_click_routing() -> None:
    """A clicked row must spotlight THAT specific proposal card,
    not the first OPEN ticket on the gate."""
    fn = re.search(
        r"function renderGateMarkerPopover\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "data-proposal-id" in body, (
        "popover rows must carry data-proposal-id for click routing"
    )


def test_popover_click_opens_drawer_and_spotlights_specific_proposal() -> None:
    """Click on a row → drawer opens + spotlightInboxByProposalId
    targets THAT proposal (not the gate-wide first OPEN). Reuses
    the P55-02 round-1 helper."""
    fn = re.search(
        r"function renderGateMarkerPopover\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Either calls a specific helper or wires an addEventListener
    # that calls spotlightInboxByProposalId.
    assert "spotlightInboxByProposalId" in body, (
        "row click must use spotlightInboxByProposalId so the "
        "specific proposal is highlighted, not the gate's first"
    )


def test_popover_renders_author_age_and_summary() -> None:
    """Each row surfaces the three signals a reviewer scans before
    deciding to dive in."""
    fn = re.search(
        r"function renderGateMarkerPopover\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Author name on the proposal object.
    assert "author_name" in body, "row must surface author_name"
    # Some form of summary — interpretation.summary_zh / _en or source_text.
    assert "summary_zh" in body or "summary_en" in body or "source_text" in body, (
        "row must surface a summary line"
    )
    # Relative age helper.
    assert "formatRelativeAge(" in body or "relativeAge" in body or "ago" in body.lower(), (
        "row must surface relative age via a formatter"
    )


def test_relative_age_helper_exists() -> None:
    """Centralized helper so future surfaces share the same string
    format ('2m ago' / '3h ago' / '5d ago')."""
    assert "function formatRelativeAge(" in JS


def test_popover_header_carries_gate_id_and_count() -> None:
    """Header context: which gate, how many OPEN. Lets users
    confirm they're hovering the right marker."""
    fn = re.search(
        r"function renderGateMarkerPopover\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "workbench-gate-marker-popover-header" in body


# ─── 4. Positioning ───


def test_popover_position_clamps_to_viewport_bottom() -> None:
    """Codex P55-04 round-2 P2: low-y markers (L4 near the bottom
    of a 640px SVG) on laptop-height viewports could push the
    popover off the bottom. The position math must measure the
    rendered popover height and flip above the marker (or pin to
    bottom-margin) when overflow is detected."""
    fn = re.search(
        r"function installGateMarkerHoverPreviews\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "window.innerHeight" in body, (
        "vertical clamp must consult window.innerHeight"
    )
    # Either offsetHeight (preferred) or getBoundingClientRect on the
    # popover is acceptable for measuring rendered height.
    assert (
        "popover.offsetHeight" in body
        or "popover.getBoundingClientRect" in body
    ), (
        "must measure the popover's rendered height before positioning"
    )


def test_popover_position_anchored_to_marker_via_bounding_rect() -> None:
    """SVG element coordinates require getBoundingClientRect to map
    to viewport pixels. Hard-coded x/y would drift on scroll/zoom."""
    fn = re.search(
        r"function installGateMarkerHoverPreviews\([^)]*\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "getBoundingClientRect" in body, (
        "popover position must derive from marker.getBoundingClientRect"
    )


# ─── 4b. Lifecycle: popover dismissed on click + tear-down ───


def test_hide_helper_extracted() -> None:
    """A shared hide helper avoids drift between the three dismissal
    sites (mouseleave grace, marker click, marker tear-down)."""
    assert "function hideGateMarkerPopover(" in JS


def test_marker_click_dismisses_popover() -> None:
    """Codex P55-04 round-1 P2: clicking the marker opens the
    drawer; without dismissing the popover first, the fixed-position
    overlay floats above the drawer until the user happens to leave
    its hover region."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # Locate the click handler block.
    click_match = re.search(
        r'addEventListener\("click",\s*\(e\)\s*=>\s*\{(.*?)\}\)',
        body,
        re.DOTALL,
    )
    assert click_match is not None
    click_body = click_match.group(1)
    assert "hideGateMarkerPopover" in click_body, (
        "marker click must dismiss the popover before opening the drawer"
    )


def test_marker_teardown_dismisses_popover() -> None:
    """Codex P55-04 round-1 P2: applyGateProposalMarkers tears down
    prior markers on every refresh / system switch. The popover's
    SVG anchor disappears — leaving the popover visible would float
    a stale overlay over the canvas."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    # The teardown loop ends with a closing `}` — hideGateMarkerPopover
    # call must appear at the top of the function body (before new
    # markers are rendered) so it follows the tear-down pass.
    teardown_pos = body.find('.workbench-gate-proposal-marker"')
    hide_pos = body.find("hideGateMarkerPopover(")
    assert teardown_pos != -1 and hide_pos != -1, (
        "applyGateProposalMarkers must call hideGateMarkerPopover()"
    )
    # And the hide call must precede the per-gate render loop.
    render_pos = body.find("computeOpenProposalCountsByGate(")
    assert hide_pos < render_pos, (
        "hide must happen during tear-down, before the render loop"
    )


# ─── 5. CSS — surface tokens, not bare hex ───


@pytest.mark.parametrize(
    "selector",
    [
        "#workbench-gate-marker-popover",
        ".workbench-gate-marker-popover-header",
        ".workbench-gate-marker-popover-row",
    ],
)
def test_css_declares_popover_styles(selector: str) -> None:
    assert selector in CSS, f"missing CSS rule: {selector}"


def test_popover_uses_surface_and_hairline_tokens() -> None:
    """Popover surface is a card on the canvas — derive bg from
    --surface-1 / --surface-2 and border from --hairline. NO bare
    hex (would break on theme swap per the P55-01 discipline)."""
    rule = re.search(
        r"#workbench-gate-marker-popover\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--surface" in body or "var(--bg-card" in body, (
        "popover bg must derive from a surface token"
    )
    # No raw hex backgrounds.
    assert not re.search(r"background\s*:\s*#[0-9a-fA-F]+", body), (
        "popover background must not be raw hex"
    )


def test_popover_has_motion_token_transition() -> None:
    """Fade/scale entrance uses the workbench motion tokens — no
    bare ms literal in the transition. Matches the P52-02 drawer."""
    rule = re.search(
        r"#workbench-gate-marker-popover\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--wb-ease-out)" in body or "var(--wb-duration" in body, (
        "popover transition must use --wb-* motion tokens"
    )


def test_popover_row_has_hover_affordance() -> None:
    """Each row is clickable — hover state must indicate that. A
    bg lift via --accent-tint-12 fits the palette without burning
    accent intensity (rows aren't focal)."""
    rule = re.search(
        r"\.workbench-gate-marker-popover-row:hover\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None, "popover row missing :hover affordance"
    body = rule.group(0)
    assert "background" in body or "color-mix" in body
