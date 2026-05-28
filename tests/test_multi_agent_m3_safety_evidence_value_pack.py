from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "multi_agent_m3_safety_evidence_value_pack_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "multi_agent_m3_safety_evidence_value_pack_v0_1.json"
)
RUN_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_multi_agent_m3_safety_evidence_value_pack.py"
CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_multi_agent_m3_safety_evidence_value_pack.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "multi_agent_m3_safety_evidence_value_pack_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_m3_safety_evidence_value_pack_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-multi-agent-m3-safety-evidence-value-pack"
    assert fixture["package_id"] == "multi-agent-m3-safety-evidence-value-pack-v0.1"
    assert fixture["milestone"] == {
        "id": "M3",
        "name": "Safety/Evidence 工程价值增强包",
        "budget": 48,
        "effort_unit": "施工队工时",
        "claim": "candidate-only deterministic finding value pack",
    }
    assert fixture["finding_classes"] == {
        "safety": ["CHECK_SAFETY_PRIORITY_001", "CHECK_UNDEFINED_SIGNAL_001"],
        "evidence": ["EV_SIMULATION_RESULT_FAILED", "EV_TEST_RESULT_MISSING"],
    }
    assert fixture["aggregate"] == {
        "slice_count": 4,
        "passed": 4,
        "converged": 4,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert fixture["review_exports"]["reviewer_statuses"] == [
        "converged",
        "converged",
        "converged",
        "converged",
    ]
    assert fixture["review_exports"]["finding_chain_statuses"] == [
        ["converged"],
        ["converged"],
        ["converged"],
        ["converged"],
    ]


def test_m3_safety_evidence_value_pack_runner_and_checker_converge(tmp_path: Path) -> None:
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
    payload = json.loads(run_result.stdout)
    assert payload["status"] == "pass"
    assert payload["package_id"] == "multi-agent-m3-safety-evidence-value-pack-v0.1"
    assert payload["slice_order"] == [
        "m3-safety-priority-repair",
        "m3-safety-undefined-signal-repair",
        "m3-evidence-simulation-result-failed-repair",
        "m3-evidence-test-result-missing-repair",
    ]
    assert [item["selected_task_id"] for item in payload["slices"]] == [
        "TASK-CE-CHECK-SAFETY-PRIORITY-001",
        "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
        "TASK-CE-EV-SIMULATION-RESULT-FAILED",
        "TASK-CE-EV-TEST-RESULT-MISSING",
    ]
    assert [item["selected_task_agent"] for item in payload["slices"]] == [
        "LogicIRRepairAgent",
        "LogicIRRepairAgent",
        "SimulationTestRepairAgent",
        "SimulationTestRepairAgent",
    ]
    assert payload["aggregate"]["open_findings"] == []
    assert payload["deterministic_gates"] == {
        "safety_priority_slice": "pass",
        "safety_undefined_signal_slice": "pass",
        "evidence_failed_result_slice": "pass",
        "evidence_missing_result_slice": "pass",
        "review_packet_exports": "pass",
        "local_gate": "pass",
    }

    package_path = Path(payload["artifact_paths"]["package"])
    assert package_path.exists()
    for item in payload["slices"]:
        review_export_path = Path(item["artifact_paths"]["candidate_review_packet_export"])
        assert review_export_path.exists()
        validate_candidate_review_packet_export(
            json.loads(review_export_path.read_text(encoding="utf-8"))
        )

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
    assert check_payload["child_review_exports_valid"] is True
    assert check_payload["convergence_valid"] is True
    assert check_payload["mismatches"] == []


def test_m3_safety_evidence_value_pack_checker_reports_nonconverged_child_drift(
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
        timeout=120,
    )
    assert run_result.returncode == 0, run_result.stderr

    package_path = tmp_path / "multi_agent_m3_safety_evidence_value_pack_v0_1.json"
    package = json.loads(package_path.read_text(encoding="utf-8"))
    package["slices"][1]["reviewer_status"] = "open_findings"
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
    assert payload["convergence_valid"] is False
    assert "m3-safety-undefined-signal-repair.reviewer_status must be converged" in payload[
        "mismatches"
    ]


def test_m3_safety_evidence_value_pack_is_wired_into_make() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")

    assert "multi-agent-m3-safety-evidence-value-pack" in makefile
    assert "scripts/run_multi_agent_m3_safety_evidence_value_pack.py --format json" in makefile
    assert "scripts/verify_multi_agent_m3_safety_evidence_value_pack.py --format json" in makefile
