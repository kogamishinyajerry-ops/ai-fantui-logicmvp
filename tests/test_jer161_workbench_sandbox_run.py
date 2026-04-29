from __future__ import annotations

from pathlib import Path

from well_harness.editable_workbench_run import build_workbench_sandbox_run_response


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
DEMO_SERVER = PROJECT_ROOT / "src" / "well_harness" / "demo_server.py"


def test_workbench_sandbox_run_reports_equivalent_nominal_timeline() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
            },
        }
    )

    assert error is None
    assert response["kind"] == "well-harness-workbench-sandbox-run"
    assert response["scenario_id"] == "nominal_landing"
    assert response["verdict"] == "equivalent"
    assert response["truth_level_impact"] == "none"
    assert response["diff_report"]["scenario_result"]["frame_count"] == 180
    assert response["summary"]["first_divergence"] is None


def test_workbench_sandbox_run_reports_divergent_candidate_op_edit() -> None:
    response, error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [
                    {"id": "logic3", "op": "or", "label": "L3 drift candidate"},
                ],
            },
        }
    )

    assert error is None
    assert response["verdict"] == "divergent"
    assert response["summary"]["first_divergence"]["signal_id"] in {
        "logic3",
        "logic4",
    }
    assert response["model_hash"] == response["diff_report"]["candidate_run"]["model_hash"]


def test_workbench_sandbox_run_invalid_model_and_scenario_are_reported_not_promoted() -> None:
    invalid_model, model_error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "nominal_landing",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [{"id": "logic3", "op": "python_eval"}],
            },
        }
    )
    invalid_scenario, scenario_error = build_workbench_sandbox_run_response(
        {
            "scenario_id": "not-a-fixture",
            "draft": {
                "system_id": "thrust-reverser",
                "truth_level_impact": "none",
                "controller_truth_modified": False,
                "nodes": [],
            },
        }
    )

    assert model_error is None
    assert invalid_model["verdict"] == "invalid_model"
    assert invalid_model["truth_level_impact"] == "none"
    assert scenario_error is None
    assert invalid_scenario["verdict"] == "invalid_scenario"
    assert invalid_scenario["truth_level_impact"] == "none"


def test_workbench_sandbox_run_endpoint_and_ui_contract_are_present() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    server = DEMO_SERVER.read_text(encoding="utf-8")

    assert 'id="workbench-run-sandbox-btn"' in html
    assert 'id="workbench-diff-verdict"' in html
    assert 'id="workbench-diff-first-divergence"' in html
    assert "/api/workbench/editable-sandbox-run" in server
    assert "/api/workbench/editable-sandbox-run" in js
    assert "function runWorkbenchSandboxDiff" in js
    assert "function renderWorkbenchSandboxDiff" in js
    assert "invalid_model" in js
    assert "invalid_scenario" in js
    assert "Truth-level impact: none" in js
    assert "api.linear.app" not in js
