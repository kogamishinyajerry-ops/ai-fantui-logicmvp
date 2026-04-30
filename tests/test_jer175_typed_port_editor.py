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


def test_typed_port_editor_controls_are_local_sandbox_only() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")

    assert 'id="workbench-typed-port-editor"' in html
    assert 'id="workbench-port-input-signal"' in html
    assert 'id="workbench-port-output-signal"' in html
    assert 'id="workbench-port-value-type"' in html
    assert 'id="workbench-port-unit"' in html
    assert 'id="workbench-port-required"' in html
    assert 'id="workbench-edge-signal-id"' in html
    assert 'id="workbench-edge-source-port"' in html
    assert 'id="workbench-edge-target-port"' in html
    assert 'id="workbench-apply-port-contract-btn"' in html
    assert "Local sandbox port contract only. Truth effect: none." in html


def test_typed_port_export_archive_contract_is_truth_neutral() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function normalizePortContract" in js
    assert "function collectWorkbenchTypedPorts" in js
    assert "function buildPortContractSummary" in js
    assert "function applySelectedPortContract" in js
    assert "port_contract_summary: portContractSummary" in js
    assert "typed_ports_checksum" in js
    assert "port_contract_summary_checksum" in js
    assert 'truth_effect: "none"' in js
    assert "api.linear.app" not in js


def test_ui_typed_ports_become_schema_valid_sandbox_model_metadata() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "nodes": [
            {
                "id": "logic1",
                "label": "L1 typed output draft",
                "op": "and",
                "port_contract": {
                    "input_signal_id": "logic1_candidate_input",
                    "output_signal_id": "logic1_candidate_output",
                    "value_type": "number",
                    "unit": "deg",
                    "required": True,
                    "truth_effect": "none",
                },
            },
            {
                "id": "draft_node_1",
                "label": "Draft typed gate",
                "op": "or",
                "draftNode": True,
                "port_contract": {
                    "input_signal_id": "draft_candidate_input",
                    "output_signal_id": "draft_candidate_output",
                    "value_type": "boolean",
                    "required": True,
                    "truth_effect": "none",
                },
            },
        ],
        "edges": [
            {
                "id": "edge_logic1_draft_node_1",
                "source": "logic1",
                "target": "draft_node_1",
                "signal_id": "typed_edge_signal",
                "source_port_id": "logic1:out:aux",
                "target_port_id": "draft_node_1:in:aux",
                "value_type": "number",
                "unit": "deg",
                "required": True,
            }
        ],
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    ports = {port["id"]: port for port in model["ports"]}
    assert ports["logic1:out"]["signal_id"] == "logic1_candidate_output"
    assert ports["logic1:out"]["value_type"] == "number"
    assert ports["logic1:out"]["unit"] == "deg"
    assert ports["logic1:out"]["required"] is True
    assert ports["draft_node_1:in"]["signal_id"] == "draft_candidate_input"
    assert ports["logic1:out:aux"]["signal_id"] == "typed_edge_signal"
    assert ports["logic1:out:aux"]["direction"] == "out"
    assert ports["draft_node_1:in:aux"]["signal_id"] == "typed_edge_signal"
    assert ports["draft_node_1:in:aux"]["direction"] == "in"
    assert any(
        edge["id"] == "ui-edge:edge_logic1_draft_node_1"
        and edge["source_port_id"] == "logic1:out:aux"
        and edge["target_port_id"] == "draft_node_1:in:aux"
        and edge["evidence_only"] is True
        for edge in model["edges"]
    )
    assert model["boundaries"]["truth_level_impact"] == "none"


def test_top_level_typed_ports_are_merged_without_truth_effect() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "controller_truth_modified": False,
        "nodes": [],
        "typed_ports": [
            {
                "id": "logic2:in:ui_aux",
                "node_id": "logic2",
                "direction": "in",
                "signal_id": "ui_aux_signal",
                "value_type": "state",
                "unit": "",
                "required": False,
                "truth_effect": "none",
            }
        ],
        "edges": [],
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    aux_port = next(port for port in model["ports"] if port["id"] == "logic2:in:ui_aux")
    assert aux_port["signal_id"] == "ui_aux_signal"
    assert aux_port["value_type"] == "state"
    assert model["boundaries"]["truth_level_impact"] == "none"
