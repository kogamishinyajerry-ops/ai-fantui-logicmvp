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


# ── 3. Floating ? help button ──


def test_floating_help_button_exists() -> None:
    """A persistent ? button bottom-right is the affordance for users
    who dismissed the banner and later need help. Without it, dismissal
    is a one-way door."""
    body = _read()
    pattern = (
        r'<button[^>]*\bid="helpFloatingBtn"[^>]*class="help-fab"'
    )
    assert re.search(pattern, body), (
        "floating help button id=helpFloatingBtn class=help-fab not "
        "found. After welcome dismiss, users have no way to re-open "
        "the banner without this affordance."
    )


def test_floating_help_button_reopens_banner() -> None:
    """Clicking the ? button must re-show the welcome banner. Otherwise
    the affordance is a no-op and dismiss is still one-way."""
    body = _read()
    pattern = (
        r'helpFloatingBtn[\s\S]{0,200}?addEventListener\s*\(\s*"click"'
        r'[\s\S]{0,300}?showWelcomeBanner\s*\('
    )
    assert re.search(pattern, body), (
        "helpFloatingBtn click handler does not call "
        "showWelcomeBanner(). The ? affordance must re-open the banner."
    )


def test_floating_help_button_has_aria_label() -> None:
    """Screen readers see only the literal `?` glyph without aria-label.
    Required for WCAG SC 4.1.2."""
    body = _read()
    pattern = (
        r'<button[^>]*\bid="helpFloatingBtn"[^>]*aria-label="[^"]+"'
    )
    assert re.search(pattern, body), (
        "helpFloatingBtn missing aria-label. The literal `?` glyph "
        "alone is not announced meaningfully by screen readers."
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
