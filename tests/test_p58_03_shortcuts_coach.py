"""P58-03 — keyboard shortcuts + cheatsheet modal + empty-state coaching.

Three additive surfaces:

1. Empty-state coaching — when currentTimeline.events is empty (e.g.
   user picks (自定义空白) preset), renderEventTable shows a hint card
   with 4 starter chips (one per kind). Click chip → append a
   defaults-filled event of that kind. Replaces the bare empty <tbody>
   that previously left "(自定义空白)" users staring at nothing.

2. Cheatsheet modal — `?` key (no shift) opens a modal listing the
   keyboard shortcuts. Replaces P58-01's Shift+? "reopen banner" —
   `?` is the universal help affordance, with the welcome reopen
   moving inside the modal as a button. Modal has Esc-to-close +
   focus management + visible-fallback restore (mirroring the tour's
   pattern from P58-02 R2).

3. Keyboard shortcuts —
   - Cmd+Enter / Ctrl+Enter → click #runBtn (run simulation)
   - Cmd+S    / Ctrl+S      → click #saveScenarioBtn (save scratch);
                              preventDefault so browser's native
                              "Save Page" dialog doesn't fire.
   All shortcuts skip when the user is typing in an INPUT/TEXTAREA/
   SELECT/contenteditable so they never collide with text entry.

Strict additive-only per user directive (2026-04-28). Steady-state UI
unchanged — modal hidden, empty-state only renders for actually-empty
event lists, shortcuts are invisible until invoked.
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


# ── 1. Empty-state coaching ──


def test_empty_coach_renders_when_events_empty() -> None:
    """renderEventTable must check events.length === 0 and render the
    .empty-coach card instead of an empty <tbody>. Without this, users
    on (自定义空白) preset see literal nothing."""
    body = _read()
    fn_match = re.search(
        r'function\s+renderEventTable\s*\(\s*\)\s*\{[\s\S]{0,3000}?\n\}',
        body,
    )
    assert fn_match is not None, "renderEventTable function not found"
    chunk = fn_match.group(0)
    assert re.search(r'events\.length\s*===\s*0', chunk), (
        "renderEventTable does not check events.length === 0. Empty "
        "events would render an empty <tbody> with no coaching."
    )
    assert "empty-coach" in chunk, (
        "renderEventTable does not emit the .empty-coach hint card "
        "for empty events. Users would see nothing."
    )


@pytest.mark.parametrize(
    "kind",
    ["set_input", "ramp_input", "inject_fault", "assert_condition"],
)
def test_empty_coach_chips_cover_four_kinds(kind: str) -> None:
    """The empty-state must offer ALL four event kinds as starter
    chips (set_input, ramp_input, inject_fault, assert_condition).
    Missing any kind narrows the user's first-action funnel for no
    reason — they'd have to discover the missing kind via Raw JSON."""
    body = _read()
    pattern = rf'data-coach-kind="{kind}"'
    assert re.search(pattern, body), (
        f"empty-state coach is missing a chip for kind={kind!r}. "
        f"All four kinds (set_input/ramp_input/inject_fault/"
        f"assert_condition) must be offered as starter chips."
    )


def test_empty_coach_chip_click_appends_event() -> None:
    """Clicking an empty-state chip must append a starter event of
    the indicated kind. Without this, the chips are decorative — the
    user clicks but nothing happens."""
    body = _read()
    # The handler matches `.empty-coach-chip` clicks via event delegation.
    pattern = (
        r'addEventListener\s*\(\s*"click"[\s\S]{0,200}?'
        r'(?:closest\(\s*["\']\.empty-coach-chip|'
        r'classList[\s\S]{0,100}?empty-coach-chip)'
        r'[\s\S]{0,1000}?currentTimeline\.events\.push'
    )
    assert re.search(pattern, body), (
        "empty-state chip click handler does not append to "
        "currentTimeline.events. Chips would be decorative no-ops."
    )


