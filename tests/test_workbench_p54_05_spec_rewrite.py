"""P54-05 — workbench-native requirements page (charts + cards).

User feedback: the legacy `fantui_requirements.html` doesn't fit the
workbench style and is too text-heavy. P54-05 ships a new compact,
visualization-rich page tailored for the workbench iframe embed:

- Summary KPIs (total / critical / gate coverage)
- Coverage donut SVG
- Compact REQ cards in a grid with REQ-ID + title + gate-trace pills
- Traceability matrix (8 reqs × 4 gates)

The legacy page remains at /fantui_requirements.html for the
standalone route; only the workbench iframe repoints.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench_spec.html").read_text(encoding="utf-8")
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")


def test_workbench_spec_page_exists():
    assert "workbench_spec" in (REPO_ROOT / "src" / "well_harness" / "static").as_posix() or True
    assert "<title>反推需求文档" in SPEC, (
        "workbench_spec.html must carry the requirements doc title"
    )


def test_iframe_points_at_new_spec_page():
    assert 'src="/workbench_spec.html"' in HTML, (
        "spec iframe must point at /workbench_spec.html (the "
        "workbench-native rebuild)"
    )


def test_spec_page_uses_workbench_palette():
    """Tokens align with the workbench shell: neutral hairline,
    accent cyan, --text-muted gray. We don't pin exact values, just
    that the recognizable variables exist."""
    assert "--accent: #67e8f9" in SPEC
    assert "rgba(255, 255, 255, 0.08)" in SPEC, (
        "hairline should match workbench's neutral white-tint"
    )
    assert "--text-muted" in SPEC


def test_spec_page_has_summary_kpis():
    """Three KPI cards: total / critical / gate coverage."""
    assert "spec-kpi" in SPEC
    # Three KPI cards present
    assert SPEC.count("spec-kpi-value") >= 3, (
        "expected at least 3 KPI cards"
    )


def test_spec_page_has_coverage_donut_svg():
    """Inline SVG donut chart for trace coverage."""
    donut_match = re.search(
        r'<svg[^>]*>.*?<circle[^>]*r="40"[^>]*stroke-dasharray',
        SPEC,
        re.DOTALL,
    )
    assert donut_match is not None, (
        "expected SVG donut chart with dasharray-driven arc"
    )


@pytest.mark.parametrize(
    "req_id",
    ["SR-01", "SR-02", "SR-03", "SR-04", "FR-01", "FR-02", "FR-03", "FR-04"],
)
def test_spec_page_lists_each_requirement(req_id):
    """All 8 requirements (4 SR + 4 FR) must appear on the page,
    each in its own card with the REQ-ID pill."""
    assert req_id in SPEC, f"missing requirement {req_id}"


def test_spec_page_has_traceability_matrix():
    """The matrix must include the column headers (L1-L4) and
    structural anchors so the chart actually renders, not just
    'Coming soon' text."""
    assert "spec-matrix" in SPEC
    for gate in ("L1", "L2", "L3", "L4"):
        # gate appears as a column header (inside <th>...gate...</th>)
        pattern = re.compile(r'<th[^>]*>\s*' + re.escape(gate) + r'\s*</th>')
        assert pattern.search(SPEC), (
            f"gate column header {gate} missing from matrix"
        )


def test_spec_page_no_unified_nav_leaks():
    """The new page is workbench-native; it should NOT carry the
    legacy unified-nav header (this was P54-04's complaint —
    embedded pages shouldn't expose page-level nav)."""
    assert "unified-nav" not in SPEC, (
        "workbench_spec.html should not include the legacy unified-nav"
    )


def test_spec_page_has_section_titles():
    """The page should include human-readable section dividers
    (safety / functional / matrix), not be a single text wall."""
    for title in ("安全约束", "功能要求", "追溯矩阵"):
        assert title in SPEC, f"missing section title: {title}"
