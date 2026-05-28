from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from well_harness.agent_output_contract import (
    build_agent_output_packet,
    run_evidence_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_execution_plan import build_execution_plan_from_task_package
from well_harness.agent_execution_shell import build_execution_evidence_package
from well_harness.agent_repair_loop import (
    run_evidence_agent_repair_loop,
    run_safety_guardian_repair_loop,
)
from well_harness.agent_review_packet import build_candidate_review_packet
from well_harness.agent_task_contract import build_chief_engineer_task_package
from well_harness.requirements_intake.analysis import (
    REQUIREMENTS_INTAKE_KIND,
    RequestPost,
    RequirementsIntakeError,
    THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
    _call_chat_completion,
    _extract_json_object,
    _provider_config,
    _strip_model_json,
    _str,
)


LOGIC_DRAWING_KIND = "ai-fantui-logic-link-drawing"
LOGIC_DRAWING_VERSION = 1
LOGIC_DRAWING_MAX_TOKENS = 8192
L1_L4_CIRCUIT_VIEW_KIND = "ai-fantui-l1-l4-circuit-view"
L1_L4_CIRCUIT_VIEW_VERSION = 1
L1_L4_CIRCUIT_LAYOUT = "deterministic_l1_l4_circuit_v1"
LOGIC_CHANGE_INTERPRETATION_KIND = "ai-fantui-logic-change-interpretation"
LOGIC_CHANGE_INTERPRETATION_VERSION = 1
LOGIC_CHANGE_MAX_TOKENS = 2048
STREAMED_LOGIC_AUTHORING_SESSION_KIND = "ai-fantui-streamed-logic-authoring-session"
STREAMED_LOGIC_AUTHORING_PROPOSAL_KIND = "ai-fantui-streamed-logic-authoring-proposal"
STREAMED_LOGIC_AUTHORING_VERSION = 1
STREAMED_REQUIREMENTS_EDIT_AUTHORIZATION_PHRASE = "AUTHORIZE_REQUIREMENTS_EDIT"
FAULT_INJECTION_PREPARATION_KIND = "ai-fantui-fault-injection-preparation"
FAULT_INJECTION_PREPARATION_VERSION = 1
FAULT_INJECTION_PREPARATION_MAX_TOKENS = 4096
FAULT_INJECTION_SANDBOX_PLAN_KIND = "ai-fantui-fault-injection-sandbox-plan"
FAULT_INJECTION_SANDBOX_PLAN_VERSION = 1
FAULT_INJECTION_SANDBOX_PLAN_MAX_TOKENS = 4096
MAX_DRAWING_INPUT_CHARS = 60_000

L1_L4_LOGIC_IDS = {"logic1", "logic2", "logic3", "logic4"}


THRUST_REVERSER_DEMO_CHAIN_CONTRACT: dict[str, Any] = {
    "target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
    "source": "src/well_harness/static/demo.html#fan-chain-svg",
    "canvas": {"width": 900, "height": 400},
    "nodes": [
        {"id": "sw1", "label": "SW1 · TRA [-1.4°,-6.2°]", "node_kind": "input", "x": 10, "y": 40, "width": 160, "height": 28},
        {"id": "aircraft_on_ground", "label": "aircraft_on_ground", "node_kind": "input", "x": 10, "y": 76, "width": 160, "height": 28},
        {"id": "radio_altitude_ft", "label": "RA < 6 ft", "node_kind": "input", "x": 10, "y": 112, "width": 160, "height": 28},
        {"id": "sw2", "label": "SW2 · TRA [-5°,-9.8°]", "node_kind": "input", "x": 10, "y": 156, "width": 160, "height": 28},
        {"id": "engine_running", "label": "engine_running", "node_kind": "input", "x": 10, "y": 192, "width": 160, "height": 28},
        {"id": "n1k", "label": "N1K < max_n1k", "node_kind": "input", "x": 10, "y": 234, "width": 160, "height": 28},
        {"id": "eec_enable", "label": "eec_enable", "node_kind": "input", "x": 10, "y": 270, "width": 160, "height": 28},
        {"id": "reverser_inhibited", "label": "NOT reverser_inhibited", "node_kind": "input", "x": 10, "y": 306, "width": 160, "height": 28},
        {"id": "logic1", "label": "L1", "node_kind": "logic", "x": 260, "y": 70, "width": 160, "height": 38},
        {"id": "logic2", "label": "L2", "node_kind": "logic", "x": 260, "y": 170, "width": 160, "height": 38},
        {"id": "logic3", "label": "L3", "node_kind": "logic", "x": 260, "y": 260, "width": 160, "height": 50},
        {"id": "tls115", "label": "TLS 115VAC cmd", "node_kind": "component", "x": 500, "y": 56, "width": 160, "height": 28},
        {"id": "tls_unlocked", "label": "TLS_Unlocked LS", "node_kind": "component", "x": 500, "y": 92, "width": 160, "height": 28},
        {"id": "vdt90", "label": "VDT90 (>=90% deploy)", "node_kind": "component", "x": 500, "y": 128, "width": 160, "height": 28},
        {"id": "etrac_540v", "label": "ETRAC 540VDC cmd", "node_kind": "component", "x": 500, "y": 156, "width": 160, "height": 28},
        {"id": "eec_deploy", "label": "EEC_deploy cmd", "node_kind": "output", "x": 500, "y": 246, "width": 160, "height": 28},
        {"id": "pls_power", "label": "PLS power", "node_kind": "output", "x": 500, "y": 282, "width": 160, "height": 28},
        {"id": "pdu_motor", "label": "PDU motor cmd", "node_kind": "output", "x": 500, "y": 318, "width": 160, "height": 28},
        {"id": "logic4", "label": "L4", "node_kind": "logic", "x": 720, "y": 130, "width": 160, "height": 38},
        {"id": "thr_lock", "label": "THR_LOCK release", "node_kind": "output", "x": 720, "y": 200, "width": 160, "height": 34},
    ],
    "edges": [
        {"id": "wire_sw1_logic1", "source": "sw1", "target": "logic1", "route": [{"x": 170, "y": 54}, {"x": 232, "y": 54}, {"x": 232, "y": 78}, {"x": 260, "y": 78}]},
        {"id": "wire_ground_logic2", "source": "aircraft_on_ground", "target": "logic2", "route": [{"x": 170, "y": 90}, {"x": 238, "y": 90}, {"x": 238, "y": 184}, {"x": 260, "y": 184}]},
        {"id": "wire_ra_logic1", "source": "radio_altitude_ft", "target": "logic1", "route": [{"x": 170, "y": 126}, {"x": 232, "y": 126}, {"x": 232, "y": 98}, {"x": 260, "y": 98}]},
        {"id": "wire_logic1_tls115", "source": "logic1", "target": "tls115", "route": [{"x": 420, "y": 89}, {"x": 460, "y": 89}, {"x": 460, "y": 70}, {"x": 500, "y": 70}]},
        {"id": "wire_tls115_tls_unlocked", "source": "tls115", "target": "tls_unlocked", "route": [{"x": 580, "y": 84}, {"x": 580, "y": 92}]},
        {"id": "wire_sw2_logic2", "source": "sw2", "target": "logic2", "route": [{"x": 170, "y": 170}, {"x": 234, "y": 170}, {"x": 234, "y": 180}, {"x": 260, "y": 180}]},
        {"id": "wire_engine_logic2", "source": "engine_running", "target": "logic2", "route": [{"x": 170, "y": 206}, {"x": 234, "y": 206}, {"x": 234, "y": 196}, {"x": 260, "y": 196}]},
        {"id": "wire_tls_unlocked_logic3", "source": "tls_unlocked", "target": "logic3", "route": [{"x": 660, "y": 106}, {"x": 702, "y": 106}, {"x": 702, "y": 28}, {"x": 246, "y": 28}, {"x": 246, "y": 276}, {"x": 260, "y": 276}]},
        {"id": "wire_logic2_etrac", "source": "logic2", "target": "etrac_540v", "route": [{"x": 420, "y": 189}, {"x": 460, "y": 189}, {"x": 460, "y": 170}, {"x": 500, "y": 170}]},
        {"id": "wire_n1k_logic3", "source": "n1k", "target": "logic3", "route": [{"x": 170, "y": 248}, {"x": 230, "y": 248}, {"x": 230, "y": 270}, {"x": 260, "y": 270}]},
        {"id": "wire_eec_logic2", "source": "eec_enable", "target": "logic2", "route": [{"x": 170, "y": 284}, {"x": 240, "y": 284}, {"x": 240, "y": 200}, {"x": 260, "y": 200}]},
        {"id": "wire_engine_logic3", "source": "engine_running", "target": "logic3", "route": [{"x": 170, "y": 206}, {"x": 244, "y": 206}, {"x": 244, "y": 281}, {"x": 260, "y": 281}]},
        {"id": "wire_ground_logic3", "source": "aircraft_on_ground", "target": "logic3", "route": [{"x": 170, "y": 90}, {"x": 244, "y": 90}, {"x": 244, "y": 290}, {"x": 260, "y": 290}]},
        {"id": "wire_inh_logic1", "source": "reverser_inhibited", "target": "logic1", "route": [{"x": 170, "y": 320}, {"x": 226, "y": 320}, {"x": 226, "y": 88}, {"x": 260, "y": 88}]},
        {"id": "wire_inh_logic2", "source": "reverser_inhibited", "target": "logic2", "route": [{"x": 226, "y": 188}, {"x": 260, "y": 188}]},
        {"id": "wire_inh_logic3", "source": "reverser_inhibited", "target": "logic3", "route": [{"x": 226, "y": 304}, {"x": 260, "y": 304}]},
        {"id": "wire_logic3_eec", "source": "logic3", "target": "eec_deploy", "route": [{"x": 420, "y": 279}, {"x": 465, "y": 279}, {"x": 465, "y": 260}, {"x": 500, "y": 260}]},
        {"id": "wire_logic3_pls", "source": "logic3", "target": "pls_power", "route": [{"x": 465, "y": 279}, {"x": 465, "y": 296}, {"x": 500, "y": 296}]},
        {"id": "wire_logic3_pdu", "source": "logic3", "target": "pdu_motor", "route": [{"x": 465, "y": 296}, {"x": 465, "y": 332}, {"x": 500, "y": 332}]},
        {"id": "wire_pdu_vdt90", "source": "pdu_motor", "target": "vdt90", "route": [{"x": 660, "y": 332}, {"x": 690, "y": 332}, {"x": 690, "y": 142}, {"x": 660, "y": 142}]},
        {"id": "wire_vdt90_logic4", "source": "vdt90", "target": "logic4", "route": [{"x": 660, "y": 142}, {"x": 720, "y": 142}]},
        {"id": "wire_logic3_logic4", "source": "logic3", "target": "logic4", "route": [{"x": 420, "y": 298}, {"x": 440, "y": 298}, {"x": 440, "y": 368}, {"x": 690, "y": 368}, {"x": 690, "y": 162}, {"x": 720, "y": 162}]},
        {"id": "wire_logic4_thr_lock", "source": "logic4", "target": "thr_lock", "route": [{"x": 800, "y": 168}, {"x": 800, "y": 200}]},
    ],
}

DEMO_NODE_TO_REQUIREMENT_NODE: dict[str, str] = {
    "sw1": "sw1",
    "aircraft_on_ground": "",
    "radio_altitude_ft": "ra_lt_6ft",
    "sw2": "sw2",
    "engine_running": "",
    "n1k": "",
    "eec_enable": "",
    "reverser_inhibited": "",
    "logic1": "logic1",
    "logic2": "logic2",
    "logic3": "logic3",
    "tls115": "tls_cmd",
    "tls_unlocked": "tls_cmd",
    "vdt90": "vdt_90",
    "etrac_540v": "etrac_cmd",
    "eec_deploy": "pls_pdu_cmd",
    "pls_power": "pls_pdu_cmd",
    "pdu_motor": "pls_pdu_cmd",
    "logic4": "logic4",
    "thr_lock": "thr_lock_release",
}
DEMO_EDGE_TO_REQUIREMENT_PAIR: dict[tuple[str, str], tuple[str, str] | None] = {
    ("sw1", "logic1"): ("sw1", "logic1"),
    ("radio_altitude_ft", "logic1"): ("ra_lt_6ft", "logic1"),
    ("logic1", "tls115"): ("logic1", "tls_cmd"),
    ("tls115", "tls_unlocked"): ("logic1", "tls_cmd"),
    ("sw2", "logic2"): ("sw2", "logic2"),
    ("logic2", "etrac_540v"): ("logic2", "etrac_cmd"),
    ("tls_unlocked", "logic3"): ("tls_cmd", "logic3"),
    ("logic2", "logic3"): ("logic2", "logic3"),
    ("logic3", "pls_power"): ("logic3", "pls_pdu_cmd"),
    ("logic3", "pdu_motor"): ("logic3", "pls_pdu_cmd"),
    ("pdu_motor", "vdt90"): ("pls_pdu_cmd", "vdt_90"),
    ("vdt90", "logic4"): ("vdt_90", "logic4"),
    ("logic3", "logic4"): ("logic3", "pls_pdu_cmd"),
    ("logic4", "thr_lock"): ("logic4", "thr_lock_release"),
}
DEMO_NODE_ANCHOR_FALLBACKS: dict[str, dict[str, tuple[Any, ...]]] = {
    "radio_altitude_ft": {
        "nodes": ("ra_lt_6ft",),
        "groups": ("logic1",),
        "edges": (("ra_lt_6ft", "logic1"),),
    },
    "sw1": {
        "nodes": ("sw1", "tra_reverse_range"),
        "groups": ("logic1",),
        "edges": (("sw1", "logic1"),),
    },
    "sw2": {
        "nodes": ("sw2", "tra_reverse_range"),
        "groups": ("logic2",),
        "edges": (("sw2", "logic2"),),
    },
    "vdt90": {
        "nodes": ("vdt_90",),
        "groups": ("logic4",),
        "edges": (("vdt_90", "logic4"),),
    },
    "thr_lock": {
        "nodes": ("thr_lock_release",),
        "groups": ("logic4",),
        "edges": (("logic4", "thr_lock_release"),),
    },
}
DEMO_ACTIVE_NODES = {"aircraft_on_ground", "radio_altitude_ft", "engine_running", "eec_enable"}
DEMO_BLOCKED_NODES = {"logic1", "logic2", "logic3", "logic4", "thr_lock"}
DEMO_WIRE_JUNCTIONS: tuple[dict[str, Any], ...] = (
    {"x": 226, "y": 188, "source": "reverser_inhibited", "state": "idle"},
    {"x": 226, "y": 304, "source": "reverser_inhibited", "state": "idle"},
    {"x": 465, "y": 279, "source": "logic3", "state": "idle"},
    {"x": 465, "y": 296, "source": "logic3", "state": "idle"},
)


def _limited_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "status": payload.get("status"),
        "summary_zh": payload.get("summary_zh"),
        "source_document": payload.get("source_document"),
        "reconstruction_target": payload.get("reconstruction_target") or "",
        "concept_logic_nodes": payload.get("concept_logic_nodes") or [],
        "concept_edges": payload.get("concept_edges") or [],
        "document_assumptions": payload.get("document_assumptions") or [],
        "open_questions": payload.get("open_questions") or [],
        "ready_for_logic_builder": payload.get("ready_for_logic_builder"),
        "requirement_groups": payload.get("requirement_groups") or [],
        "source_scope": payload.get("source_scope") or {},
        "reading_burden": payload.get("reading_burden") or {},
        "deterministic_preparse": payload.get("deterministic_preparse") or {},
    }
    text = json.dumps(compact, ensure_ascii=False)
    if len(text) <= MAX_DRAWING_INPUT_CHARS:
        return compact
    compact["concept_logic_nodes"] = compact["concept_logic_nodes"][:24]
    compact["concept_edges"] = compact["concept_edges"][:36]
    compact["input_truncated"] = True
    return compact


def _reconstruction_target(payload: dict[str, Any]) -> str:
    target = _str(payload.get("reconstruction_target"))
    return target if target == THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET else ""


def _reference_contract_prompt_block(requirements_payload: dict[str, Any]) -> str:
    if _reconstruction_target(requirements_payload) != THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET:
        return ""
    return (
        "\n\n[反推逻辑演示舱一比一重构目标]\n"
        "本轮不是自由发挥的概念图，而是复刻 src/well_harness/static/demo.html#fan-chain-svg。"
        "必须使用下方 contract 中的 canvas、node id、label、node_kind、坐标、尺寸、edge id、source、target、route。"
        "不要新增节点或连线，不要省略节点或连线；parameter_panels 必须返回 []，因为演示舱 SVG 把参数写在节点标签里。"
        "如果你不确定语义，仍然按 contract 复刻图纸，语义说明放到 drawing_notes。\n"
        f"{json.dumps(THRUST_REVERSER_DEMO_CHAIN_CONTRACT, ensure_ascii=False)}"
    )


