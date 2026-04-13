from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Iterable

from well_harness.controller_adapter import build_reference_controller_adapter
from well_harness.models import FieldChange, HarnessConfig, LogicTransitionDiagnosis, SimulationResult
from well_harness.runner import SimulationRunner
from well_harness.scenarios import nominal_deploy_scenario


CONTROL_CHAIN = (
    "SW1 -> logic1/TLS115 -> TLS unlocked -> SW2 -> logic2/540V -> "
    "logic3/EEC+PLS+PDU -> VDT90 -> logic4/THR_LOCK"
)
MODEL_BOUNDARY = (
    "当前回答基于内置 nominal-deploy / retract-reset scenario 和 simplified first-cut plant；"
    "它不是完整自然语言 AI 系统，也不是完整真实物理模型。"
)


@dataclass(frozen=True)
class DemoAnswer:
    intent: str
    matched_node: str | None
    target_logic: str | None
    evidence: tuple[str, ...]
    outcome: tuple[str, ...]
    possible_causes: tuple[str, ...]
    required_changes: tuple[str, ...]
    risks: tuple[str, ...]


def demo_answer_to_payload(answer: DemoAnswer) -> dict[str, object]:
    return {
        "intent": answer.intent,
        "matched_node": answer.matched_node,
        "target_logic": answer.target_logic,
        "evidence": list(answer.evidence),
        "outcome": list(answer.outcome),
        "possible_causes": list(answer.possible_causes),
        "required_changes": list(answer.required_changes),
        "risks": list(answer.risks),
    }


@dataclass(frozen=True)
class DemoNode:
    node_id: str
    aliases: tuple[str, ...]
    category: str
    downstream_summary: str
    trace_field: str | None = None
    logic_name: str | None = None
    blocker_hints: tuple[str, ...] = ()


@dataclass(frozen=True)
class UpstreamEvidenceStatus:
    name: str
    source: str
    observed: bool
    summary: str


@dataclass(frozen=True)
class BlockedEvidenceStatus:
    name: str
    source: str
    observed: bool
    checkpoint_time_s: float | None
    value: object
    required: str


NODE_CATALOG = (
    DemoNode(
        node_id="sw1",
        aliases=("SW1", "sw1"),
        category="switch",
        trace_field="sw1",
        downstream_summary="SW1 latched 后会使 logic1 有机会成立，并驱动 TLS115 供电命令。",
        blocker_hints=(
            "SW1 依赖 TRA 穿过受控 switch window；先看 events() 中 sw1 是否有 0->1。",
            "若 SW1 未触发，再沿 trace 的 TRA 输入和 switch window 解释排查；这不是修改 controller.py 的路径。",
        ),
    ),
    DemoNode(
        node_id="logic1",
        aliases=("logic1", "logic 1"),
        category="logic",
        trace_field="logic1_active",
        logic_name="logic1",
        downstream_summary="logic1 active 后会输出 TLS115 供电命令，推动 TLS unlock evidence 出现。",
    ),
    DemoNode(
        node_id="tls115",
        aliases=("TLS115", "tls115", "tls 115", "tls_115vac_cmd", "115vac"),
        category="command",
        trace_field="tls_115vac_cmd",
        downstream_summary="TLS115 命令给 simplified plant 的 TLS unlock 计时提供输入。",
        blocker_hints=(
            "TLS115 依赖 logic1；先用 logic_transition_diagnostics(logic1) / DeployController.explain(logic1) 看 logic1 blocker。",
            "也看 events() 中 logic1_active 与 tls_115vac_cmd 是否在同一窗口触发。",
        ),
    ),
    DemoNode(
        node_id="tls_unlocked",
        aliases=("TLS unlocked", "tls unlocked", "tls_unlocked_ls", "tls unlock"),
        category="sensor",
        trace_field="tls_unlocked_ls",
        downstream_summary="TLS unlocked sensor 成立后，logic3 的 TLS 门控条件可以通过。",
        blocker_hints=(
            "TLS unlocked 依赖 TLS115 / logic1：先看 events() 中 logic1_active 与 tls_115vac_cmd 是否已触发。",
            "若 TLS115 已触发但 tls_unlocked_ls 未触发，再看 simplified plant TLS timer：trace 里的 plant_state.tls_powered_s 和 events() 的 tls_unlocked_ls。",
            "logic1 的门控仍以 DeployController.explain(logic1) / logic_transition_diagnostics(logic1) 为证据来源。",
        ),
    ),
    DemoNode(
        node_id="sw2",
        aliases=("SW2", "sw2"),
        category="switch",
        trace_field="sw2",
        downstream_summary="SW2 latched 后会使 logic2 有机会成立，并驱动 540V command。",
        blocker_hints=(
            "SW2 依赖 TRA 穿过受控 switch window；先看 events() 中 sw2 是否有 0->1。",
            "若 SW2 未触发，再沿 trace 的 TRA 输入和 switch window 解释排查；它不是 controller.py 的独立 logic。",
        ),
    ),
    DemoNode(
        node_id="logic2",
        aliases=("logic2", "logic 2"),
        category="logic",
        trace_field="logic2_active",
        logic_name="logic2",
        downstream_summary="logic2 active 后会输出 ETRAC 540V command。",
    ),
    DemoNode(
        node_id="etrac_540v",
        aliases=("540V", "540v", "540vdc", "etrac 540v", "etrac_540vdc_cmd"),
        category="command",
        trace_field="etrac_540vdc_cmd",
        downstream_summary="540V command 是 deploy 控制链中 SW2 / logic2 之后的供电命令节点。",
        blocker_hints=(
            "540V 依赖 logic2 / SW2：先看 events() 中 sw2、logic2_active、etrac_540vdc_cmd 是否同窗触发。",
            "若 logic2 未触发，用 DeployController.explain(logic2) / logic_transition_diagnostics(logic2) 看 SW2 或其他 blocker。",
        ),
    ),
    DemoNode(
        node_id="logic3",
        aliases=("logic3", "logic 3"),
        category="logic",
        trace_field="logic3_active",
        logic_name="logic3",
        downstream_summary="logic3 active 后会同时驱动 EEC deploy、PLS power、PDU motor 命令。",
    ),
    DemoNode(
        node_id="eec_deploy",
        aliases=("EEC deploy", "eec deploy", "eec_deploy_cmd", "eec"),
        category="command",
        trace_field="eec_deploy_cmd",
        downstream_summary="EEC deploy command 是 logic3 下游的 deploy command evidence。",
        blocker_hints=(
            "EEC deploy 依赖 logic3：先看 logic_transition_diagnostics(logic3) 的 failed_conditions 和 context_changes。",
            "再看 events() 中 logic3_active 与 eec_deploy_cmd 是否同窗触发；logic3 条件仍由 DeployController.explain(logic3) 给出。",
        ),
    ),
    DemoNode(
        node_id="pls_power",
        aliases=("PLS power", "pls power", "pls_power_cmd", "pls"),
        category="command",
        trace_field="pls_power_cmd",
        downstream_summary="PLS power command 驱动 simplified plant 的 PLS unlock 计时。",
        blocker_hints=(
            "PLS power 依赖 logic3：先看 logic_transition_diagnostics(logic3) 的 failed_conditions 和 context_changes。",
            "再看 events() 中 logic3_active 与 pls_power_cmd 是否同窗触发；后续 PLS timer 属于 simplified plant evidence。",
        ),
    ),
    DemoNode(
        node_id="pdu_motor",
        aliases=("PDU motor", "pdu motor", "pdu_motor_cmd", "motor"),
        category="command",
        trace_field="pdu_motor_cmd",
        downstream_summary="PDU motor command 推动 simplified deploy position 上升，后续形成 VDT90 evidence。",
        blocker_hints=(
            "PDU motor 依赖 logic3：先看 logic_transition_diagnostics(logic3) 的 failed_conditions 和 context_changes。",
            "再看 events() 中 logic3_active 与 pdu_motor_cmd 是否同窗触发；logic3 条件仍由 DeployController.explain(logic3) 给出。",
        ),
    ),
    DemoNode(
        node_id="vdt90",
        aliases=("VDT90", "vdt90", "deploy 90", "deploy90", "deploy_90_percent_vdt", "90% vdt"),
        category="plant_feedback",
        trace_field="deploy_90_percent_vdt",
        downstream_summary="VDT90 feedback 成立后，logic4 的 deploy_90_percent_vdt 条件可以通过。",
        blocker_hints=(
            "VDT90 依赖 PDU motor / pdu_motor_cmd 推动 simplified deploy position；先看 events() 中 pdu_motor_cmd 是否已触发。",
            "再看 timeline / diagnose context 中 deploy_position_percent 是否到达 90%，以及 events() 中 deploy_90_percent_vdt 是否翻转。",
            "这是 simplified first-cut plant feedback，不是完整真实 actuator 根因证明。",
        ),
    ),
    DemoNode(
        node_id="logic4",
        aliases=("logic4", "logic 4"),
        category="logic",
        trace_field="logic4_active",
        logic_name="logic4",
        downstream_summary="logic4 active 后会输出 throttle_lock_release_cmd / THR_LOCK release。",
    ),
    DemoNode(
        node_id="thr_lock",
        aliases=(
            "THR_LOCK",
            "thr_lock",
            "thr lock",
            "throttle lock",
            "throttle_lock_release_cmd",
            "throttle lock release",
        ),
        category="command",
        trace_field="throttle_lock_release_cmd",
        downstream_summary="THR_LOCK release command 是当前 deploy demo 链路的末端释放命令。",
        blocker_hints=(
            "THR_LOCK 依赖 logic4 / deploy_90_percent_vdt：先看 logic_transition_diagnostics(logic4) 与 DeployController.explain(logic4)。",
            "再看 events() 中 deploy_90_percent_vdt、logic4_active、throttle_lock_release_cmd 是否同窗触发。",
            "如果 deploy_90_percent_vdt 仍为 0，继续回看 VDT90 / PDU motor / deploy_position_percent 的 simplified plant evidence。",
        ),
    ),
)
NODE_BY_ID = {node.node_id: node for node in NODE_CATALOG}


