from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

from well_harness.agent_execution_shell import validate_execution_evidence_package
from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_task_contract import validate_agent_task_package


PROJECT_ROOT = Path(__file__).parents[1]
AGENT_OUTPUT_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "agent_output_contract_v0_1.json"


def _load_logic_ir_packet() -> dict:
    assert AGENT_OUTPUT_FIXTURE_PATH.exists(), f"missing fixture: {AGENT_OUTPUT_FIXTURE_PATH}"
    return json.loads(AGENT_OUTPUT_FIXTURE_PATH.read_text(encoding="utf-8"))


def _repair_loop_module():
    try:
        return importlib.import_module("well_harness.agent_repair_loop")
    except ModuleNotFoundError as exc:
        pytest.fail(f"missing agent_repair_loop module: {exc}")


def _approval(task_id: str) -> dict:
    return {
        "approval_id": "APPROVAL-REPAIR-001",
        "approved": True,
        "task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-20T00:00:00Z",
    }


def _transition_by_id(packet: dict, transition_id: str) -> dict:
    for transition in packet["agent_output"]["payload"]["logic_ir"]["transitions"]:
        if transition["id"] == transition_id:
            return transition
    raise AssertionError(f"missing transition {transition_id}")


def _safety_clean_packet() -> dict:
    packet = _load_logic_ir_packet()
    _transition_by_id(packet, "T004")["priority"] = "safety"
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": True,
        "failed_checks": [],
    }
    return packet


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


def test_repair_loop_blocks_safety_finding_without_explicit_approval() -> None:
    repair_loop = _repair_loop_module()
    packet = _load_logic_ir_packet()

    result = repair_loop.run_safety_guardian_repair_loop(packet)

    assert result["status"] == "blocked_missing_approval"
    assert result["selected_finding"]["code"] == "CHECK_SAFETY_PRIORITY_001"
    assert result["before"]["safety_guardian"]["status"] == "fail"
    assert result["before"]["task_package"]["chief_engineer"]["status"] == "tasks_ready_for_review"
    evidence = result["before"]["execution_evidence_package"]
    validate_execution_evidence_package(evidence)
    assert evidence["executor"]["status"] == "blocked_missing_approval"
    assert "after" not in result
    assert _transition_by_id(packet, "T004")["priority"] == "normal"


