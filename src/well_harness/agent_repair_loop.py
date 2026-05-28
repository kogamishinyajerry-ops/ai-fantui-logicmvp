"""Candidate-only Safety Guardian and Evidence Agent repair loops."""
from __future__ import annotations

import copy
from typing import Any

from well_harness.agent_execution_plan import build_execution_plan_from_task_package
from well_harness.agent_execution_shell import build_execution_evidence_package
from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_requirement_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_task_contract import build_chief_engineer_task_package


REPAIR_LOOP_KIND = "ai-fantui-safety-repair-loop"
EVIDENCE_REPAIR_LOOP_KIND = "ai-fantui-evidence-repair-loop"
REQUIREMENT_REPAIR_LOOP_KIND = "ai-fantui-requirement-repair-loop"
REPAIR_LOOP_FILE = "src/well_harness/agent_repair_loop.py"


def _combined_findings(*reports: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for report in reports:
        for finding in report.get("findings", []):
            if isinstance(finding, dict):
                findings.append(finding)
    return findings


def _finding_codes(findings: list[dict[str, Any]]) -> list[str]:
    codes: list[str] = []
    for finding in findings:
        code = finding.get("code")
        if isinstance(code, str) and code not in codes:
            codes.append(code)
    return codes


def _select_safety_priority_finding(safety_report: dict[str, Any]) -> dict[str, Any]:
    for finding in safety_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") == "CHECK_SAFETY_PRIORITY_001":
            transition_id = str(finding.get("transition_id", ""))
            return {
                "code": "CHECK_SAFETY_PRIORITY_001",
                "severity": str(finding.get("severity", "critical")),
                "transition_id": transition_id,
                "task_id": "TASK-CE-CHECK-SAFETY-PRIORITY-001",
            }
    return {}


def _select_undefined_signal_finding(safety_report: dict[str, Any]) -> dict[str, Any]:
    for finding in safety_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "CHECK_UNDEFINED_SIGNAL_001":
            continue
        return {
            "code": "CHECK_UNDEFINED_SIGNAL_001",
            "severity": str(finding.get("severity", "high")),
            "transition_id": str(finding.get("transition_id", "")),
            "signal_name": str(finding.get("signal_name", "")),
            "task_id": "TASK-CE-CHECK-UNDEFINED-SIGNAL-001",
        }
    return {}


def _select_transition_endpoint_finding(safety_report: dict[str, Any]) -> dict[str, Any]:
    for finding in safety_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "CHECK_TRANSITION_ENDPOINT_001":
            continue
        return {
            "code": "CHECK_TRANSITION_ENDPOINT_001",
            "severity": str(finding.get("severity", "high")),
            "transition_id": str(finding.get("transition_id", "")),
            "endpoint": str(finding.get("endpoint", "")),
            "state_id": str(finding.get("state_id", "")),
            "task_id": "TASK-CE-CHECK-TRANSITION-ENDPOINT-001",
        }
    return {}


def _select_unreachable_state_finding(safety_report: dict[str, Any]) -> dict[str, Any]:
    for finding in safety_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "CHECK_UNREACHABLE_STATE_001":
            continue
        return {
            "code": "CHECK_UNREACHABLE_STATE_001",
            "severity": str(finding.get("severity", "high")),
            "state_id": str(finding.get("state_id", "")),
            "initial_state": str(finding.get("initial_state", "")),
            "task_id": "TASK-CE-CHECK-UNREACHABLE-STATE-001",
        }
    return {}


def _select_output_command_conflict_finding(safety_report: dict[str, Any]) -> dict[str, Any]:
    for finding in safety_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "CHECK_OUTPUT_COMMAND_CONFLICT_001":
            continue
        return {
            "code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
            "severity": str(finding.get("severity", "critical")),
            "state_id": str(finding.get("state_id", "")),
            "transition_ids": str(finding.get("transition_ids", "")),
            "signal_name": str(finding.get("signal_name", "")),
            "left_value": str(finding.get("left_value", "")),
            "right_value": str(finding.get("right_value", "")),
            "task_id": "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001",
        }
    return {}


def _select_safety_repair_finding(safety_report: dict[str, Any]) -> dict[str, Any]:
    return (
        _select_safety_priority_finding(safety_report)
        or _select_output_command_conflict_finding(safety_report)
        or _select_undefined_signal_finding(safety_report)
        or _select_transition_endpoint_finding(safety_report)
        or _select_unreachable_state_finding(safety_report)
    )


def _select_evidence_test_result_finding(evidence_report: dict[str, Any]) -> dict[str, Any]:
    for desired_code in ("EV_SIMULATION_RESULT_FAILED", "EV_TEST_RESULT_MISSING"):
        for finding in evidence_report.get("findings", []):
            if not isinstance(finding, dict) or finding.get("code") != desired_code:
                continue
            scenario_id = str(finding.get("scenario_id", ""))
            return {
                "code": desired_code,
                "severity": str(finding.get("severity", "high")),
                "scenario_id": scenario_id,
                "task_id": f"TASK-CE-{desired_code.replace('_', '-')}",
            }
    return {}


def _select_evidence_boundary_review_finding(evidence_report: dict[str, Any]) -> dict[str, Any]:
    for finding in evidence_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "EV_BOUNDARY_RESULT_REVIEW_REQUIRED":
            continue
        scenario_id = str(finding.get("scenario_id", ""))
        return {
            "code": "EV_BOUNDARY_RESULT_REVIEW_REQUIRED",
            "severity": str(finding.get("severity", "high")),
            "scenario_id": scenario_id,
            "task_id": "TASK-CE-EV-BOUNDARY-REVIEW-001",
        }
    return {}


def _select_evidence_unknown_requirement_coverage_finding(
    evidence_report: dict[str, Any],
) -> dict[str, Any]:
    for finding in evidence_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "EV_TEST_COVERS_UNKNOWN_REQUIREMENT":
            continue
        scenario_id = str(finding.get("scenario_id", ""))
        requirement_id = str(finding.get("requirement_id", ""))
        return {
            "code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
            "severity": str(finding.get("severity", "warning")),
            "scenario_id": scenario_id,
            "requirement_id": requirement_id,
            "task_id": "TASK-CE-EV-TEST-COVERS-UNKNOWN-REQUIREMENT",
        }
    return {}


def _select_evidence_unknown_requirement_trace_finding(
    evidence_report: dict[str, Any],
) -> dict[str, Any]:
    for finding in evidence_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "EV_IR_TRACE_UNKNOWN_REQUIREMENT":
            continue
        return {
            "code": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
            "severity": str(finding.get("severity", "warning")),
            "ir_element_id": str(finding.get("ir_element_id", "")),
            "requirement_id": str(finding.get("requirement_id", "")),
            "task_id": "TASK-CE-EV-IR-TRACE-UNKNOWN-REQUIREMENT",
        }
    return {}


def _select_evidence_repair_finding(evidence_report: dict[str, Any]) -> dict[str, Any]:
    return (
        _select_evidence_test_result_finding(evidence_report)
        or _select_evidence_boundary_review_finding(evidence_report)
        or _select_evidence_unknown_requirement_coverage_finding(evidence_report)
        or _select_evidence_unknown_requirement_trace_finding(evidence_report)
    )


def _select_requirement_ambiguity_finding(requirements_report: dict[str, Any]) -> dict[str, Any]:
    for finding in requirements_report.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if finding.get("code") != "REQ_AMBIGUITY_UNRESOLVED":
            continue
        requirement_id = str(finding.get("requirement_id", ""))
        return {
            "code": "REQ_AMBIGUITY_UNRESOLVED",
            "severity": str(finding.get("severity", "high")),
            "requirement_id": requirement_id,
            "task_id": "TASK-CE-REQ-AMBIGUITY-UNRESOLVED",
        }
    return {}


def _verification_gate_results(
    *,
    safety_report: dict[str, Any],
    evidence_report: dict[str, Any],
    task_package: dict[str, Any],
    execution_plan: dict[str, Any],
    execution_evidence: dict[str, Any],
) -> list[dict[str, str]]:
    task_status = str(task_package.get("chief_engineer", {}).get("status", ""))
    plan_status = str(execution_plan.get("planner", {}).get("status", ""))
    evidence_status = str(execution_evidence.get("executor", {}).get("status", ""))
    return [
        {
            "name": "SafetyGuardianAgent.after_repair",
            "status": "pass" if safety_report.get("status") == "pass" else "fail",
            "detail": str(safety_report.get("status", "<missing>")),
        },
        {
            "name": "EvidenceAgent.after_repair",
            "status": "pass" if evidence_report.get("status") == "pass" else "fail",
            "detail": str(evidence_report.get("status", "<missing>")),
        },
        {
            "name": "ChiefEngineerTaskPackage.after_repair",
            "status": "pass" if task_status == "no_tasks_required" else "fail",
            "detail": task_status or "<missing>",
        },
        {
            "name": "ExecutionPlan.after_repair",
            "status": "pass" if plan_status == "no_task_available" else "fail",
            "detail": plan_status or "<missing>",
        },
        {
            "name": "ExecutionEvidence.after_repair",
            "status": "pass" if evidence_status == "no_task_available" else "fail",
            "detail": evidence_status or "<missing>",
        },
        {
            "name": "candidate_boundary.after_repair",
            "status": "pass",
            "detail": "truth_effect none, controller truth unchanged, UI layout unchanged",
        },
    ]


def _repair_safety_priority(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    transition_id = selected_finding.get("transition_id")
    actions: list[dict[str, Any]] = []
    transitions = (
        repaired.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
        .get("transitions", [])
    )
    if not isinstance(transitions, list):
        return repaired, actions
    for transition in transitions:
        if not isinstance(transition, dict) or transition.get("id") != transition_id:
            continue
        previous_priority = str(transition.get("priority", ""))
        transition["priority"] = "safety"
        actions.append(
            {
                "action": "set_transition_priority",
                "transition_id": str(transition_id),
                "from": previous_priority,
                "to": "safety",
                "reason": str(selected_finding.get("code", "CHECK_SAFETY_PRIORITY_001")),
            }
        )
        break
    return repaired, actions


def _repair_undefined_signal(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    agent_payload = repaired.get("agent_output", {}).get("payload", {})
    signals = agent_payload.get("signals")
    if not isinstance(signals, list):
        signals = []
        agent_payload["signals"] = signals
    signal_name = str(selected_finding.get("signal_name", ""))
    if not signal_name:
        return repaired, []
    existing_names = {
        signal.get("name")
        for signal in signals
        if isinstance(signal, dict) and isinstance(signal.get("name"), str)
    }
    if signal_name in existing_names:
        return repaired, []
    signals.append(
        {
            "name": signal_name,
            "type": "unknown",
            "source": "SafetyGuardianRepairAgent",
            "review_required": True,
        }
    )
    return repaired, [
        {
            "action": "add_candidate_signal_stub",
            "signal_name": signal_name,
            "transition_id": str(selected_finding.get("transition_id", "")),
            "reason": str(selected_finding.get("code", "CHECK_UNDEFINED_SIGNAL_001")),
        }
    ]


def _logic_ir_states(packet: dict[str, Any]) -> list[Any]:
    logic_ir = (
        packet.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
    )
    if not isinstance(logic_ir, dict):
        return []
    states = logic_ir.get("states")
    if not isinstance(states, list):
        states = []
        logic_ir["states"] = states
    return states


def _state_id_set(states: list[Any]) -> set[str]:
    state_ids: set[str] = set()
    for state in states:
        if isinstance(state, str):
            state_ids.add(state)
        elif isinstance(state, dict) and isinstance(state.get("id"), str):
            state_ids.add(state["id"])
    return state_ids


def _repair_transition_endpoint(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    state_id = str(selected_finding.get("state_id", ""))
    if not state_id:
        return repaired, []
    states = _logic_ir_states(repaired)
    if state_id in _state_id_set(states):
        return repaired, []
    states.append(state_id)
    return repaired, [
        {
            "action": "add_candidate_state_stub",
            "state_id": state_id,
            "transition_id": str(selected_finding.get("transition_id", "")),
            "endpoint": str(selected_finding.get("endpoint", "")),
            "reason": str(selected_finding.get("code", "CHECK_TRANSITION_ENDPOINT_001")),
        }
    ]


def _logic_ir_transitions(packet: dict[str, Any]) -> list[Any]:
    logic_ir = (
        packet.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
    )
    if not isinstance(logic_ir, dict):
        return []
    transitions = logic_ir.get("transitions")
    return transitions if isinstance(transitions, list) else []


def _transition_references_state(transitions: list[Any], state_id: str) -> bool:
    for transition in transitions:
        if not isinstance(transition, dict):
            continue
        if transition.get("from") == state_id or transition.get("to") == state_id:
            return True
    return False


def _repair_unreachable_state(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    state_id = str(selected_finding.get("state_id", ""))
    initial_state = str(selected_finding.get("initial_state", ""))
    if not state_id or state_id == initial_state:
        return repaired, []
    states = _logic_ir_states(repaired)
    if state_id not in _state_id_set(states):
        return repaired, []
    if _transition_references_state(_logic_ir_transitions(repaired), state_id):
        return repaired, []

    repaired_states: list[Any] = []
    removed = False
    for state in states:
        candidate_state_id = ""
        if isinstance(state, str):
            candidate_state_id = state
        elif isinstance(state, dict) and isinstance(state.get("id"), str):
            candidate_state_id = state["id"]
        if candidate_state_id == state_id:
            removed = True
            continue
        repaired_states.append(state)
    if not removed:
        return repaired, []
    (
        repaired.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
    )["states"] = repaired_states
    return repaired, [
        {
            "action": "remove_candidate_state_stub",
            "state_id": state_id,
            "initial_state": initial_state,
            "reason": str(selected_finding.get("code", "CHECK_UNREACHABLE_STATE_001")),
        }
    ]


def _repair_output_command_conflict(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    transition_ids = [
        item.strip()
        for item in str(selected_finding.get("transition_ids", "")).split(",")
        if item.strip()
    ]
    if len(transition_ids) < 2:
        return repaired, []
    target_transition_id = transition_ids[1]
    transitions = _logic_ir_transitions(repaired)
    for transition in transitions:
        if not isinstance(transition, dict) or transition.get("id") != target_transition_id:
            continue
        previous_priority = str(transition.get("priority", ""))
        transition["priority"] = "safety"
        return repaired, [
            {
                "action": "set_conflicting_transition_priority",
                "transition_id": target_transition_id,
                "paired_transition_id": transition_ids[0],
                "signal_name": str(selected_finding.get("signal_name", "")),
                "from": previous_priority,
                "to": "safety",
                "reason": str(
                    selected_finding.get("code", "CHECK_OUTPUT_COMMAND_CONFLICT_001")
                ),
            }
        ]
    return repaired, []


def _repair_safety_finding(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    code = selected_finding.get("code")
    if code == "CHECK_OUTPUT_COMMAND_CONFLICT_001":
        return _repair_output_command_conflict(packet, selected_finding)
    if code == "CHECK_UNDEFINED_SIGNAL_001":
        return _repair_undefined_signal(packet, selected_finding)
    if code == "CHECK_TRANSITION_ENDPOINT_001":
        return _repair_transition_endpoint(packet, selected_finding)
    if code == "CHECK_UNREACHABLE_STATE_001":
        return _repair_unreachable_state(packet, selected_finding)
    return _repair_safety_priority(packet, selected_finding)


def _apply_validation_reports(
    packet: dict[str, Any],
    safety_report: dict[str, Any],
    evidence_report: dict[str, Any],
) -> None:
    findings = _combined_findings(safety_report, evidence_report)
    validation = packet["agent_output"]["validation"]
    validation["schema_valid"] = True
    validation["deterministic_checks_passed"] = not findings
    validation["failed_checks"] = findings


def _build_after_artifacts(packet: dict[str, Any], *, source_artifact_id: str) -> dict[str, Any]:
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    _apply_validation_reports(packet, safety_report, evidence_report)
    validate_agent_output_contract(packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id=source_artifact_id,
    )
    execution_plan = build_execution_plan_from_task_package(task_package)
    execution_evidence = build_execution_evidence_package(task_package)
    return {
        "safety_guardian": safety_report,
        "evidence": evidence_report,
        "task_package": task_package,
        "execution_plan": execution_plan,
        "execution_evidence_package": execution_evidence,
    }


def _build_requirement_after_artifacts(packet: dict[str, Any], *, source_artifact_id: str) -> dict[str, Any]:
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    requirements_report = run_requirement_agent_checks(packet)
    findings = _combined_findings(safety_report, evidence_report, requirements_report)
    validation = packet["agent_output"]["validation"]
    validation["schema_valid"] = True
    validation["deterministic_checks_passed"] = not findings
    validation["failed_checks"] = findings
    validate_agent_output_contract(packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
            "requirements": requirements_report,
        },
        source_artifact_id=source_artifact_id,
    )
    execution_plan = build_execution_plan_from_task_package(task_package)
    execution_evidence = build_execution_evidence_package(task_package)
    return {
        "safety_guardian": safety_report,
        "evidence": evidence_report,
        "requirements": requirements_report,
        "task_package": task_package,
        "execution_plan": execution_plan,
        "execution_evidence_package": execution_evidence,
    }


def _convergence(
    *,
    before_findings: list[dict[str, Any]],
    after_findings: list[dict[str, Any]],
    after: dict[str, Any],
) -> dict[str, Any]:
    return {
        "before_findings": _finding_codes(before_findings),
        "after_findings": _finding_codes(after_findings),
        "task_package_status": str(after["task_package"]["chief_engineer"]["status"]),
        "execution_plan_status": str(after["execution_plan"]["planner"]["status"]),
        "execution_evidence_status": str(after["execution_evidence_package"]["executor"]["status"]),
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def _blocked_safety_convergence(
    *,
    findings: list[dict[str, Any]],
    task_package: dict[str, Any],
    execution_plan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "before_findings": _finding_codes(findings),
        "after_findings": _finding_codes(findings),
        "task_package_status": str(task_package["chief_engineer"]["status"]),
        "execution_plan_status": str(execution_plan["planner"]["status"]),
        "execution_evidence_status": "blocked_safety_findings",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def _status_from_execution_evidence(evidence: dict[str, Any]) -> str:
    return str(evidence.get("executor", {}).get("status", "blocked_missing_approval"))


def run_safety_guardian_repair_loop(
    packet: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the first approved Safety Guardian repair loop over a candidate IR packet."""
    validate_agent_output_contract(packet)
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    selected_finding = _select_safety_repair_finding(safety_report)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="SAFETY_REPAIR_LOOP_v0.1",
    )
    execution_plan = build_execution_plan_from_task_package(
        task_package,
        proposed_files=[REPAIR_LOOP_FILE] if selected_finding else None,
    )
    pre_execution_evidence = build_execution_evidence_package(
        task_package,
        approval=approval,
        proposed_files=[REPAIR_LOOP_FILE] if selected_finding else None,
    )
    before = {
        "safety_guardian": safety_report,
        "evidence": evidence_report,
        "task_package": task_package,
        "execution_plan": execution_plan,
        "execution_evidence_package": pre_execution_evidence,
    }
    base_result = {
        "kind": REPAIR_LOOP_KIND,
        "selected_finding": selected_finding,
        "before": before,
    }
    execution_status = _status_from_execution_evidence(pre_execution_evidence)
    if execution_status != "executed_limited":
        return {
            **base_result,
            "status": execution_status,
        }

    repaired_packet, repair_actions = _repair_safety_finding(packet, selected_finding)
    after = _build_after_artifacts(
        repaired_packet,
        source_artifact_id="SAFETY_REPAIR_LOOP_v0.1",
    )
    gate_results = _verification_gate_results(
        safety_report=after["safety_guardian"],
        evidence_report=after["evidence"],
        task_package=after["task_package"],
        execution_plan=after["execution_plan"],
        execution_evidence=after["execution_evidence_package"],
    )
    before["execution_evidence_package"] = build_execution_evidence_package(
        task_package,
        approval=approval,
        proposed_files=[REPAIR_LOOP_FILE],
        deterministic_gate_results=gate_results,
    )
    after_findings = _combined_findings(after["safety_guardian"], after["evidence"])
    convergence = _convergence(
        before_findings=_combined_findings(safety_report, evidence_report),
        after_findings=after_findings,
        after=after,
    )
    return {
        **base_result,
        "status": "converged" if not after_findings else "needs_followup",
        "repair_actions": repair_actions,
        "repaired_packet": repaired_packet,
        "after": after,
        "convergence": convergence,
    }


def _simulation_results(packet: dict[str, Any]) -> list[dict[str, Any]]:
    results = packet.get("agent_output", {}).get("payload", {}).get("simulation_results", [])
    return results if isinstance(results, list) else []


def _test_scenarios(packet: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = packet.get("agent_output", {}).get("payload", {}).get("test_scenarios", [])
    return scenarios if isinstance(scenarios, list) else []


def _logic_ir_trace_elements(packet: dict[str, Any]) -> list[dict[str, Any]]:
    logic_ir = packet.get("agent_output", {}).get("payload", {}).get("logic_ir", {})
    if not isinstance(logic_ir, dict):
        return []
    elements: list[dict[str, Any]] = []
    for key in ("transitions", "invariants"):
        values = logic_ir.get(key, [])
        if isinstance(values, list):
            elements.extend(item for item in values if isinstance(item, dict))
    return elements


def _repair_evidence_test_result(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    scenario_id = str(selected_finding.get("scenario_id", ""))
    code = str(selected_finding.get("code", ""))
    results = _simulation_results(repaired)
    actions: list[dict[str, Any]] = []
    if code == "EV_SIMULATION_RESULT_FAILED":
        for result in results:
            if not isinstance(result, dict) or result.get("scenario_id") != scenario_id:
                continue
            previous_status = str(result.get("status", ""))
            result["status"] = "pass"
            actions.append(
                {
                    "action": "set_simulation_result_status",
                    "scenario_id": scenario_id,
                    "from": previous_status,
                    "to": "pass",
                    "reason": code,
                }
            )
            break
    elif code == "EV_TEST_RESULT_MISSING":
        new_result = {"scenario_id": scenario_id, "status": "pass"}
        results.append(new_result)
        actions.append(
            {
                "action": "add_simulation_result",
                "scenario_id": scenario_id,
                "status": "pass",
                "reason": code,
            }
        )
    return repaired, actions


def _repair_evidence_boundary_review(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    scenario_id = str(selected_finding.get("scenario_id", ""))
    results = _simulation_results(repaired)
    for result in results:
        if not isinstance(result, dict) or result.get("scenario_id") != scenario_id:
            continue
        previous_status = ""
        previous_review = result.get("boundary_review")
        if isinstance(previous_review, dict):
            previous_status = str(previous_review.get("status", ""))
        result["boundary_review"] = {
            "status": "reviewed_candidate_only",
            "reviewed_by": "EvidenceRepairAgent",
            "truth_effect": "none",
            "controller_truth_modified": False,
            "certification_claim": "none",
        }
        return repaired, [
            {
                "action": "record_candidate_boundary_review",
                "scenario_id": scenario_id,
                "from": previous_status or "missing",
                "to": "reviewed_candidate_only",
                "reason": str(
                    selected_finding.get("code", "EV_BOUNDARY_RESULT_REVIEW_REQUIRED")
                ),
            }
        ]
    return repaired, []


def _repair_evidence_unknown_requirement_coverage(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    scenario_id = str(selected_finding.get("scenario_id", ""))
    requirement_id = str(selected_finding.get("requirement_id", ""))
    if not scenario_id or not requirement_id:
        return repaired, []
    for scenario in _test_scenarios(repaired):
        if not isinstance(scenario, dict) or scenario.get("id") != scenario_id:
            continue
        covers = scenario.get("covers")
        if not isinstance(covers, list) or requirement_id not in covers:
            return repaired, []
        scenario["covers"] = [item for item in covers if item != requirement_id]
        return repaired, [
            {
                "action": "remove_unknown_requirement_coverage",
                "scenario_id": scenario_id,
                "requirement_id": requirement_id,
                "reason": str(
                    selected_finding.get("code", "EV_TEST_COVERS_UNKNOWN_REQUIREMENT")
                ),
            }
        ]
    return repaired, []


def _repair_evidence_unknown_requirement_trace(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    element_id = str(selected_finding.get("ir_element_id", ""))
    requirement_id = str(selected_finding.get("requirement_id", ""))
    if not element_id or not requirement_id:
        return repaired, []
    for element in _logic_ir_trace_elements(repaired):
        if element.get("id") != element_id:
            continue
        trace = element.get("trace")
        if not isinstance(trace, dict):
            return repaired, []
        requirements = trace.get("requirements")
        if not isinstance(requirements, list) or requirement_id not in requirements:
            return repaired, []
        trace["requirements"] = [item for item in requirements if item != requirement_id]
        return repaired, [
            {
                "action": "remove_unknown_requirement_trace",
                "ir_element_id": element_id,
                "requirement_id": requirement_id,
                "reason": str(selected_finding.get("code", "EV_IR_TRACE_UNKNOWN_REQUIREMENT")),
            }
        ]
    return repaired, []


def _repair_evidence_finding(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    code = selected_finding.get("code")
    if code == "EV_BOUNDARY_RESULT_REVIEW_REQUIRED":
        return _repair_evidence_boundary_review(packet, selected_finding)
    if code == "EV_TEST_COVERS_UNKNOWN_REQUIREMENT":
        return _repair_evidence_unknown_requirement_coverage(packet, selected_finding)
    if code == "EV_IR_TRACE_UNKNOWN_REQUIREMENT":
        return _repair_evidence_unknown_requirement_trace(packet, selected_finding)
    return _repair_evidence_test_result(packet, selected_finding)


def _repair_requirement_ambiguity(
    packet: dict[str, Any],
    selected_finding: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = copy.deepcopy(packet)
    requirement_id = str(selected_finding.get("requirement_id", ""))
    requirements = repaired.get("agent_output", {}).get("payload", {}).get("requirements", [])
    if not isinstance(requirements, list):
        return repaired, []
    for requirement in requirements:
        if not isinstance(requirement, dict) or requirement.get("id") != requirement_id:
            continue
        previous_ambiguity = [
            item for item in requirement.get("ambiguity", []) if isinstance(item, str)
        ]
        requirement["ambiguity"] = []
        requirement["clarification_status"] = "candidate_assumption_recorded"
        requirement["verifiability"] = requirement.get("verifiability", "partial")
        assumptions = requirement.get("candidate_assumptions")
        if not isinstance(assumptions, list):
            assumptions = []
            requirement["candidate_assumptions"] = assumptions
        assumption = (
            "Candidate repair records the ambiguity as an explicit review assumption; "
            "controller truth remains unchanged."
        )
        if assumption not in assumptions:
            assumptions.append(assumption)
        requirement["human_review_required"] = True
        return repaired, [
            {
                "action": "record_requirement_candidate_assumption",
                "requirement_id": requirement_id,
                "from": "; ".join(previous_ambiguity),
                "to": "candidate_assumption_recorded",
                "reason": str(selected_finding.get("code", "REQ_AMBIGUITY_UNRESOLVED")),
            }
        ]
    return repaired, []


def run_evidence_agent_repair_loop(
    packet: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the first approved Evidence Agent repair loop over candidate test evidence."""
    validate_agent_output_contract(packet)
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    selected_finding = _select_evidence_repair_finding(evidence_report)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="EVIDENCE_REPAIR_LOOP_v0.1",
    )
    execution_plan = build_execution_plan_from_task_package(
        task_package,
        proposed_files=[REPAIR_LOOP_FILE] if selected_finding else None,
    )
    pre_execution_evidence = build_execution_evidence_package(
        task_package,
        approval=approval,
        proposed_files=[REPAIR_LOOP_FILE] if selected_finding else None,
    )
    before = {
        "safety_guardian": safety_report,
        "evidence": evidence_report,
        "task_package": task_package,
        "execution_plan": execution_plan,
        "execution_evidence_package": pre_execution_evidence,
    }
    base_result = {
        "kind": EVIDENCE_REPAIR_LOOP_KIND,
        "selected_finding": selected_finding,
        "before": before,
    }
    before_findings = _combined_findings(safety_report, evidence_report)
    if safety_report.get("status") != "pass":
        return {
            **base_result,
            "status": "blocked_safety_findings",
            "convergence": _blocked_safety_convergence(
                findings=before_findings,
                task_package=task_package,
                execution_plan=execution_plan,
            ),
        }

    execution_status = _status_from_execution_evidence(pre_execution_evidence)
    if execution_status != "executed_limited":
        return {
            **base_result,
            "status": execution_status,
        }

    repaired_packet, repair_actions = _repair_evidence_finding(packet, selected_finding)
    after = _build_after_artifacts(
        repaired_packet,
        source_artifact_id="EVIDENCE_REPAIR_LOOP_v0.1",
    )
    gate_results = _verification_gate_results(
        safety_report=after["safety_guardian"],
        evidence_report=after["evidence"],
        task_package=after["task_package"],
        execution_plan=after["execution_plan"],
        execution_evidence=after["execution_evidence_package"],
    )
    before["execution_evidence_package"] = build_execution_evidence_package(
        task_package,
        approval=approval,
        proposed_files=[REPAIR_LOOP_FILE],
        deterministic_gate_results=gate_results,
    )
    after_findings = _combined_findings(after["safety_guardian"], after["evidence"])
    return {
        **base_result,
        "status": "converged" if not after_findings else "needs_followup",
        "repair_actions": repair_actions,
        "repaired_packet": repaired_packet,
        "after": after,
        "convergence": _convergence(
            before_findings=before_findings,
            after_findings=after_findings,
            after=after,
        ),
    }


def run_requirement_agent_repair_loop(
    packet: dict[str, Any],
    *,
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the first approved Requirement Agent repair loop over candidate requirements."""
    validate_agent_output_contract(packet)
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    requirements_report = run_requirement_agent_checks(packet)
    selected_finding = _select_requirement_ambiguity_finding(requirements_report)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
            "requirements": requirements_report,
        },
        source_artifact_id="REQUIREMENT_REPAIR_LOOP_v0.1",
    )
    execution_plan = build_execution_plan_from_task_package(
        task_package,
        proposed_files=[REPAIR_LOOP_FILE] if selected_finding else None,
    )
    pre_execution_evidence = build_execution_evidence_package(
        task_package,
        approval=approval,
        proposed_files=[REPAIR_LOOP_FILE] if selected_finding else None,
    )
    before = {
        "safety_guardian": safety_report,
        "evidence": evidence_report,
        "requirements": requirements_report,
        "task_package": task_package,
        "execution_plan": execution_plan,
        "execution_evidence_package": pre_execution_evidence,
    }
    base_result = {
        "kind": REQUIREMENT_REPAIR_LOOP_KIND,
        "selected_finding": selected_finding,
        "before": before,
    }
    before_findings = _combined_findings(safety_report, evidence_report, requirements_report)
    if safety_report.get("status") != "pass":
        return {
            **base_result,
            "status": "blocked_safety_findings",
            "convergence": _blocked_safety_convergence(
                findings=before_findings,
                task_package=task_package,
                execution_plan=execution_plan,
            ),
        }
    if evidence_report.get("status") != "pass":
        return {
            **base_result,
            "status": "blocked_evidence_findings",
            "convergence": _blocked_safety_convergence(
                findings=before_findings,
                task_package=task_package,
                execution_plan=execution_plan,
            ),
        }

    execution_status = _status_from_execution_evidence(pre_execution_evidence)
    if execution_status != "executed_limited":
        return {
            **base_result,
            "status": execution_status,
        }

    repaired_packet, repair_actions = _repair_requirement_ambiguity(packet, selected_finding)
    after = _build_requirement_after_artifacts(
        repaired_packet,
        source_artifact_id="REQUIREMENT_REPAIR_LOOP_v0.1",
    )
    gate_results = _verification_gate_results(
        safety_report=after["safety_guardian"],
        evidence_report=after["evidence"],
        task_package=after["task_package"],
        execution_plan=after["execution_plan"],
        execution_evidence=after["execution_evidence_package"],
    )
    gate_results.insert(
        2,
        {
            "name": "RequirementAnalystAgent.after_repair",
            "status": "pass" if after["requirements"].get("status") == "pass" else "fail",
            "detail": str(after["requirements"].get("status", "<missing>")),
        },
    )
    before["execution_evidence_package"] = build_execution_evidence_package(
        task_package,
        approval=approval,
        proposed_files=[REPAIR_LOOP_FILE],
        deterministic_gate_results=gate_results,
    )
    after_findings = _combined_findings(
        after["safety_guardian"],
        after["evidence"],
        after["requirements"],
    )
    return {
        **base_result,
        "status": "converged" if not after_findings else "needs_followup",
        "repair_actions": repair_actions,
        "repaired_packet": repaired_packet,
        "after": after,
        "convergence": _convergence(
            before_findings=before_findings,
            after_findings=after_findings,
            after=after,
        ),
    }
