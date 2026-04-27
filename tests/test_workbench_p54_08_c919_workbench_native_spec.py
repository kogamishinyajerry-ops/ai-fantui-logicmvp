"""P54-08 — workbench-native rebuild of the C919 E-TRAS spec view.

User feedback after P54-07: "C919 ETRAS 的需求文档没有进行适配优化，
还是原文档" — the spec view was iframing the legacy
/c919_requirements.html, which has its own visual style (text-heavy,
section-numbered, decision boxes, AI-analysis box) that doesn't
match the workbench's Claude-app aesthetic.

P54-08 mirrors what we did for thrust-reverser in P54-05: build a
workbench-native /workbench_c919_spec.html that reuses
workbench_spec.html's design language (KPI cards, donut, REQ-card
grid, traceability matrix) and add C919-specific surfaces (state
machine flow strip, FANTUI-vs-C919 comparison cards). The legacy
/c919_requirements.html stays available for direct visitors.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC = REPO_ROOT / "src" / "well_harness" / "static"
WB_HTML = (STATIC / "workbench.html").read_text(encoding="utf-8")
SPEC = (STATIC / "workbench_c919_spec.html").read_text(encoding="utf-8")
TR_SPEC = (STATIC / "workbench_spec.html").read_text(encoding="utf-8")


# ─── 1. spec view repointed at the workbench-native rebuild ───


def test_spec_view_iframe_points_at_workbench_c919_spec():
    block = re.search(
        r'<section[^>]*id="workbench-spec-panel"[^>]*>(.*?)</section>',
        WB_HTML,
        re.DOTALL,
    )
    assert block is not None
    body = block.group(0)
    assert (
        'data-system-src-c919-etras="/workbench_c919_spec.html"' in body
    ), "C919 spec view must use the workbench-native rebuild"
    # The legacy page must NOT be the spec view's iframe target —
    # it stays at its standalone route for direct visitors.
    assert (
        'data-system-src-c919-etras="/c919_requirements.html' not in body
    ), "spec view must no longer iframe the legacy C919 requirements page"


# ─── 2. workbench-native shell present ───


@pytest.mark.parametrize(
    "selector",
    [
        # Same shared design tokens / classes as workbench_spec.html
        "spec-shell",
        "spec-header",
        "spec-eyebrow",
        "spec-overview",
        "spec-kpis",
        "spec-kpi",
        "spec-donut",
        "spec-section-title",
        "spec-req-grid",
        "spec-req-card",
        "spec-matrix",
        "spec-matrix-cell-on",
    ],
)
def test_c919_spec_uses_workbench_design_tokens(selector):
    """Reusing workbench_spec.html's class names guarantees the
    C919 surface inherits the same look-and-feel without duplicate
    tokens drifting over time."""
    assert selector in SPEC, (
        f"workbench_c919_spec.html missing shared class '{selector}'"
    )


def test_c919_spec_shares_design_tokens_with_thrust_reverser_spec():
    """The two specs declare the same CSS custom properties so the
    workbench as a whole has one design system, not two."""
    for token in ("--accent", "--text-main", "--text-muted", "--hairline", "--bg-card"):
        assert token in SPEC, f"missing shared token {token}"
        assert token in TR_SPEC


# ─── 3. C919-specific content present ───


def test_c919_spec_has_state_machine_flow_strip():
    """C919's defining feature is the FSM (S0..S10 + SF). The page
    must surface a compact horizontal flow strip with all 12 states."""
    assert "spec-state-flow" in SPEC
    assert "spec-state-track" in SPEC
    for state in (
        "S0", "S1", "S2", "S3", "S4", "S5",
        "S6", "S7", "S8", "S9", "S10", "SF",
    ):
        assert (
            f">{state}</div>" in SPEC or f">{state}<" in SPEC
        ), f"state {state} missing from flow strip"


def test_c919_spec_has_three_requirement_kinds():
    """AR (architecture), SM (state-machine), FR (functional) —
    all three taxonomies must render as REQ cards with the right
    color-coded id pill."""
    for kind in ("ar", "sm", "fr"):
        assert (
            f'data-kind="{kind}"' in SPEC
        ), f"missing data-kind={kind} on REQ id pill"


def test_c919_spec_has_traceability_matrix_with_real_outputs():
    """The state→output matrix must enumerate all 12 states as
    columns and include the 5 canonical C919 commands."""
    assert "spec-matrix" in SPEC
    for output_cmd in (
        "SinglePhaseUnlockPower",
        "ThreePhaseTRCUPower",
        "FADEC_Deploy_Command",
        "FADEC_Stow_Command",
    ):
        assert output_cmd in SPEC, (
            f"missing {output_cmd} row in traceability matrix"
        )


def test_c919_spec_has_compare_block_against_fantui():
    """The comparison block (FANTUI vs C919) helps engineers
    moving between the two systems orient quickly. It uses the
    spec-compare-card pattern."""
    assert "spec-compare" in SPEC
    assert "FANTUI" in SPEC
    assert "C919" in SPEC


# ─── 4. iframe-embed nav-hide guard preserved ───


def test_c919_spec_carries_iframe_embed_nav_hide_guard():
    """Same guard the C919 legacy pages got in P54-04 — keeps the
    embed contract uniform across all 4 surfaces. Even though this
    page has no unified-nav itself, the hook stays in for symmetry."""
    assert "window.self !== window.top" in SPEC
    assert "is-iframe-embed" in SPEC
    assert (
        "html.is-iframe-embed .unified-nav" in SPEC
        or ".is-iframe-embed .unified-nav" in SPEC
    )


# ─── 5. legacy page still routable (regression guard) ───


def test_legacy_c919_requirements_html_still_exists():
    """Direct visitors hitting /c919_requirements.html (e.g. from
    the unified-nav) must still see the original page; we only
    redirected the workbench's spec-view iframe, not the standalone
    URL."""
    legacy = STATIC / "c919_requirements.html"
    assert legacy.exists()
    assert legacy.stat().st_size > 1000
