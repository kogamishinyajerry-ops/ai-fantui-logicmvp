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
    / "multi_agent_m2_requirement_to_ir_demo_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_m2_requirement_to_ir_demo_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m2_requirement_to_ir_demo.py"
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_multi_agent_m2_requirement_to_ir_demo.py"
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m2_requirement_to_ir_demo_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_m2_requirement_to_ir_demo_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m2-requirement-to-ir-demo"
    assert fixture["package_id"] == "multi-agent-m2-requirement-to-ir-demo-v0.1"
    assert fixture["milestone"] == {
        "id": "M2",
        "name": "Requirement to IR 最小产品演示包",
        "budget": 36,
        "effort_unit": "施工队工时",
        "claim": "candidate-only requirement-to-ir demo",
    }
    assert fixture["source_requirement"]["fixture_id"] == "engine-start-control-requirement-v0.1"
    assert fixture["pipeline"]["structured_requirement_count"] == 4
    assert fixture["pipeline"]["candidate_ir"]["state_count"] == 6
    assert fixture["pipeline"]["candidate_ir"]["transition_count"] == 5
    assert fixture["pipeline"]["safety_findings_before"] == ["CHECK_SAFETY_PRIORITY_001"]
    assert fixture["pipeline"]["evidence_findings_before"] == []
    assert fixture["review_export"]["reviewer_status"] == "converged"
    assert fixture["review_export"]["finding_chain_statuses"] == ["converged"]
    assert fixture["aggregate"] == {
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_m2_review": True,
    }


def test_m2_requirement_to_ir_demo_runner_and_checker_converge(tmp_path: Path) -> None:
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
        timeout=120,
    )

    assert run_result.returncode == 0, run_result.stderr
    run_payload = json.loads(run_result.stdout)
    assert run_payload["status"] == "pass"
    assert run_payload["package_id"] == "multi-agent-m2-requirement-to-ir-demo-v0.1"
    assert run_payload["structured_requirements"]["ids"] == [
        "REQ-START-001",
        "REQ-START-002",
        "REQ-SAFE-001",
        "REQ-SAFE-002",
    ]
    assert run_payload["task_package"]["selected_task_id"] == "TASK-CE-CHECK-SAFETY-PRIORITY-001"
    assert run_payload["deterministic_gates"] == {
        "agent_output_contract": "pass",
        "requirement_traceability": "pass",
        "safety_finding_detected": "pass",
        "approved_task_shell": "pass",
        "repair_loop_converged": "pass",
        "candidate_review_export": "pass",
    }
    package_path = Path(run_payload["artifact_paths"]["demo_package"])
    assert package_path.exists()

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
        timeout=60,
    )

    assert check_result.returncode == 0, check_result.stderr
    check_payload = json.loads(check_result.stdout)
    assert check_payload["status"] == "pass"
    assert check_payload["schema_valid"] is True
    assert check_payload["child_artifacts_valid"] is True
    assert check_payload["traceability_valid"] is True
    assert check_payload["review_export_valid"] is True
    assert check_payload["mismatches"] == []


def test_m2_requirement_to_ir_demo_checker_reports_open_finding_drift(tmp_path: Path) -> None:
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
        timeout=120,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m2_requirement_to_ir_demo_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["aggregate"]["open_findings"] = ["DRIFTED_FINDING"]
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
        timeout=60,
    )

    assert check_result.returncode == 1
    payload = json.loads(check_result.stdout)
    assert payload["status"] == "fail"
    assert payload["traceability_valid"] is False
    assert "aggregate.open_findings must be empty" in payload["mismatches"]


def test_m2_requirement_to_ir_demo_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-m2-requirement-to-ir-demo" in makefile
    assert "scripts/run_multi_agent_m2_requirement_to_ir_demo.py --format json" in makefile
