from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_workbench_exposes_draft_import_export_controls() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'id="workbench-export-draft-btn"' in html
    assert 'id="workbench-import-draft-btn"' in html
    assert 'id="workbench-draft-json-buffer"' in html
    assert 'id="workbench-draft-json-status"' in html
    assert 'id="workbench-interface-binding-editor"' in html
    assert 'id="workbench-interface-hardware-id"' in html
    assert 'id="workbench-interface-cable"' in html
    assert 'id="workbench-interface-connector"' in html
    assert 'id="workbench-interface-port-local"' in html
    assert 'id="workbench-interface-port-peer"' in html
    assert "Export draft JSON" in html
    assert "Import draft JSON" in html


def test_workbench_draft_export_contract_is_truth_neutral() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function buildEditableDraftExport" in js
    assert 'kind: "well-harness-workbench-ui-draft"' in js
    assert "version: 1" in js
    assert 'truth_level_impact: "none"' in js
    assert 'dal_pssa_impact: "none"' in js
    assert "controller_truth_modified: false" in js
    assert "collectWorkbenchInterfacePorts" in js
    assert "edges:" in js
    assert "hardware_bindings: snapshot.hardware_bindings" in js
    assert "hardware_binding: nodeInterfaceBinding" in js
    assert "source_refs" in js
    assert "selected_node" in js


def test_workbench_draft_import_rejects_truth_mutation_claims() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function validateEditableDraftImport" in js
    assert "function applyEditableDraftImport" in js
    assert "truth_level_impact must be none" in js
    assert "dal_pssa_impact must be none" in js
    assert "controller_truth_modified must be false" in js
    assert "hardware_bindings must be an array when present" in js
    assert "hardware_binding: node.hardware_binding" in js
    assert "sandbox_candidate restored from imported JSON" in js
    assert "api.linear.app" not in js
