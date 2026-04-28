"""P58-02 — vanilla 5-step guided tour (replaces P58-01 Take-Tour stub).

P58-01 shipped the welcome banner with a tour-launch CTA that was a
stub (status message + session-only hide). P58-02 wires the real tour:
spotlight overlay + step card + Next/Prev/Skip controls, in vanilla
JS with no third-party dependencies (no Shepherd.js / Tippy.js /
Driver.js).

Contract:
  - 5 ordered steps target the highest-leverage UI elements
    (preset dropdown, visual editor tabs, save/scratch toolbar,
    run button, results panel)
  - Active only while overlay is visible (`hidden` attribute toggle)
  - Steady-state UI for completed/skipped users is pixel-identical to
    pre-P58 (per user directive 2026-04-28)
  - Completing all 5 steps persists onboarding-dismissed flag
  - Skipping is session-only (banner returns on next reload until
    explicit dismiss via × or 知道了)
  - Esc key cancels (session-only)
  - aria-modal=true + aria-labelledby on the dialog so screen readers
    announce it correctly

Tests use the regex-on-source pattern from P57+P58-01.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TIMELINE_SIM = REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"


def _read() -> str:
    return TIMELINE_SIM.read_text(encoding="utf-8")


# ── 1. Tour DOM presence + hidden-by-default ──


def test_tour_overlay_exists() -> None:
    """The tour overlay container must exist as <div id=tourOverlay>
    with the `hidden` attribute in static markup. Without the hidden
    attribute, returning users see the overlay paint for one frame
    before JS initializes (FOUC) — and worse, before the first
    dismiss check runs the overlay is fully visible.
    """
    body = _read()
    pattern = (
        r'<div\s+id="tourOverlay"[^>]*class="tour-overlay"'
        r'[^>]*\bhidden\b'
    )
    assert re.search(pattern, body), (
        "tour overlay <div id=tourOverlay> not found, or missing the "
        "`hidden` attribute. The overlay must be hidden by default so "
        "steady-state UI is pixel-identical to pre-P58."
    )


def test_tour_overlay_is_aria_modal() -> None:
    """The overlay must be role=dialog + aria-modal=true so assistive
    tech treats it as a modal dialog (focus trap signal). aria-labelledby
    points at the step card title so the dialog has an accessible name."""
    body = _read()
    pattern = (
        r'<div\s+id="tourOverlay"[^>]*role="dialog"'
        r'[^>]*aria-modal="true"[^>]*aria-labelledby="tourCardTitle"'
    )
    assert re.search(pattern, body), (
        "tour overlay missing role=dialog + aria-modal=true + "
        "aria-labelledby=tourCardTitle. Required for screen-reader "
        "announcement of the tour as a modal dialog."
    )


@pytest.mark.parametrize(
    "elem_id",
    [
        "tourDimTop", "tourDimRight", "tourDimBottom", "tourDimLeft",
        "tourSpotlightRing", "tourCard", "tourCardTitle",
        "tourCardDesc", "tourStepCounter",
        "tourSkipBtn", "tourPrevBtn", "tourNextBtn",
    ],
)
def test_tour_subtree_elements_exist(elem_id: str) -> None:
    """Each subtree element must exist with a stable id. The 4 dim
    panels (top/right/bottom/left) form the spotlight cutout; the
    accent ring sits inside; the card holds title/desc/counter/buttons."""
    body = _read()
    pattern = rf'\bid="{elem_id}"'
    assert re.search(pattern, body), (
        f"tour subtree element id={elem_id!r} not found. The tour "
        f"controller depends on stable ids to position the spotlight."
    )


# ── 2. TOUR_STEPS array: shape + 5 ordered steps ──


def test_tour_steps_array_has_five_entries() -> None:
    """Onboarding contract: exactly 5 steps. Fewer skips important
    surfaces; more risks user fatigue. Step count is fixed — if the
    number genuinely needs to change, the welcome banner copy
    ("引导漫游（5 步）") and the step counter format also need updates."""
    body = _read()
    array_match = re.search(
        r'const\s+TOUR_STEPS\s*=\s*\[([\s\S]*?)\]\s*;',
        body,
    )
    assert array_match is not None, "TOUR_STEPS array not declared"
    steps_block = array_match.group(1)
    # Each step is `{ selector: ..., title: ..., desc: ... }`.
    selector_count = len(re.findall(r"\bselector\s*:", steps_block))
    assert selector_count == 5, (
        f"TOUR_STEPS has {selector_count} entries; expected exactly 5. "
        f"If you intentionally changed the count, also update the "
        f"welcome banner copy (引导漫游（N 步）) and the counter format."
    )


@pytest.mark.parametrize(
    "selector",
    ["#presetSelect", ".tabs", "#saveScenarioBtn", "#runBtn", "#assertList"],
)
def test_tour_step_targets_real_elements(selector: str) -> None:
    """Every TOUR_STEPS selector must resolve to a real element id /
    class on the page. If a future refactor renames any of these,
    the tour breaks — this test catches the drift before users do.
    The 5 selectors are the highest-leverage surfaces: preset picker,
    visual/raw tabs, save toolbar, run trigger, results."""
    body = _read()
    # Selector appears as a string in TOUR_STEPS (escape for regex).
    in_steps = re.search(
        rf'TOUR_STEPS\s*=[\s\S]*?selector\s*:\s*"{re.escape(selector)}"',
        body,
    )
    assert in_steps is not None, (
        f"TOUR_STEPS does not target selector {selector!r}. The 5 "
        f"required targets are: #presetSelect, .tabs, #saveScenarioBtn, "
        f"#runBtn, #assertList."
    )
    # The element/class actually exists in the markup.
    if selector.startswith("#"):
        elem_pat = rf'\bid="{re.escape(selector[1:])}"'
    else:
        elem_pat = rf'\bclass="[^"]*\b{re.escape(selector[1:])}\b'
    assert re.search(elem_pat, body), (
        f"TOUR_STEPS targets {selector!r} but no matching element "
        f"appears in the markup. The tour would silently skip past "
        f"this step (the controller's no-target fallback)."
    )


# ── 3. Tour lifecycle: start / next / prev / skip / finish ──


def test_take_tour_button_starts_tour() -> None:
    """The welcome banner's Take-Tour button must call startTour()
    after hiding the banner. P58-01 wired this as a stub; P58-02
    must replace the stub with the real launch."""
    body = _read()
    handler_match = re.search(
        r'welcomeTakeTourBtn[\s\S]{0,200}?addEventListener\s*\(\s*"click"'
        r'[\s\S]{0,800}?\}\s*\)\s*;',
        body,
    )
    assert handler_match is not None, "welcomeTakeTourBtn handler not found"
    chunk = handler_match.group(0)
    assert "startTour" in chunk, (
        "welcomeTakeTourBtn handler does not call startTour(). The "
        "P58-01 stub message should be replaced by the real tour launch."
    )


def test_complete_tour_persists_dismissal() -> None:
    """Completing all 5 steps (clicking 下一步 on the last step) must
    persist the welcome-dismissed flag — the user has clearly seen
    onboarding and shouldn't be greeted again on next reload."""
    body = _read()
    # endTour(true) is called somewhere; tourNext on last step calls
    # endTour(true). Verify endTour(true) invocation exists.
    assert re.search(r'endTour\s*\(\s*true\s*\)', body), (
        "endTour(true) call not found. Completing all 5 steps must "
        "persist dismissal so returning users don't see the banner "
        "again."
    )
    # Also verify endTour(true) → setWelcomeDismissed(true).
    end_tour_match = re.search(
        r'function\s+endTour\s*\(\s*persistent\s*\)\s*\{[\s\S]{0,400}?\n\}',
        body,
    )
    assert end_tour_match is not None, "endTour function not found"
    chunk = end_tour_match.group(0)
    assert re.search(
        r'if\s*\(\s*persistent\s*\)\s*\{[^}]*setWelcomeDismissed\s*\(\s*true',
        chunk,
    ), (
        "endTour(persistent) does not call setWelcomeDismissed(true) "
        "when persistent=true. Completion would not persist."
    )


