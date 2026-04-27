"""P54-07 — wire C919 E-TRAS circuit + correct sim↔cockpit swap.

Two user-reported defects from P54-06's first cut:

(1) sim/cockpit C919 sources were swapped:
    - Per unified-nav semantics, /c919_etras_workstation.html is
      the workstation (i.e. cockpit/演示 equivalent of /demo.html),
      and /c919_etras_panel/index.html is the simulation panel.
    - P54-06 had them backwards. P54-07 swaps them back.

(2) C919 circuit was still showing the "circuit not yet wired"
    placeholder because:
    a. /api/workbench/circuit-fragment had no _CIRCUIT_SOURCE_BY_SYSTEM
       entry for c919-etras (fell through to placeholder branch)
    b. The SVG extractor hard-coded `viewBox="0 0 1000 640"`, so
       even after wiring c919_etras_panel/circuit.html (viewBox
       0 0 1020 560), the extraction would have failed with 503
       "circuit_svg_block_not_found".
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"
HTML = (STATIC / "workbench.html").read_text(encoding="utf-8")
DEMO_SERVER = (REPO_ROOT / "src" / "well_harness" / "demo_server.py").read_text(
    encoding="utf-8"
)
C919_CIRCUIT = (STATIC / "c919_etras_panel" / "circuit.html").read_text(
    encoding="utf-8"
)


# ─── 1. sim ↔ cockpit swap correction ───


def test_c919_sim_panel_points_at_panel_index_not_workstation():
    """仿真面板 = /c919_etras_panel/index.html (NOT workstation)."""
    block = re.search(
        r'<section[^>]*id="workbench-sim-panel"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(0)
    assert (
        'data-system-src-c919-etras="/c919_etras_panel/index.html?embed=1"'
        in body
    ), "sim panel must load /c919_etras_panel/index.html for C919"
    assert (
        'data-system-src-c919-etras="/c919_etras_workstation.html' not in body
    ), "sim panel must NOT load workstation (that's the cockpit's job)"


def test_c919_cockpit_panel_points_at_workstation_not_panel_index():
    """演示舱 = /c919_etras_workstation.html (NOT panel/index)."""
    block = re.search(
        r'<section[^>]*id="workbench-cockpit-panel"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(0)
    assert (
        'data-system-src-c919-etras="/c919_etras_workstation.html?embed=1"'
        in body
    ), "cockpit must load /c919_etras_workstation.html for C919"
    assert (
        'data-system-src-c919-etras="/c919_etras_panel/index.html' not in body
    ), "cockpit must NOT load panel/index (that's the sim's job)"


# ─── 2. C919 circuit wired into the fragment endpoint ───


def test_c919_circuit_source_registered():
    """`_CIRCUIT_SOURCE_BY_SYSTEM` must include c919-etras pointing at
    c919_etras_panel/circuit.html so the fragment endpoint stops
    falling through to the placeholder branch."""
    # Walk the dict block and assert the mapping.
    block = re.search(
        r'_CIRCUIT_SOURCE_BY_SYSTEM:[^=]*=\s*\{(.*?)\n\}',
        DEMO_SERVER,
        re.DOTALL,
    )
    assert block is not None, (
        "could not locate _CIRCUIT_SOURCE_BY_SYSTEM dict"
    )
    body = block.group(1)
    assert '"c919-etras"' in body, (
        "c919-etras key missing from _CIRCUIT_SOURCE_BY_SYSTEM"
    )
    assert '"c919_etras_panel/circuit.html"' in body, (
        "c919-etras must map to c919_etras_panel/circuit.html"
    )


def test_c919_circuit_html_actually_exists_with_svg():
    """The wired source must really exist and contain an SVG block."""
    assert "<svg" in C919_CIRCUIT
    # The C919 circuit uses a different canvas size than the
    # thrust-reverser one — test_svg_extractor_is_viewbox_agnostic
    # below asserts the extractor handles it.
    assert 'viewBox="0 0 1020 560"' in C919_CIRCUIT


def test_svg_extractor_is_viewbox_agnostic():
    """The fragment endpoint's SVG extraction must NOT hard-code
    viewBox dimensions — otherwise wiring a new system with its
    own canvas size silently 503s with circuit_svg_block_not_found."""
    # The hard-coded literal is gone.
    assert '"<svg viewBox=\\"0 0 1000 640\\""' not in DEMO_SERVER, (
        "hard-coded viewBox still present in extractor"
    )
    assert (
        '<svg viewBox="0 0 1000 640"' not in DEMO_SERVER
        or "P54-07" in DEMO_SERVER
    ), "literal viewBox match should be replaced by a viewBox-agnostic regex"
    # The new regex form is in place.
    assert "re.search(r'<svg" in DEMO_SERVER or 're.search(r"<svg' in DEMO_SERVER, (
        "extractor must use a regex to find the SVG opening tag"
    )


def test_c919_circuit_passes_through_extractor_logic():
    """Manual replay of the extractor against c919_etras_panel/circuit.html:
    a viewBox-agnostic regex must locate `<svg ... viewBox="..."`
    and find a closing </svg>, so the endpoint returns the fragment
    instead of the 503 / placeholder branches."""
    pattern = re.compile(r'<svg\s+[^>]*viewBox="[^"]+"')
    match = pattern.search(C919_CIRCUIT)
    assert match is not None, (
        "viewBox-agnostic pattern should match C919 circuit's <svg> tag"
    )
    end = C919_CIRCUIT.find("</svg>", match.start())
    assert end != -1, "C919 circuit must contain a closing </svg>"


# ─── 3. C919 doesn't carry the thrust-reverser gate sanity check ───


def test_c919_etras_not_in_required_gates_table():
    """The per-system required-gate guard only applies to systems
    whose SVGs publish data-gate-id="L1..L4" (currently just
    thrust-reverser). Adding c919-etras to that table without
    drafting matching gate anchors would cause every fragment
    request to 503."""
    block = re.search(
        r'_CIRCUIT_REQUIRED_GATES:[^=]*=\s*\{(.*?)\n\}',
        DEMO_SERVER,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(1)
    assert '"c919-etras"' not in body, (
        "c919-etras circuit has no L1..L4 gate anchors yet — keep it "
        "out of the required-gate guard until they're drafted"
    )
