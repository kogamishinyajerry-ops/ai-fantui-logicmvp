from __future__ import annotations

from pathlib import Path

from well_harness.editable_workbench_run import build_workbench_sandbox_run_response


def test_sandbox_run_defaults_to_nominal_scenario_metadata() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
                "edges": [],
            },
        }
    )

    assert error is None
    assert response["scenario_id"] == "nominal_landing"
    assert response["scenario_metadata"]["scenario_id"] == "nominal_landing"
    assert response["scenario_metadata"]["custom_snapshot_applied"] is False
    assert "nominal_landing" in response["scenario_metadata"]["supported_scenarios"]


def test_sandbox_run_supports_explicit_scenario_and_custom_snapshot() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "sw1_stuck_at_touchdown",
            "custom_snapshot": {"n1k": 55.0, "engine_running": True},
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
                "edges": [],
            },
        }
    )

    metadata = response["scenario_metadata"]

    assert error is None
    assert response["scenario_id"] == "sw1_stuck_at_touchdown"
    assert response["truth_level_impact"] == "none"
    assert metadata["custom_snapshot_applied"] is True
    assert metadata["custom_snapshot_keys"] == ["engine_running", "n1k"]
    assert metadata["custom_snapshot_truth_effect"] == "none"


def test_invalid_custom_snapshot_is_sandbox_validation_not_truth_decision() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "custom_snapshot": {"unknown_input": 1.0},
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
                "edges": [],
            },
        }
    )

    assert error is None
    assert response["verdict"] == "invalid_model"
    assert response["truth_level_impact"] == "none"
    assert response["scenario_metadata"]["scenario_id"] == "nominal_landing"
    assert response["scenario_metadata"]["custom_snapshot_applied"] is True
    assert "unsupported inputs" in response["error"]


def test_invalid_scenario_returns_sandbox_validation_metadata() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "not_a_supported_scenario",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
                "edges": [],
            },
        }
    )

    assert error is None
    assert response["verdict"] == "invalid_scenario"
    assert response["truth_level_impact"] == "none"
    assert response["scenario_metadata"]["scenario_id"] == "not_a_supported_scenario"
    assert "nominal_landing" in response["scenario_metadata"]["supported_scenarios"]


def test_workbench_ui_exposes_scenario_selector_snapshot_and_archive_metadata() -> None:
    html = Path("src/well_harness/static/workbench.html").read_text(encoding="utf-8")
    js = Path("src/well_harness/static/workbench.js").read_text(encoding="utf-8")

    assert "workbench-sandbox-scenario-select" in html
    assert "workbench-custom-snapshot-json" in html
    assert "function parseWorkbenchCustomSnapshot" in js
    assert "custom_snapshot" in js
    assert "scenario_metadata" in js
