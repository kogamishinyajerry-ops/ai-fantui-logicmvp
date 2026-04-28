"""P56-02a — link cockpit pages to the shared etras_chrome.css.

This is the structural step BEFORE token unification: the two cockpit
pages (demo.html, c919_etras_workstation.html) currently have their
own token namespaces (--fan-*, --etras-*) and an inline copy of the
iframe-embed nav-suppression rule that already lives in
/etras_chrome.css since P56-01.

P56-02a — minimal, zero-visual-change:
  - both cockpits <link> /etras_chrome.css (extension point for
    future token alignment in P56-02b)
  - both cockpits drop the duplicate iframe-embed inline CSS
  - the iframe-embed contract continues to hold (verified against
    the shared file via the link follow done in P54-04 / P54-06
    tests since round-1 P3 fix)

P56-02b (follow-up, requires user approval on color choice) will
alias the local --fan-* / --etras-* tokens to shared ones so all
four E-TRAS surfaces draw from a single palette.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"


COCKPIT_PAGES = [
    STATIC / "demo.html",
    STATIC / "c919_etras_workstation.html",
]


@pytest.mark.parametrize(
    "page",
    COCKPIT_PAGES,
    ids=lambda p: p.name,
)
def test_cockpit_links_shared_chrome(page: Path) -> None:
    """Both cockpit pages must link /etras_chrome.css so they pick
    up the shared iframe-embed nav-suppression + (future) shared
    palette tokens. Without this link, P56-02b can't alias the
    local tokens to shared."""
    body = page.read_text(encoding="utf-8")
    assert (
        '"/etras_chrome.css"' in body
        or '"etras_chrome.css"' in body
    ), (
        f"{page.name} must <link> the shared /etras_chrome.css"
    )


@pytest.mark.parametrize(
    "page",
    COCKPIT_PAGES,
    ids=lambda p: p.name,
)
def test_cockpit_strips_inline_iframe_embed_css(page: Path) -> None:
    """The iframe-embed nav-suppression rule already lives in
    /etras_chrome.css since P56-01. Keeping a duplicate inline copy
    creates two sources of truth — a future tweak (e.g. a different
    selector) lands in one and not the other."""
    body = page.read_text(encoding="utf-8")
    # Find inline <style> blocks.
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", body, re.DOTALL)
    inline_css = "\n".join(style_blocks)
    # Strip CSS comments so a docblock mentioning the rule by name
    # doesn't false-positive.
    inline_css = re.sub(r"/\*.*?\*/", "", inline_css, flags=re.DOTALL)
    assert "html.is-iframe-embed .unified-nav" not in inline_css, (
        f"{page.name} still inlines `html.is-iframe-embed .unified-nav` "
        f"— move it to etras_chrome.css (already there since P56-01)"
    )
    assert "html.is-iframe-embed body.unified-nav-enabled" not in inline_css, (
        f"{page.name} still inlines the iframe-embed body padding "
        f"override — already in etras_chrome.css"
    )


@pytest.mark.parametrize(
    "page",
    COCKPIT_PAGES,
    ids=lambda p: p.name,
)
def test_cockpit_keeps_iframe_embed_detection_script(page: Path) -> None:
    """The detection script that adds `.is-iframe-embed` to <html>
    when window.self !== window.top stays inline — it's per-page
    JS, not CSS. Removing it would break the iframe contract."""
    body = page.read_text(encoding="utf-8")
    assert "window.self !== window.top" in body, (
        f"{page.name} must keep the iframe-embed detection script "
        f"(adds .is-iframe-embed class to <html> on first paint)"
    )
    assert "is-iframe-embed" in body


# ─── App-shell scoping: chrome's full-viewport rules must NOT
#     leak into cockpit pages that don't opt-in. ───


def test_chrome_root_scope_is_safe_for_cockpits() -> None:
    """Codex P56-02a round-1 P1: the chrome's `html, body { height:
    100%; overflow: hidden; }` and `body { display: flex; ... }`
    rules were sized for the sim panels' fixed-viewport layout, but
    leak into the cockpits' document-flow scrolling when linked
    naïvely. The fix is to scope app-shell rules to opt-in
    `body.etras-app` so cockpits inheriting only the root-scoped
    bits (color tokens, scrollbar, iframe-embed) stay intact."""
    chrome = (
        REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
    ).read_text(encoding="utf-8")
    # Bare `html, body { ... overflow: hidden ... }` would leak into
    # any importing page. Must be scoped via :has(body.etras-app)
    # or a body.etras-app selector chain.
    bare_html_body = re.search(
        r"^html\s*,\s*body\s*\{[^}]*overflow:\s*hidden[^}]*\}",
        chrome,
        re.MULTILINE | re.DOTALL,
    )
    assert bare_html_body is None, (
        "etras_chrome.css must NOT declare an unscoped `html, body "
        "{ overflow: hidden }` rule — it leaks into cockpit pages "
        "that import the chrome for tokens but use document flow"
    )
    # And the scoped form must exist somewhere.
    assert "body.etras-app" in chrome, (
        "etras_chrome.css missing the body.etras-app opt-in scope"
    )


