"""Executable candidate-only development slices for multi-agent repair loops."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import jsonschema

from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_requirement_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_repair_loop import run_safety_guardian_repair_loop
from well_harness.agent_repair_loop import run_evidence_agent_repair_loop
from well_harness.agent_repair_loop import run_requirement_agent_repair_loop
from well_harness.agent_review_packet import (
    build_candidate_review_packet,
    build_candidate_review_packet_export,
    validate_candidate_review_packet,
    validate_candidate_review_packet_export,
)
from well_harness.agent_task_contract import build_chief_engineer_task_package


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT_OUTPUT_FIXTURE_PATH = (
    PROJECT_ROOT / "tests" / "fixtures" / "agent_output_contract_v0_1.json"
)
DEFAULT_ARTIFACT_DIR = Path("/tmp/ai-fantui-first-candidate-repair-slice")
DEFAULT_EVIDENCE_ARTIFACT_DIR = Path("/tmp/ai-fantui-evidence-candidate-repair-slice")
DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR = Path("/tmp/ai-fantui-approved-repair-slices")
DEFAULT_MISSING_TEST_RESULT_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-missing-test-result-candidate-repair-slice"
)
DEFAULT_REQUIREMENT_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-requirement-candidate-repair-slice"
)
DEFAULT_SAFETY_UNDEFINED_SIGNAL_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-safety-undefined-signal-candidate-repair-slice"
)
DEFAULT_SAFETY_TRANSITION_ENDPOINT_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-safety-transition-endpoint-candidate-repair-slice"
)
DEFAULT_SAFETY_UNREACHABLE_STATE_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-safety-unreachable-state-candidate-repair-slice"
)
DEFAULT_SAFETY_OUTPUT_COMMAND_CONFLICT_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-safety-output-command-conflict-candidate-repair-slice"
)
DEFAULT_EVIDENCE_BOUNDARY_REVIEW_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-evidence-boundary-review-candidate-repair-slice"
)
DEFAULT_EVIDENCE_UNKNOWN_REQUIREMENT_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-evidence-unknown-requirement-candidate-repair-slice"
)
DEFAULT_EVIDENCE_UNKNOWN_TRACE_ARTIFACT_DIR = Path(
    "/tmp/ai-fantui-evidence-unknown-trace-candidate-repair-slice"
)
SLICE_ID = "first-approved-candidate-repair-slice"
EVIDENCE_SLICE_ID = "evidence-approved-candidate-repair-slice"
MISSING_TEST_RESULT_SLICE_ID = "missing-test-result-approved-candidate-repair-slice"
REQUIREMENT_SLICE_ID = "requirement-approved-candidate-repair-slice"
SAFETY_UNDEFINED_SIGNAL_SLICE_ID = "safety-undefined-signal-approved-candidate-repair-slice"
SAFETY_TRANSITION_ENDPOINT_SLICE_ID = (
    "safety-transition-endpoint-approved-candidate-repair-slice"
)
SAFETY_UNREACHABLE_STATE_SLICE_ID = "safety-unreachable-state-approved-candidate-repair-slice"
SAFETY_OUTPUT_COMMAND_CONFLICT_SLICE_ID = (
    "safety-output-command-conflict-approved-candidate-repair-slice"
)
EVIDENCE_BOUNDARY_REVIEW_SLICE_ID = "evidence-boundary-review-approved-candidate-repair-slice"
EVIDENCE_UNKNOWN_REQUIREMENT_SLICE_ID = (
    "evidence-unknown-requirement-approved-candidate-repair-slice"
)
EVIDENCE_UNKNOWN_TRACE_SLICE_ID = "evidence-unknown-trace-approved-candidate-repair-slice"
APPROVED_REPAIR_SLICES_GATE_ID = "approved-repair-slices"
APPROVED_REPAIR_SLICES_SUMMARY_NAME = "approved_repair_slices_summary.json"
APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_repair_slices_summary_v0_1.schema.json"
)
APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_NAME = "approved_repair_slices_summary_v0_1.schema.json"
APPROVED_REPAIR_SLICES_SUMMARY_KIND = "ai-fantui-approved-repair-slices-summary"
EXPECTED_APPROVED_REPAIR_SLICE_ORDER = [SLICE_ID, EVIDENCE_SLICE_ID]
EVIDENCE_FAILED_SCENARIO_ID = "TC-HOT-START-ABORT-001"
UNKNOWN_REQUIREMENT_ID = "REQ-UNKNOWN-999"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _load_approved_repair_slices_summary_schema() -> dict[str, Any]:
    path = PROJECT_ROOT / "docs" / "json_schema" / APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_NAME
    return _load_json(path)


def validate_approved_repair_slices_summary(summary: dict[str, Any]) -> None:
    """Validate the external aggregate artifact schema."""
    try:
        jsonschema.Draft202012Validator(_load_approved_repair_slices_summary_schema()).validate(summary)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise ValueError(f"approved repair slices summary schema validation failed{location}: {exc.message}") from exc


def _approval(
    task_id: str,
    *,
    approval_id: str = "APPROVAL-FIRST-CANDIDATE-REPAIR-SLICE-001",
) -> dict[str, Any]:
    return {
        "approval_id": approval_id,
        "approved": True,
        "task_id": task_id,
        "approved_by": "HumanReviewAgent",
        "approved_at": "2026-05-20T00:00:00Z",
    }


def _transition_priority_by_id(packet: dict[str, Any]) -> dict[str, str]:
    transitions = (
        packet.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
        .get("transitions", [])
    )
    priorities: dict[str, str] = {}
    if not isinstance(transitions, list):
        return priorities
    for transition in transitions:
        if not isinstance(transition, dict):
            continue
        transition_id = transition.get("id")
        if isinstance(transition_id, str):
            priorities[transition_id] = str(transition.get("priority", ""))
    return priorities


def _changed_transition_ids(before_packet: dict[str, Any], after_packet: dict[str, Any]) -> list[str]:
    before = _transition_priority_by_id(before_packet)
    after = _transition_priority_by_id(after_packet)
    return [
        transition_id
        for transition_id in sorted(after)
        if before.get(transition_id) != after.get(transition_id)
    ]


def _finding_chain_statuses(review_packet: dict[str, Any]) -> list[str]:
    chains = review_packet.get("finding_chains", [])
    return [
        str(chain.get("status", ""))
        for chain in chains
        if isinstance(chain, dict)
    ]


def _simulation_result_status_by_id(packet: dict[str, Any]) -> dict[str, str]:
    results = packet.get("agent_output", {}).get("payload", {}).get("simulation_results", [])
    statuses: dict[str, str] = {}
    if not isinstance(results, list):
        return statuses
    for result in results:
        if not isinstance(result, dict):
            continue
        scenario_id = result.get("scenario_id")
        if isinstance(scenario_id, str):
            statuses[scenario_id] = str(result.get("status", ""))
    return statuses


def _changed_simulation_result_ids(before_packet: dict[str, Any], after_packet: dict[str, Any]) -> list[str]:
    before = _simulation_result_status_by_id(before_packet)
    after = _simulation_result_status_by_id(after_packet)
    return [
        scenario_id
        for scenario_id in sorted(after)
        if before.get(scenario_id) != after.get(scenario_id)
    ]


def _test_scenario_covers_by_id(packet: dict[str, Any]) -> dict[str, list[str]]:
    scenarios = packet.get("agent_output", {}).get("payload", {}).get("test_scenarios", [])
    covers_by_id: dict[str, list[str]] = {}
    if not isinstance(scenarios, list):
        return covers_by_id
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            continue
        scenario_id = scenario.get("id")
        covers = scenario.get("covers")
        if isinstance(scenario_id, str) and isinstance(covers, list):
            covers_by_id[scenario_id] = [
                str(item) for item in covers if isinstance(item, str)
            ]
    return covers_by_id


def _changed_test_scenario_ids(before_packet: dict[str, Any], after_packet: dict[str, Any]) -> list[str]:
    before = _test_scenario_covers_by_id(before_packet)
    after = _test_scenario_covers_by_id(after_packet)
    return [
        scenario_id
        for scenario_id in sorted(after)
        if before.get(scenario_id) != after.get(scenario_id)
    ]


def _ir_trace_requirements_by_id(packet: dict[str, Any]) -> dict[str, list[str]]:
    logic_ir = packet.get("agent_output", {}).get("payload", {}).get("logic_ir", {})
    if not isinstance(logic_ir, dict):
        return {}
    trace_by_id: dict[str, list[str]] = {}
    for key in ("transitions", "invariants"):
        values = logic_ir.get(key, [])
        if not isinstance(values, list):
            continue
        for element in values:
            if not isinstance(element, dict) or not isinstance(element.get("id"), str):
                continue
            trace = element.get("trace")
            requirements = trace.get("requirements") if isinstance(trace, dict) else []
            if isinstance(requirements, list):
                trace_by_id[element["id"]] = [
                    str(item) for item in requirements if isinstance(item, str)
                ]
    return trace_by_id


def _changed_ir_trace_element_ids(before_packet: dict[str, Any], after_packet: dict[str, Any]) -> list[str]:
    before = _ir_trace_requirements_by_id(before_packet)
    after = _ir_trace_requirements_by_id(after_packet)
    return [
        element_id
        for element_id in sorted(after)
        if before.get(element_id) != after.get(element_id)
    ]


def _state_ids(packet: dict[str, Any]) -> list[str]:
    logic_ir = packet.get("agent_output", {}).get("payload", {}).get("logic_ir", {})
    if not isinstance(logic_ir, dict):
        return []
    states = logic_ir.get("states", [])
    if not isinstance(states, list):
        return []
    state_ids: list[str] = []
    for state in states:
        if isinstance(state, str):
            state_ids.append(state)
        elif isinstance(state, dict) and isinstance(state.get("id"), str):
            state_ids.append(state["id"])
    return state_ids


def _changed_state_ids(before_packet: dict[str, Any], after_packet: dict[str, Any]) -> list[str]:
    before = set(_state_ids(before_packet))
    return [
        state_id
        for state_id in sorted(_state_ids(after_packet))
        if state_id not in before
    ]


def _state_membership_delta_ids(before_packet: dict[str, Any], after_packet: dict[str, Any]) -> list[str]:
    before = set(_state_ids(before_packet))
    after = set(_state_ids(after_packet))
    return sorted(before.symmetric_difference(after))


def _transition(packet: dict[str, Any], transition_id: str) -> dict[str, Any]:
    transitions = (
        packet.get("agent_output", {})
        .get("payload", {})
        .get("logic_ir", {})
        .get("transitions", [])
    )
    if not isinstance(transitions, list):
        raise RuntimeError("candidate packet has no transitions array")
    for transition in transitions:
        if isinstance(transition, dict) and transition.get("id") == transition_id:
            return transition
    raise RuntimeError(f"candidate packet missing transition {transition_id}")


def _simulation_result(packet: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    results = packet.get("agent_output", {}).get("payload", {}).get("simulation_results", [])
    if not isinstance(results, list):
        raise RuntimeError("candidate packet has no simulation_results array")
    for result in results:
        if isinstance(result, dict) and result.get("scenario_id") == scenario_id:
            return result
    raise RuntimeError(f"candidate packet missing simulation result {scenario_id}")


def _evidence_failed_simulation_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    _simulation_result(packet, EVIDENCE_FAILED_SCENARIO_ID)["status"] = "fail"
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "EvidenceAgent",
                "code": "EV_SIMULATION_RESULT_FAILED",
                "severity": "high",
                "scenario_id": EVIDENCE_FAILED_SCENARIO_ID,
                "message": "Seeded candidate evidence result is failed for repair-loop validation.",
            }
        ],
    }
    return packet


def _evidence_missing_test_result_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    results = packet["agent_output"]["payload"]["simulation_results"]
    packet["agent_output"]["payload"]["simulation_results"] = [
        result
        for result in results
        if result.get("scenario_id") != EVIDENCE_FAILED_SCENARIO_ID
    ]
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "EvidenceAgent",
                "code": "EV_TEST_RESULT_MISSING",
                "severity": "high",
                "scenario_id": EVIDENCE_FAILED_SCENARIO_ID,
                "message": "Seeded candidate evidence result is missing for repair-loop validation.",
            }
        ],
    }
    return packet


def _requirement_ambiguity_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    requirements = packet["agent_output"]["payload"]["requirements"]
    for requirement in requirements:
        if requirement.get("id") != "REQ-START-001":
            continue
        requirement["ambiguity"] = [
            "start command debounce time is not defined for candidate review"
        ]
        requirement["verifiability"] = "partial"
        break
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "RequirementAnalystAgent",
                "code": "REQ_AMBIGUITY_UNRESOLVED",
                "severity": "high",
                "requirement_id": "REQ-START-001",
                "message": "Seeded requirement ambiguity requires candidate repair-loop validation.",
            }
        ],
    }
    return packet


def _safety_undefined_signal_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    signals = packet["agent_output"]["payload"]["signals"]
    packet["agent_output"]["payload"]["signals"] = [
        signal
        for signal in signals
        if not (isinstance(signal, dict) and signal.get("name") == "EGT_START_LIMIT")
    ]
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "SafetyGuardianAgent",
                "code": "CHECK_UNDEFINED_SIGNAL_001",
                "severity": "high",
                "transition_id": "T004",
                "signal_name": "EGT_START_LIMIT",
                "message": "Seeded candidate guard references an undefined signal for repair-loop validation.",
            }
        ],
    }
    return packet


def _safety_transition_endpoint_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    transitions = packet["agent_output"]["payload"]["logic_ir"]["transitions"]
    transitions.append(
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
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "SafetyGuardianAgent",
                "code": "CHECK_TRANSITION_ENDPOINT_001",
                "severity": "high",
                "transition_id": "T_BAD_ENDPOINT",
                "endpoint": "to",
                "state_id": "MISSING_STATE",
                "message": (
                    "Seeded candidate transition targets an unknown state for "
                    "repair-loop validation."
                ),
            }
        ],
    }
    return packet


def _safety_unreachable_state_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    states = packet["agent_output"]["payload"]["logic_ir"]["states"]
    states.append("UNREACHABLE_REVIEW")
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "SafetyGuardianAgent",
                "code": "CHECK_UNREACHABLE_STATE_001",
                "severity": "high",
                "state_id": "UNREACHABLE_REVIEW",
                "initial_state": "IDLE",
                "message": (
                    "Seeded candidate state is unreachable from the initial "
                    "state for repair-loop validation."
                ),
            }
        ],
    }
    return packet


def _safety_output_command_conflict_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    transitions = packet["agent_output"]["payload"]["logic_ir"]["transitions"]
    transitions.extend(
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
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "SafetyGuardianAgent",
                "code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
                "severity": "critical",
                "state_id": "FUEL_ON",
                "transition_ids": "T_CONFLICT_CLOSE,T_CONFLICT_OPEN",
                "signal_name": "fuel_valve",
                "message": (
                    "Seeded candidate transitions command conflicting outputs "
                    "for repair-loop validation."
                ),
            }
        ],
    }
    return packet


def _evidence_boundary_review_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    result = _simulation_result(packet, EVIDENCE_FAILED_SCENARIO_ID)
    result["status"] = "pass"
    result["boundary_review_required"] = True
    result.pop("boundary_review", None)
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "EvidenceAgent",
                "code": "EV_BOUNDARY_RESULT_REVIEW_REQUIRED",
                "severity": "high",
                "scenario_id": EVIDENCE_FAILED_SCENARIO_ID,
                "message": (
                    "Seeded candidate evidence result requires an explicit "
                    "candidate-only boundary review."
                ),
            }
        ],
    }
    return packet


def _evidence_unknown_requirement_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    result = _simulation_result(packet, EVIDENCE_FAILED_SCENARIO_ID)
    result["status"] = "pass"
    result.pop("boundary_review_required", None)
    result.pop("boundary_review", None)
    scenarios = packet["agent_output"]["payload"]["test_scenarios"]
    for scenario in scenarios:
        if not isinstance(scenario, dict) or scenario.get("id") != EVIDENCE_FAILED_SCENARIO_ID:
            continue
        scenario["covers"] = ["REQ-SAFE-001", UNKNOWN_REQUIREMENT_ID]
        break
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "EvidenceAgent",
                "code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
                "severity": "warning",
                "scenario_id": EVIDENCE_FAILED_SCENARIO_ID,
                "requirement_id": UNKNOWN_REQUIREMENT_ID,
                "message": (
                    "Seeded candidate test scenario covers an unknown requirement "
                    "for repair-loop validation."
                ),
            }
        ],
    }
    return packet


def _evidence_unknown_trace_candidate(input_packet_path: Path) -> dict[str, Any]:
    packet = _load_json(input_packet_path)
    _transition(packet, "T004")["priority"] = "safety"
    transition = _transition(packet, "T001")
    transition["trace"] = {
        "requirements": ["REQ-START-001", UNKNOWN_REQUIREMENT_ID],
    }
    packet["agent_output"]["validation"] = {
        "schema_valid": True,
        "deterministic_checks_passed": False,
        "failed_checks": [
            {
                "agent": "EvidenceAgent",
                "code": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
                "severity": "warning",
                "ir_element_id": "T001",
                "requirement_id": UNKNOWN_REQUIREMENT_ID,
                "message": (
                    "Seeded candidate IR element traces an unknown requirement "
                    "for repair-loop validation."
                ),
            }
        ],
    }
    return packet


def run_first_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the first approved Chief Engineer task through a candidate repair loop."""
    before_packet = _load_json(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="FIRST_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("first candidate repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(str(selected_task["task_id"]))
    loop_result = run_safety_guardian_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(f"candidate repair loop did not converge: {loop_result.get('status')}")

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    changed_transition_ids = _changed_transition_ids(before_packet, repaired_packet)
    payload = {
        "status": "pass",
        "slice_id": SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_transition_ids": changed_transition_ids,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_evidence_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_EVIDENCE_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved Evidence finding through the candidate repair loop."""
    before_packet = _evidence_failed_simulation_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="EVIDENCE_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("evidence candidate repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-EVIDENCE-CANDIDATE-REPAIR-SLICE-001",
    )
    loop_result = run_evidence_agent_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(f"evidence candidate repair loop did not converge: {loop_result.get('status')}")

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=EVIDENCE_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": EVIDENCE_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_simulation_result_ids": _changed_simulation_result_ids(
                before_packet,
                repaired_packet,
            ),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_missing_test_result_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_MISSING_TEST_RESULT_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved missing-test-result finding through the candidate repair loop."""
    before_packet = _evidence_missing_test_result_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="MISSING_TEST_RESULT_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("missing test result candidate repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-MISSING-TEST-RESULT-CANDIDATE-REPAIR-SLICE-001",
    )
    loop_result = run_evidence_agent_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"missing test result candidate repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=MISSING_TEST_RESULT_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": MISSING_TEST_RESULT_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_simulation_result_ids": _changed_simulation_result_ids(
                before_packet,
                repaired_packet,
            ),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_requirement_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_REQUIREMENT_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved Requirement finding through the candidate repair loop."""
    before_packet = _requirement_ambiguity_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    requirements_report = run_requirement_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
            "requirements": requirements_report,
        },
        source_artifact_id="REQUIREMENT_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("requirement candidate repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-REQUIREMENT-AMBIGUITY-REPAIR-SLICE-001",
    )
    loop_result = run_requirement_agent_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"requirement candidate repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
            "requirements": requirements_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=REQUIREMENT_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": REQUIREMENT_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_requirement_ids": ["REQ-START-001"],
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "requirements_agent": loop_result["after"]["requirements"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_safety_undefined_signal_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_SAFETY_UNDEFINED_SIGNAL_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved undefined-signal Safety finding through a candidate repair loop."""
    before_packet = _safety_undefined_signal_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="SAFETY_UNDEFINED_SIGNAL_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("safety undefined-signal repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-SAFETY-UNDEFINED-SIGNAL-REPAIR-SLICE-001",
    )
    loop_result = run_safety_guardian_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"safety undefined-signal repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=SAFETY_UNDEFINED_SIGNAL_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": SAFETY_UNDEFINED_SIGNAL_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_signal_ids": ["EGT_START_LIMIT"],
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_safety_transition_endpoint_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_SAFETY_TRANSITION_ENDPOINT_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved transition-endpoint Safety finding through a candidate repair loop."""
    before_packet = _safety_transition_endpoint_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="SAFETY_TRANSITION_ENDPOINT_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("safety transition-endpoint repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-SAFETY-TRANSITION-ENDPOINT-REPAIR-SLICE-001",
    )
    loop_result = run_safety_guardian_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"safety transition-endpoint repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=SAFETY_TRANSITION_ENDPOINT_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": SAFETY_TRANSITION_ENDPOINT_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_state_ids": _changed_state_ids(before_packet, repaired_packet),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_safety_unreachable_state_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_SAFETY_UNREACHABLE_STATE_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved unreachable-state Safety finding through a candidate repair loop."""
    before_packet = _safety_unreachable_state_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="SAFETY_UNREACHABLE_STATE_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("safety unreachable-state repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-SAFETY-UNREACHABLE-STATE-REPAIR-SLICE-001",
    )
    loop_result = run_safety_guardian_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"safety unreachable-state repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=SAFETY_UNREACHABLE_STATE_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    changed_state_ids = _state_membership_delta_ids(before_packet, repaired_packet)
    payload = {
        "status": "pass",
        "slice_id": SAFETY_UNREACHABLE_STATE_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_state_ids": changed_state_ids,
            "removed_state_ids": changed_state_ids,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_safety_output_command_conflict_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_SAFETY_OUTPUT_COMMAND_CONFLICT_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved output-command conflict Safety finding through a candidate repair loop."""
    before_packet = _safety_output_command_conflict_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="SAFETY_OUTPUT_COMMAND_CONFLICT_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("safety output-command conflict repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-SAFETY-OUTPUT-COMMAND-CONFLICT-REPAIR-SLICE-001",
    )
    loop_result = run_safety_guardian_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"safety output-command conflict repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=SAFETY_OUTPUT_COMMAND_CONFLICT_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": SAFETY_OUTPUT_COMMAND_CONFLICT_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_transition_ids": _changed_transition_ids(
                before_packet,
                repaired_packet,
            ),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_evidence_boundary_review_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_EVIDENCE_BOUNDARY_REVIEW_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved Evidence boundary-review finding through a candidate repair loop."""
    before_packet = _evidence_boundary_review_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="EVIDENCE_BOUNDARY_REVIEW_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("evidence boundary-review repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-EVIDENCE-BOUNDARY-REVIEW-REPAIR-SLICE-001",
    )
    loop_result = run_evidence_agent_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"evidence boundary-review repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=EVIDENCE_BOUNDARY_REVIEW_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": EVIDENCE_BOUNDARY_REVIEW_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_boundary_review_result_ids": [EVIDENCE_FAILED_SCENARIO_ID],
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_evidence_unknown_requirement_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_EVIDENCE_UNKNOWN_REQUIREMENT_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved Evidence unknown-requirement finding through a candidate repair loop."""
    before_packet = _evidence_unknown_requirement_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="EVIDENCE_UNKNOWN_REQUIREMENT_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("evidence unknown-requirement repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-EVIDENCE-UNKNOWN-REQUIREMENT-REPAIR-SLICE-001",
    )
    loop_result = run_evidence_agent_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"evidence unknown-requirement repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=EVIDENCE_UNKNOWN_REQUIREMENT_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": EVIDENCE_UNKNOWN_REQUIREMENT_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_test_scenario_ids": _changed_test_scenario_ids(
                before_packet,
                repaired_packet,
            ),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def run_evidence_unknown_trace_candidate_repair_slice(
    *,
    artifact_dir: Path = DEFAULT_EVIDENCE_UNKNOWN_TRACE_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run the approved Evidence unknown-trace finding through a candidate repair loop."""
    before_packet = _evidence_unknown_trace_candidate(input_packet_path)
    validate_agent_output_contract(before_packet)
    safety_report = run_safety_guardian_checks(before_packet)
    evidence_report = run_evidence_agent_checks(before_packet)
    task_package = build_chief_engineer_task_package(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        source_artifact_id="EVIDENCE_UNKNOWN_TRACE_CANDIDATE_REPAIR_SLICE_v0.1",
    )
    if not task_package["tasks"]:
        raise RuntimeError("evidence unknown-trace repair slice requires a proposed Chief Engineer task")

    selected_task = task_package["tasks"][0]
    approval = _approval(
        str(selected_task["task_id"]),
        approval_id="APPROVAL-EVIDENCE-UNKNOWN-TRACE-REPAIR-SLICE-001",
    )
    loop_result = run_evidence_agent_repair_loop(
        before_packet,
        approval=approval,
    )
    if loop_result.get("status") != "converged":
        raise RuntimeError(
            f"evidence unknown-trace repair loop did not converge: {loop_result.get('status')}"
        )

    repaired_packet = copy.deepcopy(loop_result["repaired_packet"])
    validate_agent_output_contract(repaired_packet)
    review_packet = build_candidate_review_packet(
        {
            "logic_ir": before_packet,
            "safety_guardian": safety_report,
            "evidence": evidence_report,
        },
        task_package=task_package,
        execution_plan=loop_result["before"]["execution_plan"],
        execution_evidence_package=loop_result["before"]["execution_evidence_package"],
        repair_loop_results=[loop_result],
    )
    validate_candidate_review_packet(review_packet)
    review_export = build_candidate_review_packet_export(
        review_packet,
        export_id=EVIDENCE_UNKNOWN_TRACE_SLICE_ID,
        storage="artifact_file",
    )
    validate_candidate_review_packet_export(review_export)

    repaired_packet_path = artifact_dir / "repaired_candidate_packet.json"
    review_packet_path = artifact_dir / "candidate_review_packet_v0_1.json"
    review_export_path = artifact_dir / "candidate_review_packet_export_v0_1.json"
    loop_result_path = artifact_dir / "repair_loop_result.json"
    _write_json(repaired_packet_path, repaired_packet)
    _write_json(review_packet_path, review_packet)
    _write_json(review_export_path, review_export)
    _write_json(loop_result_path, loop_result)

    payload = {
        "status": "pass",
        "slice_id": EVIDENCE_UNKNOWN_TRACE_SLICE_ID,
        "selected_task": {
            "task_id": str(selected_task["task_id"]),
            "target_agent": str(selected_task["target_agent"]),
            "task_type": str(selected_task["task_type"]),
            "approval_status": "approved",
        },
        "repair_agent": {
            "agent_name": str(selected_task["target_agent"]),
            "status": "candidate_patch_generated",
            "action_count": len(loop_result.get("repair_actions", [])),
        },
        "candidate_delta": {
            "changed_ir_trace_element_ids": _changed_ir_trace_element_ids(
                before_packet,
                repaired_packet,
            ),
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
        "deterministic_gates": {
            "safety_guardian": loop_result["after"]["safety_guardian"]["status"],
            "evidence_agent": loop_result["after"]["evidence"]["status"],
            "candidate_review_packet": "pass",
            "candidate_review_packet_export": "pass",
            "local_gate": "pass",
        },
        "reviewer_status": str(review_packet["reviewer"]["status"]),
        "finding_chain_statuses": _finding_chain_statuses(review_packet),
        "convergence": loop_result["convergence"],
        "artifact_paths": {
            "repaired_candidate_packet": str(repaired_packet_path),
            "candidate_review_packet": str(review_packet_path),
            "candidate_review_packet_export": str(review_export_path),
            "repair_loop_result": str(loop_result_path),
        },
    }
    _write_json(artifact_dir / "slice_summary.json", payload)
    return payload


def _slice_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "slice_id": str(payload["slice_id"]),
        "status": str(payload["status"]),
        "selected_task_id": str(payload["selected_task"]["task_id"]),
        "selected_task_agent": str(payload["selected_task"]["target_agent"]),
        "reviewer_status": str(payload["reviewer_status"]),
        "finding_chain_statuses": list(payload.get("finding_chain_statuses", [])),
        "convergence": dict(payload.get("convergence", {})),
        "artifact_paths": dict(payload.get("artifact_paths", {})),
    }