def test_approved_repair_loop_converges_safety_priority_finding() -> None:
    repair_loop = _repair_loop_module()
    packet = _load_logic_ir_packet()

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-SAFETY-PRIORITY-001"),
    )

    assert result["kind"] == "ai-fantui-safety-repair-loop"
    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "CHECK_SAFETY_PRIORITY_001",
        "severity": "critical",
        "transition_id": "T004",
        "task_id": "TASK-CE-CHECK-SAFETY-PRIORITY-001",
    }
    assert result["repair_actions"] == [
        {
            "action": "set_transition_priority",
            "transition_id": "T004",
            "from": "normal",
            "to": "safety",
            "reason": "CHECK_SAFETY_PRIORITY_001",
        }
    ]

    before = result["before"]
    assert before["safety_guardian"]["status"] == "fail"
    assert before["task_package"]["chief_engineer"]["status"] == "tasks_ready_for_review"
    assert before["execution_plan"]["planner"]["status"] == "dry_run_ready"
    assert before["execution_evidence_package"]["executor"]["status"] == "executed_limited"
    assert before["execution_evidence_package"]["approval"]["approved_task_id"] == (
        "TASK-CE-CHECK-SAFETY-PRIORITY-001"
    )
    assert before["execution_evidence_package"]["file_operations"] == [
        {
            "operation": "restricted_candidate_execution",
            "path": "src/well_harness/agent_repair_loop.py",
            "allowed": True,
            "execution_status": "executed",
            "reason": "approved by HumanReviewAgent for task TASK-CE-CHECK-SAFETY-PRIORITY-001",
        }
    ]

    repaired_packet = result["repaired_packet"]
    validate_agent_output_contract(repaired_packet)
    assert _transition_by_id(repaired_packet, "T004")["priority"] == "safety"
    assert _transition_by_id(packet, "T004")["priority"] == "normal"
    assert repaired_packet["agent_output"]["validation"] == {
        "schema_valid": True,
        "deterministic_checks_passed": True,
        "failed_checks": [],
    }
    assert repaired_packet["agent_output"]["boundary"] == packet["agent_output"]["boundary"]

    after = result["after"]
    assert after["safety_guardian"]["status"] == "pass"
    assert after["safety_guardian"]["findings"] == []
    assert after["evidence"]["status"] == "pass"
    assert after["evidence"]["findings"] == []
    validate_agent_task_package(after["task_package"])
    assert after["task_package"]["chief_engineer"]["status"] == "no_tasks_required"
    assert after["task_package"]["tasks"] == []
    assert after["execution_plan"]["planner"]["status"] == "no_task_available"
    validate_execution_evidence_package(after["execution_evidence_package"])
    assert after["execution_evidence_package"]["executor"]["status"] == "no_task_available"

    assert result["convergence"] == {
        "before_findings": ["CHECK_SAFETY_PRIORITY_001"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_repair_loop_converges_undefined_guard_signal_finding() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    packet["agent_output"]["payload"]["signals"] = [
        signal
        for signal in packet["agent_output"]["payload"]["signals"]
        if signal["name"] != "EGT_START_LIMIT"
    ]
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [],
    }

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-UNDEFINED-SIGNAL-001"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "CHECK_UNDEFINED_SIGNAL_001",
        "severity": "high",
        "transition_id": "T004",
        "signal_name": "EGT_START_LIMIT",
        "task_id": "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
    }
    assert result["repair_actions"] == [
        {
            "action": "add_candidate_signal_stub",
            "signal_name": "EGT_START_LIMIT",
            "transition_id": "T004",
            "reason": "CHECK_UNDEFINED_SIGNAL_001",
        }
    ]
    assert result["convergence"] == {
        "before_findings": ["CHECK_UNDEFINED_SIGNAL_001"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    repaired_signals = result["repaired_packet"]["agent_output"]["payload"]["signals"]
    assert {
        "name": "EGT_START_LIMIT",
        "type": "unknown",
        "source": "SafetyGuardianRepairAgent",
        "review_required": True,
    } in repaired_signals


def test_approved_repair_loop_converges_transition_endpoint_finding() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    packet["agent_output"]["payload"]["logic_ir"]["transitions"].append(
        {
            "id": "T_BAD_ENDPOINT",
            "from": "FUEL_ON",
            "to": "MISSING_STATE",
            "guard": "EGT_valid == false",
            "guard_signals": [],
            "priority": "normal",
            "trace": {"requirements": ["REQ-SAFE-001"]},
        }
    )

    report = run_safety_guardian_checks(packet)
    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "CHECK_TRANSITION_ENDPOINT_001"

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-TRANSITION-ENDPOINT-001"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "CHECK_TRANSITION_ENDPOINT_001",
        "severity": "high",
        "transition_id": "T_BAD_ENDPOINT",
        "endpoint": "to",
        "state_id": "MISSING_STATE",
        "task_id": "TASK-CE-CHECK-TRANSITION-ENDPOINT-001",
    }
    assert result["repair_actions"] == [
        {
            "action": "add_candidate_state_stub",
            "state_id": "MISSING_STATE",
            "transition_id": "T_BAD_ENDPOINT",
            "endpoint": "to",
            "reason": "CHECK_TRANSITION_ENDPOINT_001",
        }
    ]
    repaired_states = result["repaired_packet"]["agent_output"]["payload"]["logic_ir"]["states"]
    assert "MISSING_STATE" in repaired_states
    assert "MISSING_STATE" not in packet["agent_output"]["payload"]["logic_ir"]["states"]
    assert result["after"]["safety_guardian"]["status"] == "pass"
    assert result["convergence"] == {
        "before_findings": ["CHECK_TRANSITION_ENDPOINT_001"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_repair_loop_converges_unreachable_state_finding() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    packet["agent_output"]["payload"]["logic_ir"]["states"].append("UNREACHABLE_REVIEW")

    report = run_safety_guardian_checks(packet)
    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "CHECK_UNREACHABLE_STATE_001"

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-UNREACHABLE-STATE-001"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "CHECK_UNREACHABLE_STATE_001",
        "severity": "high",
        "state_id": "UNREACHABLE_REVIEW",
        "initial_state": "IDLE",
        "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
    }
    assert result["repair_actions"] == [
        {
            "action": "remove_candidate_state_stub",
            "state_id": "UNREACHABLE_REVIEW",
            "initial_state": "IDLE",
            "reason": "CHECK_UNREACHABLE_STATE_001",
        }
    ]
    repaired_states = result["repaired_packet"]["agent_output"]["payload"]["logic_ir"]["states"]
    assert "UNREACHABLE_REVIEW" not in repaired_states
    assert "UNREACHABLE_REVIEW" in packet["agent_output"]["payload"]["logic_ir"]["states"]
    assert result["after"]["safety_guardian"]["status"] == "pass"
    assert result["convergence"] == {
        "before_findings": ["CHECK_UNREACHABLE_STATE_001"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_repair_loop_converges_output_command_conflict_finding() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    packet["agent_output"]["payload"]["logic_ir"]["transitions"].extend(
        [
            {
                "id": "T_CONFLICT_CLOSE",
                "from": "FUEL_ON",
                "to": "ABORTED",
                "guard": "reverse_request == true",
                "guard_signals": [],
                "priority": "normal",
                "action": {"fuel_valve": "closed"},
                "trace": {"requirements": ["REQ-SAFE-001"]},
            },
            {
                "id": "T_CONFLICT_OPEN",
                "from": "FUEL_ON",
                "to": "ABORTED",
                "guard": "reverse_request == true",
                "guard_signals": [],
                "priority": "normal",
                "action": {"fuel_valve": "open"},
                "trace": {"requirements": ["REQ-SAFE-001"]},
            },
        ]
    )

    report = run_safety_guardian_checks(packet)
    codes = [finding["code"] for finding in report["findings"]]
    assert "CHECK_OUTPUT_COMMAND_CONFLICT_001" in codes

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        "severity": "critical",
        "state_id": "FUEL_ON",
        "transition_ids": "T_CONFLICT_CLOSE,T_CONFLICT_OPEN",
        "signal_name": "fuel_valve",
        "left_value": "closed",
        "right_value": "open",
        "task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
    }
    assert result["repair_actions"] == [
        {
            "action": "set_conflicting_transition_priority",
            "transition_id": "T_CONFLICT_OPEN",
            "paired_transition_id": "T_CONFLICT_CLOSE",
            "signal_name": "fuel_valve",
            "from": "normal",
            "to": "safety",
            "reason": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        }
    ]
    assert _transition_by_id(result["repaired_packet"], "T_CONFLICT_OPEN")["priority"] == (
        "safety"
    )
    assert _transition_by_id(packet, "T_CONFLICT_OPEN")["priority"] == "normal"
    assert result["after"]["safety_guardian"]["status"] == "pass"
    assert result["convergence"] == {
        "before_findings": [
            "CHECK_TRANSITION_OVERLAP_001",
            "CHECK_OUTPUT_COMMAND_CONFLICT_001",
        ],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_repair_loop_rejects_mismatched_task_approval() -> None:
    repair_loop = _repair_loop_module()
    packet = _load_logic_ir_packet()

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-SOME-OTHER-FINDING"),
    )

    assert result["status"] == "blocked_task_mismatch"
    assert result["before"]["execution_evidence_package"]["approval"]["status"] == "task_mismatch"
    assert "repaired_packet" not in result


def test_repair_loop_does_not_claim_convergence_when_evidence_still_fails() -> None:
    repair_loop = _repair_loop_module()
    packet = _load_logic_ir_packet()
    packet["agent_output"]["payload"]["simulation_results"][1]["status"] = "fail"

    result = repair_loop.run_safety_guardian_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-SAFETY-PRIORITY-001"),
    )

    assert result["status"] == "needs_followup"
    assert result["after"]["safety_guardian"]["status"] == "pass"
    assert result["after"]["evidence"]["status"] == "fail"
    assert result["after"]["task_package"]["chief_engineer"]["status"] == "tasks_ready_for_review"
    assert result["after"]["task_package"]["tasks"][0]["task_id"] == (
        "TASK-CE-EV-SIMULATION-RESULT-FAILED"
    )
    assert result["convergence"]["after_findings"] == ["EV_SIMULATION_RESULT_FAILED"]


def test_evidence_repair_loop_blocks_failed_simulation_without_explicit_approval() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")["status"] = "fail"

    result = repair_loop.run_evidence_agent_repair_loop(packet)

    assert result["kind"] == "ai-fantui-evidence-repair-loop"
    assert result["status"] == "blocked_missing_approval"
    assert result["selected_finding"] == {
        "code": "EV_SIMULATION_RESULT_FAILED",
        "severity": "high",
        "scenario_id": "TC-HOT-START-ABORT-001",
        "task_id": "TASK-CE-EV-SIMULATION-RESULT-FAILED",
    }
    assert result["before"]["safety_guardian"]["status"] == "pass"
    assert result["before"]["evidence"]["status"] == "fail"
    assert result["before"]["task_package"]["tasks"][0]["target_agent"] == "SimulationTestRepairAgent"
    assert result["before"]["execution_evidence_package"]["executor"]["status"] == "blocked_missing_approval"
    assert "after" not in result
    assert _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")["status"] == "fail"


def test_approved_evidence_repair_loop_converges_failed_simulation_result() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")["status"] = "fail"

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-EV-SIMULATION-RESULT-FAILED"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"]["code"] == "EV_SIMULATION_RESULT_FAILED"
    assert result["repair_actions"] == [
        {
            "action": "set_simulation_result_status",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "from": "fail",
            "to": "pass",
            "reason": "EV_SIMULATION_RESULT_FAILED",
        }
    ]
    assert result["before"]["execution_evidence_package"]["executor"]["status"] == "executed_limited"
    assert result["before"]["execution_evidence_package"]["approval"]["approved_task_id"] == (
        "TASK-CE-EV-SIMULATION-RESULT-FAILED"
    )
    repaired_packet = result["repaired_packet"]
    validate_agent_output_contract(repaired_packet)
    assert _simulation_result_by_id(repaired_packet, "TC-HOT-START-ABORT-001")["status"] == "pass"
    assert _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")["status"] == "fail"
    assert repaired_packet["agent_output"]["validation"] == {
        "schema_valid": True,
        "deterministic_checks_passed": True,
        "failed_checks": [],
    }
    assert result["after"]["safety_guardian"]["status"] == "pass"
    assert result["after"]["evidence"]["status"] == "pass"
    assert result["after"]["task_package"]["chief_engineer"]["status"] == "no_tasks_required"
    assert result["after"]["execution_plan"]["planner"]["status"] == "no_task_available"
    assert result["after"]["execution_evidence_package"]["executor"]["status"] == "no_task_available"
    assert result["convergence"] == {
        "before_findings": ["EV_SIMULATION_RESULT_FAILED"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_evidence_repair_loop_converges_missing_simulation_result() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    packet["agent_output"]["payload"]["simulation_results"] = [
        {"scenario_id": "TC-NORMAL-START-001", "status": "pass"}
    ]

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-EV-TEST-RESULT-MISSING"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "EV_TEST_RESULT_MISSING",
        "severity": "high",
        "scenario_id": "TC-HOT-START-ABORT-001",
        "task_id": "TASK-CE-EV-TEST-RESULT-MISSING",
    }
    assert result["repair_actions"] == [
        {
            "action": "add_simulation_result",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "status": "pass",
            "reason": "EV_TEST_RESULT_MISSING",
        }
    ]
    assert _simulation_result_by_id(result["repaired_packet"], "TC-HOT-START-ABORT-001") == {
        "scenario_id": "TC-HOT-START-ABORT-001",
        "status": "pass",
    }
    assert result["after"]["evidence"]["status"] == "pass"
    assert result["convergence"]["after_findings"] == []


def test_approved_evidence_repair_loop_converges_boundary_review_requirement() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    evidence_result = _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")
    evidence_result["status"] = "pass"
    evidence_result["boundary_review_required"] = True

    report = run_evidence_agent_checks(packet)
    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "EV_BOUNDARY_RESULT_REVIEW_REQUIRED"

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-EV-BOUNDARY-REVIEW-001"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "EV_BOUNDARY_RESULT_REVIEW_REQUIRED",
        "severity": "high",
        "scenario_id": "TC-HOT-START-ABORT-001",
        "task_id": "TASK-CE-EV-BOUNDARY-REVIEW-001",
    }
    assert result["repair_actions"] == [
        {
            "action": "record_candidate_boundary_review",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "from": "missing",
            "to": "reviewed_candidate_only",
            "reason": "EV_BOUNDARY_RESULT_REVIEW_REQUIRED",
        }
    ]
    repaired_result = _simulation_result_by_id(
        result["repaired_packet"],
        "TC-HOT-START-ABORT-001",
    )
    assert repaired_result["boundary_review"] == {
        "status": "reviewed_candidate_only",
        "reviewed_by": "EvidenceRepairAgent",
        "truth_effect": "none",
        "controller_truth_modified": False,
        "certification_claim": "none",
    }
    assert result["after"]["evidence"]["status"] == "pass"
    assert result["convergence"] == {
        "before_findings": ["EV_BOUNDARY_RESULT_REVIEW_REQUIRED"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_evidence_repair_loop_converges_unknown_requirement_coverage() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    scenario = _test_scenario_by_id(packet, "TC-HOT-START-ABORT-001")
    scenario["covers"] = ["REQ-SAFE-001", "REQ-UNKNOWN-999"]

    report = run_evidence_agent_checks(packet)
    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "EV_TEST_COVERS_UNKNOWN_REQUIREMENT"

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
        "severity": "warning",
        "scenario_id": "TC-HOT-START-ABORT-001",
        "requirement_id": "REQ-UNKNOWN-999",
        "task_id": "TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT",
    }
    assert result["repair_actions"] == [
        {
            "action": "remove_unknown_requirement_coverage",
            "scenario_id": "TC-HOT-START-ABORT-001",
            "requirement_id": "REQ-UNKNOWN-999",
            "reason": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
        }
    ]
    repaired_scenario = _test_scenario_by_id(
        result["repaired_packet"],
        "TC-HOT-START-ABORT-001",
    )
    assert repaired_scenario["covers"] == ["REQ-SAFE-001"]
    assert _test_scenario_by_id(packet, "TC-HOT-START-ABORT-001")["covers"] == [
        "REQ-SAFE-001",
        "REQ-UNKNOWN-999",
    ]
    assert result["after"]["evidence"]["status"] == "pass"
    assert result["convergence"] == {
        "before_findings": ["EV_TEST_COVERS_UNKNOWN_REQUIREMENT"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_approved_evidence_repair_loop_converges_unknown_requirement_trace() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    transition = _transition_by_id(packet, "T001")
    transition["trace"]["requirements"] = ["REQ-START-001", "REQ-UNKNOWN-999"]

    report = run_evidence_agent_checks(packet)
    assert report["status"] == "fail"
    assert report["findings"][0]["code"] == "EV_IR_TRACE_UNKNOWN_REQUIREMENT"

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-EV-IR-TRACE-UNKNOWN-REQUIREMENT"),
    )

    assert result["status"] == "converged"
    assert result["selected_finding"] == {
        "code": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
        "severity": "warning",
        "ir_element_id": "T001",
        "requirement_id": "REQ-UNKNOWN-999",
        "task_id": "TASK-CE-EV-IR-TRACE-UNKNOWN-REQUIREMENT",
    }
    assert result["repair_actions"] == [
        {
            "action": "remove_unknown_requirement_trace",
            "ir_element_id": "T001",
            "requirement_id": "REQ-UNKNOWN-999",
            "reason": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
        }
    ]
    repaired_transition = _transition_by_id(result["repaired_packet"], "T001")
    assert repaired_transition["trace"]["requirements"] == ["REQ-START-001"]
    assert _transition_by_id(packet, "T001")["trace"]["requirements"] == [
        "REQ-START-001",
        "REQ-UNKNOWN-999",
    ]
    assert result["after"]["evidence"]["status"] == "pass"
    assert result["convergence"] == {
        "before_findings": ["EV_IR_TRACE_UNKNOWN_REQUIREMENT"],
        "after_findings": [],
        "task_package_status": "no_tasks_required",
        "execution_plan_status": "no_task_available",
        "execution_evidence_status": "no_task_available",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def test_evidence_repair_loop_rejects_mismatched_task_approval() -> None:
    repair_loop = _repair_loop_module()
    packet = _safety_clean_packet()
    _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")["status"] = "fail"

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-CHECK-SAFETY-PRIORITY-001"),
    )

    assert result["status"] == "blocked_task_mismatch"
    assert result["before"]["execution_evidence_package"]["approval"]["status"] == "task_mismatch"
    assert "repaired_packet" not in result


def test_evidence_repair_loop_blocks_when_safety_findings_remain() -> None:
    repair_loop = _repair_loop_module()
    packet = _load_logic_ir_packet()
    _simulation_result_by_id(packet, "TC-HOT-START-ABORT-001")["status"] = "fail"

    result = repair_loop.run_evidence_agent_repair_loop(
        packet,
        approval=_approval("TASK-CE-EV-SIMULATION-RESULT-FAILED"),
    )

    assert result["status"] == "blocked_safety_findings"
    assert result["before"]["safety_guardian"]["status"] == "fail"
    assert result["convergence"] == {
        "before_findings": ["CHECK_SAFETY_PRIORITY_001", "EV_SIMULATION_RESULT_FAILED"],
        "after_findings": ["CHECK_SAFETY_PRIORITY_001", "EV_SIMULATION_RESULT_FAILED"],
        "task_package_status": "tasks_ready_for_review",
        "execution_plan_status": "dry_run_ready",
        "execution_evidence_status": "blocked_safety_findings",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
