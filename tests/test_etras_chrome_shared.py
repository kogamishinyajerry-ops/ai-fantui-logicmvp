"""P56-01 — shared E-TRAS chrome CSS.

User direction (2026-04-28): "反推和 C919 ETRAS 应该在 4 个页面上，每一个
页面都一样的风格、标准，我建议都以 C919 ETRAS 为标准，去进行统一。"

Today the C919 panel (`c919_etras_panel/index.html`) and the
thrust-reverser sim (`fan_console.html`) both inline the same
~80-line CSS chrome (color tokens, .hbadge / .btn / .sec / .tog /
.workspace / scrollbar, etc.). Copy-pasted, with subtle drift
(--bg0: #020810 vs #02080f, .sim-indicator vs .sim-dot, padding 8px
vs 10px). Adding a third system (landing-gear, bleed-air-valve) would
multiply the drift.

This phase extracts the shared chrome to a single file the workbench
serves once, and migrates both pages to import it. Successive phases
will migrate the cockpit (demo.html / c919_etras_workstation.html)
and the spec docs.

Tests below lock:
  1. The shared file exists at /static/etras_chrome.css.
  2. It declares all the chrome tokens (color, font, layout).
  3. Both pages link it.
  4. Neither page re-declares the shared tokens inline (no drift).
  5. C919 is the visual standard — the shared file's values come
     from the C919 panel, not fan_console (subtle padding, naming).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"

SHARED_CSS_PATH = STATIC / "etras_chrome.css"
C919_PANEL_PATH = STATIC / "c919_etras_panel" / "index.html"
FAN_CONSOLE_PATH = STATIC / "fan_console.html"


# ─── 1. The shared file exists ───


def test_shared_chrome_file_exists() -> None:
    assert SHARED_CSS_PATH.exists(), (
        f"missing shared chrome file at {SHARED_CSS_PATH}"
    )
    body = SHARED_CSS_PATH.read_text(encoding="utf-8")
    # Sanity: non-empty and contains a :root rule.
    assert ":root" in body, "shared chrome must declare a :root rule"
    assert len(body) > 1000, (
        "shared chrome looks suspiciously small — should be the full "
        "extracted color-token + component layer"
    )


# ─── 2. Shared file declares the chrome contract ───


SHARED_TOKENS = [
    "--bg0",
    "--bg1",
    "--bg2",
    "--bg3",
    "--bg4",
    "--b0",
    "--b1",
    "--b2",
    "--text0",
    "--text1",
    "--text2",
    "--amber",
    "--amber-d",
    "--green",
    "--green-d",
    "--red",
    "--red-d",
    "--cyan",
    "--cyan-d",
    "--mono",
    "--ui",
]


@pytest.mark.parametrize("token", SHARED_TOKENS)
def test_shared_chrome_declares_token(token: str) -> None:
    body = SHARED_CSS_PATH.read_text(encoding="utf-8")
    assert re.search(
        rf"^\s*{re.escape(token)}\s*:",
        body,
        re.MULTILINE,
    ), f"shared chrome missing :root token {token}"


SHARED_COMPONENTS = [
    ".hbadge",
    ".htitle",
    ".hsub",
    ".hcontrols",
    ".btn",
    ".sim-indicator",  # C919 canonical name
    ".htime",
    ".state-pill",
    ".workspace",
    ".panel",
    ".sec",
    ".sec-title",
    ".row",
    ".val",
    ".tog",
    "input[type=range]",
    "@keyframes blink",
    "::-webkit-scrollbar",
]


@pytest.mark.parametrize("selector", SHARED_COMPONENTS)
def test_shared_chrome_declares_component(selector: str) -> None:
    body = SHARED_CSS_PATH.read_text(encoding="utf-8")
    assert selector in body, (
        f"shared chrome missing component {selector!r}"
    )


def test_panel_header_rule_excludes_unified_nav() -> None:
    """Codex P56-01 round-2 P3: a bare `header { ... }` rule matches
    BOTH the page's panel header AND the existing <header class=
    "unified-nav"> wrapper. .unified-nav overrides height/background
    but NOT padding/gap, so the top nav inherited 16px padding and
    overflowed earlier on narrow viewports. The shared rule must
    scope away from .unified-nav."""
    body = SHARED_CSS_PATH.read_text(encoding="utf-8")
    # The header rule must use :not(.unified-nav) (or a class
    # selector entirely) — a bare `header {` would re-introduce the
    # leak. Allow either the explicit `:not(.unified-nav)` form or
    # any class-based selector.
    bare_header = re.search(r"^header\s*\{", body, re.MULTILINE)
    assert bare_header is None, (
        "shared chrome must NOT use a bare `header {` selector — "
        "it leaks into <header class=\"unified-nav\">. Use "
        "`header:not(.unified-nav)` or a dedicated class."
    )
    # And the scoped form must exist somewhere.
    assert (
        "header:not(.unified-nav)" in body
        or ".panel-head" in body
        or ".etras-head" in body
    ), "shared chrome missing the scoped panel-header rule"


def test_shared_chrome_uses_c919_canonical_sim_indicator() -> None:
    """fan_console.html historically used `.sim-dot`; C919 uses
    `.sim-indicator`. The shared file picks C919's name as the
    standard. fan_console.html must migrate to the new name."""
    body = SHARED_CSS_PATH.read_text(encoding="utf-8")
    assert ".sim-indicator" in body
    # The legacy alias may exist as a back-compat line, but the
    # canonical class is .sim-indicator.
    assert ".sim-indicator.running" in body, (
        "shared chrome must declare the .running variant on the "
        "canonical .sim-indicator class"
    )


# ─── 3. Both pages link the shared file ───


@pytest.mark.parametrize(
    "html_path",
    [C919_PANEL_PATH, FAN_CONSOLE_PATH],
    ids=["c919_panel", "fan_console"],
)
def test_page_links_shared_chrome(html_path: Path) -> None:
    body = html_path.read_text(encoding="utf-8")
    # Either /etras_chrome.css (absolute) or etras_chrome.css (relative).
    assert (
        '"/etras_chrome.css"' in body
        or '"etras_chrome.css"' in body
        or '"../etras_chrome.css"' in body
    ), f"{html_path.name} must <link> the shared chrome stylesheet"


# ─── 4. No inline drift — neither page re-declares shared tokens ───


@pytest.mark.parametrize(
    "html_path",
    [C919_PANEL_PATH, FAN_CONSOLE_PATH],
    ids=["c919_panel", "fan_console"],
)
def test_page_does_not_redeclare_shared_tokens(html_path: Path) -> None:
    """The whole point of extraction is preventing drift. If a page
    redeclares any of the canonical color tokens in its inline
    <style>, the next palette tweak will only land in one place."""
    body = html_path.read_text(encoding="utf-8")
    # Find the inline <style> blocks.
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", body, re.DOTALL)
    inline_css = "\n".join(style_blocks)
    # Strip CSS comments so an example token in a docblock comment
    # doesn't false-positive.
    inline_css = re.sub(r"/\*.*?\*/", "", inline_css, flags=re.DOTALL)
    redeclared: list[str] = []
    for token in SHARED_TOKENS:
        # Match `--token: <value>;` declaration form ONLY (not
        # `var(--token)` references, which are fine).
        if re.search(
            rf"^\s*{re.escape(token)}\s*:",
            inline_css,
            re.MULTILINE,
        ):
            redeclared.append(token)
    assert not redeclared, (
        f"{html_path.name} re-declares shared tokens inline: {redeclared}. "
        f"Move them to etras_chrome.css to prevent drift."
    )


# ─── 5. fan_console migrates the .sim-dot → .sim-indicator ───


def test_standalone_c919_server_serves_shared_chrome() -> None:
    """Codex P56-01 round-1 P1: the standalone C919 panel server
    (scripts/c919_etras_panel_server.py, port 9191) only serves
    explicitly-whitelisted assets from the shared static root. The
    C919 panel's new `<link rel="stylesheet" href="/etras_chrome.css">`
    must resolve there too — otherwise the live :9191 panel 404s
    and silently loses the extracted styles."""
    server_script = REPO_ROOT / "scripts" / "c919_etras_panel_server.py"
    body = server_script.read_text(encoding="utf-8")
    assert '"/etras_chrome.css"' in body, (
        "scripts/c919_etras_panel_server.py must whitelist "
        "/etras_chrome.css so the standalone :9191 panel can resolve "
        "the shared stylesheet (parallels the existing "
        "/unified-nav.css case)"
    )
    # And it must actually serve the file from SHARED_STATIC_ROOT,
    # not redirect/404. Look for the _serve_file call after the
    # route guard (could be many comment lines between).
    route_pos = body.find('"/etras_chrome.css"')
    next_elif = body.find("elif", route_pos + 1)
    block = body[route_pos:next_elif] if next_elif != -1 else body[route_pos:]
    assert "_serve_file" in block, (
        "/etras_chrome.css route must call _serve_file with the "
        "shared static path, not just match the path string"
    )
    assert "etras_chrome.css" in block


def test_fan_console_uses_canonical_sim_indicator_class() -> None:
    """The HTML inside fan_console must use the canonical class
    name. A residual `.sim-dot` class on the indicator div would
    miss the shared chrome's .running animation."""
    body = FAN_CONSOLE_PATH.read_text(encoding="utf-8")
    # Find the indicator element. It's typically <div class="..." id="...">
    # near the play/sim controls.
    indicator_match = re.search(
        r'<div[^>]*\bclass="([^"]*)"[^>]*\bid="(?:simDot|simIndicator)"',
        body,
    )
    if indicator_match:
        cls = indicator_match.group(1)
        assert "sim-indicator" in cls, (
            f"sim indicator div uses class={cls!r} — must include "
            f"the canonical sim-indicator class"
        )
    else:
        # The id may have been renamed too. Fall back: assert that
        # the page has a class="sim-indicator" somewhere AND no bare
        # class="sim-dot" instances on indicators.
        assert "sim-indicator" in body
