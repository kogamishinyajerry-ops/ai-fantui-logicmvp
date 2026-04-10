from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from well_harness.system_spec import (
    AcceptanceScenarioSpec,
    ClarificationItemSpec,
    ComponentSpec,
    ControlSystemWorkbenchSpec,
    FaultModeSpec,
    KnowledgeCaptureSpec,
    LogicConditionSpec,
    LogicNodeSpec,
    TimedTransitionSpec,
    default_workbench_clarification_questions,
    workbench_spec_to_dict,
)


@dataclass(frozen=True)
class SourceDocumentRef:
    id: str
    kind: str
    title: str
    location: str
    role: str
    notes: str = ""


@dataclass(frozen=True)
class ClarificationAnswer:
    question_id: str
    answer: str
    status: str = "answered"


@dataclass(frozen=True)
class ControlSystemIntakePacket:
    system_id: str
    title: str
    objective: str
    source_of_truth: str
    source_documents: tuple[SourceDocumentRef, ...]
    components: tuple[ComponentSpec, ...]
    logic_nodes: tuple[LogicNodeSpec, ...]
    acceptance_scenarios: tuple[AcceptanceScenarioSpec, ...]
    fault_modes: tuple[FaultModeSpec, ...]
    knowledge_capture: KnowledgeCaptureSpec
    clarification_answers: tuple[ClarificationAnswer, ...] = ()
    tags: tuple[str, ...] = ()


def _tuple_or_empty(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,)


