"""P52-00 — workbench contrast emergency fix regression.

Lock down the body-background reset so a future PR can't quietly
drop the rule and reintroduce the white-on-white state the user
reported on 2026-04-27. Pure CSS-text assertions (cheap to run,
fast to fail-loud).

What we're guarding:
- `html, body { background: ...; color: ...; }` MUST be in workbench.css
- The bg MUST resolve to the design-tokens dark base (--bg-base)
  rather than browser default white
- The text color MUST resolve to a light token (--text-main) so it's
  legible on the dark base — and conversely, the bg+color pair MUST
  NOT both be light
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"
TOKENS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "design-tokens.css"


def _read_css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def test_body_background_rule_present():
    """Without this rule the browser default (white) shows through
    every gap between the semi-transparent chrome panels and the
    light text becomes invisible. The whole workbench surface
    relies on the rule existing."""
    css = _read_css()
    # Match `html, body {` (with optional whitespace) followed by
    # a rule block that contains `background:` AND `color:`.
    match = re.search(
        r"html\s*,\s*body\s*\{[^}]*background\s*:[^;]+;[^}]*color\s*:[^;]+;[^}]*\}",
        css,
        re.DOTALL,
    )
    assert match is not None, (
        "workbench.css must declare an `html, body { background:…; color:…; }` "
        "rule (P52-00 reintroduced this; see commit log for the white-on-white "
        "incident report)."
    )


def test_body_background_uses_dark_token():
    """The bg MUST be a dark token, not white/transparent. We accept
    --bg-base or any explicit dark-hex, but reject white/#fff/transparent."""
    css = _read_css()
    match = re.search(
        r"html\s*,\s*body\s*\{[^}]*background\s*:\s*([^;]+);",
        css,
        re.DOTALL,
    )
    assert match is not None, "no html,body background rule"
    bg_value = match.group(1).strip().lower()
    forbidden = ("white", "#fff", "#ffffff", "transparent", "rgb(255")
    for f in forbidden:
        assert f not in bg_value, (
            f"workbench body bg resolves to {f!r} — that reproduces "
            f"the original bug. value={bg_value!r}"
        )
    # Must reference the dark base (token preferred; explicit dark hex
    # is also acceptable in case someone inlines).
    is_token = "var(--bg-base)" in bg_value or "var(--bg-surface)" in bg_value
    is_dark_hex = bool(re.match(r"^#[0-2][0-9a-f]", bg_value))
    assert is_token or is_dark_hex, (
        f"workbench body bg must be a dark token or dark hex; got {bg_value!r}"
    )


def test_body_text_color_is_light_token():
    """The text color MUST be light so it's readable on the dark
    base. Combined with the bg check above, this prevents the
    dual-light state that caused the bug."""
    css = _read_css()
    match = re.search(
        r"html\s*,\s*body\s*\{[^}]*color\s*:\s*([^;]+);",
        css,
        re.DOTALL,
    )
    assert match is not None, "no html,body color rule"
    fg_value = match.group(1).strip().lower()
    is_light_token = (
        "var(--text-main)" in fg_value
        or "var(--text-primary)" in fg_value
    )
    is_light_hex = bool(re.match(r"^#[c-fC-F][c-fC-F]", fg_value))
    assert is_light_token or is_light_hex, (
        f"workbench body text color must be a light token or light "
        f"hex; got {fg_value!r}"
    )


def test_design_tokens_bg_base_is_dark():
    """If a future PR changes --bg-base to something light, the body
    rule above silently breaks. Lock the token's value range too."""
    tokens = TOKENS_PATH.read_text(encoding="utf-8")
    match = re.search(r"--bg-base\s*:\s*(#[0-9a-fA-F]+)\s*;", tokens)
    assert match is not None, "design-tokens.css missing --bg-base"
    hex_value = match.group(1).lower()
    # Accept #RGB or #RRGGBB starting with 0/1/2 (= each channel ≤ 0x2F = ~18%
    # luminance, comfortably "dark"). #050914 (R=05) passes.
    assert re.match(r"^#[0-2]", hex_value), (
        f"--bg-base must be a dark color (#0?-#2?...); got {hex_value!r}"
    )
