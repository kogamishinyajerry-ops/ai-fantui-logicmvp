from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_workbench_exposes_duplicate_toolbar_action() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'data-editor-tool="duplicate"' in html
    assert 'title="Duplicate draft node"' in html


def test_duplicate_and_keyboard_shortcuts_are_sandbox_only() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function duplicateSelectedEditableNode" in js
    assert "function handleEditableKeyboardShortcut" in js
    assert "Baseline reference nodes cannot be duplicated" in js
    assert 'tool === "duplicate"' in js
    assert 'key === "d"' in js
    assert 'key === "z"' in js
    assert 'key === "y"' in js
    assert 'event.key === "Delete"' in js
    assert "recordEditableHistory(" in js
    assert "duplicate_node" in js
    assert "ui_draft.duplicate" in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js