def _require_str(payload: dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value.strip()


def _component_from_dict(payload: dict[str, Any]) -> ComponentSpec:
    allowed_range = payload.get("allowed_range")
    if allowed_range is not None:
        if not isinstance(allowed_range, (list, tuple)) or len(allowed_range) != 2:
            raise ValueError("component.allowed_range must be a 2-item list when present.")
        allowed_range = (float(allowed_range[0]), float(allowed_range[1]))
    return ComponentSpec(
        id=_require_str(payload, "id"),
        label=_require_str(payload, "label"),
        kind=_require_str(payload, "kind"),
        state_shape=_require_str(payload, "state_shape"),
        unit=_require_str(payload, "unit"),
        description=_require_str(payload, "description"),
        allowed_range=allowed_range,
        allowed_states=tuple(str(item) for item in _tuple_or_empty(payload.get("allowed_states"))),
        monitor_priority=str(payload.get("monitor_priority", "optional")),
    )


def _logic_condition_from_dict(payload: dict[str, Any]) -> LogicConditionSpec:
    return LogicConditionSpec(
        name=_require_str(payload, "name"),
        source_component_id=_require_str(payload, "source_component_id"),
        comparison=_require_str(payload, "comparison"),
        threshold_value=payload.get("threshold_value"),
        note=_require_str(payload, "note"),
    )


def _logic_node_from_dict(payload: dict[str, Any]) -> LogicNodeSpec:
    return LogicNodeSpec(
        id=_require_str(payload, "id"),
        label=_require_str(payload, "label"),
        description=_require_str(payload, "description"),
        conditions=tuple(_logic_condition_from_dict(item) for item in payload.get("conditions", [])),
        downstream_component_ids=tuple(str(item) for item in _tuple_or_empty(payload.get("downstream_component_ids"))),
        evidence_priority=str(payload.get("evidence_priority", "high")),
    )


def _timed_transition_from_dict(payload: dict[str, Any]) -> TimedTransitionSpec:
    return TimedTransitionSpec(
        signal_id=_require_str(payload, "signal_id"),
        start_s=float(payload.get("start_s", 0.0)),
        end_s=float(payload.get("end_s", 0.0)),
        start_value=float(payload.get("start_value", 0.0)),
        end_value=float(payload.get("end_value", 0.0)),
        unit=_require_str(payload, "unit"),
        note=_require_str(payload, "note"),
    )


def _acceptance_scenario_from_dict(payload: dict[str, Any]) -> AcceptanceScenarioSpec:
    return AcceptanceScenarioSpec(
        id=_require_str(payload, "id"),
        label=_require_str(payload, "label"),
        description=_require_str(payload, "description"),
        time_scale_factor=float(payload.get("time_scale_factor", 1.0)),
        total_duration_s=float(payload.get("total_duration_s", 0.0)),
        monitored_signal_ids=tuple(str(item) for item in _tuple_or_empty(payload.get("monitored_signal_ids"))),
        transitions=tuple(_timed_transition_from_dict(item) for item in payload.get("transitions", [])),
        completion_condition=_require_str(payload, "completion_condition"),
    )


def _fault_mode_from_dict(payload: dict[str, Any]) -> FaultModeSpec:
    return FaultModeSpec(
        id=_require_str(payload, "id"),
        target_component_id=_require_str(payload, "target_component_id"),
        fault_kind=_require_str(payload, "fault_kind"),
        symptom=_require_str(payload, "symptom"),
        reasoning_scope_component_ids=tuple(str(item) for item in _tuple_or_empty(payload.get("reasoning_scope_component_ids"))),
        expected_diagnostic_sections=tuple(str(item) for item in _tuple_or_empty(payload.get("expected_diagnostic_sections"))),
        optimization_prompt=_require_str(payload, "optimization_prompt"),
    )


def _knowledge_capture_from_dict(payload: dict[str, Any]) -> KnowledgeCaptureSpec:
    return KnowledgeCaptureSpec(
        incident_fields=tuple(str(item) for item in _tuple_or_empty(payload.get("incident_fields"))),
        resolution_fields=tuple(str(item) for item in _tuple_or_empty(payload.get("resolution_fields"))),
        optimization_fields=tuple(str(item) for item in _tuple_or_empty(payload.get("optimization_fields"))),
    )


def _source_document_from_dict(payload: dict[str, Any]) -> SourceDocumentRef:
    return SourceDocumentRef(
        id=_require_str(payload, "id"),
        kind=_require_str(payload, "kind"),
        title=_require_str(payload, "title"),
        location=_require_str(payload, "location"),
        role=_require_str(payload, "role"),
        notes=str(payload.get("notes", "")),
    )


def _clarification_answer_from_dict(payload: dict[str, Any]) -> ClarificationAnswer:
    return ClarificationAnswer(
        question_id=_require_str(payload, "question_id"),
        answer=_require_str(payload, "answer"),
        status=str(payload.get("status", "answered")),
    )


def intake_template_payload() -> dict[str, Any]:
    return {
        "system_id": "new_control_system_id",
        "title": "New Control System",
        "objective": "Describe what this system must control or protect.",
        "source_of_truth": "engineer-supplied mixed docs/PDF packet",
        "source_documents": [
            {
                "id": "doc-logic-spec",
                "kind": "pdf",
                "title": "Logic Specification",
                "location": "docs/logic-spec.pdf",
                "role": "logic_spec",
                "notes": "Reference the original source even if structured extraction happens elsewhere.",
            },
            {
                "id": "doc-ab-test",
                "kind": "markdown",
                "title": "A/B Test Timeline",
                "location": "docs/ab-test-timeline.md",
                "role": "acceptance_evidence",
                "notes": "Use additional entries for Notion pages, tables, screenshots, or extracted text bundles.",
            },
        ],
        "components": [
            {
                "id": "signal_id",
                "label": "Signal Label",
                "kind": "sensor",
                "state_shape": "analog",
                "unit": "custom-unit",
                "description": "Engineer-defined semantics for this system only.",
                "allowed_range": [0.0, 100.0],
                "monitor_priority": "required",
            }
        ],
        "logic_nodes": [],
        "acceptance_scenarios": [],
        "fault_modes": [],
        "knowledge_capture": {
            "incident_fields": ["system_id", "scenario_id", "fault_mode_id", "observed_symptoms", "evidence_links"],
            "resolution_fields": ["confirmed_root_cause", "repair_action", "validation_after_fix", "residual_risk"],
            "optimization_fields": ["suggested_logic_change", "reliability_gain_hypothesis", "redundancy_reduction_or_guardrail_note"],
        },
        "clarification_answers": [
            {
                "question_id": "source_documents",
                "answer": "Mixed docs/PDF",
            },
            {
                "question_id": "component_state_domains",
                "answer": "Each system defines its own signal semantics, units, and legal ranges.",
            },
        ],
        "tags": ["mixed-doc-intake", "custom-signal-semantics"],
    }


def load_intake_packet(path: str | Path) -> ControlSystemIntakePacket:
    packet_path = Path(path)
    with packet_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("intake packet root must be a JSON object.")
    return intake_packet_from_dict(payload)


def intake_packet_from_dict(payload: dict[str, Any]) -> ControlSystemIntakePacket:
    return ControlSystemIntakePacket(
        system_id=_require_str(payload, "system_id"),
        title=_require_str(payload, "title"),
        objective=_require_str(payload, "objective"),
        source_of_truth=_require_str(payload, "source_of_truth"),
        source_documents=tuple(_source_document_from_dict(item) for item in payload.get("source_documents", [])),
        components=tuple(_component_from_dict(item) for item in payload.get("components", [])),
        logic_nodes=tuple(_logic_node_from_dict(item) for item in payload.get("logic_nodes", [])),
        acceptance_scenarios=tuple(_acceptance_scenario_from_dict(item) for item in payload.get("acceptance_scenarios", [])),
        fault_modes=tuple(_fault_mode_from_dict(item) for item in payload.get("fault_modes", [])),
        knowledge_capture=_knowledge_capture_from_dict(payload.get("knowledge_capture", {})),
        clarification_answers=tuple(_clarification_answer_from_dict(item) for item in payload.get("clarification_answers", [])),
        tags=tuple(str(item) for item in _tuple_or_empty(payload.get("tags"))),
    )


def _component_blockers(components: tuple[ComponentSpec, ...]) -> list[str]:
    blockers: list[str] = []
    for component in components:
        if component.state_shape == "analog" and component.allowed_range is None:
            blockers.append(f"component {component.id} is analog but missing allowed_range.")
        if component.state_shape in {"binary", "discrete"} and not component.allowed_states:
            blockers.append(f"component {component.id} is {component.state_shape} but missing allowed_states.")
    return blockers


def _scenario_blockers(
    scenarios: tuple[AcceptanceScenarioSpec, ...],
    component_ids: set[str],
) -> list[str]:
    blockers: list[str] = []
    for scenario in scenarios:
        if not scenario.transitions:
            blockers.append(f"scenario {scenario.id} has no transitions.")
        for signal_id in scenario.monitored_signal_ids:
            if signal_id not in component_ids:
                blockers.append(f"scenario {scenario.id} references unknown monitored signal {signal_id}.")
        for transition in scenario.transitions:
            if transition.signal_id not in component_ids:
                blockers.append(f"scenario {scenario.id} transition references unknown signal {transition.signal_id}.")
    return blockers


def _logic_blockers(
    logic_nodes: tuple[LogicNodeSpec, ...],
    component_ids: set[str],
) -> list[str]:
    blockers: list[str] = []
    for logic_node in logic_nodes:
        if not logic_node.conditions:
            blockers.append(f"logic node {logic_node.id} has no conditions.")
        for condition in logic_node.conditions:
            if condition.source_component_id not in component_ids:
                blockers.append(
                    f"logic node {logic_node.id} references unknown source component {condition.source_component_id}."
                )
    return blockers


def _fault_blockers(
    fault_modes: tuple[FaultModeSpec, ...],
    component_ids: set[str],
) -> list[str]:
    blockers: list[str] = []
    for fault_mode in fault_modes:
        if fault_mode.target_component_id not in component_ids:
            blockers.append(f"fault mode {fault_mode.id} targets unknown component {fault_mode.target_component_id}.")
        for component_id in fault_mode.reasoning_scope_component_ids:
            if component_id not in component_ids:
                blockers.append(f"fault mode {fault_mode.id} references unknown scope component {component_id}.")
    return blockers


def _unanswered_clarifications(
    answers: tuple[ClarificationAnswer, ...],
    required_questions: tuple[ClarificationItemSpec, ...],
) -> list[dict[str, str]]:
    answer_map = {
        answer.question_id: answer.answer.strip()
        for answer in answers
        if answer.status == "answered" and answer.answer.strip()
    }
    missing = []
    for question in required_questions:
        if not answer_map.get(question.id):
            missing.append(
                {
                    "id": question.id,
                    "prompt": question.prompt,
                    "rationale": question.rationale,
                    "required_for": question.required_for,
                }
            )
    return missing


def intake_packet_to_workbench_spec(packet: ControlSystemIntakePacket) -> ControlSystemWorkbenchSpec:
    return ControlSystemWorkbenchSpec(
        system_id=packet.system_id,
        title=packet.title,
        objective=packet.objective,
        source_of_truth=packet.source_of_truth,
        components=packet.components,
        logic_nodes=packet.logic_nodes,
        acceptance_scenarios=packet.acceptance_scenarios,
        fault_modes=packet.fault_modes,
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=packet.knowledge_capture,
        tags=packet.tags,
    )


def assess_intake_packet(packet: ControlSystemIntakePacket) -> dict[str, Any]:
    required_questions = default_workbench_clarification_questions()
    component_ids = {component.id for component in packet.components}
    blockers: list[str] = []
    if not packet.source_documents:
        blockers.append("at least one source document is required.")
    if not packet.components:
        blockers.append("at least one component definition is required.")
    if not packet.logic_nodes:
        blockers.append("at least one logic node definition is required.")
    if not packet.acceptance_scenarios:
        blockers.append("at least one acceptance scenario is required.")
    if not packet.fault_modes:
        blockers.append("at least one fault mode is required.")
    if not packet.knowledge_capture.incident_fields:
        blockers.append("knowledge_capture.incident_fields must not be empty.")
    if not packet.knowledge_capture.resolution_fields:
        blockers.append("knowledge_capture.resolution_fields must not be empty.")
    if not packet.knowledge_capture.optimization_fields:
        blockers.append("knowledge_capture.optimization_fields must not be empty.")

    blockers.extend(_component_blockers(packet.components))
    blockers.extend(_logic_blockers(packet.logic_nodes, component_ids))
    blockers.extend(_scenario_blockers(packet.acceptance_scenarios, component_ids))
    blockers.extend(_fault_blockers(packet.fault_modes, component_ids))

    unanswered = _unanswered_clarifications(packet.clarification_answers, required_questions)
    ready = not blockers and not unanswered
    generated_spec = workbench_spec_to_dict(intake_packet_to_workbench_spec(packet)) if ready else None
    source_document_kinds = sorted({document.kind for document in packet.source_documents})

    return {
        "system_id": packet.system_id,
        "title": packet.title,
        "objective": packet.objective,
        "source_document_count": len(packet.source_documents),
        "source_document_kinds": source_document_kinds,
        "includes_pdf_sources": "pdf" in source_document_kinds,
        "mixed_source_packet": len(source_document_kinds) > 1,
        "component_count": len(packet.components),
        "logic_node_count": len(packet.logic_nodes),
        "acceptance_scenario_count": len(packet.acceptance_scenarios),
        "fault_mode_count": len(packet.fault_modes),
        "custom_signal_semantics": [
            {
                "id": component.id,
                "label": component.label,
                "state_shape": component.state_shape,
                "unit": component.unit,
                "kind": component.kind,
            }
            for component in packet.components
        ],
        "unanswered_clarifications": unanswered,
        "blocking_reasons": blockers,
        "ready_for_spec_build": ready,
        "generated_workbench_spec": generated_spec,
    }


def render_intake_assessment_text(report: dict[str, Any]) -> str:
    lines = [
        f"system: {report['system_id']} - {report['title']}",
        f"objective: {report['objective']}",
        (
            f"sources: {report['source_document_count']} "
            f"(kinds={', '.join(report['source_document_kinds']) or '-'})"
        ),
        f"includes_pdf_sources: {'yes' if report['includes_pdf_sources'] else 'no'}",
        f"mixed_source_packet: {'yes' if report['mixed_source_packet'] else 'no'}",
        (
            f"coverage: components={report['component_count']} "
            f"logic_nodes={report['logic_node_count']} "
            f"acceptance_scenarios={report['acceptance_scenario_count']} "
            f"fault_modes={report['fault_mode_count']}"
        ),
        f"ready_for_spec_build: {'yes' if report['ready_for_spec_build'] else 'no'}",
    ]
    if report["custom_signal_semantics"]:
        lines.append("signal semantics:")
        lines.extend(
            f"  - {item['id']} [{item['state_shape']}] unit={item['unit']} kind={item['kind']}"
            for item in report["custom_signal_semantics"]
        )
    if report["blocking_reasons"]:
        lines.append("blocking reasons:")
        lines.extend(f"  - {reason}" for reason in report["blocking_reasons"])
    if report["unanswered_clarifications"]:
        lines.append("clarifications still required:")
        lines.extend(
            f"  - {item['id']}: {item['prompt']}"
            for item in report["unanswered_clarifications"]
        )
    return "\n".join(lines)
