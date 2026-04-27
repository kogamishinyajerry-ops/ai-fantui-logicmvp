"""P52-05 — approve drawer deep polish + structural fix.

Mirrors what P52-03 did for the monitor drawer: consolidates the four
sibling sections that currently share `data-dock-section="approve"`
(annotation-inbox + workbench-bottom-bar + pending-signoff + approval-
center-panel) into ONE wrapping `#workbench-tool-approve` drawer so
they don't position-fixed-stack on top of each other.

Also locks in the visual polish for the inner panels (governance gate,
review queue, approval center, plan timeline).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


def _approve_drawer() -> str:
    """Slice from `<section id="workbench-tool-approve">` to the
    explicit `<!-- /#workbench-tool-approve -->` boundary marker.
    Naive nesting-aware parsing isn't worth the complexity here —
    the source uses an explicit close-comment so the test can lock
    in the structural envelope unambiguously."""
    m = re.search(
        r'<section[^>]*id="workbench-tool-approve"[^>]*>(.*?)<!--\s*/#workbench-tool-approve\s*-->',
        HTML,
        re.DOTALL,
    )
    assert m is not None, (
        "approve drawer wrapper not found (must be bracketed by "
        "<section id=workbench-tool-approve> ... "
        "<!-- /#workbench-tool-approve -->)"
    )
    return m.group(0)


# ─── 1. wrapper exists and is the dock-section host ──────────────


def test_approve_drawer_wrapper_exists():
    assert 'id="workbench-tool-approve"' in HTML, (
        "P52-05 introduces a single #workbench-tool-approve wrapper"
    )
    block = _approve_drawer()
    assert 'data-dock-section="approve"' in block
    assert "workbench-tool-drawer-section" in block


def test_approve_drawer_has_standard_header():
    block = _approve_drawer()
    assert "workbench-tool-drawer-header" in block, (
        "approve drawer must use the canonical drawer header for "
        "visual consistency with monitor/annotate/new"
    )
    assert "data-dock-close" in block, (
        "approve drawer must include the close button"
    )
    eyebrow = re.search(
        r'<p\s+class="eyebrow">([^<]+)</p>',
        block,
    )
    assert eyebrow is not None
    assert "approve" in eyebrow.group(1).lower()


# ─── 2. four legacy approve sections live INSIDE the wrapper ─────


@pytest.mark.parametrize(
    "section_id",
    [
        "annotation-inbox",
        "workbench-bottom-bar",
        "workbench-pending-signoff-affordance",
        "approval-center-panel",
    ],
)
def test_legacy_approve_section_lives_inside_wrapper(section_id):
    block = _approve_drawer()
    assert f'id="{section_id}"' in block, (
        f"#{section_id} must now live inside #workbench-tool-approve "
        f"(P52-05 consolidation)"
    )


# ─── 3. legacy children no longer carry data-dock-section ─────────


@pytest.mark.parametrize(
    "section_id",
    [
        "annotation-inbox",
        "workbench-bottom-bar",
        "workbench-pending-signoff-affordance",
        "approval-center-panel",
    ],
)
def test_legacy_approve_section_dropped_dock_attribute(section_id):
    """If two siblings share data-dock-section="approve", both
    become position-fixed and stack — broken. After P52-05, only
    the wrapper carries the attribute."""
    open_tag = re.search(
        r'<\w+[^>]*\bid="' + re.escape(section_id) + r'"[^>]*>',
        HTML,
    )
    assert open_tag is not None
    tag = open_tag.group(0)
    assert 'data-dock-section' not in tag, (
        f"#{section_id} must no longer carry data-dock-section; "
        f"the wrapping #workbench-tool-approve handles dock toggling"
    )


# ─── 4. plan-timeline panel also moves into the approve drawer ───


def test_plan_timeline_inside_approve_wrapper():
    block = _approve_drawer()
    assert 'id="workbench-plan-timeline"' in block, (
        "plan timeline belongs inside the approve drawer (it shows "
        "the lifecycle progress reviewers care about)"
    )


def test_governance_panel_inside_approve_wrapper():
    block = _approve_drawer()
    assert 'id="workbench-governance-panel"' in block, (
        "governance gate panel must live inside the approve drawer"
    )


# ─── 5. visual polish — proposal cards + gov gate ────────────────


def test_proposal_card_uses_p52_radius():
    """Proposal item rows in the inbox must round at 10/12px to match
    the post-P52-02 ladder."""
    rule = re.search(
        r'\.workbench-annotation-inbox-item\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    if rule is None:
        # alternative class name
        rule = re.search(
            r'\.workbench-annotation-inbox\s+li\s*\{[^}]*\}',
            CSS,
            re.DOTALL,
        )
    assert rule is not None, "proposal card rule not found"
    body = rule.group(0)
    assert (
        "border-radius: 10px" in body
        or "border-radius:10px" in body
        or "border-radius: 12px" in body
        or "border-radius:12px" in body
    ), (
        f"proposal card radius should be 10–12px (P52 ladder); "
        f"rule was: {body[:300]!r}"
    )


def test_governance_panel_uses_hairline_token():
    rule = re.search(
        r'\.workbench-governance-panel\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--wb-hairline)" in body or "border: none" in body, (
        f"governance panel should reference --wb-hairline (or be "
        f"chrome-stripped inside the approve drawer); rule body: "
        f"{body[:300]!r}"
    )