def test_chrome_html_rule_does_not_rely_on_has() -> None:
    """Codex P56-02a round-4 P2: `:has()` still misses on older
    Firefox ESR + some embedded Chromium shells. The html-level
    full-viewport rule must use a regular class selector instead
    so unsupported browsers fall back gracefully."""
    chrome = (
        REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
    ).read_text(encoding="utf-8")
    chrome_no_comments = re.sub(r"/\*.*?\*/", "", chrome, flags=re.DOTALL)
    assert ":has(" not in chrome_no_comments, (
        "etras_chrome.css must not rely on :has() — older Firefox "
        "ESR / embedded Chromium ignore it, breaking the sim shell "
        "layout. Use html.etras-app-root or similar opt-in class."
    )
    # The opt-in class form must exist.
    assert "html.etras-app-root" in chrome_no_comments


@pytest.mark.parametrize(
    "page_path",
    [
        "src/well_harness/static/fan_console.html",
        "src/well_harness/static/c919_etras_panel/index.html",
    ],
    ids=["fan_console", "c919_panel"],
)
def test_sim_panel_html_carries_etras_app_root_class(page_path: str) -> None:
    """Codex P56-02a round-4 P2: sim panels must declare the
    full-viewport opt-in via a static class on <html>, NOT through
    :has(body.etras-app). Class declared inline on the tag co-
    exists with the iframe-embed script's classList.add('is-
    iframe-embed') call."""
    body = (REPO_ROOT / page_path).read_text(encoding="utf-8")
    html_match = re.search(r"<html[^>]*\bclass=\"([^\"]+)\"", body)
    assert html_match is not None, (
        f"{page_path} <html> tag must carry class attribute"
    )
    classes = html_match.group(1).split()
    assert "etras-app-root" in classes, (
        f"{page_path} <html> missing `etras-app-root` class — "
        f"required for the opt-in full-viewport layout"
    )


def test_app_shell_body_does_not_clobber_unified_nav_padding() -> None:
    """Codex P56-02a round-2 P1: `body.etras-app { padding: 0 }`
    has equal specificity to unified-nav.css's `body.unified-nav-
    enabled { padding-top: var(--nav-height) }` but loads later,
    so it would clobber the 48px nav spacer on non-embedded sim
    pages. The chrome must not declare ANY `padding` (shorthand or
    longhand) on body.etras-app — let unified-nav-enabled control
    that property.

    Codex P56-02a round-3 P2: `margin: 0` IS allowed and required
    (zeroes the UA default `body { margin: 8px }`). unified-nav.css
    does not declare margin on body, so no conflict."""
    chrome = (
        REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
    ).read_text(encoding="utf-8")
    # Strip comments BEFORE the rule extraction so a `}` inside a
    # docblock comment can't terminate the [^}]+ capture.
    chrome_no_comments = re.sub(r"/\*.*?\*/", "", chrome, flags=re.DOTALL)
    body_rule = re.search(
        r"body\.etras-app\s*\{([^}]+)\}",
        chrome_no_comments,
        re.DOTALL,
    )
    assert body_rule is not None
    body_props = body_rule.group(1)
    assert not re.search(
        r"^\s*padding(-top|-right|-bottom|-left)?\s*:",
        body_props,
        re.MULTILINE,
    ), (
        "body.etras-app must not declare padding (shorthand or "
        "longhand) — unified-nav.css's body.unified-nav-enabled "
        "padding-top owns that property"
    )


def test_app_shell_resets_default_body_margin() -> None:
    """Codex P56-02a round-3 P2: removing the wildcard descendant
    reset (round-2) was correct, but it also took away the body's
    own UA-default-margin reset. With nothing zeroing `body
    { margin: 8px }`, the full-viewport sim shell rendered with an
    8px gutter around it. The chrome must declare `margin: 0` on
    body.etras-app — safe because unified-nav.css doesn't touch
    body margin."""
    chrome = (
        REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
    ).read_text(encoding="utf-8")
    # Strip comments BEFORE locating the rule (a comment containing
    # `}` would terminate the [^}]+ capture early).
    chrome_no_comments = re.sub(r"/\*.*?\*/", "", chrome, flags=re.DOTALL)
    body_rule = re.search(
        r"body\.etras-app\s*\{([^}]+)\}",
        chrome_no_comments,
        re.DOTALL,
    )
    assert body_rule is not None
    body_props = body_rule.group(1)
    assert re.search(
        r"^\s*margin\s*:\s*0\s*;",
        body_props,
        re.MULTILINE,
    ), (
        "body.etras-app must declare `margin: 0` to clear the UA "
        "default 8px body margin — without it the full-viewport "
        "shell renders with an 8px gutter"
    )