def answer_demo_prompt(prompt: str, config: HarnessConfig | None = None) -> DemoAnswer:
    intent, target = match_demo_intent(prompt)
    result = _nominal_result(config)

    if intent == "trigger_node":
        return _trigger_node_answer(result, target or "logic3")
    if intent == "logic4_thr_lock_bridge":
        return _logic4_throttle_lock_bridge_answer(result)
    if intent == "blocked_state":
        return _blocked_state_answer(result, target or "vdt90")
    if intent == "diagnose_problem":
        return _throttle_lock_diagnosis_answer(result)
    if intent == "propose_logic_change":
        proposed_threshold = _parse_proposed_threshold(prompt)
        return _logic3_threshold_proposal_answer(result, proposed_threshold, config or HarnessConfig())
    return _unsupported_answer(prompt)


def match_demo_intent(prompt: str) -> tuple[str, str | None]:
    normalized = _normalize_prompt(prompt)

    if (
        "logic3" in normalized
        and "tra" in normalized
        and ("阈值" in normalized or "threshold" in normalized)
        and ("改" in normalized or "change" in normalized)
    ):
        return "propose_logic_change", "logic3"

    if _matches_logic4_throttle_lock_bridge(normalized):
        return "logic4_thr_lock_bridge", "logic4"

    blocked_state_node = _match_blocked_state_node(normalized)
    if blocked_state_node is not None:
        return "blocked_state", blocked_state_node.node_id

    throttle_lock_terms = (
        "throttlelock",
        "thr_lock",
        "throttle_lock",
        "油门锁",
    )
    release_problem_terms = (
        "为什么",
        "没释放",
        "未释放",
        "notrelease",
    )
    if any(term in normalized for term in throttle_lock_terms) and any(
        term in normalized for term in release_problem_terms
    ):
        return "diagnose_problem", "throttle_lock_release_cmd"

    if "触发" in normalized or "trigger" in normalized:
        node = _match_node_from_catalog(normalized)
        if node is not None:
            return "trigger_node", node.node_id

    return "unsupported", None


def render_demo_answer(answer: DemoAnswer) -> str:
    lines = [
        f"intent: {answer.intent}",
        f"matched_node: {answer.matched_node or '(none)'}",
        f"target_logic: {answer.target_logic or '(none)'}",
        "evidence:",
        *_format_list(answer.evidence),
        "outcome:",
        *_format_list(answer.outcome),
        "possible_causes:",
        *_format_list(answer.possible_causes),
        "required_changes:",
        *_format_list(answer.required_changes),
        "risks:",
        *_format_list(answer.risks),
    ]
    return "\n".join(lines)


def _trigger_node_answer(result: SimulationResult, node_id: str) -> DemoAnswer:
    node = NODE_BY_ID.get(node_id)
    if node is None:
        return DemoAnswer(
            intent="trigger_node",
            matched_node=node_id,
            target_logic=None,
            evidence=(f"未知受控 demo node: {node_id}",),
            outcome=("当前 node catalog 没有该节点。",),
            possible_causes=("这不是开放式节点编辑器；只能回答 catalog 中的受控节点。",),
            required_changes=("如需支持新节点，需要先把它显式加入受控 node catalog。",),
            risks=(MODEL_BOUNDARY,),
        )

    diagnosis = _activation_diagnosis(result, node.logic_name) if node.logic_name else None
    event = _first_event_for_field(result, node.trace_field) if node.trace_field else None
    observed_time = diagnosis.time_s if diagnosis is not None else (event.time_s if event else None)

    if observed_time is None:
        return DemoAnswer(
            intent="trigger_node",
            matched_node=node.node_id,
            target_logic=node.logic_name,
            evidence=(
                f"node={node.node_id}; category={node.category}; trace_field={node.trace_field or '(none)'}; "
                f"logic={node.logic_name or '(none)'}。",
                f"{result.scenario_name}: 当前内置 scenario 没有观测到 {node.node_id} 触发。",
                f"控制链路证据: {CONTROL_CHAIN}",
            ),
            outcome=("当前内置 scenario 不足以展示该节点触发。", node.downstream_summary),
            possible_causes=(
                "如果这是 logic node，请查看对应 --view diagnose / --view explain 的 failed_conditions。",
                "如果这是 command / sensor / plant feedback，请先检查它的上游 logic 或 plant feedback blocker。",
            ),
            required_changes=(
                "不修改 controller.py；只扩展受控 scenario 或输入证据才能看到更多路径。",
            ),
            risks=(MODEL_BOUNDARY,),
        )

    evidence = [
        (
            f"node={node.node_id}; category={node.category}; trace_field={node.trace_field or '(none)'}; "
            f"logic={node.logic_name or '(none)'}。"
        ),
        f"{result.scenario_name}: {node.node_id} 在约 {_format_time(observed_time)} 触发。",
    ]
    if diagnosis is not None:
        evidence.extend(
            (
                _changed_condition_summary(diagnosis),
                _all_context_change_summary(diagnosis),
            )
        )
    if event is not None:
        evidence.append(_event_window_summary(event))
    elif diagnosis is not None:
        evidence.append(_event_summary(result, diagnosis.time_s, (node.trace_field or diagnosis.logic_name,)))
    evidence.extend(_upstream_status_table(result, node))
    evidence.append(f"控制链路证据: {CONTROL_CHAIN}")

    return DemoAnswer(
        intent="trigger_node",
        matched_node=node.node_id,
        target_logic=node.logic_name,
        evidence=tuple(evidence),
        outcome=_trigger_outcome(node),
        possible_causes=_trigger_possible_causes(node, diagnosis),
        required_changes=(
            f"不需要修改 controller.py；在 nominal-deploy 中现有输入已经触发 {node.node_id}。",
            "若要演示别的 timing，需要新增受控 scenario，而不是改控制真值来源。",
        ),
        risks=(MODEL_BOUNDARY,),
    )


