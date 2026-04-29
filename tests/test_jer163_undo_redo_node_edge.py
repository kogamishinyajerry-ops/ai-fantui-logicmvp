from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_workbench_exposes_node_edge_edit_controls_and_status() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'data-editor-tool="node"' in html
    assert 'data-editor-tool="edge"' in html
    assert 'data-editor-tool="remove"' in html
    assert 'data-editor-tool="disconnect"' in html
    assert 'data-editor-tool="undo"' in html
    assert 'data-editor-tool="redo"' in html
    assert 'id="workbench-graph-validation-status"' in html
    assert 'id="workbench-draft-hash-label"' in html


def test_editable_canvas_has_undo_redo_and_node_edge_operations() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    for function_name in (
        "function serializeEditableState",
        "function recordEditableHistory",
        "function undoEditableEdit",
        "function redoEditableEdit",
        "function addEditableNode",
        "function removeSelectedEditableNode",
        "function beginEditableEdgeConnect",
        "function disconnectSelectedEditableEdge",
        "function validateEditableGraph",
    ):
        assert function_name in js

    assert "undoStack" in js
    assert "redoStack" in js
    assert "draftEdges" in js
    assert "editableDraftHash(JSON.stringify(currentDraftSnapshot()))" in js


def test_editable_graph_validation_and_snapshot_remain_truth_neutral() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert 'truth_level_impact: "none"' in js
    assert "controller_truth_modified: false" in js
    assert "Baseline reference nodes cannot be removed" in js
    assert "invalid_edge" in js
    assert "dangling_port" in js
    assert "Graph validation" in js
    assert "api.linear.app" not in js
