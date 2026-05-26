from __future__ import annotations

from well_harness.editable_control_model import (
    build_reference_editable_control_model,
    editable_control_model_hash,
    validate_editable_control_model,
)
from well_harness.editable_workbench_run import (
    build_workbench_sandbox_run_response,
    canonicalize_workbench_ui_draft,
)


def test_ui_draft_dynamic_node_and_edge_become_schema_valid_model() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "nodes": [
            {
                "id": "draft_node_1",
                "label": "Draft monitor gate",
                "op": "and",
                "sourceRef": "ui_draft.nodes.draft_node_1",
                "draftNode": True,
            },
        ],
        "edges": [
            {
                "id": "edge_logic1_draft_node_1",
                "source": "logic1",
                "target": "draft_node_1",
            },
        ],
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    assert model["kind"] == "well-harness-editable-control-model"
    assert model["truth_status"] == "sandbox_candidate"
    assert model["view_status"] == "draft"
    assert model["boundaries"]["truth_level_impact"] == "none"
    assert any(node["id"] == "draft_node_1" for node in model["nodes"])
    assert any(port["id"] == "draft_node_1:in" for port in model["ports"])
    assert any(port["id"] == "draft_node_1:out" for port in model["ports"])
    assert any(
        edge["id"] == "ui-edge:edge_logic1_draft_node_1"
        and edge["source_port_id"] == "logic1:out"
        and edge["target_port_id"] == "draft_node_1:in"
        and edge["evidence_only"] is True
        for edge in model["edges"]
    )
    assert editable_control_model_hash(model) != editable_control_model_hash(base)


def test_ui_draft_edge_to_existing_logic_gets_synthetic_target_port() -> None:
    base = build_reference_editable_control_model()
    draft = {
        "system_id": "thrust-reverser",
        "truth_level_impact": "none",
        "controller_truth_modified": False,
        "nodes": [],
        "edges": [
            {
                "id": "edge_logic1_logic3_draft",
                "source": "logic1",
                "target": "logic3",
            },
        ],
    }

    model = canonicalize_workbench_ui_draft(base, draft)

    validate_editable_control_model(model)
    assert any(
        port["id"] == "logic3:in:ui_edge:logic1"
        and port["node_id"] == "logic3"
        and port["direction"] == "in"
        for port in model["ports"]
    )
    assert any(
        edge["id"] == "ui-edge:edge_logic1_logic3_draft"
        and edge["target_port_id"] == "logic3:in:ui_edge:logic1"
        for edge in model["edges"]
    )


def test_sandbox_run_exposes_canonical_model_evidence_for_ui_draft() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [
                    {
                        "id": "draft_node_1",
                        "label": "Draft monitor gate",
                        "op": "or",
                        "draftNode": True,
                    },
                ],
                "edges": [
                    {
                        "id": "edge_logic1_draft_node_1",
                        "source": "logic1",
                        "target": "draft_node_1",
                    },
                ],
            },
        }
    )

    assert error is None
    assert response["truth_level_impact"] == "none"
    assert response["canonical_model"]["kind"] == "well-harness-editable-control-model"
    assert response["canonical_model_hash"] == response["model_hash"]
    assert any(node["id"] == "draft_node_1" for node in response["canonical_model"]["nodes"])


def test_sandbox_run_accepts_ui_catalog_input_and_output_primitives() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [
                    {
                        "id": "draft_node_1",
                        "label": "Draft input",
                        "op": "input",
                        "draftNode": True,
                        "op_catalog_entry": "input",
                    },
                    {
                        "id": "draft_node_2",
                        "label": "Draft output",
                        "op": "output",
                        "draftNode": True,
                        "op_catalog_entry": "output",
                    },
                ],
                "edges": [
                    {
                        "id": "edge_draft_input_output",
                        "source": "draft_node_1",
                        "target": "draft_node_2",
                    }
                ],
            },
        }
    )

    assert error is None
    assert response["verdict"] != "invalid_model"
    nodes = {node["id"]: node for node in response["canonical_model"]["nodes"]}
    assert nodes["draft_node_1"]["op"] == "input"
    assert nodes["draft_node_1"]["node_type"] == "input"
    assert nodes["draft_node_2"]["op"] == "output"
    assert nodes["draft_node_2"]["node_type"] == "output"
    assert response["validation_report"]["status"] == "pass"
    assert response["truth_level_impact"] == "none"


def test_sandbox_run_accepts_ui_catalog_compare_and_between_primitives() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [
                    {
                        "id": "draft_node_1",
                        "label": "Draft compare",
                        "op": "compare",
                        "draftNode": True,
                        "op_catalog_entry": "compare",
                    },
                    {
                        "id": "draft_node_2",
                        "label": "Draft between",
                        "op": "between",
                        "draftNode": True,
                        "op_catalog_entry": "between",
                    },
                ],
                "edges": [
                    {
                        "id": "edge_draft_compare_between",
                        "source": "draft_node_1",
                        "target": "draft_node_2",
                    }
                ],
            },
        }
    )

    assert error is None
    assert response["verdict"] != "invalid_model"
    nodes = {node["id"]: node for node in response["canonical_model"]["nodes"]}
    assert nodes["draft_node_1"]["op"] == "compare"
    assert nodes["draft_node_2"]["op"] == "between"
    assert response["validation_report"]["status"] == "pass"
    assert response["truth_level_impact"] == "none"


def test_ui_draft_invalid_edge_is_reported_as_invalid_model_not_truth_change() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
                "edges": [
                    {
                        "id": "edge_missing_logic1",
                        "source": "missing_node",
                        "target": "logic1",
                    },
                ],
            },
        }
    )

    assert error is None
    assert response["verdict"] == "invalid_model"
    assert response["truth_level_impact"] == "none"
    assert "references missing source node" in response["error"]
    assert response["red_lines"]["controller_truth_modified"] is False
