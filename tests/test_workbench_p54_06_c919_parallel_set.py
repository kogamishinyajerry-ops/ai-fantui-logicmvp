"""P54-06 — extend the system toggle to the full 4-piece set.

Before this phase, only the circuit view honored the 反推/C919
toggle; sim/cockpit/spec were hard-pointed at thrust-reverser
pages, so switching to C919 silently left 3 of the 4 surfaces
showing the wrong system. P54-06 promotes the toggle to canvas-
level (always visible, top-right of viewport) and re-points all
4 surfaces in lockstep.

Mapping:
    | view    | thrust-reverser src         | c919-etras src                  |
    |---------|-----------------------------|---------------------------------|
    | sim     | /fan_console.html?embed=1   | /c919_etras_workstation.html    |
    | cockpit | /demo.html?embed=1          | /c919_etras_panel/index.html    |
    | spec    | /workbench_spec.html        | /c919_requirements.html?embed=1 |

The circuit view continues to swap via the legacy
#workbench-system-select dropdown (unchanged from P54-04).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"
HTML = (STATIC / "workbench.html").read_text(encoding="utf-8")
CSS = (STATIC / "workbench.css").read_text(encoding="utf-8")
JS = (STATIC / "workbench.js").read_text(encoding="utf-8")


# ─── 1. toggle promoted to canvas-level (not nested inside circuit hero) ──


def test_toggle_lives_at_canvas_level_not_inside_circuit_hero():
    """The toggle markup must NOT be nested inside #workbench-circuit-hero
    anymore — it has to drive all 4 views, so it lives at canvas level."""
    hero_block = re.search(
        r'<section[^>]*id="workbench-circuit-hero"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert hero_block is not None
    assert "workbench-system-toggle" not in hero_block.group(0), (
        "P54-06: toggle must be lifted out of #workbench-circuit-hero"
    )
    assert 'id="workbench-system-toggle"' in HTML, (
        "P54-06: canvas-level #workbench-system-toggle must exist"
    )


def test_toggle_pinned_top_right_via_fixed_or_absolute():
    """The promoted toggle has to be pinned (position: fixed/absolute)
    in the top-right so it stays visible regardless of which view is
    active and survives canvas scroll."""
    rule = re.search(
        r'\.workbench-system-toggle\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, "missing .workbench-system-toggle rule"
    body = rule.group(0)
    assert "position:" in body and ("fixed" in body or "absolute" in body), (
        f"toggle must be position:fixed or :absolute — got: {body!r}"
    )
    assert "right:" in body, "toggle must anchor to the right edge"
    assert "top:" in body, "toggle must anchor to the top edge"


# ─── 2. all 3 iframe views carry the system-aware src attributes ──


@pytest.mark.parametrize(
    "panel_id,view_key,thrust_src,c919_src",
    [
        (
            "workbench-sim-panel",
            "sim",
            "/fan_console.html?embed=1",
            "/c919_etras_workstation.html?embed=1",
        ),
        (
            "workbench-cockpit-panel",
            "cockpit",
            "/demo.html?embed=1",
            "/c919_etras_panel/index.html?embed=1",
        ),
        (
            "workbench-spec-panel",
            "spec",
            "/workbench_spec.html",
            "/c919_requirements.html?embed=1",
        ),
    ],
)
def test_iframe_carries_system_src_attributes(
    panel_id, view_key, thrust_src, c919_src
):
    block = re.search(
        r'<section[^>]*id="' + re.escape(panel_id) + r'"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(0)
    assert f'data-system-iframe="{view_key}"' in body, (
        f"#{panel_id} iframe missing data-system-iframe=\"{view_key}\""
    )
    assert f'data-system-src-thrust-reverser="{thrust_src}"' in body, (
        f"#{panel_id} iframe missing thrust-reverser src ({thrust_src})"
    )
    assert f'data-system-src-c919-etras="{c919_src}"' in body, (
        f"#{panel_id} iframe missing c919-etras src ({c919_src})"
    )


# ─── 3. C919 pages hide unified-nav under iframe-embed ──


@pytest.mark.parametrize(
    "page_path",
    [
        "src/well_harness/static/c919_etras_workstation.html",
        "src/well_harness/static/c919_etras_panel/index.html",
        "src/well_harness/static/c919_requirements.html",
    ],
)
def test_c919_page_hides_nav_when_iframed(page_path):
    """Each C919 page that can be iframed must include the same
    nav-hide guard the legacy thrust-reverser pages use, so the
    workbench canvas doesn't expose a second navigation bar."""
    html = (REPO_ROOT / page_path).read_text(encoding="utf-8")
    assert "window.self !== window.top" in html and "is-iframe-embed" in html, (
        f"{page_path} missing iframe-embed detection script"
    )
    assert (
        "html.is-iframe-embed .unified-nav" in html
        or ".is-iframe-embed .unified-nav" in html
    ), (
        f"{page_path} missing CSS rule that hides .unified-nav under "
        f".is-iframe-embed"
    )


# ─── 4. JS performs iframe src swap on toggle click ──


def test_js_swaps_iframe_src_on_system_change():
    """On toggle click the boot block must read the per-iframe
    `data-system-src-{system}` attribute and re-point the iframe
    src — otherwise sim/cockpit/spec stay frozen on whichever
    system was loaded at boot."""
    assert "data-system-iframe" in JS, (
        "JS must query for [data-system-iframe] iframes to swap srcs"
    )
    assert (
        'data-system-src-' in JS
        or '"data-system-src-"' in JS
    ), "JS must read the data-system-src-{system} attribute"
    # The boot block name is preserved from P54-04 for traceability.
    assert "_wbCircuitSystemToggleBoot" in JS
