from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA  # type: ignore[import-untyped]
from well_harness.models import HarnessConfig  # type: ignore[import-untyped]


CONTROL_SYSTEM_SPEC_KIND = "well-harness-control-system-spec"
CONTROL_SYSTEM_SPEC_VERSION = 1
CONTROL_SYSTEM_SPEC_SCHEMA_ID = "https://well-harness.local/json_schema/control_system_spec_v1.schema.json"


@dataclass(frozen=True)
class ComponentSpec:
    id: str
    label: str
    kind: str
    state_shape: str
    unit: str
    description: str
    allowed_range: tuple[float, float] | None = None
    allowed_states: tuple[str, ...] = ()
    monitor_priority: str = "optional"


@dataclass(frozen=True)
class LogicConditionSpec:
    name: str
    source_component_id: str
    comparison: str
    threshold_value: Any
    note: str


@dataclass(frozen=True)
class LogicNodeSpec:
    id: str
    label: str
    description: str
    conditions: tuple[LogicConditionSpec, ...]
    downstream_component_ids: tuple[str, ...] = ()
    evidence_priority: str = "high"


@dataclass(frozen=True)
class TimedTransitionSpec:
    signal_id: str
    start_s: float
    end_s: float
    start_value: float
    end_value: float
    unit: str
    note: str


@dataclass(frozen=True)
class SteadySignalSpec:
    signal_id: str
    value: Any
    unit: str
    note: str


@dataclass(frozen=True)
class AcceptanceScenarioSpec:
    id: str
    label: str
    description: str
    time_scale_factor: float
    total_duration_s: float
    monitored_signal_ids: tuple[str, ...]
    transitions: tuple[TimedTransitionSpec, ...]
    completion_condition: str
    steady_signals: tuple[SteadySignalSpec, ...] = ()


@dataclass(frozen=True)
class FaultModeSpec:
    id: str
    target_component_id: str
    fault_kind: str
    symptom: str
    reasoning_scope_component_ids: tuple[str, ...]
    expected_diagnostic_sections: tuple[str, ...]
    optimization_prompt: str


@dataclass(frozen=True)
class ClarificationItemSpec:
    id: str
    prompt: str
    rationale: str
    required_for: str


@dataclass(frozen=True)
class KnowledgeCaptureSpec:
    incident_fields: tuple[str, ...]
    resolution_fields: tuple[str, ...]
    optimization_fields: tuple[str, ...]


@dataclass(frozen=True)
class ControlSystemWorkbenchSpec:
    system_id: str
    title: str
    objective: str
    source_of_truth: str
    components: tuple[ComponentSpec, ...]
    logic_nodes: tuple[LogicNodeSpec, ...]
    acceptance_scenarios: tuple[AcceptanceScenarioSpec, ...]
    fault_modes: tuple[FaultModeSpec, ...]
    onboarding_questions: tuple[ClarificationItemSpec, ...]
    knowledge_capture: KnowledgeCaptureSpec
    tags: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json_safe_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_value(item) for item in value]
    return value


def workbench_spec_to_dict(spec: ControlSystemWorkbenchSpec) -> dict[str, Any]:
    payload = _json_safe_value(spec.to_dict())
    return {
        "$schema": CONTROL_SYSTEM_SPEC_SCHEMA_ID,
        "kind": CONTROL_SYSTEM_SPEC_KIND,
        "version": CONTROL_SYSTEM_SPEC_VERSION,
        **payload,
    }


