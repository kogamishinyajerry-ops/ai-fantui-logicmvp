from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_m5_construction_control_plane_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_m5_construction_control_plane_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m5_construction_control_plane.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_m5_construction_control_plane.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m5_construction_control_plane_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_m5_construction_control_plane_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m5-construction-control-plane"
    assert fixture["package_id"] == "multi-agent-m5-construction-control-plane-v0.1"
    assert fixture["milestone"] == {
        "id": "M5",
        "name": "长时间开工控制面",
        "budget": 40,
        "effort_unit": "施工队工时",
        "claim": "candidate-only long-running construction control plane",
    }
    assert fixture["control_plane_summary"] == {
        "readiness_status": "ready_for_long_running_construction",
        "entrypoint": "make multi-agent-construction-control-plane",
        "included_milestones": ["M1", "M2", "M3", "M4"],
        "single_entrypoint": True,
    }
    assert fixture["queue_snapshot"] == {
        "queue_id": "approved-candidate-task-queue-v0.1",
        "task_count": 3,
        "passed": 3,
        "preflight_passed": 3,
        "executed_limited": 3,
        "converged": 3,
        "open_findings": [],
        "ready_for_long_running_development": True,
    }
    assert fixture["aggregate"] == {
        "milestone_count": 4,
        "child_package_count": 3,
        "queue_task_count": 3,
        "approved_task_count": 3,
        "active_stop_conditions": [],
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_long_running_construction": True,
    }
    assert [item["id"] for item in fixture["failure_recovery"]] == [
        "FR-GATE-001",
        "FR-QUEUE-001",
        "FR-BOUNDARY-001",
        "FR-CHILD-001",
    ]
    assert [item["id"] for item in fixture["phase_review_stop_conditions"]] == [
        "STOP-APPROVAL-MISSING",
        "STOP-CONTROLLER-TRUTH-DIFF",
        "STOP-UI-LAYOUT-DIFF",
        "STOP-CERTIFICATION-CLAIM",
        "STOP-DETERMINISTIC-GATE-FAIL",
    ]


def test_m5_construction_control_plane_runner_and_checker_converge(tmp_path: Path) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=360,
    )

    assert run_result.returncode == 0, run_result.stderr
    payload = json.loads(run_result.stdout)
    assert payload["status"] == "pass"
    assert payload["package_id"] == "multi-agent-m5-construction-control-plane-v0.1"
    assert payload["deterministic_gates"] == {
        "m4_external_review_handoff": "pass",
        "approved_candidate_task_queue": "pass",
        "approved_candidate_task_queue_artifact": "pass",
        "construction_readiness": "pass",
        "failure_recovery_runbook": "pass",
        "phase_review_stop_conditions": "pass",
        "local_gate_entrypoint": "pass",
    }
    assert payload["control_plane_summary"]["readiness_status"] == (
        "ready_for_long_running_construction"
    )
    assert payload["aggregate"]["ready_for_long_running_construction"] is True
    assert payload["aggregate"]["active_stop_conditions"] == []
    assert payload["execution_policy"]["approved_only"] is True
    assert payload["execution_policy"]["requires_explicit_approval"] is True

    package_path = Path(payload["artifact_paths"]["control_plane_package"])
    runbook_path = Path(payload["artifact_paths"]["operator_runbook"])
    assert package_path.exists()
    assert runbook_path.exists()
    runbook_text = runbook_path.read_text(encoding="utf-8")
    assert "M5 Construction Control Plane" in runbook_text
    assert "make multi-agent-construction-control-plane" in runbook_text
    assert "STOP-CONTROLLER-TRUTH-DIFF" in runbook_text

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["schema_valid"] is True
    assert check_payload["child_packages_valid"] is True
    assert check_payload["queue_snapshot_valid"] is True
    assert check_payload["failure_recovery_valid"] is True
    assert check_payload["phase_stop_conditions_valid"] is True
    assert check_payload["boundary_valid"] is True
    assert check_payload["mismatches"] == []


def test_m5_construction_control_plane_checker_reports_stop_condition_drift(
    tmp_path: Path,
) -> None:
    run_result = subprocess.run(
        [
            sys.executable,
            str(RUN_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=360,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m5_construction_control_plane_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["phase_review_stop_conditions"] = [
        item
        for item in package["phase_review_stop_conditions"]
        if item["id"] != "STOP-CONTROLLER-TRUTH-DIFF"
    ]
    package_path.write_text(json.dumps(package), encoding="utf-8")

    check_result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--package",
            str(package_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["phase_stop_conditions_valid"] is False
    assert "phase_review_stop_conditions must include STOP-CONTROLLER-TRUTH-DIFF" in payload[
        "mismatches"
    ]


def test_m5_construction_control_plane_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-construction-control-plane" in makefile
    assert "scripts/run_multi_agent_m5_construction_control_plane.py --format json" in makefile
    assert "scripts/verify_multi_agent_m5_construction_control_plane.py --format json" in makefile