def _throttle_lock_diagnosis_answer(result: SimulationResult) -> DemoAnswer:
    diagnosis = _activation_diagnosis(result, "logic4")
    if diagnosis is None:
        evidence = (f"{result.scenario_name}: 没有观测到 logic4 / throttle_lock_release_cmd 触发。",)
    else:
        evidence = (
            f"{result.scenario_name}: throttle_lock_release_cmd 随 logic4 在约 {_format_time(diagnosis.time_s)} 从 0->1。",
            "logic4 触发前 failed_conditions: "
            f"{', '.join(diagnosis.before_failed_conditions) or '(none)'}。",
            _changed_condition_summary(diagnosis),
            _context_change_summary(
                diagnosis,
                (
                    ("plant_sensors", "deploy_90_percent_vdt"),
                    ("plant_sensors", "deploy_position_percent"),
                    ("controller_outputs", "throttle_lock_release_cmd"),
                ),
            ),
            _event_summary(
                result,
                diagnosis.time_s,
                ("deploy_90_percent_vdt", "logic4_active", "throttle_lock_release_cmd"),
            ),
        )

    return DemoAnswer(
        intent="diagnose_problem",
        matched_node="throttle_lock_release_cmd",
        target_logic="logic4",
        evidence=evidence,
        outcome=(
            "在 nominal-deploy 中 throttle lock 不是永久没释放；它约 5.0s 才随 logic4 释放。",
            "如果某个窗口里还没释放，直接原因是 logic4 尚未 active。",
        ),
        possible_causes=(
            "最常见 blocker 是 deploy_90_percent_vdt 仍为 0；当前诊断显示它在约 5.0s 才变为 1。",
            "其他门控包括 TRA 必须在 (-32, 0)、aircraft_on_ground=True、engine_running=True。",
        ),
        required_changes=(
            "让 demo trace 到达 deploy_90_percent_vdt=True，且保持 logic4 其他条件满足。",
            "不修改 controller.py；这是基于现有 explain / diagnose 的排障映射。",
        ),
        risks=(MODEL_BOUNDARY,),
    )


def _logic4_throttle_lock_bridge_answer(result: SimulationResult) -> DemoAnswer:
    trigger_time = _first_trigger_time_for_node(result, NODE_BY_ID["logic4"])
    checkpoint_row = _pre_trigger_checkpoint_row(result, trigger_time)
    if trigger_time is None or checkpoint_row is None:
        evidence = (
            f"{result.scenario_name}: 当前内置 scenario 没有足够 evidence 构造 logic4 <-> THR_LOCK bridge summary。",
        )
    else:
        failed_conditions = _failed_conditions_at_time(result, "logic4", checkpoint_row.time_s)
        evidence = (
            (
                f"bridge=logic4->THR_LOCK; checkpoint={_format_time(checkpoint_row.time_s)}; "
                f"eventual_trigger={_format_time(trigger_time)}。"
            ),
            (
                f"{result.scenario_name}: 这是内置 nominal-deploy 的受控 evidence bridge；"
                "它不是完整异常仿真，也不是真实物理根因证明。"
            ),
            "logic4 是上游 logic gate；throttle_lock_release_cmd / THR_LOCK 是下游末端释放命令。",
            (
                f"blocked-state 解释 checkpoint gate 为什么未满足：logic4 explain@{_format_time(checkpoint_row.time_s)} "
                f"failed_conditions: {', '.join(failed_conditions) or '(none)'}。"
            ),
            (
                "diagnose_problem 解释下游 release 为什么在该窗口尚未发生："
                "logic4 尚未 active 时 throttle_lock_release_cmd 仍不会释放。"
            ),
            _event_summary(
                result,
                trigger_time,
                ("deploy_90_percent_vdt", "logic4_active", "throttle_lock_release_cmd"),
            ),
        )

    return DemoAnswer(
        intent="logic4_thr_lock_bridge",
        matched_node="logic4->thr_lock",
        target_logic="logic4",
        evidence=evidence,
        outcome=(
            "4.9s checkpoint 时 logic4 仍被 deploy_90_percent_vdt 卡住，所以下游 THR_LOCK release 也尚未发生。",
            "5.0s 时 deploy_90_percent_vdt 翻转，logic4_active 与 throttle_lock_release_cmd 在同一事件窗口触发。",
        ),
        possible_causes=(
            "如果只问 logic4 blocked-state，要看 checkpoint row 的 DeployController.explain(logic4)。",
            "如果只问 throttle lock 没释放，要看 logic4 是否 active 以及 deploy_90_percent_vdt 是否到位。",
            "这个 bridge summary 只是把两条现有受控 evidence path 放在同一回答里。",
        ),
        required_changes=(
            "不修改 controller.py；不新增 scenario；不重跑 plant。",
            "若要改变释放时机，需要在受控 scenario 中改变上游 deploy feedback timing，而不是在 demo answer 中改控制真值。",
        ),
        risks=(
            "bridge summary 只桥接 nominal-deploy 的现有 evidence，不是完整异常诊断。",
            MODEL_BOUNDARY,
        ),
    )


