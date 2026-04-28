"""P55-01 — LCH 3-token theme foundation.

Linear's redesign collapsed 98 variables down to 3 semantic tokens
(base / accent / contrast). We adopt the same spine: `--base` is
the canvas bg, `--accent` is the ONE highlight color (reserved for
"currently affected gate"), `--contrast` is the primary fg. All
neutrals + accent washes derive from those three via `color-mix(in
lch, ...)`, which is perceptually-uniform and theme-stable.

This phase:
  1. Declares the 3 root tokens at workbench.css :root
  2. Adds derived tokens (surface-1/2, hairline, text-muted, ...)
  3. Migrates the most common ad-hoc rgba/hex literals to the tokens:
       rgba(103, 232, 249, X)  →  color-mix(--accent X%, transparent)
       #67e8f9                 →  var(--accent)
       rgba(255, 255, 255, X)  →  color-mix(--contrast X%, transparent)
  4. Keeps legacy --wb-* / --workbench-* aliases (rules referencing
     them still work; they're now derived from the 3 roots)

Future phases migrate the remaining semantic colors (severity reds /
greens / ambers / SVG fill tints) — those are intentionally NOT
folded into the 3-token foundation since they carry distinct
semantic meaning.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(
    encoding="utf-8"
)


# ─── 1. The three semantic tokens are declared at :root ───────


@pytest.mark.parametrize("token", ["--base", "--accent", "--contrast"])
def test_root_declares_three_semantic_tokens(token: str) -> None:
    """workbench.css :root must declare the 3 canonical tokens.
    Changing these three values is the only knob needed to retheme
    the workbench end-to-end."""
    # Find the first :root rule and verify the token is inside.
    root_rule = re.search(r":root\s*\{(.*?)\n\}", CSS, re.DOTALL)
    assert root_rule is not None, "no :root rule found in workbench.css"
    body = root_rule.group(1)
    assert re.search(rf"^\s*{re.escape(token)}\s*:", body, re.MULTILINE), (
        f"missing root declaration: {token}"
    )


# ─── 2. Derived tokens use color-mix(in lch, ...) ─────────────


@pytest.mark.parametrize(
    "derived_token",
    [
        "--surface-1",
        "--surface-2",
        "--hairline",
        "--text-muted",
        "--accent-tint-12",
        "--accent-tint-28",
    ],
)
def test_derived_tokens_use_lch_color_mix(derived_token: str) -> None:
    """The point of LCH is perceptual uniformity — neutral
    derivations and accent washes must use color-mix(in lch, ...)
    so future theme changes propagate predictably. A hex/rgba
    constant would be a regression."""
    pattern = re.compile(
        rf"{re.escape(derived_token)}\s*:\s*color-mix\(\s*in\s+lch,",
    )
    assert pattern.search(CSS), (
        f"{derived_token} must derive via color-mix(in lch, ...)"
    )


# ─── 3. Legacy aliases still resolve ──────────────────────────


@pytest.mark.parametrize(
    "legacy_alias",
    [
        "--wb-hairline",
        "--wb-active-fill",
        "--wb-active-border",
        "--wb-dock-bg",
        "--wb-drawer-bg",
        "--bg-card",
        "--bg-card-hover",
    ],
)
def test_legacy_aliases_preserved_for_backwards_compat(legacy_alias: str) -> None:
    """Pre-P55-01 rules across the 4900-line stylesheet reference
    these names. They stay declared (each one derived from the 3
    roots) so no rule needs to migrate in lockstep."""
    assert re.search(
        rf"^\s*{re.escape(legacy_alias)}\s*:",
        CSS,
        re.MULTILINE,
    ), f"legacy alias {legacy_alias} must remain declared"


# ─── 4. The big literal migration ─────────────────────────────


def test_no_remaining_cyan_rgba_literals() -> None:
    """The accent color #67e8f9 / rgba(103, 232, 249, X) was the
    most-ad-hoc-repeated literal in the codebase. Every occurrence
    must now route through var(--accent) or an --accent-tint-* /
    color-mix expression — otherwise a future accent swap would
    miss them."""
    assert "rgba(103, 232, 249" not in CSS, (
        "raw cyan rgba literal still present; must use --accent token"
    )
    assert "#67e8f9" not in CSS, (
        "raw cyan hex still present; must use var(--accent)"
    )


def test_no_remaining_white_rgba_literals() -> None:
    """rgba(255, 255, 255, X) was the second-most-common — used
    for hairlines, surface tints, faint borders. Migrated to
    color-mix(in lch, var(--contrast) X%, transparent)."""
    assert "rgba(255, 255, 255" not in CSS, (
        "raw white rgba still present; must derive from --contrast"
    )


# ─── 5. Single-accent discipline ──────────────────────────────


def test_accent_token_used_throughout() -> None:
    """Sanity: the post-migration file must reference var(--accent)
    enough times that the migration isn't just removing the
    literals — they must be replaced with the token."""
    accent_uses = len(re.findall(r"var\(--accent[\s,)]", CSS))
    accent_tint_uses = len(re.findall(r"var\(--accent-tint", CSS))
    assert accent_uses + accent_tint_uses >= 30, (
        f"expected ≥30 var(--accent*) uses after migration, "
        f"got {accent_uses} + {accent_tint_uses} tinted"
    )


def test_no_double_wrapped_accent_fallback() -> None:
    """A textual replace of #67e8f9 → var(--accent) inside an
    existing var(--accent, #67e8f9) fallback would have produced
    var(--accent, var(--accent)). Sanity-check that's been cleaned."""
    assert "var(--accent, var(--accent))" not in CSS


# ─── 6. Browser-support note (informational only) ─────────────


def test_color_mix_is_used_extensively() -> None:
    """All major browsers shipped lch() + color-mix() by early
    2023; we rely on them without fallback. Count uses to confirm
    the migration actually adopted the new syntax rather than
    leaving everything as flat hex/rgba."""
    color_mix_count = CSS.count("color-mix(in lch")
    assert color_mix_count >= 15, (
        f"expected substantial color-mix(in lch) usage; got "
        f"{color_mix_count}"
    )
