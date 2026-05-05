from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast

from well_harness.fault_taxonomy import validate_fault_kind  # type: ignore[import-untyped]
from well_harness.system_spec import (  # type: ignore[import-untyped]
    AcceptanceScenarioSpec,
    ClarificationItemSpec,
    ComponentSpec,
    ControlSystemWorkbenchSpec,
    FaultModeSpec,
    KnowledgeCaptureSpec,
    LogicConditionSpec,
    LogicNodeSpec,
    SteadySignalSpec,
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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


def _steady_signal_from_dict(payload: dict[str, Any]) -> SteadySignalSpec:
    return SteadySignalSpec(
        signal_id=_require_str(payload, "signal_id"),
        value=payload.get("value"),
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
        steady_signals=tuple(_steady_signal_from_dict(item) for item in payload.get("steady_signals", [])),
        transitions=tuple(_timed_transition_from_dict(item) for item in payload.get("transitions", [])),
        completion_condition=_require_str(payload, "completion_condition"),
    )


def _fault_mode_from_dict(payload: dict[str, Any]) -> FaultModeSpec:
    return FaultModeSpec(
        id=_require_str(payload, "id"),
        target_component_id=_require_str(payload, "target_component_id"),
        fault_kind=validate_fault_kind(_require_str(payload, "fault_kind")),
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
        "acceptance_scenarios": [
            {
                "id": "scenario_id",
                "label": "Scenario Label",
                "description": "Engineer-described process to replay.",
                "time_scale_factor": 1.0,
                "total_duration_s": 5.0,
                "monitored_signal_ids": ["signal_id"],
                "steady_signals": [
                    {
                        "signal_id": "signal_id",
                        "value": 0.0,
                        "unit": "custom-unit",
                        "note": "Baseline value before timed transitions start.",
                    }
                ],
                "transitions": [
                    {
                        "signal_id": "signal_id",
                        "start_s": 0.0,
                        "end_s": 5.0,
                        "start_value": 0.0,
                        "end_value": 50.0,
                        "unit": "custom-unit",
                        "note": "Example ramp from intake docs.",
                    }
                ],
                "completion_condition": "signal_id == 50",
            }
        ],
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


def intake_packet_to_dict(packet: ControlSystemIntakePacket) -> dict[str, Any]:
    return packet.to_dict()


def _unique_stub_id(existing_ids: set[str], base_id: str) -> str:
    if base_id not in existing_ids:
        return base_id
    index = 2
    while f"{base_id}_{index}" in existing_ids:
        index += 1
    return f"{base_id}_{index}"


def _first_component_payload(payload: dict[str, Any]) -> dict[str, Any]:
    components = payload.get("components", [])
    if isinstance(components, list) and components:
        return cast(dict[str, Any], components[0])
    return cast(dict[str, Any], intake_template_payload()["components"][0])


def _default_component_stub() -> dict[str, Any]:
    return dict(intake_template_payload()["components"][0])


def _default_source_document_stub() -> dict[str, Any]:
    return dict(intake_template_payload()["source_documents"][0])


def _default_logic_node_stub(payload: dict[str, Any]) -> dict[str, Any]:
    component = _first_component_payload(payload)
    component_id = str(component.get("id", "signal_id"))
    existing_ids = {
        str(item.get("id", "")).strip()
        for item in payload.get("logic_nodes", [])
        if isinstance(item, dict)
    }
    logic_id = _unique_stub_id(existing_ids, f"logic_{component_id}")
    return {
        "id": logic_id,
        "label": logic_id.upper(),
        "description": "Auto-filled logic stub. Replace the threshold and downstream mapping with the real engineer logic.",
        "conditions": [
            {
                "name": component_id,
                "source_component_id": component_id,
                "comparison": ">=",
                "threshold_value": 1.0,
                "note": "Auto-filled threshold stub. Replace with the real triggering condition.",
            }
        ],
        "downstream_component_ids": [component_id],
        "evidence_priority": "high",
    }


def _default_acceptance_scenario_stub(payload: dict[str, Any]) -> dict[str, Any]:
    component = _first_component_payload(payload)
    component_id = str(component.get("id", "signal_id"))
    unit = str(component.get("unit", "custom-unit"))
    existing_ids = {
        str(item.get("id", "")).strip()
        for item in payload.get("acceptance_scenarios", [])
        if isinstance(item, dict)
    }
    scenario_id = _unique_stub_id(existing_ids, f"{component_id}_scenario")
    return {
        "id": scenario_id,
        "label": scenario_id.replace("_", " ").title(),
        "description": "Auto-filled acceptance scenario stub. Replace the timeline with the real engineer process.",
        "time_scale_factor": 1.0,
        "total_duration_s": 5.0,
        "monitored_signal_ids": [component_id],
        "steady_signals": [
            {
                "signal_id": component_id,
                "value": 0.0,
                "unit": unit,
                "note": "Auto-filled baseline stub.",
            }
        ],
        "transitions": [
            {
                "signal_id": component_id,
                "start_s": 0.0,
                "end_s": 5.0,
                "start_value": 0.0,
                "end_value": 1.0,
                "unit": unit,
                "note": "Auto-filled transition stub. Replace with the real trajectory.",
            }
        ],
        "completion_condition": f"{component_id} >= 1.0",
    }


def _default_fault_mode_stub(payload: dict[str, Any]) -> dict[str, Any]:
    component = _first_component_payload(payload)
    component_id = str(component.get("id", "signal_id"))
    existing_ids = {
        str(item.get("id", "")).strip()
        for item in payload.get("fault_modes", [])
        if isinstance(item, dict)
    }
    fault_id = _unique_stub_id(existing_ids, f"{component_id}_fault")
    return {
        "id": fault_id,
        "target_component_id": component_id,
        "fault_kind": "stuck_low",
        "symptom": f"{component_id} never reaches the expected threshold.",
        "reasoning_scope_component_ids": [component_id],
        "expected_diagnostic_sections": ["symptoms", "repair_hint"],
        "optimization_prompt": "Describe what extra guardrail or redundancy should be added after this fault is understood.",
    }


def _default_scenario_transition_stub(packet: ControlSystemIntakePacket, scenario_id: str) -> dict[str, Any] | None:
    scenarios = {scenario.id: scenario for scenario in packet.acceptance_scenarios}
    scenario = scenarios.get(scenario_id)
    if scenario is None:
        return None
    component_map = {component.id: component for component in packet.components}
    candidate_signal_id = scenario.monitored_signal_ids[0] if scenario.monitored_signal_ids else (
        packet.components[0].id if packet.components else None
    )
    if candidate_signal_id is None:
        return None
    component = component_map.get(candidate_signal_id)
    if component is None or component.state_shape == "discrete":
        return None
    return {
        "signal_id": component.id,
        "start_s": 0.0,
        "end_s": max(scenario.total_duration_s, 1.0),
        "start_value": 0.0,
        "end_value": 1.0,
        "unit": component.unit,
        "note": "Auto-filled transition stub. Replace with the real monitored timeline.",
    }


def build_schema_repair_suggestions(
    packet: ControlSystemIntakePacket,
    *,
    blocking_reasons: list[str],
) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    covered_reasons: set[str] = set()

    def add_suggestion(
        suggestion_id: str,
        title: str,
        detail: str,
        target_path: str,
        blocking_reason: str,
        *,
        autofix_available: bool,
        autofix_label: str | None = None,
        expected_effect: str | None = None,
    ) -> None:
        suggestions.append(
            {
                "id": suggestion_id,
                "title": title,
                "detail": detail,
                "target_path": target_path,
                "blocking_reason": blocking_reason,
                "autofix_available": autofix_available,
                "autofix_label": autofix_label,
                "expected_effect": expected_effect or "Repair this blocker and rerun the intake flow.",
            }
        )
        covered_reasons.add(blocking_reason)

    if not packet.source_documents:
        add_suggestion(
            "add_source_document_stub",
            "补一个 source document 占位",
            "当前 packet 没有任何来源文档，系统无法确认工程真值来自哪里。",
            "source_documents",
            "at least one source document is required.",
            autofix_available=True,
            autofix_label="插入文档占位",
            expected_effect="至少补上一个可编辑的 source document 占位，后续再替换成真实文档引用。",
        )

    if not packet.components:
        add_suggestion(
            "add_component_stub",
            "补一个 component 占位",
            "当前 packet 没有任何组件定义，后续 logic / scenario / fault 都无法落到具体信号上。",
            "components",
            "at least one component definition is required.",
            autofix_available=True,
            autofix_label="插入组件占位",
            expected_effect="先补一个可编辑 component stub，让 packet 具备最基本的信号骨架。",
        )

    for component in packet.components:
        if component.state_shape == "analog" and component.allowed_range is None:
            reason = f"component {component.id} is analog but missing allowed_range."
            add_suggestion(
                f"set_allowed_range:{component.id}",
                f"补全 {component.id} 的 allowed_range",
                f"{component.id} 是模拟量，但当前还没有合法范围；至少需要一个临时 range 才能安全回放和注入故障。",
                f"components[{component.id}].allowed_range",
                reason,
                autofix_available=True,
                autofix_label="填入默认范围",
                expected_effect="先补一个 0..100 的默认范围占位，后续再替换成真实工程范围。",
            )
        if component.state_shape == "binary" and not component.allowed_states:
            reason = f"component {component.id} is binary but missing allowed_states."
            add_suggestion(
                f"set_allowed_states:{component.id}",
                f"补全 {component.id} 的 allowed_states",
                f"{component.id} 是二值量，但当前还没有合法状态集合。",
                f"components[{component.id}].allowed_states",
                reason,
                autofix_available=True,
                autofix_label="填入 0/1 状态",
                expected_effect="先补一个常见的 0/1 状态占位，后续再替换成真实工程状态定义。",
            )
        if component.state_shape == "discrete" and not component.allowed_states:
            reason = f"component {component.id} is discrete but missing allowed_states."
            add_suggestion(
                f"set_allowed_states:{component.id}",
                f"补全 {component.id} 的 allowed_states",
                f"{component.id} 是离散态，但当前还没有状态枚举。",
                f"components[{component.id}].allowed_states",
                reason,
                autofix_available=True,
                autofix_label="填入状态占位",
                expected_effect="先补一个最小离散状态集合占位，后续再替换成真实工程枚举。",
            )

    if not packet.logic_nodes:
        add_suggestion(
            "add_logic_node_stub",
            "补一条 logic node 骨架",
            "当前 packet 没有 logic node，系统还不知道控制门控是怎么被触发的。",
            "logic_nodes",
            "at least one logic node definition is required.",
            autofix_available=True,
            autofix_label="插入 logic stub",
            expected_effect="先补一条可编辑 logic node stub，后续再替换成真实 logic chain。",
        )

    if not packet.acceptance_scenarios:
        add_suggestion(
            "add_acceptance_scenario_stub",
            "补一个 acceptance scenario 占位",
            "当前 packet 没有任何验收场景，系统无法生成严格回放时间线。",
            "acceptance_scenarios",
            "at least one acceptance scenario is required.",
            autofix_available=True,
            autofix_label="插入 scenario stub",
            expected_effect="先补一个可编辑 scenario stub，后续再替换成真实 engineer process。",
        )
    else:
        for scenario in packet.acceptance_scenarios:
            if not scenario.transitions and _default_scenario_transition_stub(packet, scenario.id) is not None:
                reason = f"scenario {scenario.id} has no transitions."
                add_suggestion(
                    f"add_scenario_transition_stub:{scenario.id}",
                    f"给 {scenario.id} 补一个 transition 占位",
                    f"{scenario.id} 目前没有任何 transition；系统至少需要一个时间线骨架才能继续回放。",
                    f"acceptance_scenarios[{scenario.id}].transitions",
                    reason,
                    autofix_available=True,
                    autofix_label="插入 transition stub",
                    expected_effect="先补一条可编辑 transition stub，后续再替换成真实工程时间线。",
                )

    if not packet.fault_modes:
        add_suggestion(
            "add_fault_mode_stub",
            "补一个 fault mode 占位",
            "当前 packet 没有故障模式，系统还无法进入 fault diagnosis / knowledge capture。",
            "fault_modes",
            "at least one fault mode is required.",
            autofix_available=True,
            autofix_label="插入 fault stub",
            expected_effect="先补一个可编辑 fault mode stub，后续再替换成真实 fault taxonomy。",
        )

    if not packet.knowledge_capture.incident_fields:
        add_suggestion(
            "fill_knowledge_capture_incident_fields",
            "补 incident_fields 默认骨架",
            "knowledge_capture.incident_fields 为空，当前无法稳定记录 incident 事实。",
            "knowledge_capture.incident_fields",
            "knowledge_capture.incident_fields must not be empty.",
            autofix_available=True,
            autofix_label="填入默认 incident fields",
        )
    if not packet.knowledge_capture.resolution_fields:
        add_suggestion(
            "fill_knowledge_capture_resolution_fields",
            "补 resolution_fields 默认骨架",
            "knowledge_capture.resolution_fields 为空，当前无法记录修复结果。",
            "knowledge_capture.resolution_fields",
            "knowledge_capture.resolution_fields must not be empty.",
            autofix_available=True,
            autofix_label="填入默认 resolution fields",
        )
    if not packet.knowledge_capture.optimization_fields:
        add_suggestion(
            "fill_knowledge_capture_optimization_fields",
            "补 optimization_fields 默认骨架",
            "knowledge_capture.optimization_fields 为空，当前无法沉淀 guardrail / reliability 建议。",
            "knowledge_capture.optimization_fields",
            "knowledge_capture.optimization_fields must not be empty.",
            autofix_available=True,
            autofix_label="填入默认 optimization fields",
        )

    manual_counter = 1
    for reason in blocking_reasons:
        if reason in covered_reasons:
            continue
        suggestions.append(
            {
                "id": f"manual_schema_fix_{manual_counter}",
                "title": f"手工修复 blocker {manual_counter}",
                "detail": reason,
                "target_path": "packet JSON",
                "blocking_reason": reason,
                "autofix_available": False,
                "autofix_label": None,
                "expected_effect": "这个 blocker 还需要工程师手工调整 packet JSON 或文档语义后再重跑。",
            }
        )
        manual_counter += 1

    return suggestions


def _apply_schema_repair_suggestion_to_payload(payload: dict[str, Any], suggestion_id: str) -> dict[str, Any]:
    next_payload = cast(dict[str, Any], json.loads(json.dumps(payload, ensure_ascii=False)))
    template_defaults = intake_template_payload()

    if suggestion_id == "add_source_document_stub":
        source_documents = next_payload.setdefault("source_documents", [])
        if not source_documents:
            source_documents.append(_default_source_document_stub())
        return next_payload

    if suggestion_id == "add_component_stub":
        components = next_payload.setdefault("components", [])
        if not components:
            components.append(_default_component_stub())
        return next_payload

    if suggestion_id == "add_logic_node_stub":
        logic_nodes = next_payload.setdefault("logic_nodes", [])
        if not logic_nodes:
            logic_nodes.append(_default_logic_node_stub(next_payload))
        return next_payload

    if suggestion_id == "add_acceptance_scenario_stub":
        scenarios = next_payload.setdefault("acceptance_scenarios", [])
        if not scenarios:
            scenarios.append(_default_acceptance_scenario_stub(next_payload))
        return next_payload

    if suggestion_id == "add_fault_mode_stub":
        fault_modes = next_payload.setdefault("fault_modes", [])
        if not fault_modes:
            fault_modes.append(_default_fault_mode_stub(next_payload))
        return next_payload

    if suggestion_id.startswith("set_allowed_range:"):
        component_id = suggestion_id.split(":", 1)[1]
        for component in next_payload.get("components", []):
            if component.get("id") == component_id and component.get("allowed_range") is None:
                component["allowed_range"] = [0.0, 100.0]
                break
        return next_payload

    if suggestion_id.startswith("set_allowed_states:"):
        component_id = suggestion_id.split(":", 1)[1]
        for component in next_payload.get("components", []):
            if component.get("id") != component_id or component.get("allowed_states"):
                continue
            component["allowed_states"] = ["0", "1"] if component.get("state_shape") == "binary" else ["state_a", "state_b"]
            break
        return next_payload

    if suggestion_id.startswith("add_scenario_transition_stub:"):
        scenario_id = suggestion_id.split(":", 1)[1]
        current_packet = intake_packet_from_dict(next_payload)
        transition_stub = _default_scenario_transition_stub(current_packet, scenario_id)
        if transition_stub is None:
            return next_payload
        for scenario in next_payload.get("acceptance_scenarios", []):
            if scenario.get("id") == scenario_id and not scenario.get("transitions"):
                scenario["transitions"] = [transition_stub]
                if not scenario.get("steady_signals"):
                    scenario["steady_signals"] = [
                        {
                            "signal_id": transition_stub["signal_id"],
                            "value": transition_stub["start_value"],
                            "unit": transition_stub["unit"],
                            "note": "Auto-filled baseline stub.",
                        }
                    ]
                break
        return next_payload

    if suggestion_id == "fill_knowledge_capture_incident_fields":
        next_payload.setdefault("knowledge_capture", {})
        if not next_payload["knowledge_capture"].get("incident_fields"):
            next_payload["knowledge_capture"]["incident_fields"] = list(template_defaults["knowledge_capture"]["incident_fields"])
        return next_payload

    if suggestion_id == "fill_knowledge_capture_resolution_fields":
        next_payload.setdefault("knowledge_capture", {})
        if not next_payload["knowledge_capture"].get("resolution_fields"):
            next_payload["knowledge_capture"]["resolution_fields"] = list(template_defaults["knowledge_capture"]["resolution_fields"])
        return next_payload

    if suggestion_id == "fill_knowledge_capture_optimization_fields":
        next_payload.setdefault("knowledge_capture", {})
        if not next_payload["knowledge_capture"].get("optimization_fields"):
            next_payload["knowledge_capture"]["optimization_fields"] = list(
                template_defaults["knowledge_capture"]["optimization_fields"]
            )
        return next_payload

    raise ValueError(f"unknown or unsupported schema repair suggestion: {suggestion_id}")


def apply_safe_schema_repairs(packet: ControlSystemIntakePacket) -> tuple[ControlSystemIntakePacket, tuple[str, ...]]:
    payload = intake_packet_to_dict(packet)
    applied_suggestion_ids: list[str] = []

    while True:
        current_packet = intake_packet_from_dict(payload)
        report = assess_intake_packet(current_packet)
        safe_suggestions = [
            item
            for item in report["repair_suggestions"]
            if item["autofix_available"] and item["id"] not in applied_suggestion_ids
        ]
        if not safe_suggestions:
            break
        suggestion_id = safe_suggestions[0]["id"]
        previous_payload = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        payload = _apply_schema_repair_suggestion_to_payload(payload, suggestion_id)
        applied_suggestion_ids.append(suggestion_id)
        if json.dumps(payload, ensure_ascii=False, sort_keys=True) == previous_payload:
            break

    return intake_packet_from_dict(payload), tuple(applied_suggestion_ids)


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
    logic_source_ids: set[str],
    derived_component_ids: set[str],
) -> list[str]:
    blockers: list[str] = []
    for scenario in scenarios:
        if not scenario.transitions:
            blockers.append(f"scenario {scenario.id} has no transitions.")
        covered_signal_ids = {signal.signal_id for signal in scenario.steady_signals}
        covered_signal_ids.update(transition.signal_id for transition in scenario.transitions)
        for signal_id in scenario.monitored_signal_ids:
            if signal_id not in component_ids:
                blockers.append(f"scenario {scenario.id} references unknown monitored signal {signal_id}.")
            elif signal_id not in covered_signal_ids and signal_id not in derived_component_ids:
                blockers.append(
                    f"scenario {scenario.id} does not define a baseline or transition for monitored signal {signal_id}."
                )
        for steady_signal in scenario.steady_signals:
            if steady_signal.signal_id not in component_ids:
                blockers.append(f"scenario {scenario.id} steady signal references unknown signal {steady_signal.signal_id}.")
        for transition in scenario.transitions:
            if transition.signal_id not in component_ids:
                blockers.append(f"scenario {scenario.id} transition references unknown signal {transition.signal_id}.")
        for source_id in logic_source_ids:
            if source_id not in covered_signal_ids and source_id not in derived_component_ids:
                blockers.append(
                    f"scenario {scenario.id} does not define a baseline or transition for logic source {source_id}."
                )
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
    logic_ids: set[str],
) -> list[str]:
    blockers: list[str] = []
    for fault_mode in fault_modes:
        if fault_mode.target_component_id not in component_ids:
            blockers.append(f"fault mode {fault_mode.id} targets unknown component {fault_mode.target_component_id}.")
        for component_id in fault_mode.reasoning_scope_component_ids:
            if component_id not in component_ids and component_id not in logic_ids:
                blockers.append(f"fault mode {fault_mode.id} references unknown scope item {component_id}.")
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
    logic_ids = {logic_node.id for logic_node in packet.logic_nodes}
    logic_source_ids = {
        condition.source_component_id
        for logic_node in packet.logic_nodes
        for condition in logic_node.conditions
    }
    derived_component_ids = {
        component_id
        for logic_node in packet.logic_nodes
        for component_id in logic_node.downstream_component_ids
    }
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
    blockers.extend(_scenario_blockers(packet.acceptance_scenarios, component_ids, logic_source_ids, derived_component_ids))
    blockers.extend(_fault_blockers(packet.fault_modes, component_ids, logic_ids))

    unanswered = _unanswered_clarifications(packet.clarification_answers, required_questions)
    ready = not blockers and not unanswered
    generated_spec = workbench_spec_to_dict(intake_packet_to_workbench_spec(packet)) if ready else None
    source_document_kinds = sorted({document.kind for document in packet.source_documents})
    repair_suggestions = build_schema_repair_suggestions(packet, blocking_reasons=blockers)

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
        "repair_suggestions": repair_suggestions,
        "ready_for_spec_build": ready,
        "generated_workbench_spec": generated_spec,
    }