def _blocked_state_answer(result: SimulationResult, node_id: str) -> DemoAnswer:
    node = NODE_BY_ID.get(node_id)
    if node is None:
        return _unsupported_answer(f"blocked_state:{node_id}")

    trigger_time = _first_trigger_time_for_node(result, node)
    checkpoint_row = _pre_trigger_checkpoint_row(result, trigger_time)
    if trigger_time is None or checkpoint_row is None:
        return DemoAnswer(
            intent="blocked_state",
            matched_node=node.node_id,
            target_logic=_blocked_state_target_logic(node.node_id),
            evidence=(
                f"{result.scenario_name}: 当前内置 scenario 没有足够的 trigger evidence 来构造 {node.node_id} 的 pre-trigger comparison。",
                "这类回答只针对 nominal-deploy 中最终会触发的受控节点。",
            ),
            outcome=("当前内置 nominal-deploy 没有观测到该节点的受控 pre-trigger checkpoint。",),
            possible_causes=node.blocker_hints or ("请改用 trigger demo 或 diagnose / explain 视图继续排查。",),
            required_changes=("如需更多 blocked-state 路径，需要新增受控 scenario，而不是改 controller.py。",),
            risks=(MODEL_BOUNDARY,),
        )

    blocked_statuses = _blocked_statuses(result, node.node_id, checkpoint_row.time_s)
    evidence = [
        (
            f"node={node.node_id}; category={node.category}; checkpoint={_format_time(checkpoint_row.time_s)}; "
            f"eventual_trigger={_format_time(trigger_time)}。"
        ),
        (
            f"{result.scenario_name}: 这是内置 nominal-deploy 的 pre-trigger checkpoint comparison；"
            "它不是完整异常仿真，也不是真实物理根因证明。"
        ),
        "blocked_state_table:",
        *(_format_blocked_status(status) for status in blocked_statuses),
        f"控制链路证据: {CONTROL_CHAIN}",
    ]
    if node_id == "sw1":
        failed_conditions = _failed_conditions_at_time(result, "logic1", checkpoint_row.time_s)
        evidence.append(
            f"logic1 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("sw1", "logic1_active", "tls_115vac_cmd"),
            )
        )
    elif node_id == "sw2":
        failed_conditions = _failed_conditions_at_time(result, "logic2", checkpoint_row.time_s)
        evidence.append(
            f"logic2 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("sw2", "logic2_active", "etrac_540vdc_cmd"),
            )
        )
    elif node_id == "tls115":
        failed_conditions = _failed_conditions_at_time(result, "logic1", checkpoint_row.time_s)
        evidence.append(
            f"logic1 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("sw1", "logic1_active", "tls_115vac_cmd"),
            )
        )
    elif node_id == "logic1":
        failed_conditions = _failed_conditions_at_time(result, "logic1", checkpoint_row.time_s)
        evidence.append(
            f"logic1 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("sw1", "logic1_active", "tls_115vac_cmd"),
            )
        )
    elif node_id == "logic2":
        failed_conditions = _failed_conditions_at_time(result, "logic2", checkpoint_row.time_s)
        evidence.append(
            f"logic2 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("sw2", "logic2_active", "etrac_540vdc_cmd"),
            )
        )
    elif node_id == "logic3":
        failed_conditions = _failed_conditions_at_time(result, "logic3", checkpoint_row.time_s)
        evidence.append(
            f"logic3 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("logic3_active", "eec_deploy_cmd", "pls_power_cmd", "pdu_motor_cmd"),
            )
        )
    elif node_id == "logic4":
        failed_conditions = _failed_conditions_at_time(result, "logic4", checkpoint_row.time_s)
        evidence.append(
            f"logic4 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("deploy_90_percent_vdt", "logic4_active", "throttle_lock_release_cmd"),
            )
        )
    elif node_id == "vdt90":
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("deploy_90_percent_vdt", "logic4_active", "throttle_lock_release_cmd"),
            )
        )
    elif node_id == "tls_unlocked":
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("tls_unlocked_ls",),
            )
        )
    elif node_id == "etrac_540v":
        failed_conditions = _failed_conditions_at_time(result, "logic2", checkpoint_row.time_s)
        evidence.append(
            f"logic2 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("sw2", "logic2_active", "etrac_540vdc_cmd"),
            )
        )
    elif node_id == "thr_lock":
        failed_conditions = _failed_conditions_at_time(result, "logic4", checkpoint_row.time_s)
        evidence.append(
            f"logic4 explain@{_format_time(checkpoint_row.time_s)} failed_conditions: "
            f"{', '.join(failed_conditions) or '(none)'}。"
        )
        evidence.append(
            _event_summary(
                result,
                trigger_time,
                ("deploy_90_percent_vdt", "logic4_active", "throttle_lock_release_cmd"),
            )
        )

    return DemoAnswer(
        intent="blocked_state",
        matched_node=node.node_id,
        target_logic=_blocked_state_target_logic(node.node_id),
        evidence=tuple(evidence),
        outcome=_blocked_state_outcome(node.node_id, checkpoint_row.time_s, trigger_time),
        possible_causes=_blocked_state_possible_causes(node, blocked_statuses),
        required_changes=(
            "这是受控 demo comparison，不修改 controller.py，也不重跑新的 plant / scenario。",
            "若要更早触发该节点，需要在受控 scenario 中改变上游输入或 feedback timing，而不是在这里直接改控制真值。",
        ),
        risks=(
            "blocked-state comparison 只说明 nominal-deploy 中触发前最近一拍的 evidence 缺口，不是完整异常根因证明。",
            MODEL_BOUNDARY,
        ),
    )


def _logic3_threshold_proposal_answer(
    result: SimulationResult,
    proposed_threshold: float,
    config: HarnessConfig,
) -> DemoAnswer:
    current_threshold = config.logic3_tra_deg_threshold
    current_diagnosis = _activation_diagnosis(result, "logic3")
    proposed_time = _first_logic3_time_with_threshold(result, proposed_threshold, config)
    current_time_text = _format_time(current_diagnosis.time_s) if current_diagnosis else "(not observed)"
    proposed_time_text = _format_time(proposed_time) if proposed_time is not None else "(not observed)"

    evidence = [
        (
            f"当前 logic3 TRA 条件来自 DeployController.explain: "
            f"tra_deg <= {current_threshold:g}。"
        ),
        f"当前 nominal-deploy 中 logic3 首次激活约 {current_time_text}。",
        (
            f"dry-run 仅在现有 trace row 上用阈值 {proposed_threshold:g} 重新跑 "
            f"DeployController.explain；首次满足 logic3 的 row 约 {proposed_time_text}。"
        ),
    ]
    if current_diagnosis is not None:
        evidence.append(_changed_condition_summary(current_diagnosis))

    if proposed_time == (current_diagnosis.time_s if current_diagnosis else None):
        outcome = (
            "在当前离散 nominal-deploy trace 中，把阈值改成 -8 不会改变首次满足 logic3 的 trace row。",
            "原因是该内置 scenario 从 TRA=-7 直接跳到 TRA=-14；-8 与 -11.74 都是在同一个 1.9s row 首次满足。",
        )
    else:
        outcome = (
            f"在现有 trace row 的局部 dry-run 中，logic3 首次满足时间会从 {current_time_text} 变为 {proposed_time_text}。",
            "这只是 explain-level impact report，不是完整 plant re-simulation。",
        )

    return DemoAnswer(
        intent="propose_logic_change",
        matched_node="logic3.tra_deg",
        target_logic="logic3",
        evidence=tuple(evidence),
        outcome=outcome,
        possible_causes=(
            "阈值从 -11.74 放宽到 -8 会允许较浅 reverse pull-back 通过 logic3 TRA 门控。",
            "在更细粒度或不同 scenario 中，只要 TLS unlocked、N1K、ground / running 等条件已满足，logic3 可能更早触发。",
        ),
        required_changes=(
            "这只是 dry-run proposal；本轮没有修改 controller.py 或 HarnessConfig 默认值。",
            "若真的改，需要更新控制真值来源、阈值解释测试、diagnose / demo 期望，并重新评估安全边界。",
        ),
        risks=(
            "更早触发 logic3 可能更早输出 EEC deploy、PLS power、PDU motor。",
            "logic4 / THR_LOCK 仍取决于 deploy_90_percent_vdt 和后续 deploy evidence，不会仅因 logic3 TRA 阈值改变而自动释放。",
            MODEL_BOUNDARY,
        ),
    )


