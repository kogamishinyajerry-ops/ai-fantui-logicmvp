from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_multi_select_state_helpers_are_sandbox_only() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "let selectedNodeIds = new Set" in js
    assert "function toggleEditableNodeSelection" in js
    assert "function selectedEditableDraftNodes" in js
    assert "batch_duplicate_nodes" in js
    assert "batch_remove_nodes" in js
    assert "selected_node_ids" in js
    assert "Multi-select:" in js
    assert "Baseline reference nodes cannot be duplicated" in js
    assert "Baseline reference nodes cannot be removed" in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js


def test_multi_select_visual_state_is_explicit() -> None:
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert '.workbench-editable-node[data-multi-selected="true"]' in css
