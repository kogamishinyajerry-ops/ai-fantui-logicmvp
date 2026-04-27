"""P53-00 — pure-circuit canvas (Claude.app-level minimalism).

The user feedback was: the main page should be ONLY the logic
control circuit. Everything else (page title, identity/ticket
chips, system selector, state-of-world advisory bar, truth-engine
readonly link, circuit hero title+eyebrow+sub-paragraph) is chrome
that belongs inside a drawer or hidden entirely until the user
opens a tool from the dock.

This test locks in CSS rules that hide each piece of chrome by
default. The elements stay in the DOM (so tests + JS bindings
keep working), they just don't render in the default canvas state.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


def _chrome_hidden_by_default(selector: str) -> bool:
    """Find any rule that explicitly hides this selector. We accept
    `display: none` or `visibility: hidden` as evidence — Claude.app
    minimalism just needs the chrome to not paint, not to be
    DOM-removed."""
    pattern = re.compile(
        re.escape(selector) + r'\s*\{[^}]*\}',
        re.DOTALL,
    )
    for rule in pattern.findall(CSS):
        if "display: none" in rule or "display:none" in rule:
            return True
        if "visibility: hidden" in rule or "visibility:hidden" in rule:
            return True
    return False


@pytest.mark.parametrize(
    "selector",
    [
        # The whole topbar (h1 + 5 chips + system select) — chrome
        ".workbench-collab-topbar",
        # The advisory state-of-world bar — observability info,
        # belongs inside the monitor drawer or hidden entirely
        ".workbench-state-of-world-bar",
        # The truth-engine read-only chip is policy info, not chrome
        # the engineer needs to read every paint
        ".workbench-truth-engine-chip",
        # The circuit hero's own header (eyebrow + h2 + sub-paragraph)
        # — the SVG itself is the title; the words are noise
        ".workbench-circuit-hero-header",
    ],
)
def test_chrome_hidden_by_default(selector):
    assert _chrome_hidden_by_default(selector), (
        f"P53-00 contract: {selector} must be `display: none` (or "
        f"visibility: hidden) by default. The default canvas is the "
        f"circuit alone — everything else lives in a drawer or is "
        f"hidden entirely."
    )


def test_circuit_hero_fills_canvas():
    """Once the chrome is hidden, the circuit hero must be free
    to fill the available canvas (no longer constrained by a
    half-inch margin from the chrome above it). Search ALL matching
    rules — later overrides count, since cascade winds up using
    them in the live render."""
    rules = re.findall(
        r'\.workbench-circuit-hero(?![\w-])\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rules, ".workbench-circuit-hero rule missing"
    has_fill = False
    for body in rules:
        if (
            "min-height: 100" in body
            or "min-height:100" in body
            or "height: 100" in body
            or "flex: 1" in body
            or "flex:1" in body
            or "min-height: calc" in body
            or "min-height:calc" in body
        ):
            has_fill = True
            break
    assert has_fill, (
        f"circuit hero should fill the canvas now that chrome is "
        f"hidden; matched rules:\n" + "\n---\n".join(r[:300] for r in rules)
    )