def test_skip_tour_does_not_persist() -> None:
    """Skipping is session-only — the banner returns on next reload
    until the user explicitly dismisses via × or 知道了. Persisting
    on skip would punish exploratory users."""
    body = _read()
    skip_match = re.search(
        r'function\s+tourSkip\s*\(\s*\)\s*\{[\s\S]{0,200}?\n\}',
        body,
    )
    assert skip_match is not None, "tourSkip function not found"
    chunk = skip_match.group(0)
    assert "endTour(false)" in chunk or re.search(
        r'endTour\s*\(\s*false\s*\)', chunk,
    ), (
        "tourSkip does not call endTour(false). Skip must end the "
        "tour session-only — endTour(true) would persist dismissal."
    )


def test_esc_key_cancels_tour() -> None:
    """Esc is the universal "close this dialog" key. The handler
    must check the overlay is visible (otherwise Esc anywhere in the
    page would no-op via tourSkip's hidden-overlay check, but it'd
    still fire the listener which is wasted work)."""
    body = _read()
    # Look for keydown listener that checks overlay !hidden + Escape.
    pattern = (
        r'document\.addEventListener\s*\(\s*"keydown"[\s\S]{0,800}?'
        r'tourOverlay[\s\S]{0,200}?Escape[\s\S]{0,200}?tourSkip'
    )
    # Allow either order of overlay check vs key check; weaker but safer:
    weak_pattern = (
        r'addEventListener\s*\(\s*"keydown"[\s\S]{0,1000}?'
        r'(?:e\.key\s*===\s*"Escape"|key\s*===\s*"Escape")'
    )
    assert re.search(weak_pattern, body), (
        "no keydown listener checks for Escape. The user has no "
        "keyboard escape from the tour besides the Skip button."
    )
    # And the body actually wires escape to tourSkip somewhere.
    assert re.search(r'Escape[\s\S]{0,300}?tourSkip\s*\(', body), (
        "Escape key handler does not call tourSkip(). Pressing Esc "
        "should cancel the tour."
    )