def _unsupported_answer(prompt: str) -> DemoAnswer:
    return DemoAnswer(
        intent="unsupported",
        matched_node=None,
        target_logic=None,
        evidence=(f"未匹配受控 demo 短句: {prompt}",),
        outcome=("当前只支持 trigger_node、blocked_state、diagnose_problem、propose_logic_change 四类受控 intent。",),
        possible_causes=("这不是开放式自然语言 AI 系统。",),
        required_changes=("请使用类似“触发 logic3 会发生什么”的受控短句。",),
        risks=(MODEL_BOUNDARY,),
    )


def _nominal_result(config: HarnessConfig | None = None) -> SimulationResult:
    scenario = nominal_deploy_scenario()
    return SimulationRunner(config).run(scenario.name, list(scenario.frames))


def _activation_diagnosis(
    result: SimulationResult,
    logic_name: str,
) -> LogicTransitionDiagnosis | None:
    for diagnosis in result.logic_transition_diagnostics(logic_name=logic_name):
        if not diagnosis.before_active and diagnosis.after_active:
            return diagnosis
    return None


def _match_blocked_state_node(normalized_prompt: str) -> DemoNode | None:
    if "为什么" not in normalized_prompt and "why" not in normalized_prompt:
        return None
    if "还没满足" in normalized_prompt or "尚未满足" in normalized_prompt:
        return _match_node_from_ids(
            normalized_prompt,
            ("logic1", "logic2", "logic3", "logic4"),
        )
    if "还没触发" in normalized_prompt or "尚未触发" in normalized_prompt:
        return _match_node_from_ids(
            normalized_prompt,
            ("sw1", "sw2", "tls115", "tls_unlocked", "etrac_540v", "vdt90"),
        )
    if "还没释放" in normalized_prompt or "尚未释放" in normalized_prompt:
        return _match_node_from_ids(normalized_prompt, ("thr_lock",))
    return None


def _matches_logic4_throttle_lock_bridge(normalized_prompt: str) -> bool:
    has_logic4 = "logic4" in normalized_prompt
    has_throttle_lock = any(
        term in normalized_prompt
        for term in ("throttlelock", "thr_lock", "throttle_lock", "油门锁")
    )
    has_bridge_relation = any(term in normalized_prompt for term in ("关系", "有关", "桥接", "bridge"))
    has_joint_blocked_question = (
        ("为什么" in normalized_prompt or "why" in normalized_prompt)
        and ("还没满足" in normalized_prompt or "尚未满足" in normalized_prompt)
        and ("没释放" in normalized_prompt or "未释放" in normalized_prompt or "还没释放" in normalized_prompt)
    )
    return has_logic4 and has_throttle_lock and (has_bridge_relation or has_joint_blocked_question)


def _match_node_from_catalog(normalized_prompt: str) -> DemoNode | None:
    return _match_node_from_ids(normalized_prompt, tuple(node.node_id for node in NODE_CATALOG))


def _match_node_from_ids(normalized_prompt: str, node_ids: tuple[str, ...]) -> DemoNode | None:
    matches = []
    for node_id in node_ids:
        node = NODE_BY_ID[node_id]
        for alias in node.aliases:
            normalized_alias = _normalize_prompt(alias)
            if normalized_alias and normalized_alias in normalized_prompt:
                matches.append((len(normalized_alias), node))
                break
    if not matches:
        return None
    return max(matches, key=lambda item: item[0])[1]


def _first_event_for_field(result: SimulationResult, field_name: str | None):
    if field_name is None:
        return None
    for event in result.events():
        for change in event.changes:
            if change.field_name == field_name and _is_truthy_after_change(change):
                return event
    return None


def _is_truthy_after_change(change: FieldChange) -> bool:
    if isinstance(change.after, bool):
        return change.after
    if isinstance(change.after, (int, float)):
        return change.after != 0
    return change.after is not None


def _all_context_change_summary(diagnosis: LogicTransitionDiagnosis) -> str:
    if not diagnosis.context_changes:
        return "context_changes: (none)"
    parts = [
        (
            f"{change.field_group}.{change.field_name} "
            f"{_format_demo_value(change.before_value)}->{_format_demo_value(change.after_value)}"
        )
        for change in diagnosis.context_changes
    ]
    return "context_changes: " + "; ".join(parts)


def _event_window_summary(event) -> str:
    parts = [
        f"{change.field_name} {_format_demo_value(change.before)}->{_format_demo_value(change.after)}"
        for change in event.changes
    ]
    return f"events@{_format_time(event.time_s)}: " + ("; ".join(parts) if parts else "(none)")


def _trigger_outcome(node: DemoNode) -> tuple[str, ...]:
    if node.node_id == "logic3":
        return (
            "logic3 触发后，EEC deploy、PLS power、PDU motor 命令在同一 trace window 置为 1。",
            "logic3 不是 throttle lock release；后续仍要等 deploy_90_percent_vdt 触发 logic4。",
        )
    if node.node_id == "logic4":
        return (
            "logic4 触发后，throttle_lock_release_cmd 在同一 trace window 置为 1。",
            "在当前 nominal-deploy 中，这表示 THR_LOCK demo 节点被释放。",
        )
    if node.node_id == "vdt90":
        return (
            node.downstream_summary,
            "在当前 nominal-deploy 中，VDT90 与 logic4 / throttle_lock_release_cmd 在同一事件窗口联动。",
        )
    if node.node_id == "thr_lock":
        return (
            node.downstream_summary,
            "在当前 nominal-deploy 中，它是 logic4 之后的末端释放命令节点。",
        )
    return (
        node.downstream_summary,
        "该节点是受控 demo catalog 中的当前链路节点，输出基于 nominal-deploy 的真实 trace evidence。",
    )


def _trigger_possible_causes(
    node: DemoNode,
    diagnosis: LogicTransitionDiagnosis | None,
) -> tuple[str, ...]:
    if diagnosis is not None and diagnosis.before_failed_conditions:
        failed_conditions = ", ".join(diagnosis.before_failed_conditions)
        return (
            f"若 {node.node_id} 未触发，先检查对应 logic 翻转前的 failed_conditions: {failed_conditions}。",
            "也可以用 --view explain / --view diagnose 看同一 trace-row window 的 blocker。",
        )
    if node.blocker_hints:
        return node.blocker_hints
    if node.node_id == "logic3":
        return (
            "如果 logic3 没触发，当前诊断窗口显示主要 blocker 是 tra_deg 未过阈值。",
            "还需要 TLS unlocked、engine running、aircraft on ground、N1K limit 与 reverser inhibit 条件同时满足。",
        )
    if node.node_id == "logic4":
        return (
            "如果 logic4 没触发，优先检查 deploy_90_percent_vdt 是否仍为 0。",
            "还需要 TRA 保持在 (-32, 0) 的 reverse travel 区间、aircraft on ground、engine running。",
        )
    if node.node_id == "vdt90":
        return (
            "如果 VDT90 没触发，先检查 PDU motor command 是否已触发以及 deploy_position_percent 是否到达 90%。",
            "这来自 simplified first-cut plant，不是完整真实 actuator 模型。",
        )
    if node.node_id == "thr_lock":
        return (
            "如果 THR_LOCK 没释放，先检查 logic4 是否 active 以及 deploy_90_percent_vdt 是否为 1。",
            "也要确认 TRA、aircraft_on_ground、engine_running 等 logic4 门控条件满足。",
        )
    return (
        f"如果 {node.node_id} 没触发，先沿 catalog 下游 / 上游链路检查 blocker。",
        "switch / command / sensor / plant feedback 节点通常要先看上游 logic 与同一事件窗口的 field changes。",
    )


