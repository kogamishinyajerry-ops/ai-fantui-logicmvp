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
import shutil
import subprocess
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
    # Also verify endTour(true) → setWelcomeDismissed(true). Larger
    # window (1200 chars) accommodates the focus-restore logic added
    # in Codex P58-02 R1 MEDIUM fix.
    end_tour_match = re.search(
        r'function\s+endTour\s*\(\s*persistent\s*\)\s*\{[\s\S]{0,1200}?\n\}',
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
    # P58-02 R2: signature evolved from startTour() to startTour(launcher)
    # so the captured launcher param is explicit. Match either form.
    fn_match = re.search(
        r'function\s+startTour\s*\([^)]*\)\s*\{[\s\S]{0,1000}?\n\}',
        body,
    )
    assert fn_match is not None, "startTour function not found"
    chunk = fn_match.group(0)
    assert re.search(r'\.focus\s*\(\s*\)', chunk), (
        "startTour does not call .focus() on any element. Without "
        "focus management, screen readers don't announce the dialog "
        "open and keyboard users have no entry point."
    )


# ── 6a. Focus management (Codex R1 MEDIUM): trap + restore ──


def test_keydown_handler_traps_tab() -> None:
    """Codex P58-02 R1 MEDIUM: aria-modal=true + role=dialog without a
    Tab/Shift+Tab focus trap is a lie — keyboard focus leaks into the
    background DOM. The keydown handler must intercept Tab and wrap
    focus within the tour buttons.

    Required behavior verified:
      - Tab on last → wrap to first
      - Shift+Tab on first → wrap to last
    """
    body = _read()
    # Find ALL keydown handlers on document (P58-01 added one for
    # Shift+? to reopen the welcome banner; P58-02 adds another for
    # Esc/Tab inside the tour). Pick the one that mentions tourOverlay
    # — that's the tour's handler.
    handler_chunks = [
        m.group(0)
        for m in re.finditer(
            r'document\.addEventListener\s*\(\s*"keydown"[\s\S]*?\}\s*\)\s*;',
            body,
        )
    ]
    tour_handlers = [c for c in handler_chunks if "tourOverlay" in c]
    assert tour_handlers, (
        "no keydown listener references tourOverlay — the tour's "
        "Esc/Tab handler is missing or mis-attributed."
    )
    chunk = tour_handlers[0]
    # The handler must check for Tab key.
    assert re.search(r'e\.key\s*===\s*"Tab"', chunk), (
        "keydown handler does not check for Tab key. Without it, "
        "focus leaks into background DOM while the modal is open "
        "(Codex R1 MEDIUM)."
    )
    # And distinguish shift vs no-shift.
    assert re.search(r'e\.shiftKey', chunk), (
        "keydown handler does not branch on shiftKey. Shift+Tab needs "
        "different wrapping logic (last-button-was-active → first)."
    )
    # And call .focus() on a button to wrap.
    assert re.search(r'\.focus\s*\(\s*\)', chunk), (
        "keydown handler does not call .focus() to wrap focus. The "
        "Tab key default would leak focus out of the dialog."
    )


def test_end_tour_restores_focus_to_launcher() -> None:
    """Codex R1 MEDIUM: aria-modal dialogs must restore focus to the
    element that opened them on close. Otherwise focus lands on
    <body> and screen-reader users have no anchor.

    startTour() must accept an explicit launcher OR fall back to
    document.activeElement, and endTour() must call .focus() on it.
    """
    body = _read()
    # startTour must accept an explicit launcher param (Codex R2 MED:
    # the welcome banner is hidden before startTour is called, so an
    # activeElement-only capture is unreliable).
    start_fn = re.search(
        r'function\s+startTour\s*\(\s*launcher\s*\)\s*\{[\s\S]{0,1000}?\n\}',
        body,
    )
    assert start_fn is not None, (
        "startTour does not accept an explicit launcher parameter. "
        "Per Codex R2 MEDIUM, callers must pass the launcher element "
        "BEFORE hiding it (e.g. e.currentTarget) so the saved ref is "
        "the actual button, not whatever activeElement was at hide-time."
    )
    start_chunk = start_fn.group(0)
    assert "tourLauncherEl" in start_chunk, (
        "startTour does not assign tourLauncherEl. Focus restoration "
        "needs the saved reference."
    )
    # endTour must restore focus.
    end_fn = re.search(
        r'function\s+endTour\s*\(\s*persistent\s*\)\s*\{[\s\S]{0,1500}?\n\}',
        body,
    )
    assert end_fn is not None, "endTour function not found"
    end_chunk = end_fn.group(0)
    assert "tourLauncherEl" in end_chunk and ".focus" in end_chunk, (
        "endTour does not restore focus to the launcher. Screen-reader "
        "users will land on <body> with no anchor (WCAG SC 2.4.3)."
    )


def test_take_tour_handler_captures_launcher_before_hiding_banner() -> None:
    """Codex P58-02 R2 MEDIUM: the welcomeTakeTourBtn click handler
    must capture the launcher BEFORE calling hideWelcomeBannerSessionOnly.
    Otherwise startTour's activeElement snapshot would include a button
    whose ancestor was just marked [hidden], breaking focus restore."""
    body = _read()
    handler_match = re.search(
        r'welcomeTakeTourBtn[\s\S]{0,200}?addEventListener\s*\(\s*"click"'
        r'[\s\S]{0,800}?\}\s*\)\s*;',
        body,
    )
    assert handler_match is not None, (
        "welcomeTakeTourBtn click handler not found"
    )
    chunk = handler_match.group(0)
    # The handler must capture e.currentTarget (or e.target) before
    # calling hideWelcomeBannerSessionOnly.
    capture_idx = -1
    hide_idx = -1
    capture_match = re.search(r'(?:currentTarget|target)\b', chunk)
    if capture_match:
        capture_idx = capture_match.start()
    hide_match = re.search(r'hideWelcomeBannerSessionOnly', chunk)
    if hide_match:
        hide_idx = hide_match.start()
    assert capture_idx >= 0, (
        "welcomeTakeTourBtn handler does not capture e.currentTarget "
        "/ e.target. The launcher must be captured explicitly so it "
        "survives the banner hide (Codex R2 MEDIUM)."
    )
    assert hide_idx >= 0, (
        "welcomeTakeTourBtn handler does not call "
        "hideWelcomeBannerSessionOnly."
    )
    assert capture_idx < hide_idx, (
        "welcomeTakeTourBtn handler hides the banner BEFORE capturing "
        "the launcher. After hide, the launcher is inside [hidden] "
        "ancestor and focus restore won't work (Codex R2 MEDIUM)."
    )
    # And startTour must be called with the captured ref.
    assert re.search(r'startTour\s*\(\s*launcher\b', chunk), (
        "welcomeTakeTourBtn handler does not call startTour(launcher). "
        "The captured ref must be passed explicitly."
    )


def test_end_tour_falls_back_to_visible_control() -> None:
    """Codex P58-02 R2 MEDIUM: even with an explicit launcher reference,
    if that launcher lives inside a hidden ancestor (typical case:
    welcome banner was dismissed before tour), .focus() is a silent
    no-op and focus lands on <body>. endTour must check focusability
    (not inside [hidden] ancestor) AND fall back to a visible control
    like #presetSelect when the launcher is unavailable."""
    body = _read()
    end_fn = re.search(
        r'function\s+endTour\s*\(\s*persistent\s*\)\s*\{[\s\S]{0,1500}?\n\}',
        body,
    )
    assert end_fn is not None, "endTour function not found"
    chunk = end_fn.group(0)
    # Must check that the launcher is NOT inside a hidden ancestor.
    has_hidden_check = (
        re.search(r'closest\s*\(\s*["\']\[hidden\]', chunk)
        or "isLauncherFocusable" in chunk
    )
    assert has_hidden_check, (
        "endTour does not check whether the launcher's ancestor is "
        "[hidden]. Hidden launcher → focus falls to <body>. Either "
        "inline `el.closest('[hidden]')` or call a helper "
        "isLauncherFocusable (Codex R2 MEDIUM)."
    )
    # Must fall back to a visible control if launcher unavailable —
    # specifically, an EXECUTABLE branch: document.getElementById
    # ("presetSelect") plus a .focus() call on it. Codex P58-02 R3 LOW:
    # bare "presetSelect" string match would let a future regression
    # leave only a comment behind and still pass.
    fallback_pattern = (
        r'document\.getElementById\s*\(\s*["\']presetSelect["\']\s*\)'
        r'[\s\S]{0,300}?\.focus\s*\('
    )
    assert re.search(fallback_pattern, chunk), (
        "endTour does not contain an executable "
        "document.getElementById('presetSelect') + .focus() fallback. "
        "Bare string match isn't enough — the fallback must be a real "
        "code path (Codex P58-02 R3 LOW)."
    )


# ── 6. No third-party dependency leaked in ──


# ── 7. Inline-script syntax check (Codex R1 HIGH carry-forward) ──


def test_inline_script_parses_as_valid_javascript() -> None:
    """Codex P58-02 R1 HIGH: the previous P58-02 commit shipped step 3's
    desc with unescaped ASCII `"` mid-string ("用户暂存"), which closed
    the JS string early and made the entire inline `<script>` block
    fail to parse — `node --check` raised SyntaxError, the page never
    booted. Regex-on-source tests cannot catch this class of bug
    because they don't model JS grammar.

    This test extracts the inline `<script>` block and runs it through
    `node --check`, which validates JS syntax without executing. If
    Node is not installed (CI without Node), the test is skipped with
    a clear reason.

    Without this test, future curly-quote/escape mistakes in TOUR_STEPS
    descriptions or any other inline JS will silently break the page
    until a manual browser test catches it.
    """
    if shutil.which("node") is None:
        pytest.skip(
            "node not installed — JS syntax check skipped. Install "
            "Node.js to enable this safety net."
        )
    body = TIMELINE_SIM.read_text(encoding="utf-8")
    # Extract every <script>...</script> block (the file has one large
    # inline block plus possibly external-src tags which we ignore).
    script_blocks = re.findall(
        r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',
        body,
    )
    assert script_blocks, "no inline <script> block found"
    for idx, js in enumerate(script_blocks):
        result = subprocess.run(
            ["node", "--check", "-"],
            input=js,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, (
            f"inline <script> block #{idx} fails `node --check` "
            f"(JS syntax error). Without this test we'd ship a broken "
            f"page. Stderr:\n{result.stderr}"
        )


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
