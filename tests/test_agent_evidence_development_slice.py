from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from well_harness.agent_review_packet import validate_candidate_review_packet_export


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_evidence_candidate_repair_slice.py"
MISSING_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "run_missing_test_result_candidate_repair_slice.py"
UNKNOWN_REQUIREMENT_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_evidence_unknown_requirement_candidate_repair_slice.py"
)
UNKNOWN_TRACE_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "run_evidence_unknown_trace_candidate_repair_slice.py"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def _simulation_result_by_id(packet: dict, scenario_id: str) -> dict:
    for result in packet["agent_output"]["payload"]["simulation_results"]:
        if result["scenario_id"] == scenario_id:
            return result
    raise AssertionError(f"missing simulation result {scenario_id}")


def _test_scenario_by_id(packet: dict, scenario_id: str) -> dict:
    for scenario in packet["agent_output"]["payload"]["test_scenarios"]:
        if scenario["id"] == scenario_id:
            return scenario
    raise AssertionError(f"missing test scenario {scenario_id}")


def _transition_by_id(packet: dict, transition_id: str) -> dict:
    for transition in packet["agent_output"]["payload"]["logic_ir"]["transitions"]:
        if transition["id"] == transition_id:
            return transition
    raise AssertionError(f"missing transition {transition_id}")


def test_evidence_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "evidence-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-EV-SIMULATION-RESULT-FAILED",
        "target_agent": "SimulationTestRepairAgent",
        "task_type": "repair_candidate_test_oracle",
        "approval_status": "approved",
    }
    assert payload["repair_agent"] == {
        "agent_name": "SimulationTestRepairAgent",
        "status": "candidate_patch_generated",
        "action_count": 1,
    }
    assert payload["candidate_delta"] == {
        "changed_simulation_result_ids": ["TC-HOT-START-ABORT-001"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["deterministic_gates"] == {
        "safety_guardian": "pass",
        "evidence_agent": "pass",
        "candidate_review_packet": "pass",
        "candidate_review_packet_export": "pass",
        "local_gate": "pass",
    }
    assert payload["reviewer_status"] == "converged"
    assert payload["finding_chain_statuses"] == ["converged"]
    assert payload["convergence"]["before_findings"] == ["EV_SIMULATION_RESULT_FAILED"]
    assert payload["convergence"]["after_findings"] == []
    assert payload["convergence"]["task_package_status"] == "no_tasks_required"
    assert payload["convergence"]["execution_plan_status"] == "no_task_available"
    assert payload["convergence"]["execution_evidence_status"] == "no_task_available"

    artifact_paths = payload["artifact_paths"]
    repaired_packet_path = Path(artifact_paths["repaired_candidate_packet"])
    review_export_path = Path(artifact_paths["candidate_review_packet_export"])
    assert repaired_packet_path.exists()
    assert review_export_path.exists()

    repaired_packet = json.loads(repaired_packet_path.read_text(encoding="utf-8"))
    assert _simulation_result_by_id(
        repaired_packet,
        "TC-HOT-START-ABORT-001",
    )["status"] == "pass"

    review_export = json.loads(review_export_path.read_text(encoding="utf-8"))
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["reviewer"]["status"] == "converged"
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["performed"] is True
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "set_simulation_result_status",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "from": "fail",
            "to": "pass",
            "reason": "EV_SIMULATION_RESULT_FAILED",
        }
    ]


def test_evidence_candidate_repair_slice_is_wired_into_makefile() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "evidence-candidate-repair-slice" in makefile
    assert "scripts/run_evidence_candidate_repair_slice.py --format json" in makefile


def test_missing_test_result_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(MISSING_SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "missing-test-result-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-EV-TEST-RESULT-MISSING",
        "target_agent": "SimulationTestRepairAgent",
        "task_type": "repair_candidate_test_oracle",
        "approval_status": "approved",
    }
    assert payload["candidate_delta"] == {
        "changed_simulation_result_ids": ["TC-HOT-START-ABORT-001"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["convergence"]["before_findings"] == ["EV_TEST_RESULT_MISSING"]
    assert payload["convergence"]["after_findings"] == []

    repaired_packet = json.loads(
        Path(payload["artifact_paths"]["repaired_candidate_packet"]).read_text(encoding="utf-8")
    )
    assert _simulation_result_by_id(
        repaired_packet,
        "TC-HOT-START-ABORT-001",
    )["status"] == "pass"

    review_export = json.loads(
        Path(payload["artifact_paths"]["candidate_review_packet_export"]).read_text(
            encoding="utf-8"
        )
    )
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "add_simulation_result",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "status": "pass",
            "reason": "EV_TEST_RESULT_MISSING",
        }
    ]


def test_unknown_requirement_coverage_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(UNKNOWN_REQUIREMENT_SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "evidence-unknown-requirement-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT",
        "target_agent": "EvidenceRepairAgent",
        "task_type": "repair_evidence_trace",
        "approval_status": "approved",
    }
    assert payload["candidate_delta"] == {
        "changed_test_scenario_ids": ["TC-HOT-START-ABORT-001"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["convergence"]["before_findings"] == ["EV_TEST_COVERS_UNKNOWN_REQUIREMENT"]
    assert payload["convergence"]["after_findings"] == []

    repaired_packet = json.loads(
        Path(payload["artifact_paths"]["repaired_candidate_packet"]).read_text(encoding="utf-8")
    )
    assert _test_scenario_by_id(
        repaired_packet,
        "TC-HOT-START-ABORT-001",
    )["covers"] == ["REQ-SAFE-001"]

    review_export = json.loads(
        Path(payload["artifact_paths"]["candidate_review_packet_export"]).read_text(
            encoding="utf-8"
        )
    )
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "remove_unknown_requirement_coverage",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "requirement_id": "REQ-UNKNOWN-999",
            "reason": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
        }
    ]


def test_unknown_requirement_trace_candidate_repair_slice_runs_approved_task_to_convergence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(UNKNOWN_TRACE_SCRIPT_PATH),
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
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["slice_id"] == "evidence-unknown-trace-approved-candidate-repair-slice"
    assert payload["selected_task"] == {
        "task_id": "TASK-CE-EV-IR-TRACE-UNKNOWN-REQUIREMENT",
        "target_agent": "EvidenceRepairAgent",
        "task_type": "repair_evidence_trace",
        "approval_status": "approved",
    }
    assert payload["candidate_delta"] == {
        "changed_ir_trace_element_ids": ["T001"],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    assert payload["convergence"]["before_findings"] == ["EV_IR_TRACE_UNKNOWN_REQUIREMENT"]
    assert payload["convergence"]["after_findings"] == []

    repaired_packet = json.loads(
        Path(payload["artifact_paths"]["repaired_candidate_packet"]).read_text(encoding="utf-8")
    )
    assert _transition_by_id(repaired_packet, "T001")["trace"]["requirements"] == [
        "REQ-START-001"
    ]

    review_export = json.loads(
        Path(payload["artifact_paths"]["candidate_review_packet_export"]).read_text(
            encoding="utf-8"
        )
    )
    validate_candidate_review_packet_export(review_export)
    assert review_export["review_packet"]["finding_chains"][0]["repair"]["actions"] == [
        {
            "action": "remove_unknown_requirement_trace",
            "ir_element_id": "T001",
            "requirement_id": "REQ-UNKNOWN-999",
            "reason": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
        }
    ]