def _payload_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _safe_contract_id(prefix: str, value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", _str(value)).strip("_").upper()
    return f"{prefix}-{normalized or 'CANDIDATE'}"


def _contract_requirement_ids(requirements_payload: dict[str, Any]) -> list[str]:
    groups = requirements_payload.get("requirement_groups")
    if isinstance(groups, list):
        requirement_ids = [
            _safe_contract_id("REQ", _str(group.get("id")))
            for group in groups
            if isinstance(group, dict) and _str(group.get("id"))
        ]
        if requirement_ids:
            return requirement_ids
    if requirements_payload.get("concept_logic_nodes") or requirements_payload.get("concept_edges"):
        return ["REQ-DRAWING-STRUCTURE"]
    return ["REQ-UNSPECIFIED-CANDIDATE"]


def _logic_ir_packet_payload(
    drawing: dict[str, Any],
    requirements_payload: dict[str, Any],
) -> dict[str, Any]:
    nodes = [node for node in drawing.get("nodes", []) if isinstance(node, dict) and _str(node.get("id"))]
    edges = [edge for edge in drawing.get("edges", []) if isinstance(edge, dict) and _str(edge.get("id"))]
    node_ids = [_str(node.get("id")) for node in nodes]
    edge_sources = {_str(edge.get("source")) for edge in edges}
    edge_targets = {_str(edge.get("target")) for edge in edges}
    entry_nodes = [node_id for node_id in node_ids if node_id in edge_sources and node_id not in edge_targets]
    if not entry_nodes:
        entry_nodes = node_ids[:1]
    requirement_ids = _contract_requirement_ids(requirements_payload)
    transitions: list[dict[str, Any]] = [
        {
            "id": f"T_ENTRY_{index:03d}",
            "from": "__START__",
            "to": node_id,
            "guard": "",
            "guard_signals": [],
            "priority": "normal",
            "trace": {"requirements": requirement_ids},
        }
        for index, node_id in enumerate(entry_nodes, start=1)
    ]
    transitions.extend(
        {
            "id": _safe_contract_id("T", _str(edge.get("id"))),
            "from": _str(edge.get("source")),
            "to": _str(edge.get("target")),
            "guard": f"{_str(edge.get('id'))}_candidate_link_active",
            "guard_signals": [_str(edge.get("source"))],
            "priority": "normal",
            "trace": {"requirements": requirement_ids},
        }
        for edge in edges
    )
    return {
        "requirements": [
            {
                "id": requirement_id,
                "text": "Candidate requirement grouping from requirements-intake payload.",
            }
            for requirement_id in requirement_ids
        ],
        "signals": [{"name": node_id} for node_id in node_ids],
        "logic_ir": {
            "id": "REQ_INTAKE_LOGIC_DRAWING_CANDIDATE",
            "type": "directed_candidate_graph",
            "initial_state": "__START__",
            "states": [
                {"id": "__START__", "label": "candidate graph entry"},
                *[
                    {
                        "id": _str(node.get("id")),
                        "label": _str(node.get("label"), _str(node.get("id"))),
                        "node_kind": _str(node.get("node_kind"), "component"),
                    }
                    for node in nodes
                ],
            ],
            "transitions": transitions,
            "invariants": [],
        },
        "test_scenarios": [
            {
                "id": "TC-CANDIDATE-GRAPH-STRUCTURE",
                "purpose": "Verify candidate drawing graph is represented in machine-readable IR.",
                "covers": requirement_ids,
            }
        ],
        "simulation_results": [
            {
                "scenario_id": "TC-CANDIDATE-GRAPH-STRUCTURE",
                "status": "pass",
            }
        ],
        "drawing_summary": {
            "kind": drawing.get("kind"),
            "node_count": len(nodes),
            "edge_count": len(edges),
            "source_requirements_sha256": drawing.get("source_requirements_sha256"),
        },
    }


def _attach_logic_ir_agent_contracts(
    drawing: dict[str, Any],
    requirements_payload: dict[str, Any],
) -> dict[str, Any]:
    source_sha = _str(drawing.get("source_requirements_sha256")) or _payload_sha256(requirements_payload)
    packet = build_agent_output_packet(
        agent_name="LogicIRAgent",
        task_id=f"LOGIC-BUILDER-{source_sha[:12] or 'UNHASHED'}",
        input_artifacts=[
            f"{REQUIREMENTS_INTAKE_KIND}:{source_sha[:12] or 'unhashed'}",
            f"{LOGIC_DRAWING_KIND}:v{LOGIC_DRAWING_VERSION}",
        ],
        output_artifacts=["logic_ir:REQ_INTAKE_LOGIC_DRAWING_CANDIDATE"],
        candidate_state="logic_ir_candidate",
        assumptions=[
            "The embedded IR is a candidate graph representation of the drawing payload, not controller truth.",
            "Pass/fail evidence is limited to deterministic structure and trace checks for this route.",
        ],
        open_issues=[],
        confidence_level="medium",
        confidence_reason="IR was derived deterministically from requirements-intake and logic-builder candidate payloads.",
        deterministic_checks_passed=True,
        failed_checks=[],
        human_review_required=True,
        payload=_logic_ir_packet_payload(drawing, requirements_payload),
    )
    safety_report = run_safety_guardian_checks(packet)
    evidence_report = run_evidence_agent_checks(packet)
    combined_findings = [*safety_report.get("findings", []), *evidence_report.get("findings", [])]
    packet["agent_output"]["validation"]["deterministic_checks_passed"] = not combined_findings
    packet["agent_output"]["validation"]["failed_checks"] = combined_findings
    validate_agent_output_contract(packet)
    drawing["agent_output_contract_v0_1"] = {
        "logic_ir": packet,
        "safety_guardian": safety_report,
        "evidence": evidence_report,
    }
    drawing["chief_engineer_task_package_v0_1"] = build_chief_engineer_task_package(
        drawing["agent_output_contract_v0_1"],
        source_artifact_id=f"{LOGIC_DRAWING_KIND}:{source_sha[:12] or 'unhashed'}",
    )
    drawing["execution_plan_v0_1"] = build_execution_plan_from_task_package(
        drawing["chief_engineer_task_package_v0_1"]
    )
    drawing["execution_evidence_package_v0_1"] = build_execution_evidence_package(
        drawing["chief_engineer_task_package_v0_1"]
    )
    repair_loop_results = _candidate_repair_loop_results(
        packet,
        safety_report=safety_report,
        evidence_report=evidence_report,
    )
    drawing["candidate_review_packet_v0_1"] = build_candidate_review_packet(
        drawing["agent_output_contract_v0_1"],
        task_package=drawing["chief_engineer_task_package_v0_1"],
        execution_plan=drawing["execution_plan_v0_1"],
        execution_evidence_package=drawing["execution_evidence_package_v0_1"],
        repair_loop_results=repair_loop_results,
    )
    return drawing


def _candidate_repair_loop_results(
    packet: dict[str, Any],
    *,
    safety_report: dict[str, Any],
    evidence_report: dict[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if safety_report.get("findings"):
        results.append(run_safety_guardian_repair_loop(packet))
    supported_evidence_codes = {
        "EV_SIMULATION_RESULT_FAILED",
        "EV_TEST_RESULT_MISSING",
    }
    evidence_findings = evidence_report.get("findings", [])
    if any(
        isinstance(finding, dict) and finding.get("code") in supported_evidence_codes
        for finding in evidence_findings
    ):
        results.append(run_evidence_agent_repair_loop(packet))
    return results


def _limited_drawing_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "kind": payload.get("kind"),
        "version": payload.get("version"),
        "status": payload.get("status"),
        "summary_zh": payload.get("summary_zh"),
        "canvas": payload.get("canvas") or {},
        "nodes": payload.get("nodes") or [],
        "edges": payload.get("edges") or [],
        "parameter_panels": payload.get("parameter_panels") or [],
        "drawing_notes": payload.get("drawing_notes") or [],
    }
    text = json.dumps(compact, ensure_ascii=False)
    if len(text) <= MAX_DRAWING_INPUT_CHARS:
        return compact
    compact["nodes"] = compact["nodes"][:18]
    compact["edges"] = compact["edges"][:32]
    compact["parameter_panels"] = compact["parameter_panels"][:8]
    compact["input_truncated"] = True
    return compact


def _drawing_prompt(requirements_payload: dict[str, Any]) -> list[dict[str, str]]:
    compact = _limited_payload(requirements_payload)
    reference_contract_block = _reference_contract_prompt_block(requirements_payload)
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的逻辑链路绘图助手。你必须独立完成初版概念逻辑电路图布局，"
                "前端只会按你输出的 JSON 坐标和路径渲染。不得输出可执行仿真、不得修改 controller truth、"
                "不得要求人工继续绘图。只输出一个完整 JSON 对象。"
            ),
        },
        {
            "role": "user",
            "content": (
                "根据已澄清需求 JSON 生成逻辑链路绘制 JSON。\n"
                "固定字段：summary_zh, canvas, nodes, edges, parameter_panels, drawing_notes。\n"
                "canvas: {width,height}，推荐 1280x760；超过18个节点时可用 1600x980。\n"
                "nodes: 8-24 个，每个含 id,label,node_kind(input|logic|output|component),x,y,width,height,description_zh；"
                "必须覆盖已澄清需求 JSON 中 concept_logic_nodes 的所有 id；不得省略已澄清输出节点；"
                "坐标必须是数字，采用左到右信号流：输入在左、逻辑门中间、输出/执行部件在右；L1-L4垂直分层或顺序排列。\n"
                "edges: 每条含 id,source,target,label,route；必须覆盖 concept_edges 的主要逻辑关系，"
                "source/target 使用 nodes 中的 id；route 至少 2 个点，每点含 x,y，必须使用正交折线，不要让连线穿过主要节点文字。\n"
                "parameter_panels: 3-6 个，含 id,node_id,label,unit,min,max,default,x,y,width,height；"
                "每个 node_id 最多一个参数面板；SW1/SW2/TRA 等区间参数合并在一个面板标签里。"
                "参数面板必须依附在对应节点外侧，不能覆盖节点本体或其他参数面板；"
                "对左侧输入节点，优先放在节点右侧：x约等于node.x+node.width+16，y接近node.y；"
                "对中间逻辑节点，优先放在节点下方：y约等于node.y+node.height+12；参数面板高度至少76。\n"
                "drawing_notes 最多 4 条，说明模型如何布局。输出紧凑 JSON：不要 Markdown，不要解释 JSON 之外内容，不要缩进和多余换行。\n\n"
                f"已澄清需求 JSON：\n{json.dumps(compact, ensure_ascii=False)}"
                f"{reference_contract_block}"
            ),
        },
    ]


def _drawing_repair_prompt(
    requirements_payload: dict[str, Any],
    broken_response: str,
    error: RequirementsIntakeError,
) -> list[dict[str, str]]:
    compact = _limited_payload(requirements_payload)
    reference_contract_block = _reference_contract_prompt_block(requirements_payload)
    error_payload = {
        "code": error.code,
        "message": error.message,
        "details": error.details,
    }
    response_excerpt = broken_response.strip()
    if len(response_excerpt) > 6000:
        response_excerpt = response_excerpt[:6000] + "\n[TRUNCATED]"
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的逻辑链路绘图 JSON 修复助手。上一轮模型输出未通过结构校验，"
                "你必须只返回一份完整、可渲染、覆盖已澄清需求节点和主要连线的 JSON 图纸。"
                "不得要求前端补图，不得输出局部 patch，不得修改 controller truth。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请修复上一轮逻辑链路绘图 JSON。\n"
                "固定字段仍为：summary_zh, canvas, nodes, edges, parameter_panels, drawing_notes。\n"
                "nodes 必须覆盖已澄清需求 JSON 中 concept_logic_nodes 的所有 id；"
                "edges 必须覆盖 concept_edges 的主要 source/target 关系并为每条边提供 route；"
                "parameter_panels 必须引用存在的 node_id。"
                "如果存在 reconstruction_target，则还必须逐项满足目标 contract 的节点和连线集合。"
                "只输出完整 JSON 对象，不要 Markdown，不要解释 JSON 之外内容。\n\n"
                f"校验错误 JSON：\n{json.dumps(error_payload, ensure_ascii=False)}\n\n"
                f"已澄清需求 JSON：\n{json.dumps(compact, ensure_ascii=False)}\n\n"
                f"上一轮模型输出摘录：\n{response_excerpt}"
                f"{reference_contract_block}"
            ),
        },
    ]


def _change_interpretation_prompt(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    annotation_text: str,
    target_node_id: str,
    annotation_batch: list[dict[str, str]] | None = None,
    selected_nodes: list[str] | None = None,
    selected_edges: list[str] | None = None,
) -> list[dict[str, str]]:
    compact_requirements = _limited_payload(requirements_payload)
    compact_drawing = _limited_drawing_payload(drawing_payload)
    batch = annotation_batch if isinstance(annotation_batch, list) else []
    selected_payload = {
        "selected_nodes": selected_nodes if isinstance(selected_nodes, list) else [],
        "selected_edges": selected_edges if isinstance(selected_edges, list) else [],
        "annotation_batch": batch,
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的逻辑图修改意图理解助手。你只负责理解工程师批注、"
                "回到原需求中定位相关内容，并向用户确认意图；不要更新图纸，不要输出仿真或可执行内容。"
                "只输出一个完整 JSON 对象。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请根据原始已澄清需求、当前逻辑链路图和工程师批注，输出修改意图理解 JSON。\n"
                "固定字段：understanding_zh, requirements_match_zh, affected_nodes, affected_edges, "
                "affected_parameter_panels, proposed_changes, annotation_batch_summary_zh, "
                "conflict_summary_zh, annotation_groups, confirmation_question_zh。\n"
                "affected_* 必须只使用当前图纸中已经存在的 id；无法确定时返回空数组。"
                "proposed_changes 最多 5 条，confirmation_question_zh 必须是面向用户的一句话。"
                "如果存在多点批注，请归并重复批注，指出互相冲突或需要工程师二次确认的地方，"
                "annotation_groups 最多 4 组，每组包含 group_label, annotation_ids, summary_zh。"
                "不要更新图纸，不要返回 nodes/edges/parameter_panels 的新版本。\n\n"
                f"用户选中节点：{target_node_id or '未指定'}\n"
                f"工程师批注：{annotation_text}\n\n"
                f"多点批注 JSON：\n{json.dumps(selected_payload, ensure_ascii=False)}\n\n"
                f"已澄清需求 JSON：\n{json.dumps(compact_requirements, ensure_ascii=False)}\n\n"
                f"当前图纸 JSON：\n{json.dumps(compact_drawing, ensure_ascii=False)}"
            ),
        },
    ]


def _drawing_update_prompt(drawing_payload: dict[str, Any], interpretation_payload: dict[str, Any]) -> list[dict[str, str]]:
    compact_drawing = _limited_drawing_payload(drawing_payload)
    compact_interpretation = {
        "kind": interpretation_payload.get("kind"),
        "status": interpretation_payload.get("status"),
        "target_node_id": interpretation_payload.get("target_node_id"),
        "annotation_text": interpretation_payload.get("annotation_text"),
        "understanding_zh": interpretation_payload.get("understanding_zh"),
        "requirements_match_zh": interpretation_payload.get("requirements_match_zh"),
        "affected_nodes": interpretation_payload.get("affected_nodes") or [],
        "affected_edges": interpretation_payload.get("affected_edges") or [],
        "affected_parameter_panels": interpretation_payload.get("affected_parameter_panels") or [],
        "proposed_changes": interpretation_payload.get("proposed_changes") or [],
    }
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的逻辑链路图更新助手。用户已经确认修改意图，你必须根据确认后的理解"
                "返回完整更新后的概念图纸 JSON。不得输出可执行仿真、不得修改 controller truth。"
                "只输出一个完整 JSON 对象。"
            ),
        },
        {
            "role": "user",
            "content": (
                "返回完整更新后的逻辑链路绘制 JSON。\n"
                "固定字段：summary_zh, canvas, nodes, edges, parameter_panels, drawing_notes。\n"
                "保持原有 id 稳定；确需新增节点/连线时才新增 id。"
                "edges 每条必须含 route 且 route 至少 2 个点；parameter_panels 必须依附节点外侧且高度至少76。"
                "输出紧凑 JSON：不要 Markdown，不要解释 JSON 之外内容。\n\n"
                f"已由用户确认的修改理解 JSON：\n{json.dumps(compact_interpretation, ensure_ascii=False)}\n\n"
                f"当前图纸 JSON：\n{json.dumps(compact_drawing, ensure_ascii=False)}"
            ),
        },
    ]


def _limited_change_history(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value[-8:]:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "status": item.get("status"),
                "target_node_id": item.get("target_node_id"),
                "annotation_text": item.get("annotation_text"),
                "understanding_zh": item.get("understanding_zh"),
                "updated_summary_zh": item.get("updated_summary_zh"),
            }
        )
    return items


def _critical_fault_nodes_for_prompt(drawing_payload: dict[str, Any]) -> list[dict[str, str]]:
    critical_ids = _critical_fault_node_ids(drawing_payload)
    nodes: list[dict[str, str]] = []
    for item in drawing_payload.get("nodes", []):
        if not isinstance(item, dict):
            continue
        node_id = _str(item.get("id"))
        if node_id not in critical_ids:
            continue
        nodes.append(
            {
                "id": node_id,
                "label": _str(item.get("label"), node_id)[:80],
                "node_kind": _str(item.get("node_kind"), "logic")[:32],
            }
        )
    return nodes