def test_empty_coach_chip_handler_calls_render_and_sync() -> None:
    """After appending the starter event, the chip handler must call
    renderEventTable() AND syncToTextarea() — otherwise the new event
    is in the model but not in the visual table or Raw JSON view."""
    body = _read()
    handler_match = re.search(
        r'addEventListener\s*\(\s*"click"[\s\S]{0,200}?'
        r'empty-coach-chip[\s\S]{0,1500}?\}\s*\)\s*;',
        body,
    )
    assert handler_match is not None, (
        "empty-state chip click handler not found"
    )
    chunk = handler_match.group(0)
    assert "renderEventTable" in chunk, (
        "chip handler does not call renderEventTable() after appending. "
        "Visual table would stay stale."
    )
    assert "syncToTextarea" in chunk, (
        "chip handler does not call syncToTextarea() after appending. "
        "Raw JSON view would stay stale."
    )


# ── 2. Cheatsheet modal DOM ──


def test_shortcut_modal_exists_and_hidden_by_default() -> None:
    """The cheatsheet modal must be a <div id=shortcutModal> with the
    `hidden` attribute in static markup. Without `hidden`, the modal
    flashes open on first paint before JS sets it (FOUC)."""
    body = _read()
    pattern = (
        r'<div\s+id="shortcutModal"[^>]*class="shortcut-modal"'
        r'[^>]*\bhidden\b'
    )
    assert re.search(pattern, body), (
        "shortcutModal not found, or missing `hidden` attribute. The "
        "modal must be hidden by default to avoid FOUC."
    )


def test_shortcut_modal_is_aria_modal() -> None:
    """role=dialog + aria-modal=true + aria-labelledby — the standard
    a11y triad for modal dialogs (per ARIA APG)."""
    body = _read()
    pattern = (
        r'<div\s+id="shortcutModal"[^>]*role="dialog"'
        r'[^>]*aria-modal="true"[^>]*aria-labelledby="shortcutModalTitle"'
    )
    assert re.search(pattern, body), (
        "shortcutModal missing role=dialog + aria-modal=true + "
        "aria-labelledby=shortcutModalTitle."
    )


@pytest.mark.parametrize(
    "elem_id",
    ["shortcutModalTitle", "shortcutCloseBtn", "shortcutReopenWelcomeBtn"],
)
def test_shortcut_modal_subtree_elements(elem_id: str) -> None:
    """Modal subtree must include title (a11y label), close button
    (primary action), and reopen-welcome button (replaces P58-01's
    Shift+? affordance)."""
    body = _read()
    pattern = rf'\bid="{elem_id}"'
    assert re.search(pattern, body), (
        f"shortcutModal subtree missing element id={elem_id!r}"
    )


def test_shortcut_modal_lists_required_shortcuts() -> None:
    """The modal must list at minimum: `?`, Cmd+Enter, Cmd+S, Esc.
    A cheatsheet that omits any of these sends mixed signals
    ("which shortcuts actually exist?")."""
    body = _read()
    # Find the shortcut modal block.
    modal_match = re.search(
        r'<div\s+id="shortcutModal"[\s\S]*?</div>\s*</div>\s*</div>',
        body,
    )
    assert modal_match is not None, "shortcutModal HTML block not found"
    chunk = modal_match.group(0)
    # Each shortcut should be listed via at least one <kbd> or text.
    required_shortcuts = ["?", "Enter", "S", "Esc"]
    for sc in required_shortcuts:
        assert sc in chunk, (
            f"shortcutModal does not list {sc!r}. The cheatsheet must "
            f"document every shortcut the keydown handler responds to."
        )


# ── 3. Cheatsheet modal lifecycle ──


def test_question_mark_opens_shortcut_modal() -> None:
    """`?` key (no shift required; e.key is already "?" post-shift on
    US layouts) must open the cheatsheet modal when no form input has
    focus and no other modal/tour is active."""
    body = _read()
    # The keydown handler must contain a `?` branch that calls
    # openShortcutModal.
    pattern = (
        r'document\.addEventListener\s*\(\s*"keydown"[\s\S]*?'
        r'e\.key\s*===\s*"\?"[\s\S]{0,500}?openShortcutModal\s*\('
    )
    assert re.search(pattern, body), (
        "keydown handler does not call openShortcutModal() on `?` key. "
        "The cheatsheet has no entry point."
    )