def _upstream_status_table(result: SimulationResult, node: DemoNode) -> tuple[str, ...]:
    statuses = _upstream_statuses(result, node.node_id)
    if not statuses:
        return ()
    return ("upstream_status_table:", *(_format_upstream_status(status) for status in statuses))


def _blocked_state_outcome(
    node_id: str,
    checkpoint_time_s: float,
    trigger_time_s: float,
) -> tuple[str, ...]:
    if node_id == "logic1":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，checkpoint row 的 logic1 explain 仍显示 "
                "radio_altitude_ft 和 sw1 尚未满足，所以 logic1_active 还没有成立。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "radio altitude / SW1 条件一起到位，logic1_active 与 TLS115 command 同窗触发。"
            ),
        )
    if node_id == "logic2":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，checkpoint row 的 logic2 explain 显示 "
                "engine_running、aircraft_on_ground、reverser_inhibited、eec_enable 已满足，但 sw2 仍未满足。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "sw2 变为 1，logic2_active 与 540V command 在同一事件窗口触发。"
            ),
        )
    if node_id == "logic3":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，checkpoint row 的 logic3 explain 显示 "
                "engine_running、aircraft_on_ground、reverser_inhibited、tls_unlocked_ls、n1k 已满足，"
                "但 tra_deg 仍未过阈值。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "tra_deg 越过 logic3 阈值，logic3_active 与 EEC deploy / PLS power / PDU motor 同窗触发。"
            ),
        )
    if node_id == "logic4":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，checkpoint row 的 logic4 explain 显示 "
                "tra_deg、aircraft_on_ground、engine_running 已满足，但 deploy_90_percent_vdt 仍未满足。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "deploy_90_percent_vdt 变为 1，logic4_active 与 throttle_lock_release_cmd 在同一事件窗口触发。"
            ),
        )
    if node_id == "sw1":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，当前 TRA 还没有形成受控 SW1 switch-window evidence，"
                "所以 sw1 与 logic1_active 都仍未触发。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "观测到 sw1 0->1，并带出 logic1_active 与 TLS115 command。"
            ),
        )
    if node_id == "sw2":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，当前 TRA 还没有形成受控 SW2 switch-window evidence，"
                "所以 sw2 与 logic2_active 都仍未触发。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "观测到 sw2 0->1，并在同一事件窗口带出 logic2_active 与 540V command。"
            ),
        )
    if node_id == "tls115":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，logic1 仍未 active，"
                "所以 tls_115vac_cmd 还没有被置为 1。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "logic1 成立，并在同一事件窗口输出 TLS115 command。"
            ),
        )
    if node_id == "tls_unlocked":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，logic1 与 tls_115vac_cmd 已满足，"
                "但 simplified TLS powered timer 还在积累，所以 tls_unlocked_ls 仍未触发。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "tls_powered_s 达到 unlock evidence 窗口，TLS unlocked sensor 翻转为 1。"
            ),
        )
    if node_id == "etrac_540v":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，当前 trace 还没观测到 sw2 event evidence，"
                "所以 logic2_active 与 etrac_540vdc_cmd 都仍为 0。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "观测到 sw2 0->1，并在同一事件窗口带出 logic2_active 与 540V command。"
            ),
        )
    if node_id == "vdt90":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，PDU motor command 已经满足，"
                "但 deploy_position_percent 仍未到 90%，所以 deploy_90_percent_vdt 还没触发。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "deploy_position_percent 到 90%，VDT90 触发，并带出 logic4 / THR_LOCK 的同窗联动。"
            ),
        )
    if node_id == "thr_lock":
        return (
            (
                f"在 checkpoint={_format_time(checkpoint_time_s)} 时，deploy_90_percent_vdt 仍为 0，"
                "所以 logic4_active 和 throttle_lock_release_cmd 都还没有满足。"
            ),
            (
                f"在当前 nominal-deploy 中，后续约 {_format_time(trigger_time_s)} "
                "deploy_90_percent_vdt 变为 1，logic4_active 与 THR_LOCK release 同窗触发。"
            ),
        )
    return (
        "当前回答只支持少量受控 blocked-state 节点。",
        "如需更多节点，需要先把 checkpoint comparison 显式加入 demo catalog。",
    )


def _blocked_state_possible_causes(
    node: DemoNode,
    statuses: tuple[BlockedEvidenceStatus, ...],
) -> tuple[str, ...]:
    unmet = [status.name for status in statuses if not status.observed]
    unmet_text = ", ".join(unmet) if unmet else "(none)"
    if node.logic_name is not None:
        return (
            f"checkpoint 中尚未满足的 explain 条件: {unmet_text}。",
            f"这些 blocker 直接来自 checkpoint row 的 DeployController.explain({node.logic_name})，不是另一套控制真值。",
            "如需继续排障，可把同一 checkpoint 与激活窗口附近的 events() / logic_transition_diagnostics() 一起看。",
        )
    return (
        f"checkpoint 中尚未满足的 upstream evidence: {unmet_text}。",
        *node.blocker_hints,
    )