def _fault_injection_prompt(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    change_history: list[dict[str, Any]],
) -> list[dict[str, str]]:
    compact_requirements = _limited_payload(requirements_payload)
    compact_drawing = _limited_drawing_payload(drawing_payload)
    compact_history = _limited_change_history(change_history)
    critical_fault_nodes = _critical_fault_nodes_for_prompt(drawing_payload)
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的故障注入准备助手。你只生成概念性候选、注入点和需要工程师确认的边界；"
                "不要执行仿真、不要输出可操作控制步骤、不要修改 controller truth、不要声称通过认证。"
                "只输出一个完整 JSON 对象。"
            ),
        },
        {
            "role": "user",
            "content": (
                "根据已澄清需求、当前逻辑链路图和 change_history，输出故障注入准备 JSON。\n"
                "固定字段：summary_zh, assumptions, fault_scenarios, injection_points, boundary_questions, workflow_notes。\n"
                "fault_scenarios: 3-8 个，每个含 id,label,node_id,fault_type,rationale_zh,expected_effect_zh,"
                "observable_signals,severity(low|medium|high)。node_id 必须来自当前图纸 nodes。\n"
                "fault_scenarios 必须覆盖当前图纸中的输入节点、输出节点和带参数面板的节点。\n"
                "必须覆盖 critical_fault_nodes 中列出的每一个 node_id；覆盖可以出现在 fault_scenarios 或 injection_points，"
                "但每个 critical node_id 至少出现一次。不要省略 sw_and、engine_run、eec_enable 这类逻辑聚合或门控节点。\n"
                "injection_points: 3-8 个，每个含 id,node_id,parameter_panel_id,signal_name,injection_mode,"
                "safe_boundary_zh。node_id 必须来自当前图纸 nodes；parameter_panel_id 如无法匹配可为空字符串。\n"
                "boundary_questions: 2-6 个，每个含 id,prompt_zh,rationale_zh,blocks，blocks 固定为 fault_injection。"
                "workflow_notes 最多 4 条，说明后续进入故障注入前还需确认什么。"
                "输出紧凑 JSON：不要 Markdown，不要解释 JSON 之外内容。\n\n"
                f"已澄清需求 JSON：\n{json.dumps(compact_requirements, ensure_ascii=False)}\n\n"
                f"当前图纸 JSON：\n{json.dumps(compact_drawing, ensure_ascii=False)}\n\n"
                f"critical_fault_nodes JSON：\n{json.dumps(critical_fault_nodes, ensure_ascii=False)}\n\n"
                f"change_history JSON：\n{json.dumps(compact_history, ensure_ascii=False)}"
            ),
        },
    ]


def _fault_injection_repair_prompt(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    change_history: list[dict[str, Any]],
    broken_response: str,
    error: RequirementsIntakeError,
) -> list[dict[str, str]]:
    compact_requirements = _limited_payload(requirements_payload)
    compact_drawing = _limited_drawing_payload(drawing_payload)
    compact_history = _limited_change_history(change_history)
    critical_fault_nodes = _critical_fault_nodes_for_prompt(drawing_payload)
    error_payload = {"code": error.code, "message": error.message, "details": error.details}
    response_excerpt = broken_response.strip()
    if len(response_excerpt) > 6000:
        response_excerpt = response_excerpt[:6000] + "\n[TRUNCATED]"
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的故障注入准备 JSON 修复助手。上一轮模型输出未通过结构校验，"
                "你必须只返回完整故障准备 JSON，不得要求前端补候选，不得执行仿真，不得修改 controller truth。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请修复上一轮故障注入准备 JSON。\n"
                "固定字段：summary_zh, assumptions, fault_scenarios, injection_points, boundary_questions, workflow_notes。\n"
                "fault_scenarios 必须是非空数组，node_id 必须来自当前图纸 nodes；"
                "injection_points 如返回也必须引用当前图纸 nodes；boundary_questions 必须用于 fault_injection 边界确认。"
                "必须覆盖 critical_fault_nodes 中列出的每一个 node_id；如校验错误包含 missing_critical_nodes，"
                "这些 node_id 必须逐一补入 fault_scenarios 或 injection_points。"
                "只输出完整 JSON 对象，不要 Markdown，不要解释 JSON 之外内容。\n\n"
                f"校验错误 JSON：\n{json.dumps(error_payload, ensure_ascii=False)}\n\n"
                f"已澄清需求 JSON：\n{json.dumps(compact_requirements, ensure_ascii=False)}\n\n"
                f"当前图纸 JSON：\n{json.dumps(compact_drawing, ensure_ascii=False)}\n\n"
                f"critical_fault_nodes JSON：\n{json.dumps(critical_fault_nodes, ensure_ascii=False)}\n\n"
                f"change_history JSON：\n{json.dumps(compact_history, ensure_ascii=False)}\n\n"
                f"上一轮模型输出摘录：\n{response_excerpt}"
            ),
        },
    ]


def _limited_fault_preparation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "kind": payload.get("kind"),
        "version": payload.get("version"),
        "status": payload.get("status"),
        "summary_zh": payload.get("summary_zh"),
        "assumptions": payload.get("assumptions") or [],
        "fault_scenarios": payload.get("fault_scenarios") or [],
        "injection_points": payload.get("injection_points") or [],
        "boundary_questions": payload.get("boundary_questions") or [],
        "boundary_answers": payload.get("boundary_answers") or [],
        "workflow_notes": payload.get("workflow_notes") or [],
    }
    text = json.dumps(compact, ensure_ascii=False)
    if len(text) <= MAX_DRAWING_INPUT_CHARS:
        return compact
    compact["fault_scenarios"] = compact["fault_scenarios"][:8]
    compact["injection_points"] = compact["injection_points"][:8]
    compact["boundary_questions"] = compact["boundary_questions"][:6]
    compact["boundary_answers"] = compact["boundary_answers"][:6]
    compact["input_truncated"] = True
    return compact


def _limited_boundary_answers(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    answers: list[dict[str, str]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        answer = _str(item.get("answer_zh") or item.get("answer")).strip()
        if not answer:
            continue
        answers.append(
            {
                "id": _str(item.get("id") or item.get("question_id"), f"boundary_{index}")[:64],
                "prompt_zh": _str(item.get("prompt_zh") or item.get("prompt"))[:220],
                "answer_zh": answer[:500],
            }
        )
        if len(answers) >= 8:
            break
    return answers


def _fault_injection_sandbox_plan_prompt(
    fault_injection_preparation_payload: dict[str, Any],
    boundary_answers: list[dict[str, Any]],
) -> list[dict[str, str]]:
    compact_preparation = _limited_fault_preparation_payload(fault_injection_preparation_payload)
    compact_answers = _limited_boundary_answers(boundary_answers)
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的沙盒故障注入配置建议助手。你只生成 dry-run 沙盒配置建议、"
                "预期观测点和审查清单；不要调用 /api/tick，不要执行仿真，不要输出真实控制步骤，"
                "不要修改 controller truth。只输出一个完整 JSON 对象。"
            ),
        },
        {
            "role": "user",
            "content": (
                "根据故障注入准备草稿和 boundary_answers，输出沙盒故障注入建议 JSON。\n"
                "固定字段：summary_zh, sandbox_injection_plan, observation_points, review_checklist, "
                "execution_contract, workflow_notes。\n"
                "sandbox_injection_plan: 1-8 个，每个含 id,fault_scenario_id,node_id,signal_name,"
                "injection_mode,safe_range_zh,duration_ms,expected_effect_zh。"
                "fault_scenario_id 必须来自 fault_scenarios；node_id 优先来自对应 scenario 或 injection_points。"
                "必须覆盖 fault_scenarios 中的每一个 id；每个故障场景至少对应一个 sandbox_injection_plan。"
                "observation_points: 1-8 个，每个含 id,node_id,signal_name,check_zh。"
                "review_checklist: 2-8 个，每个含 id,category,condition_zh,pass_criteria_zh。"
                "execution_contract 必须表达 run_tick=false, simulate=false, dry_run_only=true。"
                "输出紧凑 JSON：不要 Markdown，不要解释 JSON 之外内容。\n\n"
                f"fault_injection_preparation JSON：\n{json.dumps(compact_preparation, ensure_ascii=False)}\n\n"
                f"boundary_answers JSON：\n{json.dumps(compact_answers, ensure_ascii=False)}"
            ),
        },
    ]


def _fault_injection_sandbox_repair_prompt(
    fault_injection_preparation_payload: dict[str, Any],
    boundary_answers: list[dict[str, Any]],
    broken_response: str,
    error: RequirementsIntakeError,
) -> list[dict[str, str]]:
    compact_preparation = _limited_fault_preparation_payload(fault_injection_preparation_payload)
    compact_answers = _limited_boundary_answers(boundary_answers)
    error_payload = {"code": error.code, "message": error.message, "details": error.details}
    response_excerpt = broken_response.strip()
    if len(response_excerpt) > 6000:
        response_excerpt = response_excerpt[:6000] + "\n[TRUNCATED]"
    return [
        {
            "role": "system",
            "content": (
                "你是 AI FANTUI 的沙盒故障注入建议 JSON 修复助手。上一轮模型输出未通过结构校验，"
                "你必须只返回完整 dry-run 沙盒建议 JSON，不得调用 /api/tick，不得执行仿真，不得修改 controller truth。"
            ),
        },
        {
            "role": "user",
            "content": (
                "请修复上一轮沙盒故障注入建议 JSON。\n"
                "固定字段：summary_zh, sandbox_injection_plan, observation_points, review_checklist, execution_contract, workflow_notes。\n"
                "sandbox_injection_plan 必须是非空数组，fault_scenario_id 必须来自 fault_scenarios；"
                "必须覆盖 fault_scenarios 中的每一个 id；如果校验错误包含 missing_fault_scenario_ids，必须逐一补齐。"
                "execution_contract 必须表达 run_tick=false, simulate=false, dry_run_only=true。"
                "只输出完整 JSON 对象，不要 Markdown，不要解释 JSON 之外内容。\n\n"
                f"校验错误 JSON：\n{json.dumps(error_payload, ensure_ascii=False)}\n\n"
                f"fault_injection_preparation JSON：\n{json.dumps(compact_preparation, ensure_ascii=False)}\n\n"
                f"boundary_answers JSON：\n{json.dumps(compact_answers, ensure_ascii=False)}\n\n"
                f"上一轮模型输出摘录：\n{response_excerpt}"
            ),
        },
    ]


def _num(value: Any, *, default: float | None = None) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            pass
    if default is not None:
        return default
    raise RequirementsIntakeError(
        "logic_drawing_json_error",
        "Logic drawing JSON contains a non-numeric coordinate.",
        status_code=502,
    )


def _normalize_point(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        raise RequirementsIntakeError("logic_drawing_json_error", "Edge route point must be an object.", status_code=502)
    return {"x": _num(value.get("x")), "y": _num(value.get("y"))}


def _normalize_nodes(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RequirementsIntakeError("logic_drawing_json_error", "Logic drawing must include nodes.", status_code=502)
    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise RequirementsIntakeError("logic_drawing_json_error", "Each drawing node must be an object.", status_code=502)
        node_id = _str(item.get("id"), f"node_{index}")
        if not node_id or node_id in seen:
            raise RequirementsIntakeError("logic_drawing_json_error", "Drawing node ids must be unique.", status_code=502)
        seen.add(node_id)
        width = max(120.0, _num(item.get("width"), default=180.0))
        height = max(28.0, _num(item.get("height"), default=104.0))
        nodes.append(
            {
                "id": node_id,
                "label": _str(item.get("label"), node_id)[:36],
                "node_kind": _str(item.get("node_kind"), "logic") or "logic",
                "x": _num(item.get("x")),
                "y": _num(item.get("y")),
                "width": width,
                "height": height,
                "description_zh": _str(item.get("description_zh"))[:120],
            }
        )
    return nodes


def _normalize_edges(value: Any, node_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise RequirementsIntakeError("logic_drawing_json_error", "Logic drawing edges must be a list.", status_code=502)
    edges: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise RequirementsIntakeError("logic_drawing_json_error", "Each drawing edge must be an object.", status_code=502)
        source = _str(item.get("source"))
        target = _str(item.get("target"))
        if source not in node_ids or target not in node_ids:
            raise RequirementsIntakeError(
                "logic_drawing_json_error",
                "Drawing edge source/target must reference model-created node ids.",
                status_code=502,
                details={"edge": item.get("id") or f"edge_{index}", "source": source, "target": target},
            )
        route = item.get("route")
        if not isinstance(route, list) or len(route) < 2:
            raise RequirementsIntakeError(
                "logic_drawing_json_error",
                "Each drawing edge must include a model-provided route with at least two points.",
                status_code=502,
            )
        edges.append(
            {
                "id": _str(item.get("id"), f"edge_{index}"),
                "source": source,
                "target": target,
                "label": _str(item.get("label")),
                "route": [_normalize_point(point) for point in route[:8]],
            }
        )
    return edges


def _normalize_parameter_panels(value: Any, node_ids: set[str]) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise RequirementsIntakeError("logic_drawing_json_error", "parameter_panels must be a list.", status_code=502)
    panels: list[dict[str, Any]] = []
    seen_node_ids: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            raise RequirementsIntakeError("logic_drawing_json_error", "Each parameter panel must be an object.", status_code=502)
        node_id = _str(item.get("node_id"))
        if node_id not in node_ids:
            raise RequirementsIntakeError(
                "logic_drawing_json_error",
                "Parameter panel node_id must reference a model-created node id.",
                status_code=502,
                details={"panel": item.get("id") or f"param_{index}", "node_id": node_id},
            )
        if node_id in seen_node_ids:
            raise RequirementsIntakeError(
                "logic_drawing_json_error",
                "Each model-created node may have at most one parameter panel.",
                status_code=502,
                details={"node_id": node_id},
            )
        seen_node_ids.add(node_id)
        panels.append(
            {
                "id": _str(item.get("id"), f"param_{index}"),
                "node_id": node_id,
                "label": _str(item.get("label"), f"参数 {index}")[:36],
                "unit": _str(item.get("unit"))[:12],
                "min": _num(item.get("min"), default=0.0),
                "max": _num(item.get("max"), default=1.0),
                "default": _num(item.get("default"), default=0.0),
                "x": _num(item.get("x")),
                "y": _num(item.get("y")),
                "width": max(96.0, _num(item.get("width"), default=140.0)),
                "height": max(76.0, _num(item.get("height"), default=76.0)),
            }
        )
    return panels


def _expand_canvas_to_drawing_bounds(
    canvas: dict[str, float],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    panels: list[dict[str, Any]],
    requirements_payload: dict[str, Any],
) -> dict[str, float]:
    if _reconstruction_target(requirements_payload) == THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET:
        return canvas
    max_x = canvas["width"]
    max_y = canvas["height"]
    for node in nodes:
        max_x = max(max_x, float(node["x"]) + float(node["width"]) + 72.0)
        max_y = max(max_y, float(node["y"]) + float(node["height"]) + 72.0)
    for panel in panels:
        max_x = max(max_x, float(panel["x"]) + float(panel["width"]) + 72.0)
        max_y = max(max_y, float(panel["y"]) + float(panel["height"]) + 72.0)
    for edge in edges:
        for point in edge.get("route", []):
            if not isinstance(point, dict):
                continue
            max_x = max(max_x, float(point.get("x", 0.0)) + 72.0)
            max_y = max(max_y, float(point.get("y", 0.0)) + 72.0)
    return {"width": max_x, "height": max_y}


def _required_concept_node_ids(requirements_payload: dict[str, Any]) -> set[str]:
    nodes = requirements_payload.get("concept_logic_nodes")
    if not isinstance(nodes, list):
        return set()
    return {_str(item.get("id")) for item in nodes if isinstance(item, dict) and _str(item.get("id"))}


def _required_concept_edge_pairs(requirements_payload: dict[str, Any], required_node_ids: set[str]) -> set[tuple[str, str]]:
    edges = requirements_payload.get("concept_edges")
    if not isinstance(edges, list):
        return set()
    pairs: set[tuple[str, str]] = set()
    for item in edges:
        if not isinstance(item, dict):
            continue
        source = _str(item.get("source"))
        target = _str(item.get("target"))
        if source in required_node_ids and target in required_node_ids:
            pairs.add((source, target))
    return pairs


def _validate_drawing_covers_requirements(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    requirements_payload: dict[str, Any],
) -> None:
    if _reconstruction_target(requirements_payload) == THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET:
        return

    required_node_ids = _required_concept_node_ids(requirements_payload)
    if not required_node_ids:
        return

    drawing_node_ids = {node["id"] for node in nodes}
    missing_nodes = sorted(required_node_ids - drawing_node_ids)
    if missing_nodes:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing omitted required concept nodes.",
            status_code=502,
            details={"missing_required_nodes": missing_nodes[:16]},
        )

    required_edges = _required_concept_edge_pairs(requirements_payload, required_node_ids)
    if not required_edges:
        return
    drawing_edges = {(_str(edge.get("source")), _str(edge.get("target"))) for edge in edges}
    missing_edges = sorted(f"{source}->{target}" for source, target in required_edges - drawing_edges)
    if missing_edges:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing omitted required concept edges.",
            status_code=502,
            details={"missing_required_edges": missing_edges[:16]},
        )


def _validate_drawing_matches_reference_target(
    canvas: dict[str, float],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    requirements_payload: dict[str, Any],
) -> None:
    if _reconstruction_target(requirements_payload) != THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET:
        return

    expected_canvas = THRUST_REVERSER_DEMO_CHAIN_CONTRACT["canvas"]
    canvas_mismatches = [
        field
        for field in ("width", "height")
        if abs(float(canvas[field]) - float(expected_canvas[field])) > 0.01
    ]
    if canvas_mismatches:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing canvas does not match the thrust-reverser demo cabin contract.",
            status_code=502,
            details={
                "reconstruction_target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
                "canvas_mismatches": canvas_mismatches,
                "expected_canvas": expected_canvas,
                "actual_canvas": canvas,
            },
        )

    expected_node_ids = {node["id"] for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]}
    actual_node_ids = {node["id"] for node in nodes}
    missing_nodes = sorted(expected_node_ids - actual_node_ids)
    extra_nodes = sorted(actual_node_ids - expected_node_ids)
    if missing_nodes or extra_nodes:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing does not match the thrust-reverser demo cabin node contract.",
            status_code=502,
            details={
                "reconstruction_target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
                "missing_reference_nodes": missing_nodes[:24],
                "extra_reference_nodes": extra_nodes[:24],
            },
        )

    expected_nodes_by_id = {node["id"]: node for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]}
    node_geometry_mismatches: list[str] = []
    for node in nodes:
        expected = expected_nodes_by_id[node["id"]]
        for field in ("x", "y", "width", "height"):
            if abs(float(node[field]) - float(expected[field])) > 0.01:
                node_geometry_mismatches.append(f"{node['id']}.{field}")
    if node_geometry_mismatches:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing node geometry does not match the thrust-reverser demo cabin contract.",
            status_code=502,
            details={
                "reconstruction_target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
                "node_geometry_mismatches": node_geometry_mismatches[:32],
            },
        )

    expected_edge_ids = {edge["id"] for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]}
    actual_edge_ids = {edge["id"] for edge in edges}
    missing_edge_ids = sorted(expected_edge_ids - actual_edge_ids)
    extra_edge_ids = sorted(actual_edge_ids - expected_edge_ids)
    expected_pairs = {(edge["source"], edge["target"]) for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]}
    actual_pairs = {(edge["source"], edge["target"]) for edge in edges}
    missing_pairs = sorted(f"{source}->{target}" for source, target in expected_pairs - actual_pairs)
    extra_pairs = sorted(f"{source}->{target}" for source, target in actual_pairs - expected_pairs)
    if missing_edge_ids or extra_edge_ids or missing_pairs or extra_pairs:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing does not match the thrust-reverser demo cabin edge contract.",
            status_code=502,
            details={
                "reconstruction_target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
                "missing_reference_edges": missing_edge_ids[:32],
                "extra_reference_edges": extra_edge_ids[:32],
                "missing_reference_pairs": missing_pairs[:32],
                "extra_reference_pairs": extra_pairs[:32],
            },
        )

    expected_edges_by_id = {edge["id"]: edge for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]}
    route_mismatches: list[str] = []
    for edge in edges:
        expected_route = expected_edges_by_id[edge["id"]]["route"]
        actual_route = edge["route"]
        if len(actual_route) != len(expected_route):
            route_mismatches.append(f"{edge['id']}.route_length")
            continue
        for index, (actual_point, expected_point) in enumerate(zip(actual_route, expected_route)):
            if (
                abs(float(actual_point["x"]) - float(expected_point["x"])) > 0.01
                or abs(float(actual_point["y"]) - float(expected_point["y"])) > 0.01
            ):
                route_mismatches.append(f"{edge['id']}.route[{index}]")
                break
    if route_mismatches:
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing routes do not match the thrust-reverser demo cabin contract.",
            status_code=502,
            details={
                "reconstruction_target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
                "route_mismatches": route_mismatches[:32],
            },
        )