def test_question_mark_skips_when_form_input_focused() -> None:
    """Typing `?` in the JSON textarea must not open the modal. The
    handler must check isFormInputTarget(e.target) BEFORE the `?`
    branch."""
    body = _read()
    # Find the unified P58-03 keydown handler (contains both `?` and
    # Cmd+Enter / Cmd+S branches).
    handler_match = re.search(
        r'document\.addEventListener\s*\(\s*"keydown"[\s\S]*?'
        r'(?:metaKey|ctrlKey)[\s\S]*?Enter[\s\S]*?\}\s*\)\s*;',
        body,
    )
    assert handler_match is not None, "P58-03 keydown handler not found"
    chunk = handler_match.group(0)
    assert "isFormInputTarget" in chunk, (
        "P58-03 keydown handler does not call isFormInputTarget(). "
        "Typing in the JSON textarea would inadvertently fire shortcuts."
    )


def test_form_input_helper_covers_four_input_classes() -> None:
    """isFormInputTarget must cover INPUT/TEXTAREA/SELECT/contenteditable.
    Missing any one means typing into that surface fires shortcuts —
    the JSON textarea collision was the prime example in P58-01 R1."""
    body = _read()
    fn_match = re.search(
        r'function\s+isFormInputTarget\s*\(\s*target\s*\)\s*\{'
        r'[\s\S]{0,500}?\n\}',
        body,
    )
    assert fn_match is not None, "isFormInputTarget helper not found"
    chunk = fn_match.group(0)
    for guard in ("INPUT", "TEXTAREA", "SELECT", "isContentEditable"):
        assert guard in chunk, (
            f"isFormInputTarget missing {guard!r} check. Typing in "
            f"that surface would fire shortcuts unexpectedly."
        )


def test_esc_closes_shortcut_modal() -> None:
    """Esc is the universal modal-close. The handler must check the
    modal is !hidden first — otherwise Esc anywhere would call
    closeShortcutModal which would scroll/refocus unnecessarily."""
    body = _read()
    pattern = (
        r'shortcutModal[\s\S]{0,300}?(?:hidden\s*&&|!\s*\$\("shortcutModal"\)\.hidden)'
        r'[\s\S]{0,300}?Escape[\s\S]{0,200}?closeShortcutModal'
    )
    weak_pattern = (
        r'closeShortcutModal\s*\(\s*\)'
    )
    # First check the close function is invoked from a keydown branch
    # gated on Escape + modal !hidden.
    assert re.search(weak_pattern, body), (
        "closeShortcutModal never invoked. Esc has no effect on the "
        "modal."
    )
    # Verify it's wired via a keydown handler that checks Escape.
    keydown_chunks = re.findall(
        r'document\.addEventListener\s*\(\s*"keydown"[\s\S]*?\}\s*\)\s*;',
        body,
    )
    has_esc_close = any(
        re.search(r'shortcutModal[\s\S]{0,300}?Escape[\s\S]{0,200}?closeShortcutModal', c)
        or re.search(r'Escape[\s\S]{0,200}?closeShortcutModal', c)
        for c in keydown_chunks
    )
    assert has_esc_close, (
        "no keydown handler routes Escape to closeShortcutModal. The "
        "modal can only be closed via the close button — keyboard "
        "users have no Esc affordance (WCAG SC 2.1.1)."
    )


def test_close_modal_restores_focus_with_visible_fallback() -> None:
    """Mirroring P58-02 R2 fix: closeShortcutModal must restore focus
    to the launcher (where activeElement was when modal opened) AND
    fall back to a visible control (#presetSelect) when launcher
    isn't focusable. Without fallback, focus lands on <body>."""
    body = _read()
    fn_match = re.search(
        r'function\s+closeShortcutModal\s*\(\s*\)\s*\{[\s\S]{0,1500}?\n\}',
        body,
    )
    assert fn_match is not None, "closeShortcutModal function not found"
    chunk = fn_match.group(0)
    # Must check launcher is still focusable (closest("[hidden]")
    # check, or via a helper).
    has_focusable_check = (
        re.search(r'closest\s*\(\s*["\']\[hidden\]', chunk)
        or "isLauncherFocusable" in chunk
    )
    assert has_focusable_check, (
        "closeShortcutModal does not check whether the launcher is "
        "still focusable (not inside [hidden] ancestor). Hidden "
        "launcher → focus falls to <body>."
    )
    # Must fall back to #presetSelect via executable branch.
    fallback_pattern = (
        r'document\.getElementById\s*\(\s*["\']presetSelect["\']\s*\)'
        r'[\s\S]{0,300}?\.focus\s*\('
    )
    assert re.search(fallback_pattern, chunk), (
        "closeShortcutModal has no executable fallback to "
        "#presetSelect.focus(). Hidden-launcher case lands on <body>."
    )


