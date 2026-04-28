"""P58-01 — welcome banner + floating ? help button (onboarding kickoff).

The user reported "新手刚刚打开这个工作台页面，就可以快速地理解这个工作台
该如何使用" as the bar for enterprise-grade. P58 is the onboarding arc.

P58-01 ships the smallest possible discoverable surface:
  1. A welcome banner above the existing layout. Tells the user what
     this page does in 2 lines and offers three actions:
        - 🎯 引导漫游 (stub today; P58-02 wires the real tour)
        - 📦 加载一个示例 (loads C919 nominal preset)
        - 知道了，不再显示 (dismiss + persist)
  2. A floating ? button bottom-right that re-opens the banner. This
     is the affordance for users who dismissed and later need help.
  3. Versioned localStorage dismissal flag (`-v1` suffix) so future
     P58 phases can force-show the banner again without losing the
     preference for older cohorts.

Strict design constraint (per user directive 2026-04-28):
  > 绝对不要推翻现在的 UI 设计

After dismissal, the page renders identically to pre-P58 layout —
no color/typography/positioning changes to existing elements. The
banner is the FIRST child of <main>; once hidden via the `hidden`
attribute it occupies zero pixels.

Tests use the regex-on-source contract pattern (continuing the P57
convention) since timeline-sim.html is single-file vanilla JS.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TIMELINE_SIM = REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"


def _read() -> str:
    return TIMELINE_SIM.read_text(encoding="utf-8")


# ── 1. Banner DOM presence + structure ──


def test_welcome_banner_exists() -> None:
    """The welcome banner must be an <aside id="welcomeBanner"> element
    so it has the right semantics for assistive tech and a stable id
    the test suite can target."""
    body = _read()
    pattern = r'<aside\s+id="welcomeBanner"[^>]*class="welcome-banner"'
    assert re.search(pattern, body), (
        "welcome banner <aside id=welcomeBanner> not found. "
        "P58-01 needs an additive banner above the existing layout."
    )


def test_welcome_banner_has_aria_labelledby() -> None:
    """The banner uses role=region + aria-labelledby per ARIA APG.
    Without these, screen readers announce nothing meaningful when
    focus enters the banner."""
    body = _read()
    aria_pattern = (
        r'<aside\s+id="welcomeBanner"[^>]*role="region"[^>]*'
        r'aria-labelledby="welcomeBannerTitle"'
    )
    title_pattern = r'<h2\s+id="welcomeBannerTitle"'
    assert re.search(aria_pattern, body), (
        "welcome banner missing role=region + aria-labelledby"
    )
    assert re.search(title_pattern, body), (
        "welcome banner title element id=welcomeBannerTitle not found"
    )


def test_welcome_banner_starts_hidden_in_markup() -> None:
    """The banner ships with the `hidden` attribute in the static
    markup. JS un-hides on first load if not dismissed; this avoids
    a flash-of-content for returning users (FOUC) where the banner
    paints for one frame before the dismiss check runs."""
    body = _read()
    # The hidden attribute may appear before or after class — match either.
    pattern = (
        r'<aside\s+id="welcomeBanner"[^>]*\bhidden\b'
    )
    assert re.search(pattern, body), (
        "welcome banner must include `hidden` attribute in static "
        "markup so returning users don't see a flash of the banner "
        "before JS runs the dismiss check."
    )


# ── 2. Action buttons ──


@pytest.mark.parametrize(
    "btn_id",
    ["welcomeTakeTourBtn", "welcomeLoadExampleBtn",
     "welcomeDismissBtn", "welcomeDismissBtn2"],
)
def test_welcome_banner_action_buttons_exist(btn_id: str) -> None:
    """Each banner action must have a stable id so the JS handlers
    can find it. Two dismiss buttons (× corner + the inline 知道了
    button) cover both keyboard-tab users and 'I'm done reading'
    flows."""
    body = _read()
    pattern = rf'<button[^>]*\bid="{btn_id}"'
    assert re.search(pattern, body), (
        f"welcome banner action button id={btn_id!r} not found"
    )


def test_welcome_load_example_button_loads_c919_nominal() -> None:
    """The 加载示例 button must call loadPresetInEditor with a real
    preset key. Picking c919_nominal because it's the most-frequently-
    used C919 fixture and demonstrates the deploy chain end-to-end."""
    body = _read()
    # Look for the click handler on welcomeLoadExampleBtn that calls
    # loadPresetInEditor with c919_nominal.
    pattern = (
        r'welcomeLoadExampleBtn[\s\S]{0,200}?addEventListener\s*\(\s*"click"'
        r'[\s\S]{0,300}?loadPresetInEditor\s*\(\s*"c919_nominal"'
    )
    assert re.search(pattern, body), (
        "welcomeLoadExampleBtn click handler does not call "
        "loadPresetInEditor('c919_nominal'). The example button is "
        "supposed to land the user in a real, runnable scenario."
    )


# ── 3. Re-open affordance: keyboard shortcut, not visible UI ──
#
# Codex R1 HIGH (2026-04-28): a persistent floating ? button violates
# the user's "additive-only post-dismiss" directive — it's a new
# always-visible UI element vs pre-P58. Re-open moved to a Shift+?
# keyboard shortcut (invisible to layout). P58-03 will document it
# via the cheatsheet modal.


def test_no_floating_help_button_in_markup() -> None:
    """Codex R1 HIGH: a persistent floating ? FAB breaks the "additive-
    only post-dismiss" contract because it remains visible for
    returning users (different from pre-P58). The FAB must be absent
    from both DOM and CSS in P58-01."""
    body = _read()
    forbidden_dom = re.search(
        r'<button[^>]*\bid="helpFloatingBtn"',
        body,
    )
    forbidden_class = re.search(r'class="[^"]*\bhelp-fab\b', body)
    forbidden_css = re.search(r'\.help-fab\s*\{', body)
    assert forbidden_dom is None, (
        "helpFloatingBtn is back in the DOM — Codex R1 HIGH said this "
        "is a new always-visible element vs pre-P58 layout. Use the "
        "Shift+? keyboard shortcut for re-open instead."
    )
    assert forbidden_class is None, (
        "help-fab class still in markup — remove it (Codex R1 HIGH)."
    )
    assert forbidden_css is None, (
        "`.help-fab` CSS selector still defined — remove it (Codex R1 HIGH)."
    )


def test_keyboard_shortcut_reopens_banner() -> None:
    """Re-open affordance: Shift+? key listener calls showWelcomeBanner.
    No visible UI change, so dismissed-state layout stays pixel-identical
    to pre-P58."""
    body = _read()
    # The keydown listener must check e.key === "?" AND e.shiftKey AND
    # call showWelcomeBanner.
    pattern = (
        r'document\.addEventListener\s*\(\s*"keydown"'
        r'[\s\S]{0,800}?e\.key\s*===\s*"\?"'
        r'[\s\S]{0,200}?e\.shiftKey'
        r'[\s\S]{0,200}?showWelcomeBanner\s*\('
    )
    assert re.search(pattern, body), (
        "keydown listener for Shift+? not found, or does not call "
        "showWelcomeBanner(). This is the re-open affordance for "
        "dismissed users."
    )


def test_keyboard_shortcut_skips_form_inputs() -> None:
    """The Shift+? shortcut must not fire while the user is typing in
    INPUT/TEXTAREA/SELECT/contenteditable — typing `?` in the JSON
    textarea must NOT pop the banner over the editor."""
    body = _read()
    # Check the listener guards against form inputs before checking the key.
    pattern = (
        r'document\.addEventListener\s*\(\s*"keydown"'
        r'[\s\S]{0,400}?(?:tagName\s*===\s*"INPUT"'
        r'|tagName\s*===\s*"TEXTAREA")'
    )
    assert re.search(pattern, body), (
        "keydown listener does not skip form inputs. Typing in the "
        "JSON textarea would inadvertently pop the welcome banner."
    )


# ── 4. Persistence: versioned localStorage dismissal flag ──


def test_welcome_dismiss_flag_uses_versioned_key() -> None:
    """Versioned key (`-v1`) so future P58 phases can re-show the
    banner for material content changes without nuking everyone's
    dismissal preference. Naked `welcome-dismissed` would force
    awkward migration in P58-02+."""
    body = _read()
    pattern = (
        r'WELCOME_DISMISSED_KEY\s*=\s*"well-harness:welcome-dismissed-v1"'
    )
    assert re.search(pattern, body), (
        "WELCOME_DISMISSED_KEY const must be the versioned literal "
        "'well-harness:welcome-dismissed-v1'. Bare `welcome-dismissed` "
        "would force awkward migration when P58-02 changes the "
        "banner content."
    )


def test_dismiss_handlers_persist_to_localstorage() -> None:
    """The dismiss handlers must call setWelcomeDismissed(true) which
    in turn calls localStorage.setItem with the versioned key. Without
    persistence, every page refresh would re-show the banner — that's
    aggressive at best, hostile at worst."""
    body = _read()
    # Look for the dismissWelcomeBanner function calling setWelcomeDismissed(true).
    fn_pattern = (
        r'function\s+dismissWelcomeBanner\s*\(\s*\)\s*\{[^}]*'
        r'setWelcomeDismissed\s*\(\s*true\s*\)'
    )
    assert re.search(fn_pattern, body), (
        "dismissWelcomeBanner() does not call setWelcomeDismissed(true). "
        "Banner dismissal must persist across reloads."
    )
    # And setWelcomeDismissed must call localStorage.setItem with the key.
    setitem_pattern = (
        r'function\s+setWelcomeDismissed[\s\S]{0,300}?'
        r'localStorage\.setItem\s*\(\s*WELCOME_DISMISSED_KEY'
    )
    assert re.search(setitem_pattern, body), (
        "setWelcomeDismissed does not call localStorage.setItem with "
        "WELCOME_DISMISSED_KEY. Dismissal would not persist."
    )


def test_localstorage_access_wrapped_in_try_catch() -> None:
    """localStorage throws under quota-exceeded or private-browsing.
    Both isWelcomeDismissed and setWelcomeDismissed must wrap access
    in try/catch so the entire onboarding flow doesn't break in
    incognito tabs (P57-03 R1 carry-forward)."""
    body = _read()
    # Find each function and verify try/catch around localStorage access.
    for fn_name in ("isWelcomeDismissed", "setWelcomeDismissed"):
        fn_match = re.search(
            rf'function\s+{fn_name}\s*\([^)]*\)\s*\{{[\s\S]{{0,500}}?\n\}}',
            body,
        )
        assert fn_match is not None, f"function {fn_name} not found"
        chunk = fn_match.group(0)
        has_try_catch = re.search(
            r'try\s*\{[^}]*localStorage\.[gs]etItem[\s\S]*?\}\s*catch',
            chunk,
        ) or re.search(
            r'try\s*\{[^}]*localStorage\.[gs]etItem[\s\S]*?'
            r'localStorage\.removeItem[\s\S]*?\}\s*catch',
            chunk,
        )
        assert has_try_catch is not None, (
            f"{fn_name}: localStorage access not wrapped in try/catch. "
            f"Private-browsing throw would break onboarding (P57-03 "
            f"R1 carry-forward)."
        )


# ── 5. First-load auto-show vs returning-user no-op ──


def test_first_load_shows_banner_when_not_dismissed() -> None:
    """The init code at the bottom of the script block must call
    showWelcomeBanner() iff isWelcomeDismissed() returns false. This
    is the first-run surface — without it, the entire onboarding
    surface is invisible."""
    body = _read()
    # Pattern: a top-level if (!isWelcomeDismissed()) showWelcomeBanner();
    pattern = (
        r'if\s*\(\s*!\s*isWelcomeDismissed\s*\(\s*\)\s*\)\s*\{?\s*'
        r'showWelcomeBanner\s*\('
    )
    assert re.search(pattern, body), (
        "first-load auto-show check missing. Need: "
        "if (!isWelcomeDismissed()) showWelcomeBanner();"
    )


# ── 6. Take-Tour stub: must not persist dismissal (Codex R1 MEDIUM) ──


def test_take_tour_stub_does_not_persist_dismissal() -> None:
    """Codex R1 MEDIUM: until P58-02 ships the real tour, clicking
    'Take a tour' must NOT persist dismissal — otherwise a first-time
    user who clicks the promised onboarding path loses the banner
    permanently without receiving any onboarding.

    The stub handler must NOT call dismissWelcomeBanner (which writes
    localStorage). Session-only hide via hideWelcomeBannerSessionOnly
    is acceptable — banner returns on next reload."""
    body = _read()
    # Find the welcomeTakeTourBtn click handler block.
    handler_match = re.search(
        r'welcomeTakeTourBtn[\s\S]{0,200}?addEventListener\s*\(\s*"click"'
        r'[\s\S]{0,800}?\}\s*\)\s*;',
        body,
    )
    assert handler_match is not None, (
        "welcomeTakeTourBtn click handler not found"
    )
    chunk = handler_match.group(0)
    # The handler MUST NOT call dismissWelcomeBanner (which persists).
    assert "dismissWelcomeBanner" not in chunk, (
        "welcomeTakeTourBtn click handler calls dismissWelcomeBanner — "
        "this persists dismissal but the tour doesn't exist yet. "
        "Use hideWelcomeBannerSessionOnly() so the banner returns on "
        "next reload (Codex R1 MEDIUM)."
    )


def test_take_tour_button_label_indicates_coming_soon() -> None:
    """The Take-Tour button's visible label must signal that the tour
    is not yet available — otherwise users click it expecting a
    tour and get a status message instead. Codex R1 MEDIUM: relabel
    or disable until P58-02 ships."""
    body = _read()
    # Find the button text — should contain something like "P58-02"
    # or "即将上线" or "coming soon" so the user knows what to expect.
    btn_match = re.search(
        r'<button[^>]*\bid="welcomeTakeTourBtn"[^>]*>'
        r'([\s\S]{0,200}?)</button>',
        body,
    )
    assert btn_match is not None, "welcomeTakeTourBtn element not found"
    label = btn_match.group(1)
    coming_soon = (
        "即将上线" in label
        or "coming soon" in label.lower()
        or "P58-02" in label
    )
    assert coming_soon, (
        f"welcomeTakeTourBtn label does not indicate coming-soon "
        f"status. Current label: {label!r}. Users clicking the "
        f"primary onboarding CTA expect a tour; the label must "
        f"flag that it's not yet available (Codex R1 MEDIUM)."
    )