def test_app_shell_no_wildcard_descendant_reset() -> None:
    """Codex P56-02a round-2 P1: `body.etras-app * { margin: 0;
    padding: 0 }` outranks unified-nav.css's class selectors
    (specificity 0,1,1 vs 0,1,0) and collapses .unified-nav-brand /
    .unified-nav-group / .unified-nav-link spacing on every sim
    page. The wildcard descendant reset must not exist."""
    chrome = (
        REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
    ).read_text(encoding="utf-8")
    # Strip /* ... */ comments so docblock examples don't false-positive.
    chrome_no_comments = re.sub(r"/\*.*?\*/", "", chrome, flags=re.DOTALL)
    bad = re.search(
        r"body\.etras-app\s+\*\s*\{[^}]*(margin|padding)\s*:",
        chrome_no_comments,
        re.DOTALL,
    )
    assert bad is None, (
        "etras_chrome.css must NOT declare `body.etras-app * { margin/padding }` — "
        "outranks unified-nav.css and breaks the top nav layout"
    )


def test_chrome_app_shell_components_are_scoped() -> None:
    """Component selectors that historically lived bare (.btn,
    .workspace, .panel, .sec, etc.) must now sit under the
    body.etras-app scope. Otherwise importing the chrome from a
    page that uses .panel or .btn for its own classes (cockpit
    c919_etras_workstation.css does!) inherits unwanted properties
    from the chrome rule."""
    chrome = (
        REPO_ROOT / "src" / "well_harness" / "static" / "etras_chrome.css"
    ).read_text(encoding="utf-8")
    leaky_classes = [
        ".btn",
        ".workspace",
        ".panel",
        ".sec",
        ".row",
        ".tog",
        ".hbadge",
        ".sim-indicator",
        ".state-pill",
    ]
    for cls in leaky_classes:
        # An unscoped rule would be `^<class> {`. A scoped rule is
        # `body.etras-app <class> {` or similar.
        bare = re.search(
            rf"^\s*{re.escape(cls)}\s*\{{",
            chrome,
            re.MULTILINE,
        )
        assert bare is None, (
            f"etras_chrome.css declares an unscoped {cls!r} rule that "
            f"would leak into pages importing the chrome for tokens "
            f"only. Scope it under body.etras-app."
        )


@pytest.mark.parametrize(
    "page_path",
    [
        "src/well_harness/static/fan_console.html",
        "src/well_harness/static/c919_etras_panel/index.html",
    ],
    ids=["fan_console", "c919_panel"],
)
def test_sim_panel_body_carries_etras_app_class(page_path: str) -> None:
    """Sim panels opt INTO the chrome's full-viewport layout by
    adding `etras-app` to body. Without this class, the chrome's
    app-shell rules don't activate and the sim panel falls back to
    document flow (broken)."""
    body = (REPO_ROOT / page_path).read_text(encoding="utf-8")
    body_match = re.search(r"<body[^>]*\bclass=\"([^\"]+)\"", body)
    assert body_match is not None, f"{page_path} has no <body class=...>"
    classes = body_match.group(1).split()
    assert "etras-app" in classes, (
        f"{page_path} <body> missing `etras-app` class — without it, "
        f"the chrome's full-viewport layout doesn't activate"
    )


@pytest.mark.parametrize(
    "page",
    COCKPIT_PAGES,
    ids=lambda p: p.name,
)
def test_cockpit_body_does_not_carry_etras_app_class(page: Path) -> None:
    """Cockpit pages must NOT add `etras-app` — they use document
    flow, not the full-viewport sim layout. Adding it would
    re-introduce the round-1 P1 regression (overflow: hidden +
    flex column on document body)."""
    body = page.read_text(encoding="utf-8")
    body_match = re.search(r"<body[^>]*\bclass=\"([^\"]+)\"", body)
    assert body_match is not None
    classes = body_match.group(1).split()
    assert "etras-app" not in classes, (
        f"{page.name} <body> must NOT carry `etras-app` — it "
        f"activates the full-viewport sim layout which breaks the "
        f"cockpit's document flow + custom panel header"
    )


@pytest.mark.parametrize(
    "page",
    COCKPIT_PAGES,
    ids=lambda p: p.name,
)
def test_cockpit_link_order_etras_chrome_before_local_css(page: Path) -> None:
    """The shared chrome must load BEFORE the page-local stylesheet
    so local rules can `var(--bg0)` etc. without the variable being
    undefined. Wrong order = local rules silently render with
    fallback values."""
    body = page.read_text(encoding="utf-8")
    chrome_match = re.search(
        r'<link[^>]*\bhref="/?etras_chrome\.css"',
        body,
    )
    if chrome_match is None:
        # The previous test catches this; let it carry the failure.
        return
    chrome_pos = chrome_match.start()
    # Find the page-local stylesheet (demo.css or
    # c919_etras_workstation.css) link.
    local_match = re.search(
        r'<link[^>]*\bhref="/?(?:demo|c919_etras_workstation)\.css"',
        body,
    )
    assert local_match is not None, (
        f"{page.name}: cannot locate the page-local stylesheet link"
    )
    assert chrome_pos < local_match.start(), (
        f"{page.name}: /etras_chrome.css must be linked BEFORE the "
        f"page-local stylesheet so shared tokens are defined when "
        f"local rules consume them via var()"
    )