def test_reopen_welcome_button_works_from_modal() -> None:
    """The 'reopen welcome' button inside the modal must close the
    modal AND show the welcome banner. Without the modal close,
    the user is stuck behind the modal with the banner unreachable."""
    body = _read()
    # The handler closes modal + shows banner.
    pattern = (
        r'shortcutReopenWelcomeBtn[\s\S]{0,200}?addEventListener\s*\(\s*"click"'
        r'[\s\S]{0,500}?closeShortcutModal[\s\S]{0,200}?showWelcomeBanner'
    )
    assert re.search(pattern, body), (
        "shortcutReopenWelcomeBtn click handler does not close the "
        "modal AND reopen the welcome banner. Both actions are required."
    )


# ── 4. Cmd+Enter and Cmd+S shortcuts ──


def test_cmd_enter_triggers_run_btn() -> None:
    """Cmd+Enter / Ctrl+Enter must click #runBtn — running the
    simulation is the most-frequent action and deserves a shortcut.
    Both metaKey and ctrlKey checked so mac and win/linux users
    both benefit."""
    body = _read()
    pattern = (
        r'\(\s*e\.metaKey\s*\|\|\s*e\.ctrlKey\s*\)\s*&&\s*'
        r'e\.key\s*===\s*"Enter"[\s\S]{0,500}?'
        r'getElementById\s*\(\s*["\']runBtn["\']\s*\)'
    )
    assert re.search(pattern, body), (
        "Cmd+Enter / Ctrl+Enter shortcut does not target #runBtn. "
        "The most-frequent action has no keyboard accelerator."
    )


def test_cmd_s_triggers_save_btn_and_prevents_default() -> None:
    """Cmd+S / Ctrl+S must click #saveScenarioBtn AND preventDefault
    — without preventDefault, the browser's native Save Page As
    dialog appears, defeating the shortcut."""
    body = _read()
    # Look for the unified Cmd+S branch.
    pattern = (
        r'\(\s*e\.metaKey\s*\|\|\s*e\.ctrlKey\s*\)\s*&&\s*'
        r'\(\s*e\.key\s*===\s*"s"\s*\|\|\s*e\.key\s*===\s*"S"\s*\)'
        r'[\s\S]{0,500}?preventDefault[\s\S]{0,300}?'
        r'getElementById\s*\(\s*["\']saveScenarioBtn["\']\s*\)'
    )
    # Also accept the order: getElementById first, preventDefault
    # second — both are valid as long as both appear.
    alt_pattern = (
        r'\(\s*e\.metaKey\s*\|\|\s*e\.ctrlKey\s*\)\s*&&\s*'
        r'\(\s*e\.key\s*===\s*"s"\s*\|\|\s*e\.key\s*===\s*"S"\s*\)'
        r'[\s\S]{0,500}?preventDefault'
    )
    has_save = re.search(alt_pattern, body)
    has_btn_click = re.search(
        r'getElementById\s*\(\s*["\']saveScenarioBtn["\']\s*\)\s*[\s\S]{0,100}?'
        r'\.click\s*\(',
        body,
    )
    assert has_save is not None, (
        "Cmd+S / Ctrl+S shortcut not wired with preventDefault. The "
        "browser's native Save Page dialog would still fire."
    )
    assert has_btn_click is not None, (
        "Cmd+S handler does not click #saveScenarioBtn. The shortcut "
        "would just preventDefault but not actually save."
    )


# ── 5. Inline-script syntax (carry-forward from P58-02 R1) ──


def test_inline_script_still_parses() -> None:
    """P58-02 R1 HIGH carry-forward: every change to the inline JS
    must keep node --check passing. Without this, future copy edits
    to TOUR_STEPS / shortcut modal text could reintroduce ASCII-quote
    parse breaks."""
    if shutil.which("node") is None:
        pytest.skip("node not installed")
    body = TIMELINE_SIM.read_text(encoding="utf-8")
    script_blocks = re.findall(
        r'<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)</script>',
        body,
    )
    assert script_blocks
    for js in script_blocks:
        result = subprocess.run(
            ["node", "--check", "-"],
            input=js, capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, (
            f"inline <script> parse error:\n{result.stderr}"
        )
