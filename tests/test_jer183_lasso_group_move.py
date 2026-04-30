from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_lasso_and_group_move_helpers_are_sandbox_only() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "let lassoDragState = null" in js
    assert "let groupDragState = null" in js
    assert "function beginCanvasLasso" in js
    assert "function applyLassoSelection" in js
    assert "function beginEditableGroupDrag" in js
    assert "function updateEditableGroupDrag" in js
    assert "function clampCanvasPercent" in js
    assert "renderEditableEdges();" in js
    assert "group_move_nodes" in js
    assert "lasso selected" in js
    assert "group moved" in js
    assert "Truth effect: none" in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js


def test_lasso_visual_marquee_is_explicit() -> None:
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert ".workbench-selection-marquee" in css
    assert '.workbench-selection-marquee[data-active="true"]' in css