def _upstream_statuses(
    result: SimulationResult,
    node_id: str,
) -> tuple[UpstreamEvidenceStatus, ...]:
    if node_id == "sw1":
        sw1_event = _first_event_for_field(result, "sw1")
        time_s = sw1_event.time_s if sw1_event is not None else None
        return (
            _trace_field_status(
                result,
                "tra_deg",
                "tra_deg",
                time_s=time_s,
                observed_when=lambda value: value is not None,
            ),
            _event_field_status(result, "sw1", "sw1"),
            _logic_status(result, "logic1_active", "logic1"),
        )
    if node_id == "sw2":
        sw2_event = _first_event_for_field(result, "sw2")
        time_s = sw2_event.time_s if sw2_event is not None else None
        return (
            _trace_field_status(
                result,
                "tra_deg",
                "tra_deg",
                time_s=time_s,
                observed_when=lambda value: value is not None,
            ),
            _event_field_status(result, "sw2", "sw2"),
            _logic_status(result, "logic2_active", "logic2"),
        )
    if node_id == "tls115":
        return (
            _logic_status(result, "logic1_active", "logic1"),
            _event_field_status(result, "tls_115vac_cmd", "tls_115vac_cmd"),
        )
    if node_id == "tls_unlocked":
        tls_event = _first_event_for_field(result, "tls_unlocked_ls")
        time_s = tls_event.time_s if tls_event is not None else None
        return (
            _logic_status(result, "logic1", "logic1"),
            _event_field_status(result, "tls_115vac_cmd", "tls_115vac_cmd"),
            _trace_field_status(
                result,
                "plant_state.tls_powered_s",
                "plant_state.tls_powered_s",
                time_s=time_s,
                observed_when=lambda value: value > 0.0,
            ),
            _event_field_status(result, "tls_unlocked_ls", "tls_unlocked_ls"),
        )
    if node_id == "etrac_540v":
        return (
            _logic_status(result, "logic2_active", "logic2"),
            _event_field_status(result, "etrac_540vdc_cmd", "etrac_540vdc_cmd"),
        )
    if node_id == "eec_deploy":
        return (
            _logic_status(result, "logic3_active", "logic3"),
            _event_field_status(result, "eec_deploy_cmd", "eec_deploy_cmd"),
        )
    if node_id == "pls_power":
        return (
            _logic_status(result, "logic3_active", "logic3"),
            _event_field_status(result, "pls_power_cmd", "pls_power_cmd"),
        )
    if node_id == "pdu_motor":
        return (
            _logic_status(result, "logic3_active", "logic3"),
            _event_field_status(result, "pdu_motor_cmd", "pdu_motor_cmd"),
        )
    if node_id == "vdt90":
        vdt_event = _first_event_for_field(result, "deploy_90_percent_vdt")
        time_s = vdt_event.time_s if vdt_event is not None else None
        return (
            _event_field_status(result, "pdu_motor_cmd", "pdu_motor_cmd"),
            _trace_field_status(
                result,
                "deploy_position_percent",
                "deploy_position_percent",
                time_s=time_s,
                observed_when=lambda value: value >= 90.0,
            ),
            _event_field_status(result, "deploy_90_percent_vdt", "deploy_90_percent_vdt"),
        )
    if node_id == "thr_lock":
        return (
            _logic_status(result, "logic4_active", "logic4"),
            _event_field_status(result, "deploy_90_percent_vdt", "deploy_90_percent_vdt"),
            _event_field_status(
                result,
                "throttle_lock_release_cmd",
                "throttle_lock_release_cmd",
            ),
        )
    return ()