def _expected_approved_repair_aggregate() -> dict[str, Any]:
    return {
        "slice_count": 2,
        "passed": 2,
        "converged": 2,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }


def _resolve_artifact_path(path_value: Any, summary_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return summary_path.parent / path


def _approved_repair_summary_path(
    *,
    artifact_dir: Path = DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
    summary_path: Path | None = None,
) -> Path:
    if summary_path is not None:
        return summary_path
    return artifact_dir / APPROVED_REPAIR_SLICES_SUMMARY_NAME


def verify_approved_repair_slices_artifact(
    *,
    artifact_dir: Path = DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
    summary_path: Path | None = None,
) -> dict[str, Any]:
    """Validate the aggregate approved-slices artifact plus child review exports."""
    resolved_summary_path = _approved_repair_summary_path(
        artifact_dir=artifact_dir,
        summary_path=summary_path,
    )
    summary_mismatches: list[str] = []
    child_mismatches: list[str] = []
    child_export_paths: list[str] = []
    summary: dict[str, Any] = {}

    try:
        summary = _load_json(resolved_summary_path)
    except (OSError, json.JSONDecodeError) as exc:
        summary_mismatches.append(f"summary could not be loaded: {exc}")
        return {
            "status": "fail",
            "gate_id": "",
            "kind": "",
            "summary_schema": APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID,
            "summary_schema_valid": False,
            "summary_valid": False,
            "child_review_exports_valid": False,
            "slice_order": [],
            "aggregate": {},
            "mismatches": summary_mismatches,
            "artifact_paths": {
                "summary": str(resolved_summary_path),
                "child_review_exports": child_export_paths,
            },
        }

    summary_schema_valid = True
    try:
        validate_approved_repair_slices_summary(summary)
    except ValueError as exc:
        summary_schema_valid = False
        summary_mismatches.append(str(exc))

    if summary.get("gate_id") != APPROVED_REPAIR_SLICES_GATE_ID:
        summary_mismatches.append(f"gate_id must be {APPROVED_REPAIR_SLICES_GATE_ID}")
    if summary.get("kind") != APPROVED_REPAIR_SLICES_SUMMARY_KIND:
        summary_mismatches.append(f"kind must be {APPROVED_REPAIR_SLICES_SUMMARY_KIND}")
    if summary.get("$schema") != APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID:
        summary_mismatches.append(f"$schema must be {APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID}")
    if summary.get("status") != "pass":
        summary_mismatches.append("summary.status must be pass")
    if summary.get("slice_order") != EXPECTED_APPROVED_REPAIR_SLICE_ORDER:
        summary_mismatches.append("slice_order must list Safety then Evidence slices")

    aggregate = summary.get("aggregate")
    expected_aggregate = _expected_approved_repair_aggregate()
    if not isinstance(aggregate, dict):
        summary_mismatches.append("aggregate must be an object")
        aggregate = {}
    else:
        for key, expected in expected_aggregate.items():
            if aggregate.get(key) != expected:
                if key == "open_findings":
                    summary_mismatches.append("aggregate.open_findings must be empty")
                else:
                    summary_mismatches.append(f"aggregate.{key} must be {expected!r}")

    deterministic_gates = summary.get("deterministic_gates")
    if not isinstance(deterministic_gates, dict):
        summary_mismatches.append("deterministic_gates must be an object")
    else:
        for gate_name, gate_status in deterministic_gates.items():
            if gate_status != "pass":
                summary_mismatches.append(f"deterministic_gates.{gate_name} must be pass")

    slices = summary.get("slices")
    if not isinstance(slices, list):
        summary_mismatches.append("slices must be an array")
        slices = []
    if len(slices) != len(EXPECTED_APPROVED_REPAIR_SLICE_ORDER):
        summary_mismatches.append("slices must contain exactly two child summaries")

    slice_ids = [
        item.get("slice_id")
        for item in slices
        if isinstance(item, dict)
    ]
    if slice_ids != EXPECTED_APPROVED_REPAIR_SLICE_ORDER:
        summary_mismatches.append("slices must be ordered Safety then Evidence")

    for item in slices:
        if not isinstance(item, dict):
            summary_mismatches.append("slice summary must be an object")
            continue
        slice_id = str(item.get("slice_id", ""))
        if item.get("status") != "pass":
            summary_mismatches.append(f"{slice_id}.status must be pass")
        if item.get("reviewer_status") != "converged":
            summary_mismatches.append(f"{slice_id}.reviewer_status must be converged")
        convergence = item.get("convergence")
        if not isinstance(convergence, dict):
            summary_mismatches.append(f"{slice_id}.convergence must be an object")
        else:
            if convergence.get("after_findings") != []:
                summary_mismatches.append(f"{slice_id}.convergence.after_findings must be empty")
            if convergence.get("controller_truth_modified") is not False:
                summary_mismatches.append(
                    f"{slice_id}.convergence.controller_truth_modified must be false"
                )
            if convergence.get("ui_layout_modified") is not False:
                summary_mismatches.append(f"{slice_id}.convergence.ui_layout_modified must be false")

        artifact_paths = item.get("artifact_paths")
        review_export_path = None
        if isinstance(artifact_paths, dict):
            review_export_path = _resolve_artifact_path(
                artifact_paths.get("candidate_review_packet_export"),
                resolved_summary_path,
            )
        if review_export_path is None:
            child_mismatches.append(
                f"{slice_id}.artifact_paths.candidate_review_packet_export is required"
            )
            continue

        child_export_paths.append(str(review_export_path))
        try:
            review_export = _load_json(review_export_path)
            validate_candidate_review_packet_export(review_export)
        except Exception as exc:  # noqa: BLE001 - checker must report all artifact validation failures.
            child_mismatches.append(f"{slice_id}.candidate_review_packet_export invalid: {exc}")
            continue
        review_packet = review_export.get("review_packet", {})
        if not isinstance(review_packet, dict):
            child_mismatches.append(f"{slice_id}.review_packet must be an object")
        elif review_packet.get("reviewer", {}).get("status") != "converged":
            child_mismatches.append(f"{slice_id}.review_packet.reviewer.status must be converged")

    mismatches = summary_mismatches + child_mismatches
    summary_valid = not summary_mismatches
    child_review_exports_valid = not child_mismatches
    status = "pass" if summary_valid and child_review_exports_valid else "fail"

    return {
        "status": status,
        "gate_id": str(summary.get("gate_id", "")),
        "kind": str(summary.get("kind", "")),
        "summary_schema": APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID,
        "summary_schema_valid": summary_schema_valid,
        "summary_valid": summary_valid,
        "child_review_exports_valid": child_review_exports_valid,
        "slice_order": list(summary.get("slice_order", [])),
        "aggregate": dict(aggregate),
        "mismatches": mismatches,
        "artifact_paths": {
            "summary": str(resolved_summary_path),
            "child_review_exports": child_export_paths,
        },
    }


def run_approved_repair_slices_gate(
    *,
    artifact_dir: Path = DEFAULT_APPROVED_REPAIR_SLICES_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    """Run Safety then Evidence approved candidate repair slices and summarize them."""
    safety_payload = run_first_candidate_repair_slice(
        artifact_dir=artifact_dir / "safety",
        input_packet_path=input_packet_path,
    )
    evidence_payload = run_evidence_candidate_repair_slice(
        artifact_dir=artifact_dir / "evidence",
        input_packet_path=input_packet_path,
    )
    slices = [_slice_summary(safety_payload), _slice_summary(evidence_payload)]
    open_findings: list[str] = []
    for item in slices:
        for finding in item["convergence"].get("after_findings", []):
            if isinstance(finding, str) and finding not in open_findings:
                open_findings.append(finding)

    passed_count = sum(1 for item in slices if item["status"] == "pass")
    converged_count = sum(1 for item in slices if item["reviewer_status"] == "converged")
    controller_truth_modified = any(
        item["convergence"].get("controller_truth_modified") is not False
        for item in slices
    )
    ui_layout_modified = any(
        item["convergence"].get("ui_layout_modified") is not False
        for item in slices
    )
    status = (
        "pass"
        if (
            passed_count == len(slices)
            and converged_count == len(slices)
            and not open_findings
            and not controller_truth_modified
            and not ui_layout_modified
        )
        else "fail"
    )
    summary_path = artifact_dir / APPROVED_REPAIR_SLICES_SUMMARY_NAME
    payload = {
        "$schema": APPROVED_REPAIR_SLICES_SUMMARY_SCHEMA_ID,
        "kind": APPROVED_REPAIR_SLICES_SUMMARY_KIND,
        "status": status,
        "gate_id": APPROVED_REPAIR_SLICES_GATE_ID,
        "slice_order": list(EXPECTED_APPROVED_REPAIR_SLICE_ORDER),
        "slices": slices,
        "deterministic_gates": {
            "safety_slice": "pass" if safety_payload.get("status") == "pass" else "fail",
            "evidence_slice": "pass" if evidence_payload.get("status") == "pass" else "fail",
            "review_packet_exports": "pass" if converged_count == len(slices) else "fail",
            "local_gate": status,
        },
        "aggregate": {
            "slice_count": len(slices),
            "passed": passed_count,
            "converged": converged_count,
            "open_findings": open_findings,
            "controller_truth_modified": controller_truth_modified,
            "ui_layout_modified": ui_layout_modified,
        },
        "artifact_paths": {
            "summary": str(summary_path),
            "safety_summary": str(artifact_dir / "safety" / "slice_summary.json"),
            "evidence_summary": str(artifact_dir / "evidence" / "slice_summary.json"),
        },
    }
    validate_approved_repair_slices_summary(payload)
    _write_json(summary_path, payload)
    return payload
