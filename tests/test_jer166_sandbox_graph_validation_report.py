from __future__ import annotations

import copy
from pathlib import Path

import pytest

from well_harness.editable_control_model import build_reference_editable_control_model
from well_harness.editable_workbench_run import (
    WorkbenchGraphValidationError,
    build_workbench_sandbox_run_response,
    canonicalize_workbench_ui_draft,
)


def test_invalid_edge_returns_structured_missing_node_report() -> None:
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

    report = response["validation_report"]

    assert error is None
    assert response["verdict"] == "invalid_model"
    assert report["kind"] == "well-harness-workbench-graph-validation-report"
    assert report["status"] == "fail"
    assert report["issue_count"] == 1
    assert set(report["categories"]) == {
        "invalid_edge",
        "dangling_port",
        "duplicate_edge",
        "unsafe_op",
        "missing_node",
    }
    assert report["categories"]["missing_node"][0]["edge_id"] == "edge_missing_logic1"
    assert report["categories"]["missing_node"][0]["node_id"] == "missing_node"
    assert response["summary"]["validation_issue_count"] == 1
    assert response["truth_level_impact"] == "none"


def test_unsafe_op_and_duplicate_edge_are_classified() -> None:
    unsafe_response, _ = build_workbench_sandbox_run_response(
        {
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [{"id": "draft_node_1", "op": "__import__"}],
                "edges": [],
            },
        }
    )

    duplicate_response, _ = build_workbench_sandbox_run_response(
        {
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [{"id": "draft_node_1"}, {"id": "draft_node_2"}],
                "edges": [
                    {"id": "duplicate_edge", "source": "draft_node_1", "target": "draft_node_2"},
                    {"id": "duplicate_edge", "source": "draft_node_2", "target": "draft_node_1"},
                ],
            },
        }
    )

    assert unsafe_response["validation_report"]["categories"]["unsafe_op"][0]["node_id"] == "draft_node_1"
    assert unsafe_response["validation_report"]["categories"]["unsafe_op"][0]["code"] == "unsafe_op"
    assert duplicate_response["validation_report"]["categories"]["duplicate_edge"][0]["edge_id"] == "duplicate_edge"
    assert duplicate_response["validation_report"]["categories"]["duplicate_edge"][0]["code"] == "duplicate_edge"


def test_dangling_port_report_is_available_for_invalid_canonical_graph() -> None:
    base = build_reference_editable_control_model()
    broken_base = copy.deepcopy(base)
    broken_base["ports"] = [
        port
        for port in broken_base["ports"]
        if port["id"] != "logic1:out"
    ]

    with pytest.raises(WorkbenchGraphValidationError) as exc_info:
        canonicalize_workbench_ui_draft(
            broken_base,
            {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [{"id": "draft_node_1"}],
                "edges": [{"id": "edge_logic1_draft", "source": "logic1", "target": "draft_node_1"}],
            },
        )

    report = exc_info.value.validation_report
    assert report["status"] == "fail"
    assert report["categories"]["dangling_port"][0]["port_id"] == "logic1:out"
    assert report["categories"]["dangling_port"][0]["edge_id"] == "edge_logic1_draft"


def test_valid_sandbox_response_includes_empty_pass_validation_report() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [{"id": "draft_node_1", "op": "or"}],
                "edges": [{"id": "edge_logic1_draft", "source": "logic1", "target": "draft_node_1"}],
            },
        }
    )

    report = response["validation_report"]

    assert error is None
    assert response["verdict"] in {"equivalent", "divergent"}
    assert report["status"] == "pass"
    assert report["issue_count"] == 0
    assert all(not issues for issues in report["categories"].values())


def test_workbench_js_renders_validation_report_summary() -> None:
    js = Path("src/well_harness/static/workbench.js").read_text(encoding="utf-8")

    assert "function graphValidationReportText" in js
    assert "validation_report" in js
    assert "missing_node" in js
    assert "unsafe_op" in js
