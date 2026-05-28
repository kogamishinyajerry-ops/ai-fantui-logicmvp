"""Candidate-only multi-agent output contracts and deterministic checks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


AGENT_OUTPUT_CONTRACT_SCHEMA_ID = (
    "https://well-harness.local/json_schema/agent_output_contract_v0_1.schema.json"
)
AGENT_OUTPUT_CONTRACT_SCHEMA_NAME = "agent_output_contract_v0_1.schema.json"
CANDIDATE_BOUNDARY = {
    "truth_effect": "none",
    "controller_truth_modified": False,
    "certification_claim": "none",
}
REQUIRED_AGENT_OUTPUT_FIELDS = {
    "agent_name",
    "task_id",
    "input_artifacts",
    "output_artifacts",
    "assumptions",
    "open_issues",
    "confidence",
    "validation",
    "boundary",
    "human_review_required",
    "payload",
}


class AgentOutputContractError(ValueError):
    """Raised when a multi-agent packet violates candidate-only contracts."""


def _non_empty_text(value: Any, default: str) -> str:
    text = str(value).strip() if value not in (None, "") else ""
    return text or default


def _string_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    result: list[str] = []
    for value in values:
        if isinstance(value, str) and value.strip():
            result.append(value.strip())
    return result


def build_agent_output_packet(
    *,
    agent_name: str,
    task_id: str,
    input_artifacts: list[str],
    output_artifacts: list[str],
    candidate_state: str,
    payload: dict[str, Any],
    assumptions: list[str] | None = None,
    open_issues: list[str] | None = None,
    confidence_level: str = "medium",
    confidence_reason: str = "Candidate output generated from bounded project artifacts.",
    deterministic_checks_passed: bool = True,
    failed_checks: list[dict[str, Any]] | None = None,
    human_review_required: bool = False,
) -> dict[str, Any]:
    """Build a schema-valid candidate-only agent output packet."""
    packet = {
        "$schema": AGENT_OUTPUT_CONTRACT_SCHEMA_ID,
        "agent_output": {
            "agent_name": _non_empty_text(agent_name, "UnknownAgent"),
            "task_id": _non_empty_text(task_id, "TASK-UNSPECIFIED"),
            "input_artifacts": _string_list(input_artifacts) or ["artifact:unspecified-input"],
            "output_artifacts": _string_list(output_artifacts) or ["artifact:unspecified-output"],
            "assumptions": _string_list(assumptions or []),
            "open_issues": _string_list(open_issues or []),
            "confidence": {
                "level": confidence_level if confidence_level in {"low", "medium", "high"} else "medium",
                "reason": _non_empty_text(confidence_reason, "Candidate confidence was not provided."),
            },
            "validation": {
                "schema_valid": True,
                "deterministic_checks_passed": bool(deterministic_checks_passed),
                "failed_checks": failed_checks or [],
            },
            "boundary": {
                "candidate_state": candidate_state,
                **CANDIDATE_BOUNDARY,
            },
            "human_review_required": bool(human_review_required),
            "payload": payload,
        },
    }
    validate_agent_output_contract(packet)
    return packet


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_schema() -> dict[str, Any]:
    path = _project_root() / "docs" / "json_schema" / AGENT_OUTPUT_CONTRACT_SCHEMA_NAME
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_validate(payload: dict[str, Any]) -> None:
    try:
        import jsonschema
    except ModuleNotFoundError as exc:
        if exc.name not in {None, "jsonschema"}:
            raise
        _fallback_schema_validate(payload)
        return

    schema = _load_schema()
    try:
        jsonschema.Draft202012Validator(schema).validate(payload)
    except jsonschema.ValidationError as exc:
        path = ".".join(str(part) for part in exc.absolute_path)
        location = f" at {path}" if path else ""
        raise AgentOutputContractError(
            f"agent output schema validation failed{location}: {exc.message}"
        ) from exc


def _fallback_schema_validate(payload: dict[str, Any]) -> None:
    """Runtime-safe structural checks used when optional jsonschema is absent."""
    if payload.get("$schema") != AGENT_OUTPUT_CONTRACT_SCHEMA_ID:
        raise AgentOutputContractError("agent output $schema is invalid")
    agent_output = payload.get("agent_output")
    if not isinstance(agent_output, dict):
        raise AgentOutputContractError("agent_output must be an object")
    missing = sorted(REQUIRED_AGENT_OUTPUT_FIELDS - set(agent_output))
    if missing:
        raise AgentOutputContractError(
            f"agent_output missing required field(s): {', '.join(missing)}"
        )
    for field_name in ("input_artifacts", "output_artifacts", "assumptions", "open_issues"):
        if not isinstance(agent_output.get(field_name), list):
            raise AgentOutputContractError(f"agent_output.{field_name} must be a list")
    if not isinstance(agent_output.get("confidence"), dict):
        raise AgentOutputContractError("agent_output.confidence must be an object")
    if not isinstance(agent_output.get("validation"), dict):
        raise AgentOutputContractError("agent_output.validation must be an object")
    if not isinstance(agent_output.get("boundary"), dict):
        raise AgentOutputContractError("agent_output.boundary must be an object")
    if not isinstance(agent_output.get("human_review_required"), bool):
        raise AgentOutputContractError("agent_output.human_review_required must be a boolean")


def _agent_output(payload: dict[str, Any]) -> dict[str, Any]:
    agent_output = payload.get("agent_output")
    if not isinstance(agent_output, dict):
        raise AgentOutputContractError("agent_output must be an object")
    return agent_output


def _boundary(payload: dict[str, Any]) -> dict[str, Any]:
    boundary = _agent_output(payload).get("boundary")
    if not isinstance(boundary, dict):
        raise AgentOutputContractError("agent_output.boundary must be an object")
    return boundary


def validate_agent_output_contract(payload: dict[str, Any]) -> None:
    """Validate the schema and hard candidate-only boundary invariants."""
    _schema_validate(payload)
    boundary = _boundary(payload)
    for field_name, expected_value in CANDIDATE_BOUNDARY.items():
        if boundary.get(field_name) != expected_value:
            raise AgentOutputContractError(
                f"boundary.{field_name} must be {expected_value!r}"
            )


def _payload(payload: dict[str, Any]) -> dict[str, Any]:
    agent_payload = _agent_output(payload).get("payload")
    if not isinstance(agent_payload, dict):
        return {}
    return agent_payload


def _string_id_items(items: Any, key: str = "id") -> list[str]:
    if not isinstance(items, list):
        return []
    values: list[str] = []
    for item in items:
        if isinstance(item, dict) and isinstance(item.get(key), str):
            values.append(item[key])
        elif isinstance(item, str):
            values.append(item)
    return values


def _trace_requirements(element: dict[str, Any]) -> list[str]:
    trace = element.get("trace")
    if not isinstance(trace, dict):
        return []
    requirements = trace.get("requirements")
    if not isinstance(requirements, list):
        return []
    return [item for item in requirements if isinstance(item, str)]


def _logic_transitions(agent_payload: dict[str, Any]) -> list[dict[str, Any]]:
    logic_ir = agent_payload.get("logic_ir")
    if not isinstance(logic_ir, dict):
        return []
    transitions = logic_ir.get("transitions")
    if not isinstance(transitions, list):
        return []
    return [item for item in transitions if isinstance(item, dict)]


def _logic_ir(agent_payload: dict[str, Any]) -> dict[str, Any]:
    logic_ir = agent_payload.get("logic_ir")
    if not isinstance(logic_ir, dict):
        return {}
    return logic_ir


def _logic_state_ids(agent_payload: dict[str, Any]) -> list[str]:
    states = _logic_ir(agent_payload).get("states")
    if not isinstance(states, list):
        return []
    state_ids: list[str] = []
    for state in states:
        if isinstance(state, str):
            state_ids.append(state)
        elif isinstance(state, dict) and isinstance(state.get("id"), str):
            state_ids.append(state["id"])
    return state_ids


def _logic_invariants(agent_payload: dict[str, Any]) -> list[dict[str, Any]]:
    logic_ir = agent_payload.get("logic_ir")
    if not isinstance(logic_ir, dict):
        return []
    invariants = logic_ir.get("invariants")
    if not isinstance(invariants, list):
        return []
    return [item for item in invariants if isinstance(item, dict)]


def _requirements(agent_payload: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = agent_payload.get("requirements")
    if not isinstance(requirements, list):
        return []
    return [item for item in requirements if isinstance(item, dict)]


def _signal_names(agent_payload: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    signals = agent_payload.get("signals")
    if not isinstance(signals, list):
        return names
    for signal in signals:
        if isinstance(signal, dict) and isinstance(signal.get("name"), str):
            names.add(signal["name"])
        elif isinstance(signal, str):
            names.add(signal)
    return names


def _transition_guard_signature(transition: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    guard = transition.get("guard")
    guard_text = guard.strip() if isinstance(guard, str) else ""
    guard_signals = tuple(
        sorted(
            signal
            for signal in transition.get("guard_signals", [])
            if isinstance(signal, str)
        )
    )
    return (guard_text, guard_signals)


def _append_transition_overlap_findings(
    findings: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> None:
    transitions_by_source: dict[str, list[dict[str, Any]]] = {}
    for transition in transitions:
        source_state = transition.get("from")
        if isinstance(source_state, str):
            transitions_by_source.setdefault(source_state, []).append(transition)

    for source_state, source_transitions in transitions_by_source.items():
        for left_index, left in enumerate(source_transitions):
            left_signature = _transition_guard_signature(left)
            if left_signature == ("", ()):
                continue
            for right in source_transitions[left_index + 1 :]:
                if left_signature != _transition_guard_signature(right):
                    continue
                if left.get("priority") == "safety" or right.get("priority") == "safety":
                    continue
                left_id = str(left.get("id", "<unknown>"))
                right_id = str(right.get("id", "<unknown>"))
                findings.append(
                    {
                        "code": "CHECK_TRANSITION_OVERLAP_001",
                        "severity": "high",
                        "message": (
                            f"Transitions {left_id} and {right_id} leave {source_state} "
                            "with overlapping guards and no safety priority separation."
                        ),
                        "state_id": source_state,
                        "transition_ids": f"{left_id},{right_id}",
                    }
                )


def _append_transition_endpoint_findings(
    findings: list[dict[str, Any]],
    agent_payload: dict[str, Any],
    transitions: list[dict[str, Any]],
) -> None:
    state_ids = set(_logic_state_ids(agent_payload))
    if not state_ids:
        return
    for transition in transitions:
        transition_id = str(transition.get("id", "<unknown>"))
        for endpoint in ("from", "to"):
            state_id = transition.get(endpoint)
            if not isinstance(state_id, str) or state_id in state_ids:
                continue
            direction = "starts from" if endpoint == "from" else "targets"
            findings.append(
                {
                    "code": "CHECK_TRANSITION_ENDPOINT_001",
                    "severity": "high",
                    "message": f"Transition {transition_id} {direction} unknown state {state_id}.",
                    "transition_id": transition_id,
                    "endpoint": endpoint,
                    "state_id": state_id,
                }
            )


def _transition_action_values(transition: dict[str, Any]) -> dict[str, str]:
    raw_action = transition.get("action")
    if not isinstance(raw_action, dict):
        raw_action = transition.get("actions")
    if not isinstance(raw_action, dict):
        return {}
    return {
        str(key): str(value)
        for key, value in raw_action.items()
        if isinstance(key, str) and key.strip()
    }


def _append_output_command_conflict_findings(
    findings: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> None:
    transitions_by_source: dict[str, list[dict[str, Any]]] = {}
    for transition in transitions:
        source_state = transition.get("from")
        if isinstance(source_state, str):
            transitions_by_source.setdefault(source_state, []).append(transition)

    for source_state, source_transitions in transitions_by_source.items():
        for left_index, left in enumerate(source_transitions):
            left_actions = _transition_action_values(left)
            if not left_actions:
                continue
            left_signature = _transition_guard_signature(left)
            for right in source_transitions[left_index + 1 :]:
                if left_signature != _transition_guard_signature(right):
                    continue
                if left.get("priority") == "safety" or right.get("priority") == "safety":
                    continue
                right_actions = _transition_action_values(right)
                for signal_name in sorted(set(left_actions) & set(right_actions)):
                    left_value = left_actions[signal_name]
                    right_value = right_actions[signal_name]
                    if left_value == right_value:
                        continue
                    left_id = str(left.get("id", "<unknown>"))
                    right_id = str(right.get("id", "<unknown>"))
                    findings.append(
                        {
                            "code": "CHECK_OUTPUT_COMMAND_CONFLICT_001",
                            "severity": "critical",
                            "message": (
                                f"Transitions {left_id} and {right_id} can assign "
                                f"conflicting {signal_name} commands."
                            ),
                            "state_id": source_state,
                            "transition_ids": f"{left_id},{right_id}",
                            "signal_name": signal_name,
                            "left_value": left_value,
                            "right_value": right_value,
                        }
                    )


def _append_unreachable_state_findings(
    findings: list[dict[str, Any]],
    agent_payload: dict[str, Any],
    transitions: list[dict[str, Any]],
) -> None:
    state_ids = _logic_state_ids(agent_payload)
    if not state_ids:
        return
    initial_state = _logic_ir(agent_payload).get("initial_state")
    if not isinstance(initial_state, str):
        initial_state = state_ids[0]

    outgoing: dict[str, list[str]] = {state_id: [] for state_id in state_ids}
    state_id_set = set(state_ids)
    for transition in transitions:
        source_state = transition.get("from")
        target_state = transition.get("to")
        if isinstance(source_state, str) and isinstance(target_state, str):
            if source_state in state_id_set and target_state in state_id_set:
                outgoing.setdefault(source_state, []).append(target_state)

    reachable: set[str] = set()
    frontier = [initial_state]
    while frontier:
        state_id = frontier.pop()
        if state_id in reachable:
            continue
        reachable.add(state_id)
        frontier.extend(outgoing.get(state_id, []))

    for state_id in state_ids:
        if state_id in reachable:
            continue
        findings.append(
            {
                "code": "CHECK_UNREACHABLE_STATE_001",
                "severity": "high",
                "message": f"State {state_id} is not reachable from {initial_state}.",
                "state_id": state_id,
                "initial_state": initial_state,
            }
        )


def run_safety_guardian_checks(payload: dict[str, Any]) -> dict[str, Any]:
    """Run deterministic red-team checks over candidate logic IR."""
    validate_agent_output_contract(payload)
    agent_output = _agent_output(payload)
    agent_payload = _payload(payload)
    known_signals = _signal_names(agent_payload)
    transitions = _logic_transitions(agent_payload)
    findings: list[dict[str, Any]] = []

    for transition in transitions:
        transition_id = str(transition.get("id", "<unknown>"))
        guard_signals = [
            item
            for item in transition.get("guard_signals", [])
            if isinstance(item, str)
        ]
        for signal_name in guard_signals:
            if signal_name not in known_signals:
                findings.append(
                    {
                        "code": "CHECK_UNDEFINED_SIGNAL_001",
                        "severity": "high",
                        "message": f"Transition {transition_id} references undefined signal {signal_name}.",
                        "transition_id": transition_id,
                        "signal_name": signal_name,
                    }
                )
        if transition.get("safety_condition") is True and transition.get("priority") != "safety":
            findings.append(
                {
                    "code": "CHECK_SAFETY_PRIORITY_001",
                    "severity": "critical",
                    "message": f"Transition {transition_id} is safety-critical but lacks safety priority.",
                    "transition_id": transition_id,
                    "required_action": "Set priority to safety or add an explicit reviewed override.",
                }
            )

    _append_transition_endpoint_findings(findings, agent_payload, transitions)
    _append_transition_overlap_findings(findings, transitions)
    _append_output_command_conflict_findings(findings, transitions)
    _append_unreachable_state_findings(findings, agent_payload, transitions)

    return {
        "agent_name": "SafetyGuardianAgent",
        "source_agent_name": agent_output["agent_name"],
        "task_id": agent_output["task_id"],
        "status": "fail" if findings else "pass",
        "boundary": dict(agent_output["boundary"]),
        "findings": findings,
    }


def run_evidence_agent_checks(payload: dict[str, Any]) -> dict[str, Any]:
    """Build deterministic requirement -> IR -> test -> result evidence."""
    validate_agent_output_contract(payload)
    agent_output = _agent_output(payload)
    agent_payload = _payload(payload)

    requirement_ids = _string_id_items(agent_payload.get("requirements"))
    transitions = _logic_transitions(agent_payload)
    invariants = _logic_invariants(agent_payload)
    test_scenarios = [
        item
        for item in agent_payload.get("test_scenarios", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ]
    simulation_results = [
        item
        for item in agent_payload.get("simulation_results", [])
        if isinstance(item, dict) and isinstance(item.get("scenario_id"), str)
    ]
    result_scenario_ids = {item["scenario_id"] for item in simulation_results}
    findings: list[dict[str, Any]] = []

    ir_by_requirement: dict[str, list[str]] = {req_id: [] for req_id in requirement_ids}
    for element_kind, element in [
        *(("transition", item) for item in transitions),
        *(("invariant", item) for item in invariants),
    ]:
        element_id = str(element.get("id", "<unknown>"))
        trace_requirements = _trace_requirements(element)
        if not trace_requirements:
            findings.append(
                {
                    "code": "EV_IR_ELEMENT_MISSING_REQUIREMENT_TRACE",
                    "severity": "high",
                    "message": f"IR element {element_id} has no requirement trace.",
                    "ir_element_id": element_id,
                    "element_kind": element_kind,
                }
            )
        for req_id in trace_requirements:
            if req_id in ir_by_requirement:
                ir_by_requirement[req_id].append(element_id)
            else:
                findings.append(
                    {
                        "code": "EV_IR_TRACE_UNKNOWN_REQUIREMENT",
                        "severity": "warning",
                        "message": f"IR element {element_id} traces unknown requirement {req_id}.",
                        "requirement_id": req_id,
                        "ir_element_id": element_id,
                    }
                )

    tests_by_requirement: dict[str, list[str]] = {req_id: [] for req_id in requirement_ids}
    for scenario in test_scenarios:
        scenario_id = scenario["id"]
        covers = scenario.get("covers", [])
        if isinstance(covers, list):
            for req_id in covers:
                if isinstance(req_id, str) and req_id in tests_by_requirement:
                    tests_by_requirement[req_id].append(scenario_id)
                elif isinstance(req_id, str):
                    findings.append(
                        {
                            "code": "EV_TEST_COVERS_UNKNOWN_REQUIREMENT",
                            "severity": "warning",
                            "message": (
                                f"Test scenario {scenario_id} covers unknown requirement {req_id}."
                            ),
                            "scenario_id": scenario_id,
                            "requirement_id": req_id,
                        }
                    )
        if scenario_id not in result_scenario_ids:
            findings.append(
                {
                    "code": "EV_TEST_RESULT_MISSING",
                    "severity": "high",
                    "message": f"Test scenario {scenario_id} has no simulation result.",
                    "scenario_id": scenario_id,
                }
            )

    for result in simulation_results:
        status = str(result.get("status", "")).lower()
        scenario_id = result["scenario_id"]
        if status != "pass":
            findings.append(
                {
                    "code": "EV_SIMULATION_RESULT_FAILED",
                    "severity": "high",
                    "message": f"Simulation result for {scenario_id} is {status or '<missing>'}.",
                    "scenario_id": scenario_id,
                    "status": status or "<missing>",
                }
            )
            continue
        boundary_review = result.get("boundary_review")
        boundary_review_status = ""
        if isinstance(boundary_review, dict):
            boundary_review_status = str(boundary_review.get("status", ""))
        if (
            result.get("boundary_review_required") is True
            and boundary_review_status != "reviewed_candidate_only"
        ):
            findings.append(
                {
                    "code": "EV_BOUNDARY_RESULT_REVIEW_REQUIRED",
                    "severity": "high",
                    "message": (
                        f"Simulation result for {scenario_id} requires an explicit "
                        "candidate-only boundary review."
                    ),
                    "scenario_id": scenario_id,
                }
            )

    for req_id in requirement_ids:
        if not ir_by_requirement[req_id]:
            findings.append(
                {
                    "code": "EV_REQUIREMENT_NOT_TRACED_TO_IR",
                    "severity": "high",
                    "message": f"Requirement {req_id} has no IR trace.",
                    "requirement_id": req_id,
                }
            )
        if not tests_by_requirement[req_id]:
            findings.append(
                {
                    "code": "EV_REQUIREMENT_NOT_COVERED_BY_TEST",
                    "severity": "high",
                    "message": f"Requirement {req_id} has no covering test scenario.",
                    "requirement_id": req_id,
                }
            )

    trace_matrix = [
        {
            "requirement_id": req_id,
            "ir_elements": sorted(set(ir_by_requirement[req_id])),
            "test_cases": sorted(set(tests_by_requirement[req_id])),
            "result_statuses": [
                result["status"]
                for result in simulation_results
                if result["scenario_id"] in set(tests_by_requirement[req_id])
            ],
        }
        for req_id in requirement_ids
    ]
    return {
        "agent_name": "EvidenceAgent",
        "source_agent_name": agent_output["agent_name"],
        "task_id": agent_output["task_id"],
        "status": "fail" if findings else "pass",
        "boundary": dict(agent_output["boundary"]),
        "coverage": {
            "requirements": {
                "total": len(requirement_ids),
                "covered_by_ir": sum(1 for req_id in requirement_ids if ir_by_requirement[req_id]),
                "covered_by_tests": sum(1 for req_id in requirement_ids if tests_by_requirement[req_id]),
                "uncovered_by_ir": [
                    req_id for req_id in requirement_ids if not ir_by_requirement[req_id]
                ],
                "uncovered_by_tests": [
                    req_id for req_id in requirement_ids if not tests_by_requirement[req_id]
                ],
            },
            "test_scenarios": {
                "total": len(test_scenarios),
                "with_results": sum(
                    1 for scenario in test_scenarios if scenario["id"] in result_scenario_ids
                ),
            },
            "model_elements": {
                "transitions": len(transitions),
                "invariants": len(invariants),
            },
        },
        "trace_matrix": trace_matrix,
        "findings": findings,
    }


def run_requirement_agent_checks(payload: dict[str, Any]) -> dict[str, Any]:
    """Run deterministic checks over structured requirement candidates."""
    validate_agent_output_contract(payload)
    agent_output = _agent_output(payload)
    agent_payload = _payload(payload)
    findings: list[dict[str, Any]] = []

    for requirement in _requirements(agent_payload):
        requirement_id = str(requirement.get("id", "<unknown>"))
        ambiguity = requirement.get("ambiguity")
        unresolved_items = [
            item
            for item in ambiguity
            if isinstance(item, str) and item.strip()
        ] if isinstance(ambiguity, list) else []
        clarification_status = str(requirement.get("clarification_status", ""))
        if unresolved_items and clarification_status not in {
            "candidate_assumption_recorded",
            "resolved",
        }:
            findings.append(
                {
                    "code": "REQ_AMBIGUITY_UNRESOLVED",
                    "severity": "high",
                    "message": (
                        f"Requirement {requirement_id} has unresolved ambiguity: "
                        f"{'; '.join(unresolved_items)}"
                    ),
                    "requirement_id": requirement_id,
                }
            )

    return {
        "agent_name": "RequirementAnalystAgent",
        "source_agent_name": agent_output["agent_name"],
        "task_id": agent_output["task_id"],
        "status": "fail" if findings else "pass",
        "boundary": dict(agent_output["boundary"]),
        "findings": findings,
    }