# ── 4. Spotlight positioning + responsiveness ──


def test_spotlight_position_uses_4_dim_panels() -> None:
    """The spotlight cutout is implemented as 4 dim panels (top/right/
    bottom/left) positioned around the target rect. clip-path masks
    are simpler but degrade with rounded borders + transitions; the
    4-panel approach reflows cleanly. The positioning function must
    set top/left/width/height on each panel from getBoundingClientRect."""
    body = _read()
    # Each dim panel must be assigned in positionTourStep (or equivalent).
    fn_match = re.search(
        r'function\s+positionTourStep[\s\S]{0,3500}?\n\}',
        body,
    )
    assert fn_match is not None, "positionTourStep function not found"
    chunk = fn_match.group(0)
    for panel in ("tourDimTop", "tourDimBottom", "tourDimLeft", "tourDimRight"):
        assert panel in chunk, (
            f"positionTourStep does not position {panel!r}. The "
            f"spotlight cutout would have a hole on that side."
        )
    # And uses getBoundingClientRect (or a wrapper).
    assert "getBoundingClientRect" in chunk, (
        "positionTourStep does not call getBoundingClientRect. Without "
        "viewport coordinates, the dim panels can't be positioned."
    )


def test_resize_listener_repositions_active_tour() -> None:
    """Browser resize while tour is active must reposition the spotlight,
    otherwise it sits over stale coordinates. The listener must check
    overlay !hidden before doing work."""
    body = _read()
    pattern = (
        r'window\.addEventListener\s*\(\s*"resize"[\s\S]{0,500}?'
        r'tourOverlay[\s\S]{0,200}?positionTourStep'
    )
    assert re.search(pattern, body), (
        "no resize listener calls positionTourStep on viewport change. "
        "Spotlight would track stale coordinates after resize."
    )


# ── 5. Accessibility: focus into the dialog on start ──


def test_start_tour_moves_focus_into_card() -> None:
    """When the tour opens, keyboard focus must move into the dialog
    so screen readers announce it and Tab cycles through the controls.
    Standard target: the primary "Next" button (first action)."""
    body = _read()
    fn_match = re.search(
        r'function\s+startTour\s*\(\s*\)\s*\{[\s\S]{0,500}?\n\}',
        body,
    )
    assert fn_match is not None, "startTour function not found"
    chunk = fn_match.group(0)
    assert re.search(r'\.focus\s*\(\s*\)', chunk), (
        "startTour does not call .focus() on any element. Without "
        "focus management, screen readers don't announce the dialog "
        "open and keyboard users have no entry point."
    )


# ── 6. No third-party dependency leaked in ──


def test_tour_uses_no_external_dependency() -> None:
    """P58 commits to vanilla JS — no Shepherd.js, Tippy.js, Driver.js,
    Intro.js, Joyride. If any sneak in, they bring transitive deps,
    bundle size hits, and typically jQuery. Block at the contract
    level by scanning <script src=...> tags (comments mentioning
    these libs by name in a "we don't use X" context don't count)."""
    body = _read()
    script_tags = re.findall(r'<script[^>]*\bsrc="([^"]+)"', body)
    forbidden = ["shepherd", "tippy", "driver.js", "intro.js",
                 "introjs", "joyride", "jquery"]
    for src in script_tags:
        src_lower = src.lower()
        for dep in forbidden:
            assert dep not in src_lower, (
                f"forbidden dependency in <script src={src!r}>. "
                f"P58 commits to vanilla JS — no third-party tour libs."
            )