def workbench_spec_from_dict(payload: dict[str, Any]) -> ControlSystemWorkbenchSpec:
    return ControlSystemWorkbenchSpec(
        system_id=payload["system_id"],
        title=payload["title"],
        objective=payload["objective"],
        source_of_truth=payload["source_of_truth"],
        components=tuple(
            ComponentSpec(
                id=item["id"],
                label=item["label"],
                kind=item["kind"],
                state_shape=item["state_shape"],
                unit=item["unit"],
                description=item["description"],
                allowed_range=tuple(item["allowed_range"]) if item["allowed_range"] is not None else None,
                allowed_states=tuple(item.get("allowed_states", ())),
                monitor_priority=item.get("monitor_priority", "optional"),
            )
            for item in payload["components"]
        ),
        logic_nodes=tuple(
            LogicNodeSpec(
                id=item["id"],
                label=item["label"],
                description=item["description"],
                conditions=tuple(
                    LogicConditionSpec(
                        name=condition["name"],
                        source_component_id=condition["source_component_id"],
                        comparison=condition["comparison"],
                        threshold_value=condition["threshold_value"],
                        note=condition["note"],
                    )
                    for condition in item["conditions"]
                ),
                downstream_component_ids=tuple(item.get("downstream_component_ids", ())),
                evidence_priority=item.get("evidence_priority", "high"),
            )
            for item in payload["logic_nodes"]
        ),
        acceptance_scenarios=tuple(
            AcceptanceScenarioSpec(
                id=item["id"],
                label=item["label"],
                description=item["description"],
                time_scale_factor=item["time_scale_factor"],
                total_duration_s=item["total_duration_s"],
                monitored_signal_ids=tuple(item["monitored_signal_ids"]),
                transitions=tuple(
                    TimedTransitionSpec(
                        signal_id=transition["signal_id"],
                        start_s=transition["start_s"],
                        end_s=transition["end_s"],
                        start_value=transition["start_value"],
                        end_value=transition["end_value"],
                        unit=transition["unit"],
                        note=transition["note"],
                    )
                    for transition in item["transitions"]
                ),
                completion_condition=item["completion_condition"],
                steady_signals=tuple(
                    SteadySignalSpec(
                        signal_id=signal["signal_id"],
                        value=signal["value"],
                        unit=signal["unit"],
                        note=signal["note"],
                    )
                    for signal in item.get("steady_signals", ())
                ),
            )
            for item in payload["acceptance_scenarios"]
        ),
        fault_modes=tuple(
            FaultModeSpec(
                id=item["id"],
                target_component_id=item["target_component_id"],
                fault_kind=item["fault_kind"],
                symptom=item["symptom"],
                reasoning_scope_component_ids=tuple(item["reasoning_scope_component_ids"]),
                expected_diagnostic_sections=tuple(item["expected_diagnostic_sections"]),
                optimization_prompt=item["optimization_prompt"],
            )
            for item in payload["fault_modes"]
        ),
        onboarding_questions=tuple(
            ClarificationItemSpec(
                id=item["id"],
                prompt=item["prompt"],
                rationale=item["rationale"],
                required_for=item["required_for"],
            )
            for item in payload["onboarding_questions"]
        ),
        knowledge_capture=KnowledgeCaptureSpec(
            incident_fields=tuple(payload["knowledge_capture"]["incident_fields"]),
            resolution_fields=tuple(payload["knowledge_capture"]["resolution_fields"]),
            optimization_fields=tuple(payload["knowledge_capture"]["optimization_fields"]),
        ),
        tags=tuple(payload.get("tags", ())),
    )


def default_workbench_clarification_questions() -> tuple[ClarificationItemSpec, ...]:
    return (
        ClarificationItemSpec(
            id="source_documents",
            prompt="新系统的输入文档具体是什么格式：结构化表格、Markdown/Notion、PDF，还是混合来源？",
            rationale="决定是否先做文档适配器，还是先要求工程师整理为统一 spec。",
            required_for="严格验收与快速泛化",
        ),
        ClarificationItemSpec(
            id="component_state_domains",
            prompt="每个组件究竟是二值开关、固定电平、离散状态，还是连续模拟量？单位和合法范围分别是什么？",
            rationale="避免把不同信号形态混成一套错误的监控曲线。",
            required_for="监控曲线仿真与故障注入",
        ),
        ClarificationItemSpec(
            id="timeline_rules",
            prompt="工程师给出的运行过程是事件驱动、速率驱动，还是带延时/滞后的状态机？哪些节点允许保持/饱和？",
            rationale="决定如何把 A/B 过程文档转成严格可回放的时间线。",
            required_for="严格验收仿真",
        ),
        ClarificationItemSpec(
            id="fault_taxonomy",
            prompt="新系统需要支持哪些故障注入类型：卡滞、短路、断路、虚警、延迟、阈值漂移，还是其他类型？",
            rationale="决定诊断树、推理文档模板和优化建议的范围。",
            required_for="故障分析与知识积累",
        ),
    )


