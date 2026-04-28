"""P56-05 — fix the time-series chart drawer overlapping the sim panel.

User report (2026-04-28): "时序图会遮挡仿真面板的部分区域，这是布局的问题，
需要优化."

Root cause: both c919_etras_panel/index.html and fan_console.html
declare `.tsc-drawer.open { max-height: 320px; overflow: visible; }`.
The drawer's content (head ~24px + chart-svg 240px + legend ~30px +
inner padding 18px + gaps ~12px ≈ 324px) is taller than 320px, and
`overflow: visible` lets the surplus spill out. Combined with the
dropdown panel inside the drawer head being `position: absolute` +
`top: calc(100% + 3px)` (opens DOWNWARD into the chart area), the
visible overflow can paint over the surrounding workspace.

Fix:
  1. drawer's open state uses `overflow: hidden` so content is
     strictly contained — no spillover regardless of viewport
  2. max-height reduced (320 → 280) so the drawer claims less of
     the available vertical space when iframed (workbench iframe
     is height-constrained; 320px was eating most of the visible
     workspace area)
  3. SVG height reduced 240 → 200 (markup AND `TimeseriesChart.create`
     runtime config — the JS overwrites SVG attributes, so both must
     agree) so the contained content fits within 280px max-height
  4. tsc-selector-panel dropdown opens DOWNWARD (`top: calc(100% +
     3px); bottom: auto`) so it stays INSIDE the drawer's clipped
     region (Codex R1 caught: opening upward inside `overflow:hidden`
     would clip the dropdown at the drawer's top edge, making it
     unreachable). Brief overlap with the chart while the dropdown
     is open is acceptable; the chart re-emerges on close.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"


SIM_PAGES = [
    STATIC / "c919_etras_panel" / "index.html",
    STATIC / "fan_console.html",
]


def _inline_css(html: str) -> str:
    blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL)
    return "\n".join(blocks)


# ─── 1. Drawer's open state uses overflow: hidden ───


@pytest.mark.parametrize(
    "page", SIM_PAGES, ids=lambda p: p.name,
)
def test_drawer_open_state_clips_overflow(page: Path) -> None:
    """`.tsc-drawer.open { overflow: visible }` is the bug — it
    lets content paint outside the 320px box. Switch to
    `overflow: hidden` so the drawer is a strict container."""
    body = page.read_text(encoding="utf-8")
    css = _inline_css(body)
    rule = re.search(
        r"\.tsc-drawer\.open\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    assert rule is not None, f"{page.name}: no .tsc-drawer.open rule found"
    body_props = rule.group(1)
    assert "overflow:visible" not in body_props.replace(" ", ""), (
        f"{page.name}: .tsc-drawer.open declares overflow: visible — "
        f"that's what lets the chart spill into the workspace. Use "
        f"overflow: hidden to keep content contained."
    )
    assert "overflow: hidden" in body_props or "overflow:hidden" in body_props, (
        f"{page.name}: .tsc-drawer.open must declare overflow: hidden"
    )


# ─── 2. Max-height reduced to make room when iframed ───


@pytest.mark.parametrize(
    "page", SIM_PAGES, ids=lambda p: p.name,
)
def test_drawer_max_height_fits_iframed_workspace(page: Path) -> None:
    """When the panel is iframed inside the workbench, available
    vertical space is constrained. 320px max-height eats most of
    the visible workspace; 280px leaves more breathing room while
    still showing the chart legibly."""
    body = page.read_text(encoding="utf-8")
    css = _inline_css(body)
    rule = re.search(
        r"\.tsc-drawer\.open\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    assert rule is not None
    height_match = re.search(r"max-height\s*:\s*(\d+)px", rule.group(1))
    assert height_match is not None, (
        f"{page.name}: .tsc-drawer.open must declare a numeric max-height"
    )
    h = int(height_match.group(1))
    assert h <= 280, (
        f"{page.name}: drawer max-height={h}px is too tall — eats "
        f"workspace when iframed. Reduce to 280 or less."
    )


# ─── 3. Chart SVG height fits within the new max-height budget ───


@pytest.mark.parametrize(
    "page", SIM_PAGES, ids=lambda p: p.name,
)
def test_tsc_svg_height_fits_drawer(page: Path) -> None:
    """SVG was 240px tall — combined with head + legend + paddings
    that exceeds 280px (post-fix max-height). Reduce to 200 so the
    drawer's contained content fits without clipping itself."""
    body = page.read_text(encoding="utf-8")
    svg_match = re.search(
        r'<svg\s+id="tsc-svg"[^>]*\bheight="(\d+)"',
        body,
    )
    if svg_match is None:
        # SVG height may be set via viewBox or attribute order; fall
        # back to checking the viewBox second pair.
        vb_match = re.search(
            r'<svg\s+id="tsc-svg"[^>]*\bviewBox="0 0 \d+ (\d+)"',
            body,
        )
        assert vb_match is not None, (
            f"{page.name}: cannot find tsc-svg height/viewBox"
        )
        h = int(vb_match.group(1))
    else:
        h = int(svg_match.group(1))
    assert h <= 200, (
        f"{page.name}: tsc-svg height={h}px doesn't fit the new "
        f"280px drawer budget (head ~24 + svg + legend ~30 + "
        f"paddings 18 + gaps 12 must total ≤ 280). Reduce to ≤ 200."
    )