def build_clarification_brief(packet: ControlSystemIntakePacket) -> dict[str, Any]:
    report = assess_intake_packet(packet)
    answered_map = {
        answer.question_id: {
            "answer": answer.answer.strip(),
            "status": answer.status,
        }
        for answer in packet.clarification_answers
        if answer.answer.strip()
    }
    follow_up_items = []
    open_question_ids: list[str] = []
    for question in default_workbench_clarification_questions():
        answer_payload = answered_map.get(question.id)
        status = "answered" if answer_payload and answer_payload["status"] == "answered" else "needs_answer"
        if status != "answered":
            open_question_ids.append(question.id)
        follow_up_items.append(
            {
                "id": question.id,
                "status": status,
                "prompt": question.prompt,
                "rationale": question.rationale,
                "required_for": question.required_for,
                "answer": answer_payload["answer"] if answer_payload else "",
            }
        )

    if report["ready_for_spec_build"]:
        gate_status = "ready"
        gating_statement = (
            "Clarification gate is clear. The intake packet can now advance into spec build, playback, diagnosis, and "
            "knowledge capture."
        )
    elif open_question_ids and report["blocking_reasons"]:
        gate_status = "blocked_by_schema_and_clarifications"
        gating_statement = (
            f"Spec build is blocked by {len(report['blocking_reasons'])} structural issue(s) and "
            f"{len(open_question_ids)} unanswered clarification(s)."
        )
    elif open_question_ids:
        gate_status = "blocked_by_clarifications"
        gating_statement = (
            f"Spec build is blocked until {len(open_question_ids)} clarification question(s) are answered."
        )
    else:
        gate_status = "blocked_by_schema"
        gating_statement = (
            f"Clarifications are complete, but {len(report['blocking_reasons'])} structural issue(s) still block spec build."
        )

    next_actions = [
        f"Answer clarification {item['id']}: {item['prompt']}"
        for item in follow_up_items
        if item["status"] != "answered"
    ]
    if report["blocking_reasons"]:
        next_actions.extend(f"Fix schema blocker: {reason}" for reason in report["blocking_reasons"])
    if not next_actions:
        next_actions.append("Proceed to spec build, playback, fault diagnosis, or knowledge capture.")

    return {
        "system_id": packet.system_id,
        "title": packet.title,
        "objective": packet.objective,
        "gate_status": gate_status,
        "ready_for_spec_build": report["ready_for_spec_build"],
        "gating_statement": gating_statement,
        "open_question_count": len(open_question_ids),
        "blocking_reason_count": len(report["blocking_reasons"]),
        "source_documents": [
            {
                "id": document.id,
                "kind": document.kind,
                "title": document.title,
                "role": document.role,
                "location": document.location,
            }
            for document in packet.source_documents
        ],
        "follow_up_items": follow_up_items,
        "blocking_reasons": report["blocking_reasons"],
        "next_actions": next_actions,
        "unlocks_after_completion": [
            "spec_build",
            "scenario_playback",
            "fault_diagnosis",
            "knowledge_capture",
        ]
        if report["ready_for_spec_build"]
        else ["spec_build"],
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
    if report["repair_suggestions"]:
        lines.append("repair suggestions:")
        lines.extend(
            "  - "
            + ("[safe] " if item["autofix_available"] else "[manual] ")
            + f"{item['title']} -> {item['target_path']}"
            for item in report["repair_suggestions"]
        )
    if report["unanswered_clarifications"]:
        lines.append("clarifications still required:")
        lines.extend(
            f"  - {item['id']}: {item['prompt']}"
            for item in report["unanswered_clarifications"]
        )
    return "\n".join(lines)


def render_clarification_brief_text(brief: dict[str, Any]) -> str:
    lines = [
        f"system: {brief['system_id']} - {brief['title']}",
        f"objective: {brief['objective']}",
        f"gate_status: {brief['gate_status']}",
        f"ready_for_spec_build: {'yes' if brief['ready_for_spec_build'] else 'no'}",
        f"gating_statement: {brief['gating_statement']}",
        (
            f"open_questions={brief['open_question_count']} "
            f"blocking_reasons={brief['blocking_reason_count']}"
        ),
    ]
    if brief["source_documents"]:
        lines.append("source_documents:")
        lines.extend(
            f"  - {item['id']} [{item['kind']}] role={item['role']} title={item['title']} location={item['location']}"
            for item in brief["source_documents"]
        )
    lines.append("follow_up_items:")
    lines.extend(
        (
            f"  - {item['id']} [{item['status']}] {item['prompt']}"
            + (f" | answer={item['answer']}" if item["answer"] else "")
            + f" | required_for={item['required_for']}"
        )
        for item in brief["follow_up_items"]
    )
    if brief["blocking_reasons"]:
        lines.append("blocking_reasons:")
        lines.extend(f"  - {reason}" for reason in brief["blocking_reasons"])
    lines.append("next_actions:")
    lines.extend(f"  - {item}" for item in brief["next_actions"])
    lines.append(f"unlocks_after_completion: {', '.join(brief['unlocks_after_completion'])}")
    return "\n".join(lines)