def _string_list(value: Any, *, allowed: set[str] | None = None, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    seen: set[str] = set()
    for raw in value:
        item = _str(raw).strip()
        if not item or item in seen:
            continue
        if allowed is not None and item not in allowed:
            continue
        seen.add(item)
        items.append(item[:80])
        if len(items) >= limit:
            break
    return items


def _normalize_source_anchors(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    anchors: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        anchor_id = _str(item.get("id") or item.get("anchor_id"))[:32]
        quote = _str(item.get("quote_zh") or item.get("quote"))[:120]
        if not anchor_id and not quote:
            continue
        key = (anchor_id, quote)
        if key in seen:
            continue
        seen.add(key)
        anchors.append(
            {
                "id": anchor_id or f"A{len(anchors) + 1:02d}",
                "kind": _str(item.get("kind"), "正文条件")[:32],
                "origin": _str(item.get("origin"), "model_inference")[:32],
                "quote_zh": quote,
            }
        )
        if len(anchors) >= 4:
            break
    return anchors


def _requirement_node_context(requirements_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _str(item.get("id")): item
        for item in requirements_payload.get("concept_logic_nodes", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }


def _requirement_edge_context(requirements_payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (_str(item.get("source")), _str(item.get("target"))): item
        for item in requirements_payload.get("concept_edges", [])
        if isinstance(item, dict) and _str(item.get("source")) and _str(item.get("target"))
    }


def _requirement_group_context(requirements_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _str(item.get("id")): item
        for item in requirements_payload.get("requirement_groups", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }


def _merge_source_anchors(*anchor_lists: Any, limit: int = 4) -> list[dict[str, str]]:
    anchors: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for value in anchor_lists:
        for anchor in _normalize_source_anchors(value):
            key = (_str(anchor.get("id")), _str(anchor.get("quote_zh")))
            if key in seen:
                continue
            seen.add(key)
            anchors.append(anchor)
            if len(anchors) >= limit:
                return anchors
    return anchors


def _source_anchor_ids(anchors: Any) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for anchor in _normalize_source_anchors(anchors):
        anchor_id = _str(anchor.get("id"))
        if anchor_id and anchor_id not in seen:
            seen.add(anchor_id)
            ids.append(anchor_id)
    return ids


def _demo_node_source_anchors(
    demo_id: str,
    linked_node_id: str,
    nodes_by_id: dict[str, dict[str, Any]],
    groups_by_id: dict[str, dict[str, Any]],
    edges_by_pair: dict[tuple[str, str], dict[str, Any]],
) -> list[dict[str, str]]:
    anchor_sources: list[Any] = []
    if linked_node_id:
        anchor_sources.append(nodes_by_id.get(linked_node_id, {}).get("source_anchors"))
    fallback = DEMO_NODE_ANCHOR_FALLBACKS.get(demo_id, {})
    for node_id in fallback.get("nodes", ()):
        anchor_sources.append(nodes_by_id.get(_str(node_id), {}).get("source_anchors"))
    for group_id in fallback.get("groups", ()):
        anchor_sources.append(groups_by_id.get(_str(group_id), {}).get("source_anchors"))
    for pair in fallback.get("edges", ()):
        if isinstance(pair, tuple) and len(pair) == 2:
            anchor_sources.append(edges_by_pair.get((_str(pair[0]), _str(pair[1])), {}).get("source_anchors"))
    return _merge_source_anchors(*anchor_sources)


def _l1_l4_circuit_candidate(requirements_payload: dict[str, Any]) -> bool:
    groups_by_id = _requirement_group_context(requirements_payload)
    nodes_by_id = _requirement_node_context(requirements_payload)
    has_groups = L1_L4_LOGIC_IDS.issubset(groups_by_id.keys())
    has_logic_nodes = L1_L4_LOGIC_IDS.issubset(nodes_by_id.keys())
    preparse = requirements_payload.get("deterministic_preparse")
    has_preparse = isinstance(preparse, dict) and bool(preparse.get("available") or preparse.get("applied"))
    return has_logic_nodes and (has_groups or has_preparse)


def _circuit_node_label(node: dict[str, Any], fallback: str) -> str:
    label = _str(node.get("label"), fallback)
    return label[:34] if label else fallback


def _circuit_node_description(node: dict[str, Any]) -> str:
    return _str(node.get("description_zh"))[:120]


def _circuit_route(source_box: dict[str, Any], target_box: dict[str, Any]) -> list[dict[str, float]]:
    sx = float(source_box["x"]) + float(source_box["width"])
    sy = float(source_box["y"]) + float(source_box["height"]) / 2.0
    tx = float(target_box["x"])
    ty = float(target_box["y"]) + float(target_box["height"]) / 2.0
    mid_x = (sx + tx) / 2.0 if sx <= tx else sx + 34.0
    return [
        {"x": sx, "y": sy},
        {"x": mid_x, "y": sy},
        {"x": mid_x, "y": ty},
        {"x": tx, "y": ty},
    ]


def _build_l1_l4_circuit_view(requirements_payload: dict[str, Any]) -> dict[str, Any] | None:
    if not _l1_l4_circuit_candidate(requirements_payload):
        return None

    nodes_by_id = _requirement_node_context(requirements_payload)
    groups_by_id = _requirement_group_context(requirements_payload)
    edges_by_pair = _requirement_edge_context(requirements_payload)
    circuit_nodes: list[dict[str, Any]] = []

    def node_role(node: dict[str, Any]) -> str:
        node_id = _str(node.get("id"))
        if _str(node.get("node_kind")).lower() == "logic":
            return "gate"
        if node_id == "thr_lock":
            return "final_output"
        if float(node.get("x") or 0) >= 500:
            return "intermediate"
        return "input"

    def node_state(node_id: str) -> str:
        if node_id in DEMO_ACTIVE_NODES:
            return "active"
        if node_id in DEMO_BLOCKED_NODES:
            return "blocked"
        return "idle"

    for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]:
        demo_id = _str(node.get("id"))
        linked_node_id = DEMO_NODE_TO_REQUIREMENT_NODE.get(demo_id, "")
        source_node = nodes_by_id.get(linked_node_id, {})
        anchors = _demo_node_source_anchors(demo_id, linked_node_id, nodes_by_id, groups_by_id, edges_by_pair)
        provenance = "docx_body" if anchors else "demo_cabin_context"
        circuit_nodes.append(
            {
                "id": demo_id,
                "linked_node_id": linked_node_id,
                "row_id": linked_node_id if linked_node_id in L1_L4_LOGIC_IDS else "",
                "circuit_role": node_role(node),
                "label": _str(node.get("label"), demo_id),
                "node_kind": _str(node.get("node_kind"), "logic"),
                "description_zh": _circuit_node_description(source_node),
                "x": float(node.get("x") or 0.0),
                "y": float(node.get("y") or 0.0),
                "width": float(node.get("width") or 160.0),
                "height": float(node.get("height") or 28.0),
                "state": node_state(demo_id),
                "source_anchors": anchors,
                "source_anchor_ids": _source_anchor_ids(anchors),
                "provenance": provenance,
            }
        )

    circuit_rows: list[dict[str, Any]] = []
    contract_edges = [
        item
        for item in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]
        if isinstance(item, dict) and _str(item.get("source")) and _str(item.get("target"))
    ]
    for row_id in ("logic1", "logic2", "logic3", "logic4"):
        group = groups_by_id.get(row_id, {})
        group_anchor_source = group.get("source_anchors") if isinstance(group, dict) else []
        gate_anchors = _merge_source_anchors(group_anchor_source, nodes_by_id.get(row_id, {}).get("source_anchors"))
        gate_box = next((node for node in circuit_nodes if node["id"] == row_id), {})
        inputs = [_str(edge.get("source")) for edge in contract_edges if _str(edge.get("target")) == row_id]
        outputs = [_str(edge.get("target")) for edge in contract_edges if _str(edge.get("source")) == row_id]

        circuit_rows.append(
            {
                "id": row_id,
                "label": row_id.replace("logic", "L"),
                "title_zh": _str(nodes_by_id.get(row_id, {}).get("description_zh")),
                "center_y": float(gate_box.get("y", 0.0)) + float(gate_box.get("height", 0.0)) / 2.0,
                "inputs": inputs,
                "outputs": outputs,
                "gate": {
                    "id": row_id,
                    "label": row_id.replace("logic", "L"),
                    "gate_type": "AND",
                    "x": float(gate_box.get("x", 0.0)),
                    "y": float(gate_box.get("y", 0.0)),
                    "width": float(gate_box.get("width", 0.0)),
                    "height": float(gate_box.get("height", 0.0)),
                    "source_anchors": gate_anchors,
                    "source_anchor_ids": _source_anchor_ids(gate_anchors),
                },
                "source_anchors": _merge_source_anchors(group_anchor_source, gate_anchors),
                "source_anchor_ids": _source_anchor_ids(_merge_source_anchors(group_anchor_source, gate_anchors)),
            }
        )

    circuit_wires: list[dict[str, Any]] = []
    for index, edge in enumerate(contract_edges, start=1):
        source_id = _str(edge.get("source"))
        target_id = _str(edge.get("target"))
        requirement_pair = DEMO_EDGE_TO_REQUIREMENT_PAIR.get((source_id, target_id))
        source_edge = edges_by_pair.get(requirement_pair or ("", "")) if requirement_pair else {}
        source_node_id = DEMO_NODE_TO_REQUIREMENT_NODE.get(source_id, "")
        target_node_id = DEMO_NODE_TO_REQUIREMENT_NODE.get(target_id, "")
        anchors = _merge_source_anchors(
            source_edge.get("source_anchors") if isinstance(source_edge, dict) else [],
            nodes_by_id.get(source_node_id, {}).get("source_anchors"),
            nodes_by_id.get(target_node_id, {}).get("source_anchors"),
            groups_by_id.get(source_node_id, {}).get("source_anchors") if source_node_id in L1_L4_LOGIC_IDS else [],
            groups_by_id.get(target_node_id, {}).get("source_anchors") if target_node_id in L1_L4_LOGIC_IDS else [],
        )
        wire_state = "active" if source_id in DEMO_ACTIVE_NODES else "idle"
        if target_id == "thr_lock":
            wire_state = "blocked"
        circuit_wires.append(
            {
                "id": _str(edge.get("id"), f"wire_{index}")[:64],
                "source": source_id,
                "target": target_id,
                "label": _str(edge.get("label"))[:80],
                "route": [_normalize_point(point) for point in edge.get("route", [])],
                "state": wire_state,
                "provenance": "docx_body" if anchors else "demo_cabin_context",
                "source_anchors": anchors,
                "source_anchor_ids": _source_anchor_ids(anchors),
            }
        )

    source_scope = requirements_payload.get("source_scope") if isinstance(requirements_payload.get("source_scope"), dict) else {}
    badges: list[dict[str, Any]] = []
    fault_scope = source_scope.get("fault_injection") if isinstance(source_scope, dict) else None
    if isinstance(fault_scope, dict) and fault_scope.get("status") == "source_deferred":
        badges.append(
            {
                "id": "fault_injection_deferred",
                "label_zh": "故障注入暂缓",
                "source_anchor_ids": _source_anchor_ids(fault_scope.get("source_anchors")),
            }
        )

    return {
        "kind": L1_L4_CIRCUIT_VIEW_KIND,
        "version": L1_L4_CIRCUIT_VIEW_VERSION,
        "layout": L1_L4_CIRCUIT_LAYOUT,
        "canvas": {"width": 900, "height": 400},
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "source_scope": source_scope,
        "rows": circuit_rows,
        "nodes": circuit_nodes,
        "wires": circuit_wires,
        "junctions": list(DEMO_WIRE_JUNCTIONS),
        "badges": badges,
    }


def _attach_drawing_source_context(
    drawing: dict[str, Any],
    requirements_payload: dict[str, Any],
) -> None:
    nodes_by_id = _requirement_node_context(requirements_payload)
    edges_by_pair = _requirement_edge_context(requirements_payload)
    for node in drawing.get("nodes", []):
        if not isinstance(node, dict):
            continue
        source_node = nodes_by_id.get(_str(node.get("id")), {})
        anchors = _normalize_source_anchors(node.get("source_anchors")) or _normalize_source_anchors(source_node.get("source_anchors"))
        node["source_anchors"] = anchors
        node["provenance"] = _str(node.get("provenance") or source_node.get("provenance"), "model_inference")
    for edge in drawing.get("edges", []):
        if not isinstance(edge, dict):
            continue
        source_edge = edges_by_pair.get((_str(edge.get("source")), _str(edge.get("target"))), {})
        anchors = _normalize_source_anchors(edge.get("source_anchors")) or _normalize_source_anchors(source_edge.get("source_anchors"))
        edge["source_anchors"] = anchors
        edge["provenance"] = _str(edge.get("provenance") or source_edge.get("provenance"), "model_inference")


def _normalize_logic_drawing(
    raw: str,
    requirements_payload: dict[str, Any],
    *,
    attach_agent_contracts: bool = True,
) -> dict[str, Any]:
    try:
        parsed = _extract_json_object(_strip_model_json(raw))
    except json.JSONDecodeError as exc:
        raise RequirementsIntakeError("logic_drawing_json_error", "Model drawing response was not valid JSON.", status_code=502) from exc

    canvas_raw = parsed.get("canvas") if isinstance(parsed.get("canvas"), dict) else {}
    min_canvas_height = 400.0 if _reconstruction_target(requirements_payload) else 560.0
    canvas = {
        "width": max(900.0, _num(canvas_raw.get("width"), default=1280.0)),
        "height": max(min_canvas_height, _num(canvas_raw.get("height"), default=760.0)),
    }
    nodes = _normalize_nodes(parsed.get("nodes"))
    node_ids = {node["id"] for node in nodes}
    edges = _normalize_edges(parsed.get("edges"), node_ids)
    panels = _normalize_parameter_panels(parsed.get("parameter_panels"), node_ids)
    _validate_drawing_matches_reference_target(canvas, nodes, edges, requirements_payload)
    _validate_drawing_covers_requirements(nodes, edges, requirements_payload)
    if _reconstruction_target(requirements_payload) != THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET:
        for node in nodes:
            node["width"] = max(float(node["width"]), min(260.0, 96.0 + len(_str(node.get("label"))) * 7.0))
            node["height"] = max(float(node["height"]), 72.0)
        canvas = _expand_canvas_to_drawing_bounds(canvas, nodes, edges, panels, requirements_payload)
    source_sha = _payload_sha256(requirements_payload)

    notes = parsed.get("drawing_notes")
    if not isinstance(notes, list):
        notes = []
    drawing = {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": LOGIC_DRAWING_KIND,
        "version": LOGIC_DRAWING_VERSION,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": source_sha,
        "summary_zh": _str(parsed.get("summary_zh"), "模型已生成初版逻辑链路图。")[:180],
        "canvas": canvas,
        "nodes": nodes,
        "edges": edges,
        "parameter_panels": panels,
        "drawing_notes": [_str(item)[:120] for item in notes[:4] if _str(item)],
    }
    _attach_drawing_source_context(drawing, requirements_payload)
    circuit_view = _build_l1_l4_circuit_view(requirements_payload)
    if circuit_view is not None:
        circuit_view["source_requirements_sha256"] = source_sha
        drawing["circuit_view"] = circuit_view
    if attach_agent_contracts:
        _attach_logic_ir_agent_contracts(drawing, requirements_payload)
    return drawing


def _drawing_id_sets(drawing_payload: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    node_ids = {_str(item.get("id")) for item in drawing_payload.get("nodes", []) if isinstance(item, dict)}
    edge_ids = {_str(item.get("id")) for item in drawing_payload.get("edges", []) if isinstance(item, dict)}
    panel_ids = {_str(item.get("id")) for item in drawing_payload.get("parameter_panels", []) if isinstance(item, dict)}
    return node_ids, edge_ids, panel_ids


def _normalize_annotation_batch(value: Any, *, limit: int = 12) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    annotations: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        target_type = _str(item.get("target_type"), "node").lower()[:32]
        if target_type not in {"node", "wire", "edge", "parameter_panel", "canvas"}:
            target_type = "node"
        annotation_id = _str(item.get("id"), f"annotation_{index}")[:80]
        if annotation_id in seen:
            annotation_id = f"{annotation_id}_{index}"[:80]
        seen.add(annotation_id)
        target_id = _str(item.get("target_id") or item.get("node_id") or item.get("edge_id"))[:100]
        text = _str(item.get("text") or item.get("annotation_text"))[:500]
        if not target_id and not text:
            continue
        annotations.append(
            {
                "id": annotation_id,
                "target_type": target_type,
                "target_id": target_id,
                "target_label": _str(item.get("target_label"), target_id)[:120],
                "text": text,
                "provider": _str(item.get("provider"))[:40],
                "created_at": _str(item.get("created_at"))[:40],
            }
        )
        if len(annotations) >= limit:
            break
    return annotations


def _normalize_annotation_groups(value: Any, annotation_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    groups: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        group_label = _str(item.get("group_label"), f"批注组 {index}")[:80]
        ids = _string_list(item.get("annotation_ids"), allowed=annotation_ids or None, limit=8)
        summary = _str(item.get("summary_zh") or item.get("summary"))[:220]
        if not ids and not summary:
            continue
        groups.append(
            {
                "group_label": group_label,
                "annotation_ids": ids,
                "summary_zh": summary,
            }
        )
        if len(groups) >= 4:
            break
    return groups


def _parameter_panel_node_map(drawing_payload: dict[str, Any]) -> dict[str, str]:
    panel_map: dict[str, str] = {}
    for item in drawing_payload.get("parameter_panels", []):
        if not isinstance(item, dict):
            continue
        panel_id = _str(item.get("id"))
        node_id = _str(item.get("node_id"))
        if panel_id and node_id:
            panel_map[panel_id] = node_id
    return panel_map


def _critical_fault_node_ids(drawing_payload: dict[str, Any]) -> set[str]:
    critical_nodes = set(_parameter_panel_node_map(drawing_payload).values())
    for item in drawing_payload.get("nodes", []):
        if not isinstance(item, dict):
            continue
        node_kind = _str(item.get("node_kind")).lower()
        node_id = _str(item.get("id"))
        if node_id and node_kind in {"input", "output"}:
            critical_nodes.add(node_id)
    return critical_nodes


def _validate_requirements_payload(requirements_payload: dict[str, Any]) -> None:
    if not isinstance(requirements_payload, dict):
        raise RequirementsIntakeError("invalid_requirements_payload", "requirements_payload must be an object.")
    if requirements_payload.get("kind") != REQUIREMENTS_INTAKE_KIND:
        raise RequirementsIntakeError(
            "invalid_requirements_payload",
            "requirements_payload must come from the requirements-intake analyzer.",
        )
    if requirements_payload.get("open_questions"):
        raise RequirementsIntakeError(
            "requirements_not_ready",
            "requirements_payload still contains open clarification questions.",
            status_code=409,
        )
    if not requirements_payload.get("concept_logic_nodes"):
        raise RequirementsIntakeError("requirements_not_ready", "requirements_payload has no concept logic nodes.", status_code=409)


def _validate_drawing_payload(drawing_payload: dict[str, Any]) -> None:
    if not isinstance(drawing_payload, dict):
        raise RequirementsIntakeError("invalid_drawing_payload", "drawing_payload must be an object.")
    if drawing_payload.get("kind") != LOGIC_DRAWING_KIND:
        raise RequirementsIntakeError(
            "invalid_drawing_payload",
            "drawing_payload must come from the logic builder model drawing step.",
        )
    if drawing_payload.get("status") != "draft_ready":
        raise RequirementsIntakeError(
            "invalid_drawing_payload",
            "drawing_payload must be a draft_ready logic drawing.",
            status_code=409,
        )
    if not isinstance(drawing_payload.get("nodes"), list) or not drawing_payload.get("nodes"):
        raise RequirementsIntakeError("invalid_drawing_payload", "drawing_payload must include nodes.", status_code=409)


def _streamed_target_key(target_type: str, target_id: str) -> str:
    return f"{_str(target_type)}:{_str(target_id)}"


def _streamed_proposal_id(target_type: str, target_id: str, *, revision_index: int = 0) -> str:
    raw = f"{target_type}-{target_id}"
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "-", raw).strip("-").lower()
    base = f"m21-{safe or 'candidate-edit'}"
    if revision_index > 0:
        return f"{base}-revision-{revision_index}"
    return base


def _normalize_streamed_requirements_document_patch(
    value: Any,
    *,
    feedback_text: str,
    target_type: str,
    target_id: str,
    proposal_id: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        value = {}
    proposed_text = _str(
        value.get("proposed_text_zh")
        or value.get("replacement_text_zh")
        or value.get("text_zh")
        or feedback_text
    )[:500]
    return {
        "operation": _str(value.get("operation") or "candidate_requirements_text_revision")[:80],
        "target": _str(value.get("target") or "requirements_document")[:120],
        "target_type": target_type,
        "target_id": target_id,
        "source_proposal_id": proposal_id,
        "proposed_text_zh": proposed_text,
        "truth_effect": "none",
        "controller_truth_modified": False,
        "requires_explicit_authorization": True,
    }


def _normalize_streamed_decision_history(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    history: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        decision = _str(item.get("decision")).strip().lower()
        if decision in {"confirmed", "accepted", "accept"}:
            decision = "confirm"
        if decision in {"reject", "rejected", "feedback", "revise"}:
            decision = "request_revision"
        if decision not in {"confirm", "request_revision"}:
            continue
        target_type = _str(item.get("target_type")).strip().lower()
        if target_type not in {"node", "wire"}:
            target_type = ""
        target_id = _str(item.get("target_id"))[:120]
        proposal_id = _str(item.get("proposal_id"))[:160]
        feedback_text = _str(item.get("feedback_text"))[:500]
        edit_requested = (
            item.get("requirements_document_edit_requested") is True
            or item.get("requirements_document_update_requested") is True
            or isinstance(item.get("requirements_document_patch"), dict)
        )
        authorization_phrase = _str(item.get("requirements_document_authorization_phrase"))[:120]
        edit_authorized = (
            item.get("requirements_document_edit_authorized") is True
            and authorization_phrase == STREAMED_REQUIREMENTS_EDIT_AUTHORIZATION_PHRASE
        )
        requirements_document_patch = (
            _normalize_streamed_requirements_document_patch(
                item.get("requirements_document_patch"),
                feedback_text=feedback_text,
                target_type=target_type,
                target_id=target_id,
                proposal_id=proposal_id,
            )
            if edit_requested
            else None
        )
        history.append(
            {
                "proposal_id": proposal_id,
                "target_type": target_type,
                "target_id": target_id,
                "target_key": _streamed_target_key(target_type, target_id) if target_type and target_id else "",
                "decision": decision,
                "feedback_text": feedback_text,
                "decided_at": _str(item.get("decided_at"))[:80],
                "requirements_document_edit_requested": edit_requested,
                "requirements_document_edit_authorized": edit_authorized,
                "requirements_document_authorization_phrase": authorization_phrase,
                "requirements_document_patch": requirements_document_patch,
                "source_requirements_sha256": _str(item.get("source_requirements_sha256"))[:80],
                "source_drawing_sha256": _str(item.get("source_drawing_sha256"))[:80],
            }
        )
        if len(history) >= 64:
            break
    return history


def _filter_streamed_decision_history(
    history: list[dict[str, Any]],
    *,
    source_requirements_sha256: str,
    source_drawing_sha256: str,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    confirmed_targets: set[str] = set()
    revision_counts_by_key: dict[str, int] = {}
    for item in history:
        target_key = _str(item.get("target_key"))
        if not target_key:
            continue
        item_requirements_sha = _str(item.get("source_requirements_sha256"))
        item_drawing_sha = _str(item.get("source_drawing_sha256"))
        if item_requirements_sha and item_requirements_sha != source_requirements_sha256:
            continue
        if item_drawing_sha and item_drawing_sha != source_drawing_sha256:
            continue
        if item.get("decision") == "confirm":
            if target_key in confirmed_targets:
                continue
            expected_revision_index = revision_counts_by_key.get(target_key, 0)
            expected_proposal_id = _streamed_proposal_id(
                _str(item.get("target_type")),
                _str(item.get("target_id")),
                revision_index=expected_revision_index,
            )
            if _str(item.get("proposal_id")) != expected_proposal_id:
                continue
            confirmed_targets.add(target_key)
            filtered.append(item)
            continue
        if item.get("decision") == "request_revision":
            if target_key in confirmed_targets:
                continue
            expected_revision_index = revision_counts_by_key.get(target_key, 0)
            expected_proposal_id = _streamed_proposal_id(
                _str(item.get("target_type")),
                _str(item.get("target_id")),
                revision_index=expected_revision_index,
            )
            if _str(item.get("proposal_id")) != expected_proposal_id:
                continue
            filtered.append(item)
            revision_counts_by_key[target_key] = expected_revision_index + 1
    return filtered


def _streamed_requirements_document_edit_gate(history: list[dict[str, Any]]) -> dict[str, Any]:
    requested = [item for item in history if item.get("requirements_document_edit_requested")]
    base = {
        "requires_explicit_authorization": True,
        "authorized": False,
        "truth_effect": "none",
        "controller_truth_modified": False,
        "requirements_document_modified": False,
        "automatic_document_mutation": False,
        "write_effect": "none",
        "authorization_record": None,
        "authorization_gate": {
            "required_phrase": STREAMED_REQUIREMENTS_EDIT_AUTHORIZATION_PHRASE,
            "status": "not_requested",
        },
    }
    if not requested:
        return {
            **base,
            "status": "not_requested",
            "pending_candidate_patch": None,
            "proposal": None,
        }
    latest = requested[-1]
    authorized = latest.get("requirements_document_edit_authorized") is True
    pending_patch = latest.get("requirements_document_patch")
    pending_patch_sha256 = _payload_sha256(pending_patch) if isinstance(pending_patch, dict) else ""
    return {
        **base,
        "status": "authorized_candidate_patch" if authorized else "authorization_required",
        "authorized": authorized,
        "pending_candidate_patch": pending_patch,
        "pending_candidate_patch_sha256": pending_patch_sha256,
        "proposal": pending_patch,
        "authorization_gate": {
            "required_phrase": STREAMED_REQUIREMENTS_EDIT_AUTHORIZATION_PHRASE,
            "provided_phrase_matches": authorized,
            "status": "authorized" if authorized else "blocked_without_explicit_authorization",
        },
        "authorization_record": {
            "proposal_id": latest.get("proposal_id", ""),
            "target_type": latest.get("target_type", ""),
            "target_id": latest.get("target_id", ""),
            "decided_at": latest.get("decided_at", ""),
        } if authorized else None,
    }


def _streamed_source_excerpt(anchors: list[dict[str, str]], fallback: str) -> str:
    for anchor in anchors:
        quote = _str(anchor.get("quote_zh") or anchor.get("quote")).strip()
        if quote:
            return quote[:180]
    return fallback[:180] or "来源未提供；当前为候选解释，需要工程师确认。"


def _streamed_node_anchors(
    node: dict[str, Any],
    requirement_nodes: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    node_id = _str(node.get("id"))
    linked_id = _str(node.get("linked_node_id"))
    return _merge_source_anchors(
        node.get("source_anchors"),
        requirement_nodes.get(linked_id, {}).get("source_anchors"),
        requirement_nodes.get(node_id, {}).get("source_anchors"),
    )


def _streamed_wire_anchors(
    wire: dict[str, Any],
    requirement_edges: dict[tuple[str, str], dict[str, Any]],
    requirement_nodes: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    source_id = _str(wire.get("source"))
    target_id = _str(wire.get("target"))
    edge_context = requirement_edges.get((source_id, target_id), {})
    return _merge_source_anchors(
        wire.get("source_anchors"),
        edge_context.get("source_anchors"),
        requirement_nodes.get(source_id, {}).get("source_anchors"),
        requirement_nodes.get(target_id, {}).get("source_anchors"),
    )


def _streamed_candidate_objects(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    requirement_nodes = _requirement_node_context(requirements_payload)
    requirement_edges = _requirement_edge_context(requirements_payload)
    circuit_view = drawing_payload.get("circuit_view")
    if isinstance(circuit_view, dict) and circuit_view.get("kind"):
        nodes = [item for item in circuit_view.get("nodes", []) if isinstance(item, dict)]
        wires = [item for item in circuit_view.get("wires", []) if isinstance(item, dict)]
    else:
        nodes = [item for item in drawing_payload.get("nodes", []) if isinstance(item, dict)]
        wires = [item for item in drawing_payload.get("edges", []) if isinstance(item, dict)]

    candidates: list[dict[str, Any]] = []
    wire_context: dict[str, dict[str, list[str]]] = {}
    for wire in wires:
        source_id = _str(wire.get("source"))
        target_id = _str(wire.get("target"))
        if not source_id or not target_id:
            continue
        wire_id = f"{source_id}->{target_id}"
        wire_context.setdefault(source_id, {"upstream": [], "downstream": []})["downstream"].append(target_id)
        wire_context.setdefault(target_id, {"upstream": [], "downstream": []})["upstream"].append(source_id)
        anchors = _streamed_wire_anchors(wire, requirement_edges, requirement_nodes)
        candidates.append(
            {
                "target_type": "wire",
                "target_id": wire_id,
                "display_label": _str(wire.get("label")) or f"{source_id} -> {target_id}",
                "edit_type": "add_wire",
                "source_id": source_id,
                "target_node_id": target_id,
                "source_anchors": anchors,
                "source_excerpt": _streamed_source_excerpt(anchors, _str(wire.get("label"))),
                "interpreted_logic": _str(wire.get("label")) or f"{source_id} feeds {target_id}",
                "upstream": [source_id],
                "downstream": [target_id],
            }
        )

    node_candidates: list[dict[str, Any]] = []
    for node in nodes:
        node_id = _str(node.get("id"))
        if not node_id:
            continue
        linked_id = _str(node.get("linked_node_id"))
        display_label = _str(node.get("display_label") or node.get("label") or linked_id or node_id)
        description = _str(node.get("description_zh") or node.get("label") or display_label)
        anchors = _streamed_node_anchors(node, requirement_nodes)
        context = wire_context.get(node_id, {"upstream": [], "downstream": []})
        node_candidates.append(
            {
                "target_type": "node",
                "target_id": node_id,
                "display_label": display_label,
                "edit_type": "add_node",
                "source_anchors": anchors,
                "source_excerpt": _streamed_source_excerpt(anchors, description),
                "interpreted_logic": description,
                "upstream": context.get("upstream", [])[:6],
                "downstream": context.get("downstream", [])[:6],
            }
        )
    return node_candidates + candidates


def _streamed_proposal_from_candidate(
    candidate: dict[str, Any],
    *,
    sequence_index: int,
    revision_of: str = "",
    user_feedback: str = "",
    revision_index: int = 0,
    feedback_decided_at: str = "",
    source_requirements_sha256: str = "",
    source_drawing_sha256: str = "",
    decision_history_count: int = 0,
) -> dict[str, Any]:
    target_type = _str(candidate.get("target_type"))
    target_id = _str(candidate.get("target_id"))
    edit_type = _str(candidate.get("edit_type"))
    graph_diff = {
        "operation": edit_type,
        "node_ids_added": [target_id] if target_type == "node" else [],
        "wire_ids_added": [target_id] if target_type == "wire" else [],
        "truth_effect": "none",
    }
    proposal_id = _streamed_proposal_id(target_type, target_id, revision_index=revision_index)
    source_anchors = _normalize_source_anchors(candidate.get("source_anchors"))
    proposal = {
        "kind": STREAMED_LOGIC_AUTHORING_PROPOSAL_KIND,
        "version": STREAMED_LOGIC_AUTHORING_VERSION,
        "id": proposal_id,
        "proposal_status": "candidate_proposal_ready",
        "sequence_index": sequence_index,
        "revision_index": revision_index,
        "edit_type": edit_type,
        "target_type": target_type,
        "target_id": target_id,
        "display_label": _str(candidate.get("display_label"))[:120],
        "source_excerpt": _str(candidate.get("source_excerpt"))[:220],
        "source_anchor_ids": _source_anchor_ids(source_anchors),
        "source_anchors": source_anchors,
        "interpreted_logic": _str(candidate.get("interpreted_logic"))[:260],
        "upstream": _string_list(candidate.get("upstream"), limit=8),
        "downstream": _string_list(candidate.get("downstream"), limit=8),
        "model_rationale": (
            "This is the next atomic candidate graph edit. It must be "
            "confirmed by the engineer before it is committed to the candidate graph."
        ),
        "graph_diff": graph_diff,
        "requires_user_confirmation": True,
        "confirmation_question_zh": "这个节点/连线是否按需求原文理解正确？",
        "revision_gate": {
            "status": "not_requested",
            "truth_effect": "none",
            "controller_truth_modified": False,
            "requires_engineer_confirmation": True,
        },
        "recomputed_from": {
            "source_requirements_sha256": source_requirements_sha256,
            "source_drawing_sha256": source_drawing_sha256,
            "decision_history_count": decision_history_count,
        },
    }
    if revision_of:
        feedback_sha256 = hashlib.sha256(user_feedback.encode("utf-8")).hexdigest()
        proposal["proposal_status"] = "revised_proposal_ready"
        proposal["revision_of"] = revision_of
        proposal["user_feedback"] = user_feedback
        proposal["feedback_applied"] = {
            "proposal_id": revision_of,
            "target_type": target_type,
            "target_id": target_id,
            "feedback_text": user_feedback,
            "feedback_sha256": feedback_sha256,
            "decided_at": feedback_decided_at,
        }
        proposal["revision_gate"] = {
            "status": "revision_candidate_ready",
            "feedback_applied": bool(user_feedback),
            "truth_effect": "none",
            "controller_truth_modified": False,
            "requires_engineer_confirmation": True,
        }
        proposal["model_rationale"] = (
            "This revised candidate edit incorporates the engineer feedback "
            "while preserving the original source excerpt and truth boundary."
        )
    return proposal


def _streamed_replay_and_committed_graph(
    *,
    history: list[dict[str, Any]],
    candidates_by_key: dict[str, dict[str, Any]],
    source_requirements_sha256: str,
    source_drawing_sha256: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    replay: list[dict[str, Any]] = []
    committed_edit_ids: list[str] = []
    node_ids_added: list[str] = []
    wire_ids_added: list[str] = []
    confirmed_revision_pairs: list[dict[str, str]] = []

    for decision_index, decision in enumerate(history, start=1):
        candidate = candidates_by_key.get(_str(decision.get("target_key")))
        if not candidate:
            continue
        proposal = _streamed_proposal_from_candidate(
            candidate,
            sequence_index=len(committed_edit_ids) + 1,
            source_requirements_sha256=source_requirements_sha256,
            source_drawing_sha256=source_drawing_sha256,
            decision_history_count=decision_index,
        )
        proposal_id = _str(decision.get("proposal_id")) or proposal["id"]
        committed = decision.get("decision") == "confirm"
        previous_revision = None
        if committed:
            for previous in reversed(history[: decision_index - 1]):
                if (
                    previous.get("decision") == "request_revision"
                    and previous.get("target_key") == decision.get("target_key")
                ):
                    previous_revision = previous
                    break
        confirmed_revision_of = _str(previous_revision.get("proposal_id")) if previous_revision else ""
        if confirmed_revision_of == proposal_id:
            confirmed_revision_of = ""
        graph_diff = proposal["graph_diff"]
        feedback_text = _str(decision.get("feedback_text"))
        requirements_patch = decision.get("requirements_document_patch")
        requirements_patch_is_dict = isinstance(requirements_patch, dict)
        requirements_patch_sha256 = (
            _payload_sha256(requirements_patch) if requirements_patch_is_dict else ""
        )
        requirements_edit_requested = decision.get("requirements_document_edit_requested") is True
        requirements_edit_authorized = decision.get("requirements_document_edit_authorized") is True
        if requirements_edit_authorized:
            requirements_patch_status = "authorized_candidate_patch"
        elif requirements_edit_requested:
            requirements_patch_status = "authorization_required"
        else:
            requirements_patch_status = "not_requested"
        replay_event = {
            "kind": "ai-fantui-streamed-logic-authoring-replay-event",
            "version": STREAMED_LOGIC_AUTHORING_VERSION,
            "id": f"m21-replay-{decision_index}",
            "decision_index": decision_index,
            "event_type": "candidate_edit_committed" if committed else "candidate_edit_revision_requested",
            "proposal_id": proposal_id,
            "target_type": proposal["target_type"],
            "target_id": proposal["target_id"],
            "display_label": proposal["display_label"],
            "source_excerpt": proposal["source_excerpt"],
            "source_anchor_ids": proposal["source_anchor_ids"],
            "interpreted_logic": proposal["interpreted_logic"],
            "graph_diff": graph_diff,
            "committed": committed,
            "user_feedback": feedback_text,
            "decided_at": _str(decision.get("decided_at")),
            "requirements_document_edit_requested": requirements_edit_requested,
            "requirements_document_edit_authorized": requirements_edit_authorized,
            "requirements_document_patch_status": requirements_patch_status,
            "requirements_document_patch": requirements_patch if requirements_patch_is_dict else None,
            "requirements_document_patch_sha256": requirements_patch_sha256,
            "requirements_document_authorization_gate": {
                "required_phrase": STREAMED_REQUIREMENTS_EDIT_AUTHORIZATION_PHRASE,
                "provided_phrase_matches": requirements_edit_authorized,
                "status": (
                    "authorized"
                    if requirements_edit_authorized
                    else (
                        "blocked_without_explicit_authorization"
                        if requirements_edit_requested
                        else "not_requested"
                    )
                ),
            },
            "requirements_document_modified": False,
            "truth_effect": "none",
            "controller_truth_modified": False,
            "commit_boundary": "one_confirmed_candidate_edit_per_user_decision",
            "confirmed_revision_of": confirmed_revision_of,
            "commits_revision": bool(confirmed_revision_of),
        }
        if not committed:
            replay_event["candidate_recalculation"] = {
                "status": "revision_candidate_ready",
                "source_proposal_id": proposal_id,
                "feedback_text": feedback_text,
                "feedback_sha256": hashlib.sha256(feedback_text.encode("utf-8")).hexdigest()
                if feedback_text
                else "",
                "truth_effect": "none",
                "controller_truth_modified": False,
            }
        if committed:
            replay_event["committed_edit_index"] = len(committed_edit_ids) + 1
            committed_edit_ids.append(proposal_id)
            if confirmed_revision_of:
                confirmed_revision_pairs.append(
                    {
                        "committed_proposal_id": proposal_id,
                        "revision_of": confirmed_revision_of,
                        "target_key": _str(decision.get("target_key")),
                    }
                )
            node_ids_added.extend(graph_diff.get("node_ids_added", []))
            wire_ids_added.extend(graph_diff.get("wire_ids_added", []))
        replay.append(replay_event)

    if not committed_edit_ids:
        status = "empty"
    elif len(committed_edit_ids) == 1:
        status = "one_edit_committed"
    else:
        status = "multiple_edits_committed"
    committed_graph = {
        "kind": "ai-fantui-streamed-logic-authoring-committed-candidate-graph",
        "version": STREAMED_LOGIC_AUTHORING_VERSION,
        "status": status,
        "commit_boundary": "one_confirmed_candidate_edit_per_user_decision",
        "committed_edit_count": len(committed_edit_ids),
        "committed_edit_ids": committed_edit_ids,
        "confirmed_revision_pairs": confirmed_revision_pairs,
        "node_ids_added": node_ids_added,
        "wire_ids_added": wire_ids_added,
        "truth_effect": "none",
        "controller_truth_modified": False,
        "requirements_document_modified": False,
        "replay_event_ids": [
            event["id"] for event in replay if event.get("committed") is True
        ],
    }
    return replay, committed_graph


def _streamed_candidate_queue_state(
    *,
    candidates: list[dict[str, Any]],
    active_proposal: dict[str, Any] | None,
    accepted_keys: set[str],
    rejected_items: list[dict[str, Any]],
    stream_replay: list[dict[str, Any]],
    committed_candidate_graph: dict[str, Any],
) -> dict[str, Any]:
    active_target_type = _str(active_proposal.get("target_type")) if active_proposal else ""
    active_target_id = _str(active_proposal.get("target_id")) if active_proposal else ""
    active_target_key = (
        _streamed_target_key(active_target_type, active_target_id)
        if active_target_type and active_target_id
        else ""
    )
    ordered_target_keys = [
        _streamed_target_key(_str(item.get("target_type")), _str(item.get("target_id")))
        for item in candidates
    ]
    revised_targets_confirmed = {
        item["target_key"]
        for item in rejected_items
        if item.get("target_key") in accepted_keys
    }
    if not active_proposal:
        status = "candidate_queue_completed"
    elif active_proposal.get("proposal_status") == "revised_proposal_ready":
        status = "revision_candidate_ready"
    else:
        status = "candidate_queue_active"
    total_count = len(candidates)
    accepted_count = len(accepted_keys)
    return {
        "kind": "ai-fantui-streamed-logic-authoring-candidate-queue",
        "version": STREAMED_LOGIC_AUTHORING_VERSION,
        "status": status,
        "total_candidate_count": total_count,
        "accepted_count": accepted_count,
        "rejected_count": len(rejected_items),
        "committed_count": int(committed_candidate_graph.get("committed_edit_count") or 0),
        "pending_count": max(total_count - accepted_count, 0),
        "replay_event_count": len(stream_replay),
        "ordered_target_keys": ordered_target_keys,
        "accepted_target_keys": sorted(accepted_keys),
        "rejected_target_keys": [
            _str(item.get("target_key")) for item in rejected_items if item.get("target_key")
        ],
        "revised_targets_confirmed": sorted(revised_targets_confirmed),
        "can_continue_after_revision": bool(revised_targets_confirmed),
        "active_target_key": active_target_key,
        "active_target_type": active_target_type,
        "active_target_id": active_target_id,
        "active_sequence_index": int(active_proposal.get("sequence_index") or 0)
        if active_proposal
        else 0,
        "active_revision_index": int(active_proposal.get("revision_index") or 0)
        if active_proposal
        else 0,
        "next_candidate_kind": active_target_type,
        "truth_effect": "none",
        "controller_truth_modified": False,
        "requirements_document_modified": False,
    }


def build_streamed_logic_authoring_session(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    *,
    decision_history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    _validate_requirements_payload(requirements_payload)
    _validate_drawing_payload(drawing_payload)
    source_requirements_sha256 = _payload_sha256(requirements_payload)
    source_drawing_sha256 = _payload_sha256(drawing_payload)
    history = _filter_streamed_decision_history(
        _normalize_streamed_decision_history(decision_history),
        source_requirements_sha256=source_requirements_sha256,
        source_drawing_sha256=source_drawing_sha256,
    )
    accepted_keys = {item["target_key"] for item in history if item["decision"] == "confirm" and item["target_key"]}
    accepted_edit_ids = [item["proposal_id"] for item in history if item["decision"] == "confirm" and item["proposal_id"]]
    rejected_items = [item for item in history if item["decision"] == "request_revision" and item["target_key"]]
    rejected_edit_ids = [item["proposal_id"] for item in rejected_items if item["proposal_id"]]
    candidates = _streamed_candidate_objects(requirements_payload, drawing_payload)
    candidates_by_key = {
        _streamed_target_key(_str(item.get("target_type")), _str(item.get("target_id"))): item
        for item in candidates
    }
    stream_replay, committed_candidate_graph = _streamed_replay_and_committed_graph(
        history=history,
        candidates_by_key=candidates_by_key,
        source_requirements_sha256=source_requirements_sha256,
        source_drawing_sha256=source_drawing_sha256,
    )
    active_proposal: dict[str, Any] | None = None
    latest_rejected = rejected_items[-1] if rejected_items else None
    if latest_rejected and latest_rejected["target_key"] not in accepted_keys:
        candidate = candidates_by_key.get(latest_rejected["target_key"])
        if candidate:
            revision_count = sum(
                1
                for item in rejected_items
                if item["target_key"] == latest_rejected["target_key"]
            )
            active_proposal = _streamed_proposal_from_candidate(
                candidate,
                sequence_index=len(accepted_keys) + 1,
                revision_of=latest_rejected["proposal_id"],
                user_feedback=latest_rejected["feedback_text"],
                revision_index=revision_count,
                feedback_decided_at=latest_rejected["decided_at"],
                source_requirements_sha256=source_requirements_sha256,
                source_drawing_sha256=source_drawing_sha256,
                decision_history_count=len(history),
            )
    if active_proposal is None:
        for index, candidate in enumerate(candidates, start=1):
            key = _streamed_target_key(_str(candidate.get("target_type")), _str(candidate.get("target_id")))
            if key in accepted_keys:
                continue
            active_proposal = _streamed_proposal_from_candidate(
                candidate,
                sequence_index=len(accepted_keys) + 1,
                source_requirements_sha256=source_requirements_sha256,
                source_drawing_sha256=source_drawing_sha256,
                decision_history_count=len(history),
            )
            break
    candidate_queue = _streamed_candidate_queue_state(
        candidates=candidates,
        active_proposal=active_proposal,
        accepted_keys=accepted_keys,
        rejected_items=rejected_items,
        stream_replay=stream_replay,
        committed_candidate_graph=committed_candidate_graph,
    )

    return {
        "$schema": "https://well-harness.local/json_schema/streamed_logic_authoring_session_v1.schema.json",
        "kind": STREAMED_LOGIC_AUTHORING_SESSION_KIND,
        "version": STREAMED_LOGIC_AUTHORING_VERSION,
        "status": "awaiting_user_confirmation" if active_proposal else "completed",
        "m21_mode": "engineer_in_the_loop_streamed_authoring",
        "truth_effect": "none",
        "candidate_state": "streamed_logic_authoring_candidate",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": source_requirements_sha256,
        "source_drawing_sha256": source_drawing_sha256,
        "accepted_edit_ids": accepted_edit_ids,
        "rejected_edit_ids": rejected_edit_ids,
        "decision_history": history,
        "stream_replay": stream_replay,
        "committed_candidate_graph": committed_candidate_graph,
        "candidate_queue": candidate_queue,
        "proposal_count": len(candidates),
        "active_proposal": active_proposal,
        "requirements_document_edit": _streamed_requirements_document_edit_gate(history),
        "non_claims": [
            "no controller truth promotion",
            "no automatic requirements document mutation",
            "no certification or DAL readiness claim",
            "no whole-graph black-box generation acceptance",
        ],
    }


def _normalize_change_interpretation(
    raw: str,
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    annotation_text: str,
    target_node_id: str,
    annotation_batch: list[dict[str, str]] | None = None,
    selected_nodes: list[str] | None = None,
    selected_edges: list[str] | None = None,
) -> dict[str, Any]:
    try:
        parsed = _extract_json_object(_strip_model_json(raw))
    except json.JSONDecodeError as exc:
        raise RequirementsIntakeError("logic_change_json_error", "Model change interpretation was not valid JSON.", status_code=502) from exc

    node_ids, edge_ids, panel_ids = _drawing_id_sets(drawing_payload)
    selected_node = target_node_id if target_node_id in node_ids else ""
    batch = _normalize_annotation_batch(annotation_batch)
    annotation_ids = {item["id"] for item in batch}
    annotation_groups = _normalize_annotation_groups(parsed.get("annotation_groups"), annotation_ids)
    if batch and not annotation_groups:
        annotation_groups = [
            {
                "group_label": "本次批注",
                "annotation_ids": [item["id"] for item in batch[:8]],
                "summary_zh": "模型未返回分组，已按本次提交保留批注集合。",
            }
        ]
    proposed_changes = _string_list(parsed.get("proposed_changes"), limit=5)
    understanding = _str(parsed.get("understanding_zh"))[:280]
    question = _str(parsed.get("confirmation_question_zh"))[:220]
    if not question:
        question = "请确认模型对这条修改意见的理解是否正确？"
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_change_interpretation_v1.schema.json",
        "kind": LOGIC_CHANGE_INTERPRETATION_KIND,
        "version": LOGIC_CHANGE_INTERPRETATION_VERSION,
        "status": "needs_user_confirmation",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing_change",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "source_drawing_sha256": _payload_sha256(drawing_payload),
        "target_node_id": selected_node,
        "selected_nodes": _string_list(selected_nodes, allowed=node_ids, limit=12),
        "selected_edges": _string_list(selected_edges, limit=12),
        "annotation_batch": batch,
        "annotation_text": annotation_text[:800],
        "understanding_zh": understanding or "模型未返回明确理解，请补充修改意见。",
        "requirements_match_zh": _str(parsed.get("requirements_match_zh"))[:280],
        "affected_nodes": _string_list(parsed.get("affected_nodes"), allowed=node_ids, limit=8),
        "affected_edges": _string_list(parsed.get("affected_edges"), allowed=edge_ids, limit=10),
        "affected_parameter_panels": _string_list(parsed.get("affected_parameter_panels"), allowed=panel_ids, limit=8),
        "proposed_changes": proposed_changes,
        "annotation_batch_summary_zh": _str(
            parsed.get("annotation_batch_summary_zh"),
            f"已收到 {len(batch)} 条标注意见。" if batch else "",
        )[:280],
        "conflict_summary_zh": _str(
            parsed.get("conflict_summary_zh"),
            "未发现冲突。" if batch else "",
        )[:280],
        "annotation_groups": annotation_groups,
        "confirmation_question_zh": question,
    }


def _normalize_fault_scenarios(value: Any, node_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RequirementsIntakeError(
            "fault_injection_json_error",
            "Fault injection preparation must include fault_scenarios.",
            status_code=502,
        )
    scenarios: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        node_id = _str(item.get("node_id"))
        if node_id not in node_ids:
            raise RequirementsIntakeError(
                "fault_injection_json_error",
                "Fault scenario node_id must reference a drawing node.",
                status_code=502,
                details={"scenario": item.get("id") or f"fault_{index}", "node_id": node_id},
            )
        scenario_id = _str(item.get("id"), f"fault_{index}")
        if scenario_id in seen:
            scenario_id = f"{scenario_id}_{index}"
        seen.add(scenario_id)
        scenarios.append(
            {
                "id": scenario_id[:64],
                "label": _str(item.get("label"), scenario_id)[:60],
                "node_id": node_id,
                "fault_type": _str(item.get("fault_type"), "candidate_fault")[:48],
                "rationale_zh": _str(item.get("rationale_zh"))[:220],
                "expected_effect_zh": _str(item.get("expected_effect_zh"))[:220],
                "observable_signals": _string_list(item.get("observable_signals"), limit=8),
                "severity": _str(item.get("severity"), "medium")[:24],
            }
        )
        if len(scenarios) >= 8:
            break
    if not scenarios:
        raise RequirementsIntakeError(
            "fault_injection_json_error",
            "Fault injection preparation returned no usable fault_scenarios.",
            status_code=502,
        )
    return scenarios


def _normalize_injection_points(
    value: Any,
    node_ids: set[str],
    panel_ids: set[str],
    panel_node_map: dict[str, str],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    points: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        node_id = _str(item.get("node_id"))
        if node_id not in node_ids:
            raise RequirementsIntakeError(
                "fault_injection_json_error",
                "Injection point node_id must reference a drawing node.",
                status_code=502,
                details={"point": item.get("id") or f"point_{index}", "node_id": node_id},
            )
        panel_id = _str(item.get("parameter_panel_id"))
        if panel_id and panel_id not in panel_ids:
            raise RequirementsIntakeError(
                "fault_injection_json_error",
                "Injection point parameter_panel_id must reference a drawing parameter panel.",
                status_code=502,
                details={
                    "semantic_gate": "parameter_panel_node_match",
                    "point": item.get("id") or f"point_{index}",
                    "parameter_panel_id": panel_id,
                },
            )
        expected_node_id = panel_node_map.get(panel_id, "")
        if panel_id and expected_node_id and expected_node_id != node_id:
            raise RequirementsIntakeError(
                "fault_injection_json_error",
                "Injection point parameter panel must belong to the same drawing node.",
                status_code=502,
                details={
                    "semantic_gate": "parameter_panel_node_match",
                    "point": item.get("id") or f"point_{index}",
                    "node_id": node_id,
                    "parameter_panel_id": panel_id,
                    "expected_node_id": expected_node_id,
                },
            )
        point_id = _str(item.get("id"), f"point_{index}")
        if point_id in seen:
            point_id = f"{point_id}_{index}"
        seen.add(point_id)
        points.append(
            {
                "id": point_id[:64],
                "node_id": node_id,
                "parameter_panel_id": panel_id,
                "signal_name": _str(item.get("signal_name"), node_id)[:60],
                "injection_mode": _str(item.get("injection_mode"), "candidate_override")[:48],
                "safe_boundary_zh": _str(item.get("safe_boundary_zh"))[:220],
            }
        )
        if len(points) >= 8:
            break
    return points


def _validate_fault_preparation_semantics(
    preparation: dict[str, Any],
    drawing_payload: dict[str, Any],
) -> None:
    critical_nodes = _critical_fault_node_ids(drawing_payload)
    if not critical_nodes:
        return
    covered_nodes = {
        _str(item.get("node_id"))
        for item in preparation.get("fault_scenarios", [])
        if isinstance(item, dict) and _str(item.get("node_id"))
    }
    covered_nodes.update(
        _str(item.get("node_id"))
        for item in preparation.get("injection_points", [])
        if isinstance(item, dict) and _str(item.get("node_id"))
    )
    missing = sorted(critical_nodes - covered_nodes)
    if missing:
        raise RequirementsIntakeError(
            "fault_injection_json_error",
            "Fault injection preparation must cover critical drawing nodes.",
            status_code=502,
            details={
                "semantic_gate": "critical_node_coverage",
                "missing_critical_nodes": missing,
            },
        )


def _drawing_node_by_id(drawing_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _str(item.get("id")): item
        for item in drawing_payload.get("nodes", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }


def _fault_preparation_covered_node_ids(preparation: dict[str, Any]) -> set[str]:
    covered = {
        _str(item.get("node_id"))
        for item in preparation.get("fault_scenarios", [])
        if isinstance(item, dict) and _str(item.get("node_id"))
    }
    covered.update(
        _str(item.get("node_id"))
        for item in preparation.get("injection_points", [])
        if isinstance(item, dict) and _str(item.get("node_id"))
    )
    return covered


def _fault_safe_id(prefix: str, node_id: str, existing: set[str]) -> str:
    stem = re.sub(r"[^A-Za-z0-9_]+", "_", node_id).strip("_").lower() or "node"
    candidate = f"{prefix}_{stem}"[:64]
    if candidate not in existing:
        existing.add(candidate)
        return candidate
    for index in range(2, 100):
        variant = f"{candidate[:58]}_{index}"
        if variant not in existing:
            existing.add(variant)
            return variant
    existing.add(candidate)
    return candidate


def _complete_fault_preparation_coverage(
    preparation: dict[str, Any],
    drawing_payload: dict[str, Any],
) -> None:
    critical_nodes = _critical_fault_node_ids(drawing_payload)
    missing = sorted(critical_nodes - _fault_preparation_covered_node_ids(preparation))
    if not missing:
        return

    nodes_by_id = _drawing_node_by_id(drawing_payload)
    scenario_ids = {
        _str(item.get("id"))
        for item in preparation.get("fault_scenarios", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }
    completed: list[str] = []
    for node_id in missing:
        node = nodes_by_id.get(node_id, {})
        label = _str(node.get("label"), node_id)
        kind = _str(node.get("node_kind"), "logic")
        scenario_id = _fault_safe_id("auto_fault", node_id, scenario_ids)
        preparation.setdefault("fault_scenarios", []).append(
            {
                "id": scenario_id,
                "label": f"{label} 覆盖候选"[:60],
                "node_id": node_id,
                "fault_type": "dry_run_observation_gap",
                "rationale_zh": f"{label} 是关键 {kind} 节点，需要进入故障候选覆盖清单。",
                "expected_effect_zh": "用于 dry-run 沙盒中观察该节点异常或边界偏移是否影响下游逻辑。",
                "observable_signals": [node_id],
                "severity": "medium",
            }
        )
        completed.append(node_id)
    preparation["coverage_completion"] = {
        "strategy": "deterministic_dry_run_candidate",
        "completed_node_ids": completed,
        "semantic_gate": "critical_node_coverage",
    }
    notes = preparation.setdefault("workflow_notes", [])
    if isinstance(notes, list):
        notes.append("已自动补齐关键节点覆盖候选；进入沙盒前仍需工程师确认边界。")


def _normalize_boundary_questions(value: Any) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue
            prompt = _str(item.get("prompt_zh") or item.get("question_zh")).strip()
            if not prompt:
                continue
            questions.append(
                {
                    "id": _str(item.get("id"), f"boundary_{index}")[:64],
                    "prompt_zh": prompt[:220],
                    "rationale_zh": _str(item.get("rationale_zh"))[:220],
                    "blocks": "fault_injection",
                }
            )
            if len(questions) >= 6:
                break
    if questions:
        return questions
    return [
        {
            "id": "confirm_fault_scope",
            "prompt_zh": "请确认本轮故障注入候选只用于沙盒准备，不进入真实控制或认证结论。",
            "rationale_zh": "故障注入前必须确认安全边界。",
            "blocks": "fault_injection",
        }
    ]


def _validate_fault_preparation_payload(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise RequirementsIntakeError(
            "invalid_fault_injection_preparation_payload",
            "fault_injection_preparation_payload must be an object.",
        )
    if payload.get("kind") != FAULT_INJECTION_PREPARATION_KIND:
        raise RequirementsIntakeError(
            "invalid_fault_injection_preparation_payload",
            "fault_injection_preparation_payload must come from the fault injection preparation step.",
        )
    if not isinstance(payload.get("fault_scenarios"), list) or not payload.get("fault_scenarios"):
        raise RequirementsIntakeError(
            "invalid_fault_injection_preparation_payload",
            "fault_injection_preparation_payload must include fault_scenarios.",
            status_code=409,
        )


def _normalize_fault_injection_preparation(
    raw: str,
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    change_history: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        parsed = _extract_json_object(_strip_model_json(raw))
    except json.JSONDecodeError as exc:
        raise RequirementsIntakeError(
            "fault_injection_json_error",
            "Model fault injection preparation was not valid JSON.",
            status_code=502,
        ) from exc

    node_ids, _edge_ids, panel_ids = _drawing_id_sets(drawing_payload)
    panel_node_map = _parameter_panel_node_map(drawing_payload)
    assumptions = parsed.get("assumptions")
    if not isinstance(assumptions, list):
        assumptions = []
    notes = parsed.get("workflow_notes")
    if not isinstance(notes, list):
        notes = []
    preparation = {
        "$schema": "https://well-harness.local/json_schema/requirements_fault_injection_preparation_v1.schema.json",
        "kind": FAULT_INJECTION_PREPARATION_KIND,
        "version": FAULT_INJECTION_PREPARATION_VERSION,
        "status": "needs_user_confirmation",
        "truth_effect": "none",
        "candidate_state": "fault_injection_preparation",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "source_drawing_sha256": _payload_sha256(drawing_payload),
        "source_change_history_sha256": _payload_sha256({"change_history": _limited_change_history(change_history)}),
        "summary_zh": _str(parsed.get("summary_zh"), "模型已生成故障注入准备候选。")[:220],
        "assumptions": [_str(item)[:160] for item in assumptions[:6] if _str(item)],
        "fault_scenarios": _normalize_fault_scenarios(parsed.get("fault_scenarios"), node_ids),
        "injection_points": _normalize_injection_points(
            parsed.get("injection_points"),
            node_ids,
            panel_ids,
            panel_node_map,
        ),
        "boundary_questions": _normalize_boundary_questions(parsed.get("boundary_questions")),
        "workflow_notes": [_str(item)[:160] for item in notes[:4] if _str(item)],
    }
    _complete_fault_preparation_coverage(preparation, drawing_payload)
    _validate_fault_preparation_semantics(preparation, drawing_payload)
    _attach_fault_preparation_source_context(preparation, requirements_payload, drawing_payload)
    return preparation


def _attach_fault_preparation_source_context(
    preparation: dict[str, Any],
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
) -> None:
    if requirements_payload.get("source_scope"):
        preparation["source_scope"] = requirements_payload.get("source_scope")
    nodes_by_id = {
        _str(item.get("id")): item
        for item in drawing_payload.get("nodes", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }
    for key in ("fault_scenarios", "injection_points"):
        for item in preparation.get(key, []):
            if not isinstance(item, dict):
                continue
            node = nodes_by_id.get(_str(item.get("node_id")), {})
            anchors = _normalize_source_anchors(item.get("source_anchors")) or _normalize_source_anchors(node.get("source_anchors"))
            item["source_anchors"] = anchors
            item["provenance"] = "model_fault_candidate_from_source_node" if anchors else "model_assumption"


def _fault_preparation_ids(payload: dict[str, Any]) -> tuple[set[str], set[str]]:
    scenario_ids = {
        _str(item.get("id"))
        for item in payload.get("fault_scenarios", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }
    node_ids = {
        _str(item.get("node_id"))
        for item in payload.get("fault_scenarios", [])
        if isinstance(item, dict) and _str(item.get("node_id"))
    }
    node_ids.update(
        _str(item.get("node_id"))
        for item in payload.get("injection_points", [])
        if isinstance(item, dict) and _str(item.get("node_id"))
    )
    return scenario_ids, node_ids


def _normalize_sandbox_injection_plan(
    value: Any,
    scenario_ids: set[str],
    node_ids: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise RequirementsIntakeError(
            "fault_injection_sandbox_json_error",
            "Fault injection sandbox plan must include sandbox_injection_plan.",
            status_code=502,
        )
    plans: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            continue
        scenario_id = _str(item.get("fault_scenario_id"))
        if scenario_id not in scenario_ids:
            raise RequirementsIntakeError(
                "fault_injection_sandbox_json_error",
                "Sandbox injection plan fault_scenario_id must reference a prepared fault scenario.",
                status_code=502,
                details={"plan": item.get("id") or f"inject_{index}", "fault_scenario_id": scenario_id},
            )
        node_id = _str(item.get("node_id"))
        if node_id and node_ids and node_id not in node_ids:
            raise RequirementsIntakeError(
                "fault_injection_sandbox_json_error",
                "Sandbox injection plan node_id must reference a prepared node.",
                status_code=502,
                details={"plan": item.get("id") or f"inject_{index}", "node_id": node_id},
            )
        plan_id = _str(item.get("id"), f"inject_{index}")
        if plan_id in seen:
            plan_id = f"{plan_id}_{index}"
        seen.add(plan_id)
        plans.append(
            {
                "id": plan_id[:64],
                "fault_scenario_id": scenario_id,
                "node_id": node_id,
                "signal_name": _str(item.get("signal_name"), node_id or scenario_id)[:60],
                "injection_mode": _str(item.get("injection_mode"), "dry_run_override")[:48],
                "safe_range_zh": _str(item.get("safe_range_zh"))[:220],
                "duration_ms": int(max(0.0, _num(item.get("duration_ms"), default=0.0))),
                "expected_effect_zh": _str(item.get("expected_effect_zh") or item.get("expected_effect"))[:220],
            }
        )
        if len(plans) >= 8:
            break
    if not plans:
        raise RequirementsIntakeError(
            "fault_injection_sandbox_json_error",
            "Fault injection sandbox response returned no usable sandbox_injection_plan.",
            status_code=502,
        )
    return plans


def _validate_sandbox_plan_semantics(
    sandbox_plan: dict[str, Any],
    fault_injection_preparation_payload: dict[str, Any],
) -> None:
    scenario_ids, _node_ids = _fault_preparation_ids(fault_injection_preparation_payload)
    planned_ids = {
        _str(item.get("fault_scenario_id"))
        for item in sandbox_plan.get("sandbox_injection_plan", [])
        if isinstance(item, dict) and _str(item.get("fault_scenario_id"))
    }
    missing = sorted(scenario_ids - planned_ids)
    if missing:
        raise RequirementsIntakeError(
            "fault_injection_sandbox_json_error",
            "Fault injection sandbox plan must cover every prepared fault scenario.",
            status_code=502,
            details={
                "semantic_gate": "scenario_plan_coverage",
                "missing_fault_scenario_ids": missing,
            },
        )


def _fault_scenarios_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _str(item.get("id")): item
        for item in payload.get("fault_scenarios", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }


def _sandbox_planned_fault_scenario_ids(sandbox_plan: dict[str, Any]) -> set[str]:
    return {
        _str(item.get("fault_scenario_id"))
        for item in sandbox_plan.get("sandbox_injection_plan", [])
        if isinstance(item, dict) and _str(item.get("fault_scenario_id"))
    }


def _scenario_signal_name(scenario: dict[str, Any], scenario_id: str, node_id: str) -> str:
    signals = scenario.get("observable_signals")
    if isinstance(signals, list):
        for signal in signals:
            signal_name = _str(signal)
            if signal_name:
                return signal_name[:60]
    return _str(node_id or scenario_id, scenario_id)[:60]


def _complete_sandbox_plan_coverage(
    sandbox_plan: dict[str, Any],
    fault_injection_preparation_payload: dict[str, Any],
) -> None:
    scenario_ids, node_ids = _fault_preparation_ids(fault_injection_preparation_payload)
    missing = sorted(scenario_ids - _sandbox_planned_fault_scenario_ids(sandbox_plan))
    if not missing:
        return

    scenarios_by_id = _fault_scenarios_by_id(fault_injection_preparation_payload)
    existing_plan_ids = {
        _str(item.get("id"))
        for item in sandbox_plan.get("sandbox_injection_plan", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }
    existing_observation_ids = {
        _str(item.get("id"))
        for item in sandbox_plan.get("observation_points", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }
    existing_check_ids = {
        _str(item.get("id"))
        for item in sandbox_plan.get("review_checklist", [])
        if isinstance(item, dict) and _str(item.get("id"))
    }

    completed: list[str] = []
    for scenario_id in missing:
        scenario = scenarios_by_id.get(scenario_id, {})
        node_id = _str(scenario.get("node_id"))
        if node_id and node_ids and node_id not in node_ids:
            node_id = ""
        signal_name = _scenario_signal_name(scenario, scenario_id, node_id)
        expected_effect = _str(
            scenario.get("expected_effect_zh") or scenario.get("expected_effect"),
            "观察该故障候选在 dry-run 沙盒下的下游影响。",
        )[:220]
        sandbox_plan.setdefault("sandbox_injection_plan", []).append(
            {
                "id": _fault_safe_id("auto_plan", scenario_id, existing_plan_ids),
                "fault_scenario_id": scenario_id,
                "node_id": node_id,
                "signal_name": signal_name,
                "injection_mode": "dry_run_observe",
                "safe_range_zh": "仅作为 dry-run 沙盒建议；不触发真实仿真、tick 或控制器写入。",
                "duration_ms": 0,
                "expected_effect_zh": expected_effect,
            }
        )
        sandbox_plan.setdefault("observation_points", []).append(
            {
                "id": _fault_safe_id("auto_obs", scenario_id, existing_observation_ids),
                "node_id": node_id,
                "signal_name": signal_name,
                "check_zh": "观察自动补齐的 dry-run 故障候选是否具备可审查的下游影响说明。",
            }
        )
        sandbox_plan.setdefault("review_checklist", []).append(
            {
                "id": _fault_safe_id("auto_review", scenario_id, existing_check_ids),
                "category": "coverage_completion",
                "condition_zh": f"{scenario_id} 已由本地覆盖补齐器生成 dry-run 沙盒计划。",
                "pass_criteria_zh": "工程师确认该候选只用于审查，不进入真实控制或认证结论。",
            }
        )
        completed.append(scenario_id)

    sandbox_plan["plan_coverage_completion"] = {
        "strategy": "deterministic_dry_run_plan",
        "completed_fault_scenario_ids": completed,
        "semantic_gate": "scenario_plan_coverage",
    }
    notes = sandbox_plan.setdefault("workflow_notes", [])
    if isinstance(notes, list):
        notes.append("已自动补齐未被模型覆盖的故障场景 dry-run 沙盒计划。")


def _normalize_observation_points(value: Any, node_ids: set[str]) -> list[dict[str, str]]:
    points: list[dict[str, str]] = []
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue
            node_id = _str(item.get("node_id"))
            if node_id and node_ids and node_id not in node_ids:
                node_id = ""
            signal_name = _str(item.get("signal_name"), node_id or f"signal_{index}")[:60]
            check = _str(item.get("check_zh") or item.get("check"))[:220]
            if not signal_name and not check:
                continue
            points.append(
                {
                    "id": _str(item.get("id"), f"obs_{index}")[:64],
                    "node_id": node_id,
                    "signal_name": signal_name,
                    "check_zh": check or "观察该信号在 dry-run 配置下的预期变化。",
                }
            )
            if len(points) >= 8:
                break
    if points:
        return points
    return [
        {
            "id": "obs_review_only",
            "node_id": "",
            "signal_name": "review_only",
            "check_zh": "检查沙盒配置建议，不执行仿真。",
        }
    ]


def _normalize_review_checklist(value: Any) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    if isinstance(value, list):
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                continue
            condition = _str(item.get("condition_zh") or item.get("condition")).strip()
            criteria = _str(item.get("pass_criteria_zh") or item.get("pass_criteria")).strip()
            if not condition and not criteria:
                continue
            items.append(
                {
                    "id": _str(item.get("id"), f"chk_{index}")[:64],
                    "category": _str(item.get("category"), "review")[:40],
                    "condition_zh": condition[:220],
                    "pass_criteria_zh": criteria[:220],
                }
            )
            if len(items) >= 8:
                break
    items.append(
        {
            "id": "chk_dry_run_contract",
            "category": "safety",
            "condition_zh": "不调用真实仿真、tick 或控制接口。",
            "pass_criteria_zh": "execution_contract.run_tick=false, simulate=false, dry_run_only=true。",
        }
    )
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in items:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        deduped.append(item)
    return deduped[:8]


def _normalize_fault_injection_sandbox_plan(
    raw: str,
    fault_injection_preparation_payload: dict[str, Any],
    boundary_answers: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        parsed = _extract_json_object(_strip_model_json(raw))
    except json.JSONDecodeError as exc:
        raise RequirementsIntakeError(
            "fault_injection_sandbox_json_error",
            "Model fault injection sandbox plan was not valid JSON.",
            status_code=502,
        ) from exc

    scenario_ids, node_ids = _fault_preparation_ids(fault_injection_preparation_payload)
    notes = parsed.get("workflow_notes")
    if not isinstance(notes, list):
        notes = []
    sandbox_plan = {
        "$schema": "https://well-harness.local/json_schema/requirements_fault_injection_sandbox_plan_v1.schema.json",
        "kind": FAULT_INJECTION_SANDBOX_PLAN_KIND,
        "version": FAULT_INJECTION_SANDBOX_PLAN_VERSION,
        "status": "ready_for_review",
        "truth_effect": "none",
        "candidate_state": "fault_injection_sandbox_plan",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_fault_injection_preparation_sha256": _payload_sha256(fault_injection_preparation_payload),
        "source_boundary_answers_sha256": _payload_sha256({"boundary_answers": _limited_boundary_answers(boundary_answers)}),
        "summary_zh": _str(parsed.get("summary_zh"), "模型已生成沙盒故障注入配置建议。")[:220],
        "sandbox_injection_plan": _normalize_sandbox_injection_plan(
            parsed.get("sandbox_injection_plan"),
            scenario_ids,
            node_ids,
        ),
        "observation_points": _normalize_observation_points(parsed.get("observation_points"), node_ids),
        "review_checklist": _normalize_review_checklist(parsed.get("review_checklist")),
        "execution_contract": {
            "run_tick": False,
            "simulate": False,
            "dry_run_only": True,
        },
        "workflow_notes": [_str(item)[:160] for item in notes[:4] if _str(item)],
    }
    _complete_sandbox_plan_coverage(sandbox_plan, fault_injection_preparation_payload)
    _validate_sandbox_plan_semantics(sandbox_plan, fault_injection_preparation_payload)
    _attach_sandbox_source_context(sandbox_plan, fault_injection_preparation_payload)
    return sandbox_plan


def _attach_sandbox_source_context(
    sandbox_plan: dict[str, Any],
    fault_injection_preparation_payload: dict[str, Any],
) -> None:
    if fault_injection_preparation_payload.get("source_scope"):
        sandbox_plan["source_scope"] = fault_injection_preparation_payload.get("source_scope")
    scenarios_by_id = _fault_scenarios_by_id(fault_injection_preparation_payload)
    for plan in sandbox_plan.get("sandbox_injection_plan", []):
        if not isinstance(plan, dict):
            continue
        scenario = scenarios_by_id.get(_str(plan.get("fault_scenario_id")), {})
        anchors = _normalize_source_anchors(plan.get("source_anchors")) or _normalize_source_anchors(scenario.get("source_anchors"))
        plan["source_anchors"] = anchors
        plan["provenance"] = "dry_run_plan_from_fault_candidate" if anchors else "model_assumption"
    for point in sandbox_plan.get("observation_points", []):
        if isinstance(point, dict) and "source_anchors" not in point:
            point["source_anchors"] = []
            point["provenance"] = "model_assumption"
    for item in sandbox_plan.get("review_checklist", []):
        if isinstance(item, dict) and "source_anchors" not in item:
            item["source_anchors"] = []
            item["provenance"] = "model_assumption"


def _self_repair_failure_details(original_error: RequirementsIntakeError, repair_error: RequirementsIntakeError) -> dict[str, Any]:
    details = dict(original_error.details)
    details["self_repair"] = {
        "attempted": True,
        "success": False,
        "error": repair_error.code,
        "message": repair_error.message,
    }
    if repair_error.details:
        details["self_repair"]["details"] = repair_error.details
    return details


def _self_repair_success(reason: str) -> dict[str, Any]:
    return {
        "attempted": True,
        "success": True,
        "reason": reason,
    }


def build_logic_drawing(
    requirements_payload: dict[str, Any],
    *,
    provider: str = "deepseek",
    request_post: RequestPost | None = None,
) -> dict[str, Any]:
    _validate_requirements_payload(requirements_payload)
    cfg = _provider_config(provider)
    content = _call_chat_completion(
        cfg,
        _drawing_prompt(requirements_payload),
        request_post=request_post,
        max_tokens=LOGIC_DRAWING_MAX_TOKENS,
    )
    self_repair: dict[str, Any] | None = None
    try:
        drawing = _normalize_logic_drawing(content, requirements_payload)
    except RequirementsIntakeError as original_error:
        if original_error.code != "logic_drawing_json_error":
            raise
        try:
            repaired_content = _call_chat_completion(
                cfg,
                _drawing_repair_prompt(requirements_payload, content, original_error),
                request_post=request_post,
                max_tokens=LOGIC_DRAWING_MAX_TOKENS,
            )
            drawing = _normalize_logic_drawing(repaired_content, requirements_payload)
        except RequirementsIntakeError as repair_error:
            raise RequirementsIntakeError(
                original_error.code,
                original_error.message,
                status_code=original_error.status_code,
                details=_self_repair_failure_details(original_error, repair_error),
            ) from repair_error
        self_repair = _self_repair_success(original_error.code)
    drawing["llm"] = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_base": cfg.api_base,
        "key_source": cfg.key_source,
        "response_source": "live_llm",
    }
    if self_repair is not None:
        drawing["llm"]["self_repair"] = self_repair
    return drawing


def interpret_logic_change(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    annotation_text: str,
    *,
    target_node_id: str = "",
    annotation_batch: list[dict[str, str]] | None = None,
    selected_nodes: list[str] | None = None,
    selected_edges: list[str] | None = None,
    provider: str = "deepseek",
    request_post: RequestPost | None = None,
) -> dict[str, Any]:
    _validate_requirements_payload(requirements_payload)
    _validate_drawing_payload(drawing_payload)
    annotation = _str(annotation_text).strip()
    if not annotation:
        raise RequirementsIntakeError(
            "missing_logic_change_annotation",
            "annotation_text must describe the requested drawing change.",
            details={"field": "annotation_text"},
        )

    cfg = _provider_config(provider)
    normalized_batch = _normalize_annotation_batch(annotation_batch)
    normalized_selected_nodes = _string_list(selected_nodes, limit=12)
    normalized_selected_edges = _string_list(selected_edges, limit=12)
    content = _call_chat_completion(
        cfg,
        _change_interpretation_prompt(
            requirements_payload,
            drawing_payload,
            annotation,
            _str(target_node_id),
            annotation_batch=normalized_batch,
            selected_nodes=normalized_selected_nodes,
            selected_edges=normalized_selected_edges,
        ),
        request_post=request_post,
        max_tokens=LOGIC_CHANGE_MAX_TOKENS,
    )
    interpretation = _normalize_change_interpretation(
        content,
        requirements_payload,
        drawing_payload,
        annotation,
        _str(target_node_id),
        annotation_batch=normalized_batch,
        selected_nodes=normalized_selected_nodes,
        selected_edges=normalized_selected_edges,
    )
    interpretation["llm"] = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_base": cfg.api_base,
        "key_source": cfg.key_source,
        "response_source": "live_llm",
    }
    return interpretation


def update_logic_drawing(
    drawing_payload: dict[str, Any],
    interpretation_payload: dict[str, Any],
    *,
    requirements_payload: dict[str, Any] | None = None,
    provider: str = "deepseek",
    request_post: RequestPost | None = None,
) -> dict[str, Any]:
    _validate_drawing_payload(drawing_payload)
    if requirements_payload is not None:
        _validate_requirements_payload(requirements_payload)
    if not isinstance(interpretation_payload, dict):
        raise RequirementsIntakeError("invalid_logic_change_interpretation", "interpretation_payload must be an object.")
    if interpretation_payload.get("kind") != LOGIC_CHANGE_INTERPRETATION_KIND:
        raise RequirementsIntakeError(
            "invalid_logic_change_interpretation",
            "interpretation_payload must come from the logic change interpreter.",
        )
    if interpretation_payload.get("status") != "confirmed_by_user":
        raise RequirementsIntakeError(
            "logic_change_not_confirmed",
            "The model-understood change must be confirmed by the user before updating the drawing.",
            status_code=409,
        )

    cfg = _provider_config(provider)
    content = _call_chat_completion(
        cfg,
        _drawing_update_prompt(drawing_payload, interpretation_payload),
        request_post=request_post,
        max_tokens=LOGIC_DRAWING_MAX_TOKENS,
    )
    updated = _normalize_logic_drawing(
        content,
        requirements_payload or drawing_payload,
        attach_agent_contracts=requirements_payload is not None,
    )
    if requirements_payload is not None:
        updated["source_requirements_sha256"] = _payload_sha256(requirements_payload)
    elif drawing_payload.get("source_requirements_sha256"):
        updated["source_requirements_sha256"] = _str(drawing_payload.get("source_requirements_sha256"))
    interpretation_sha = _payload_sha256(interpretation_payload)
    updated["source_drawing_sha256"] = _payload_sha256(drawing_payload)
    updated["change_applied"] = {
        "source_interpretation_sha256": interpretation_sha,
        "target_node_id": _str(interpretation_payload.get("target_node_id")),
        "annotation_text": _str(interpretation_payload.get("annotation_text"))[:800],
        "understanding_zh": _str(interpretation_payload.get("understanding_zh"))[:280],
    }
    updated["llm"] = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_base": cfg.api_base,
        "key_source": cfg.key_source,
        "response_source": "live_llm",
    }
    return updated


def prepare_fault_injection(
    requirements_payload: dict[str, Any],
    drawing_payload: dict[str, Any],
    *,
    change_history: list[dict[str, Any]] | None = None,
    provider: str = "deepseek",
    request_post: RequestPost | None = None,
) -> dict[str, Any]:
    _validate_requirements_payload(requirements_payload)
    _validate_drawing_payload(drawing_payload)
    history = change_history if isinstance(change_history, list) else []

    cfg = _provider_config(provider)
    content = _call_chat_completion(
        cfg,
        _fault_injection_prompt(requirements_payload, drawing_payload, history),
        request_post=request_post,
        max_tokens=FAULT_INJECTION_PREPARATION_MAX_TOKENS,
    )
    self_repair: dict[str, Any] | None = None
    try:
        preparation = _normalize_fault_injection_preparation(content, requirements_payload, drawing_payload, history)
    except RequirementsIntakeError as original_error:
        if original_error.code != "fault_injection_json_error":
            raise
        try:
            repaired_content = _call_chat_completion(
                cfg,
                _fault_injection_repair_prompt(requirements_payload, drawing_payload, history, content, original_error),
                request_post=request_post,
                max_tokens=FAULT_INJECTION_PREPARATION_MAX_TOKENS,
            )
            preparation = _normalize_fault_injection_preparation(repaired_content, requirements_payload, drawing_payload, history)
        except RequirementsIntakeError as repair_error:
            raise RequirementsIntakeError(
                original_error.code,
                original_error.message,
                status_code=original_error.status_code,
                details=_self_repair_failure_details(original_error, repair_error),
            ) from repair_error
        self_repair = _self_repair_success(original_error.code)
    preparation["llm"] = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_base": cfg.api_base,
        "key_source": cfg.key_source,
        "response_source": "live_llm",
    }
    if self_repair is not None:
        preparation["llm"]["self_repair"] = self_repair
    return preparation


def prepare_fault_injection_sandbox_plan(
    fault_injection_preparation_payload: dict[str, Any],
    *,
    boundary_answers: list[dict[str, Any]] | None = None,
    provider: str = "deepseek",
    request_post: RequestPost | None = None,
) -> dict[str, Any]:
    _validate_fault_preparation_payload(fault_injection_preparation_payload)
    answers = boundary_answers if isinstance(boundary_answers, list) else []

    cfg = _provider_config(provider)
    content = _call_chat_completion(
        cfg,
        _fault_injection_sandbox_plan_prompt(fault_injection_preparation_payload, answers),
        request_post=request_post,
        max_tokens=FAULT_INJECTION_SANDBOX_PLAN_MAX_TOKENS,
    )
    self_repair: dict[str, Any] | None = None
    try:
        sandbox_plan = _normalize_fault_injection_sandbox_plan(content, fault_injection_preparation_payload, answers)
    except RequirementsIntakeError as original_error:
        if original_error.code != "fault_injection_sandbox_json_error":
            raise
        try:
            repaired_content = _call_chat_completion(
                cfg,
                _fault_injection_sandbox_repair_prompt(fault_injection_preparation_payload, answers, content, original_error),
                request_post=request_post,
                max_tokens=FAULT_INJECTION_SANDBOX_PLAN_MAX_TOKENS,
            )
            sandbox_plan = _normalize_fault_injection_sandbox_plan(repaired_content, fault_injection_preparation_payload, answers)
        except RequirementsIntakeError as repair_error:
            raise RequirementsIntakeError(
                original_error.code,
                original_error.message,
                status_code=original_error.status_code,
                details=_self_repair_failure_details(original_error, repair_error),
            ) from repair_error
        self_repair = _self_repair_success(original_error.code)
    sandbox_plan["llm"] = {
        "provider": cfg.provider,
        "model": cfg.model,
        "api_base": cfg.api_base,
        "key_source": cfg.key_source,
        "response_source": "live_llm",
    }
    if self_repair is not None:
        sandbox_plan["llm"]["self_repair"] = self_repair
    return sandbox_plan
