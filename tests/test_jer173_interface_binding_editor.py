from __future__ import annotations

from pathlib import Path

from well_harness.editable_control_model import (  # type: ignore[import-untyped]
    build_reference_editable_control_model,
    validate_editable_control_model,
)
from well_harness.editable_workbench_run import (  # type: ignore[import-untyped]
    canonicalize_workbench_ui_draft,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_interface_binding_editor_controls_are_local_sandbox_only() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'id="workbench-interface-binding-editor"' in html
    assert 'id="workbench-interface-hardware-id"' in html
    assert 'id="workbench-interface-cable"' in html
    assert 'id="workbench-interface-connector"' in html
    assert 'id="workbench-interface-port-local"' in html
    assert 'id="workbench-interface-port-peer"' in html
    assert 'id="workbench-interface-evidence-status"' in html
    assert 'id="workbench-apply-interface-binding-btn"' in html
    assert "Local sandbox binding only. Truth effect: none." in html


def test_interface_binding_export_import_archive_contract_is_truth_neutral() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function normalizeInterfaceBinding" in js
    assert "function collectWorkbenchHardwareBindings" in js
    assert "function applySelectedInterfaceBinding" in js
    assert "applyInterfaceBindingBtn.addEventListener" in js
    assert "hardware_bindings: snapshot.hardware_bindings" in js
    assert "hardware_bindings_checksum" in js
    assert 'truth_effect: "none"' in js
    assert "api.linear.app" not in js


def test_ui_hardware_interface_binding_becomes_schema_valid_sandbox_evidence() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "nodes": [
            {
                "id": "logic1",
                "label": "L1 draft binding",
                "op": "and",
                "hardware_binding": {
                    "hardware_id": "TR-LRU-001",
                    "cable": "CBL-TR-A",
                    "connector": "J1",
                    "port_local": "logic1:out",
                    "port_peer": "TR-LRU-001:J1",
                    "evidence_status": "ui_draft",
                },
            }
        ],
        "edges": [],
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    ui_binding = next(
        binding
        for binding in model["hardware_bindings"]
        if binding["binding_kind"] == "ui_interface_binding"
    )
    assert ui_binding["owner_kind"] == "node"
    assert ui_binding["owner_id"] == "logic1"
    assert ui_binding["hardware_id"] == "TR-LRU-001"
    assert ui_binding["cable"] == "CBL-TR-A"
    assert ui_binding["connector"] == "J1"
    assert ui_binding["port_id"] == "logic1:out"
    assert ui_binding["port_local"] == "logic1:out"
    assert ui_binding["port_peer"] == "TR-LRU-001:J1"
    assert ui_binding["evidence_status"] == "ui_draft"
    assert ui_binding["truth_effect"] == "none"