def _blocked_statuses(
    result: SimulationResult,
    node_id: str,
    checkpoint_time_s: float,
) -> tuple[BlockedEvidenceStatus, ...]:
    if node_id in {"logic1", "logic2", "logic3", "logic4"}:
        return _blocked_logic_condition_statuses(result, node_id, checkpoint_time_s)
    if node_id == "sw1":
        return (
            _blocked_trace_status(
                result,
                "tra_deg",
                "tra_deg",
                checkpoint_time_s,
                observed_when=lambda value: value <= -1.0,
                required="SW1_window",
            ),
            _blocked_trace_status(
                result,
                "sw1",
                "sw1",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "logic1_active",
                "logic1_active",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    if node_id == "sw2":
        return (
            _blocked_trace_status(
                result,
                "tra_deg",
                "tra_deg",
                checkpoint_time_s,
                observed_when=lambda value: value <= -7.0,
                required="SW2_window",
            ),
            _blocked_trace_status(
                result,
                "sw2",
                "sw2",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "logic2_active",
                "logic2_active",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    if node_id == "tls115":
        return (
            _blocked_trace_status(
                result,
                "logic1",
                "logic1_active",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "tls_115vac_cmd",
                "tls_115vac_cmd",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    if node_id == "tls_unlocked":
        return (
            _blocked_trace_status(
                result,
                "logic1",
                "logic1_active",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "tls_115vac_cmd",
                "tls_115vac_cmd",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "plant_state.tls_powered_s",
                "plant_state.tls_powered_s",
                checkpoint_time_s,
                observed_when=lambda value: value >= 0.3,
                required=">=0.3",
            ),
            _blocked_trace_status(
                result,
                "tls_unlocked_ls",
                "tls_unlocked_ls",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    if node_id == "etrac_540v":
        return (
            _blocked_trace_status(
                result,
                "sw2",
                "sw2",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "logic2_active",
                "logic2_active",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "etrac_540vdc_cmd",
                "etrac_540vdc_cmd",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    if node_id == "vdt90":
        return (
            _blocked_trace_status(
                result,
                "pdu_motor_cmd",
                "pdu_motor_cmd",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "deploy_position_percent",
                "deploy_position_percent",
                checkpoint_time_s,
                observed_when=lambda value: value >= 90.0,
                required=">=90",
            ),
            _blocked_trace_status(
                result,
                "deploy_90_percent_vdt",
                "deploy_90_percent_vdt",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    if node_id == "thr_lock":
        return (
            _blocked_trace_status(
                result,
                "deploy_90_percent_vdt",
                "deploy_90_percent_vdt",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "logic4_active",
                "logic4_active",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
            _blocked_trace_status(
                result,
                "throttle_lock_release_cmd",
                "throttle_lock_release_cmd",
                checkpoint_time_s,
                observed_when=lambda value: bool(value),
                required="True",
            ),
        )
    return ()


def _blocked_logic_condition_statuses(
    result: SimulationResult,
    logic_name: str,
    checkpoint_time_s: float,
) -> tuple[BlockedEvidenceStatus, ...]:
    row = _trace_row_at_time(result, checkpoint_time_s)
    if row is None:
        return ()
    logic_explain = row.controller_explain.by_logic_name(logic_name)
    return tuple(
        BlockedEvidenceStatus(
            name=condition.name,
            source="explain_condition",
            observed=condition.passed,
            checkpoint_time_s=row.time_s,
            value=condition.current_value,
            required=_condition_requirement(condition.comparison, condition.threshold_value),
        )
        for condition in logic_explain.conditions
    )


def _logic_status(
    result: SimulationResult,
    name: str,
    logic_name: str,
) -> UpstreamEvidenceStatus:
    diagnosis = _activation_diagnosis(result, logic_name)
    if diagnosis is not None:
        return UpstreamEvidenceStatus(
            name=name,
            source="logic_diagnosis",
            observed=True,
            summary=f"time={_format_time(diagnosis.time_s)}",
        )
    if not result.rows:
        return UpstreamEvidenceStatus(
            name=name,
            source="logic_diagnosis",
            observed=False,
            summary="time=(none) value=(none)",
        )
    row = result.rows[-1]
    active = row.controller_explain.by_logic_name(logic_name).active
    return UpstreamEvidenceStatus(
        name=name,
        source="logic_diagnosis",
        observed=active,
        summary=f"time={_format_time(row.time_s)} value={_format_demo_value(active)}",
    )


def _event_field_status(
    result: SimulationResult,
    name: str,
    field_name: str,
) -> UpstreamEvidenceStatus:
    event = _first_event_for_field(result, field_name)
    if event is not None:
        return UpstreamEvidenceStatus(
            name=name,
            source="event",
            observed=True,
            summary=f"time={_format_time(event.time_s)}",
        )
    if not result.rows:
        return UpstreamEvidenceStatus(
            name=name,
            source="event",
            observed=False,
            summary="time=(none) value=(none)",
        )
    row = result.rows[-1]
    value = getattr(row, field_name)
    return UpstreamEvidenceStatus(
        name=name,
        source="event",
        observed=bool(value),
        summary=f"time={_format_time(row.time_s)} value={_format_demo_value(value)}",
    )


def _trace_field_status(
    result: SimulationResult,
    name: str,
    field_path: str,
    time_s: float | None,
    observed_when,
) -> UpstreamEvidenceStatus:
    row = _trace_row_at_time(result, time_s)
    if row is None:
        return UpstreamEvidenceStatus(
            name=name,
            source="trace_field",
            observed=False,
            summary="time=(none) value=(none)",
        )
    value = _trace_field_value(row, field_path)
    return UpstreamEvidenceStatus(
        name=name,
        source="trace_field",
        observed=bool(observed_when(value)),
        summary=f"time={_format_time(row.time_s)} value={_format_demo_value(value)}",
    )


def _blocked_trace_status(
    result: SimulationResult,
    name: str,
    field_path: str,
    checkpoint_time_s: float,
    observed_when,
    required: str,
) -> BlockedEvidenceStatus:
    row = _trace_row_at_time(result, checkpoint_time_s)
    if row is None:
        return BlockedEvidenceStatus(
            name=name,
            source="trace_field",
            observed=False,
            checkpoint_time_s=None,
            value=None,
            required=required,
        )
    value = _trace_field_value(row, field_path)
    return BlockedEvidenceStatus(
        name=name,
        source="trace_field",
        observed=bool(observed_when(value)),
        checkpoint_time_s=row.time_s,
        value=value,
        required=required,
    )


def _trace_row_at_time(result: SimulationResult, time_s: float | None):
    if not result.rows:
        return None
    if time_s is None:
        return result.rows[-1]
    return min(result.rows, key=lambda row: abs(row.time_s - time_s))


def _trace_field_value(row, field_path: str):
    value = row
    for field_part in field_path.split("."):
        value = getattr(value, field_part)
    return value


def _format_upstream_status(status: UpstreamEvidenceStatus) -> str:
    return (
        f"upstream_status: name={status.name} source={status.source} "
        f"observed={status.observed} {status.summary}"
    )


def _format_blocked_status(status: BlockedEvidenceStatus) -> str:
    checkpoint = _format_time(status.checkpoint_time_s) if status.checkpoint_time_s is not None else "(none)"
    return (
        f"blocked_status: name={status.name} source={status.source} observed={status.observed} "
        f"checkpoint={checkpoint} value={_format_demo_value(status.value)} required={status.required}"
    )


def _first_logic3_time_with_threshold(
    result: SimulationResult,
    proposed_threshold: float,
    config: HarnessConfig,
) -> float | None:
    proposed_config = replace(config, logic3_tra_deg_threshold=proposed_threshold)
    controller_adapter = build_reference_controller_adapter(proposed_config)
    for row in result.rows:
        if controller_adapter.explain(row.resolved_inputs).logic3.active:
            return row.time_s
    return None


def _parse_proposed_threshold(prompt: str) -> float:
    negative_numbers = re.findall(r"(?<![A-Za-z])-\d+(?:\.\d+)?", prompt)
    if negative_numbers:
        return float(negative_numbers[-1])
    return -8.0


def _changed_condition_summary(diagnosis: LogicTransitionDiagnosis) -> str:
    if not diagnosis.changed_conditions:
        return "changed_conditions: (none)"
    changes = []
    for change in diagnosis.changed_conditions:
        changes.append(
            f"{change.name} {change.before_current_value}->{change.after_current_value} "
            f"{change.comparison} {change.threshold_value}"
        )
    return "changed_conditions: " + "; ".join(changes)


def _context_change_summary(
    diagnosis: LogicTransitionDiagnosis,
    wanted: Iterable[tuple[str, str]],
) -> str:
    change_by_key = {
        (change.field_group, change.field_name): change
        for change in diagnosis.context_changes
    }
    parts = []
    for key in wanted:
        change = change_by_key.get(key)
        if change is None:
            continue
        parts.append(
            f"{change.field_group}.{change.field_name} "
            f"{change.before_value}->{change.after_value}"
        )
    return "context_changes: " + ("; ".join(parts) if parts else "(none)")


def _event_summary(
    result: SimulationResult,
    time_s: float,
    wanted_fields: Iterable[str],
) -> str:
    wanted = tuple(wanted_fields)
    for event in result.events():
        if event.time_s != time_s:
            continue
        changes = {
            change.field_name: change
            for change in event.changes
            if change.field_name in wanted
        }
        parts = [
            f"{field_name} {changes[field_name].before}->{changes[field_name].after}"
            for field_name in wanted
            if field_name in changes
        ]
        return f"events@{_format_time(time_s)}: " + ("; ".join(parts) if parts else "(none)")
    return f"events@{_format_time(time_s)}: (none)"


def _first_trigger_time_for_node(result: SimulationResult, node: DemoNode) -> float | None:
    event = _first_event_for_field(result, node.trace_field)
    if event is not None:
        return event.time_s
    if node.logic_name is not None:
        diagnosis = _activation_diagnosis(result, node.logic_name)
        if diagnosis is not None:
            return diagnosis.time_s
    return None


def _pre_trigger_checkpoint_row(result: SimulationResult, trigger_time_s: float | None):
    if trigger_time_s is None:
        return None
    prior_rows = [row for row in result.rows if row.time_s < trigger_time_s]
    if not prior_rows:
        return None
    return prior_rows[-1]


def _failed_conditions_at_time(
    result: SimulationResult,
    logic_name: str,
    time_s: float,
) -> tuple[str, ...]:
    row = _trace_row_at_time(result, time_s)
    if row is None:
        return ()
    logic_explain = row.controller_explain.by_logic_name(logic_name)
    return tuple(condition.name for condition in logic_explain.failed_conditions)


def _blocked_state_target_logic(node_id: str) -> str | None:
    if node_id == "logic1":
        return "logic1"
    if node_id == "logic2":
        return "logic2"
    if node_id == "logic3":
        return "logic3"
    if node_id == "logic4":
        return "logic4"
    if node_id == "sw1":
        return "logic1"
    if node_id == "sw2":
        return "logic2"
    if node_id == "tls115":
        return "logic1"
    if node_id == "tls_unlocked":
        return "logic1"
    if node_id == "etrac_540v":
        return "logic2"
    if node_id == "thr_lock":
        return "logic4"
    return None


def _format_demo_value(value) -> str:
    if isinstance(value, float):
        return f"{value:.3f}".rstrip("0").rstrip(".") or "0"
    if isinstance(value, tuple):
        return "(" + ", ".join(_format_demo_value(part) for part in value) + ")"
    return str(value)


def _format_time(time_s: float) -> str:
    return f"{time_s:.1f}s"


def _format_list(items: tuple[str, ...]) -> list[str]:
    if not items:
        return ["- (none)"]
    return [f"- {item}" for item in items]


def _normalize_prompt(prompt: str) -> str:
    return prompt.lower().replace(" ", "")


def _condition_requirement(comparison: str, threshold_value) -> str:
    if comparison == "==":
        return _format_demo_value(threshold_value)
    if comparison == "between_exclusive" and isinstance(threshold_value, tuple):
        left, right = threshold_value
        return f"between_exclusive {_format_demo_value(left)}..{_format_demo_value(right)}"
    return f"{comparison} {_format_demo_value(threshold_value)}"
