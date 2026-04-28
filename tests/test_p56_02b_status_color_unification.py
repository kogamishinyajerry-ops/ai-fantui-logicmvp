"""P56-02b — unify the 4 status indicator colors across all E-TRAS surfaces.

After P56-02a (structural linking + chrome scoping), the 4 surfaces
share /etras_chrome.css but the color values for status indicators
(accent / active / warn / fail) still drift between sim and cockpit:

  Surface                | accent      | active      | warn        | fail
  --- | --- | --- | --- | ---
  sim chrome (P56-01)    | #22d3ee     | #4ade80     | #f5a623     | #f87171
  cockpit demo.css       | #00c8f5     | #00e5a0     | #f5c518     | #e05555
  cockpit c919.css       | #00c8f5     | #00e5a0     | #f5c518     | #e05555

P56-02b picks the cockpit palette as the unified standard:

  - More authentic to the avionics domain (#00e5a0 OK indicator,
    #f5c518 warn yellow, #e05555 fail are classic cockpit colors)
  - Two surfaces already use it (cockpits) — flipping one (sim
    panels) is a smaller blast radius
  - User direction "都以 C919 ETRAS 为标准" — and the cockpits are
    the more "production"-feeling C919 ETRAS surfaces

Implementation:
  - etras_chrome.css :root --cyan/--green/--amber/--red (+ -d
    transparent variants) get the cockpit values
  - demo.css aliases --fan-accent/active/warn/fail → var(--cyan/
    --green/--amber/--red); same for c919_etras_workstation.css's
    --etras-* equivalents
  - Cockpit visuals unchanged (same value, new source)
  - Sim panel visuals shift on the 4 status colors (intentional)

Background/text tokens stay distinct on each surface — disturbing
those would change layout legibility without semantic benefit.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"


# ─── 1. Shared chrome adopts the cockpit status palette ───


@pytest.mark.parametrize(
    ("token", "expected_value"),
    [
        ("--cyan", "#00c8f5"),
        ("--green", "#00e5a0"),
        ("--amber", "#f5c518"),
        ("--red", "#e05555"),
    ],
)
def test_chrome_token_matches_cockpit_palette(
    token: str, expected_value: str,
) -> None:
    """The shared chrome's status-indicator tokens must match the
    cockpit values, not the legacy Tailwind-ish sim values."""
    chrome = (STATIC / "etras_chrome.css").read_text(encoding="utf-8")
    match = re.search(
        rf"^\s*{re.escape(token)}\s*:\s*(#[0-9a-fA-F]+)\s*;",
        chrome,
        re.MULTILINE,
    )
    assert match is not None, f"chrome missing root declaration of {token}"
    actual = match.group(1).lower()
    assert actual == expected_value.lower(), (
        f"{token} = {actual} (expected {expected_value} from cockpit palette)"
    )


@pytest.mark.parametrize(
    ("token", "expected_rgb"),
    [
        ("--cyan-d", "rgba(0, 200, 245"),
        ("--green-d", "rgba(0, 229, 160"),
        ("--amber-d", "rgba(245, 197, 24"),
        ("--red-d", "rgba(224, 85, 85"),
    ],
)
def test_chrome_transparent_variant_matches_cockpit(
    token: str, expected_rgb: str,
) -> None:
    """The -d (transparent) variants must derive from the same RGB
    triple as the new solid tokens. Legacy values were the Tailwind
    rgbs (e.g. rgba(74,222,128, ...) for --green-d); they must
    update too so e.g. .btn:hover backgrounds match the new accent."""
    chrome = (STATIC / "etras_chrome.css").read_text(encoding="utf-8")
    match = re.search(
        rf"^\s*{re.escape(token)}\s*:\s*([^;]+);",
        chrome,
        re.MULTILINE,
    )
    assert match is not None
    value = match.group(1).strip()
    # Tolerant prefix match — alpha may differ across variants.
    assert expected_rgb in value, (
        f"{token} = {value!r} — must derive from {expected_rgb}"
    )


# ─── 2. Cockpits alias their local semantic tokens to the shared ones ───


COCKPIT_TOKEN_MAP = {
    # demo.css local → shared
    "--fan-accent": "--cyan",
    "--fan-active": "--green",
    "--fan-warn": "--amber",
    "--fan-fail": "--red",
    # c919_etras_workstation.css local → shared
    "--etras-accent": "--cyan",
    "--etras-active": "--green",
    "--etras-warn": "--amber",
    "--etras-fail": "--red",
}


@pytest.mark.parametrize(
    ("local", "shared"),
    list(COCKPIT_TOKEN_MAP.items())[:4],
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_demo_css_aliases_status_tokens_to_shared(
    local: str, shared: str,
) -> None:
    """demo.css must alias `--fan-accent` etc. to the shared
    `var(--cyan)` so a future palette change at chrome:root
    propagates without touching demo.css."""
    body = (STATIC / "demo.css").read_text(encoding="utf-8")
    # Match `--fan-accent: var(--cyan);` (accept whitespace variations).
    pattern = rf"^\s*{re.escape(local)}\s*:\s*var\(\s*{re.escape(shared)}\s*\)"
    assert re.search(pattern, body, re.MULTILINE), (
        f"demo.css must declare `{local}: var({shared});` so it aliases "
        f"the shared chrome token instead of redeclaring a hex literal"
    )


@pytest.mark.parametrize(
    ("local", "shared"),
    list(COCKPIT_TOKEN_MAP.items())[4:],
    ids=lambda x: x if isinstance(x, str) else "",
)
def test_c919_workstation_css_aliases_status_tokens(
    local: str, shared: str,
) -> None:
    """c919_etras_workstation.css must alias `--etras-accent` etc.
    to the shared `var(--cyan)` for the same propagation reason."""
    body = (STATIC / "c919_etras_workstation.css").read_text(encoding="utf-8")
    pattern = rf"^\s*{re.escape(local)}\s*:\s*var\(\s*{re.escape(shared)}\s*\)"
    assert re.search(pattern, body, re.MULTILINE), (
        f"c919_etras_workstation.css must declare `{local}: var({shared});`"
    )


# ─── 3. No straggler hex literals for the unified colors ───


@pytest.mark.parametrize(
    "css_file",
    ["demo.css", "c919_etras_workstation.css"],
)
def test_cockpit_css_strips_redundant_status_hex_literals(css_file: str) -> None:
    """After aliasing, the legacy `--fan-accent: #00c8f5;` line must
    be REMOVED (replaced with the var() form). A leftover hex
    literal would defeat the unification — any subsequent palette
    tweak in the chrome wouldn't propagate to that file."""
    body = (STATIC / css_file).read_text(encoding="utf-8")
    # Strip CSS comments so explanatory mentions don't false-positive.
    body_no_comments = re.sub(r"/\*.*?\*/", "", body, flags=re.DOTALL)
    # Look for `--fan-accent:` or `--etras-accent:` followed by a
    # hex literal (vs the var() form).
    legacy_hex_lines = re.findall(
        r"^\s*(--(?:fan|etras)-(?:accent|active|warn|fail))\s*:\s*(#[0-9a-fA-F]+)\s*;",
        body_no_comments,
        re.MULTILINE,
    )
    assert not legacy_hex_lines, (
        f"{css_file} retains legacy hex declarations: {legacy_hex_lines}. "
        f"Replace with `var(--cyan)`/`var(--green)`/etc. so the chrome "
        f"palette is the single source of truth."
    )
