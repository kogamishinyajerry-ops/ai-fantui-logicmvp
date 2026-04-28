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