def current_reference_workbench_spec(config: HarnessConfig | None = None) -> ControlSystemWorkbenchSpec:
    active_config = config or HarnessConfig()
    components = (
        ComponentSpec(
            id="radio_altitude_ft",
            label="RA",
            kind="sensor",
            state_shape="analog",
            unit="ft",
            description="无线电高度输入；L1 依赖该值小于阈值。",
            allowed_range=(0.0, 20.0),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="tra_deg",
            label="TRA",
            kind="pilot_input",
            state_shape="analog",
            unit="deg",
            description="反推拉杆角度；当前系统在 -32° 到 0° 之间工作。",
            allowed_range=(active_config.reverse_travel_min_deg, active_config.reverse_travel_max_deg),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="sw1",
            label="SW1",
            kind="switch",
            state_shape="binary",
            unit="state",
            description="TRA 进入 SW1 窗口时闭合。",
            allowed_states=("0", "1"),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="sw2",
            label="SW2",
            kind="switch",
            state_shape="binary",
            unit="state",
            description="TRA 进入 SW2 窗口时闭合。",
            allowed_states=("0", "1"),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="engine_running",
            label="Engine Running",
            kind="state",
            state_shape="binary",
            unit="state",
            description="发动机运行状态；L2/L4 依赖该值为真。",
            allowed_states=("0", "1"),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="aircraft_on_ground",
            label="On Ground",
            kind="state",
            state_shape="binary",
            unit="state",
            description="飞机是否在地面；L2/L4 依赖该值为真。",
            allowed_states=("0", "1"),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="reverser_inhibited",
            label="Reverser Inhibited",
            kind="state",
            state_shape="binary",
            unit="state",
            description="反推抑制状态；L1/L2 依赖该值为假。",
            allowed_states=("0", "1"),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="eec_enable",
            label="EEC Enable",
            kind="state",
            state_shape="binary",
            unit="state",
            description="EEC 允许位；L2 依赖该值为真。",
            allowed_states=("0", "1"),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="n1k",
            label="N1K",
            kind="sensor",
            state_shape="analog",
            unit="percent",
            description="N1K 输入；L3 依赖该值低于限制。",
            allowed_range=(0.0, 110.0),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="max_n1k_deploy_limit",
            label="Max N1K Deploy Limit",
            kind="parameter",
            state_shape="analog",
            unit="percent",
            description="允许 deploy 的 N1K 限制。",
            allowed_range=(0.0, 110.0),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="tls_voltage_v",
            label="TLS",
            kind="power",
            state_shape="analog",
            unit="V",
            description="TLS 组件断开时为 0V，接通后为 115V。",
            allowed_range=(0.0, 115.0),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="etrac_voltage_v",
            label="ETRAC",
            kind="power",
            state_shape="analog",
            unit="V",
            description="ETRAC 组件断开时为 0V，接通后为 540V。",
            allowed_range=(0.0, 540.0),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="eec_cmd",
            label="EEC",
            kind="command",
            state_shape="binary",
            unit="state",
            description="EEC 指令节点，只有 0/1 状态。",
            allowed_states=("0", "1"),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="pls_cmd",
            label="PLS",
            kind="command",
            state_shape="binary",
            unit="state",
            description="PLS 指令节点，只有 0/1 状态。",
            allowed_states=("0", "1"),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="pdu_cmd",
            label="PDU",
            kind="command",
            state_shape="binary",
            unit="state",
            description="PDU 驱动命令，当前逻辑由 L3 扇出。",
            allowed_states=("0", "1"),
            monitor_priority="optional",
        ),
        ComponentSpec(
            id="deploy_position_percent",
            label="Deploy Feedback",
            kind="feedback",
            state_shape="analog",
            unit="%",
            description="当前参考系统中的 simplified plant 位移反馈，用于产生 VDT90/L4 条件。",
            allowed_range=(0.0, 100.0),
            monitor_priority="required",
        ),
        ComponentSpec(
            id="thr_lock",
            label="THR_LOCK",
            kind="command",
            state_shape="binary",
            unit="state",
            description="电子油门锁释放命令，只有 0/1 状态。",
            allowed_states=("0", "1"),
            monitor_priority="required",
        ),
    )

    logic_nodes = (
        LogicNodeSpec(
            id="logic1",
            label="L1",
            description="RA + SW1 + inhibit/eec 边界共同驱动 TLS。",
            conditions=(
                LogicConditionSpec("radio_altitude_ft", "radio_altitude_ft", "<", active_config.logic1_ra_ft_threshold, "RA 需要低于阈值"),
                LogicConditionSpec("sw1", "sw1", "==", True, "SW1 必须闭合"),
                LogicConditionSpec("reverser_inhibited", "reverser_inhibited", "==", False, "反推不能被抑制"),
                LogicConditionSpec("reverser_not_deployed_eec", "reverser_not_deployed_eec", "==", True, "EEC 视角下应仍处于未展开"),
            ),
            downstream_component_ids=("tls_voltage_v",),
        ),
        LogicNodeSpec(
            id="logic2",
            label="L2",
            description="发动机/地面/SW2/EEC 边界共同驱动 ETRAC。",
            conditions=(
                LogicConditionSpec("engine_running", "engine_running", "==", True, "发动机必须运行"),
                LogicConditionSpec("aircraft_on_ground", "aircraft_on_ground", "==", True, "飞机必须在地面"),
                LogicConditionSpec("reverser_inhibited", "reverser_inhibited", "==", False, "反推不能被抑制"),
                LogicConditionSpec("sw2", "sw2", "==", True, "SW2 必须闭合"),
                LogicConditionSpec("eec_enable", "eec_enable", "==", True, "EEC enable 必须为真"),
            ),
            downstream_component_ids=("etrac_voltage_v",),
        ),
        LogicNodeSpec(
            id="logic3",
            label="L3",
            description="TLS 解锁、N1K、TRA 阈值共同驱动 EEC / PLS / PDU。",
            conditions=(
                LogicConditionSpec("engine_running", "engine_running", "==", True, "发动机必须运行"),
                LogicConditionSpec("aircraft_on_ground", "aircraft_on_ground", "==", True, "飞机必须在地面"),
                LogicConditionSpec("reverser_inhibited", "reverser_inhibited", "==", False, "反推不能被抑制"),
                # tls_unlocked_ls is a processed boolean: True when tls_voltage_v >= 115V
                # Use the processed signal directly so generator produces correct logic
                LogicConditionSpec("tls_unlocked_ls", "tls_unlocked_ls", "==", True, "TLS 已通电并经过解锁延迟"),
                LogicConditionSpec("n1k", "n1k", "<", "max_n1k_deploy_limit", "N1K 必须低于 limit"),
                LogicConditionSpec("tra_deg", "tra_deg", "<=", active_config.logic3_tra_deg_threshold, "TRA 必须进入 L3 阈值内"),
            ),
            downstream_component_ids=("eec_cmd", "pls_cmd", "pdu_cmd"),
        ),
        LogicNodeSpec(
            id="logic4",
            label="L4",
            description="VDT90、反推 travel、发动机和地面条件共同驱动 THR_LOCK。注意：VDT90 由 L3 扇出的 PDU motor 驱动位移反馈产生，L4 实际上间接依赖 L3 的成立（物理因果链：L3 → pdu_motor_cmd → deploy_position_percent ≥ 90% → VDT90 → L4）。",
            conditions=(
                LogicConditionSpec("deploy_90_percent_vdt", "deploy_position_percent", ">=", active_config.deploy_90_threshold_percent, "VDT 反馈位移已达到 90%（由 L3 驱动 PDU 产生）"),
                LogicConditionSpec("tra_deg", "tra_deg", "between_lower_inclusive", (active_config.reverse_travel_min_deg, active_config.reverse_travel_max_deg), "TRA 必须处于有效反推 travel 内（下界包含：机械停位即最大反推，仍有效）"),
                LogicConditionSpec("aircraft_on_ground", "aircraft_on_ground", "==", True, "飞机必须在地面"),
                LogicConditionSpec("engine_running", "engine_running", "==", True, "发动机必须运行"),
            ),
            downstream_component_ids=("thr_lock",),
        ),
    )

    acceptance_scenarios = (
        AcceptanceScenarioSpec(
            id="compressed_ra_tra_vdt_monitor",
            label="压缩版 RA -> TRA -> VDT 监控流程",
            description="将原始监控过程压缩到 1/10，作为严格验收的第一条参考场景。",
            time_scale_factor=0.1,
            total_duration_s=7.0,
            monitored_signal_ids=(
                "radio_altitude_ft",
                "tra_deg",
                "sw1",
                "sw2",
                "tls_voltage_v",
                "etrac_voltage_v",
                "eec_cmd",
                "pls_cmd",
                "deploy_position_percent",
                "thr_lock",
            ),
            transitions=(
                TimedTransitionSpec("radio_altitude_ft", 0.0, 7.0, 7.0, 0.0, "ft", "RA 线性下降到 0ft 后保持"),
                TimedTransitionSpec("tra_deg", 1.0, 2.4, 0.0, -14.0, "deg", "RA 降到 6ft 后，TRA 以压缩后的速率推到 -14°"),
                TimedTransitionSpec("sw1", 1.2, 1.4, 0.0, 1.0, "state", "TRA 进入 SW1 窗口后，SW1 置位。"),
                TimedTransitionSpec("sw2", 1.8, 2.0, 0.0, 1.0, "state", "TRA 继续深入 reverse 区后，SW2 置位。"),
                TimedTransitionSpec("deploy_position_percent", 2.4, 4.4, 0.0, 100.0, "%", "TRA 到达 -14° 后，VDT 相关反馈开始爬升到 100%"),
            ),
            completion_condition="deploy_position_percent == 100% and thr_lock == 1",
            steady_signals=(
                SteadySignalSpec("engine_running", 1, "state", "参考场景固定假设发动机处于运行状态。"),
                SteadySignalSpec("aircraft_on_ground", 1, "state", "参考场景固定假设飞机已经在地面。"),
                SteadySignalSpec("reverser_inhibited", 0, "state", "参考场景中反推不被抑制。"),
                SteadySignalSpec("eec_enable", 1, "state", "参考场景固定假设 EEC enable 为真。"),
                SteadySignalSpec("n1k", 35.0, "percent", "参考场景中 N1K 保持在 deploy 限值以下。"),
                SteadySignalSpec("max_n1k_deploy_limit", 60.0, "percent", "参考场景中 deploy 限值固定为 60。"),
            ),
        ),
    )

    fault_modes = (
        FaultModeSpec(
            id="sw1_stuck_open",
            target_component_id="sw1",
            fault_kind="stuck_low",
            symptom="RA 已低于阈值但 TLS 始终不通电。",
            reasoning_scope_component_ids=("radio_altitude_ft", "sw1", "logic1", "tls_voltage_v"),
            expected_diagnostic_sections=("symptoms", "upstream_checks", "logic_blockers", "repair_hint"),
            optimization_prompt="如果 SW1 失效频繁，可评估是否增加独立的 travel cross-check 或更明确的锁位自检。",
        ),
        FaultModeSpec(
            id="tls_never_unlocks",
            target_component_id="tls_voltage_v",
            fault_kind="latched_no_unlock",
            symptom="TLS 已通电但 L3 长时间不满足，EEC/PLS/PDU 不扇出。",
            reasoning_scope_component_ids=("logic1", "tls_voltage_v", "logic3", "eec_cmd", "pls_cmd"),
            expected_diagnostic_sections=("symptoms", "power_path", "unlock_assumptions", "repair_hint"),
            optimization_prompt="可评估增加 TLS 解锁状态确认或超时降级提示，降低下游诊断歧义。",
        ),
        FaultModeSpec(
            id="thr_lock_never_releases",
            target_component_id="thr_lock",
            fault_kind="command_path_failure",
            symptom="TRA 和反馈位移都已满足，但 THR_LOCK 仍未释放。",
            reasoning_scope_component_ids=("deploy_position_percent", "logic4", "thr_lock"),
            expected_diagnostic_sections=("symptoms", "boundary_checks", "downstream_command_path", "repair_hint"),
            optimization_prompt="可评估将 L4 条件和 THR_LOCK 执行链分开观测，提升容错和可诊断性。",
        ),
    )

    knowledge_capture = KnowledgeCaptureSpec(
        incident_fields=(
            "system_id",
            "scenario_id",
            "fault_mode_id",
            "observed_symptoms",
            "evidence_links",
        ),
        resolution_fields=(
            "confirmed_root_cause",
            "repair_action",
            "validation_after_fix",
            "residual_risk",
        ),
        optimization_fields=(
            "suggested_logic_change",
            "reliability_gain_hypothesis",
            "redundancy_reduction_or_guardrail_note",
        ),
    )

    return ControlSystemWorkbenchSpec(
        system_id="reference_thrust_reverser_deploy",
        title="Reference Thrust Reverser Control Workbench Spec",
        objective=(
            "Use the current deterministic deploy chain as the first reference system for future "
            "strict acceptance playback, fault injection, diagnosis, and cross-system generalization."
        ),
        source_of_truth=REFERENCE_DEPLOY_CONTROLLER_METADATA.source_of_truth,
        components=components,
        logic_nodes=logic_nodes,
        acceptance_scenarios=acceptance_scenarios,
        fault_modes=fault_modes,
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=knowledge_capture,
        tags=("reference-system", "strict-acceptance", "fault-injection", "generalization-ready"),
    )