# ─── 4. Selector dropdown opens downward, contained by drawer's hidden overflow ───
#
# Codex R1 (2026-04-28) flagged: opening upward inside a clipped drawer
# clips the dropdown at the drawer's top edge — worse than downward.
# With overflow: hidden on the drawer, downward keeps the dropdown
# inside the drawer body (briefly covering chart area while open),
# which is contained and reachable.


@pytest.mark.parametrize(
    "page", SIM_PAGES, ids=lambda p: p.name,
)
def test_tsc_selector_panel_opens_downward(page: Path) -> None:
    """`.tsc-selector-panel` must use `top: calc(100% + ...)` so the
    dropdown opens downward, INSIDE the clipped drawer. Opening
    upward would be clipped by `.tsc-drawer.open { overflow: hidden }`
    at the drawer's top edge (Codex R1 flagged this regression)."""
    body = page.read_text(encoding="utf-8")
    css = _inline_css(body)
    rule = re.search(
        r"\.tsc-selector-panel\s*\{([^}]+)\}",
        css,
        re.DOTALL,
    )
    if rule is None:
        return
    rule_body = rule.group(1)
    top_match = re.search(r"top\s*:\s*([^;}]+)", rule_body)
    assert top_match is not None, (
        f"{page.name}: .tsc-selector-panel must declare a `top` "
        f"property so the dropdown opens downward (contained inside "
        f"the drawer's overflow:hidden box)."
    )
    top_val = top_match.group(1).strip()
    assert top_val.startswith("calc"), (
        f"{page.name}: .tsc-selector-panel `top: {top_val}` — must "
        f"open downward via `top: calc(100% + ...)`. Opening upward "
        f"gets clipped by the drawer's overflow:hidden top edge."
    )
    # And `bottom:` must NOT be set to a positive value (auto is OK).
    bottom_match = re.search(r"bottom\s*:\s*([^;}]+)", rule_body)
    if bottom_match is not None:
        bottom_val = bottom_match.group(1).strip()
        assert bottom_val == "auto" or bottom_val.startswith("auto"), (
            f"{page.name}: .tsc-selector-panel still has `bottom: "
            f"{bottom_val}` — that flips it upward into the clipped "
            f"region. Use `bottom: auto` or omit `bottom` entirely."
        )


# ─── 5. JS ensureChart() height matches the static SVG markup ───
#
# Codex R1 (2026-04-28) flagged: `TimeseriesChart.create({...height:240})`
# overwrites the live SVG's height attribute at runtime, so the static
# height="200" in the markup gets reverted on first render. The runtime
# config MUST agree with the static SVG.


@pytest.mark.parametrize(
    "page", SIM_PAGES, ids=lambda p: p.name,
)
def test_ensure_chart_js_height_matches_svg(page: Path) -> None:
    """`TimeseriesChart.create({ ..., height: N, ... })` runs every
    time the drawer first opens and OVERWRITES the SVG's height
    attribute. If JS still says 240 while the static markup says 200,
    the chart pops back to 240px on first render and the drawer
    budget is blown again. Both must declare the same value (≤ 200)."""
    body = page.read_text(encoding="utf-8")
    # Match `height: 200` or `height:200` inside a TimeseriesChart.create
    # call — both pages use this identical pattern.
    create_match = re.search(
        r"TimeseriesChart\.create\s*\(\s*\{[^}]*?\bheight\s*:\s*(\d+)",
        body,
        re.DOTALL,
    )
    assert create_match is not None, (
        f"{page.name}: cannot find TimeseriesChart.create({{...height:N}}) "
        f"runtime config — the test needs updating to find it."
    )
    h = int(create_match.group(1))
    assert h <= 200, (
        f"{page.name}: TimeseriesChart.create({{...height:{h}}}) — JS "
        f"runtime height must match the static SVG markup (≤ 200). "
        f"Otherwise the chart reverts to {h}px on first open and the "
        f"280px drawer budget is blown."
    )
