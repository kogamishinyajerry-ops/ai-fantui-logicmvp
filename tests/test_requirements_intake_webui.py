from __future__ import annotations

import base64
import http.client
import io
import json
import threading
import time
import urllib.error
import zipfile
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from well_harness.agent_output_contract import validate_agent_output_contract
from well_harness.agent_execution_plan import validate_execution_plan
from well_harness.agent_execution_shell import validate_execution_evidence_package
from well_harness.agent_review_packet import (
    validate_candidate_review_packet,
    validate_candidate_review_packet_export,
)
from well_harness.agent_task_contract import validate_agent_task_package
from well_harness import demo_server
from well_harness.demo_server import DemoRequestHandler
from well_harness.requirements_intake import (
    RequirementsIntakeError,
    analyze_requirements_text,
    build_local_preparse_payload,
    build_logic_drawing,
    build_streamed_logic_authoring_session,
    interpret_logic_change,
    prepare_fault_injection,
    prepare_fault_injection_sandbox_plan,
    resolve_provider_metadata,
    update_logic_drawing,
)
from well_harness.requirements_intake.analysis import _analysis_prompt
from well_harness.requirements_intake.analysis import THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET
from well_harness.requirements_intake.logic_builder import (
    THRUST_REVERSER_DEMO_CHAIN_CONTRACT,
    _build_l1_l4_circuit_view,
    _drawing_prompt,
    _normalize_logic_drawing,
    _payload_sha256,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_ROOT = REPO_ROOT / "src" / "well_harness" / "static"


class _FakeResponse:
    def __init__(self, body: bytes):
        self._buf = io.BytesIO(body)

    def read(self) -> bytes:
        return self._buf.getvalue()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _model_response(content: dict) -> str:
    return json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(content, ensure_ascii=False),
                    }
                }
            ]
        },
        ensure_ascii=False,
    )


def _ready_requirements_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "summary_zh": "L1 到 L4 反推逻辑已澄清。",
        "open_questions": [],
        "concept_logic_nodes": [
            {"id": "RA", "label": "无线电高度", "node_kind": "input", "description_zh": "RA<6ft"},
            {"id": "L1", "label": "逻辑1", "node_kind": "logic", "description_zh": "TLS解锁逻辑"},
        ],
        "concept_edges": [{"id": "e1", "source": "RA", "target": "L1", "label": "高度<6ft"}],
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _ready_reconstruction_payload() -> dict:
    payload = _ready_requirements_payload()
    payload["reconstruction_target"] = THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET
    payload["summary_zh"] = "按反推逻辑演示舱基准链路重构 L1-L4 电路。"
    payload["concept_logic_nodes"] = [
        {
            "id": node["id"],
            "label": node["label"],
            "node_kind": node["node_kind"],
            "description_zh": "反推演示舱基准节点。",
        }
        for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]
    ]
    payload["concept_edges"] = [
        {
            "id": edge["id"],
            "source": edge["source"],
            "target": edge["target"],
            "label": "demo cabin route",
            "endpoint_status": "resolved",
        }
        for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]
    ]
    return payload


def _l1_l4_requirements_payload_for_circuit() -> dict:
    anchor_logic = {
        "id": "B81",
        "kind": "正文条件",
        "origin": "docx_body",
        "quote_zh": "飞机离地小于6ft时，DIU发出TLS解锁指令。",
    }
    anchor_fault = {
        "id": "B91",
        "kind": "正文条件",
        "origin": "docx_body",
        "quote_zh": "故障注入目前暂时不考虑，很复杂。",
    }
    nodes = [
        {"id": "ra_lt_6ft", "label": "RA<6ft", "node_kind": "input", "source_anchors": [anchor_logic]},
        {"id": "sw1", "label": "SW1", "node_kind": "input", "source_anchors": [anchor_logic]},
        {"id": "sw2", "label": "SW2", "node_kind": "input", "source_anchors": [anchor_logic]},
        {"id": "tra_reverse_range", "label": "TRA反推区", "node_kind": "input", "source_anchors": [anchor_logic]},
        {"id": "logic1", "label": "L1", "node_kind": "logic", "source_anchors": [anchor_logic]},
        {"id": "tls_cmd", "label": "TLS 115VAC", "node_kind": "output", "source_anchors": [anchor_logic]},
        {"id": "logic2", "label": "L2", "node_kind": "logic", "source_anchors": [anchor_logic]},
        {"id": "etrac_cmd", "label": "ETRAC 540VDC", "node_kind": "output", "source_anchors": [anchor_logic]},
        {"id": "logic3", "label": "L3", "node_kind": "logic", "source_anchors": [anchor_logic]},
        {"id": "pls_pdu_cmd", "label": "PLS/PDU", "node_kind": "output", "source_anchors": [anchor_logic]},
        {"id": "vdt_90", "label": "VDT 90%", "node_kind": "component", "source_anchors": [anchor_logic]},
        {"id": "logic4", "label": "L4", "node_kind": "logic", "source_anchors": [anchor_logic]},
        {"id": "thr_lock_release", "label": "THR_LOCK release", "node_kind": "output", "source_anchors": [anchor_logic]},
    ]
    edges = [
        {"id": "e_ra_l1", "source": "ra_lt_6ft", "target": "logic1", "label": "高度门限", "source_anchors": [anchor_logic]},
        {"id": "e_sw1_l1", "source": "sw1", "target": "logic1", "label": "SW1 条件", "source_anchors": [anchor_logic]},
        {"id": "e_l1_tls", "source": "logic1", "target": "tls_cmd", "label": "TLS 输出", "source_anchors": [anchor_logic]},
        {"id": "e_sw2_l2", "source": "sw2", "target": "logic2", "label": "SW2 条件", "source_anchors": [anchor_logic]},
        {"id": "e_l2_etrac", "source": "logic2", "target": "etrac_cmd", "label": "ETRAC 输出", "source_anchors": [anchor_logic]},
        {"id": "e_tls_l3", "source": "tls_cmd", "target": "logic3", "label": "TLS 反馈", "source_anchors": [anchor_logic]},
        {"id": "e_l2_l3", "source": "logic2", "target": "logic3", "label": "执行链汇合", "source_anchors": [anchor_logic]},
        {"id": "e_l3_pls", "source": "logic3", "target": "pls_pdu_cmd", "label": "PLS/PDU 输出", "source_anchors": [anchor_logic]},
        {"id": "e_pls_vdt", "source": "pls_pdu_cmd", "target": "vdt_90", "label": "展开反馈", "source_anchors": [anchor_logic]},
        {"id": "e_vdt_l4", "source": "vdt_90", "target": "logic4", "label": "90% 反馈", "source_anchors": [anchor_logic]},
        {"id": "e_tra_l4", "source": "tra_reverse_range", "target": "logic4", "label": "TRA 门限", "source_anchors": [anchor_logic]},
        {"id": "e_l4_lock", "source": "logic4", "target": "thr_lock_release", "label": "释放", "source_anchors": [anchor_logic]},
    ]
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "summary_zh": "本地预解析已收敛出 L1-L4 反推链路。",
        "open_questions": [],
        "concept_logic_nodes": nodes,
        "concept_edges": edges,
        "requirement_groups": [
            {"id": "logic1", "label": "L1", "node_ids": ["ra_lt_6ft", "sw1", "logic1", "tls_cmd"], "source_anchors": [anchor_logic]},
            {"id": "logic2", "label": "L2", "node_ids": ["sw2", "logic2", "etrac_cmd"], "source_anchors": [anchor_logic]},
            {"id": "logic3", "label": "L3", "node_ids": ["tls_cmd", "logic2", "logic3", "pls_pdu_cmd"], "source_anchors": [anchor_logic]},
            {"id": "logic4", "label": "L4", "node_ids": ["vdt_90", "tra_reverse_range", "logic4", "thr_lock_release"], "source_anchors": [anchor_logic]},
        ],
        "source_scope": {
            "fault_injection": {
                "status": "source_deferred",
                "reason_zh": "源文档声明故障注入本轮暂不考虑。",
                "source_anchors": [anchor_fault],
            }
        },
        "deterministic_preparse": {
            "available": True,
            "applied": True,
            "reason": "model_output_empty",
            "strategy": "docx_l1_l4_rule_preparse",
        },
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _ready_drawing_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": "abc123",
        "summary_zh": "模型已绘制 L1 链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "RA",
                "label": "无线电高度",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 180,
                "height": 96,
                "description_zh": "RA<6ft",
            },
            {
                "id": "L1",
                "label": "逻辑1",
                "node_kind": "logic",
                "x": 420,
                "y": 120,
                "width": 190,
                "height": 104,
                "description_zh": "TLS解锁",
            },
        ],
        "edges": [
            {
                "id": "edge_ra_l1",
                "source": "RA",
                "target": "L1",
                "label": "高度<6ft",
                "route": [{"x": 260, "y": 168}, {"x": 420, "y": 168}],
            }
        ],
        "parameter_panels": [
            {
                "id": "panel_ra",
                "node_id": "RA",
                "label": "RA阈值",
                "unit": "ft",
                "min": 0,
                "max": 20,
                "default": 6,
                "x": 276,
                "y": 120,
                "width": 150,
                "height": 76,
            }
        ],
        "drawing_notes": ["输入在左，逻辑在中。"],
    }


def _streamed_decision(
    session: dict,
    proposal: dict,
    decision: str = "confirm",
    **overrides,
) -> dict:
    payload = {
        "proposal_id": proposal["id"],
        "target_type": proposal["target_type"],
        "target_id": proposal["target_id"],
        "decision": decision,
        "source_requirements_sha256": session["source_requirements_sha256"],
        "source_drawing_sha256": session["source_drawing_sha256"],
    }
    payload.update(overrides)
    return payload


def _ready_fault_preparation_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_fault_injection_preparation_v1.schema.json",
        "kind": "ai-fantui-fault-injection-preparation",
        "version": 1,
        "status": "needs_user_confirmation",
        "truth_effect": "none",
        "candidate_state": "fault_injection_preparation",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": "req123",
        "source_drawing_sha256": "draw123",
        "summary_zh": "故障注入准备完成。",
        "assumptions": ["只生成候选，不执行仿真。"],
        "fault_scenarios": [
            {
                "id": "fault_ra_stuck_low",
                "label": "RA 卡滞低值",
                "node_id": "RA",
                "fault_type": "sensor_stuck_low",
                "rationale_zh": "RA 是 L1 关键输入。",
                "expected_effect_zh": "可能提前满足高度门限。",
                "observable_signals": ["RA", "L1"],
                "severity": "medium",
            }
        ],
        "injection_points": [
            {
                "id": "point_ra",
                "node_id": "RA",
                "parameter_panel_id": "panel_ra",
                "signal_name": "RA",
                "injection_mode": "override_value",
                "safe_boundary_zh": "仅作为沙盒候选，不写入控制器。",
            }
        ],
        "boundary_questions": [
            {
                "id": "boundary_ra_range",
                "prompt_zh": "RA 故障候选的取值边界是否限制在 0-20ft？",
                "rationale_zh": "边界会影响后续沙盒注入范围。",
                "blocks": "fault_injection",
            }
        ],
        "boundary_answers": [
            {
                "id": "boundary_ra_range",
                "prompt_zh": "RA 故障候选的取值边界是否限制在 0-20ft？",
                "answer_zh": "限制在 0-20ft，只用于沙盒。",
            }
        ],
        "workflow_notes": ["下一步需要工程师确认边界后再进入沙盒故障注入。"],
    }


@pytest.fixture(autouse=True)
def _scrub_llm_env(monkeypatch):
    for name in (
        "DEEPSEEK_API_KEY",
        "DeepSeek_API_key",
        "DEEPSEEK_API_BASE",
        "DEEPSEEK_MODEL",
        "MINIMAX_API_KEY",
        "Minimax_API_key",
        "MINIMAX_API_BASE",
        "MINIMAX_MODEL",
        "REQUIREMENTS_INTAKE_LLM_TIMEOUT_SECONDS",
        "REQUIREMENTS_INTAKE_LLM_MAX_TOKENS",
    ):
        monkeypatch.delenv(name, raising=False)


def test_deepseek_metadata_prefers_uppercase_env(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "  sk-do-not-print  ")
    monkeypatch.setenv("DeepSeek_API_key", "sk-fallback")

    meta = resolve_provider_metadata("deepseek")

    assert meta == {
        "provider": "deepseek",
        "model": "deepseek-v4-pro",
        "api_base": "https://api.deepseek.com",
        "key_source": "env:DEEPSEEK_API_KEY",
    }
    assert "sk-" not in json.dumps(meta)


def test_demo_server_provider_status_reports_deepseek_key_without_leaking_secret(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-live-secret")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-v4-pro")

    server, thread = _start_server()
    try:
        status, payload = _get(server, "/api/requirements-intake/provider-status?provider=deepseek")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload == {
        "provider": "deepseek",
        "model": "deepseek-v4-pro",
        "api_base": "https://api.deepseek.com",
        "key_available": True,
        "key_source": "env:DEEPSEEK_API_KEY",
        "live_ready": True,
    }
    assert "sk-live-secret" not in json.dumps(payload)


def test_missing_deepseek_key_is_deterministic_and_redacted():
    with pytest.raises(RequirementsIntakeError) as exc:
        analyze_requirements_text("RA 小于 6ft 时允许进入逻辑链路。", provider="deepseek")

    payload = exc.value.to_payload()
    assert exc.value.status_code == 503
    assert payload["error"] == "missing_api_key"
    assert payload["details"]["checked"] == ["DEEPSEEK_API_KEY", "DeepSeek_API_key"]
    assert "sk-" not in json.dumps(payload)


def test_analyze_requirements_text_calls_deepseek_with_concept_only_contract(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["url"] = url
        captured["headers"] = dict(headers)
        captured["body"] = json.loads(body.decode("utf-8"))
        captured["timeout"] = timeout
        return _model_response(
            {
                "summary_zh": "需求描述了 RA 输入、SW1 门限和放行逻辑，但故障范围还需确认。",
                "document_assumptions": ["RA 单位按 ft 处理。"],
                "open_questions": [
                    {
                        "id": "fault_scope",
                        "prompt_zh": "是否需要考虑 RA 传感器卡滞？",
                        "rationale_zh": "故障注入模块需要明确故障类型。",
                        "blocks": "fault_injection",
                    }
                ],
                "concept_logic_nodes": [
                    {
                        "id": "node_ra",
                        "label": "RA",
                        "node_kind": "input",
                        "description_zh": "无线电高度输入。",
                        "parameters": [
                            {
                                "id": "ra_threshold_ft",
                                "label": "RA 阈值",
                                "unit": "ft",
                                "min": 0,
                                "max": 50,
                                "default": 6,
                                "source_hint": "原文：RA < 6ft",
                            }
                        ],
                    },
                    {
                        "id": "node_logic1",
                        "label": "L1",
                        "node_kind": "logic",
                        "description_zh": "RA 与 SW1 的组合判断。",
                    },
                ],
                "concept_edges": [
                    {"id": "edge_ra_l1", "source": "node_ra", "target": "node_logic1", "label": "RA gate"}
                ],
                "ready_for_logic_builder": False,
            }
        )

    result = analyze_requirements_text(
        "当 RA 小于 6ft 且 SW1 有效时，L1 可以进入下一逻辑。",
        document_name="sample.md",
        provider="deepseek",
        request_post=fake_post,
    )

    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["headers"]["Authorization"] == "Bearer sk-test-secret"
    assert captured["body"]["model"] == "deepseek-v4-pro"
    assert captured["body"]["response_format"] == {"type": "json_object"}
    assert captured["body"]["thinking"] == {"type": "disabled"}
    assert captured["body"]["max_tokens"] == 2048
    assert captured["timeout"] == 180.0
    assert result["kind"] == "ai-fantui-requirements-intake-analysis"
    assert result["status"] == "needs_clarification"
    assert result["truth_effect"] == "none"
    assert result["candidate_state"] == "concept_only"
    assert result["certification_claim"] == "none"
    assert result["controller_truth_modified"] is False
    assert result["source_document"]["name"] == "sample.md"
    assert result["source_document"]["text_chars"] > 0
    assert result["source_document"]["sha256"]
    assert result["analysis_input"]["compacted"] is False
    assert result["llm"]["provider"] == "deepseek"
    assert result["llm"]["key_source"] == "env:DEEPSEEK_API_KEY"
    assert "sk-test-secret" not in json.dumps(result, ensure_ascii=False)
    assert result["concept_logic_nodes"][0]["parameters"][0]["id"] == "ra_threshold_ft"
    assert result["concept_edges"][0]["endpoint_status"] == "resolved"


def test_llm_post_has_wall_clock_timeout(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    monkeypatch.setenv("REQUIREMENTS_INTAKE_LLM_TIMEOUT_SECONDS", "0.1")

    def hanging_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        assert timeout == 0.1
        time.sleep(2.0)
        return _model_response({"summary_zh": "too late"})

    start = time.monotonic()
    with pytest.raises(RequirementsIntakeError) as exc:
        analyze_requirements_text("RA 小于 6ft 时进入逻辑。", provider="deepseek", request_post=hanging_post)

    elapsed = time.monotonic() - start
    assert elapsed < 0.8
    assert exc.value.status_code == 502
    assert exc.value.code == "llm_timeout"
    assert exc.value.details == {"provider": "deepseek", "timeout_sec": 0.1}


def test_analysis_prompt_preserves_clarified_signal_anchors():
    messages = _analysis_prompt(
        (
            "反推控制逻辑。\n"
            "[工程师澄清回答]\n"
            "回答：L1 输出 tls_115vac_cmd；L2 输出 etrac_540vdc_cmd；"
            "L3 输出 eec_deploy_cmd、pls_power_cmd、pdu_motor_cmd；"
            "L4 由 deploy_90_percent_vdt 触发并输出 thr_lock_release。"
        ),
        "logic.docx",
        {"input_chars": 180, "original_chars": 180, "compacted": False, "strategy": "full_text"},
    )

    user_prompt = messages[1]["content"]

    assert "concept_logic_nodes 最多24个" in user_prompt
    assert "英文信号名" in user_prompt
    assert "*_cmd" in user_prompt
    assert "每个工作逻辑的直接输出必须单独建 output 节点" in user_prompt
    assert "不得把不同逻辑的输出合并到同一个节点" in user_prompt


def test_analysis_prompt_can_request_demo_cabin_reconstruction_target():
    messages = _analysis_prompt(
        "请一模一样重构反推逻辑演示舱链路。",
        "demo-reconstruction.md",
        {"input_chars": 32, "original_chars": 32, "compacted": False, "strategy": "full_text"},
    )

    user_prompt = messages[1]["content"]

    assert "可选字段：reconstruction_target" in user_prompt
    assert THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET in user_prompt
    assert "一模一样重构反推逻辑演示舱" in user_prompt


def test_model_response_preserves_demo_cabin_reconstruction_target(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        return _model_response(
            {
                "summary_zh": "反推演示舱重构目标已识别。",
                "document_assumptions": [],
                "open_questions": [],
                "reconstruction_target": THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET,
                "concept_logic_nodes": [
                    {"id": "sw1", "label": "SW1", "node_kind": "input"},
                    {"id": "logic1", "label": "L1", "node_kind": "logic"},
                ],
                "concept_edges": [{"id": "wire_sw1_logic1", "source": "sw1", "target": "logic1", "label": "feeds"}],
                "ready_for_logic_builder": True,
            }
        )

    result = analyze_requirements_text(
        "请一模一样重构反推逻辑演示舱链路。",
        provider="deepseek",
        request_post=fake_post,
    )

    assert result["status"] == "ready_for_logic_builder"
    assert result["reconstruction_target"] == THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET


def test_drawing_prompt_preserves_requirement_nodes_and_edges():
    messages = _drawing_prompt(
        {
            "status": "ready_for_logic_builder",
            "summary_zh": "L1-L4 已澄清。",
            "concept_logic_nodes": [
                {"id": "logic1", "label": "工作逻辑1", "node_kind": "logic"},
                {"id": "tls_115vac_cmd", "label": "TLS命令", "node_kind": "output"},
                {"id": "thr_lock_release", "label": "电子锁释放", "node_kind": "output"},
            ],
            "concept_edges": [
                {"id": "e_l1_tls", "source": "logic1", "target": "tls_115vac_cmd", "label": "输出"},
                {"id": "e_l4_lock", "source": "logic4", "target": "thr_lock_release", "label": "释放"},
            ],
            "open_questions": [],
            "ready_for_logic_builder": True,
        }
    )

    user_prompt = messages[1]["content"]

    assert "nodes: 8-24 个" in user_prompt
    assert "必须覆盖已澄清需求 JSON 中 concept_logic_nodes 的所有 id" in user_prompt
    assert "必须覆盖 concept_edges 的主要逻辑关系" in user_prompt
    assert "不得省略已澄清输出节点" in user_prompt


def test_drawing_prompt_includes_exact_demo_cabin_contract():
    messages = _drawing_prompt(_ready_reconstruction_payload())

    user_prompt = messages[1]["content"]

    assert "[反推逻辑演示舱一比一重构目标]" in user_prompt
    assert "src/well_harness/static/demo.html#fan-chain-svg" in user_prompt
    assert "parameter_panels 必须返回 []" in user_prompt
    assert THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET in user_prompt
    assert '"id": "sw1"' in user_prompt
    assert '"id": "logic4"' in user_prompt
    assert '"id": "wire_logic4_thr_lock"' in user_prompt
    assert '"source": "pdu_motor", "target": "vdt90"' in user_prompt


def test_reconstruction_target_rejects_missing_demo_cabin_node():
    payload = _ready_reconstruction_payload()
    broken_drawing = {
        "summary_zh": "遗漏了 THR_LOCK。",
        "canvas": {"width": 900, "height": 400},
        "nodes": [node for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"] if node["id"] != "thr_lock"],
        "edges": [
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["id"],
                "route": edge["route"],
            }
            for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]
            if edge["target"] != "thr_lock"
        ],
        "parameter_panels": [],
        "drawing_notes": [],
    }

    with pytest.raises(RequirementsIntakeError) as exc:
        _normalize_logic_drawing(json.dumps(broken_drawing, ensure_ascii=False), payload)

    assert exc.value.code == "logic_drawing_json_error"
    assert exc.value.details["reconstruction_target"] == THRUST_REVERSER_DEMO_RECONSTRUCTION_TARGET
    assert exc.value.details["missing_reference_nodes"] == ["thr_lock"]


def test_reconstruction_target_accepts_exact_demo_cabin_geometry_and_routes():
    payload = _ready_reconstruction_payload()
    exact_drawing = {
        "summary_zh": "已复刻反推演示舱链路。",
        "canvas": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["canvas"],
        "nodes": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"],
        "edges": [
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["id"],
                "route": edge["route"],
            }
            for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]
        ],
        "parameter_panels": [],
        "drawing_notes": ["按 demo.html#fan-chain-svg 复刻。"],
    }

    result = _normalize_logic_drawing(json.dumps(exact_drawing, ensure_ascii=False), payload)

    assert result["canvas"] == {"width": 900.0, "height": 400.0}
    assert len(result["nodes"]) == len(THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"])
    assert len(result["edges"]) == len(THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"])
    assert result["parameter_panels"] == []


def test_reconstruction_target_uses_demo_contract_when_intake_ids_are_generic():
    payload = _ready_reconstruction_payload()
    payload["concept_logic_nodes"] = [
        {"id": f"n{index}", "label": f"节点{index}", "node_kind": "logic", "description_zh": "模型泛化命名。"}
        for index in range(1, 21)
    ]
    payload["concept_edges"] = [
        {"id": f"e{index}", "source": f"n{index}", "target": f"n{index + 1}", "label": "模型泛化连线"}
        for index in range(1, 20)
    ]
    exact_drawing = {
        "summary_zh": "已复刻反推演示舱链路。",
        "canvas": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["canvas"],
        "nodes": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"],
        "edges": [
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["id"],
                "route": edge["route"],
            }
            for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]
        ],
        "parameter_panels": [],
        "drawing_notes": ["按 demo.html#fan-chain-svg 复刻。"],
    }

    result = _normalize_logic_drawing(json.dumps(exact_drawing, ensure_ascii=False), payload)

    assert result["canvas"] == {"width": 900.0, "height": 400.0}
    assert {node["id"] for node in result["nodes"]} == {
        node["id"] for node in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"]
    }


def test_reconstruction_target_rejects_shifted_demo_cabin_route():
    payload = _ready_reconstruction_payload()
    shifted_edges = []
    for edge in THRUST_REVERSER_DEMO_CHAIN_CONTRACT["edges"]:
        route = [dict(point) for point in edge["route"]]
        if edge["id"] == "wire_logic4_thr_lock":
            route[0]["x"] += 12
        shifted_edges.append(
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["id"],
                "route": route,
            }
        )
    shifted_drawing = {
        "summary_zh": "拓扑正确但路径偏移。",
        "canvas": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["canvas"],
        "nodes": THRUST_REVERSER_DEMO_CHAIN_CONTRACT["nodes"],
        "edges": shifted_edges,
        "parameter_panels": [],
        "drawing_notes": [],
    }

    with pytest.raises(RequirementsIntakeError) as exc:
        _normalize_logic_drawing(json.dumps(shifted_drawing, ensure_ascii=False), payload)

    assert exc.value.details["route_mismatches"] == ["wire_logic4_thr_lock.route[0]"]


def test_minimax_provider_is_supported_when_selected(monkeypatch):
    monkeypatch.setenv("Minimax_API_key", "sk-minimax-secret")
    captured: dict[str, object] = {}

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["url"] = url
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "summary_zh": "可进入逻辑构建。",
                "open_questions": [],
                "concept_logic_nodes": [{"id": "input_a", "label": "A", "node_kind": "input"}],
                "concept_edges": [],
                "ready_for_logic_builder": True,
            }
        )

    result = analyze_requirements_text("A 信号为真时输出允许。", provider="minimax", request_post=fake_post)

    assert captured["url"] == "https://api.minimaxi.com/v1/chat/completions"
    assert captured["body"]["model"] == "MiniMax-M2.7-highspeed"
    assert result["llm"]["provider"] == "minimax"
    assert result["ready_for_logic_builder"] is True


def test_model_response_embedded_json_is_recovered(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        content = (
            "下面是提取结果：\n"
            "```json\n"
            "{\n"
            '  "summary_zh": "模型多说了一句话但 JSON 仍可恢复。",\n'
            '  "open_questions": [],\n'
            '  "concept_logic_nodes": [{"id": "node_a", "label": "A", "node_kind": "input"}],\n'
            '  "concept_edges": [],\n'
            '  "ready_for_logic_builder": true\n'
            "}\n"
            "```"
        )
        return json.dumps({"choices": [{"message": {"content": content}}]}, ensure_ascii=False)

    result = analyze_requirements_text("A 信号为真时输出允许。", provider="deepseek", request_post=fake_post)

    assert result["summary_zh"] == "模型多说了一句话但 JSON 仍可恢复。"
    assert result["status"] == "ready_for_logic_builder"


def test_empty_model_output_gets_actionable_fallback_questions(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        return _model_response(
            {
                "summary_zh": "",
                "open_questions": [],
                "concept_logic_nodes": [],
                "concept_edges": [],
                "ready_for_logic_builder": False,
            }
        )

    result = analyze_requirements_text("控制逻辑文档正文。", provider="deepseek", request_post=fake_post)

    assert result["status"] == "needs_clarification"
    assert result["ready_for_logic_builder"] is False
    assert len(result["open_questions"]) >= 2
    assert {q["id"] for q in result["open_questions"]} >= {
        "clarify_control_goal",
        "clarify_io_signals",
    }
    assert "控制的对象" in result["open_questions"][0]["prompt_zh"]


def test_docx_l1_l4_preparse_recovers_empty_model_output(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        user_prompt = request["messages"][1]["content"]
        assert "deterministic_preparse" in user_prompt
        assert "docx_l1_l4_rule_preparse" in user_prompt
        return _model_response(
            {
                "summary_zh": "",
                "open_questions": [],
                "concept_logic_nodes": [],
                "concept_edges": [],
                "ready_for_logic_builder": False,
            }
        )

    docx_text = "\n".join(
        [
            "工作逻辑1 L1：当 RA<6ft 且 SW1 进入 TRA [-1.4,-6.2] 区间，输出 TLS 115VAC。",
            "工作逻辑2 L2：当 SW2 有效且 TRA 区间满足时，输出 ETRAC 540VDC。",
            "工作逻辑3 L3：TLS/PLS 反馈满足后，驱动 PDU motor 并等待 VDT。",
            "工作逻辑4 L4：当 VDT 达到 90% deploy 且 TRA<=-11.74°，THR_LOCK release。",
            "故障注入目前暂时不考虑，很复杂。",
        ]
    )

    result = analyze_requirements_text(docx_text, document_name="logic.docx", provider="deepseek", request_post=fake_post)

    assert result["status"] == "ready_for_logic_builder"
    assert result["ready_for_logic_builder"] is True
    assert result["open_questions"] == []
    assert result["deterministic_preparse"]["applied"] is True
    assert result["deterministic_preparse"]["reason"] == "model_output_empty"
    assert {item["id"] for item in result["concept_logic_nodes"]} >= {
        "logic1",
        "logic2",
        "logic3",
        "logic4",
        "ra_lt_6ft",
        "thr_lock_release",
    }
    assert len(result["concept_edges"]) >= 12
    assert result["concept_logic_nodes"][0]["source_anchors"][0]["id"] == "B01"
    assert result["source_scope"]["fault_injection"]["status"] == "source_deferred"
    assert "故障注入按源文档暂缓" in result["reading_burden"]["key_outputs_zh"]


def test_local_preparse_attaches_requirement_analyst_agent_output_contract():
    docx_text = "\n".join(
        [
            "工作逻辑1 L1：当 RA<6ft 且 SW1 进入 TRA [-1.4,-6.2] 区间，输出 TLS 115VAC。",
            "工作逻辑2 L2：当 SW2 有效且 TRA 区间满足时，输出 ETRAC 540VDC。",
            "工作逻辑3 L3：TLS/PLS 反馈满足后，驱动 PDU motor 并等待 VDT。",
            "工作逻辑4 L4：当 VDT 达到 90% deploy 且 TRA<=-11.74°，THR_LOCK release。",
        ]
    )

    result = build_local_preparse_payload(docx_text, document_name="logic.docx")

    packet = result["agent_output_contract_v0_1"]["requirement_analyst"]
    validate_agent_output_contract(packet)
    agent_output = packet["agent_output"]
    assert agent_output["agent_name"] == "RequirementAnalystAgent"
    assert agent_output["boundary"] == {
        "candidate_state": "requirements_candidate",
        "truth_effect": "none",
        "controller_truth_modified": False,
        "certification_claim": "none",
    }
    assert agent_output["validation"]["schema_valid"] is True
    assert agent_output["payload"]["ready_for_logic_builder"] is True
    assert agent_output["payload"]["requirement_counts"]["concept_nodes"] >= 12
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False


def test_upstream_http_error_details_are_redacted(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        error_body = json.dumps(
            {
                "error": {
                    "message": "context length exceeded for sk-should-not-leak",
                    "type": "invalid_request_error",
                }
            }
        ).encode("utf-8")
        raise urllib.error.HTTPError(url, 400, "Bad Request", {}, io.BytesIO(error_body))

    with pytest.raises(RequirementsIntakeError) as exc:
        analyze_requirements_text("A" * 100, provider="deepseek", request_post=fake_post)

    payload = exc.value.to_payload()
    assert exc.value.status_code == 502
    assert payload["error"] == "llm_http_error"
    assert payload["details"]["upstream_status"] == 400
    assert payload["details"]["upstream_error_type"] == "invalid_request_error"
    assert "context length exceeded" in payload["details"]["upstream_message"]
    assert "sk-" not in json.dumps(payload)


def test_long_document_is_compacted_before_llm_call(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "summary_zh": "长文档已通过压缩输入分析。",
                "open_questions": [{"id": "coverage", "prompt_zh": "未抽取章节是否包含额外逻辑？"}],
                "concept_logic_nodes": [{"id": "node_ra", "label": "RA", "node_kind": "input"}],
                "concept_edges": [],
                "ready_for_logic_builder": False,
            }
        )

    long_text = (
        "项目背景说明。\n" * 3000
        + "REQ-1 当 RA 小于 6ft 且 SW1 有效时，L1 可以进入下一逻辑。\n"
        + "REQ-2 如果 TRA 进入反推区，应释放油门锁命令。\n"
        + "附录说明。\n" * 3000
    )
    result = analyze_requirements_text(long_text, provider="deepseek", request_post=fake_post)

    user_message = captured["body"]["messages"][1]["content"]
    assert len(user_message) < len(long_text)
    assert "[COMPACTION_NOTICE]" in user_message
    assert "REQ-1 当 RA 小于 6ft" in user_message
    assert result["analysis_input"]["compacted"] is True
    assert result["analysis_input"]["strategy"] == "head_requirement_lines_tail"
    assert result["status"] == "needs_clarification"


def test_build_logic_drawing_calls_model_for_layout(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["url"] = url
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "summary_zh": "模型已绘制 L1 链路。",
                "canvas": {"width": 1280, "height": 760},
                "nodes": [
                    {
                        "id": "RA",
                        "label": "无线电高度",
                        "node_kind": "input",
                        "x": 80,
                        "y": 120,
                        "width": 180,
                        "height": 96,
                        "description_zh": "RA<6ft",
                    },
                    {
                        "id": "L1",
                        "label": "逻辑1",
                        "node_kind": "logic",
                        "x": 420,
                        "y": 120,
                        "width": 190,
                        "height": 104,
                        "description_zh": "TLS解锁",
                    },
                ],
                "edges": [
                    {
                        "id": "edge_ra_l1",
                        "source": "RA",
                        "target": "L1",
                        "label": "高度<6ft",
                        "route": [{"x": 260, "y": 168}, {"x": 420, "y": 168}],
                    }
                ],
                "parameter_panels": [
                    {
                        "id": "panel_ra",
                        "node_id": "RA",
                        "label": "RA阈值",
                        "unit": "ft",
                        "min": 0,
                        "max": 20,
                        "default": 6,
                        "x": 90,
                        "y": 226,
                        "width": 150,
                        "height": 68,
                    }
                ],
                "drawing_notes": ["输入在左，逻辑在中。"],
            }
        )

    result = build_logic_drawing(_ready_requirements_payload(), provider="deepseek", request_post=fake_post)

    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    prompt = captured["body"]["messages"][1]["content"]
    assert "前端只会按你输出的 JSON 坐标和路径渲染" in captured["body"]["messages"][0]["content"]
    assert "parameter_panels" in prompt
    assert captured["body"]["max_tokens"] == 8192
    assert result["kind"] == "ai-fantui-logic-link-drawing"
    assert result["status"] == "draft_ready"
    assert result["llm"]["provider"] == "deepseek"
    assert result["nodes"][0]["x"] == 80.0
    assert result["edges"][0]["route"] == [{"x": 260.0, "y": 168.0}, {"x": 420.0, "y": 168.0}]
    assert result["parameter_panels"][0]["node_id"] == "RA"
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False


def test_l1_l4_circuit_view_uses_control_board_geometry_and_source_scope():
    payload = _l1_l4_requirements_payload_for_circuit()

    circuit = _build_l1_l4_circuit_view(payload)

    assert circuit["kind"] == "ai-fantui-l1-l4-circuit-view"
    assert circuit["layout"] == "deterministic_l1_l4_circuit_v1"
    assert circuit["canvas"] == {"width": 900, "height": 400}
    assert [row["id"] for row in circuit["rows"]] == ["logic1", "logic2", "logic3", "logic4"]
    assert all(row["gate"]["gate_type"] == "AND" for row in circuit["rows"])
    assert circuit["source_scope"]["fault_injection"]["status"] == "source_deferred"
    assert len(circuit["nodes"]) == 20
    assert len(circuit["wires"]) == 23
    assert {node["id"] for node in circuit["nodes"]} >= {
        "logic1",
        "logic2",
        "logic3",
        "logic4",
        "radio_altitude_ft",
        "aircraft_on_ground",
        "engine_running",
        "tls115",
        "tls_unlocked",
        "vdt90",
        "thr_lock",
    }
    assert any(wire["source"] == "logic4" and wire["target"] == "thr_lock" for wire in circuit["wires"])
    assert any(node["source_anchors"] for node in circuit["nodes"] if node["id"] == "logic4")
    assert any(node["provenance"] == "demo_cabin_context" for node in circuit["nodes"] if node["id"] == "engine_running")
    assert circuit["badges"] == [
        {
            "id": "fault_injection_deferred",
            "label_zh": "故障注入暂缓",
            "source_anchor_ids": ["B91"],
        }
    ]


def test_l1_l4_circuit_view_backfills_docx_anchors_from_edges_and_groups():
    payload = _l1_l4_requirements_payload_for_circuit()
    anchors = {
        "ra": {
            "id": "B37",
            "kind": "正文条件",
            "origin": "docx_body",
            "quote_zh": "飞机离地小于6ft时，DIU发出TLS解锁指令。",
        },
        "sw1": {
            "id": "B39",
            "kind": "正文条件",
            "origin": "docx_body",
            "quote_zh": "微动开关1在油门杆角度[-1.4°, -6.2°]区间内触发。",
        },
        "sw2": {
            "id": "B41",
            "kind": "正文条件",
            "origin": "docx_body",
            "quote_zh": "微动开关2在油门杆角度[-5°, -9.8°]区间内触发。",
        },
        "tra": {
            "id": "B43",
            "kind": "正文条件",
            "origin": "docx_body",
            "quote_zh": "油门杆解析角度≤-11.74°信号。",
        },
        "vdt": {
            "id": "B45",
            "kind": "正文条件",
            "origin": "docx_body",
            "quote_zh": "反推完全展开信号与位移传感器（VDT）达到90%。",
        },
    }
    nodes_by_id = {node["id"]: node for node in payload["concept_logic_nodes"]}
    nodes_by_id["ra_lt_6ft"]["source_anchors"] = []
    nodes_by_id["sw1"]["source_anchors"] = [anchors["sw1"]]
    nodes_by_id["sw2"]["source_anchors"] = []
    nodes_by_id["tra_reverse_range"]["source_anchors"] = [anchors["tra"]]
    nodes_by_id["vdt_90"]["source_anchors"] = []
    nodes_by_id["thr_lock_release"]["source_anchors"] = []
    groups_by_id = {group["id"]: group for group in payload["requirement_groups"]}
    groups_by_id["logic1"]["source_anchors"] = [anchors["ra"], anchors["sw1"]]
    groups_by_id["logic2"]["source_anchors"] = [anchors["sw2"]]
    groups_by_id["logic3"]["source_anchors"] = [anchors["tra"]]
    groups_by_id["logic4"]["source_anchors"] = [anchors["vdt"], anchors["tra"]]
    edges_by_id = {edge["id"]: edge for edge in payload["concept_edges"]}
    edges_by_id["e_ra_l1"]["source_anchors"] = [anchors["ra"]]
    edges_by_id["e_sw2_l2"]["source_anchors"] = [anchors["sw2"]]
    edges_by_id["e_vdt_l4"]["source_anchors"] = [anchors["vdt"]]
    edges_by_id["e_tra_l4"]["source_anchors"] = [anchors["tra"]]
    edges_by_id["e_l4_lock"]["source_anchors"] = [anchors["vdt"]]

    circuit = _build_l1_l4_circuit_view(payload)

    circuit_nodes = {node["id"]: node for node in circuit["nodes"]}
    circuit_wires = {(wire["source"], wire["target"]): wire for wire in circuit["wires"]}
    assert "B37" in circuit_nodes["radio_altitude_ft"]["source_anchor_ids"]
    assert "B39" in circuit_nodes["sw1"]["source_anchor_ids"]
    assert "B41" in circuit_nodes["sw2"]["source_anchor_ids"]
    assert "B45" in circuit_nodes["vdt90"]["source_anchor_ids"]
    assert "B45" in circuit_nodes["thr_lock"]["source_anchor_ids"]
    assert "B43" in circuit_wires[("logic3", "logic4")]["source_anchor_ids"]
    assert "B45" in circuit_wires[("vdt90", "logic4")]["source_anchor_ids"]
    assert circuit_nodes["radio_altitude_ft"]["provenance"] == "docx_body"
    assert circuit_nodes["sw2"]["provenance"] == "docx_body"


def test_build_logic_drawing_attaches_circuit_view_for_l1_l4_preparse(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    requirements = _l1_l4_requirements_payload_for_circuit()

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        nodes = [
            {
                "id": node["id"],
                "label": node["label"],
                "node_kind": node["node_kind"],
                "x": 80 + (index % 4) * 260,
                "y": 80 + (index // 4) * 112,
                "width": 190,
                "height": 78,
                "description_zh": node.get("description_zh", ""),
            }
            for index, node in enumerate(requirements["concept_logic_nodes"])
        ]
        edges = [
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["label"],
                "route": [{"x": 240, "y": 120 + index * 12}, {"x": 420, "y": 120 + index * 12}],
            }
            for index, edge in enumerate(requirements["concept_edges"])
        ]
        return _model_response(
            {
                "summary_zh": "模型草图已生成，最终电路图由确定性渲染器接管。",
                "canvas": {"width": 1280, "height": 760},
                "nodes": nodes,
                "edges": edges,
                "parameter_panels": [],
                "drawing_notes": ["保留模型草图，同时生成确定性电路视图。"],
            }
        )

    result = build_logic_drawing(requirements, provider="deepseek", request_post=fake_post)

    assert result["status"] == "draft_ready"
    assert result["circuit_view"]["kind"] == "ai-fantui-l1-l4-circuit-view"
    assert result["circuit_view"]["source_requirements_sha256"] == result["source_requirements_sha256"]
    assert result["circuit_view"]["badges"][0]["label_zh"] == "故障注入暂缓"
    assert len(result["circuit_view"]["rows"]) == 4
    assert len(result["circuit_view"]["wires"]) >= 12


def test_logic_drawing_attaches_logic_ir_agent_contract_and_deterministic_reports():
    requirements = _l1_l4_requirements_payload_for_circuit()
    raw_drawing = {
        "summary_zh": "模型草图已生成。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": node["id"],
                "label": node["label"],
                "node_kind": node["node_kind"],
                "x": 80 + (index % 4) * 260,
                "y": 80 + (index // 4) * 112,
                "width": 190,
                "height": 78,
                "description_zh": node.get("description_zh", ""),
            }
            for index, node in enumerate(requirements["concept_logic_nodes"])
        ],
        "edges": [
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge["label"],
                "route": [{"x": 240, "y": 120 + index * 12}, {"x": 420, "y": 120 + index * 12}],
            }
            for index, edge in enumerate(requirements["concept_edges"])
        ],
        "parameter_panels": [],
        "drawing_notes": ["保留模型草图，同时生成确定性电路视图。"],
    }

    result = _normalize_logic_drawing(json.dumps(raw_drawing, ensure_ascii=False), requirements)

    contracts = result["agent_output_contract_v0_1"]
    logic_packet = contracts["logic_ir"]
    validate_agent_output_contract(logic_packet)
    assert logic_packet["agent_output"]["agent_name"] == "LogicIRAgent"
    assert logic_packet["agent_output"]["boundary"] == {
        "candidate_state": "logic_ir_candidate",
        "truth_effect": "none",
        "controller_truth_modified": False,
        "certification_claim": "none",
    }
    assert logic_packet["agent_output"]["payload"]["logic_ir"]["id"] == "REQ_INTAKE_LOGIC_DRAWING_CANDIDATE"

    safety_report = contracts["safety_guardian"]
    assert safety_report["agent_name"] == "SafetyGuardianAgent"
    assert safety_report["source_agent_name"] == "LogicIRAgent"
    assert safety_report["boundary"]["truth_effect"] == "none"

    evidence_report = contracts["evidence"]
    assert evidence_report["agent_name"] == "EvidenceAgent"
    assert evidence_report["source_agent_name"] == "LogicIRAgent"
    assert evidence_report["trace_matrix"]
    assert evidence_report["coverage"]["requirements"]["total"] >= 1
    task_package = result["chief_engineer_task_package_v0_1"]
    validate_agent_task_package(task_package)
    assert task_package["chief_engineer"]["agent_name"] == "ChiefEngineerAgent"
    assert task_package["chief_engineer"]["status"] == "no_tasks_required"
    assert task_package["tasks"] == []
    execution_plan = result["execution_plan_v0_1"]
    validate_execution_plan(execution_plan)
    assert execution_plan["planner"]["agent_name"] == "DeterministicExecutorAgent"
    assert execution_plan["planner"]["status"] == "no_task_available"
    assert execution_plan["dry_run_only"] is True
    assert execution_plan["execution_allowed"] is False
    execution_evidence = result["execution_evidence_package_v0_1"]
    validate_execution_evidence_package(execution_evidence)
    assert execution_evidence["executor"]["agent_name"] == "ApprovedTaskExecutionShell"
    assert execution_evidence["executor"]["status"] == "no_task_available"
    assert execution_evidence["approval"]["status"] == "missing"
    assert execution_evidence["execution_boundary"]["restricted_execution_performed"] is False
    assert execution_evidence["execution_boundary"]["controller_truth_modified"] is False
    review_packet = result["candidate_review_packet_v0_1"]
    validate_candidate_review_packet(review_packet)
    assert review_packet["reviewer"]["agent_name"] == "CandidateReviewPacketAgent"
    assert review_packet["reviewer"]["status"] == "no_findings"
    assert review_packet["source_artifacts"]["task_package_status"] == "no_tasks_required"
    assert review_packet["source_artifacts"]["execution_plan_status"] == "no_task_available"
    assert review_packet["source_artifacts"]["execution_evidence_status"] == "no_task_available"
    assert review_packet["finding_chains"] == []
    assert review_packet["summary"]["open_findings"] == []
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False


def test_build_logic_drawing_rejects_edges_without_model_route(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        return _model_response(
            {
                "summary_zh": "缺少路径。",
                "canvas": {"width": 1280, "height": 760},
                "nodes": [
                    {"id": "RA", "label": "RA", "node_kind": "input", "x": 80, "y": 120, "width": 180, "height": 96},
                    {"id": "L1", "label": "L1", "node_kind": "logic", "x": 420, "y": 120, "width": 190, "height": 104},
                ],
                "edges": [{"id": "edge_ra_l1", "source": "RA", "target": "L1", "label": "高度<6ft"}],
                "parameter_panels": [],
            }
        )

    with pytest.raises(RequirementsIntakeError) as exc:
        build_logic_drawing(_ready_requirements_payload(), provider="deepseek", request_post=fake_post)

    assert exc.value.code == "logic_drawing_json_error"
    assert "route" in exc.value.message


def test_build_logic_drawing_self_repairs_missing_required_concept_node(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls: list[dict] = []

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        calls.append(request)
        if len(calls) == 1:
            return _model_response(
                {
                    "summary_zh": "漏掉逻辑节点。",
                    "canvas": {"width": 1280, "height": 760},
                    "nodes": [
                        {
                            "id": "RA",
                            "label": "无线电高度",
                            "node_kind": "input",
                            "x": 80,
                            "y": 120,
                            "width": 180,
                            "height": 96,
                            "description_zh": "RA<6ft",
                        }
                    ],
                    "edges": [],
                    "parameter_panels": [],
                }
            )
        return _model_response(
            {
                "summary_zh": "已补齐缺失节点。",
                "canvas": {"width": 1280, "height": 760},
                "nodes": [
                    {
                        "id": "RA",
                        "label": "无线电高度",
                        "node_kind": "input",
                        "x": 80,
                        "y": 120,
                        "width": 180,
                        "height": 96,
                        "description_zh": "RA<6ft",
                    },
                    {
                        "id": "L1",
                        "label": "逻辑1",
                        "node_kind": "logic",
                        "x": 420,
                        "y": 120,
                        "width": 190,
                        "height": 104,
                        "description_zh": "TLS解锁",
                    },
                ],
                "edges": [
                    {
                        "id": "edge_ra_l1",
                        "source": "RA",
                        "target": "L1",
                        "label": "高度<6ft",
                        "route": [{"x": 260, "y": 168}, {"x": 420, "y": 168}],
                    }
                ],
                "parameter_panels": [],
                "drawing_notes": ["自修复补齐 L1。"],
            }
        )

    result = build_logic_drawing(_ready_requirements_payload(), provider="deepseek", request_post=fake_post)

    assert len(calls) == 2
    assert "修复" in calls[1]["messages"][0]["content"]
    assert "missing_required_nodes" in calls[1]["messages"][1]["content"]
    assert result["nodes"][1]["id"] == "L1"
    assert result["llm"]["self_repair"] == {
        "attempted": True,
        "success": True,
        "reason": "logic_drawing_json_error",
    }


def test_build_logic_drawing_reports_self_repair_failure(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls = 0

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        nonlocal calls
        calls += 1
        return _model_response({"summary_zh": "仍然没有图纸节点。", "edges": [], "parameter_panels": []})

    with pytest.raises(RequirementsIntakeError) as exc:
        build_logic_drawing(_ready_requirements_payload(), provider="deepseek", request_post=fake_post)

    assert calls == 2
    assert exc.value.code == "logic_drawing_json_error"
    assert exc.value.details["self_repair"]["attempted"] is True
    assert exc.value.details["self_repair"]["success"] is False
    assert exc.value.details["self_repair"]["error"] == "logic_drawing_json_error"


def test_interpret_logic_change_calls_model_for_user_confirmation(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "understanding_zh": "用户希望把 RA 放行门限从 6ft 调整为 7ft。",
                "requirements_match_zh": "原需求中 RA<6ft 是 L1 的输入条件。",
                "affected_nodes": ["RA", "L1"],
                "affected_edges": ["edge_ra_l1"],
                "affected_parameter_panels": ["panel_ra"],
                "proposed_changes": [
                    "更新 RA 节点描述为 RA<7ft。",
                    "更新 RA 参数面板默认值为 7ft。",
                ],
                "confirmation_question_zh": "是否确认将 RA 门限从 6ft 调整为 7ft？",
            }
        )

    result = interpret_logic_change(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        "选中 RA 节点，把高度门限改成 7ft。",
        target_node_id="RA",
        provider="deepseek",
        request_post=fake_post,
    )

    prompt = captured["body"]["messages"][1]["content"]
    assert "不要更新图纸" in prompt
    assert "选中 RA 节点" in prompt
    assert captured["body"]["max_tokens"] == 2048
    assert result["kind"] == "ai-fantui-logic-change-interpretation"
    assert result["status"] == "needs_user_confirmation"
    assert result["target_node_id"] == "RA"
    assert result["affected_nodes"] == ["RA", "L1"]
    assert result["confirmation_question_zh"].endswith("？")
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False


def test_interpret_logic_change_summarizes_multi_target_annotation_batch(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}
    annotation_batch = [
        {
            "target_type": "node",
            "target_id": "RA",
            "target_label": "RA",
            "text": "RA 节点门限应改成 7ft。",
        },
        {
            "target_type": "wire",
            "target_id": "RA->L1",
            "target_label": "RA → L1",
            "text": "这条连线需要同步说明 RA 如何进入 L1。",
        },
    ]

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "understanding_zh": "用户希望成组修订 RA 节点和 RA 到 L1 的输入解释。",
                "requirements_match_zh": "原需求中 RA<6ft 是 L1 输入条件。",
                "affected_nodes": ["RA", "L1"],
                "affected_edges": ["edge_ra_l1"],
                "affected_parameter_panels": ["panel_ra"],
                "proposed_changes": [
                    "把 RA 节点门限说明调整为 7ft。",
                    "同步更新 RA→L1 连线标签。",
                ],
                "annotation_batch_summary_zh": "2 条批注已归并为 1 个 RA 门限修订包。",
                "conflict_summary_zh": "未发现互相冲突的批注。",
                "annotation_groups": [
                    {
                        "group_label": "RA 门限",
                        "annotation_ids": ["annotation_1", "annotation_2"],
                        "summary_zh": "节点和连线均指向 RA 门限解释。",
                    }
                ],
                "confirmation_question_zh": "是否按该批注包修订 RA 节点和 RA→L1 连线？",
            }
        )

    result = interpret_logic_change(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        "批量标注意见：RA 节点和 RA→L1 连线需要一起修订。",
        target_node_id="RA",
        annotation_batch=annotation_batch,
        selected_nodes=["RA"],
        selected_edges=["RA->L1"],
        provider="deepseek",
        request_post=fake_post,
    )

    prompt = captured["body"]["messages"][1]["content"]
    assert "多点批注" in prompt
    assert "RA->L1" in prompt
    assert "归并重复批注" in prompt
    assert result["annotation_batch_summary_zh"] == "2 条批注已归并为 1 个 RA 门限修订包。"
    assert result["conflict_summary_zh"] == "未发现互相冲突的批注。"
    assert result["annotation_groups"][0]["group_label"] == "RA 门限"
    assert result["selected_nodes"] == ["RA"]
    assert result["selected_edges"] == ["RA->L1"]


def test_streamed_logic_authoring_session_proposes_one_atomic_edit_with_source_context():
    requirements_payload = _ready_requirements_payload()
    drawing_payload = _ready_drawing_payload()
    drawing_payload["nodes"][0]["source_anchors"] = [
        {
            "id": "REQ-RA",
            "kind": "正文条件",
            "origin": "docx_body",
            "quote_zh": "当无线电高度小于 6ft 时，L1 可进入下一逻辑。",
        }
    ]

    result = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)

    assert result["kind"] == "ai-fantui-streamed-logic-authoring-session"
    assert result["status"] == "awaiting_user_confirmation"
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False
    assert result["requirements_document_edit"]["requires_explicit_authorization"] is True
    proposal = result["active_proposal"]
    assert proposal["target_type"] == "node"
    assert proposal["target_id"] == "RA"
    assert proposal["edit_type"] == "add_node"
    assert proposal["requires_user_confirmation"] is True
    assert proposal["source_excerpt"] == "当无线电高度小于 6ft 时，L1 可进入下一逻辑。"
    assert proposal["source_anchor_ids"] == ["REQ-RA"]
    assert proposal["graph_diff"] == {
        "operation": "add_node",
        "node_ids_added": ["RA"],
        "wire_ids_added": [],
        "truth_effect": "none",
    }


def test_streamed_logic_authoring_session_schema_exists_and_validates_payload():
    import jsonschema

    requirements_payload = _ready_requirements_payload()
    drawing_payload = _ready_drawing_payload()
    result = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)
    schema_path = REPO_ROOT / "docs" / "json_schema" / "streamed_logic_authoring_session_v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(result)


def test_streamed_logic_authoring_session_uses_natural_language_prompt_to_choose_candidate():
    baseline = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    prompted = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        natural_language_prompt="请优先调整 L1 节点",
    )

    assert baseline["active_proposal"]["target_id"] == "RA"
    assert prompted["active_proposal"]["target_type"] == "node"
    assert prompted["active_proposal"]["target_id"] == "L1"
    assert prompted["candidate_queue"]["ordered_target_keys"][0] == "node:L1"
    assert prompted["candidate_queue"]["active_target_key"] == "node:L1"


def test_streamed_logic_authoring_session_advances_after_confirm_and_revises_after_feedback():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]

    second = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[
            {
                **_streamed_decision(first, first_proposal, "confirm"),
            }
        ],
    )

    assert second["accepted_edit_ids"] == [first_proposal["id"]]
    assert second["active_proposal"]["id"] != first_proposal["id"]
    assert second["active_proposal"]["sequence_index"] == 2

    revised = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[
            {
                **_streamed_decision(first, first_proposal, "request_revision"),
                "feedback_text": "需要明确这是候选节点，不要写入控制器。",
            }
        ],
    )

    revised_proposal = revised["active_proposal"]
    assert revised["rejected_edit_ids"] == [first_proposal["id"]]
    assert revised["truth_effect"] == "none"
    assert revised["controller_truth_modified"] is False
    assert revised["certification_claim"] == "none"
    assert revised_proposal["proposal_status"] == "revised_proposal_ready"
    assert revised_proposal["revision_of"] == first_proposal["id"]
    assert revised_proposal["revision_index"] == 1
    assert revised_proposal["user_feedback"] == "需要明确这是候选节点，不要写入控制器。"
    assert revised_proposal["feedback_applied"]["proposal_id"] == first_proposal["id"]
    assert revised_proposal["feedback_applied"]["feedback_text"] == "需要明确这是候选节点，不要写入控制器。"
    assert revised_proposal["feedback_applied"]["feedback_sha256"]
    assert revised_proposal["revision_gate"]["status"] == "revision_candidate_ready"
    assert revised_proposal["target_id"] == first_proposal["target_id"]
    assert revised["requirements_document_edit"]["authorized"] is False


def test_streamed_logic_authoring_session_returns_ordered_replay_and_committed_candidate_graph():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]

    second = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[
            {
                **_streamed_decision(first, first_proposal, "confirm"),
                "decided_at": "2026-05-22T08:00:00Z",
            }
        ],
    )

    replay = second["stream_replay"]
    assert len(replay) == 1
    assert replay[0]["event_type"] == "candidate_edit_committed"
    assert replay[0]["decision_index"] == 1
    assert replay[0]["proposal_id"] == first_proposal["id"]
    assert replay[0]["committed"] is True
    assert replay[0]["graph_diff"] == first_proposal["graph_diff"]
    assert replay[0]["source_excerpt"] == first_proposal["source_excerpt"]
    assert replay[0]["truth_effect"] == "none"
    assert replay[0]["controller_truth_modified"] is False
    assert replay[0]["requirements_document_modified"] is False

    committed_graph = second["committed_candidate_graph"]
    assert committed_graph["status"] == "one_edit_committed"
    assert committed_graph["commit_boundary"] == "one_confirmed_candidate_edit_per_user_decision"
    assert committed_graph["committed_edit_count"] == 1
    assert committed_graph["committed_edit_ids"] == [first_proposal["id"]]
    assert committed_graph["node_ids_added"] == first_proposal["graph_diff"]["node_ids_added"]
    assert committed_graph["wire_ids_added"] == []
    assert committed_graph["truth_effect"] == "none"
    assert committed_graph["controller_truth_modified"] is False
    assert committed_graph["requirements_document_modified"] is False


def test_streamed_logic_authoring_session_ignores_stale_or_duplicate_decisions():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    confirmed = _streamed_decision(first, first_proposal, "confirm")
    stale = {
        **confirmed,
        "proposal_id": "stale-proposal",
        "source_requirements_sha256": "stale-requirements",
        "source_drawing_sha256": "stale-drawing",
    }

    second = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[stale, confirmed, confirmed],
    )

    assert second["accepted_edit_ids"] == [first_proposal["id"]]
    assert len(second["stream_replay"]) == 1
    assert second["stream_replay"][0]["proposal_id"] == first_proposal["id"]
    assert second["committed_candidate_graph"]["committed_edit_count"] == 1
    assert second["committed_candidate_graph"]["committed_edit_ids"] == [first_proposal["id"]]


def test_streamed_logic_authoring_session_blocks_requirements_document_edit_without_authorization():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    feedback_text = "需求文档应补充：RA 节点是候选解释，不是控制器真值。"

    blocked = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[
            {
                **_streamed_decision(first, first_proposal, "request_revision"),
                "feedback_text": feedback_text,
                "requirements_document_edit_requested": True,
                "requirements_document_patch": {
                    "operation": "candidate_requirements_text_revision",
                    "proposed_text_zh": feedback_text,
                },
            }
        ],
    )

    edit = blocked["requirements_document_edit"]
    assert edit["status"] == "authorization_required"
    assert edit["requires_explicit_authorization"] is True
    assert edit["authorized"] is False
    assert edit["authorization_record"] is None
    assert edit["write_effect"] == "none"
    assert edit["truth_effect"] == "none"
    assert edit["controller_truth_modified"] is False
    assert edit["requirements_document_modified"] is False
    assert edit["authorization_gate"]["status"] == "blocked_without_explicit_authorization"
    assert edit["pending_candidate_patch"]["proposed_text_zh"] == feedback_text
    assert edit["pending_candidate_patch"]["requires_explicit_authorization"] is True
    assert "requirements_document_edit" not in blocked["active_proposal"]["graph_diff"]
    assert blocked["active_proposal"]["graph_diff"]["truth_effect"] == "none"

    authorized = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[
            {
                **_streamed_decision(first, first_proposal, "request_revision"),
                "feedback_text": feedback_text,
                "requirements_document_edit_requested": True,
                "requirements_document_edit_authorized": True,
                "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
                "requirements_document_patch": {
                    "operation": "candidate_requirements_text_revision",
                    "proposed_text_zh": feedback_text,
                },
            }
        ],
    )

    authorized_edit = authorized["requirements_document_edit"]
    assert authorized_edit["status"] == "authorized_candidate_patch"
    assert authorized_edit["authorized"] is True
    assert authorized_edit["write_effect"] == "none"
    assert authorized_edit["requirements_document_modified"] is False
    assert authorized_edit["authorization_record"]["proposal_id"] == first_proposal["id"]
    assert authorized_edit["authorization_gate"]["provided_phrase_matches"] is True


def test_streamed_logic_authoring_session_replays_revision_and_authorized_doc_patch():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    feedback_text = "RA 节点说明应写明这是候选解释，并补一个需求文档候选补丁。"
    decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }

    revised = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[decision],
    )

    event = revised["stream_replay"][0]
    assert event["event_type"] == "candidate_edit_revision_requested"
    assert event["committed"] is False
    assert event["candidate_recalculation"]["status"] == "revision_candidate_ready"
    assert event["candidate_recalculation"]["feedback_text"] == feedback_text
    assert event["candidate_recalculation"]["feedback_sha256"]
    assert event["requirements_document_patch_status"] == "authorized_candidate_patch"
    assert event["requirements_document_authorization_gate"]["status"] == "authorized"
    assert event["requirements_document_authorization_gate"]["provided_phrase_matches"] is True
    assert event["requirements_document_patch"]["proposed_text_zh"] == feedback_text
    assert event["requirements_document_patch_sha256"]
    assert event["requirements_document_modified"] is False
    assert event["truth_effect"] == "none"
    assert event["controller_truth_modified"] is False

    edit = revised["requirements_document_edit"]
    assert edit["status"] == "authorized_candidate_patch"
    assert edit["pending_candidate_patch"]["proposed_text_zh"] == feedback_text
    assert edit["pending_candidate_patch_sha256"] == event["requirements_document_patch_sha256"]
    assert revised["active_proposal"]["proposal_status"] == "revised_proposal_ready"
    assert revised["active_proposal"]["revision_gate"]["status"] == "revision_candidate_ready"


def test_streamed_logic_authoring_session_confirms_revised_candidate_and_advances_queue():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    feedback_text = "RA 节点说明应写明这是候选解释，并补一个需求文档候选补丁。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    confirm_revised = _streamed_decision(revised, revised_proposal, "confirm")

    after_revised_confirm = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[revision_decision, confirm_revised],
    )

    assert [event["event_type"] for event in after_revised_confirm["stream_replay"]] == [
        "candidate_edit_revision_requested",
        "candidate_edit_committed",
    ]
    assert after_revised_confirm["stream_replay"][1]["commits_revision"] is True
    assert after_revised_confirm["stream_replay"][1]["confirmed_revision_of"] == first_proposal["id"]
    assert after_revised_confirm["accepted_edit_ids"] == [revised_proposal["id"]]
    assert after_revised_confirm["rejected_edit_ids"] == [first_proposal["id"]]
    assert after_revised_confirm["committed_candidate_graph"]["committed_edit_count"] == 1
    assert after_revised_confirm["committed_candidate_graph"]["confirmed_revision_pairs"] == [
        {
            "committed_proposal_id": revised_proposal["id"],
            "revision_of": first_proposal["id"],
            "target_key": "node:RA",
        }
    ]
    assert after_revised_confirm["committed_candidate_graph"]["node_ids_added"] == ["RA"]
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False
    next_node = after_revised_confirm["active_proposal"]
    assert next_node["proposal_status"] == "candidate_proposal_ready"
    assert next_node["target_type"] == "node"
    assert next_node["target_id"] == "L1"
    assert next_node["sequence_index"] == 2
    queue = after_revised_confirm["candidate_queue"]
    assert queue["status"] == "candidate_queue_active"
    assert queue["total_candidate_count"] == 3
    assert queue["accepted_count"] == 1
    assert queue["rejected_count"] == 1
    assert queue["replay_event_count"] == 2
    assert queue["active_target_key"] == "node:L1"
    assert queue["next_candidate_kind"] == "node"
    assert queue["can_continue_after_revision"] is True
    assert queue["truth_effect"] == "none"
    assert queue["controller_truth_modified"] is False

    confirm_next_node = _streamed_decision(after_revised_confirm, next_node, "confirm")
    after_second_confirm = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[revision_decision, confirm_revised, confirm_next_node],
    )

    assert after_second_confirm["committed_candidate_graph"]["status"] == "multiple_edits_committed"
    assert after_second_confirm["committed_candidate_graph"]["committed_edit_count"] == 2
    assert after_second_confirm["committed_candidate_graph"]["node_ids_added"] == ["RA", "L1"]
    assert len(after_second_confirm["stream_replay"]) == 3
    next_wire = after_second_confirm["active_proposal"]
    assert next_wire["target_type"] == "wire"
    assert next_wire["target_id"] == "RA->L1"
    assert next_wire["sequence_index"] == 3
    wire_queue = after_second_confirm["candidate_queue"]
    assert wire_queue["accepted_count"] == 2
    assert wire_queue["active_sequence_index"] == 3
    assert wire_queue["active_target_key"] == "wire:RA->L1"
    assert wire_queue["next_candidate_kind"] == "wire"
    assert wire_queue["pending_count"] == 1


def test_streamed_logic_authoring_session_rejects_stale_original_confirm_after_revision():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": "RA 节点说明应写明这是候选解释。",
    }
    stale_original_confirm = _streamed_decision(first, first_proposal, "confirm")

    session = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[revision_decision, stale_original_confirm],
    )

    assert session["accepted_edit_ids"] == []
    assert session["rejected_edit_ids"] == [first_proposal["id"]]
    assert [event["event_type"] for event in session["stream_replay"]] == [
        "candidate_edit_revision_requested"
    ]
    assert session["committed_candidate_graph"]["committed_edit_count"] == 0
    assert session["candidate_queue"]["status"] == "revision_candidate_ready"
    assert session["candidate_queue"]["active_target_key"] == "node:RA"
    assert session["candidate_queue"]["accepted_count"] == 0
    assert session["active_proposal"]["proposal_status"] == "revised_proposal_ready"
    assert session["active_proposal"]["id"] != first_proposal["id"]
    assert session["active_proposal"]["revision_of"] == first_proposal["id"]


def _c919_etras_raw_requirement_text() -> str:
    return "\n".join(
        [
            "C919 E-TRAS 原始需求片段。",
            "R-C919-WOW: 当 WOW 双通道有效且反推手柄进入解锁区间时，ETRAS 可进入预位。",
            "R-C919-ARM: ETRAS 仅在 WOW 有效且手柄解锁区间成立后进入预位。",
            "R-C919-GATE: WOW 有效是 ETRAS 预位的前置门限。",
            "边界: 本片段只用于候选解释，不修改控制器，不构成冻结版或认证声明。",
        ]
    )


def _c919_etras_raw_streamed_requirements_payload() -> dict:
    return build_local_preparse_payload(
        _c919_etras_raw_requirement_text(),
        document_name="c919-etras-raw-intake.txt",
    )


def _c919_etras_real_doc_streamed_requirements_payload() -> dict:
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    return build_local_preparse_payload(
        document_path.read_text(encoding="utf-8"),
        document_name=document_path.name,
    )


def _c919_etras_real_doc_cmd2_drawing_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "summary_zh": "C919 ETRAS V0.9 CMD2 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "mlg_wow",
                "label": "MLG_WOW",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 180,
                "height": 92,
                "description_zh": "主轮载荷/WOW 已解析单路输入。",
            },
            {
                "id": "cmd2_active",
                "label": "CMD2 单相解锁",
                "node_kind": "logic",
                "x": 360,
                "y": 120,
                "width": 220,
                "height": 96,
                "description_zh": "TLS 与吊挂锁 115VAC 单相解锁供电候选节点。",
            },
        ],
        "edges": [
            {
                "id": "c919_v09_cmd2_edge",
                "source": "mlg_wow",
                "target": "cmd2_active",
                "label": "CMD2 ground gate",
                "route": [{"x": 260, "y": 168}, {"x": 360, "y": 168}],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw intake gate。"],
    }


def _c919_etras_real_doc_cmd3_apwtla_drawing_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "summary_zh": "C919 ETRAS V0.9 CMD3/APWTLA 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "apwtla",
                "label": "APWTLA/SW2",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 180,
                "height": 92,
                "description_zh": "TRA 经过 SW2 窗口后的三相作动请求。",
            },
            {
                "id": "cmd3_output",
                "label": "CMD3 三相作动",
                "node_kind": "logic",
                "x": 360,
                "y": 120,
                "width": 220,
                "height": 96,
                "description_zh": "TRCU 115VAC 三相作动供电 SR 锁存输出。",
            },
        ],
        "edges": [
            {
                "id": "c919_v09_cmd3_apwtla_edge",
                "source": "apwtla",
                "target": "cmd3_output",
                "label": "SW2 set gate",
                "route": [{"x": 260, "y": 168}, {"x": 360, "y": 168}],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 CMD3/APWTLA raw intake gate。"],
    }


def _c919_etras_real_doc_deploy_cmd1_drawing_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "summary_zh": "C919 ETRAS V0.9 Deploy CMD1 相邻阶段候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "cmd3_output",
                "label": "CMD3 三相作动",
                "node_kind": "logic",
                "x": 80,
                "y": 120,
                "width": 220,
                "height": 96,
                "description_zh": "TRCU 115VAC 三相作动供电 SR 锁存输出。",
            },
            {
                "id": "deploy_cmd1_active",
                "label": "Deploy CMD1",
                "node_kind": "logic",
                "x": 400,
                "y": 120,
                "width": 220,
                "height": 96,
                "description_zh": "FADEC 展开命令候选节点。",
            },
        ],
        "edges": [
            {
                "id": "c919_v09_deploy_cmd1_edge",
                "source": "cmd3_output",
                "target": "deploy_cmd1_active",
                "label": "Deploy CMD1 evaluation after CMD3",
                "route": [{"x": 300, "y": 168}, {"x": 400, "y": 168}],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 Deploy CMD1 raw intake gate。"],
    }


def _c919_etras_real_doc_thr_idle_lock_release_drawing_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "summary_zh": "C919 ETRAS V0.9 Deploy 后续展开确认/慢车锁释放候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "deploy_cmd1_active",
                "label": "Deploy CMD1",
                "node_kind": "logic",
                "x": 80,
                "y": 120,
                "width": 220,
                "height": 96,
                "description_zh": "FADEC 展开命令候选节点。",
            },
            {
                "id": "thr_idle_lock_release",
                "label": "慢车锁释放",
                "node_kind": "output",
                "x": 400,
                "y": 120,
                "width": 220,
                "height": 96,
                "description_zh": "TR 展开确认后释放油门慢车电子锁。",
            },
        ],
        "edges": [
            {
                "id": "c919_v09_thr_idle_lock_release_edge",
                "source": "deploy_cmd1_active",
                "target": "thr_idle_lock_release",
                "label": "TR deployed confirmation",
                "route": [{"x": 300, "y": 168}, {"x": 400, "y": 168}],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档慢车锁释放 raw intake gate。"],
    }


def test_local_preparse_handles_c919_etras_raw_requirement_packet_for_streamed_queue():
    payload = _c919_etras_raw_streamed_requirements_payload()

    assert payload["status"] == "ready_for_logic_builder"
    assert payload["ready_for_logic_builder"] is True
    assert payload["llm"]["provider"] == "local-preparse"
    assert payload["llm"]["model"] == "deterministic-c919-etras"
    assert payload["llm"]["response_source"] == "deterministic_preparse"
    assert payload["deterministic_preparse"]["applied"] is True
    assert payload["deterministic_preparse"]["strategy"] == "c919_etras_rule_preparse"
    assert payload["truth_effect"] == "none"
    assert payload["candidate_state"] == "concept_only"
    assert payload["certification_claim"] == "none"
    assert payload["controller_truth_modified"] is False
    assert payload["source_scope"]["c919_etras"]["status"] == "candidate_only"
    assert "冻结版或认证声明" in payload["source_scope"]["c919_etras"]["reason_zh"]

    nodes_by_id = {node["id"]: node for node in payload["concept_logic_nodes"]}
    assert {"wow_valid", "etras_armed", "handle_unlock_range"}.issubset(nodes_by_id)
    assert nodes_by_id["wow_valid"]["source_anchors"][0]["id"] == "C919-ETRAS-WOW"
    assert nodes_by_id["wow_valid"]["source_anchors"][0]["origin"] == "c919_etras_doc"
    assert "WOW 双通道有效" in nodes_by_id["wow_valid"]["source_anchors"][0]["quote_zh"]
    assert nodes_by_id["etras_armed"]["source_anchors"][0]["id"] == "C919-ETRAS-ARM"
    assert "ETRAS 仅在" in nodes_by_id["etras_armed"]["source_anchors"][0]["quote_zh"]
    assert "候选解释" in nodes_by_id["etras_armed"]["description_zh"]

    edges_by_id = {edge["id"]: edge for edge in payload["concept_edges"]}
    assert edges_by_id["c919_e1"]["source"] == "wow_valid"
    assert edges_by_id["c919_e1"]["target"] == "etras_armed"
    assert edges_by_id["c919_e1"]["label"] == "WOW gating"
    assert edges_by_id["c919_e1"]["source_anchors"][0]["id"] == "C919-ETRAS-WOW-EDGE"
    validate_agent_output_contract(payload["agent_output_contract_v0_1"]["requirement_analyst"])


def test_local_preparse_handles_c919_etras_v09_real_document_for_cmd2_gate():
    payload = _c919_etras_real_doc_streamed_requirements_payload()

    assert payload["source_document"]["name"] == "requirements_v0_9.md"
    assert payload["status"] == "ready_for_logic_builder"
    assert payload["ready_for_logic_builder"] is True
    assert payload["llm"]["provider"] == "local-preparse"
    assert payload["llm"]["model"] == "deterministic-c919-etras-v09"
    assert payload["deterministic_preparse"]["strategy"] == "c919_etras_v09_rule_preparse"
    assert payload["truth_effect"] == "none"
    assert payload["candidate_state"] == "concept_only"
    assert payload["certification_claim"] == "none"
    assert payload["controller_truth_modified"] is False
    assert payload["source_scope"]["c919_etras"]["status"] == "candidate_only"
    assert payload["source_scope"]["engineering_inference"]["status"] == "source_declared"

    nodes_by_id = {node["id"]: node for node in payload["concept_logic_nodes"]}
    assert {
        "mlg_wow",
        "cmd2_active",
        "apwtla",
        "cmd3_output",
        "deploy_cmd1_active",
        "thr_idle_lock_release",
    }.issubset(nodes_by_id)
    assert "etras_armed" not in nodes_by_id
    assert nodes_by_id["mlg_wow"]["source_anchors"][0]["id"] == "C919-V09-MLG-WOW"
    assert "`mlg_wow`" in nodes_by_id["mlg_wow"]["source_anchors"][0]["quote_zh"]
    assert "主轮载荷" in nodes_by_id["mlg_wow"]["source_anchors"][0]["quote_zh"]
    apwtla_anchor_ids = {
        anchor["id"] for anchor in nodes_by_id["apwtla"]["source_anchors"]
    }
    assert {"C919-V09-APWTLA", "C919-V09-CMD3-SET-APWTLA"}.issubset(apwtla_anchor_ids)

    edge = next(
        item
        for item in payload["concept_edges"]
        if item["source"] == "mlg_wow" and item["target"] == "cmd2_active"
    )
    assert edge["label"] == "CMD2 ground gate"
    edge_quotes = " ".join(anchor["quote_zh"] for anchor in edge["source_anchors"])
    assert "`mlg_wow`" in edge_quotes
    assert "TRUE" in edge_quotes
    assert "WOW 双通道有效且反推手柄进入解锁区间" not in json.dumps(
        payload,
        ensure_ascii=False,
    )
    cmd3_edge = next(
        item
        for item in payload["concept_edges"]
        if item["source"] == "apwtla" and item["target"] == "cmd3_output"
    )
    assert cmd3_edge["id"] == "c919_v09_e4"
    assert cmd3_edge["label"] == "SW2 set gate"
    cmd3_edge_anchor_ids = {anchor["id"] for anchor in cmd3_edge["source_anchors"]}
    assert {
        "C919-V09-CMD3-SET",
        "C919-V09-CMD3-SET-APWTLA",
        "C919-V09-CMD3-SR-OUTPUT",
        "C919-V09-CMD3-RESET-PRIORITY",
    }.issubset(cmd3_edge_anchor_ids)
    cmd3_edge_quotes = " ".join(anchor["quote_zh"] for anchor in cmd3_edge["source_anchors"])
    assert "CMD3 Set" in cmd3_edge_quotes
    assert "`apwtla`" in cmd3_edge_quotes
    assert "ThreePhaseTRCUPower_On = cmd3_output" in cmd3_edge_quotes
    assert "Reset 优先" in cmd3_edge_quotes
    deploy_edge = next(
        item
        for item in payload["concept_edges"]
        if item["source"] == "cmd3_output" and item["target"] == "deploy_cmd1_active"
    )
    assert deploy_edge["id"] == "c919_v09_e5"
    assert deploy_edge["label"] == "Deploy CMD1 evaluation after CMD3"
    assert deploy_edge["label"] != "TRCU power before deploy"
    deploy_edge_anchor_ids = {anchor["id"] for anchor in deploy_edge["source_anchors"]}
    assert {
        "C919-V09-CMD3-SR-OUTPUT",
        "C919-V09-DEPLOY-CMD1-OUTPUT",
        "C919-V09-DEPLOY-CMD1-ENGINE",
        "C919-V09-DEPLOY-CMD1-INHIBITED",
        "C919-V09-DEPLOY-CMD1-LOCKS",
        "C919-V09-DEPLOY-CMD1-TR-WOW",
        "C919-V09-DEPLOY-CMD1-N1K",
        "C919-V09-DEPLOY-CMD1-TRA",
        "C919-V09-EVAL-CMD3-SR-OUTPUT",
        "C919-V09-EVAL-DEPLOY-CMD1",
    }.issubset(deploy_edge_anchor_ids)
    deploy_edge_quotes = " ".join(anchor["quote_zh"] for anchor in deploy_edge["source_anchors"])
    assert "FADEC_Deploy_Command = deploy_cmd1_active" in deploy_edge_quotes
    assert "locks_unlocked_or_confirmed" in deploy_edge_quotes
    assert "max_n1k_deploy_limit_pct" in deploy_edge_quotes
    assert "tra_deg" in deploy_edge_quotes
    assert "6. 评估 CMD3 SR 锁存输出" in deploy_edge_quotes
    assert "8. 评估 Deploy CMD1" in deploy_edge_quotes
    thr_idle_edge = next(
        item
        for item in payload["concept_edges"]
        if item["source"] == "deploy_cmd1_active" and item["target"] == "thr_idle_lock_release"
    )
    assert thr_idle_edge["id"] == "c919_v09_e6"
    assert thr_idle_edge["label"] == "TR deployed confirmation"
    assert thr_idle_edge["label"] != "Deploy CMD1 directly releases THR idle lock"
    thr_idle_edge_anchor_ids = {anchor["id"] for anchor in thr_idle_edge["source_anchors"]}
    assert {
        "C919-V09-DEPLOY-CMD1-OUTPUT",
        "C919-V09-DEPLOY-CMD1-ENGINE",
        "C919-V09-DEPLOY-CMD1-INHIBITED",
        "C919-V09-DEPLOY-CMD1-LOCKS",
        "C919-V09-DEPLOY-CMD1-TR-WOW",
        "C919-V09-DEPLOY-CMD1-N1K",
        "C919-V09-DEPLOY-CMD1-TRA",
        "C919-V09-THR-IDLE-OUTPUT",
        "C919-V09-THR-IDLE-TR-DEPLOYED",
        "C919-V09-THR-IDLE-POS-CONF",
    }.issubset(thr_idle_edge_anchor_ids)
    thr_idle_edge_quotes = " ".join(anchor["quote_zh"] for anchor in thr_idle_edge["source_anchors"])
    assert "FADEC_Deploy_Command = deploy_cmd1_active" in thr_idle_edge_quotes
    assert "`tr_deployed_confirmed`" in thr_idle_edge_quotes
    assert "TR_Position ≥ 80%" in thr_idle_edge_quotes
    assert "持续 0.5s" in thr_idle_edge_quotes


def test_local_preparse_c919_etras_v09_fails_closed_without_cmd2_mlg_wow_condition():
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    partial_text = document_path.read_text(encoding="utf-8").replace(
        "| ① | `mlg_wow` | == | TRUE |",
        "| ① | `mlg_wow` | 待确认 | TRUE |",
    )

    payload = build_local_preparse_payload(
        partial_text,
        document_name="requirements_v0_9_missing_cmd2_condition.md",
    )

    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["deterministic_preparse"]["reason"] == "c919_etras_v09_coverage_not_found"
    assert "cmd2_active" in payload["deterministic_preparse"]["present_signal_ids"]
    assert "cmd2_mlg_wow_condition" not in payload["deterministic_preparse"]["present_signal_ids"]
    assert payload["concept_logic_nodes"] == []
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_local_preparse_c919_etras_v09_fails_closed_without_cmd3_apwtla_condition():
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    partial_text = document_path.read_text(encoding="utf-8").replace(
        "| ④ | `apwtla` | == | TRUE |",
        "| ④ | `apwtla` | 待确认 | TRUE |",
    )

    payload = build_local_preparse_payload(
        partial_text,
        document_name="requirements_v0_9_missing_cmd3_apwtla_condition.md",
    )

    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["deterministic_preparse"]["reason"] == "c919_etras_v09_coverage_not_found"
    assert "cmd3_output" in payload["deterministic_preparse"]["present_signal_ids"]
    assert "cmd3_apwtla_condition" not in payload["deterministic_preparse"]["present_signal_ids"]
    assert payload["concept_logic_nodes"] == []
    assert payload["concept_edges"] == []
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_local_preparse_c919_etras_v09_fails_closed_without_deploy_output():
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    partial_text = document_path.read_text(encoding="utf-8").replace(
        "**输出**: `FADEC_Deploy_Command = deploy_cmd1_active`",
        "**输出**: `FADEC_Deploy_Command = 待确认`",
    )

    payload = build_local_preparse_payload(
        partial_text,
        document_name="requirements_v0_9_missing_deploy_output.md",
    )

    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["deterministic_preparse"]["reason"] == "c919_etras_v09_coverage_not_found"
    assert "deploy_cmd1_active" in payload["deterministic_preparse"]["present_signal_ids"]
    assert "deploy_cmd1_output" not in payload["deterministic_preparse"]["present_signal_ids"]
    assert payload["concept_logic_nodes"] == []
    assert payload["concept_edges"] == []
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_local_preparse_c919_etras_v09_fails_closed_without_deploy_locks_condition():
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    partial_text = document_path.read_text(encoding="utf-8").replace(
        "| ③ | `locks_unlocked_or_confirmed` | == | TRUE | TLS + 两吊挂锁解锁（见 5.5a）|",
        "| ③ | `locks_unlocked_or_confirmed` | 待确认 | TRUE | TLS + 两吊挂锁解锁（见 5.5a）|",
    )

    payload = build_local_preparse_payload(
        partial_text,
        document_name="requirements_v0_9_missing_deploy_locks_condition.md",
    )

    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["deterministic_preparse"]["reason"] == "c919_etras_v09_coverage_not_found"
    assert "deploy_cmd1_active" in payload["deterministic_preparse"]["present_signal_ids"]
    assert "deploy_cmd1_locks_condition" not in payload["deterministic_preparse"]["present_signal_ids"]
    assert payload["concept_logic_nodes"] == []
    assert payload["concept_edges"] == []
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_local_preparse_c919_etras_v09_fails_closed_without_thr_idle_output():
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    partial_text = document_path.read_text(encoding="utf-8").replace(
        "**输出**: `thr_idle_lock_release`",
        "**输出**: `thr_idle_release_pending`",
    )

    payload = build_local_preparse_payload(
        partial_text,
        document_name="requirements_v0_9_missing_thr_idle_output.md",
    )

    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["deterministic_preparse"]["reason"] == "c919_etras_v09_coverage_not_found"
    assert "thr_idle_lock_release" in payload["deterministic_preparse"]["present_signal_ids"]
    assert "thr_idle_output" not in payload["deterministic_preparse"]["present_signal_ids"]
    assert payload["concept_logic_nodes"] == []
    assert payload["concept_edges"] == []
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_local_preparse_c919_etras_v09_fails_closed_without_thr_idle_deployed_condition():
    document_path = REPO_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    partial_text = document_path.read_text(encoding="utf-8").replace(
        "| ① | `tr_deployed_confirmed` | == | TRUE |",
        "| ① | `tr_deployed_confirmed` | 待确认 | TRUE |",
    )

    payload = build_local_preparse_payload(
        partial_text,
        document_name="requirements_v0_9_missing_thr_idle_deployed_condition.md",
    )

    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["deterministic_preparse"]["reason"] == "c919_etras_v09_coverage_not_found"
    assert "thr_idle_lock_release" in payload["deterministic_preparse"]["present_signal_ids"]
    assert "thr_idle_tr_deployed_condition" not in payload["deterministic_preparse"]["present_signal_ids"]
    assert payload["concept_logic_nodes"] == []
    assert payload["concept_edges"] == []
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_local_preparse_keeps_l1_l4_mainline_when_c919_background_is_mixed_in():
    mixed_text = "\n".join(
        [
            "背景说明：C919 E-TRAS 与 WOW 术语只作为跨域参考，不是本文档主链路。",
            "工作逻辑1 L1：当 RA<6ft 且 SW1 进入 TRA [-1.4,-6.2] 区间，输出 TLS 115VAC。",
            "工作逻辑2 L2：当 SW2 有效且 TRA 区间满足时，输出 ETRAC 540VDC。",
            "工作逻辑3 L3：TLS/PLS 反馈满足后，驱动 PDU motor 并等待 VDT。",
            "工作逻辑4 L4：当 VDT 达到 90% deploy 且 TRA<=-11.74°，THR_LOCK release。",
            "附录：当 WOW 双通道有效且反推手柄进入解锁区间时，ETRAS 可进入预位。",
        ]
    )

    payload = build_local_preparse_payload(mixed_text, document_name="mixed-c919-l1-l4.docx")

    assert payload["status"] == "ready_for_logic_builder"
    assert payload["deterministic_preparse"]["strategy"] == "docx_l1_l4_rule_preparse"
    node_ids = {node["id"] for node in payload["concept_logic_nodes"]}
    assert {"logic1", "logic2", "logic3", "logic4", "ra_lt_6ft", "thr_lock_release"}.issubset(
        node_ids
    )
    assert "wow_valid" not in node_ids
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def _c919_etras_streamed_requirements_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "summary_zh": "C919 ETRAS 候选链路已解析。",
        "open_questions": [],
        "concept_logic_nodes": [
            {
                "id": "wow_valid",
                "label": "WOW 有效",
                "node_kind": "input",
                "description_zh": "双通道地面信号一致。",
                "source_anchors": [
                    {
                        "id": "C919-ETRAS-WOW",
                        "kind": "需求条款",
                        "origin": "c919_etras_doc",
                        "quote_zh": "当 WOW 双通道有效且反推手柄进入解锁区间时，ETRAS 可进入预位。",
                    }
                ],
            },
            {
                "id": "etras_armed",
                "label": "ETRAS 预位",
                "node_kind": "logic",
                "description_zh": "反推预位候选逻辑。",
            },
        ],
        "concept_edges": [
            {
                "id": "c919_e1",
                "source": "wow_valid",
                "target": "etras_armed",
                "label": "WOW gating",
            }
        ],
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _c919_etras_streamed_drawing_payload() -> dict:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "summary_zh": "C919 ETRAS 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "wow_valid",
                "label": "WOW 有效",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 180,
                "height": 92,
                "description_zh": "双通道地面信号一致。",
            },
            {
                "id": "etras_armed",
                "label": "ETRAS 预位",
                "node_kind": "logic",
                "x": 360,
                "y": 120,
                "width": 190,
                "height": 96,
                "description_zh": "反推预位候选逻辑。",
            },
        ],
        "edges": [
            {
                "id": "c919_edge",
                "source": "wow_valid",
                "target": "etras_armed",
                "label": "WOW gating",
                "route": [{"x": 260, "y": 168}, {"x": 360, "y": 168}],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["C919 ETRAS 第二域 fixture。"],
    }


def test_streamed_logic_authoring_session_c919_etras_confirms_revised_candidate_and_advances_queue():
    first = build_streamed_logic_authoring_session(
        _c919_etras_streamed_requirements_payload(),
        _c919_etras_streamed_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    feedback_text = "WOW 有效节点说明应写明这是 C919 ETRAS 候选解释。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        _c919_etras_streamed_requirements_payload(),
        _c919_etras_streamed_drawing_payload(),
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    after_revised_confirm = build_streamed_logic_authoring_session(
        _c919_etras_streamed_requirements_payload(),
        _c919_etras_streamed_drawing_payload(),
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
        ],
    )
    next_node = after_revised_confirm["active_proposal"]
    after_second_confirm = build_streamed_logic_authoring_session(
        _c919_etras_streamed_requirements_payload(),
        _c919_etras_streamed_drawing_payload(),
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
            _streamed_decision(after_revised_confirm, next_node, "confirm"),
        ],
    )

    assert first_proposal["target_id"] == "wow_valid"
    assert revised_proposal["id"] == "m21-node-wow_valid-revision-1"
    assert after_revised_confirm["stream_replay"][1]["commits_revision"] is True
    assert after_revised_confirm["stream_replay"][1]["confirmed_revision_of"] == first_proposal["id"]
    assert after_revised_confirm["committed_candidate_graph"]["committed_edit_ids"] == [
        revised_proposal["id"]
    ]
    assert after_revised_confirm["candidate_queue"]["active_target_key"] == "node:etras_armed"
    assert after_revised_confirm["active_proposal"]["target_id"] == "etras_armed"
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False

    next_wire = after_second_confirm["active_proposal"]
    assert next_wire["target_type"] == "wire"
    assert next_wire["target_id"] == "wow_valid->etras_armed"
    assert after_second_confirm["candidate_queue"]["active_target_key"] == "wire:wow_valid->etras_armed"
    assert after_second_confirm["candidate_queue"]["accepted_count"] == 2
    assert after_second_confirm["candidate_queue"]["pending_count"] == 1
    assert after_second_confirm["truth_effect"] == "none"
    assert after_second_confirm["controller_truth_modified"] is False


def test_streamed_logic_authoring_session_c919_raw_intake_payload_advances_queue():
    requirements_payload = _c919_etras_raw_streamed_requirements_payload()
    first = build_streamed_logic_authoring_session(
        requirements_payload,
        _c919_etras_streamed_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    feedback_text = "WOW 有效节点说明应写明这是 C919 ETRAS 原始需求候选解释。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        requirements_payload,
        _c919_etras_streamed_drawing_payload(),
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    after_revised_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        _c919_etras_streamed_drawing_payload(),
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
        ],
    )
    next_node = after_revised_confirm["active_proposal"]
    after_second_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        _c919_etras_streamed_drawing_payload(),
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
            _streamed_decision(after_revised_confirm, next_node, "confirm"),
        ],
    )

    assert first["m21_mode"] == "engineer_in_the_loop_streamed_authoring"
    assert first_proposal["target_id"] == "wow_valid"
    assert first_proposal["source_anchor_ids"] == ["C919-ETRAS-WOW"]
    assert "WOW 双通道有效" in first_proposal["source_excerpt"]
    assert revised_proposal["proposal_status"] == "revised_proposal_ready"
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False
    assert after_revised_confirm["candidate_queue"]["active_target_key"] == "node:etras_armed"
    assert after_revised_confirm["active_proposal"]["target_id"] == "etras_armed"
    assert after_second_confirm["active_proposal"]["target_type"] == "wire"
    assert after_second_confirm["active_proposal"]["target_id"] == "wow_valid->etras_armed"
    assert after_second_confirm["candidate_queue"]["accepted_count"] == 2
    assert after_second_confirm["candidate_queue"]["pending_count"] == 1
    assert after_second_confirm["truth_effect"] == "none"
    assert after_second_confirm["controller_truth_modified"] is False


def test_streamed_logic_authoring_session_c919_real_doc_raw_intake_advances_cmd2_queue():
    requirements_payload = _c919_etras_real_doc_streamed_requirements_payload()
    drawing_payload = _c919_etras_real_doc_cmd2_drawing_payload()
    first = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)
    first_proposal = first["active_proposal"]
    feedback_text = "MLG_WOW 节点说明应写明这是 C919 ETRAS V0.9 原文候选解释。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    after_revised_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
        ],
    )
    next_node = after_revised_confirm["active_proposal"]
    after_second_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
            _streamed_decision(after_revised_confirm, next_node, "confirm"),
        ],
    )

    assert first["m21_mode"] == "engineer_in_the_loop_streamed_authoring"
    assert first_proposal["target_id"] == "mlg_wow"
    assert first_proposal["source_anchor_ids"] == ["C919-V09-MLG-WOW"]
    assert "`mlg_wow`" in first_proposal["source_excerpt"]
    assert "主轮载荷" in first_proposal["source_excerpt"]
    assert revised_proposal["proposal_status"] == "revised_proposal_ready"
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False
    assert after_revised_confirm["candidate_queue"]["active_target_key"] == "node:cmd2_active"
    assert after_revised_confirm["active_proposal"]["target_id"] == "cmd2_active"
    assert after_second_confirm["active_proposal"]["target_type"] == "wire"
    assert after_second_confirm["active_proposal"]["target_id"] == "mlg_wow->cmd2_active"
    assert "C919-V09-CMD2-MLG-WOW" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-CMD2" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert after_second_confirm["candidate_queue"]["accepted_count"] == 2
    assert after_second_confirm["candidate_queue"]["pending_count"] == 1
    assert after_second_confirm["truth_effect"] == "none"
    assert after_second_confirm["controller_truth_modified"] is False


def test_streamed_logic_authoring_session_c919_real_doc_raw_intake_advances_cmd3_apwtla_queue():
    requirements_payload = _c919_etras_real_doc_streamed_requirements_payload()
    drawing_payload = _c919_etras_real_doc_cmd3_apwtla_drawing_payload()
    first = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)
    first_proposal = first["active_proposal"]
    feedback_text = "APWTLA 节点说明应写明这是 CMD3 Set 的 SW2 置位候选解释。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    after_revised_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
        ],
    )
    next_node = after_revised_confirm["active_proposal"]
    after_second_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
            _streamed_decision(after_revised_confirm, next_node, "confirm"),
        ],
    )

    assert first["m21_mode"] == "engineer_in_the_loop_streamed_authoring"
    assert first_proposal["target_id"] == "apwtla"
    assert "C919-V09-CMD3-SET-APWTLA" in first_proposal["source_anchor_ids"]
    assert "`apwtla`" in first_proposal["source_excerpt"]
    assert "微动开关 2" in first_proposal["source_excerpt"]
    assert revised["active_proposal"]["proposal_status"] == "revised_proposal_ready"
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False
    assert after_revised_confirm["candidate_queue"]["active_target_key"] == "node:cmd3_output"
    assert after_revised_confirm["active_proposal"]["target_id"] == "cmd3_output"
    assert after_second_confirm["active_proposal"]["target_type"] == "wire"
    assert after_second_confirm["active_proposal"]["target_id"] == "apwtla->cmd3_output"
    assert "C919-V09-CMD3-SET" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-CMD3-SET-APWTLA" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-CMD3-SR-OUTPUT" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-CMD3-RESET-PRIORITY" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "CMD3 Set" in after_second_confirm["active_proposal"]["source_excerpt"]
    assert after_second_confirm["candidate_queue"]["accepted_count"] == 2
    assert after_second_confirm["candidate_queue"]["pending_count"] == 1
    assert after_second_confirm["truth_effect"] == "none"
    assert after_second_confirm["controller_truth_modified"] is False


def test_streamed_logic_authoring_session_c919_real_doc_raw_intake_advances_deploy_cmd1_queue():
    requirements_payload = _c919_etras_real_doc_streamed_requirements_payload()
    drawing_payload = _c919_etras_real_doc_deploy_cmd1_drawing_payload()
    first = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)
    first_proposal = first["active_proposal"]
    feedback_text = "Deploy CMD1 连线说明应写明这是相邻评估阶段候选解释，不是布尔门限。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    after_revised_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
        ],
    )
    next_node = after_revised_confirm["active_proposal"]
    after_second_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
            _streamed_decision(after_revised_confirm, next_node, "confirm"),
        ],
    )

    assert first["m21_mode"] == "engineer_in_the_loop_streamed_authoring"
    assert first_proposal["target_id"] == "cmd3_output"
    assert "C919-V09-CMD3-SR-OUTPUT" in first_proposal["source_anchor_ids"]
    assert "ThreePhaseTRCUPower_On = cmd3_output" in first_proposal["source_excerpt"]
    assert revised["active_proposal"]["proposal_status"] == "revised_proposal_ready"
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False
    assert after_revised_confirm["candidate_queue"]["active_target_key"] == "node:deploy_cmd1_active"
    assert after_revised_confirm["active_proposal"]["target_id"] == "deploy_cmd1_active"
    assert after_second_confirm["active_proposal"]["target_type"] == "wire"
    assert after_second_confirm["active_proposal"]["target_id"] == "cmd3_output->deploy_cmd1_active"
    assert "C919-V09-CMD3-SR-OUTPUT" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-DEPLOY-CMD1-OUTPUT" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-DEPLOY-CMD1-ENGINE" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-DEPLOY-CMD1-INHIBITED" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "ThreePhaseTRCUPower_On = cmd3_output" in after_second_confirm["active_proposal"]["source_excerpt"]
    assert after_second_confirm["candidate_queue"]["accepted_count"] == 2
    assert after_second_confirm["candidate_queue"]["pending_count"] == 1
    assert after_second_confirm["truth_effect"] == "none"
    assert after_second_confirm["controller_truth_modified"] is False


def test_streamed_logic_authoring_session_c919_real_doc_raw_intake_advances_thr_idle_lock_release_queue():
    requirements_payload = _c919_etras_real_doc_streamed_requirements_payload()
    drawing_payload = _c919_etras_real_doc_thr_idle_lock_release_drawing_payload()
    first = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)
    first_proposal = first["active_proposal"]
    feedback_text = "慢车锁释放说明应写明这是展开确认候选链路，不是 Deploy CMD1 的直接布尔门限。"
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": feedback_text,
        "requirements_document_edit_requested": True,
        "requirements_document_edit_authorized": True,
        "requirements_document_authorization_phrase": "AUTHORIZE_REQUIREMENTS_EDIT",
        "requirements_document_patch": {
            "operation": "candidate_requirements_text_revision",
            "target": "requirements_document",
            "proposed_text_zh": feedback_text,
        },
    }
    revised = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[revision_decision],
    )
    revised_proposal = revised["active_proposal"]
    after_revised_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
        ],
    )
    next_node = after_revised_confirm["active_proposal"]
    after_second_confirm = build_streamed_logic_authoring_session(
        requirements_payload,
        drawing_payload,
        decision_history=[
            revision_decision,
            _streamed_decision(revised, revised_proposal, "confirm"),
            _streamed_decision(after_revised_confirm, next_node, "confirm"),
        ],
    )

    assert first["m21_mode"] == "engineer_in_the_loop_streamed_authoring"
    assert first_proposal["target_id"] == "deploy_cmd1_active"
    assert "C919-V09-DEPLOY-CMD1-OUTPUT" in first_proposal["source_anchor_ids"]
    assert "FADEC_Deploy_Command = deploy_cmd1_active" in first_proposal["source_excerpt"]
    assert revised["active_proposal"]["proposal_status"] == "revised_proposal_ready"
    assert after_revised_confirm["requirements_document_edit"]["status"] == "authorized_candidate_patch"
    assert after_revised_confirm["requirements_document_edit"]["requirements_document_modified"] is False
    assert after_revised_confirm["candidate_queue"]["active_target_key"] == "node:thr_idle_lock_release"
    assert after_revised_confirm["active_proposal"]["target_id"] == "thr_idle_lock_release"
    assert after_second_confirm["active_proposal"]["target_type"] == "wire"
    assert after_second_confirm["active_proposal"]["target_id"] == "deploy_cmd1_active->thr_idle_lock_release"
    assert "C919-V09-THR-IDLE-OUTPUT" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-THR-IDLE-TR-DEPLOYED" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-THR-IDLE-POS-CONF" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "C919-V09-DEPLOY-CMD1-OUTPUT" in after_second_confirm["active_proposal"]["source_anchor_ids"]
    assert "`thr_idle_lock_release`" in after_second_confirm["active_proposal"]["source_excerpt"]
    assert after_second_confirm["candidate_queue"]["accepted_count"] == 2
    assert after_second_confirm["candidate_queue"]["pending_count"] == 1
    assert after_second_confirm["truth_effect"] == "none"
    assert after_second_confirm["controller_truth_modified"] is False


def test_streamed_logic_authoring_session_accepts_c919_etras_style_candidate_without_truth_promotion():
    requirements_payload = {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "summary_zh": "C919 ETRAS 候选链路已解析。",
        "open_questions": [],
        "concept_logic_nodes": [
            {
                "id": "wow_valid",
                "label": "WOW 有效",
                "node_kind": "input",
                "description_zh": "双通道地面信号一致。",
                "source_anchors": [
                    {
                        "id": "C919-ETRAS-WOW",
                        "kind": "需求条款",
                        "origin": "c919_etras_doc",
                        "quote_zh": "当 WOW 双通道有效且反推手柄进入解锁区间时，ETRAS 可进入预位。",
                    }
                ],
            },
            {"id": "etras_armed", "label": "ETRAS 预位", "node_kind": "logic", "description_zh": "反推预位候选逻辑。"},
        ],
        "concept_edges": [
            {
                "id": "c919_e1",
                "source": "wow_valid",
                "target": "etras_armed",
                "label": "WOW gating",
            }
        ],
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }
    drawing_payload = {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "summary_zh": "C919 ETRAS 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "wow_valid",
                "label": "WOW 有效",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 180,
                "height": 96,
                "description_zh": "双通道地面信号一致。",
            },
            {
                "id": "etras_armed",
                "label": "ETRAS 预位",
                "node_kind": "logic",
                "x": 420,
                "y": 120,
                "width": 190,
                "height": 104,
                "description_zh": "反推预位候选逻辑。",
            },
        ],
        "edges": [{"id": "c919_edge", "source": "wow_valid", "target": "etras_armed", "label": "WOW gating"}],
        "parameter_panels": [],
        "drawing_notes": [],
    }

    result = build_streamed_logic_authoring_session(requirements_payload, drawing_payload)

    assert result["m21_mode"] == "engineer_in_the_loop_streamed_authoring"
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False
    assert result["certification_claim"] == "none"
    assert result["active_proposal"]["target_id"] == "wow_valid"
    assert result["active_proposal"]["source_anchor_ids"] == ["C919-ETRAS-WOW"]
    assert "WOW 双通道有效" in result["active_proposal"]["source_excerpt"]


def test_demo_server_streamed_logic_authoring_endpoint_returns_candidate_proposal():
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/streamed-authoring/proposal",
            {
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "decision_history": [],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-streamed-logic-authoring-session"
    assert payload["status"] == "awaiting_user_confirmation"
    assert payload["active_proposal"]["requires_user_confirmation"] is True
    assert payload["m21_mode"] == "engineer_in_the_loop_streamed_authoring"


def test_demo_server_streamed_logic_authoring_endpoint_uses_natural_language_prompt():
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/streamed-authoring/proposal",
            {
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "decision_history": [],
                "natural_language_prompt": "请优先调整 L1 节点",
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["active_proposal"]["target_type"] == "node"
    assert payload["active_proposal"]["target_id"] == "L1"
    assert payload["candidate_queue"]["active_target_key"] == "node:L1"


def test_demo_server_streamed_logic_authoring_endpoint_rejects_invalid_natural_language_prompt():
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/streamed-authoring/proposal",
            {
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "natural_language_prompt": {"text": "L1"},
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 400
    assert payload["error"] == "invalid_natural_language_prompt"
    assert payload["field"] == "natural_language_prompt"


def test_demo_server_streamed_logic_authoring_endpoint_returns_replay_after_confirm():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/streamed-authoring/proposal",
            {
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "decision_history": [
                    {
                        **_streamed_decision(first, first_proposal, "confirm"),
                    }
                ],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["stream_replay"][0]["event_type"] == "candidate_edit_committed"
    assert payload["stream_replay"][0]["committed"] is True
    assert payload["committed_candidate_graph"]["committed_edit_count"] == 1
    assert payload["committed_candidate_graph"]["truth_effect"] == "none"
    assert payload["committed_candidate_graph"]["controller_truth_modified"] is False


def test_demo_server_streamed_logic_authoring_endpoint_advances_after_revised_confirm():
    first = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
    )
    first_proposal = first["active_proposal"]
    revision_decision = {
        **_streamed_decision(first, first_proposal, "request_revision"),
        "feedback_text": "RA 节点说明应写明这是候选解释。",
    }
    revised = build_streamed_logic_authoring_session(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        decision_history=[revision_decision],
    )
    confirm_revised = _streamed_decision(revised, revised["active_proposal"], "confirm")
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/streamed-authoring/proposal",
            {
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "decision_history": [revision_decision, confirm_revised],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["stream_replay"][0]["event_type"] == "candidate_edit_revision_requested"
    assert payload["stream_replay"][1]["event_type"] == "candidate_edit_committed"
    assert payload["stream_replay"][1]["confirmed_revision_of"] == first_proposal["id"]
    assert payload["committed_candidate_graph"]["committed_edit_ids"] == [
        revised["active_proposal"]["id"]
    ]
    assert payload["candidate_queue"]["active_target_key"] == "node:L1"
    assert payload["candidate_queue"]["active_sequence_index"] == 2
    assert payload["candidate_queue"]["can_continue_after_revision"] is True
    assert payload["active_proposal"]["target_id"] == "L1"
    assert payload["truth_effect"] == "none"
    assert payload["controller_truth_modified"] is False


def test_logic_builder_static_page_exposes_streamed_authoring_controls():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    js = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")
    css = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    revision_gate = (
        REPO_ROOT / "scripts" / "verify_m21_streamed_authoring_revision_browser_gate.py"
    ).read_text(encoding="utf-8")
    closeout_script = (
        REPO_ROOT / "scripts" / "run_customer_demo_mvp_closeout.py"
    ).read_text(encoding="utf-8")
    owner_packet_script = (
        REPO_ROOT / "scripts" / "run_project_owner_acceptance_review_packet.py"
    ).read_text(encoding="utf-8")
    closeout_doc = (
        REPO_ROOT / "docs" / "coordination" / "customer-demo-mvp-closeout.md"
    ).read_text(encoding="utf-8")
    owner_packet_doc = (
        REPO_ROOT / "docs" / "coordination" / "project-owner-acceptance-review-packet.md"
    ).read_text(encoding="utf-8")

    assert "logic-streamed-authoring-panel" in html
    assert 'data-demo-html-aesthetic-reference="src/well_harness/static/demo.html#fan-chain-svg"' in html
    assert 'data-demo-canvas-reference="src/well_harness/static/demo.html#fan-chain-svg"' in html
    assert 'data-canvas-visual-contract="demo-html-chain-svg"' in html
    assert 'data-default-display="logic-circuit-only"' in html
    assert 'data-console-palette="codex-light"' in html
    assert 'id="logic-streamed-panel-toggle"' in html
    assert 'id="logic-presentation-mode-toggle"' in html
    assert 'id="logic-presentation-controls"' in html
    assert 'data-presentation-mode="workbench"' in html
    assert 'data-logic-interaction-mode="natural-language"' in html
    assert 'data-workbench-input-model="natural-language"' in html
    assert 'id="logic-natural-language-control"' in html
    assert 'id="logic-natural-language-input"' in html
    assert 'id="logic-natural-language-send"' in html
    assert 'data-natural-language-step-confirmation="waiting"' in html
    assert 'data-panel-visibility="collapsed"' in html
    assert "logic-streamed-confirm" in html
    assert "logic-streamed-feedback" in html
    assert 'id="logic-streamed-revision-receipt"' in html
    assert 'id="logic-streamed-revision-status"' in html
    assert 'id="logic-streamed-revision-feedback"' in html
    assert "logic-streamed-queue" in html
    assert 'data-stream-replay="ordered-confirmed-edits"' in html
    assert 'data-m21-gate-summary="dual-gate"' in html
    assert 'data-m21-gate="candidate-recalc"' in html
    assert 'data-m21-gate="requirements-doc"' in html
    assert 'data-gate-status="locked"' in html
    assert "确认候选，不写需求" in html
    assert "反馈后重算候选" in html
    assert "不会写入真实控制器" in html
    assert "不会写入真实控制器" in js
    assert "controller.py" not in html
    assert "controller.py" not in js
    assert "/api/requirements-intake/streamed-authoring/proposal" in js
    assert "is-streamed-authoring-active" in js
    assert "stream_replay" in js
    assert "candidate_edit_committed" in js
    assert "candidate_edit_revision_requested" in js
    assert "requirements_document_patch_status" in js
    assert "requirements_document_patch_sha256" in js
    assert "committed_candidate_graph" in js
    assert "candidate_queue" in js
    assert "syncStreamedAuthoringQueue" in js
    assert "dataset.activeTargetKey" in js
    assert "dataset.proposalStatus" in js
    assert "source_requirements_sha256" in js
    assert "source_drawing_sha256" in js
    assert "streamedAuthoringInFlight" in js
    assert "requirements_document_edit_authorized" in js
    assert "setStreamedAuthoringPanelVisibility" in js
    assert "setLogicPresentationMode" in js
    assert "logicPresentationModeToggle" in js
    assert "naturalLanguageInput" in js
    assert "handleNaturalLanguageSubmit" in js
    assert "handleNaturalLanguageStreamedAuthoringSubmit" in js
    assert "streamedAuthoringLaunchPrompt" in js
    assert "natural_language_prompt" in js
    assert "dataset.launchSource = \"natural-language\"" in js
    assert "dataset.naturalLanguageConfirmation" in js
    assert "dataset.revisionFlow" in js
    assert "dataset.feedbackRevisionState" in js
    assert "feedback_applied" in js
    assert "dataset.sourceHighlight = \"active\"" in js
    assert "dataset.logicHighlight = \"active\"" in js
    assert "document.body.dataset.logicPresentationMode" in js
    assert "--logic-presentation-zoom" in js
    assert ".slice(-5)" not in js
    assert ".is-streamed-authoring-active" in css
    assert ".logic-streamed-history [data-stream-replay-event]" in css
    assert ".logic-streamed-revision-receipt" in css
    assert ".logic-streamed-queue" in css
    assert '[data-candidate-queue-status="candidate_queue_active"]' in css
    assert '[data-requirements-patch-status="authorized_candidate_patch"]' in css
    assert ".logic-streamed-authoring-panel[data-demo-html-aesthetic-reference]" in css
    assert ".logic-streamed-gates" in css
    assert '[data-gate-status="locked"]' in css
    assert '.logic-canvas[data-canvas-visual-contract="demo-html-chain-svg"]' in css
    assert ".logic-canvas[data-canvas-visual-contract=\"demo-html-chain-svg\"] .logic-node" in css
    assert ".logic-canvas[data-canvas-visual-contract=\"demo-html-chain-svg\"] .logic-wire" in css
    assert ".logic-canvas[data-canvas-visual-contract=\"demo-html-chain-svg\"] .logic-junction" in css
    assert "var(--logic-demo-chain-bg)" in css
    assert "stroke-linejoin: miter;" in css
    assert "stroke-linecap: butt;" in css
    assert 'font-family: "Courier New", monospace;' in css
    assert "logic-demo-chain-arrow-idle" in js
    assert 'polyline.setAttribute("marker-end", "url(#logic-demo-chain-arrow-idle)")' in js
    assert 'element.dataset.defaultDetail = "hidden"' in js
    assert '<div class="logic-node-desc">' not in js
    assert '<div class="logic-node-anchor">' not in js
    assert "<code>${escapeText(node.id)}</code>" not in js
    assert "label.textContent = sourceAnchorLabel(anchorsForEdge(edge))" not in js
    assert "renderEdgeJunctions" in js
    assert 'dot.classList.add("logic-junction")' in js
    assert 'dot.classList.add("logic-endpoint-dot")' not in js
    assert '--logic-bg: #f7f8fb' in css
    assert '.logic-shell[data-console-palette="codex-light"] .logic-streamed-authoring-panel' in css
    assert 'body[data-logic-presentation-mode="circuit-only"] .unified-nav' in css
    assert 'body[data-logic-presentation-mode="circuit-only"] #logic-page-system-strip' in css
    assert 'body[data-logic-presentation-mode="circuit-only"] .logic-inspector' in css
    assert 'body[data-logic-presentation-mode="circuit-only"] #logic-bottom-run-strip' in css
    assert 'body[data-logic-presentation-mode="circuit-only"] #logic-presentation-controls' in css
    assert 'body[data-logic-interaction-mode="natural-language"] .unified-nav' in css
    assert 'body[data-logic-interaction-mode="natural-language"] #logic-page-system-strip' in css
    assert 'body[data-logic-interaction-mode="natural-language"] .logic-inspector' in css
    assert 'body[data-logic-interaction-mode="natural-language"] #logic-command-palette-open' in css
    assert 'body[data-logic-interaction-mode="natural-language"] #logic-mode-dock' in css
    assert 'body[data-logic-interaction-mode="natural-language"] #logic-bottom-run-strip' in css
    assert ".logic-natural-language-control" in css
    assert 'background: rgba(255,255,255,0.96)' in css
    assert (
        'body[data-logic-interaction-mode="natural-language"] '
        '.logic-shell[data-blueprint-phase="phase-1-shell"] .logic-canvas-wrap'
    ) in css
    assert (
        'body[data-logic-interaction-mode="natural-language"] '
        '.logic-shell[data-blueprint-phase="phase-1-shell"] .logic-layout'
    ) in css
    assert "minmax(420px, 1fr)" in css
    assert "m21-streamed-authoring-revision-gate" in makefile
    assert "m21-streamed-authoring-multistep-queue-gate" in makefile
    assert "m21-streamed-authoring-c919-queue-gate" in makefile
    assert "m21-streamed-authoring-c919-raw-intake-gate" in makefile
    assert "m21-streamed-authoring-c919-real-doc-raw-intake-gate" in makefile
    assert "m21-streamed-authoring-c919-cmd3-apwtla-real-doc-raw-intake-gate" in makefile
    assert "m21-streamed-authoring-c919-deploy-cmd1-real-doc-raw-intake-gate" in makefile
    assert "m21-streamed-authoring-c919-deploy-cmd1-thr-idle-lock-release-real-doc-raw-intake-gate" in makefile
    assert "m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate" in makefile
    assert "m21-streamed-authoring-demo-fanout-junction-gate" in makefile
    assert "M21_STREAMED_AUTHORING_REVISION_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_MULTISTEP_QUEUE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_QUEUE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_RAW_INTAKE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_CMD3_APWTLA_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_DEPLOY_CMD1_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_DEPLOY_CMD1_THR_IDLE_LOCK_RELEASE_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_C919_MLG_WOW_CMD2_CMD3_FANOUT_REAL_DOC_RAW_INTAKE_GATE_ARTIFACT_DIR" in makefile
    assert "M21_STREAMED_AUTHORING_DEMO_FANOUT_JUNCTION_GATE_ARTIFACT_DIR" in makefile
    assert "--scenario c919_etras" in makefile
    assert "--scenario c919_etras_raw_intake" in makefile
    assert "--scenario c919_etras_real_doc_raw_intake" in makefile
    assert "--scenario c919_etras_cmd3_apwtla_real_doc_raw_intake" in makefile
    assert "--scenario c919_etras_deploy_cmd1_real_doc_raw_intake" in makefile
    assert "--scenario c919_etras_deploy_cmd1_thr_idle_lock_release_real_doc_raw_intake" in makefile
    assert "--scenario c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake" in makefile
    assert "--scenario fantui_demo_fanout_junction" in makefile
    test_target_line = next(line for line in makefile.splitlines() if line.startswith("test: "))
    assert "m21-streamed-authoring-c919-queue-gate" in test_target_line
    assert "m21-streamed-authoring-c919-raw-intake-gate" in test_target_line
    assert "m21-streamed-authoring-c919-real-doc-raw-intake-gate" in test_target_line
    assert "m21-streamed-authoring-c919-cmd3-apwtla-real-doc-raw-intake-gate" not in test_target_line
    assert "m21-streamed-authoring-c919-deploy-cmd1-real-doc-raw-intake-gate" not in test_target_line
    assert "m21-streamed-authoring-c919-deploy-cmd1-thr-idle-lock-release-real-doc-raw-intake-gate" not in test_target_line
    assert "m21-streamed-authoring-c919-mlg-wow-cmd2-cmd3-fanout-real-doc-raw-intake-gate" not in test_target_line
    assert "m21-streamed-authoring-demo-fanout-junction-gate" not in test_target_line
    assert "verify_m21_streamed_authoring_revision_browser_gate.py --format json" in makefile
    assert "c919_etras" in revision_gate
    assert "c919_etras_raw_intake" in revision_gate
    assert "c919_etras_real_doc_raw_intake" in revision_gate
    assert "c919_etras_cmd3_apwtla_real_doc_raw_intake" in revision_gate
    assert "c919_etras_deploy_cmd1_real_doc_raw_intake" in revision_gate
    assert "c919_etras_deploy_cmd1_thr_idle_lock_release_real_doc_raw_intake" in revision_gate
    assert "c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake" in revision_gate
    assert "c919_v09_mlg_wow_fanout" in revision_gate
    assert "fantui_demo_fanout_junction" in revision_gate
    assert "requires_fanout_junction" in revision_gate
    assert "expected_chain_junction_count" in revision_gate
    assert "fanout_junction_contract" in revision_gate
    assert "confirm_until_active_target_key" in revision_gate
    assert "requirements_v0_9.md" in revision_gate
    assert "mlg_wow" in revision_gate
    assert "cmd2_active" in revision_gate
    assert "apwtla" in revision_gate
    assert "cmd3_output" in revision_gate
    assert "deploy_cmd1_active" in revision_gate
    assert "thr_idle_lock_release" in revision_gate
    assert "demo_html_canvas_contract" in revision_gate
    assert "circuit_only_default_display_contract" in revision_gate
    assert "streamed_panel_collapsed_for_screenshot_contract" in revision_gate
    assert "pure_canvas_presentation_contract" in revision_gate
    assert "presentation_mode_for_screenshot" in revision_gate
    assert "unified_nav_display_for_presentation" in revision_gate
    assert "system_strip_display_for_presentation" in revision_gate
    assert "bottom_run_strip_display_for_presentation" in revision_gate
    assert "presentation_controls_display_for_screenshot" in revision_gate
    assert "pure_canvas_framing_contract" in revision_gate
    assert "presentation_scale_for_screenshot" in revision_gate
    assert "presentation_offset_x_for_screenshot" in revision_gate
    assert "presentation_offset_y_for_screenshot" in revision_gate
    assert "natural_language_workbench_contract" in revision_gate
    assert "natural_language_visible_button_count" in revision_gate
    assert "natural_language_input_visible" in revision_gate
    assert "natural_language_command_trigger_display" in revision_gate
    assert "natural_language_streamed_confirmation_contract" in revision_gate
    assert "one_candidate_per_natural_language_submit_contract" in revision_gate
    assert "natural_language_streamed_highlight_count" in revision_gate
    assert "natural_language_streamed_source_highlight" in revision_gate
    assert "natural_language_streamed_launch_source" in revision_gate
    assert "natural_language_canvas_height_after_submit" in revision_gate
    assert "natural_language_active_target_visible_in_canvas" in revision_gate
    assert "natural_language_active_target_hit_test_visible" in revision_gate
    assert "natural_language_step_screenshot_clip" in revision_gate
    assert "natural_language_step_visual_framing_contract" in revision_gate
    assert "natural_language_step_confirmation_screenshot" in revision_gate
    assert "step_confirmation_screenshot" in revision_gate
    assert "feedback_revision_frontstage_contract" in revision_gate
    assert "feedback_revision_confirmation_screenshot" in revision_gate
    assert "revision_confirmation_screenshot" in revision_gate
    assert "feedback_revision_panel_flow" in revision_gate
    assert "feedback_revision_feedback_matches" in revision_gate
    assert "feedback_revision_active_target_hit_test_visible" in revision_gate
    assert "streamed_panel_visibility_for_screenshot" in revision_gate
    assert "streamed_panel_display_for_screenshot" in revision_gate
    assert "reconstruction_panel_display_for_screenshot" in revision_gate
    assert "annotation_submit_bar_display_for_screenshot" in revision_gate
    assert "demo_canvas_reference" in revision_gate
    assert "canvas_visual_contract" in revision_gate
    assert "canvas_default_display" in revision_gate
    assert "chain_wire_visible_label_count" in revision_gate
    assert "chain_node_code_count" in revision_gate
    assert "chain_node_desc_count" in revision_gate
    assert "chain_node_anchor_count" in revision_gate
    assert "chain_wire_linejoin" in revision_gate
    assert "chain_node_font_family" in revision_gate
    assert "chain_wire_marker_end" in revision_gate
    assert "chain_wire_count" in revision_gate
    assert "chain_wires_with_marker_count" in revision_gate
    assert "chain_wire_marker_end_values" in revision_gate
    assert "all_wires_marker_contract" in revision_gate
    assert "m21_logic_circuit_presentation" in closeout_script
    assert "m21_pure_canvas_acceptance" in closeout_script
    assert "m21_c919_pure_canvas_gate" in closeout_script
    assert "m21_demo_fanout_pure_canvas_gate" in closeout_script
    assert "pure_canvas_presentation_contract" in closeout_script
    assert "pure_canvas_framing_contract" in closeout_script
    assert "m21_pure_canvas_evidence" in owner_packet_script
    assert "M21 Pure Canvas Evidence" in closeout_doc
    assert "M21 Pure Canvas Evidence" in owner_packet_doc
    assert "default-display: logic-circuit-only" in closeout_doc
    assert "pure_canvas_presentation_contract" in owner_packet_doc
    assert "chain_arrow_marker_count" in revision_gate
    assert "chain_endpoint_dot_count" in revision_gate
    assert "chain_unclassified_circle_count" in revision_gate
    assert "chain_junction_count" in revision_gate
    assert "CMD2 ground gate" in revision_gate
    assert "CMD3 ground gate" in revision_gate
    assert "C919-V09-CMD2-MLG-WOW" in revision_gate
    assert "C919-V09-CMD3" in revision_gate
    assert "SW2 set gate" in revision_gate
    assert "Deploy CMD1 evaluation after CMD3" in revision_gate
    assert "TR deployed confirmation" in revision_gate
    assert "TRCU power before deploy" in revision_gate
    assert "C919-V09-CMD3-SET-APWTLA" in revision_gate
    assert "C919-V09-CMD3-SR-OUTPUT" in revision_gate
    assert "C919-V09-CMD3-RESET-PRIORITY" in revision_gate
    assert "C919-V09-DEPLOY-CMD1-OUTPUT" in revision_gate
    assert "C919-V09-DEPLOY-CMD1-LOCKS" in revision_gate
    assert "C919-V09-DEPLOY-CMD1-TR-WOW" in revision_gate
    assert "C919-V09-DEPLOY-CMD1-N1K" in revision_gate
    assert "C919-V09-DEPLOY-CMD1-TRA" in revision_gate
    assert "C919-V09-EVAL-DEPLOY-CMD1" in revision_gate
    assert "C919-V09-THR-IDLE-OUTPUT" in revision_gate
    assert "C919-V09-THR-IDLE-TR-DEPLOYED" in revision_gate
    assert "C919-V09-THR-IDLE-POS-CONF" in revision_gate
    assert "C919-V09-EVAL-THR-IDLE-LOCK" in revision_gate
    assert "C919-V09-ACCEPT-THR-IDLE-LOCK" in revision_gate
    assert "requirement_anchor_ids" in revision_gate
    assert "requirement_edge_ids" in revision_gate
    assert "drawing_from_raw_preparse" in revision_gate
    assert "raw_preparse_payload" in revision_gate
    assert "raw_preparse_payload_artifact" in revision_gate
    assert "raw_preparse_payload_sha256" in revision_gate
    assert "drawing_source_requirements_sha256" in revision_gate
    assert "/api/requirements-intake/local-preparse" in revision_gate
    assert "endpoint_http_status" in revision_gate
    assert "raw_intake_payload" in revision_gate
    assert "c919_etras_rule_preparse" in revision_gate
    assert "c919_etras_v09_rule_preparse" in revision_gate
    assert "C919-ETRAS-WOW" in revision_gate
    assert "scenario_fixture" in revision_gate
    assert "server_revision_candidate" in revision_gate
    assert "server_requirements_patch_authorized" in revision_gate
    assert "revised_candidate_confirmed" in revision_gate
    assert "multi_step_queue_advance" in revision_gate
    assert "restricted_diff_after" in revision_gate
    assert "requirements_document_diff_after" in revision_gate
    assert '"docs/c919_etras"' in revision_gate
    assert "docs/thrust_reverser/requirements_supplement.md" in revision_gate
    panel_html = html[html.index("logic-streamed-authoring-panel"):html.index("logic-annotation-popover")]
    assert 'data-state="active"' not in panel_html


def test_update_logic_drawing_calls_model_for_full_updated_drawing(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}
    requirements_payload = _ready_requirements_payload()
    interpretation = {
        "kind": "ai-fantui-logic-change-interpretation",
        "version": 1,
        "status": "confirmed_by_user",
        "target_node_id": "RA",
        "annotation_text": "选中 RA 节点，把高度门限改成 7ft。",
        "understanding_zh": "用户希望把 RA 放行门限从 6ft 调整为 7ft。",
        "requirements_match_zh": "原需求中 RA<6ft 是 L1 的输入条件。",
        "affected_nodes": ["RA", "L1"],
        "affected_edges": ["edge_ra_l1"],
        "affected_parameter_panels": ["panel_ra"],
        "proposed_changes": ["更新 RA 节点描述和参数面板默认值。"],
    }

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "summary_zh": "已按确认意见更新 RA 门限。",
                "canvas": {"width": 1280, "height": 760},
                "nodes": [
                    {
                        "id": "RA",
                        "label": "无线电高度",
                        "node_kind": "input",
                        "x": 80,
                        "y": 120,
                        "width": 180,
                        "height": 96,
                        "description_zh": "RA<7ft",
                    },
                    {
                        "id": "L1",
                        "label": "逻辑1",
                        "node_kind": "logic",
                        "x": 420,
                        "y": 120,
                        "width": 190,
                        "height": 104,
                        "description_zh": "TLS解锁",
                    },
                ],
                "edges": [
                    {
                        "id": "edge_ra_l1",
                        "source": "RA",
                        "target": "L1",
                        "label": "高度<7ft",
                        "route": [{"x": 260, "y": 168}, {"x": 420, "y": 168}],
                    }
                ],
                "parameter_panels": [
                    {
                        "id": "panel_ra",
                        "node_id": "RA",
                        "label": "RA阈值",
                        "unit": "ft",
                        "min": 0,
                        "max": 20,
                        "default": 7,
                        "x": 276,
                        "y": 120,
                        "width": 150,
                        "height": 76,
                    }
                ],
                "drawing_notes": ["用户确认后，模型重绘了受影响链路。"],
            }
        )

    result = update_logic_drawing(
        _ready_drawing_payload(),
        interpretation,
        requirements_payload=requirements_payload,
        provider="deepseek",
        request_post=fake_post,
    )

    prompt = captured["body"]["messages"][1]["content"]
    assert "返回完整更新后的逻辑链路绘制 JSON" in prompt
    assert "confirmed_by_user" in prompt
    assert captured["body"]["max_tokens"] == 8192
    assert result["kind"] == "ai-fantui-logic-link-drawing"
    assert result["status"] == "draft_ready"
    assert result["nodes"][0]["description_zh"] == "RA<7ft"
    assert result["parameter_panels"][0]["default"] == 7.0
    assert result["source_requirements_sha256"] == _payload_sha256(requirements_payload)
    contracts = result["agent_output_contract_v0_1"]
    requirement_ids = {
        item["id"]
        for item in contracts["logic_ir"]["agent_output"]["payload"]["requirements"]
    }
    assert requirement_ids == {"REQ-DRAWING-STRUCTURE"}
    assert "REQ-UNSPECIFIED-CANDIDATE" not in requirement_ids
    assert result["change_applied"]["source_interpretation_sha256"]
    assert result["truth_effect"] == "none"


def test_prepare_fault_injection_calls_model_for_candidate_plan(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}
    change_history = [
        {
            "status": "updated",
            "target_node_id": "RA",
            "understanding_zh": "用户确认 RA 门限保持为 6ft。",
        }
    ]

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["url"] = url
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "summary_zh": "故障注入准备完成，优先覆盖 RA、SW1 和执行命令链路。",
                "assumptions": ["只生成候选，不执行仿真。"],
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 是 L1 关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    }
                ],
                "injection_points": [
                    {
                        "id": "point_ra",
                        "node_id": "RA",
                        "parameter_panel_id": "panel_ra",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_boundary_zh": "仅作为沙盒候选，不写入控制器。",
                    }
                ],
                "boundary_questions": [
                    {
                        "id": "boundary_ra_range",
                        "prompt_zh": "RA 故障候选的取值边界是否限制在 0-20ft？",
                        "rationale_zh": "边界会影响后续沙盒注入范围。",
                        "blocks": "fault_injection",
                    }
                ],
                "workflow_notes": ["下一步需要工程师确认边界后再进入沙盒故障注入。"],
            }
        )

    result = prepare_fault_injection(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        change_history=change_history,
        provider="deepseek",
        request_post=fake_post,
    )

    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    prompt = captured["body"]["messages"][1]["content"]
    assert "不要执行仿真" in captured["body"]["messages"][0]["content"]
    assert "change_history" in prompt
    assert "critical_fault_nodes" in prompt
    assert "必须覆盖 critical_fault_nodes 中列出的每一个 node_id" in prompt
    assert captured["body"]["max_tokens"] == 4096
    assert result["kind"] == "ai-fantui-fault-injection-preparation"
    assert result["status"] == "needs_user_confirmation"
    assert result["candidate_state"] == "fault_injection_preparation"
    assert result["source_drawing_sha256"]
    assert result["fault_scenarios"][0]["node_id"] == "RA"
    assert result["injection_points"][0]["parameter_panel_id"] == "panel_ra"
    assert result["boundary_questions"][0]["blocks"] == "fault_injection"
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False


def test_prepare_fault_injection_preserves_source_scope_and_candidate_anchors(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    requirements = _ready_requirements_payload()
    requirements["source_scope"] = {
        "fault_injection": {
            "status": "source_deferred",
            "reason_zh": "源文档声明暂不考虑故障注入。",
            "source_anchors": [{"id": "B47", "kind": "范围约束", "quote_zh": "故障注入目前暂时不考虑，很复杂。"}],
        }
    }
    drawing = _ready_drawing_payload()
    drawing["nodes"][0]["source_anchors"] = [
        {"id": "B38", "kind": "正文条件", "quote_zh": "RA<6ft。"}
    ]

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        return _model_response(
            {
                "summary_zh": "故障候选只作为 dry-run 扩展。",
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 是 L1 关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    }
                ],
                "injection_points": [],
                "boundary_questions": [],
            }
        )

    result = prepare_fault_injection(requirements, drawing, provider="deepseek", request_post=fake_post)

    assert result["source_scope"]["fault_injection"]["status"] == "source_deferred"
    assert result["fault_scenarios"][0]["source_anchors"][0]["id"] == "B38"
    assert result["fault_scenarios"][0]["provenance"] == "model_fault_candidate_from_source_node"


def test_prepare_fault_injection_completes_missing_critical_output_node(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    drawing = _ready_drawing_payload()
    drawing["nodes"].append(
        {
            "id": "THR_LOCK",
            "label": "油门锁释放",
            "node_kind": "output",
            "x": 720,
            "y": 120,
            "width": 190,
            "height": 104,
            "description_zh": "释放输出。",
        }
    )
    drawing["edges"].append(
        {
            "id": "edge_l1_thr",
            "source": "L1",
            "target": "THR_LOCK",
            "label": "释放命令",
            "route": [{"x": 610, "y": 168}, {"x": 720, "y": 168}],
        }
    )

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        return _model_response(
            {
                "summary_zh": "故障注入准备完成，但模型只覆盖 RA。",
                "assumptions": ["只生成候选，不执行仿真。"],
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 是关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    }
                ],
                "injection_points": [],
                "boundary_questions": [
                    {
                        "id": "boundary_ra_range",
                        "prompt_zh": "RA 故障候选的取值边界是否限制在 0-20ft？",
                        "rationale_zh": "边界会影响后续沙盒注入范围。",
                        "blocks": "fault_injection",
                    }
                ],
                "workflow_notes": ["下一步需要工程师确认边界。"],
            }
        )

    result = prepare_fault_injection(
        _ready_requirements_payload(),
        drawing,
        provider="deepseek",
        request_post=fake_post,
    )

    covered_nodes = {
        item["node_id"]
        for item in result["fault_scenarios"] + result["injection_points"]
    }
    assert "THR_LOCK" in covered_nodes
    assert result["coverage_completion"]["completed_node_ids"] == ["THR_LOCK"]
    assert result["coverage_completion"]["strategy"] == "deterministic_dry_run_candidate"


def test_prepare_fault_injection_self_repairs_when_fault_payload_incomplete(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls: list[dict] = []

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        calls.append(request)
        if len(calls) == 1:
            return _model_response(
                {
                    "summary_zh": "故障候选为空。",
                    "fault_scenarios": [],
                    "injection_points": [],
                    "boundary_questions": [],
                }
            )
        return _model_response(
            {
                "summary_zh": "故障注入准备已修复。",
                "assumptions": ["只生成候选，不执行仿真。"],
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 是 L1 关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    }
                ],
                "injection_points": [
                    {
                        "id": "point_ra",
                        "node_id": "RA",
                        "parameter_panel_id": "panel_ra",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_boundary_zh": "仅作为沙盒候选，不写入控制器。",
                    }
                ],
                "boundary_questions": [],
                "workflow_notes": ["自修复补齐故障场景。"],
            }
        )

    result = prepare_fault_injection(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        provider="deepseek",
        request_post=fake_post,
    )

    assert len(calls) == 2
    assert "修复" in calls[1]["messages"][0]["content"]
    assert "fault_scenarios" in calls[1]["messages"][1]["content"]
    assert result["fault_scenarios"][0]["id"] == "fault_ra_stuck_low"
    assert result["llm"]["self_repair"] == {
        "attempted": True,
        "success": True,
        "reason": "fault_injection_json_error",
    }


def test_prepare_fault_injection_completes_when_parameterized_node_is_missing(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls: list[dict] = []

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        calls.append(request)
        if len(calls) == 1:
            return _model_response(
                {
                    "summary_zh": "只覆盖 L1，漏掉 RA 参数节点。",
                    "fault_scenarios": [
                        {
                            "id": "fault_l1_logic",
                            "label": "L1 逻辑异常",
                            "node_id": "L1",
                            "fault_type": "logic_stuck",
                            "rationale_zh": "L1 是逻辑节点。",
                            "expected_effect_zh": "可能影响下游。",
                            "observable_signals": ["L1"],
                            "severity": "medium",
                        }
                    ],
                    "injection_points": [],
                    "boundary_questions": [],
                }
            )
        return _model_response(
            {
                "summary_zh": "已补齐 RA 参数节点。",
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 带参数面板，是关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    }
                ],
                "injection_points": [
                    {
                        "id": "point_ra",
                        "node_id": "RA",
                        "parameter_panel_id": "panel_ra",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_boundary_zh": "仅作为沙盒候选。",
                    }
                ],
                "boundary_questions": [],
            }
        )

    result = prepare_fault_injection(
        _ready_requirements_payload(),
        _ready_drawing_payload(),
        provider="deepseek",
        request_post=fake_post,
    )

    assert len(calls) == 1
    assert {item["node_id"] for item in result["fault_scenarios"]} == {"L1", "RA"}
    assert result["coverage_completion"] == {
        "strategy": "deterministic_dry_run_candidate",
        "completed_node_ids": ["RA"],
        "semantic_gate": "critical_node_coverage",
    }


def test_prepare_fault_injection_completes_when_output_node_is_missing(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    drawing = _ready_drawing_payload()
    drawing["nodes"] = [
        *drawing["nodes"],
        {
            "id": "OUT",
            "label": "放行输出",
            "node_kind": "output",
            "x": 680,
            "y": 120,
            "width": 180,
            "height": 96,
            "description_zh": "输出放行命令。",
        },
    ]
    calls: list[dict] = []

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        calls.append(request)
        if len(calls) == 1:
            return _model_response(
                {
                    "summary_zh": "只覆盖 RA 输入，漏掉输出节点。",
                    "fault_scenarios": [
                        {
                            "id": "fault_ra_stuck_low",
                            "label": "RA 卡滞低值",
                            "node_id": "RA",
                            "fault_type": "sensor_stuck_low",
                            "rationale_zh": "RA 是关键输入。",
                            "expected_effect_zh": "可能提前满足高度门限。",
                            "observable_signals": ["RA", "L1"],
                            "severity": "medium",
                        }
                    ],
                    "injection_points": [
                        {
                            "id": "point_ra",
                            "node_id": "RA",
                            "parameter_panel_id": "panel_ra",
                            "signal_name": "RA",
                            "injection_mode": "override_value",
                            "safe_boundary_zh": "仅作为沙盒候选。",
                        }
                    ],
                }
            )
        return _model_response(
            {
                "summary_zh": "已补齐输出节点。",
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 是关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    },
                    {
                        "id": "fault_out_blocked",
                        "label": "输出放行阻塞",
                        "node_id": "OUT",
                        "fault_type": "output_blocked",
                        "rationale_zh": "OUT 是最终输出。",
                        "expected_effect_zh": "可能无法释放放行命令。",
                        "observable_signals": ["OUT"],
                        "severity": "medium",
                    },
                ],
                "injection_points": [
                    {
                        "id": "point_ra",
                        "node_id": "RA",
                        "parameter_panel_id": "panel_ra",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_boundary_zh": "仅作为沙盒候选。",
                    }
                ],
            }
        )

    result = prepare_fault_injection(
        _ready_requirements_payload(),
        drawing,
        provider="deepseek",
        request_post=fake_post,
    )

    assert len(calls) == 1
    assert {item["node_id"] for item in result["fault_scenarios"]} == {"RA", "OUT"}
    assert result["coverage_completion"] == {
        "strategy": "deterministic_dry_run_candidate",
        "completed_node_ids": ["OUT"],
        "semantic_gate": "critical_node_coverage",
    }


def test_prepare_fault_injection_reports_parameter_panel_node_mismatch(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls = 0

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        nonlocal calls
        calls += 1
        return _model_response(
            {
                "summary_zh": "参数面板挂到了错误节点。",
                "fault_scenarios": [
                    {
                        "id": "fault_ra_stuck_low",
                        "label": "RA 卡滞低值",
                        "node_id": "RA",
                        "fault_type": "sensor_stuck_low",
                        "rationale_zh": "RA 是关键输入。",
                        "expected_effect_zh": "可能提前满足高度门限。",
                        "observable_signals": ["RA", "L1"],
                        "severity": "medium",
                    }
                ],
                "injection_points": [
                    {
                        "id": "point_wrong_panel",
                        "node_id": "L1",
                        "parameter_panel_id": "panel_ra",
                        "signal_name": "L1",
                        "injection_mode": "override_value",
                        "safe_boundary_zh": "错误地复用 RA 面板。",
                    }
                ],
            }
        )

    with pytest.raises(RequirementsIntakeError) as exc:
        prepare_fault_injection(
            _ready_requirements_payload(),
            _ready_drawing_payload(),
            provider="deepseek",
            request_post=fake_post,
        )

    assert calls == 2
    assert exc.value.code == "fault_injection_json_error"
    assert exc.value.details["self_repair"]["attempted"] is True
    repair_details = exc.value.details["self_repair"]["details"]
    assert repair_details["semantic_gate"] == "parameter_panel_node_match"
    assert repair_details["parameter_panel_id"] == "panel_ra"
    assert repair_details["expected_node_id"] == "RA"


def test_prepare_fault_injection_self_repair_failure_when_schema_still_invalid(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls = 0

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        nonlocal calls
        calls += 1
        return _model_response({"summary_zh": "仍然没有故障场景。", "fault_scenarios": []})

    with pytest.raises(RequirementsIntakeError) as exc:
        prepare_fault_injection(
            _ready_requirements_payload(),
            _ready_drawing_payload(),
            provider="deepseek",
            request_post=fake_post,
        )

    assert calls == 2
    assert exc.value.code == "fault_injection_json_error"
    assert exc.value.details["self_repair"]["attempted"] is True
    assert exc.value.details["self_repair"]["success"] is False
    assert exc.value.details["self_repair"]["error"] == "fault_injection_json_error"


def test_prepare_fault_injection_sandbox_plan_calls_model_for_dry_run_contract(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    captured: dict[str, object] = {}
    boundary_answers = [
        {
            "id": "boundary_ra_range",
            "prompt_zh": "RA 故障候选的取值边界是否限制在 0-20ft？",
            "answer_zh": "限制在 0-20ft，只用于沙盒。",
        }
    ]

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        captured["url"] = url
        captured["body"] = json.loads(body.decode("utf-8"))
        return _model_response(
            {
                "summary_zh": "沙盒注入配置建议已生成。",
                "sandbox_injection_plan": [
                    {
                        "id": "inject_ra_low",
                        "fault_scenario_id": "fault_ra_stuck_low",
                        "node_id": "RA",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_range_zh": "0-20ft",
                        "duration_ms": 2000,
                        "expected_effect_zh": "L1 高度门限判断被触发。",
                    }
                ],
                "observation_points": [
                    {
                        "id": "obs_l1",
                        "node_id": "L1",
                        "signal_name": "L1",
                        "check_zh": "观察 L1 是否因 RA 值变化而变化。",
                    }
                ],
                "review_checklist": [
                    {
                        "id": "chk_dry_run",
                        "category": "safety",
                        "condition_zh": "确认不调用真实仿真或控制接口。",
                        "pass_criteria_zh": "execution_contract.run_tick=false 且 dry_run_only=true。",
                    }
                ],
                "execution_contract": {
                    "run_tick": True,
                    "simulate": True,
                    "dry_run_only": False,
                },
                "workflow_notes": ["仅作为沙盒配置建议。"],
            }
        )

    result = prepare_fault_injection_sandbox_plan(
        _ready_fault_preparation_payload(),
        boundary_answers=boundary_answers,
        provider="deepseek",
        request_post=fake_post,
    )

    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    system_prompt = captured["body"]["messages"][0]["content"]
    user_prompt = captured["body"]["messages"][1]["content"]
    assert "不要调用 /api/tick" in system_prompt
    assert "boundary_answers" in user_prompt
    assert "必须覆盖 fault_scenarios 中的每一个 id" in user_prompt
    assert captured["body"]["max_tokens"] == 4096
    assert result["kind"] == "ai-fantui-fault-injection-sandbox-plan"
    assert result["status"] == "ready_for_review"
    assert result["candidate_state"] == "fault_injection_sandbox_plan"
    assert result["source_fault_injection_preparation_sha256"]
    assert result["sandbox_injection_plan"][0]["fault_scenario_id"] == "fault_ra_stuck_low"
    assert result["observation_points"][0]["signal_name"] == "L1"
    assert result["review_checklist"][0]["category"] == "safety"
    assert result["execution_contract"] == {
        "run_tick": False,
        "simulate": False,
        "dry_run_only": True,
    }
    assert result["truth_effect"] == "none"
    assert result["controller_truth_modified"] is False


def test_prepare_fault_injection_sandbox_plan_self_repairs_when_plan_incomplete(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls: list[dict] = []

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        calls.append(request)
        if len(calls) == 1:
            return _model_response(
                {
                    "summary_zh": "沙盒计划为空。",
                    "sandbox_injection_plan": [],
                    "observation_points": [],
                    "review_checklist": [],
                }
            )
        return _model_response(
            {
                "summary_zh": "沙盒注入配置建议已修复。",
                "sandbox_injection_plan": [
                    {
                        "id": "inject_ra_low",
                        "fault_scenario_id": "fault_ra_stuck_low",
                        "node_id": "RA",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_range_zh": "0-20ft",
                        "duration_ms": 2000,
                        "expected_effect_zh": "L1 高度门限判断被触发。",
                    }
                ],
                "observation_points": [],
                "review_checklist": [],
                "execution_contract": {"run_tick": True, "simulate": True, "dry_run_only": False},
                "workflow_notes": ["自修复补齐沙盒注入计划。"],
            }
        )

    result = prepare_fault_injection_sandbox_plan(
        _ready_fault_preparation_payload(),
        boundary_answers=_ready_fault_preparation_payload()["boundary_answers"],
        provider="deepseek",
        request_post=fake_post,
    )

    assert len(calls) == 2
    assert "修复" in calls[1]["messages"][0]["content"]
    assert "sandbox_injection_plan" in calls[1]["messages"][1]["content"]
    assert result["sandbox_injection_plan"][0]["id"] == "inject_ra_low"
    assert result["execution_contract"] == {"run_tick": False, "simulate": False, "dry_run_only": True}
    assert result["llm"]["self_repair"] == {
        "attempted": True,
        "success": True,
        "reason": "fault_injection_sandbox_json_error",
    }


def test_prepare_fault_injection_sandbox_plan_completes_missing_scenario_plan(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    preparation = _ready_fault_preparation_payload()
    preparation["fault_scenarios"] = [
        *preparation["fault_scenarios"],
        {
            "id": "auto_fault_thr_lock_release",
            "label": "反推锁释放覆盖候选",
            "node_id": "THR_LOCK",
            "fault_type": "dry_run_observation_gap",
            "rationale_zh": "反推锁释放是自动补齐的关键输出节点。",
            "expected_effect_zh": "可能阻塞下游放行。",
            "observable_signals": ["THR_LOCK"],
            "severity": "medium",
        },
    ]
    calls: list[dict] = []

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        request = json.loads(body.decode("utf-8"))
        calls.append(request)
        return _model_response(
            {
                "summary_zh": "只为 RA 生成沙盒计划。",
                "sandbox_injection_plan": [
                    {
                        "id": "inject_ra_low",
                        "fault_scenario_id": "fault_ra_stuck_low",
                        "node_id": "RA",
                        "signal_name": "RA",
                        "injection_mode": "override_value",
                        "safe_range_zh": "0-20ft",
                        "duration_ms": 2000,
                        "expected_effect_zh": "L1 高度门限判断被触发。",
                    }
                ],
                "observation_points": [],
                "review_checklist": [],
            }
        )

    result = prepare_fault_injection_sandbox_plan(
        preparation,
        boundary_answers=preparation["boundary_answers"],
        provider="deepseek",
        request_post=fake_post,
    )

    assert len(calls) == 1
    assert {item["fault_scenario_id"] for item in result["sandbox_injection_plan"]} == {
        "fault_ra_stuck_low",
        "auto_fault_thr_lock_release",
    }
    completed = result["plan_coverage_completion"]
    assert completed == {
        "strategy": "deterministic_dry_run_plan",
        "completed_fault_scenario_ids": ["auto_fault_thr_lock_release"],
        "semantic_gate": "scenario_plan_coverage",
    }
    auto_plan = [item for item in result["sandbox_injection_plan"] if item["fault_scenario_id"] == "auto_fault_thr_lock_release"][0]
    assert auto_plan["node_id"] == "THR_LOCK"
    assert auto_plan["injection_mode"] == "dry_run_observe"


def test_prepare_fault_injection_sandbox_plan_self_repair_failure(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")
    calls = 0

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        nonlocal calls
        calls += 1
        return _model_response({"summary_zh": "仍然没有沙盒计划。", "sandbox_injection_plan": []})

    with pytest.raises(RequirementsIntakeError) as exc:
        prepare_fault_injection_sandbox_plan(
            _ready_fault_preparation_payload(),
            boundary_answers=_ready_fault_preparation_payload()["boundary_answers"],
            provider="deepseek",
            request_post=fake_post,
        )

    assert calls == 2
    assert exc.value.code == "fault_injection_sandbox_json_error"
    assert exc.value.details["self_repair"]["attempted"] is True
    assert exc.value.details["self_repair"]["success"] is False
    assert exc.value.details["self_repair"]["error"] == "fault_injection_sandbox_json_error"


def _start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _post(server, path: str, body: dict):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
    conn.request("POST", path, body=json.dumps(body), headers={"Content-Type": "application/json"})
    response = conn.getresponse()
    payload = json.loads(response.read().decode("utf-8"))
    conn.close()
    return response.status, payload


def _get(server, path: str):
    conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
    conn.request("GET", path)
    response = conn.getresponse()
    payload = json.loads(response.read().decode("utf-8"))
    conn.close()
    return response.status, payload


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_logic_builder_candidate_review_packet_export_endpoint_serves_reference_packet():
    server, thread = _start_server()
    try:
        status, payload = _get(server, "/logic-builder/candidate-review-packet.json")
    finally:
        server.shutdown()
        server.server_close()

    assert status == 200
    validate_candidate_review_packet_export(payload)
    validate_candidate_review_packet(payload["review_packet"])
    assert payload["kind"] == "ai-fantui-candidate-review-packet-export"
    assert payload["exporter"]["source_route"] == "/logic-builder"
    assert payload["exporter"]["export_route"] == "/logic-builder/candidate-review-packet.json"
    assert payload["review_packet"]["summary"]["open_findings"] == [
        "CHECK_SAFETY_PRIORITY_001"
    ]
    assert payload["boundary"]["controller_truth_modified"] is False


def test_demo_server_deepseek_live_replay_endpoint_reads_artifacts(monkeypatch, tmp_path):
    artifact_dir = tmp_path / "deepseek-live-full-chain"
    artifact_dir.mkdir()
    _write_json(
        artifact_dir / "01_requirements_intake.json",
        {
            "kind": "ai-fantui-requirements-intake-analysis",
            "status": "ready_for_logic_builder",
            "concept_logic_nodes": [{"id": "ra"}, {"id": "tra"}],
            "concept_edges": [{"id": "ra_to_gate"}],
        },
    )
    _write_json(
        artifact_dir / "02_logic_drawing.json",
        {
            "kind": "ai-fantui-logic-link-drawing",
            "status": "draft_ready",
            "nodes": [{"id": "ra"}, {"id": "gate"}],
            "edges": [{"id": "edge"}],
            "parameter_panels": [{"id": "panel_ra"}],
        },
    )
    _write_json(
        artifact_dir / "03_fault_preparation.json",
        {
            "kind": "ai-fantui-fault-injection-preparation",
            "status": "needs_user_confirmation",
            "fault_scenarios": [{"id": "fault_ra"}],
            "injection_points": [{"id": "point_ra"}],
            "boundary_questions": [{"id": "dry_run", "prompt_zh": "确认只用于 dry-run？"}],
        },
    )
    _write_json(
        artifact_dir / "04_sandbox_plan.json",
        {
            "kind": "ai-fantui-fault-injection-sandbox-plan",
            "status": "ready_for_review",
            "sandbox_injection_plan": [{"id": "plan_ra"}],
            "observation_points": [{"id": "obs_ra"}],
            "review_checklist": [{"id": "chk_ra"}],
        },
    )
    _write_json(
        artifact_dir / "run_summary.json",
        {"ok": True, "model": "deepseek-v4-pro", "completed_at": "2026-05-13T10:30:00Z"},
    )
    monkeypatch.setattr(demo_server, "DEEPSEEK_LIVE_DEMO_ARTIFACT_DIR", artifact_dir)

    server, thread = _start_server()
    try:
        status, payload = _get(server, "/api/requirements-intake/deepseek-live-demo-replay")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-deepseek-live-demo-replay"
    assert payload["source"] == "artifacts/deepseek-live-full-chain"
    assert payload["requirements_payload"]["kind"] == "ai-fantui-requirements-intake-analysis"
    assert payload["drawing_payload"]["kind"] == "ai-fantui-logic-link-drawing"
    assert payload["fault_preparation_payload"]["kind"] == "ai-fantui-fault-injection-preparation"
    assert payload["sandbox_plan_payload"]["kind"] == "ai-fantui-fault-injection-sandbox-plan"
    assert payload["boundary_answers"][0]["id"] == "dry_run"
    assert payload["local_storage_keys"]["requirements"] == "ai-fantui-requirements-intake-ready-v1"
    assert payload["local_storage_keys"]["sandbox"] == "ai-fantui-fault-injection-sandbox-plan-v1"
    assert payload["replay_summary"]["model"] == "deepseek-v4-pro"
    assert payload["replay_summary"]["generated_at"] == "2026-05-13T10:30:00Z"
    assert payload["replay_summary"]["ok"] is True
    assert payload["replay_summary"]["stage_counts"] == [
        {"id": "requirements", "label_zh": "需求理解", "primary": 2, "secondary": 1, "summary_zh": "2 concepts / 1 edges"},
        {"id": "drawing", "label_zh": "逻辑图", "primary": 2, "secondary": 1, "summary_zh": "2 nodes / 1 edges / 1 panels"},
        {"id": "fault", "label_zh": "故障准备", "primary": 1, "secondary": 1, "summary_zh": "1 scenarios / 1 points / 1 questions"},
        {"id": "sandbox", "label_zh": "沙盒计划", "primary": 1, "secondary": 1, "summary_zh": "1 plans / 1 observations / 1 reviews"},
    ]
    assert "sk-" not in json.dumps(payload)


def test_deepseek_live_replay_payload_rebuilds_current_circuit_view_from_requirements(tmp_path):
    artifact_dir = tmp_path / "deepseek-live-full-chain"
    artifact_dir.mkdir()
    _write_json(artifact_dir / "01_requirements_intake.json", _l1_l4_requirements_payload_for_circuit())
    _write_json(
        artifact_dir / "02_logic_drawing.json",
        {
            "kind": "ai-fantui-logic-link-drawing",
            "status": "draft_ready",
            "summary_zh": "旧回放图纸缺少 deterministic circuit view。",
            "nodes": [{"id": "legacy_node"}],
            "edges": [],
            "parameter_panels": [],
        },
    )
    _write_json(
        artifact_dir / "03_fault_preparation.json",
        {
            "kind": "ai-fantui-fault-injection-preparation",
            "status": "source_deferred",
            "fault_scenarios": [],
            "injection_points": [],
            "boundary_questions": [],
        },
    )
    _write_json(
        artifact_dir / "04_sandbox_plan.json",
        {
            "kind": "ai-fantui-fault-injection-sandbox-plan",
            "status": "source_deferred",
            "sandbox_injection_plan": [],
            "observation_points": [],
            "review_checklist": [],
        },
    )
    _write_json(artifact_dir / "run_summary.json", {"ok": True, "model": "deepseek-v4-pro"})

    payload = demo_server.deepseek_live_demo_replay_payload(artifact_dir)

    drawing = payload["drawing_payload"]
    circuit = drawing["circuit_view"]
    nodes = {node["id"]: node for node in circuit["nodes"]}
    assert circuit["kind"] == "ai-fantui-l1-l4-circuit-view"
    assert len(circuit["nodes"]) == 20
    assert len(circuit["wires"]) == 23
    for node_id in ("radio_altitude_ft", "sw1", "sw2", "vdt90", "thr_lock"):
        assert nodes[node_id]["source_anchors"], node_id
        assert nodes[node_id]["provenance"] == "docx_body"
    assert payload["replay_summary"]["stage_counts"][1] == {
        "id": "drawing",
        "label_zh": "逻辑图",
        "primary": 20,
        "secondary": 23,
        "summary_zh": "20 circuit nodes / 23 wires",
    }


def test_demo_server_endpoint_returns_redacted_missing_key_payload():
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {"document_text": "RA 小于 6ft 时进入逻辑。", "provider": "deepseek"},
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 503
    assert payload["error"] == "missing_api_key"
    assert "sk-" not in json.dumps(payload)


def test_demo_server_local_preparse_endpoint_returns_l1_l4_without_llm_key():
    docx_text = "\n".join(
        [
            "工作逻辑1 L1：当 RA<6ft 且 SW1 进入 TRA [-1.4,-6.2] 区间，输出 TLS 115VAC。",
            "工作逻辑2 L2：当 SW2 有效且 TRA 区间满足时，输出 ETRAC 540VDC。",
            "工作逻辑3 L3：TLS/PLS 反馈满足后，驱动 PDU motor 并等待 VDT。",
            "工作逻辑4 L4：当 VDT 达到 90% deploy 且 TRA<=-11.74°，THR_LOCK release。",
            "故障注入目前暂时不考虑，很复杂。",
        ]
    )

    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/local-preparse",
            {
                "document_text": docx_text,
                "document_name": "control-logic.docx",
                "provider": "deepseek",
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["status"] == "ready_for_logic_builder"
    assert payload["ready_for_logic_builder"] is True
    assert payload["llm"]["provider"] == "local-preparse"
    assert payload["llm"]["response_source"] == "deterministic_preparse"
    assert payload["deterministic_preparse"]["applied"] is True
    assert payload["deterministic_preparse"]["reason"] == "local_preparse_first"
    nodes_by_id = {node["id"]: node for node in payload["concept_logic_nodes"]}
    for node_id in ("ra_lt_6ft", "sw2", "tra_reverse_range", "vdt_90"):
        assert nodes_by_id[node_id]["source_anchors"], node_id
        assert nodes_by_id[node_id]["provenance"] == "docx_body_condition"
    assert payload["source_scope"]["fault_injection"]["status"] == "source_deferred"
    assert "sk-" not in json.dumps(payload)


def test_local_preparse_anchors_real_docx_phrasing_for_ra_sw2_and_thr_lock():
    docx_text = "\n".join(
        [
            "SW1 和SW2 开关信号（0  1信号）",
            (
                "飞机离地小于6ft时，DIU发出TLS解锁指令（控制逻辑1）；飞机着陆后，"
                "飞行员操纵拉动反推力杆，油门台内微动开关1在油门杆角度[-1.4°, -6.2°]区间内触发，"
                "DIU控制115VAC单相电继电器闭合（控制逻辑1），TLS通电后解锁。"
                "飞行员继续操纵反推力杆，油门台内微动开关2在油门杆角度[-5°, -9.8°]区间内触发，"
                "EICU控制继电器（控制逻辑2），将540VDC供电给ETRAC；当油门杆角度小于-11.74°时，"
                "EEC将反推展开指令发送给ETRAC（控制逻辑3），ETRAC给左右PLS通电，"
                "PLS通电解锁，并将三相交流电供给电机，电机通电后带动反推滑动罩滑动罩，"
                "当反推展开到90%，油门台反推电子锁解锁（控制逻辑4），"
                "飞行员将反推力杆操纵至最大反推位，发动机响应反推力杆指令，加速至最大反推功率。"
            ),
            "故障注入目前暂时不考虑，很复杂。",
        ]
    )

    payload = build_local_preparse_payload(docx_text, document_name="real-docx-excerpt.docx")

    nodes_by_id = {node["id"]: node for node in payload["concept_logic_nodes"]}
    assert payload["status"] == "ready_for_logic_builder"
    assert set(payload["deterministic_preparse"]["detected"]["signal_ids"]) >= {
        "ra_lt_6ft",
        "sw2",
        "thr_lock_release",
    }
    expected_quote_fragments = {
        "ra_lt_6ft": "飞机离地小于6ft",
        "sw2": "SW1 和SW2",
        "thr_lock_release": "反推电子锁解锁",
    }
    for node_id, fragment in expected_quote_fragments.items():
        node = nodes_by_id[node_id]
        assert node["source_anchors"], node_id
        assert node["provenance"] == "docx_body_condition"
        assert any(fragment in anchor["quote_zh"] for anchor in node["source_anchors"])


def test_model_enrichment_maps_equivalent_node_labels_to_docx_anchors(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-secret")

    def fake_post(url: str, body: bytes, headers: dict[str, str], timeout: float) -> str:
        return _model_response(
            {
                "summary_zh": "模型保留了 L1-L4，但节点 id 与本地预解析不同。",
                "open_questions": [],
                "concept_logic_nodes": [
                    {"id": "input_ra", "label": "RA<6ft", "node_kind": "input"},
                    {"id": "input_sw2", "label": "SW2", "node_kind": "input"},
                    {"id": "input_tra", "label": "TRA<=-11.74°", "node_kind": "input"},
                    {"id": "feedback_vdt", "label": "VDT 90%", "node_kind": "component"},
                ],
                "concept_edges": [
                    {"id": "edge_ra_sw2", "source": "input_ra", "target": "input_sw2", "label": "RA to SW2"},
                ],
                "ready_for_logic_builder": True,
            }
        )

    docx_text = "\n".join(
        [
            "工作逻辑1 L1：当 RA<6ft 且 SW1 进入 TRA [-1.4,-6.2] 区间，输出 TLS 115VAC。",
            "工作逻辑2 L2：当 SW2 有效且 TRA 区间满足时，输出 ETRAC 540VDC。",
            "工作逻辑3 L3：TLS/PLS 反馈满足后，驱动 PDU motor 并等待 VDT。",
            "工作逻辑4 L4：当 VDT 达到 90% deploy 且 TRA<=-11.74°，THR_LOCK release。",
        ]
    )

    result = analyze_requirements_text(docx_text, document_name="logic.docx", provider="deepseek", request_post=fake_post)

    nodes_by_id = {node["id"]: node for node in result["concept_logic_nodes"]}
    for node_id in ("input_ra", "input_sw2", "input_tra", "feedback_vdt"):
        assert nodes_by_id[node_id]["source_anchors"], node_id
        assert nodes_by_id[node_id]["provenance"] == "docx_body_condition"


def test_demo_server_endpoint_uses_analysis_helper(monkeypatch):
    def fake_analyze(document_text: str, **kwargs):
        assert document_text == "RA 小于 6ft 时进入逻辑。"
        assert kwargs["document_name"] == "logic.md"
        assert kwargs["provider"] == "deepseek"
        return {
            "kind": "ai-fantui-requirements-intake-analysis",
            "version": 1,
            "status": "needs_clarification",
            "summary_zh": "需要确认 SW1。",
            "open_questions": [{"id": "sw1", "prompt_zh": "SW1 来源是什么？"}],
            "concept_logic_nodes": [],
            "concept_edges": [],
            "truth_effect": "none",
            "candidate_state": "concept_only",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "analyze_requirements_text", fake_analyze)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {
                "document_text": "RA 小于 6ft 时进入逻辑。",
                "document_name": "logic.md",
                "provider": "deepseek",
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["status"] == "needs_clarification"
    assert payload["truth_effect"] == "none"


def test_demo_server_appends_clarification_answers(monkeypatch):
    captured: dict[str, object] = {}

    def fake_analyze(document_text: str, **kwargs):
        captured["document_text"] = document_text
        return {
            "kind": "ai-fantui-requirements-intake-analysis",
            "version": 1,
            "status": "ready_for_logic_builder",
            "summary_zh": "澄清已合并。",
            "open_questions": [],
            "concept_logic_nodes": [{"id": "node_ra", "label": "RA", "node_kind": "input"}],
            "concept_edges": [],
            "truth_effect": "none",
            "candidate_state": "concept_only",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "ready_for_logic_builder": True,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "analyze_requirements_text", fake_analyze)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {
                "document_text": "RA 小于 6ft 时进入逻辑。",
                "document_name": "logic.md",
                "provider": "deepseek",
                "clarification_answers": [
                    {
                        "question_id": "clarify_io_signals",
                        "prompt_zh": "请列出输入输出。",
                        "answer_zh": "输入是 RA 和 SW1；输出是 L1。",
                    }
                ],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["status"] == "ready_for_logic_builder"
    assert "[工程师澄清回答]" in captured["document_text"]
    assert "问题：请列出输入输出。" in captured["document_text"]
    assert "回答：输入是 RA 和 SW1；输出是 L1。" in captured["document_text"]


def test_demo_server_filters_answered_clarification_questions(monkeypatch):
    def fake_analyze(document_text: str, **kwargs):
        return {
            "kind": "ai-fantui-requirements-intake-analysis",
            "version": 1,
            "status": "needs_clarification",
            "summary_zh": "模型重复提问。",
            "open_questions": [
                {"id": "Q1", "prompt_zh": "TLS 已解锁如何确认？"},
                {"id": "Q2", "prompt_zh": "新问题是什么？"},
            ],
            "concept_logic_nodes": [{"id": "node_tls", "label": "TLS", "node_kind": "input"}],
            "concept_edges": [{"id": "edge_tls", "source": "node_tls", "target": "node_l3", "label": "反馈"}],
            "truth_effect": "none",
            "candidate_state": "concept_only",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "ready_for_logic_builder": False,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "analyze_requirements_text", fake_analyze)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {
                "document_text": "RA 小于 6ft 时进入逻辑。",
                "document_name": "logic.md",
                "provider": "deepseek",
                "clarification_answers": [
                    {
                        "question_id": "Q1",
                        "prompt_zh": "TLS 已解锁如何确认？",
                        "answer_zh": "由 TLS 传感器反馈确认。",
                    },
                    {
                        "question_id": "Q2",
                        "prompt_zh": "新问题是什么？",
                        "answer_zh": "本轮不需要继续澄清。",
                    },
                ],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["status"] == "ready_for_logic_builder"
    assert payload["ready_for_logic_builder"] is True
    assert payload["open_questions"] == []
    assert payload["clarification_resolution"]["filtered_repeated_question_count"] == 2


def test_demo_server_marks_zero_question_zero_graph_dead_state_after_answer_filter(monkeypatch):
    def fake_analyze(document_text: str, **kwargs):
        return {
            "kind": "ai-fantui-requirements-intake-analysis",
            "version": 1,
            "status": "needs_clarification",
            "summary_zh": "",
            "open_questions": [
                {"id": "Q1", "prompt_zh": "输入信号是什么？"},
            ],
            "concept_logic_nodes": [],
            "concept_edges": [],
            "truth_effect": "none",
            "candidate_state": "concept_only",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "ready_for_logic_builder": False,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "analyze_requirements_text", fake_analyze)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {
                "document_text": "控制逻辑文档正文。",
                "provider": "deepseek",
                "clarification_answers": [
                    {
                        "question_id": "Q1",
                        "prompt_zh": "输入信号是什么？",
                        "answer_zh": "RA、SW1、SW2。",
                    }
                ],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["status"] == "needs_clarification"
    assert payload["ready_for_logic_builder"] is False
    assert payload["open_questions"] == []
    assert payload["recovery_state"]["status"] == "invalid_model_output"
    assert payload["recovery_state"]["missing_fields"] == [
        "summary_zh",
        "concept_logic_nodes",
        "concept_edges",
    ]
    assert "retry_model" in payload["recovery_state"]["actions"]


def test_demo_server_endpoint_extracts_docx_upload(monkeypatch):
    captured: dict[str, object] = {}

    def fake_analyze(document_text: str, **kwargs):
        captured["document_text"] = document_text
        captured["kwargs"] = kwargs
        return {
            "kind": "ai-fantui-requirements-intake-analysis",
            "version": 1,
            "status": "needs_clarification",
            "summary_zh": "DOCX 已解析。",
            "open_questions": [],
            "concept_logic_nodes": [],
            "concept_edges": [],
            "truth_effect": "none",
            "candidate_state": "concept_only",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    docx_buffer = io.BytesIO()
    with zipfile.ZipFile(docx_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "word/document.xml",
            (
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>RA 小于 6ft</w:t></w:r></w:p>"
                "<w:p><w:r><w:t>SW1 与 SW2 有效</w:t></w:r></w:p></w:body></w:document>"
            ),
        )

    monkeypatch.setattr(demo_server, "analyze_requirements_text", fake_analyze)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {
                "document_base64": base64.b64encode(docx_buffer.getvalue()).decode("ascii"),
                "document_name": "logic.docx",
                "provider": "deepseek",
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["summary_zh"] == "DOCX 已解析。"
    assert "RA 小于 6ft" in captured["document_text"]
    assert "SW1 与 SW2 有效" in captured["document_text"]
    assert captured["kwargs"]["document_name"] == "logic.docx"


def test_demo_server_deepseek_failure_falls_back_to_minimax(monkeypatch):
    assert "llm_timeout" in demo_server.REQUIREMENTS_INTAKE_FALLBACK_ERROR_CODES
    calls: list[str] = []

    def fake_analyze(document_text: str, **kwargs):
        calls.append(kwargs["provider"])
        if kwargs["provider"] == "deepseek":
            raise RequirementsIntakeError(
                "llm_http_error",
                "deepseek returned HTTP 502.",
                status_code=502,
                details={"provider": "deepseek", "upstream_status": 502},
            )
        assert kwargs["provider"] == "minimax"
        return {
            "kind": "ai-fantui-requirements-intake-analysis",
            "version": 1,
            "status": "needs_clarification",
            "summary_zh": "MiniMax fallback 已接管。",
            "open_questions": [],
            "concept_logic_nodes": [],
            "concept_edges": [],
            "truth_effect": "none",
            "candidate_state": "concept_only",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "llm": {"provider": "minimax", "model": "MiniMax-M2.7-highspeed", "key_source": "env:Minimax_API_key"},
        }

    monkeypatch.setattr(demo_server, "analyze_requirements_text", fake_analyze)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/analyze",
            {
                "document_text": "RA 小于 6ft 时进入逻辑。",
                "provider": "deepseek",
                "allow_fallback": True,
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert calls == ["deepseek", "minimax"]
    assert payload["llm"]["provider"] == "minimax"
    assert payload["llm"]["fallback_from"] == "deepseek"
    assert payload["llm"]["fallback_reason"] == "llm_http_error"
    assert payload["llm"]["primary_error"]["details"]["upstream_status"] == 502


def test_demo_server_logic_drawing_endpoint_uses_model_builder(monkeypatch):
    captured: dict[str, object] = {}

    def fake_build(requirements_payload: dict, **kwargs):
        captured["requirements_payload"] = requirements_payload
        captured["kwargs"] = kwargs
        return {
            "kind": "ai-fantui-logic-link-drawing",
            "version": 1,
            "status": "draft_ready",
            "summary_zh": "模型完成绘制。",
            "canvas": {"width": 1280, "height": 760},
            "nodes": [{"id": "RA", "label": "RA", "node_kind": "input", "x": 80, "y": 120, "width": 180, "height": 96}],
            "edges": [],
            "parameter_panels": [],
            "truth_effect": "none",
            "candidate_state": "concept_logic_drawing",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "build_logic_drawing", fake_build)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/draw-logic",
            {
                "provider": "deepseek",
                "requirements_payload": _ready_requirements_payload(),
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-logic-link-drawing"
    assert captured["requirements_payload"]["status"] == "ready_for_logic_builder"
    assert captured["kwargs"]["provider"] == "deepseek"


def test_demo_server_logic_drawing_endpoint_exposes_self_repair_failure(monkeypatch):
    def fake_build(requirements_payload: dict, **kwargs):
        raise RequirementsIntakeError(
            "logic_drawing_json_error",
            "Logic drawing omitted required concept nodes.",
            status_code=502,
            details={
                "missing_required_nodes": ["L1"],
                "self_repair": {
                    "attempted": True,
                    "success": False,
                    "error": "logic_drawing_json_error",
                },
            },
        )

    monkeypatch.setattr(demo_server, "build_logic_drawing", fake_build)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/draw-logic",
            {
                "provider": "deepseek",
                "allow_fallback": False,
                "requirements_payload": _ready_requirements_payload(),
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 502
    assert payload["error"] == "logic_drawing_json_error"
    assert payload["details"]["missing_required_nodes"] == ["L1"]
    assert payload["details"]["self_repair"]["attempted"] is True
    assert payload["details"]["self_repair"]["success"] is False


def test_demo_server_logic_change_endpoint_uses_model_interpreter(monkeypatch):
    captured: dict[str, object] = {}

    def fake_interpret(requirements_payload: dict, drawing_payload: dict, annotation_text: str, **kwargs):
        captured["requirements_payload"] = requirements_payload
        captured["drawing_payload"] = drawing_payload
        captured["annotation_text"] = annotation_text
        captured["kwargs"] = kwargs
        return {
            "kind": "ai-fantui-logic-change-interpretation",
            "version": 1,
            "status": "needs_user_confirmation",
            "truth_effect": "none",
            "candidate_state": "concept_logic_drawing_change",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "target_node_id": "RA",
            "annotation_text": annotation_text,
            "understanding_zh": "用户希望调整 RA 门限。",
            "requirements_match_zh": "匹配 RA 门限原文。",
            "affected_nodes": ["RA"],
            "affected_edges": [],
            "affected_parameter_panels": ["panel_ra"],
            "proposed_changes": ["把默认值改为 7ft。"],
            "confirmation_question_zh": "是否确认？",
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "interpret_logic_change", fake_interpret)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/interpret-logic-change",
            {
                "provider": "deepseek",
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "target_node_id": "RA",
                "annotation_text": "把 RA 门限改成 7ft。",
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-logic-change-interpretation"
    assert captured["annotation_text"] == "把 RA 门限改成 7ft。"
    assert captured["kwargs"]["target_node_id"] == "RA"
    assert captured["kwargs"]["provider"] == "deepseek"


def test_demo_server_logic_change_endpoint_passes_annotation_batch(monkeypatch):
    captured: dict[str, object] = {}

    def fake_interpret(requirements_payload: dict, drawing_payload: dict, annotation_text: str, **kwargs):
        captured["annotation_text"] = annotation_text
        captured["kwargs"] = kwargs
        return {
            "kind": "ai-fantui-logic-change-interpretation",
            "version": 1,
            "status": "needs_user_confirmation",
            "truth_effect": "none",
            "candidate_state": "concept_logic_drawing_change",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "target_node_id": "RA",
            "annotation_text": annotation_text,
            "understanding_zh": "用户希望批量修订 RA。",
            "requirements_match_zh": "匹配 RA 门限原文。",
            "affected_nodes": ["RA"],
            "affected_edges": ["edge_ra_l1"],
            "affected_parameter_panels": ["panel_ra"],
            "proposed_changes": ["归并 RA 节点与连线批注。"],
            "annotation_batch_summary_zh": "2 条批注已归并。",
            "conflict_summary_zh": "无冲突。",
            "annotation_groups": [],
            "selected_nodes": ["RA"],
            "selected_edges": ["RA->L1"],
            "confirmation_question_zh": "是否确认？",
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "interpret_logic_change", fake_interpret)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/interpret-logic-change",
            {
                "provider": "deepseek",
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "target_node_id": "RA",
                "annotation_text": "批量标注意见：RA 节点和 RA→L1 连线需要一起修订。",
                "annotation_batch": [
                    {"target_type": "node", "target_id": "RA", "text": "RA 节点门限应改成 7ft。"},
                    {"target_type": "wire", "target_id": "RA->L1", "text": "连线标签同步。"},
                ],
                "selected_nodes": ["RA"],
                "selected_edges": ["RA->L1"],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["annotation_batch_summary_zh"] == "2 条批注已归并。"
    assert captured["kwargs"]["annotation_batch"][1]["target_id"] == "RA->L1"
    assert captured["kwargs"]["selected_nodes"] == ["RA"]
    assert captured["kwargs"]["selected_edges"] == ["RA->L1"]


def test_demo_server_logic_update_endpoint_uses_model_updater(monkeypatch):
    captured: dict[str, object] = {}
    interpretation = {
        "kind": "ai-fantui-logic-change-interpretation",
        "version": 1,
        "status": "confirmed_by_user",
        "understanding_zh": "用户希望调整 RA 门限。",
    }

    def fake_update(drawing_payload: dict, interpretation_payload: dict, **kwargs):
        captured["drawing_payload"] = drawing_payload
        captured["interpretation_payload"] = interpretation_payload
        captured["kwargs"] = kwargs
        updated = _ready_drawing_payload()
        updated["summary_zh"] = "模型已按确认意见更新图纸。"
        updated["change_applied"] = {"source_interpretation_sha256": "change123"}
        return updated

    monkeypatch.setattr(demo_server, "update_logic_drawing", fake_update)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/update-logic-drawing",
            {
                "provider": "deepseek",
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "interpretation_payload": interpretation,
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-logic-link-drawing"
    assert payload["change_applied"]["source_interpretation_sha256"] == "change123"
    assert captured["interpretation_payload"]["status"] == "confirmed_by_user"
    assert captured["kwargs"]["requirements_payload"]["kind"] == "ai-fantui-requirements-intake-analysis"
    assert captured["kwargs"]["provider"] == "deepseek"


def test_demo_server_fault_injection_prepare_endpoint_uses_model_planner(monkeypatch):
    captured: dict[str, object] = {}

    def fake_prepare(requirements_payload: dict, drawing_payload: dict, **kwargs):
        captured["requirements_payload"] = requirements_payload
        captured["drawing_payload"] = drawing_payload
        captured["kwargs"] = kwargs
        return {
            "kind": "ai-fantui-fault-injection-preparation",
            "version": 1,
            "status": "needs_user_confirmation",
            "summary_zh": "故障注入准备完成。",
            "fault_scenarios": [{"id": "fault_ra", "label": "RA 卡滞", "node_id": "RA"}],
            "injection_points": [{"id": "point_ra", "node_id": "RA", "signal_name": "RA"}],
            "boundary_questions": [{"id": "boundary_ra", "prompt_zh": "RA 边界是什么？"}],
            "workflow_notes": ["只生成候选，不执行仿真。"],
            "truth_effect": "none",
            "candidate_state": "fault_injection_preparation",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "prepare_fault_injection", fake_prepare)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/prepare-fault-injection",
            {
                "provider": "deepseek",
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
                "change_history": [{"status": "updated", "target_node_id": "RA"}],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-fault-injection-preparation"
    assert payload["candidate_state"] == "fault_injection_preparation"
    assert captured["requirements_payload"]["status"] == "ready_for_logic_builder"
    assert captured["drawing_payload"]["kind"] == "ai-fantui-logic-link-drawing"
    assert captured["kwargs"]["change_history"][0]["target_node_id"] == "RA"
    assert captured["kwargs"]["provider"] == "deepseek"


def test_demo_server_fault_injection_prepare_endpoint_exposes_self_repair_failure(monkeypatch):
    def fake_prepare(requirements_payload: dict, drawing_payload: dict, **kwargs):
        raise RequirementsIntakeError(
            "fault_injection_json_error",
            "Fault injection preparation omitted required scenarios.",
            status_code=502,
            details={
                "missing_required_fields": ["fault_scenarios"],
                "self_repair": {
                    "attempted": True,
                    "success": False,
                    "error": "fault_injection_json_error",
                    "message": "Still missing fault_scenarios after repair.",
                },
            },
        )

    monkeypatch.setattr(demo_server, "prepare_fault_injection", fake_prepare)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/prepare-fault-injection",
            {
                "provider": "deepseek",
                "allow_fallback": False,
                "requirements_payload": _ready_requirements_payload(),
                "drawing_payload": _ready_drawing_payload(),
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 502
    assert payload["error"] == "fault_injection_json_error"
    assert payload["details"]["missing_required_fields"] == ["fault_scenarios"]
    assert payload["details"]["self_repair"]["attempted"] is True
    assert payload["details"]["self_repair"]["success"] is False
    assert payload["details"]["self_repair"]["error"] == "fault_injection_json_error"


def test_demo_server_fault_injection_sandbox_endpoint_uses_model_planner(monkeypatch):
    captured: dict[str, object] = {}
    boundary_answers = [
        {
            "id": "boundary_ra_range",
            "answer_zh": "限制在 0-20ft，只用于沙盒。",
        }
    ]

    def fake_sandbox(fault_injection_preparation_payload: dict, **kwargs):
        captured["fault_injection_preparation_payload"] = fault_injection_preparation_payload
        captured["kwargs"] = kwargs
        return {
            "kind": "ai-fantui-fault-injection-sandbox-plan",
            "version": 1,
            "status": "ready_for_review",
            "truth_effect": "none",
            "candidate_state": "fault_injection_sandbox_plan",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "source_fault_injection_preparation_sha256": "faultprep123",
            "summary_zh": "沙盒注入配置建议已生成。",
            "sandbox_injection_plan": [{"id": "inject_ra_low", "fault_scenario_id": "fault_ra_stuck_low"}],
            "observation_points": [{"id": "obs_l1", "signal_name": "L1"}],
            "review_checklist": [{"id": "chk_dry_run", "category": "safety"}],
            "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
            "llm": {"provider": "deepseek", "model": "deepseek-v4-pro", "key_source": "env:DEEPSEEK_API_KEY"},
        }

    monkeypatch.setattr(demo_server, "prepare_fault_injection_sandbox_plan", fake_sandbox)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/prepare-fault-injection/sandbox",
            {
                "provider": "deepseek",
                "fault_injection_preparation_payload": _ready_fault_preparation_payload(),
                "boundary_answers": boundary_answers,
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 200
    assert payload["kind"] == "ai-fantui-fault-injection-sandbox-plan"
    assert payload["execution_contract"]["run_tick"] is False
    assert captured["fault_injection_preparation_payload"]["kind"] == "ai-fantui-fault-injection-preparation"
    assert captured["kwargs"]["boundary_answers"] == boundary_answers
    assert captured["kwargs"]["provider"] == "deepseek"


def test_demo_server_fault_injection_sandbox_endpoint_exposes_self_repair_failure(monkeypatch):
    def fake_sandbox(fault_injection_preparation_payload: dict, **kwargs):
        raise RequirementsIntakeError(
            "fault_injection_sandbox_json_error",
            "Sandbox plan omitted injection plan.",
            status_code=502,
            details={
                "missing_required_fields": ["sandbox_injection_plan"],
                "self_repair": {
                    "attempted": True,
                    "success": False,
                    "error": "fault_injection_sandbox_json_error",
                    "message": "Still missing sandbox_injection_plan after repair.",
                },
            },
        )

    monkeypatch.setattr(demo_server, "prepare_fault_injection_sandbox_plan", fake_sandbox)
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/prepare-fault-injection/sandbox",
            {
                "provider": "deepseek",
                "allow_fallback": False,
                "fault_injection_preparation_payload": _ready_fault_preparation_payload(),
                "boundary_answers": _ready_fault_preparation_payload()["boundary_answers"],
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 502
    assert payload["error"] == "fault_injection_sandbox_json_error"
    assert payload["details"]["missing_required_fields"] == ["sandbox_injection_plan"]
    assert payload["details"]["self_repair"]["attempted"] is True
    assert payload["details"]["self_repair"]["success"] is False
    assert payload["details"]["self_repair"]["error"] == "fault_injection_sandbox_json_error"


def test_demo_server_fault_injection_sandbox_endpoint_rejects_invalid_payload():
    server, thread = _start_server()
    try:
        status, payload = _post(
            server,
            "/api/requirements-intake/prepare-fault-injection/sandbox",
            {
                "provider": "deepseek",
                "fault_injection_preparation_payload": [],
                "boundary_answers": "not-a-list",
            },
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert status == 400
    assert payload["error"] == "invalid_fault_injection_preparation_payload"


def test_requirements_intake_static_subproject_hooks_exist():
    html = (STATIC_ROOT / "requirements_intake" / "index.html").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "requirements_intake" / "requirements_intake.js").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "requirements_intake" / "requirements_intake.css").read_text(encoding="utf-8")
    logic_html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    logic_script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")
    logic_stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    fault_html = (STATIC_ROOT / "fault_injection_prepare" / "index.html").read_text(encoding="utf-8")
    fault_script = (STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.js").read_text(encoding="utf-8")
    fault_stylesheet = (STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.css").read_text(encoding="utf-8")
    sandbox_html = (STATIC_ROOT / "fault_injection_sandbox" / "index.html").read_text(encoding="utf-8")
    sandbox_script = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js").read_text(encoding="utf-8")
    sandbox_stylesheet = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.css").read_text(encoding="utf-8")

    assert 'id="requirements-dropzone"' in html
    assert 'id="requirements-provider"' in html
    assert 'id="requirements-provider-status"' in html
    assert 'id="requirements-provider-key-source"' in html
    assert 'id="requirements-live-only"' in html
    assert 'id="requirements-preflight-panel"' in html
    assert 'id="requirements-preflight-live-state"' in html
    assert 'id="requirements-replay-import"' in html
    assert 'id="requirements-offline-action"' in html
    assert "首次使用预检" in html
    assert ">DeepSeek</span>" in html
    assert "回放可用" in html
    assert "本地候选" in html
    assert "仅 DeepSeek" in html
    assert "使用真实回放演示" in html
    assert "离线本地预解析" in html
    assert 'id="clarification-list"' in html
    assert 'id="clarification-resubmit"' in html
    assert 'id="logic-builder-next"' in html
    assert 'id="clarification-trace"' in html
    assert 'id="clarification-trace-list"' in html
    assert 'id="requirements-workflow-overview"' in html
    assert 'id="requirements-workflow-stage"' in html
    assert 'id="requirements-burden-action"' in html
    assert 'id="requirements-burden-outputs"' in html
    assert 'id="process-panel"' in html
    assert 'id="process-fill"' in html
    assert 'id="process-elapsed"' in html
    assert "v=workflow2" in html
    assert "澄清交互窗口" in html
    assert "下一步" in html
    assert "提交澄清并继续" in html
    assert "TASK PROGRESS" in html
    assert 'value="deepseek"' in html
    assert "DeepSeek V4 Pro" in html
    assert "MiniMax-M2.7-highspeed" in html
    assert "/api/requirements-intake/provider-status" in script
    assert "/api/requirements-intake/deepseek-live-demo-replay" in script
    assert "refreshProviderStatus" in script
    assert "hydrateStoredRequirementsDraft" in script
    assert "importRequirementsReplay" in script
    assert "runOfflineOnly" in script
    assert "providerLiveReady" in script
    assert "DeepSeek 增强失败，可稍后重试" in script
    assert "本地" in script
    assert "requirements-live-only" in script
    assert "allow_fallback: !deepseekLiveOnly.checked" in script
    assert "requirements-intake/analyze" in script
    assert "/logic-builder" in script
    assert "ai-fantui-requirements-intake-ready-v1" in script
    assert "FileReader" in script
    assert "dragover" in script
    assert "concept_logic_nodes" in script
    assert "renderBurdenSummary" in script
    assert "模型输出无效" in script
    assert "data-recovery-action" in script
    assert "sourceAnchorLabel" in script
    assert 'id="logic-canvas"' in logic_html
    assert 'id="logic-provenance-filter"' in logic_html
    assert 'data-provenance-filter="source"' in logic_html
    assert 'data-provenance-filter="assumption"' in logic_html
    assert 'data-provenance-filter="local"' in logic_html
    assert 'id="logic-circuit-svg"' in logic_html
    assert 'id="logic-regenerate"' in logic_html
    assert 'id="logic-change-text"' in logic_html
    assert 'id="logic-submit-change"' in logic_html
    assert 'id="logic-confirm-change"' in logic_html
    assert 'id="logic-selected-node"' in logic_html
    assert 'id="logic-fault-next"' in logic_html
    assert 'id="logic-change-history"' in logic_html
    assert 'id="logic-change-history-list"' in logic_html
    assert 'id="logic-revision-handoff"' in logic_html
    assert 'id="logic-fill-handoff-draft"' in logic_html
    assert 'id="logic-circuit-eval-panel"' in logic_html
    assert 'id="logic-circuit-status-details"' in logic_html
    assert 'id="logic-drawing-notes-details"' in logic_html
    assert 'id="logic-change-loop-details"' in logic_html
    assert 'id="logic-change-history-details"' in logic_html
    assert 'id="logic-circuit-preset-select"' in logic_html
    assert 'value="landing-deploy"' in logic_html
    assert 'value="max-reverse"' in logic_html
    assert 'id="logic-circuit-tra"' in logic_html
    assert 'id="logic-circuit-ra"' in logic_html
    assert 'id="logic-circuit-n1k"' in logic_html
    assert 'id="logic-circuit-vdt"' in logic_html
    assert 'id="logic-circuit-aircraft-on-ground"' in logic_html
    assert 'id="logic-circuit-reverser-inhibited"' in logic_html
    assert 'id="logic-burden-action"' in logic_html
    assert 'id="logic-burden-outputs"' in logic_html
    assert 'id="logic-workflow-overview"' in logic_html
    assert 'id="logic-workflow-stage"' in logic_html
    assert 'id="logic-workflow-detail" data-usage-path-cue="logic"' in logic_html
    assert "本步产出候选逻辑图" in logic_html
    assert "v=workflow2" in logic_html
    assert 'const LEVER_SNAPSHOT_API = "/api/lever-snapshot"' in logic_script
    assert "logicCircuitPresets" in logic_script
    assert "buildCircuitEvaluationRequest" in logic_script
    assert "requestCircuitEvaluation" in logic_script
    assert "applyCircuitEvaluation" in logic_script
    assert "openInspectorDetails" in logic_script
    assert 'const changeLoopDetails = $("logic-change-loop-details")' in logic_script
    assert "manual_override_signoff" in logic_script
    assert "logic-circuit-node" in logic_script
    assert "requirements-intake/draw-logic" in logic_script
    assert "requirements-intake/interpret-logic-change" in logic_script
    assert "requirements-intake/update-logic-drawing" in logic_script
    assert 'allow_fallback: provider.value !== "deepseek"' in logic_script
    assert "allow_fallback: true" not in logic_script
    assert "/fault-injection-prepare" in logic_script
    assert "selectNode" in logic_script
    assert "submitChange" in logic_script
    assert "confirmChange" in logic_script
    assert "recordChangeInterpretation" in logic_script
    assert "markChangeUpdated" in logic_script
    assert "renderChangeHistory" in logic_script
    assert "renderWorkflowOverview" in logic_script
    assert "renderBurdenSummary" in logic_script
    assert "下一页生成故障矩阵" in logic_script
    assert ".logic-circuit-eval-panel" in logic_stylesheet
    assert ".logic-circuit-preset-menu" in logic_stylesheet
    assert ".logic-circuit-status-details" in logic_stylesheet
    assert ".logic-side-details > summary" in logic_stylesheet
    assert ".logic-circuit-node[data-state=\"active\"]" in logic_stylesheet
    assert "circuit_view" in logic_script
    assert "renderCircuitView" in logic_script
    assert "logic-circuit-node" in logic_script
    assert "circuitDisplayLabel" in logic_script
    assert "circuitTechnicalLabel" in logic_script
    assert "circuitRoleLabel" in logic_script
    assert "角色：" in logic_script
    assert "状态：" in logic_script
    assert "技术 ID：" in logic_script
    assert "显示标签：" in logic_script
    assert "来源：" in logic_script
    assert "技术 id:" not in logic_script
    assert "显示标签:" not in logic_script
    assert "来源:" not in logic_script
    assert "role:${node.circuit_role}" not in logic_script
    assert "state:${node.state}" not in logic_script
    assert " · state:${edge.state}" not in logic_script
    assert "circuitProvenanceKindForNode" in logic_script
    assert "renderCircuitProvenanceLegend" in logic_script
    assert "setCircuitProvenanceFilter" in logic_script
    assert "data-provenance-kind" in logic_script
    assert "renderCircuitNodeDetails" in logic_script
    assert "renderCircuitLaneGuides" in logic_script
    assert "data-readable-lane" in logic_script
    assert "SW1/SW2 通道" in logic_script
    assert "SW1/SW2 lane" not in logic_script
    assert "data-fit-mode" in logic_script
    assert "logic-circuit-short-label" in logic_script
    assert "logic-circuit-tech-id" in logic_script
    assert "logic-circuit-lane-label" in logic_script
    assert "dataset.fitScale" in logic_script
    assert "sourceAnchorLabel" in logic_script
    assert "ai-fantui-fault-injection-sandbox-revision-handoff-v1" in logic_script
    assert "loadSandboxRevisionHandoff" in logic_script
    assert "renderSandboxRevisionHandoff" in logic_script
    assert "buildSandboxHandoffDraftText" in logic_script
    assert "fillLogicChangeFromHandoff" in logic_script
    assert "window.localStorage.removeItem(REVISION_HANDOFF_KEY)" in logic_script
    assert "来自沙盒审查" in logic_script
    assert "生成修改意见草稿" in logic_html
    assert "请根据沙盒审查补充具体修改意见" in logic_script
    assert "ai-fantui-logic-builder-change-history-v1" in logic_script
    assert "第 2/4 步" in logic_html
    assert 'id="logic-page-system-strip"' in logic_html
    assert 'data-blueprint-surface="compact-top-bar"' in logic_html
    assert 'data-blueprint27-compact-topbar="step-progress-workflow"' in logic_html
    assert '#logic-page-system-strip[data-blueprint27-compact-topbar="step-progress-workflow"]' in logic_stylesheet
    assert "grid-template-rows: 10px 82px minmax(0, 1fr)" in logic_stylesheet
    assert "max-height: 82px" in logic_stylesheet
    assert ".logic-param-panel" in logic_stylesheet
    assert ".logic-circuit-svg" in logic_stylesheet
    assert ".logic-circuit-node" in logic_stylesheet
    assert ".logic-circuit-node-details" in logic_stylesheet
    assert ".logic-circuit-tech-id" in logic_stylesheet
    assert ".logic-circuit-lane-guide" in logic_stylesheet
    assert ".logic-circuit-node[data-readable-lane=\"sw\"]" in logic_stylesheet
    assert ".logic-provenance-filter" in logic_stylesheet
    assert ".logic-provenance-dot" in logic_stylesheet
    assert ".is-provenance-muted" in logic_stylesheet
    assert ".is-provenance-match" in logic_stylesheet
    assert ".logic-edit-panel" in logic_stylesheet
    assert ".logic-revision-handoff" in logic_stylesheet
    assert ".logic-burden-summary" in logic_stylesheet
    assert ".logic-node-anchor" in logic_stylesheet
    assert ".logic-change-history" in logic_stylesheet
    assert ".logic-change-card" in logic_stylesheet
    assert ".logic-workflow-overview" in logic_stylesheet
    assert ".logic-workflow-step.is-active" in logic_stylesheet
    assert ".logic-node.is-selected" in logic_stylesheet
    assert "concept_edges" in script
    assert "clarification_answers" in script
    assert "recordAnalysisRound" in script
    assert "renderClarificationTrace" in script
    assert "renderWorkflowOverview" in script
    assert "clarification-trace-list" in html
    assert "blocking_reason" in script
    assert "focusClarificationIfNeeded" in script
    assert "question-action" in script
    assert "beginTask" in script
    assert "finishTask" in script
    assert "failTask" in script
    assert "processFill" in script
    assert ".requirements-node-card" in stylesheet
    assert ".clarification-card" in stylesheet
    assert ".requirements-decision-board" in stylesheet
    assert ".requirements-decision-card" in stylesheet
    assert ".clarification-primary" in stylesheet
    assert ".clarification-trace" in stylesheet
    assert ".trace-round-card" in stylesheet
    assert ".workflow-overview" in stylesheet
    assert ".workflow-step.is-active" in stylesheet
    assert ".process-panel" in stylesheet
    assert ".process-fill" in stylesheet
    assert 'id="fault-injection-workflow-overview"' in fault_html
    assert 'id="fault-injection-workflow-stage"' in fault_html
    assert 'id="fault-injection-workflow-detail"' in fault_html
    assert 'id="fault-scenarios"' in fault_html
    assert 'id="fault-injection-points"' in fault_html
    assert 'id="fault-boundary-list"' in fault_html
    assert 'id="fault-generate"' in fault_html
    assert 'id="fault-back"' in fault_html
    assert 'id="fault-repair-details"' in fault_html
    assert 'id="fault-repair-summary"' in fault_html
    assert 'id="fault-repair-body"' in fault_html
    assert 'id="fault-quality-summary"' in fault_html
    assert 'id="fault-source-defer"' in fault_html
    assert 'id="fault-burden-action"' in fault_html
    assert 'id="fault-coverage-evidence"' in fault_html
    assert 'id="fault-coverage-evidence-list"' in fault_html
    assert "自动补齐证据" in fault_html
    assert 'id="fault-sandbox-next"' in fault_html
    assert 'id="fault-sandbox-gate"' in fault_html
    assert "v=faultprep4" in fault_html
    assert "requestFaultInjection" in fault_script
    assert "renderSelfRepairDetails" in fault_script
    assert "renderQualitySummary" in fault_script
    assert "isFaultDeferredBySource" in fault_script
    assert "仍生成 dry-run 候选" in fault_script
    assert "renderBurdenSummary" in fault_script
    assert "sourceAnchorLabel" in fault_script
    assert "renderCoverageCompletionEvidence" in fault_script
    assert "coverage_completion" in fault_script
    assert "completed_node_ids" in fault_script
    assert "deterministic_dry_run_candidate" in fault_script
    assert "已覆盖" in fault_script
    assert "个关键节点" in fault_script
    assert 'node.node_kind === "input"' in fault_script
    assert 'node.node_kind === "output"' in fault_script
    assert "repair.attempted" in fault_script
    assert "模型输出已自动整理" in fault_script
    assert "模型输出需要重新生成" in fault_script
    assert "renderFaultScenarios" in fault_script
    assert "renderInjectionPoints" in fault_script
    assert "renderBoundaryConfirmations" in fault_script
    assert "getBoundaryCompletion" in fault_script
    assert "updateSandboxGate" in fault_script
    assert "answered === total" in fault_script
    assert "需完成边界确认" in fault_script
    assert "需重新生成边界问题" in fault_script
    assert "loadFaultSourcePayload" in fault_script
    assert "goBackToLogicBuilder" in fault_script
    assert "saveFaultDraft" in fault_script
    assert "loadFaultDraft" in fault_script
    assert "requirements-intake/prepare-fault-injection" in fault_script
    assert 'allow_fallback: provider.value !== "deepseek"' in fault_script
    assert "allow_fallback: true" not in fault_script
    assert "self_repair" in fault_script
    assert "/fault-injection-sandbox" in fault_script
    assert "ai-fantui-requirements-intake-ready-v1" in fault_script
    assert "ai-fantui-logic-builder-drawing-v1" in fault_script
    assert "ai-fantui-logic-builder-change-history-v1" in fault_script
    assert "ai-fantui-fault-injection-preparation-v1" in fault_script
    assert ".fault-scenario-card" in fault_stylesheet
    assert ".fault-point-chip" in fault_stylesheet
    assert ".fault-boundary-item" in fault_stylesheet
    assert ".fault-repair-details" in fault_stylesheet
    assert ".fault-repair-row" in fault_stylesheet
    assert ".fault-quality-summary" in fault_stylesheet
    assert ".fault-source-defer" in fault_stylesheet
    assert ".fault-burden-summary" in fault_stylesheet
    assert ".fault-anchor" in fault_stylesheet
    assert ".fault-coverage-evidence" in fault_stylesheet
    assert ".fault-coverage-row" in fault_stylesheet
    assert ".fault-workflow-step.is-active" in fault_stylesheet
    assert 'id="fault-sandbox-workflow-overview"' in sandbox_html
    assert 'id="fault-sandbox-workflow-stage"' in sandbox_html
    assert 'id="fault-sandbox-injection-plan"' in sandbox_html
    assert 'id="fault-sandbox-observation-points"' in sandbox_html
    assert 'id="fault-sandbox-review-checklist"' in sandbox_html
    assert 'id="fault-sandbox-generate"' in sandbox_html
    assert 'id="fault-sandbox-back"' in sandbox_html
    assert 'id="fault-sandbox-revision-next"' in sandbox_html
    assert 'id="fault-sandbox-review-gate"' in sandbox_html
    assert 'id="fault-sandbox-primary-gates"' in sandbox_html
    assert 'data-sandbox-primary-gate="dry-run"' in sandbox_html
    assert 'data-sandbox-primary-gate="coverage"' in sandbox_html
    assert 'data-sandbox-primary-gate="risk"' in sandbox_html
    assert 'id="fault-sandbox-detail-groups"' in sandbox_html
    assert 'id="fault-sandbox-repair-details"' in sandbox_html
    assert 'id="fault-sandbox-repair-summary"' in sandbox_html
    assert 'id="fault-sandbox-repair-body"' in sandbox_html
    assert 'id="fault-sandbox-quality-summary"' in sandbox_html
    assert 'id="fault-sandbox-burden-action"' in sandbox_html
    assert 'id="fault-sandbox-burden-outputs"' in sandbox_html
    assert 'id="fault-sandbox-plan-coverage-evidence"' in sandbox_html
    assert 'id="fault-sandbox-plan-coverage-list"' in sandbox_html
    assert 'id="fault-sandbox-toggle-detail-panel"' in sandbox_html
    assert 'id="fault-sandbox-detail-drawer"' in sandbox_html
    assert "自动补齐证据" in sandbox_html
    assert "v=sandbox6" in sandbox_html
    assert "requestFaultSandboxPlan" in sandbox_script
    assert "renderSelfRepairDetails" in sandbox_script
    assert "renderQualitySummary" in sandbox_script
    assert "renderBurdenSummary" in sandbox_script
    assert "sourceAnchorLabel" in sandbox_script
    assert "renderPlanCoverageCompletionEvidence" in sandbox_script
    assert "toggleDetailPanel" in sandbox_script
    assert ".sandbox-shell" in sandbox_script
    assert "plan_coverage_completion" in sandbox_script
    assert "completed_fault_scenario_ids" in sandbox_script
    assert "deterministic_dry_run_plan" in sandbox_script
    assert "已覆盖" in sandbox_script
    assert "个故障场景" in sandbox_script
    assert "repair.attempted" in sandbox_script
    assert "模型输出已自动整理" in sandbox_script
    assert "模型输出需要重新生成" in sandbox_script
    assert "renderSandboxInjectionPlan" in sandbox_script
    assert "renderObservationPoints" in sandbox_script
    assert "renderReviewChecklist" in sandbox_script
    assert "renderPrimaryReviewGates" in sandbox_script
    assert "getReviewCompletion" in sandbox_script
    assert "updateReviewGate" in sandbox_script
    assert "data-sandbox-confirm" in sandbox_script
    assert "reviewNextButton" in sandbox_script
    assert "ai-fantui-fault-injection-sandbox-revision-handoff-v1" in sandbox_script
    assert "buildRevisionHandoff" in sandbox_script
    assert "saveRevisionHandoff" in sandbox_script
    assert "window.localStorage.setItem(REVISION_HANDOFF_KEY" in sandbox_script
    assert "可进入逻辑修订" in sandbox_script
    assert "个一级闸门" in sandbox_script
    assert "需重新生成沙盒配置" in sandbox_script
    assert "loadFaultSandboxPlanDraft" in sandbox_script
    assert "saveFaultSandboxPlanDraft" in sandbox_script
    assert "requirements-intake/prepare-fault-injection/sandbox" in sandbox_script
    assert 'allow_fallback: provider.value !== "deepseek"' in sandbox_script
    assert "allow_fallback: true" not in sandbox_script
    assert "self_repair" in sandbox_script
    assert "ai-fantui-fault-injection-preparation-v1" in sandbox_script
    assert "ai-fantui-fault-injection-sandbox-plan-v1" in sandbox_script
    assert "/logic-builder" in sandbox_script
    assert "/api/tick" not in sandbox_script + sandbox_html
    assert ".sandbox-plan-card" in sandbox_stylesheet
    assert ".sandbox-observation-card" in sandbox_stylesheet
    assert ".sandbox-review-item" in sandbox_stylesheet
    assert ".sandbox-contract-pill" in sandbox_stylesheet
    assert ".sandbox-repair-details" in sandbox_stylesheet
    assert ".sandbox-repair-row" in sandbox_stylesheet
    assert ".sandbox-quality-summary" in sandbox_stylesheet
    assert ".sandbox-burden-summary" in sandbox_stylesheet
    assert ".sandbox-anchor" in sandbox_stylesheet
    assert ".sandbox-plan-coverage-evidence" in sandbox_stylesheet
    assert ".sandbox-coverage-row" in sandbox_stylesheet
    assert ".sandbox-review-gate" in sandbox_stylesheet
    assert ".sandbox-primary-gate" in sandbox_stylesheet
    assert "/api/chat/" not in html + script
    assert "/api/chat/" not in fault_html + fault_script
    assert "/api/chat/" not in sandbox_html + sandbox_script
    assert "sk-" not in html + script
    assert "sk-" not in fault_html + fault_script
    assert "sk-" not in sandbox_html + sandbox_script


def test_requirements_intake_engineer_ui_does_not_expose_backend_payloads():
    static_pairs = [
        (
            STATIC_ROOT / "requirements_intake" / "index.html",
            STATIC_ROOT / "requirements_intake" / "requirements_intake.js",
        ),
        (
            STATIC_ROOT / "logic_builder" / "index.html",
            STATIC_ROOT / "logic_builder" / "logic_builder.js",
        ),
        (
            STATIC_ROOT / "fault_injection_prepare" / "index.html",
            STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.js",
        ),
        (
            STATIC_ROOT / "fault_injection_sandbox" / "index.html",
            STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js",
        ),
    ]
    combined_html = "\n".join(path.read_text(encoding="utf-8") for path, _ in static_pairs)
    combined_script = "\n".join(path.read_text(encoding="utf-8") for _, path in static_pairs)

    assert "<summary>JSON</summary>" not in combined_html
    assert "payload-json" not in combined_html
    assert "requirements-json" not in combined_html
    assert "logic-json" not in combined_html
    assert "JSON.stringify(payload, null, 2)" not in combined_script
    assert "JSON.stringify(result.details, null, 2)" not in combined_script
    assert "JSON.stringify(payload.details, null, 2)" not in combined_script
    assert "truth:" not in combined_html + combined_script
    assert "cert:" not in combined_html + combined_script
    assert "repair:" not in combined_html + combined_script
    assert "source:" not in combined_html + combined_script
    assert "fault_injection_json_error" not in combined_html + combined_script
    assert "fault_injection_sandbox_json_error" not in combined_html + combined_script
    assert "logic_drawing_json_error" not in combined_html + combined_script
    assert "data-upload-mode" in combined_script
    assert "safeUiError" in combined_script


def test_landing_page_links_requirements_intake_tool():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert "/docx-to-circuit" in html
    assert "反推需求到可运行电路" in html
    assert "/requirements-intake" in html
    assert "需求理解工作台" in html
    assert "/fault-injection-prepare" in html
    assert "故障注入准备" in html
    assert "/fault-injection-sandbox" in html
    assert "沙盒故障注入" in html


def test_landing_page_has_deepseek_live_replay_import_entry():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="deepseek-live-replay-import"' in html
    assert 'id="deepseek-live-replay-status"' in html
    assert 'id="deepseek-live-replay-meta"' in html
    assert 'id="deepseek-live-replay-counts"' in html
    assert "/api/requirements-intake/deepseek-live-demo-replay" in html
    assert "导入最近回放" in html
    assert "最近回放" in html
    assert "不重新调用模型" in html
    assert "renderReplaySummary" in html
    assert "stage_counts" in html
    assert "generated_at" in html
    assert 'id="deepseek-live-replay-http-link"' in html
    assert "http://127.0.0.1:8002/index.html" in html
    assert "renderFileModeReplayHelp" in html
    assert 'window.location.protocol === "file:"' in html
    assert "浏览器文件模式不能读取本地回放" in html
    assert "PYTHONPATH=src:. python3 -m well_harness.demo_server --host 127.0.0.1 --port 8002" not in html
    assert "ai-fantui-requirements-intake-ready-v1" in html
    assert "ai-fantui-logic-builder-drawing-v1" in html
    assert "ai-fantui-logic-builder-change-history-v1" in html
    assert "ai-fantui-fault-injection-preparation-v1" in html
    assert "ai-fantui-fault-injection-sandbox-plan-v1" in html
    assert 'window.location.href = "/fault-injection-sandbox?replay=deepseek-live"' in html


def test_landing_page_promotes_deepseek_v4_pro_ui_workbench_not_canvas_mainline():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert '<body class="unified-nav-enabled" data-nav-current="home" data-primary-flow="deepseek-v4-pro-ui-workbench">' in html
    assert 'data-primary-flow="deepseek-v4-pro-ui-workbench"' in html
    assert 'id="home-default-mode-grid"' in html
    assert 'aria-label="默认五入口"' in html
    for label in ["画布", "运行", "参数", "证据", "报告"]:
        assert f"<strong>{label}</strong>" in html
    for entry in [
        'data-default-entry="canvas"',
        'data-default-entry="run"',
        'data-default-entry="parameters"',
        'data-default-entry="evidence"',
        'data-default-entry="report"',
    ]:
        assert entry in html
    assert 'href="/logic-builder#run-drawer"' in html
    assert 'href="/logic-builder#parameter-drawer"' in html
    assert 'href="/logic-builder#evidence"' in html
    assert 'href="/logic-builder#report"' in html
    assert "命令面板" in html
    assert 'data-boundary-token="truth_effect:none"' in html
    assert 'data-boundary-token="candidate_state:sandbox_candidate"' in html
    assert ">truth_effect:none<" not in html
    assert ">candidate_state:sandbox_candidate<" not in html
    assert 'id="home-primary-flow-grid"' in html
    assert 'aria-label="DeepSeek 四步主流程"' in html
    assert 'id="home-advanced-modules"' in html
    assert "更多模块" in html
    assert "反推逻辑演示舱" in html
    assert "画布 / 运行 / 参数 / 证据 / 报告" in html
    assert 'href="/workbench"' not in html
    assert 'href="/workbench/start"' not in html
    assert "控制逻辑画布工作台" not in html
    assert "Sandbox Draft Canvas" not in html
    default_html = html.split('id="home-default-mode-grid"', 1)[1].split('class="home-command-palette-hint"', 1)[0]
    assert default_html.count('class="home-mode-entry"') == 5
    primary_html = html.split('id="home-primary-flow-grid"', 1)[1].split('id="home-advanced-modules"', 1)[0]
    assert primary_html.count('class="home-card"') == 4
    assert 'href="/requirements-intake"' in primary_html
    assert 'href="/logic-builder"' in primary_html
    assert 'href="/fault-injection-prepare"' in primary_html
    assert 'href="/fault-injection-sandbox"' in primary_html
    for legacy_href in [
        'href="/demo.html"',
        'href="/c919_etras_workstation.html"',
        'href="http://127.0.0.1:9191/"',
        'href="/fantui_circuit.html"',
        'href="/c919_etras_panel/circuit.html"',
        'href="/fan_console.html"',
        'href="/fantui_requirements.html"',
        'href="/c919_requirements.html"',
    ]:
        assert legacy_href not in primary_html
        assert legacy_href in html


def test_landing_page_promotes_demo_reconstruction_as_first_phase_mvp_entry():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="home-first-phase-mvp"' in html
    assert 'data-first-phase-deliverable="demo-html-reconstruction-mvp"' in html
    assert 'id="home-first-phase-demo-entry"' in html
    assert 'href="/demo-reconstruction"' in html
    assert 'data-home-priority="first-phase-mvp"' in html
    assert "复刻控制台交付物" in html
    assert "反推控制台复刻" in html
    assert "20/20 节点" in html
    assert "23/23 连线" in html
    assert 'data-validation-command="make demo-html-reconstruction-mvp"' in html
    assert 'data-validation-command="make demo-html-reconstruction-browser-acceptance"' in html
    assert "节点 20/20" in html
    assert "浏览器验收通过" in html
    assert ">make demo-html-reconstruction-mvp<" not in html
    assert ">make demo-html-reconstruction-browser-acceptance<" not in html
    assert html.index('id="home-first-phase-mvp"') < html.index('id="home-default-mode-grid"')


def test_landing_page_promotes_docx_to_circuit_as_primary_main_entry():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="home-docx-to-circuit-mainline"' in html
    assert 'data-primary-docx-entry="original-docx-to-complete-circuit"' in html
    assert 'id="home-docx-to-circuit-entry"' in html
    assert 'href="/docx-to-circuit"' in html
    assert 'data-home-priority="source-to-circuit"' in html
    assert 'id="home-primary-next"' in html
    primary_next = html.split('id="home-primary-next"', 1)[1].split(">", 1)[0]
    assert 'href="/docx-to-circuit"' in primary_next
    assert 'data-primary-entry="docx-source-to-circuit"' in primary_next
    assert "uploads/20260409-thrust-reverser-control-logic.docx" not in html
    assert "L1-L4 逻辑复刻" in html
    assert "控制台验收" in html
    assert html.index('id="home-docx-to-circuit-mainline"') < html.index('id="home-first-phase-mvp"')


def test_deepseek_subproject_primary_nav_does_not_promote_canvas_workbench():
    html_paths = [
        STATIC_ROOT / "requirements_intake" / "index.html",
        STATIC_ROOT / "logic_builder" / "index.html",
        STATIC_ROOT / "fault_injection_prepare" / "index.html",
        STATIC_ROOT / "fault_injection_sandbox" / "index.html",
    ]

    for path in html_paths:
        html = path.read_text(encoding="utf-8")
        assert 'href="/workbench"' not in html, path
        assert 'data-nav-key="workbench"' not in html, path
        assert "/requirements-intake" in html, path
        assert "/logic-builder" in html, path
        assert "/fault-injection-prepare" in html, path
        assert "/fault-injection-sandbox" in html, path


def test_deepseek_subproject_nav_collapses_legacy_modules_into_advanced_menu():
    html_paths = [
        STATIC_ROOT / "requirements_intake" / "index.html",
        STATIC_ROOT / "logic_builder" / "index.html",
        STATIC_ROOT / "fault_injection_prepare" / "index.html",
        STATIC_ROOT / "fault_injection_sandbox" / "index.html",
    ]

    for path in html_paths:
        html = path.read_text(encoding="utf-8")
        assert 'id="deepseek-nav-mainline"' in html, path
        expected_nav_label = (
            'aria-label="四步主线"'
            if path.name == "index.html" and path.parent.name == "logic_builder"
            else 'aria-label="DeepSeek 四步主线"'
        )
        assert expected_nav_label in html, path
        assert 'id="deepseek-nav-advanced-modules"' in html, path
        assert "更多模块" in html, path
        mainline_html = html.split('id="deepseek-nav-mainline"', 1)[1].split('id="deepseek-nav-advanced-modules"', 1)[0]
        assert mainline_html.count('class="unified-nav-link') == 4, path
        for mainline_href in [
            'href="/requirements-intake"',
            'href="/logic-builder"',
            'href="/fault-injection-prepare"',
            'href="/fault-injection-sandbox"',
        ]:
            assert mainline_href in mainline_html, path
        for legacy_href in [
            'href="/demo.html"',
            'href="/c919_etras_workstation.html"',
            'href="/fantui_circuit.html"',
            'href="/c919_etras_panel/circuit.html"',
            'href="/fan_console.html"',
            'href="/fantui_requirements.html"',
            'href="/c919_requirements.html"',
        ]:
            assert legacy_href not in mainline_html, path
            assert legacy_href in html, path


def test_deepseek_mainline_nav_and_workflow_strips_use_four_numbered_task_steps():
    page_contracts = [
        (STATIC_ROOT / "index.html", "deepseek-nav-mainline", "unified-nav-link"),
        (STATIC_ROOT / "requirements_intake" / "index.html", "requirements-workflow-steps", "workflow-step"),
        (STATIC_ROOT / "logic_builder" / "index.html", "logic-workflow-steps", "logic-workflow-step"),
        (STATIC_ROOT / "fault_injection_prepare" / "index.html", "fault-workflow-steps", "fault-workflow-step"),
        (STATIC_ROOT / "fault_injection_sandbox" / "index.html", "fault-sandbox-workflow-steps", "sandbox-workflow-step"),
    ]
    nav_paths = [
        STATIC_ROOT / "index.html",
        STATIC_ROOT / "requirements_intake" / "index.html",
        STATIC_ROOT / "logic_builder" / "index.html",
        STATIC_ROOT / "fault_injection_prepare" / "index.html",
        STATIC_ROOT / "fault_injection_sandbox" / "index.html",
    ]
    expected_labels = ["1 需求解析", "2 逻辑复刻", "3 故障准备", "4 沙盒审查"]

    for path in nav_paths:
        html = path.read_text(encoding="utf-8")
        mainline_html = html.split('id="deepseek-nav-mainline"', 1)[1].split('id="deepseek-nav-advanced-modules"', 1)[0]
        assert mainline_html.count('class="unified-nav-link') == 4, path
        for label in expected_labels:
            assert label in mainline_html, path
        for short_label in [">需求</a>", ">逻辑</a>", ">沙盒</a>"]:
            assert short_label not in mainline_html, path

    for path, container_id, class_name in page_contracts:
        html = path.read_text(encoding="utf-8")
        container_html = html.split(f'id="{container_id}"', 1)[1].split("</div>", 1)[0]
        if class_name == "unified-nav-link":
            assert container_html.count(f'class="{class_name}') == 4, path
        else:
            assert container_html.count(f'<span class="{class_name}') == 4, path
        for label in expected_labels:
            assert label in container_html, path


def test_deepseek_four_page_command_strips_use_single_primary_next_cta():
    page_contracts = [
        (
            STATIC_ROOT / "requirements_intake" / "index.html",
            "1",
            "STEP 1/4",
            "需求理解",
            "logic-builder-next",
            "下一步：进入逻辑链路绘制",
            [("requirements-analyze", "检查：分析需求", "分析需求")],
        ),
        (
            STATIC_ROOT / "logic_builder" / "index.html",
            "2",
            "第 2/4 步",
            "逻辑绘制",
            "logic-fault-next",
            "下一步：进入故障准备",
            [
                ("logic-regenerate", "检查：重新绘制", "重新绘制逻辑图"),
                ("logic-back", "更多：返回需求", "返回需求理解"),
            ],
        ),
        (
            STATIC_ROOT / "fault_injection_prepare" / "index.html",
            "3",
            "第 3/4 步",
            "故障准备",
            "fault-sandbox-next",
            "下一步：进入沙盒审查",
            [
                ("fault-generate", "检查：生成候选", "生成故障候选"),
                ("fault-back", "更多：返回绘图", "返回逻辑绘制"),
            ],
        ),
        (
            STATIC_ROOT / "fault_injection_sandbox" / "index.html",
            "4",
            "第 4/4 步",
            "沙盒注入",
            "fault-sandbox-revision-next",
            "下一步：生成逻辑修订单",
            [
                ("fault-sandbox-generate", "检查：生成配置", "生成沙盒配置"),
                ("fault-sandbox-back", "更多：返回故障准备", "返回故障准备"),
            ],
        ),
    ]

    for path, step, step_label, title, primary_id, primary_text, secondary_buttons in page_contracts:
        html = path.read_text(encoding="utf-8")
        assert 'data-command-strip="deepseek-step"' in html, path
        assert f'data-command-step="{step}"' in html, path
        assert f"<h1" in html and f">{title}</h1>" in html, path
        assert step_label in html, path

        assert html.count('data-primary-next-action="true"') == 1, path

        primary_start = html.index(f'id="{primary_id}"')
        primary_end = html.index("</button>", primary_start)
        primary_html = html[primary_start:primary_end]
        assert 'data-primary-next-action="true"' in primary_html, path
        assert "secondary" not in primary_html.split(">", 1)[0], path
        assert f">{primary_text}" in primary_html, path

        for button_id, visible_text, aria_label in secondary_buttons:
            assert f'id="{button_id}"' in html, path
            assert f'aria-label="{aria_label}"' in html, path
            button_start = html.index(f'id="{button_id}"')
            button_end = html.index("</button>", button_start)
            button_html = html[button_start:button_end]
            assert "secondary" in button_html.split(">", 1)[0], path
            assert f">{visible_text}" in button_html, path


def test_deepseek_low_cognitive_load_guardrails_mark_flow_and_action_tiers():
    def _opening_tag(html: str, element_id: str) -> str:
        id_pos = html.index(f'id="{element_id}"')
        tag_start = html.rfind("<", 0, id_pos)
        tag_end = html.index(">", id_pos)
        return html[tag_start : tag_end + 1]

    nav_pages = [
        STATIC_ROOT / "index.html",
        STATIC_ROOT / "requirements_intake" / "index.html",
        STATIC_ROOT / "logic_builder" / "index.html",
        STATIC_ROOT / "fault_injection_prepare" / "index.html",
        STATIC_ROOT / "fault_injection_sandbox" / "index.html",
        STATIC_ROOT / "demo_reconstruction" / "index.html",
    ]
    workflow_contracts = [
        (STATIC_ROOT / "requirements_intake" / "index.html", "requirements-workflow-steps"),
        (STATIC_ROOT / "logic_builder" / "index.html", "logic-workflow-steps"),
        (STATIC_ROOT / "fault_injection_prepare" / "index.html", "fault-workflow-steps"),
        (STATIC_ROOT / "fault_injection_sandbox" / "index.html", "fault-sandbox-workflow-steps"),
    ]
    action_contracts = [
        (
            STATIC_ROOT / "requirements_intake" / "index.html",
            "logic-builder-next",
            {
                "requirements-analyze": "secondary",
                "requirements-replay-import": "secondary",
                "requirements-offline-action": "secondary",
                "requirements-clear": "advanced",
            },
        ),
        (
            STATIC_ROOT / "logic_builder" / "index.html",
            "logic-fault-next",
            {
                "logic-regenerate": "secondary",
                "logic-back": "secondary",
                "logic-fill-handoff-draft": "secondary",
                "logic-clear-change": "advanced",
                "logic-cancel-change": "advanced",
            },
        ),
        (
            STATIC_ROOT / "fault_injection_prepare" / "index.html",
            "fault-sandbox-next",
            {
                "fault-generate": "secondary",
                "fault-back": "secondary",
                "fault-save-boundaries": "secondary",
            },
        ),
        (
            STATIC_ROOT / "fault_injection_sandbox" / "index.html",
            "fault-sandbox-revision-next",
            {
                "fault-sandbox-generate": "secondary",
                "fault-sandbox-back": "secondary",
            },
        ),
    ]

    for path in nav_pages:
        html = path.read_text(encoding="utf-8")
        nav_tag = _opening_tag(html, "deepseek-nav-mainline")
        assert 'data-ux-main-flow="four-step"' in nav_tag, path
        assert html.count('id="deepseek-nav-mainline"') == 1, path
        assert html.count('data-primary-next-action="true"') <= 1, path

    for path, workflow_id in workflow_contracts:
        html = path.read_text(encoding="utf-8")
        workflow_tag = _opening_tag(html, workflow_id)
        assert 'data-ux-main-flow="four-step"' in workflow_tag, path

    for path, primary_id, button_tiers in action_contracts:
        html = path.read_text(encoding="utf-8")
        primary_tag = _opening_tag(html, primary_id)
        assert 'data-primary-next-action="true"' in primary_tag, path
        assert 'data-ux-action-tier="primary"' in primary_tag, path

        for button_id, expected_tier in button_tiers.items():
            button_tag = _opening_tag(html, button_id)
            assert f'data-ux-action-tier="{expected_tier}"' in button_tag, (path, button_id)
            assert 'data-primary-next-action="true"' not in button_tag, (path, button_id)

    demo_html = (STATIC_ROOT / "demo_reconstruction" / "index.html").read_text(encoding="utf-8")
    assert 'data-ux-page-role="demo-mvp-console"' in demo_html
    assert 'data-primary-next-action="true"' not in demo_html


def test_deepseek_four_page_generation_streams_are_visible_and_compact():
    page_contracts = [
        (
            STATIC_ROOT / "requirements_intake" / "index.html",
            "requirements-generation-stream",
            ["读取需求", "本地预解析", "DeepSeek 增强", "生成下一步"],
        ),
        (
            STATIC_ROOT / "logic_builder" / "index.html",
            "logic-generation-stream",
            ["读取需求", "生成图纸", "结构复核", "渲染电路"],
        ),
        (
            STATIC_ROOT / "fault_injection_prepare" / "index.html",
            "fault-generation-stream",
            ["读取图纸", "DeepSeek 故障准备", "整理候选", "边界确认"],
        ),
        (
            STATIC_ROOT / "fault_injection_sandbox" / "index.html",
            "sandbox-generation-stream",
            ["读取准备", "DeepSeek 沙盒配置", "整理观测点", "审查清单"],
        ),
    ]

    for path, stream_id, labels in page_contracts:
        html = path.read_text(encoding="utf-8")
        assert f'id="{stream_id}"' in html, path
        assert 'data-generation-stream="deepseek"' in html, path
        assert html.count("generation-stream-step") >= 4, path
        for label in labels:
            assert label in html, path


def test_deepseek_workflow_exposes_progressive_stream_chunk_rails():
    page_contracts = [
        (
            STATIC_ROOT / "requirements_intake" / "index.html",
            STATIC_ROOT / "requirements_intake" / "requirements_intake.js",
            "requirements-stream-chunks",
            ["本地预解析", "DeepSeek 增强"],
        ),
        (
            STATIC_ROOT / "logic_builder" / "index.html",
            STATIC_ROOT / "logic_builder" / "logic_builder.js",
            "logic-stream-chunks",
            ["已读取需求", "正在生成图纸"],
        ),
        (
            STATIC_ROOT / "fault_injection_prepare" / "index.html",
            STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.js",
            "fault-stream-chunks",
            ["已读取图纸", "DeepSeek 正在准备"],
        ),
        (
            STATIC_ROOT / "fault_injection_sandbox" / "index.html",
            STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js",
            "sandbox-stream-chunks",
            ["已读取准备", "DeepSeek 正在配置"],
        ),
    ]

    for html_path, script_path, chunk_id, expected_labels in page_contracts:
        html = html_path.read_text(encoding="utf-8")
        script = script_path.read_text(encoding="utf-8")
        assert f'id="{chunk_id}"' in html, html_path
        assert 'data-stream-chunks="deepseek"' in html, html_path
        assert "appendStreamChunk" in script, script_path
        assert "resetStreamChunks" in script, script_path
        assert "markStreamChunksFailed" in script, script_path
        for label in expected_labels:
            assert label in script, script_path


def test_logic_builder_declares_demo_reconstruction_mode_and_bridge_entry():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")

    assert 'id="logic-reconstruction-mode-panel"' in html
    assert 'id="logic-reconstruction-mode"' in html
    assert 'id="logic-reconstruction-fidelity"' in html
    assert 'id="logic-docx-circuit-bridge"' in html
    assert 'id="logic-demo-bridge"' in html
    assert '接入同一组杆位快照后会同步点亮电路图。' in html
    assert 'href="/docx-to-circuit"' in html
    assert '打开对齐视图' in html
    assert '查看 demo.html 高保真复刻' not in html
    bridge_html = html.split('id="logic-demo-bridge"', 1)[1].split(">", 1)[0]
    assert 'href="/demo-reconstruction"' in bridge_html
    assert 'data-primary-next-action="true"' not in bridge_html

    assert "renderReconstructionMode" in script
    assert "当前模式：演示舱一致电路图" in script
    assert "链路覆盖：20/20 节点 · 23/23 连线" in script
    assert "当前模式：概念图，尚未对齐演示舱电路" in script
    assert "当前模式：demo.html 高保真复刻" not in script
    assert "function requestedDocxTemplate" in script
    assert "function renderRequestedDocxTemplate" in script
    assert 'params.get("template") === "docx-l1-l4"' in script
    docx_template_block = script.split("function buildDocxTemplateCircuitView()", 1)[1].split(
        "function requestedDocxTemplate",
        1,
    )[0]
    for label in [
        "TLS 115VAC 指令",
        "TLS 解锁反馈",
        "ETRAC 540VDC 指令",
        "EEC 展开指令",
        "PLS 供电",
        "PDU 电机指令",
        "VDT90（≥90% 展开）",
        "THR_LOCK 释放",
    ]:
        assert label in docx_template_block
    assert 'label: "真值未变"' in docx_template_block
    for legacy_label in ["LATCH -> CAUT", '"caut"', '"caut1"', '"caut2"', '"caut3"']:
        assert legacy_label not in docx_template_block
    assert 'label: "truth unchanged"' not in docx_template_block
    assert ".logic-reconstruction-mode-panel" in stylesheet


def test_official_docx_source_payload_round_trips_through_docx_extractor():
    payload = demo_server.official_docx_source_payload()
    assert payload["kind"] == "ai-fantui-official-docx-source"
    assert payload["document_name"] == "uploads/20260409-thrust-reverser-control-logic.docx"
    blob = base64.b64decode(payload["document_base64"], validate=True)
    assert len(blob) == payload["byte_size"]
    assert payload["byte_size"] > 100_000

    text, document_name = demo_server.extract_document_text_from_payload(
        {
            "document_name": payload["document_name"],
            "document_base64": payload["document_base64"],
        }
    )
    assert document_name == payload["document_name"]
    assert len(text) > 1_000
    assert any(term in text for term in ("SW1", "TRA", "反推"))


def test_docx_to_circuit_main_entry_connects_source_logic_and_demo_routes():
    html_path = STATIC_ROOT / "docx_to_circuit" / "index.html"
    script_path = STATIC_ROOT / "docx_to_circuit" / "docx_to_circuit.js"
    stylesheet_path = STATIC_ROOT / "docx_to_circuit" / "docx_to_circuit.css"
    html = html_path.read_text(encoding="utf-8")
    script = script_path.read_text(encoding="utf-8")
    stylesheet = stylesheet_path.read_text(encoding="utf-8")
    server_source = (REPO_ROOT / "src" / "well_harness" / "demo_server.py").read_text(encoding="utf-8")
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    review_link_gate = (REPO_ROOT / "scripts" / "verify_docx_to_circuit_review_links.py").read_text(
        encoding="utf-8"
    )

    assert "/docx-to-circuit" in server_source
    assert "REQUIREMENTS_OFFICIAL_DOCX_SOURCE_PATH" in server_source
    assert "official_docx_source_payload" in server_source
    assert '"document_base64"' in server_source
    assert 'data-ux-page-role="docx-to-circuit-main-entry"' in html
    assert 'data-docx-circuit-main-entry="true"' in html
    assert 'data-docx-circuit-review-workbench="interactive"' in html
    assert 'id="docx-circuit-workbench-bar"' in html
    assert 'data-docx-circuit-workbench-bar="true"' in html
    assert 'id="docx-circuit-compact-review"' in html
    assert 'data-docx-circuit-compact="true"' in html
    assert '<details id="docx-circuit-flow-details"' in html
    assert "docx-circuit-flow-details" in html
    assert "三步工作路径" in html
    assert '<details id="docx-circuit-flow-details" class="docx-circuit-flow" aria-labelledby="docx-circuit-flow-title">' in html
    assert html.count('data-compact-review-card="') == 3
    assert 'id="docx-circuit-compact-demand-title"' in html
    assert 'id="docx-circuit-compact-logic-title"' in html
    assert 'id="docx-circuit-compact-demo-title"' in html
    assert "反推需求到可运行电路" in html
    assert "已登记源文档" in html
    assert 'data-source-document-path="uploads/20260409-thrust-reverser-control-logic.docx"' in html
    assert 'href="/requirements-intake?source=official-docx"' in html
    assert 'href="/logic-builder?template=docx-l1-l4"' in html
    assert 'href="/demo-reconstruction"' in html
    assert 'id="docx-circuit-review-panel"' in html
    assert 'data-docx-circuit-sentence-toolbar="true"' in html
    assert 'id="docx-circuit-prev-step"' in html
    assert 'id="docx-circuit-next-step"' in html
    assert 'id="docx-circuit-step-position"' in html
    assert 'id="docx-circuit-element-evidence-only"' in html
    assert 'id="docx-circuit-copy-trace-packet"' in html
    assert 'id="docx-circuit-copy-review-link"' in html
    assert 'id="docx-circuit-copy-status"' in html
    assert 'id="docx-circuit-source-focus"' in html
    assert 'id="docx-circuit-active-source-entry"' in html
    assert 'id="docx-circuit-show-source-entry"' in html
    assert 'id="docx-circuit-review-packet-preview"' in html
    assert 'id="docx-circuit-review-packet-preview-text"' in html
    assert 'id="docx-circuit-delivery-panel"' in html
    assert 'data-docx-circuit-delivery-panel="true"' in html
    assert 'id="docx-circuit-delivery-evidence-list"' in html
    assert 'class="docx-circuit-review-packet-raw"' in html
    assert 'id="docx-circuit-acceptance-trail"' in html
    assert 'data-docx-circuit-acceptance-trail="true"' in html
    assert 'id="docx-circuit-trail-source"' in html
    assert 'id="docx-circuit-trail-element"' in html
    assert 'id="docx-circuit-sequence-details"' in html
    assert 'id="docx-circuit-source-index-details"' in html
    assert 'data-docx-circuit-source-index="true"' in html
    assert 'id="docx-circuit-source-index-count"' in html
    assert 'id="docx-circuit-source-index-search"' in html
    assert 'id="docx-circuit-source-index-level"' in html
    assert 'id="docx-circuit-source-index-clear"' in html
    assert 'id="docx-circuit-source-index-list"' in html
    assert 'id="docx-circuit-source-anchor"' in html
    assert 'id="docx-circuit-trace-details"' in html
    assert 'data-default-collapsed="true"' in html
    assert 'id="docx-circuit-trace-panel"' in html
    assert 'data-selected-element-id="wire_logic4_thr_lock"' in html
    assert 'id="docx-circuit-trace-evidence-list"' in html
    assert 'id="docx-circuit-logic-ladder"' in html
    assert 'id="docx-circuit-svg"' in html
    assert 'data-visual-contract="docx-l1-l4-subcircuit"' in html
    assert 'data-node-count="20"' in html
    assert 'data-wire-count="23"' in html
    assert 'id="docx-circuit-node-grid"' in html
    assert 'id="docx-circuit-wire-grid"' in html
    assert 'id="docx-circuit-contract-details"' in html
    assert 'id="docx-circuit-demo-scenario"' in html
    assert 'id="docx-circuit-demo-panel"' in html
    assert 'data-docx-circuit-demo-column="true"' in html
    assert 'id="docx-circuit-demo-frame"' in html
    assert 'src="/demo.html?embed=1&amp;palette=codex-light"' in html
    assert 'data-boundary-token="truth_effect:none"' in html
    assert 'data-boundary-token="controller_truth_modified:false"' in html
    assert "只读复刻" in html
    assert "不改真值" in html
    assert "/api/demo-reconstruction/docx-sentence-circuit-map" in script
    assert "docx-circuit-sequence-list" in script
    assert "function activateStep" in script
    assert "function applyDemoScenario" in script
    assert "function renderSubcircuit" in script
    assert "function setSvgHighlights" in script
    assert "function selectCircuitElement" in script
    assert "function renderTracePanel" in script
    assert "function renderCompactDemand" in script
    assert "function renderCompactLogic" in script
    assert "function renderCompactDemo" in script
    assert "function matchingSourceEntries" in script
    assert "function activateRelativeStep" in script
    assert "function renderSourceIndex" in script
    assert "function activateSourceEntry" in script
    assert "function stepForSourceEntry" in script
    assert "function filteredSourceEntries" in script
    assert "function sourceEntryLevels" in script
    assert "function sourceIndexQuery" in script
    assert "WORKBENCH_SECTION_ANCHORS" in script
    assert "function hasReviewHashParams" in script
    assert "function normalizedWorkbenchSectionAnchor" in script
    assert "function applyReviewHashState" in script
    assert "function writeReviewHash" in script
    assert "function writeWorkbenchSectionHash" in script
    assert "function handleWorkbenchAnchorClick" in script
    assert "function parseHashElement" in script
    assert "function currentReviewUrl" in script
    assert "function copyReviewLink" in script
    assert "function sourceEntryReviewUrl" in script
    assert "function copySourceEntryLink" in script
    assert "function renderActiveSourceEntryFocus" in script
    assert "function focusActiveSourceEntry" in script
    assert "sourceIndexDetails" in script
    assert 'params.set("source"' in script
    assert 'params.set("section"' in script
    assert "sourceEntryLinkAnchor" in script
    assert "hashchange" in script
    assert "URLSearchParams" in script
    assert "history.replaceState" in script
    assert "function currentTracePacket" in script
    assert "function tracePacketMarkdown" in script
    assert "function renderDeliverySummary" in script
    assert "function evidenceScopeLabel" in script
    assert "function renderAcceptanceTrail" in script
    assert "function elementDisplayLabel" in script
    assert "function markdownEvidenceList" in script
    assert "function currentTraceMarkdown" in script
    assert "function renderTracePacketPreview" in script
    assert "function copyTracePacket" in script
    assert "data-source-entry-anchor" in script
    assert "data-evidence-scope" in script
    assert "data-selected-element-id" in script
    assert "docx-circuit-svg-wire-hit" in script
    assert "data-wire-hit-id" in script
    assert "docx_circuit_review_packet" in script
    assert "DOCX 电路验收摘要" in script
    assert "```json" in script
    assert "验收摘要已复制" in script
    assert "CIRCUIT_NODES" in script
    assert "CIRCUIT_EDGES" in script
    assert "data-review-anchor" in script
    assert "aria-pressed" in script
    assert "wire_logic4_thr_lock" in html
    assert ".docx-circuit-stage" in stylesheet
    assert ".docx-circuit-flow > summary" in stylesheet
    assert ".docx-circuit-flow:not([open]) .docx-circuit-workflow" in stylesheet
    assert ".docx-circuit-workbench-bar" in stylesheet
    assert ".docx-circuit-compact-review" in stylesheet
    assert ".docx-circuit-compact-card" in stylesheet
    assert ".docx-circuit-collapsible" in stylesheet
    assert ".docx-circuit-collapsible .docx-circuit-source-index-panel" in stylesheet
    assert ".docx-circuit-collapsible .docx-circuit-sequence-list" in stylesheet
    assert ".docx-circuit-review-panel" in stylesheet
    assert ".docx-circuit-review-toolbar" in stylesheet
    assert ".docx-circuit-source-index-panel" in stylesheet
    assert ".docx-circuit-source-index-controls" in stylesheet
    assert ".docx-circuit-source-index-button" in stylesheet
    assert ".docx-circuit-source-link-button" in stylesheet
    assert ".docx-circuit-source-focus" in stylesheet
    assert '.docx-circuit-source-focus[data-has-source="true"]' in stylesheet
    assert ".docx-circuit-review-packet-preview" in stylesheet
    assert "#docx-circuit-demo-frame" in stylesheet
    assert "height: 430px" in stylesheet
    assert ".docx-circuit-source-focus strong" in stylesheet
    assert ".docx-circuit-delivery-panel" in stylesheet
    assert ".docx-circuit-review-packet-raw" in stylesheet
    assert ".docx-circuit-acceptance-trail" in stylesheet
    assert "scripts/verify_docx_to_circuit_review_links.py --format json" in makefile
    assert '"source_entry_link"' in review_link_gate
    assert '"review_packet_markdown_json"' in review_link_gate
    assert '"requirements_official_docx_link"' in review_link_gate
    assert '"requirements_official_docx_failure_recovery"' in review_link_gate
    assert '"submittedDocumentBase64Length"' in review_link_gate
    assert '"submittedHasDocumentBase64"' in review_link_gate
    assert '"submittedHasDocumentText"' in review_link_gate
    assert '"logic_template_query_link"' in review_link_gate
    assert '"workbench_anchor_preserves_review_state"' in review_link_gate
    assert "DOCX_TO_CIRCUIT_REVIEW_BASE_REF" in review_link_gate
    assert "origin/codex/docx-sentence-circuit-demo" in review_link_gate
    assert '"merge-base"' in review_link_gate
    assert '"--cached"' in review_link_gate
    assert '"committed"' in review_link_gate
    assert '"staged"' in review_link_gate
    assert '"unstaged"' in review_link_gate
    assert "markdown_with_json" in review_link_gate
    assert "preview_matches_clipboard" in review_link_gate
    assert "workbenchThreeColumn" in review_link_gate
    assert "demoPanelInline" in review_link_gate
    assert "flowDetailsOpen" in review_link_gate
    assert "workflowHiddenByDefault" in review_link_gate
    assert "firstScreenStageVisible" in review_link_gate
    assert "deliveryPanelVisible" in review_link_gate
    assert "rawReviewPacketHidden" in review_link_gate
    assert "acceptanceTrailVisible" in review_link_gate
    assert '"trailElement": "SW1"' in review_link_gate
    assert "RESPONSIVE_VIEWPORTS" in review_link_gate
    assert '"responsive_layout"' in review_link_gate
    assert "noHorizontalOverflow" in review_link_gate
    assert "sourceLocatorFocused" in review_link_gate
    assert "docx-to-circuit-responsive-" in review_link_gate
    assert "docx-to-circuit-workbench-anchor-" in review_link_gate
    assert "docx-to-circuit-workbench-anchor-reopen-" in review_link_gate
    assert "requirements-official-docx-link-" in review_link_gate
    assert "logic-template-query-link-" in review_link_gate
    assert '"source_entry_locator"' in review_link_gate
    assert '"activeSourceEntryAnchor": "P004"' in review_link_gate
    assert '"activeSourceEntryLabel": "P004 · 需求条目"' in review_link_gate
    assert '"section": "docx-circuit-demo-panel"' in review_link_gate
    assert '"workbench_anchor_reopen"' in review_link_gate
    requirements_script = (STATIC_ROOT / "requirements_intake" / "requirements_intake.js").read_text(encoding="utf-8")
    logic_script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")
    assert "OFFICIAL_DOCX_SOURCE" in requirements_script
    assert "function requestedOfficialDocxSource" in requirements_script
    assert "function applyOfficialDocxSource" in requirements_script
    assert "function enableAnalyzeAfterDocumentLoad" in requirements_script
    assert "enableAnalyzeAfterDocumentLoad();" in requirements_script
    assert "/api/requirements-intake/official-docx-source" in requirements_script
    assert 'state.uploadMode = "base64"' in requirements_script
    assert "payload.document_base64" in requirements_script
    assert "document_base64" in requirements_script
    assert "uploads/20260409-thrust-reverser-control-logic.docx" in requirements_script
    assert "function requestedDocxTemplate" in logic_script
    assert "function renderRequestedDocxTemplate" in logic_script
    assert ".docx-circuit-filter-toggle" in stylesheet
    assert ".docx-circuit-copy-status" in stylesheet
    assert "#docx-circuit-svg" in stylesheet
    assert ".docx-circuit-trace-panel" in stylesheet
    assert ".docx-circuit-svg-wire-hit" in stylesheet
    assert ".docx-circuit-trace-evidence li[data-source-kind=\"sequence_step\"]" in stylesheet
    assert ".docx-circuit-svg-wire[data-current-step-match=\"true\"]" in stylesheet
    assert ".docx-circuit-svg-node[data-current-step-match=\"true\"]" in stylesheet
    assert ".docx-circuit-svg-wire[data-selected=\"true\"]" in stylesheet
    assert ".docx-circuit-svg-node[data-selected=\"true\"]" in stylesheet
    assert ".docx-circuit-contract-chip[data-current-step-match=\"true\"]" in stylesheet
    assert "#docx-circuit-demo-frame" in stylesheet

    server, thread = _start_server()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("GET", "/docx-to-circuit")
        response = conn.getresponse()
        body = response.read().decode("utf-8")
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert "docx-circuit-demo-frame" in body
    assert "反推需求到可运行电路" in body

    # Regression guard: the /docx-to-circuit user-visible surface must stay in
    # acceptance/process language and must not drift back to internal backend
    # jargon. These cover the de-jargon passes in PR #378 (visible copy only;
    # contract tokens like data-boundary-token / packet boundary fields and the
    # circuit element ids are asserted as PRESENT elsewhere and are untouched).
    readable_present_html = [
        "等待控制台加载",
        ">连线</dd>",
        ">合并条件</dt>",
        ">局部子电路</h3>",
        "L4 → THR_LOCK",
        'aria-label="电路元素来源定位"',
        ">场景</span>",
        "等待读取元素来源映射",
    ]
    for token in readable_present_html:
        assert token in html, f"readable copy missing from index.html: {token}"
    readable_present_script = [
        "等待控制台加载",
        '"工序步骤"',
        "无合并条件",
        'wire: "连线"',
        "- 合并条件:",
    ]
    for token in readable_present_script:
        assert token in script, f"readable copy missing from docx_to_circuit.js: {token}"
    # Backend jargon that must never resurface in the user-visible copy.
    forbidden_visible = [
        "交付摘要",
        "等待 iframe 加载",
        "折叠谓词",
        "线束",
        ">demo<",
        "demo.html 同步",
        "不作适航声明",
        "不改控制逻辑",
    ]
    for token in forbidden_visible:
        assert token not in html, f"backend jargon leaked back into index.html: {token}"
        assert token not in script, f"backend jargon leaked back into docx_to_circuit.js: {token}"
    # The raw wire id must not appear as visible text (it stays only in data-* and JS data).
    assert "wire_logic4_thr_lock</strong>" not in html
    assert "wire_logic4_thr_lock</span>" not in html


def test_demo_reconstruction_page_is_productized_main_mvp_console():
    html_path = STATIC_ROOT / "demo_reconstruction" / "index.html"
    script_path = STATIC_ROOT / "demo_reconstruction" / "demo_reconstruction.js"
    stylesheet_path = STATIC_ROOT / "demo_reconstruction" / "demo_reconstruction.css"
    html = html_path.read_text(encoding="utf-8")
    script = script_path.read_text(encoding="utf-8")
    stylesheet = stylesheet_path.read_text(encoding="utf-8")
    server_source = (REPO_ROOT / "src" / "well_harness" / "demo_server.py").read_text(encoding="utf-8")

    assert "/demo-reconstruction" in server_source
    assert 'data-nav-current="demo-reconstruction"' in html
    assert 'data-ux-page-role="demo-mvp-console"' in html
    assert 'data-demo-mvp-console="true"' in html
    assert 'data-console-palette="codex-light"' in html
    assert 'id="demo-reconstruction-console-frame"' in html
    assert '<details id="demo-reconstruction-docx-circuit-map"' in html
    assert (
        html.index('class="demo-reconstruction-console-stage"')
        < html.index('id="demo-reconstruction-docx-circuit-map"')
    )
    assert 'data-source-document-path="uploads/20260409-thrust-reverser-control-logic.docx"' in html
    assert "已登记源文档" in html
    assert 'src="/demo.html?embed=1&amp;palette=codex-light"' in html
    assert 'id="demo-reconstruction-browser-evidence"' in html
    assert 'id="demo-reconstruction-fidelity"' in html
    assert 'id="demo-reconstruction-node-list"' in html
    assert 'id="demo-reconstruction-wire-list"' in html
    assert 'id="demo-reconstruction-node-details"' in html
    assert 'id="demo-reconstruction-wire-details"' in html
    assert 'id="demo-reconstruction-preset-details"' in html
    assert 'id="demo-reconstruction-status-details"' in html
    assert html.count('data-default-collapsed="true"') >= 4
    assert "demo.html 复刻 MVP 控制台" in html
    assert "<h2>原版 demo.html</h2>" not in html
    assert "<h2>当前复刻</h2>" not in html
    assert "demo-reconstruction-comparison-table" not in html
    assert "复刻度：20/20 节点 · 23/23 连线" in html

    for label in ["节点", "连线", "预设场景", "状态输出"]:
        assert label in html
    for label in ["默认前向", "着陆展开", "最大反推", "收起回杆", "抑制阻塞"]:
        assert label in html
    for label in ["THR_LOCK", "L1-L4", "VDT90"]:
        assert label in html

    assert "ai-fantui-logic-builder-drawing-v1" in script
    assert "/api/requirements-intake/deepseek-live-demo-replay" in script
    assert "20/20 节点" in script
    assert "23/23 连线" in script
    assert "dataset.sourceDocumentPath" in script
    assert ".demo-reconstruction-console-stage" in stylesheet
    assert ".demo-reconstruction-source-map > summary" in stylesheet
    assert ".demo-reconstruction-source-map:not([open]) .demo-reconstruction-source-layout" in stylesheet
    assert ".demo-reconstruction-evidence-details summary" in stylesheet
    assert "#demo-reconstruction-console-frame" in stylesheet
    assert "--demo-bg: #f7f8fb" in stylesheet
    assert '.demo-reconstruction-shell[data-console-palette="codex-light"]' in stylesheet
    assert "background: #ffffff" in stylesheet

    server, thread = _start_server()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
        conn.request("GET", "/demo-reconstruction")
        response = conn.getresponse()
        body = response.read().decode("utf-8")
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert response.status == 200
    assert "demo-reconstruction-console-frame" in body


def test_sandbox_review_page_has_current_conclusion_decision_board():
    html = (STATIC_ROOT / "fault_injection_sandbox" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js").read_text(encoding="utf-8")

    assert 'data-decision-board="sandbox-review"' in html
    assert 'data-sandbox-card="conclusion"' in html
    assert 'data-sandbox-card="gates"' in html
    assert 'data-sandbox-card="next"' in html
    assert html.count('class="sandbox-decision-card"') == 3
    for label in ["当前结论", "审查闸门", "下一步"]:
        assert label in html

    board_html = html.split('data-decision-board="sandbox-review"', 1)[1].split('<section class="sandbox-panel sandbox-review-gate-panel"', 1)[0]
    assert 'id="fault-sandbox-decision-conclusion"' in board_html
    assert 'id="fault-sandbox-decision-gates"' in board_html
    assert 'id="fault-sandbox-decision-next-action"' in board_html
    assert 'data-usage-path-cue="sandbox"' in board_html
    assert "审查包、证据链和回放报告" in board_html

    assert ".sandbox-decision-board" in stylesheet
    assert ".sandbox-decision-card" in stylesheet
    assert '#fault-sandbox-decision-next-action[data-usage-path-cue]' in stylesheet
    assert "sandboxDecisionConclusion" in script
    assert "setSandboxDecisionNextAction" in script
    assert "确认后用审查包和回放报告生成候选修订单" in script
    assert "审查包和回放报告将作为修订单依据" in script


def test_requirements_intake_compacts_preflight_and_result_into_decision_board():
    html = (STATIC_ROOT / "requirements_intake" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "requirements_intake" / "requirements_intake.css").read_text(encoding="utf-8")

    assert 'data-decision-board="requirements"' in html
    assert 'data-decision-card="path"' in html
    assert 'data-decision-card="verdict"' in html
    assert 'data-decision-card="next"' in html
    assert html.count('class="requirements-decision-card"') == 3
    for label in ["路径", "当前结论", "下一步"]:
        assert label in html

    board_html = html.split('data-decision-board="requirements"', 1)[1].split('<section class="requirements-layout"', 1)[0]
    assert 'id="requirements-preflight-live-state"' in board_html
    assert 'id="requirements-replay-import"' in board_html
    assert 'id="requirements-offline-action"' in board_html
    assert 'id="result-state"' in board_html
    assert 'id="requirements-summary"' in board_html
    assert 'id="next-step-copy"' in board_html
    assert 'data-usage-path-cue="requirements"' in board_html
    assert "本步产出需求候选与澄清清单" in board_html
    assert 'id="requirements-burden-action"' in board_html
    assert 'id="requirements-burden-outputs"' in board_html
    assert 'class="preflight-cards"' not in html
    assert 'class="result-header"' not in html
    assert 'id="next-step-panel"' not in html
    assert 'id="requirements-burden-summary"' not in html

    assert ".requirements-decision-board" in stylesheet
    assert ".requirements-decision-card" in stylesheet
    assert ".requirements-path-actions" in stylesheet
    assert ".requirements-compact-summary" in stylesheet
    assert '#next-step-copy[data-usage-path-cue]' in stylesheet
    assert "grid-template-rows: 32px 68px 136px minmax(0, 1fr)" in stylesheet
    assert ".requirements-compact-burden .burden-output-list" in stylesheet


def test_requirements_intake_desktop_workbench_collapses_secondary_outputs():
    html = (STATIC_ROOT / "requirements_intake" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "requirements_intake" / "requirements_intake.css").read_text(encoding="utf-8")

    assert 'data-desktop-workbench="input-clarification"' in html
    assert 'id="requirements-secondary-panels"' in html
    assert html.index('class="clarification-workbench clarification-primary"') < html.index('id="requirements-secondary-panels"')
    for panel_id in [
        "clarification-trace",
        "requirements-questions-panel",
        "requirements-concept-graph-panel",
        "requirements-edges-panel",
    ]:
        panel_start = html.index(f'id="{panel_id}"')
        panel_open = html.rfind("<details", 0, panel_start)
        panel_close = html.find(">", panel_open)
        assert panel_open != -1
        assert "open" not in html[panel_open:panel_close]

    assert ".requirements-workbench-secondary" in stylesheet
    assert ".workbench-secondary-panel" in stylesheet
    assert ".workbench-secondary-panel[open]" in stylesheet


def test_requirements_intake_uses_choice_checklist_and_on_demand_popovers():
    html = (STATIC_ROOT / "requirements_intake" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "requirements_intake" / "requirements_intake.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "requirements_intake" / "requirements_intake.js").read_text(encoding="utf-8")

    assert 'data-blueprint-stage="requirements-choice-checklist"' in html
    assert 'id="requirements-confirmation-checklist"' in html
    assert html.count('data-requirement-choice-row="') >= 4
    for token in ["L1 条件", "RA 门限", "SW 信号", "VDT 状态"]:
        assert token in html
    assert 'id="requirements-row-popover"' in html
    assert 'id="requirements-manual-bubble"' in html
    assert 'data-on-demand-popover="requirements-source"' in html

    for selector in [
        ".requirements-choice-canvas",
        ".requirements-confirmation-checklist",
        ".requirements-choice-row",
        ".requirements-floating-popover",
        ".requirements-manual-bubble",
    ]:
        assert selector in stylesheet

    for token in [
        "requirementsChoiceRows",
        "showRequirementsRowPopover",
        "hideRequirementsRowPopover",
        "toggleManualBubble",
    ]:
        assert token in script


def test_requirements_intake_uses_demo_cockpit_visual_skin():
    html = (STATIC_ROOT / "requirements_intake" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "requirements_intake" / "requirements_intake.css").read_text(encoding="utf-8")

    assert 'data-ui-skin="demo-cockpit"' in html
    for role in [
        "canopy-frame",
        "status-banner",
        "instrument-rail",
        "mission-strip",
        "input-bay",
        "mission-console",
    ]:
        assert f'data-cockpit-role="{role}"' in html
    assert html.count('class="requirements-cockpit-canopy-window"') == 3

    for selector in [
        ".requirements-cockpit-shell",
        ".requirements-cockpit-canopy",
        ".requirements-cockpit-instrument-rail",
        ".requirements-cockpit-input-bay",
        ".requirements-cockpit-mission-console",
    ]:
        assert selector in stylesheet


def test_requirements_and_logic_default_states_share_canvas_first_workstation_contract():
    requirements_html = (STATIC_ROOT / "requirements_intake" / "index.html").read_text(encoding="utf-8")
    requirements_stylesheet = (STATIC_ROOT / "requirements_intake" / "requirements_intake.css").read_text(encoding="utf-8")
    requirements_script = (STATIC_ROOT / "requirements_intake" / "requirements_intake.js").read_text(encoding="utf-8")
    logic_html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    logic_stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    logic_script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    for html in [requirements_html, logic_html]:
        assert 'data-workstation-shell="canvas-first"' in html
        assert 'data-workstation-state="primary"' in html
        assert 'data-unified-inspector-state="none"' in html
        assert 'data-panel-strategy="single-auxiliary"' in html
        assert 'data-active-aux-panel="none"' in html

    assert 'data-blueprint14-rhythm="compact-canvas"' in requirements_html
    assert 'data-blueprint14-compact-topbar="step-provider-next"' in requirements_html
    assert 'data-blueprint14-density="compact-decision-board"' in requirements_html
    assert 'data-blueprint14-layout="source-inspector-primary-canvas"' in requirements_html
    assert 'data-blueprint14-checklist="compact-four-anchor"' in requirements_html
    assert 'data-blueprint14-inspector="source-document-input"' in requirements_html
    assert 'data-blueprint14-primary-canvas="clarification-stage"' in requirements_html
    assert 'data-blueprint14-canvas-rhythm="expanded-first-screen"' in requirements_html
    assert 'data-workstation-layout="primary-canvas-plus-inspector"' in requirements_html
    assert 'data-workstation-surface="primary-canvas-stage"' in requirements_html
    assert 'class="clarification-workbench clarification-primary" data-workstation-stage="primary-canvas"' in requirements_html
    assert 'data-workstation-inspector="source-input"' in requirements_html
    assert 'data-workstation-surface="secondary-drawer"' in requirements_html
    assert 'data-unified-aux-panel="source-popover"' in requirements_html
    assert 'data-unified-aux-panel="manual-bubble"' in requirements_html

    assert 'data-workstation-surface="primary-canvas-stage"' in logic_html
    assert 'data-workstation-stage="primary-canvas"' in logic_html
    assert 'data-workstation-inspector="engineering-rail"' in logic_html
    assert 'data-workstation-surface="default-mode-dock"' in logic_html
    assert 'data-workstation-canvas="logic-drawing"' in logic_html
    assert 'data-workstation-surface="bottom-run-strip"' in logic_html
    for panel in ["left-rail", "right-inspector", "bottom-drawer", "command-palette"]:
        assert f'data-unified-aux-panel="{panel}"' in logic_html

    assert 'data-blueprint27-rhythm="compact-canvas"' in logic_html
    assert 'data-blueprint27-rhythm="compact-topband"' in logic_html
    assert 'data-blueprint29-rhythm="primary-canvas-stage"' in logic_html
    assert 'data-blueprint27-rhythm="five-entry-dock"' in logic_html
    assert 'data-blueprint38-rhythm="collapsed-inspector-rail"' in logic_html
    assert 'data-blueprint38-rhythm="bottom-run-strip"' in logic_html
    assert 'data-blueprint29-rhythm="blank-canvas-template-entry"' in logic_html

    for stylesheet in [requirements_stylesheet, logic_stylesheet]:
        assert '[data-workstation-shell="canvas-first"] [data-workstation-stage="primary-canvas"]' in stylesheet
        assert '[data-workstation-shell="canvas-first"] [data-unified-panel-state="open"]' in stylesheet
    assert '.requirements-shell[data-blueprint14-rhythm="compact-canvas"]' in requirements_stylesheet
    assert '.requirements-topbar[data-blueprint14-compact-topbar="step-provider-next"]' in requirements_stylesheet
    assert '.requirements-layout[data-blueprint14-layout="source-inspector-primary-canvas"]' in requirements_stylesheet
    assert '.clarification-primary[data-blueprint14-canvas-rhythm="expanded-first-screen"]' in requirements_stylesheet
    assert '.logic-shell[data-blueprint27-rhythm="compact-canvas"] .logic-canvas-wrap[data-blueprint29-rhythm="primary-canvas-stage"]' in logic_stylesheet
    assert '.logic-mode-dock[data-blueprint27-rhythm="five-entry-dock"]' in logic_stylesheet
    assert '#logic-right-inspector-rail[data-blueprint38-rhythm="collapsed-inspector-rail"]' in logic_stylesheet
    assert '#logic-bottom-run-strip[data-blueprint38-rhythm="bottom-run-strip"]' in logic_stylesheet

    for script in [requirements_script, logic_script]:
        assert "setActiveAuxPanel" in script
        assert "unifiedInspectorState" in script
        assert "workstationState" in script
        assert "unifiedPanelState" in script


def test_logic_builder_compacts_detail_area_into_decision_board():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    assert 'data-decision-board="logic-details"' in html
    assert 'data-detail-card="selection"' in html
    assert 'data-detail-card="source"' in html
    assert 'data-detail-card="next"' in html
    assert html.count('class="logic-detail-card"') == 3
    for label in ["当前选择", "来源判断", "下一步"]:
        assert label in html

    board_html = html.split('data-decision-board="logic-details"', 1)[1].split('<div class="logic-workbench-tabbar"', 1)[0]
    assert 'id="logic-detail-selected-node"' in board_html
    assert 'id="logic-detail-source-summary"' in board_html
    assert 'id="logic-detail-next-action"' in board_html
    assert "来源筛选在画布工具条" in board_html

    assert ".logic-detail-decision-board" in stylesheet
    assert ".logic-detail-card" in stylesheet
    assert ".logic-node-anchor" in stylesheet
    assert "logicDetailSelectedNode" in script
    assert "logicDetailSourceSummary" in script
    assert "logicDetailNextAction" in script


def test_logic_builder_exposes_cockpit_annotation_stream_surface():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    surface_gate = (REPO_ROOT / "scripts" / "verify_logic_builder_surface_gate.py").read_text(
        encoding="utf-8"
    )

    assert 'data-ui-skin="codex-minimal"' in html
    assert 'data-logic-experience="cockpit-annotation-stream"' in html
    assert 'id="logic-drawing-stream-timeline"' in html
    assert 'data-ai-stream="logic-drawing-replay"' in html
    assert 'data-default-collapsed="true"' in html
    assert "等待生成过程" in html
    assert "生成图纸" in html
    assert "DEEPSEEK STREAM" not in html
    assert "DeepSeek V4 Pro" not in html
    assert "MiniMax-M2.7-highspeed" not in html
    assert "DeepSeek 绘图" not in html
    assert "模型" not in html
    assert "模型" not in script
    assert "logic-builder-surface-gate" in makefile
    assert "scripts/verify_logic_builder_surface_gate.py --format json" in makefile
    assert "BANNED_VISIBLE_TEXT" in surface_gate
    assert '"模型"' in surface_gate
    assert "EXPECTED_VISIBLE_TEXT" in surface_gate
    assert "EXPECTED_DOM_TEXT" in surface_gate
    assert 'id="logic-annotation-popover"' in html
    assert 'id="logic-selected-target-label"' in html
    assert 'id="logic-node-comment-text"' in html
    assert 'id="logic-add-annotation"' in html
    assert 'id="logic-annotation-submit-bar"' in html
    assert 'id="logic-bottom-provider"' in html
    assert 'id="logic-submit-annotations"' in html
    assert 'id="logic-batch-interpretation-panel"' in html
    assert 'id="logic-batch-summary"' in html
    assert 'id="logic-batch-conflict-summary"' in html
    assert 'id="logic-batch-proposed-changes"' in html
    assert "提交此次标注意见" in html
    assert "AI 修订建议" in html
    assert 'data-annotation-mode="multi-target"' in html

    for selector in [
        ".logic-drawing-stream-timeline",
        ".logic-drawing-stream-timeline[open]",
        ".logic-stream-event",
        ".logic-annotation-popover",
        ".logic-annotation-submit-bar",
        ".logic-batch-interpretation-panel",
        ".logic-canvas-wrap[data-experience=\"annotation-stream\"]",
    ]:
        assert selector in stylesheet

    for token in [
        "ANNOTATION_BATCH_KEY",
        "renderDrawingStreamTimeline",
        "selectAnnotationTarget",
        "addAnnotationDraft",
        "submitAnnotationBatch",
        "buildAnnotationBatchRequest",
        "requestAnnotationBatchInterpretation",
        "renderBatchInterpretation",
        "logicBottomProvider",
    ]:
        assert token in script


def test_logic_builder_uses_selected_object_context_drawer():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    assert 'id="logic-object-context-drawer"' in html
    assert 'data-on-demand-drawer="selected-object"' in html
    assert "节点上下文" in html
    for token in ["来源", "参数", "批注"]:
        assert token in html
    assert 'id="logic-context-source"' in html
    assert 'id="logic-context-params"' in html
    assert 'id="logic-context-comment-shortcut"' in html

    for selector in [
        ".logic-object-context-drawer",
        ".logic-context-section",
        ".logic-context-comment-shortcut",
        ".logic-collapsed-tool-rail",
    ]:
        assert selector in stylesheet

    for token in [
        "objectContextDrawer",
        "renderObjectContextDrawer",
        "logicContextCommentShortcut",
    ]:
        assert token in script


def test_logic_builder_exposes_five_entry_mode_dock_command_palette_and_bottom_drawer():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    assert 'id="logic-mode-dock"' in html
    assert 'data-panel-strategy="single-auxiliary"' in html
    assert 'data-active-aux-panel="none"' in html
    dock_html = html.split('id="logic-mode-dock"', 1)[1].split("</nav>", 1)[0]
    assert dock_html.count("data-logic-mode=") == 5
    assert 'id="logic-command-palette-open"' not in dock_html
    assert ">命令</button>" not in dock_html
    for mode in ["canvas", "run", "parameters", "evidence", "report"]:
        assert f'data-logic-mode="{mode}"' in html
    for label in ["画布", "运行", "参数", "证据", "报告"]:
        assert f">{label}</button>" in html

    assert 'id="logic-command-palette"' in html
    assert 'id="logic-command-palette-open"' in html
    assert html.index('id="logic-command-palette-open"') < html.index('id="logic-mode-dock"')
    assert 'class="logic-command-palette-trigger"' in html
    assert 'data-blueprint-advanced-entry="command-palette"' in html
    assert 'data-blueprint-surface="command-palette"' in html
    assert 'data-command-run-action="run"' in html
    assert 'data-command-run-action="step"' in html
    assert 'data-command-focus-canvas="true"' in html
    assert 'data-command-close-panels="true"' in html
    assert 'data-command-open-mode="parameters"' in html
    assert 'data-command-open-mode="run"' in html
    assert 'data-panel-toggle="left"' in html
    assert 'data-panel-toggle="right"' in html
    assert "注入故障" in html
    assert "打开失败路径" in html
    assert "生成交付摘要" in html
    assert "导出审查包" not in html
    assert "raw JSON" not in html
    assert "打开证据追溯" not in html
    assert "打开报告预览" not in html

    assert 'id="logic-run-parameter-drawer"' in html
    assert 'data-active-tab="none"' in html
    for drawer_tab in ["parameters", "run", "evidence", "report"]:
        assert f'data-bottom-drawer-tab="{drawer_tab}"' in html
        assert f'data-bottom-drawer-panel="{drawer_tab}"' in html
    report_preview_html = html.split('class="logic-report-preview"', 1)[1].split("</dl>", 1)[0]
    for label in ["真值影响", "候选状态", "认证声明", "控制器真值已改动"]:
        assert f"<dt>{label}</dt>" in report_preview_html
    for token in [
        "truth_effect:none",
        "candidate_state:sandbox_candidate",
        "certification_claim:none",
        "controller_truth_modified:false",
    ]:
        assert f'data-boundary-token="{token}"' in report_preview_html
    for english_key in [
        "truth_effect",
        "candidate_state",
        "certification_claim",
        "controller_truth_modified",
    ]:
        assert f"<dt>{english_key}</dt>" not in report_preview_html
    for control_id in [
        "logic-drawer-ra",
        "logic-drawer-sw1",
        "logic-drawer-sw2",
        "logic-drawer-vdt",
        "logic-drawer-tra",
        "logic-drawer-sampling-rate",
        "logic-drawer-step-size",
        "logic-drawer-preset",
        "logic-run-timeline",
    ]:
        assert f'id="{control_id}"' in html
    for action in ["run", "pause", "step", "reset"]:
        assert f'data-run-action="{action}"' in html
    assert 'id="logic-bottom-run-strip"' in html
    assert 'data-blueprint-surface="bottom-run-strip"' in html
    assert 'id="logic-bottom-run-state"' in html
    assert 'id="logic-bottom-run-node-count"' in html
    assert 'id="logic-bottom-run-edge-count"' in html
    assert 'id="logic-right-inspector-rail"' in html
    assert 'data-blueprint-surface="collapsed-left-rail"' in html
    assert 'data-blueprint-surface="collapsed-right-inspector"' in html
    assert 'id="logic-template-entry"' in html
    assert 'data-blueprint-surface="blank-canvas-template-entry"' in html
    assert 'id="logic-start-blank-canvas"' in html
    assert 'id="logic-load-docx-template"' in html
    assert 'id="logic-restore-recent-sandbox"' in html
    assert 'data-command-template-action="docx"' in html
    assert "DOCX L1-L4 官方模板" in html

    for selector in [
        ".logic-mode-dock",
        ".logic-command-palette-trigger",
        ".logic-command-palette",
        ".logic-run-parameter-drawer",
        ".logic-bottom-run-strip",
        ".logic-right-inspector-rail",
        ".logic-template-entry",
        ".logic-template-actions",
        ".logic-template-guide",
        ".logic-parameter-grid",
        ".logic-run-timeline",
        ".logic-trace-grid",
        ".logic-report-preview",
        ".logic-shell.is-left-open .logic-inspector",
        ".logic-shell.is-right-open .logic-object-context-drawer",
    ]:
        assert selector in stylesheet
    for token in [
        "activateBottomDrawer",
        "setActiveAuxPanel",
        "openCommandPalette",
        "closeAuxiliaryPanels",
        "focusCanvas",
        "togglePanel",
        "buildDocxTemplateCandidate",
        "handleTemplateAction",
        "renderTemplateEntryState",
        "syncDrawerToCircuitInputs",
        "handleRunAction",
        "hydrateDrawerFromHash",
        "selected_final_docx_l1_l4_circuit_v1",
        "wire_logic4_thr_lock",
    ]:
        assert token in script


def test_logic_builder_uses_selected_final_codex_minimal_blueprint_skin():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    assert 'data-ui-skin="codex-minimal"' in html
    assert 'data-blueprint-source="selected-final-set-20260514"' in html
    for target in [
        "27-global-nav-default-workbench",
        "28-command-palette-advanced-entry",
        "30-docx-template-generated-canvas",
        "31-running-signal-propagation",
        "32-parameter-drawer-final",
        "38-panel-state-strategy-final",
    ]:
        assert target in html

    assert 'data-left-rail-state="collapsed"' in html
    assert 'data-right-inspector-state="collapsed"' in html
    assert 'data-bottom-drawer-state="closed"' in html
    assert 'data-command-palette-state="closed"' in html
    assert 'data-panel-default="collapsed"' in html
    assert 'data-panel-strategy="single-auxiliary"' in html
    assert "可信度 · 预设 · TRA/RA/N1K/VDT" in html
    assert "可信度 · preset · TRA/RA/N1K/VDT" not in html

    for selector in [
        '.logic-shell[data-ui-skin="codex-minimal"]',
        '.logic-shell[data-ui-skin="codex-minimal"][data-left-rail-state="collapsed"] .logic-inspector',
        '.logic-shell[data-ui-skin="codex-minimal"][data-right-inspector-state="collapsed"] .logic-object-context-drawer',
        '.logic-shell[data-ui-skin="codex-minimal"] .logic-command-palette',
        '.logic-shell[data-ui-skin="codex-minimal"] .logic-bottom-run-strip',
    ]:
        assert selector in stylesheet

    for token in [
        "syncPanelStateContract",
        "leftRailState",
        "rightInspectorState",
        "bottomDrawerState",
        "commandPaletteState",
    ]:
        assert token in script


def test_logic_builder_declares_selected_final_30_31_32_runtime_surfaces():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    for token in [
        'data-blueprint30-surface="docx-template-circuit"',
        'data-blueprint31-surface="run-signal-propagation"',
        'data-blueprint32-surface="parameter-drawer-final"',
        'id="logic-run-frame"',
        'id="logic-run-verdict"',
        'id="logic-run-signals"',
        'id="logic-drawer-tra-threshold"',
        'id="logic-drawer-tra-threshold-value"',
        'id="logic-drawer-run-mode"',
        'id="logic-drawer-run-mode-dry"',
        'id="logic-drawer-run-mode-real"',
        'id="logic-drawer-apply"',
        'id="logic-drawer-reset"',
        'id="logic-drawer-pin"',
    ]:
        assert token in html

    for selector in [
        ".logic-run-signal-summary",
        ".logic-run-signal-grid",
        ".logic-drawer-mode-toggle",
        ".logic-drawer-actions",
        ".logic-run-parameter-drawer[data-drawer-pinned=\"true\"]",
    ]:
        assert selector in stylesheet

    for token in [
        "buildDocxTemplateCircuitView",
        "renderRunSignalSummary",
        "logicRunFrame",
        "logicRunVerdict",
        "logicRunSignals",
        "drawerRunModeButtons",
        "drawerApplyButton",
        "drawerResetButton",
        "drawerPinButton",
    ]:
        assert token in script


def test_panel_state_strategy_hooks_are_declared_across_deepseek_routes():
    route_files = [
        STATIC_ROOT / "requirements_intake" / "index.html",
        STATIC_ROOT / "logic_builder" / "index.html",
        STATIC_ROOT / "fault_injection_prepare" / "index.html",
        STATIC_ROOT / "fault_injection_sandbox" / "index.html",
    ]
    for path in route_files:
        html = path.read_text(encoding="utf-8")
        assert 'data-panel-default="collapsed"' in html, path
        assert 'data-panel-strategy="single-auxiliary"' in html, path
        assert 'data-active-aux-panel="none"' in html, path

    logic_script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")
    fault_script = (STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.js").read_text(encoding="utf-8")
    sandbox_script = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js").read_text(encoding="utf-8")
    for token in ["setActiveAuxPanel", "activeAuxPanel", "activateBottomDrawer", "togglePanel"]:
        assert token in logic_script
    for token in ["setActiveAuxPanel", "activeAuxPanel", "unifiedInspectorState", "fault-context-popover"]:
        assert token in fault_script
    for token in ["setActiveAuxPanel", "activeAuxPanel", "toggleDetailPanel", "renderEvidenceRows"]:
        assert token in sandbox_script


def test_logic_builder_keeps_cockpit_role_hooks_inside_codex_minimal_skin():
    html = (STATIC_ROOT / "logic_builder" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "logic_builder" / "logic_builder.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "logic_builder" / "logic_builder.js").read_text(encoding="utf-8")

    assert 'data-ui-skin="codex-minimal"' in html
    for role in [
        "canopy-frame",
        "status-banner",
        "mission-strip",
        "control-console",
        "primary-display",
    ]:
        assert f'data-cockpit-role="{role}"' in html
    assert html.count('class="logic-cockpit-canopy-window"') == 3
    assert 'data-cockpit-role="control-deck"' in html

    for selector in [
        ".logic-cockpit-shell",
        ".logic-cockpit-canopy",
        ".logic-cockpit-control-console",
        ".logic-cockpit-primary-display",
        ".logic-cockpit-control-deck",
    ]:
        assert selector in stylesheet
    assert "grid-template-rows: 10px 82px minmax(0, 1fr)" in stylesheet
    assert "max-height: 82px" in stylesheet
    assert "logicCircuitInputDetails" in script
    assert "matchMedia" in script


def test_fault_prepare_compacts_candidates_and_boundary_into_decision_board():
    html = (STATIC_ROOT / "fault_injection_prepare" / "index.html").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.css").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "fault_injection_prepare" / "fault_injection_prepare.js").read_text(encoding="utf-8")

    assert 'data-decision-board="fault-prepare"' in html
    assert 'data-fault-card="candidate"' in html
    assert 'data-fault-card="boundary"' in html
    assert 'data-fault-card="next"' in html
    assert html.count('class="fault-decision-card"') == 3
    for label in ["候选状态", "边界确认", "下一步"]:
        assert label in html

    board_html = html.split('data-decision-board="fault-prepare"', 1)[1].split('<details id="fault-candidate-details"', 1)[0]
    assert 'id="fault-decision-candidate-summary"' in board_html
    assert 'id="fault-decision-boundary-summary"' in board_html
    assert 'id="fault-decision-next-action"' in board_html
    assert 'data-usage-path-cue="fault"' in board_html
    assert "故障矩阵与沙盒入口" in board_html
    assert 'id="fault-candidate-details"' in html
    assert 'id="fault-injection-point-details"' in html
    assert 'id="fault-matrix"' in html
    assert 'data-blueprint-surface="fault-matrix"' in html
    assert 'data-blueprint-row-contract="checkbox-id-injection-path-hazard-state"' in html
    assert 'data-blueprint33-contract="checkbox-id-injection-position-covered-path-risk_state"' in html
    assert 'data-blueprint-density="compact-workbench"' in html
    assert 'data-blueprint33-density="compact-workbench"' in html
    assert 'id="fault-candidate-matrix-panel"' in html
    assert 'id="fault-candidate-matrix-body"' in html
    assert 'data-blueprint-surface="fault-matrix-rows"' in html
    for column in ["checkbox", "id", "injection-position", "covered-path", "risk", "state"]:
        assert f'data-blueprint-col="{column}"' in html
    for header in ["编号", "注入位置", "故障类型", "触发条件", "预期影响", "覆盖路径", "风险", "状态"]:
        assert header in html
    assert '<th data-blueprint-col="id">编号</th>' in html
    assert '<th data-blueprint-col="id">ID</th>' not in html
    assert 'id="fault-bottom-action-strip"' in html
    assert 'data-blueprint-surface="fault-bottom-action-strip"' in html
    assert 'data-unified-inspector-state="none"' in html
    assert 'data-unified-inspector="right-inspector"' in html
    assert 'data-inspector-role="fault-preparation-summary"' in html
    assert 'id="fault-context-popover"' in html
    assert 'data-blueprint-surface="unified-inspector-popover"' in html
    assert 'data-unified-aux-panel="fault-context-popover"' in html
    assert 'data-unified-panel-state="closed"' in html
    assert "sandbox_candidate" in html
    assert "truth_effect:none" in html
    assert "controller_truth_modified:false" in html
    assert "候选矩阵将带入审查行、证据链和报告预览" in script
    assert 'id="fault-load-blueprint-candidate"' in html
    assert "载入蓝图候选演示" in html

    assert ".fault-decision-board" in stylesheet
    assert ".fault-decision-card" in stylesheet
    assert ".fault-candidate-matrix-panel" in stylesheet
    assert ".fault-candidate-matrix" in stylesheet
    assert '.fault-candidate-matrix-wrap[data-blueprint-density="compact-workbench"]' in stylesheet
    assert '.fault-candidate-matrix[data-blueprint-density="compact-workbench"] col[data-blueprint-col="covered-path"]' in stylesheet
    assert ".blueprint-row" in stylesheet
    assert ".blueprint-density-row" in stylesheet
    assert ".blueprint-row--fault-matrix" in stylesheet
    assert ".blueprint-row-token" in stylesheet
    assert ".blueprint-row-chip" in stylesheet
    assert ".blueprint-row-linkbar" in stylesheet
    assert ".fault-matrix-injection-cell" in stylesheet
    assert ".fault-matrix-evidence-token" in stylesheet
    assert ".fault-matrix-type-pill" in stylesheet
    assert ".fault-matrix-pathline" in stylesheet
    assert ".fault-matrix-path-token" in stylesheet
    assert ".fault-matrix-path-arrow" in stylesheet
    assert 'tr[data-blueprint33-row="fault-matrix"]' in stylesheet
    assert 'tr[data-blueprint-density="compact-workbench"]' in stylesheet
    assert ".fault-matrix-status::before" in stylesheet
    assert "overflow-wrap: anywhere" in stylesheet
    assert "word-break: break-word" in stylesheet
    assert ".fault-matrix-risk" in stylesheet
    assert ".fault-reference-details" in stylesheet
    assert ".fault-reference-details > summary" in stylesheet
    assert "overflow: visible" in stylesheet
    assert ".fault-source-defer-actions" in stylesheet
    assert ".fault-bottom-action-strip" in stylesheet
    assert ".fault-bottom-invariants" in stylesheet
    assert '.fault-sidebar[data-unified-inspector] .fault-panel:first-child' in stylesheet
    assert '.fault-context-popover[data-unified-panel-state="open"] .fault-context-card' in stylesheet
    assert ".fault-context-link-summary" in stylesheet
    assert ".fault-candidate-matrix tr.is-linked-active" in stylesheet
    assert "faultDecisionCandidateSummary" in script
    assert "faultDecisionBoundarySummary" in script
    assert "faultDecisionNextAction" in script
    assert "FAULT_SANDBOX_REVIEW_LINKS" in script
    assert "activeFaultMatrixSelection" in script
    assert "faultSandboxLinkForMatrixRow" in script
    assert "renderFaultMatrixLinkSummary" in script
    assert "data-active-review-row" in script
    assert "renderFaultCandidateMatrix" in script
    assert 'data-blueprint-fault-row", "matrix"' in script
    assert 'data-blueprint33-row", "fault-matrix"' in script
    assert "data-blueprint-col" in script
    assert "blueprintColumns" in script
    assert "blueprintDensity" in script
    assert "blueprintRowRhythm" in script
    assert "rowScanKind" in script
    assert "rowScanContract" in script
    assert "faultMatrixEvidenceToken" in script
    assert 'data-row-scan-token="evidence"' in script
    assert 'data-row-scan-token="link"' in script
    assert "compact-workbench" in script
    assert "blueprintRowPattern" in script
    assert "shared-v1" in script
    assert "blueprint-row--fault-matrix" in script
    assert "blueprint-row-token" in script
    assert "blueprint-row-chip" in script
    assert "blueprint-row-linkbar" in script
    assert "faultCoveredPathItems" in script
    assert "renderFaultPathTokens" in script
    assert "data-fault-matrix-row" in script
    assert "buildBlueprintFaultCandidate" in script
    assert "buildBlueprintSandboxCandidate" in script
    assert "loadBlueprintCandidateDemo" in script
    assert "loadFirstVisitBlueprintCandidatePreview" in script
    assert "first_visit_preview" in script
    assert "setActiveAuxPanel" in script
    assert "unifiedInspectorState" in script
    assert "unifiedPanelState" in script
    assert "fault-context-popover" in script
    assert "首次进入已载入本地蓝图候选预览" in script
    assert "未调用模型或控制器" in script


def test_sandbox_review_exposes_failure_path_evidence_and_report_blueprint_surfaces():
    html = (STATIC_ROOT / "fault_injection_sandbox" / "index.html").read_text(encoding="utf-8")
    script = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js").read_text(encoding="utf-8")
    stylesheet = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.css").read_text(encoding="utf-8")

    assert 'data-blueprint-phase="sandbox-review-final"' in html
    assert 'data-unified-inspector-state="none"' in html
    assert 'data-blueprint37-top-density="compressed-progress-gates"' in html
    assert 'id="failure-path"' in html
    assert 'data-blueprint-surface="failure-diagnosis-path"' in html
    assert 'data-blueprint37-layout="replay-canvas-report-rail-default"' in html
    assert 'data-blueprint36-contract="path_nodes-first_abnormal-input_snapshot-evidence-review_report-revision_action"' in html
    assert 'id="review-package"' in html
    assert 'data-blueprint-surface="review-package"' in html
    assert 'data-unified-aux-panel="detail-drawer"' in html
    assert 'data-inspector-role="detail-drawer"' in html
    assert 'id="fault-sandbox-review-row-panel"' in html
    assert 'data-blueprint37-surface="replay-main-canvas"' in html
    assert 'data-default-role="replay-canvas-primary"' in html
    assert 'id="fault-sandbox-replay-canvas-main"' in html
    assert 'data-blueprint37-contract="state-nodes-verified-path-warning-boundary"' in html
    assert 'data-blueprint37-density="wide-replay-canvas"' in html
    assert 'id="fault-sandbox-replay-canvas-links"' in html
    assert 'id="fault-sandbox-replay-canvas-nodes"' in html
    assert 'id="fault-sandbox-replay-canvas-metrics"' in html
    assert 'id="fault-sandbox-review-rows"' in html
    assert 'data-blueprint-row-contract="checkbox-id-gate-status-evidence-source-hazard-action"' in html
    assert 'data-blueprint36-contract="checkbox-id-gate-status-evidence-source-hazard_action-trace_report-action"' in html
    assert 'data-blueprint-density="compact-workbench"' in html
    assert 'class="sandbox-review-row-header"' in html
    assert '<span data-blueprint-col="id">编号</span>' in html
    assert '<span data-blueprint-col="id">ID</span>' not in html
    assert 'data-blueprint-surface="sandbox-review-rows"' in html
    assert 'data-blueprint-col="hazard-decision"' in html
    assert 'data-blueprint-col="trace-report"' in html
    assert 'id="fault-sandbox-diagnosis-inspector"' in html
    assert 'data-blueprint-surface="failure-diagnosis-inspector"' in html
    assert 'data-blueprint37-panel="right-report-rail"' in html
    assert 'data-blueprint37-system="replay-report-shared"' in html
    assert 'data-blueprint37-right-density="layered-report-evidence"' in html
    assert 'data-blueprint37-report-mode="replay-report-final"' in html
    assert 'data-unified-inspector="right-inspector"' in html
    assert 'data-inspector-role="failure-diagnosis"' in html
    assert 'id="fault-sandbox-main-report-rail"' in html
    assert 'data-blueprint37-right-section="report-preview"' in html
    assert 'id="fault-sandbox-main-report-actions"' in html
    assert 'id="fault-sandbox-main-report-rows"' in html
    assert 'id="fault-sandbox-diagnosis-summary"' in html
    assert 'id="fault-sandbox-review-package-summary"' in html
    assert 'data-blueprint-surface="active-review-package-summary"' in html
    assert 'data-blueprint37-right-section="active-package"' in html
    assert '<span data-blueprint-col="id">编号</span>' in script
    assert '<span data-blueprint-col="id">ID</span>' not in script
    assert '{label: "编号", value: item.id}' in script
    assert '{label: "编号", value: normalizeText(item.id)}' in script
    assert "锚点编号" in script
    assert 'data-blueprint36-contract="active_review-trace-report-unresolved-fix-evidence"' in html
    assert 'data-package-state="empty"' in html
    assert 'data-blueprint37-right-section="diagnosis-summary"' in html
    assert 'id="fault-sandbox-affected-path"' in html
    assert 'id="fault-sandbox-first-abnormal-node"' in html
    assert 'id="fault-sandbox-repair-suggestions"' in html
    assert 'id="fault-sandbox-diagnosis-chain"' in html
    assert 'data-blueprint37-right-section="failure-path"' in html
    assert 'data-blueprint36-surface="failure-chain-nodes"' in html
    assert 'id="fault-sandbox-evidence-trace"' in html
    assert 'data-blueprint-surface="evidence-trace-links"' in html
    assert 'data-blueprint37-right-section="evidence-trace"' in html
    assert 'data-blueprint37-right-rail="inspector-companion"' in html
    assert 'data-blueprint36-contract="id-stage-review_report-evidence-action"' in html
    assert 'id="fault-sandbox-evidence-trace-rows"' in html
    assert 'id="fault-sandbox-report-preview"' in html
    assert 'data-blueprint-surface="replay-report-preview"' in html
    assert 'data-blueprint37-panel="report-preview-rail"' in html
    assert 'id="fault-sandbox-report-section-rows"' in html
    assert 'data-blueprint36-contract="id-section-decision-evidence-source-trace_report-action"' in html
    assert 'data-blueprint-surface="evidence-trace-final"' in html
    assert 'id="sandbox-report-strip"' in html
    assert 'data-blueprint-surface="replay-report-final"' in html
    assert 'data-blueprint37-surface="replay-report-workbench"' in html
    assert 'data-blueprint37-system="replay-report-shared"' in html
    assert 'data-blueprint37-contract="controls-timeline-report-preview-candidate-footer"' in html
    assert 'data-inspector-role="bottom-report-strip"' in html
    assert 'id="fault-sandbox-replay-workbench"' in html
    assert 'data-blueprint-surface="replay-timeline-workbench"' in html
    assert 'id="fault-sandbox-replay-controls"' in html
    assert 'id="fault-sandbox-replay-clock"' in html
    assert 'id="fault-sandbox-replay-timeline"' in html
    assert 'data-blueprint37-contract="time-markers-sr-et-rp-linkage"' in html
    assert 'id="fault-sandbox-replay-metrics"' in html
    assert 'id="sandbox-evidence-popover"' in html
    assert 'data-unified-aux-panel="evidence-popover"' in html
    assert 'id="sandbox-review-package-panel"' in html
    assert 'data-blueprint-surface="review-package-export-preview"' in html
    assert 'data-unified-aux-panel="review-package"' in html
    assert 'data-inspector-role="review-package-export"' in html
    assert 'data-blueprint36-contract="id-section-decision-evidence-source-trace_report-action"' in html
    assert 'id="sandbox-review-package-review-rows"' in html
    assert 'id="sandbox-review-package-evidence-rows"' in html
    assert 'id="sandbox-review-package-report-rows"' in html
    assert 'id="sandbox-review-package-close"' in html
    assert "sandbox_candidate" in html
    assert "truth_effect:none" in html
    assert "certification_claim:none" in html
    assert "controller_truth_modified:false" in html

    assert ".sandbox-report-strip" in stylesheet
    assert '.sandbox-shell[data-blueprint37-top-density="compressed-progress-gates"]' in stylesheet
    assert '.sandbox-report-strip[data-inspector-role="bottom-report-strip"]' in stylesheet
    assert ".sandbox-replay-workbench" in stylesheet
    assert ".sandbox-replay-controls" in stylesheet
    assert ".sandbox-replay-timeline" in stylesheet
    assert ".sandbox-replay-marker" in stylesheet
    assert ".sandbox-replay-metrics" in stylesheet
    assert ".sandbox-report-actions" in stylesheet
    assert ".sandbox-report-invariants" in stylesheet
    assert ".blueprint-row" in stylesheet
    assert ".blueprint-density-row" in stylesheet
    assert ".blueprint-row-token" in stylesheet
    assert ".blueprint-row-chip" in stylesheet
    assert ".blueprint-row-linkbar" in stylesheet
    assert ".sandbox-review-row-panel" in stylesheet
    assert ".sandbox-replay-canvas-main" in stylesheet
    assert ".sandbox-replay-canvas-links" in stylesheet
    assert ".sandbox-replay-canvas-link-badge" in stylesheet
    assert '.sandbox-replay-canvas-link[data-link-state="active"]' in stylesheet
    assert ".sandbox-replay-canvas-node" in stylesheet
    assert ".sandbox-main-report-rail" in stylesheet
    assert ".sandbox-main-report-actions" in stylesheet
    assert ".sandbox-main-report-status" in stylesheet
    assert ".sandbox-main-report-row" in stylesheet
    assert '.sandbox-main-report-row[data-report-chapter-state="pass"]' in stylesheet
    assert '.sandbox-main-report-row[data-link-state="active"]' in stylesheet
    assert '.sandbox-review-row-list[data-blueprint-density="compact-workbench"]' in stylesheet
    assert ".sandbox-review-row-header" in stylesheet
    assert ".sandbox-review-row-check" in stylesheet
    assert ".sandbox-review-row" in stylesheet
    assert ".sandbox-review-row.is-active" in stylesheet
    assert ".sandbox-review-row-decision" in stylesheet
    assert ".sandbox-review-row-links" in stylesheet
    assert ".sandbox-review-row-link-token" in stylesheet
    assert '.sandbox-review-row[data-blueprint36-row="sandbox-review"]' in stylesheet
    assert ".sandbox-evidence-trace-row.is-linked-active" in stylesheet
    assert ".sandbox-report-section-row.is-linked-active" in stylesheet
    assert ".sandbox-diagnosis-inspector.is-review-linked" in stylesheet
    assert '.sandbox-diagnosis-inspector[data-unified-inspector="right-inspector"]' in stylesheet
    assert '.sandbox-diagnosis-inspector[data-blueprint37-right-density="layered-report-evidence"]' in stylesheet
    assert '.sandbox-diagnosis-inspector[data-blueprint37-report-mode="replay-report-final"]' in stylesheet
    assert ".sandbox-diagnosis-inspector" in stylesheet
    assert '.sandbox-main-report-rail[data-blueprint37-right-section="report-preview"]' in stylesheet
    assert ".sandbox-review-package-summary" in stylesheet
    assert ".sandbox-review-package-summary[data-package-state=\"active\"]" in stylesheet
    assert ".sandbox-review-package-summary-tokens" in stylesheet
    assert ".sandbox-review-package-summary-invariants" in stylesheet
    assert ".sandbox-diagnosis-path" in stylesheet
    assert ".sandbox-diagnosis-chain" in stylesheet
    assert ".sandbox-diagnosis-chain-node" in stylesheet
    assert ".sandbox-diagnosis-chain-link-token" in stylesheet
    assert ".sandbox-diagnosis-evidence-link" in stylesheet
    assert ".sandbox-evidence-trace" in stylesheet
    assert '.sandbox-evidence-trace[data-blueprint37-right-section="evidence-trace"]' in stylesheet
    assert '.sandbox-diagnosis-inspector .sandbox-evidence-trace[data-blueprint37-right-rail="inspector-companion"]' in stylesheet
    assert ".sandbox-evidence-trace-row" in stylesheet
    assert ".sandbox-evidence-trace-stage" in stylesheet
    assert ".sandbox-evidence-trace-links" in stylesheet
    assert ".sandbox-evidence-trace-link-token" in stylesheet
    assert ".sandbox-report-preview" in stylesheet
    assert ".sandbox-report-section-row" in stylesheet
    assert ".sandbox-report-section-decision" in stylesheet
    assert ".sandbox-report-section-links" in stylesheet
    assert ".sandbox-report-link-token" in stylesheet
    assert ".sandbox-review-package-panel" in stylesheet
    assert '.sandbox-evidence-popover[data-unified-panel-state="open"] .sandbox-evidence-card' in stylesheet
    assert '.sandbox-review-package-panel[data-unified-panel-state="open"] .sandbox-review-package-card' in stylesheet
    assert ".sandbox-review-package-card" in stylesheet
    assert ".sandbox-review-package-invariants" in stylesheet
    assert ".sandbox-review-package-item" in stylesheet
    assert ".sandbox-review-package-decision" in stylesheet
    assert ".sandbox-review-package-links" in stylesheet
    assert ".sandbox-review-package-link-token" in stylesheet
    assert ".sandbox-review-package-item:focus-visible" in stylesheet
    assert ".sandbox-review-package-item.is-linked-active" in stylesheet
    script = (STATIC_ROOT / "fault_injection_sandbox" / "fault_injection_sandbox.js").read_text(encoding="utf-8")
    assert "renderSandboxReviewRows" in script
    assert "renderMainReplayCanvas" in script
    assert "renderMainReportRail" in script
    assert "buildReplayCanvasNodes" in script
    assert "data-replay-canvas-node" in script
    assert "data-replay-link-index" in script
    assert "sandbox-replay-canvas-link-badge" in script
    assert "data-main-report-id" in script
    assert "data-report-chapter-state" in script
    assert "data-report-chapter-kind" in script
    assert "sandbox-main-report-status" in script
    assert "data-blueprint-review-row" in script
    assert "data-blueprint36-row" in script
    assert "blueprintColumns" in script
    assert "blueprintDensity" in script
    assert "blueprintRowRhythm" in script
    assert "rowScanKind" in script
    assert "rowScanContract" in script
    assert 'data-row-scan-token="evidence"' in script
    assert 'data-row-scan-token="link"' in script
    assert "compact-workbench" in script
    assert "blueprintRowPattern" in script
    assert "shared-v1" in script
    assert "blueprint-row--sandbox-review" in script
    assert "blueprint-row--diagnosis-chain" in script
    assert "blueprint-row--evidence-chain" in script
    assert "blueprint-row--replay-report" in script
    assert "blueprint-row--review-package" in script
    assert "buildReplayTimelineEvents" in script
    assert "renderReplayReportWorkbench" in script
    assert "data-replay-marker" in script
    assert "data-blueprint37-report-row" in script
    assert "blueprint-row-token" in script
    assert "blueprint-row-chip" in script
    assert "blueprint-row-linkbar" in script
    assert "sandboxReviewDecisionLabel" in script
    assert "sandbox-review-row-link-token" in script
    assert 'data-link-kind="trace"' in script
    assert "data-blueprint36-report-row" in script
    assert "data-blueprint36-package-row" in script
    assert "sandbox-report-link-token" in script
    assert "sandbox-review-package-link-token" in script
    assert "review-package-report" in script
    assert "data-blueprint-report-row" in script
    assert "REVIEW_LINKS" in script
    assert "activateReviewRow" in script
    assert "applyReviewSelection" in script
    assert "readIncomingReviewSelection" in script
    assert "applyIncomingReviewSelection" in script
    assert "URLSearchParams" in script
    assert "incoming-review" in script
    assert "activeReviewPackageSummary" in script
    assert "renderActiveReviewPackageSummary" in script
    assert "buildActiveReviewPackageSummary" in script
    assert "data-package-summary-token" in script
    assert "data-linked-report-id" not in script
    assert "linkedReportId" in script
    assert "linkedTraceId" in script
    assert "renderFailureDiagnosisInspector" in script
    assert "renderEvidenceTraceRows" in script
    assert "fault-sandbox-diagnosis-chain" in script
    assert "data-blueprint36-evidence-row" in script
    assert "sandbox-diagnosis-chain-link-token" in script
    assert "sandbox-evidence-trace-link-token" in script
    assert "blueprint36EvidenceLink" in script
    assert "renderReplayReportPreview" in script
    assert "renderReviewPackagePanel" in script
    assert "openReviewPackagePanel" in script
    assert "closeReviewPackagePanel" in script
    assert "activateReviewPackageItem" in script
    assert "primaryReviewRowForTrace" in script
    assert "primaryReviewRowForReport" in script
    assert "packageTargetReviewRow" in script
    assert "packageTargetTraceId" in script
    assert "packageTargetReportId" in script
    assert "sandbox-review-package-panel" in script
    assert "buildReplayReportSections" in script
    assert "handleReportAction" in script
    assert "unifiedInspectorState" in script
    assert "unifiedPanelState" in script
    assert "unifiedAuxPanels" in script
    assert "sandbox-report-strip" in script
    assert "buildFirstVisitFaultPreparationPreview" in script
    assert "buildFirstVisitSandboxCandidate" in script
    assert "loadFirstVisitSandboxPreview" in script
    assert "first_visit_preview" in script
    assert "首次进入已载入本地蓝图沙盒预览" in script
    assert "未调用模型、tick 或控制器" in script


def test_deepseek_visual_acceptance_script_freezes_first_screen_bundle_contract():
    script = (REPO_ROOT / "scripts" / "deepseek_ui_visual_acceptance.py").read_text(encoding="utf-8")

    assert "deepseek-ui-visual-acceptance" in script
    assert "visual-acceptance-summary.json" in script
    assert "VIEWPORTS" in script
    assert "desktop-1366x768" in script
    assert "desktop-1280x820" in script
    assert "--base-url" in script
    assert "--artifact-dir" in script
    for route in [
        "/requirements-intake",
        "/logic-builder",
        "/fault-injection-prepare",
        "/fault-injection-sandbox",
    ]:
        assert route in script
    for selector in [
        '[data-command-strip="deepseek-step"]',
        "#requirements-preflight-panel",
        '.requirements-shell[data-workstation-shell="canvas-first"]',
        '.requirements-shell[data-blueprint14-rhythm="compact-canvas"]',
        '[data-blueprint14-compact-topbar="step-provider-next"]',
        '.clarification-primary[data-workstation-stage="primary-canvas"]',
        '.clarification-primary[data-blueprint14-canvas-rhythm="expanded-first-screen"]',
        '.requirements-input-panel[data-workstation-inspector="source-input"]',
        '.requirements-input-panel[data-blueprint14-inspector="source-document-input"]',
        '#requirements-preflight-panel[data-blueprint14-density="compact-decision-board"]',
        '#logic-page-system-strip[data-blueprint27-compact-topbar="step-progress-workflow"]',
        '#logic-page-system-strip[data-blueprint27-rhythm="compact-topband"]',
        '.logic-shell[data-workstation-shell="canvas-first"]',
        '.logic-shell[data-blueprint27-rhythm="compact-canvas"]',
        '.logic-canvas-wrap[data-workstation-stage="primary-canvas"]',
        '.logic-canvas-wrap[data-blueprint29-rhythm="primary-canvas-stage"]',
        '#logic-canvas[data-workstation-canvas="logic-drawing"]',
        "#logic-canvas",
        '#logic-command-palette-open[data-blueprint-advanced-entry="command-palette"]',
        '#logic-mode-dock[data-blueprint27-rhythm="five-entry-dock"]',
        '#logic-bottom-run-strip[data-blueprint38-rhythm="bottom-run-strip"]',
        '#logic-right-inspector-rail[data-blueprint38-rhythm="collapsed-inspector-rail"]',
        '#logic-template-entry[data-blueprint29-rhythm="blank-canvas-template-entry"]',
        "#fault-candidate-matrix-panel",
        '.fault-candidate-matrix[data-blueprint-density="compact-workbench"]',
        '#fault-candidate-matrix-body [data-blueprint-fault-row="matrix"]',
        '#fault-candidate-matrix-body [data-blueprint33-row="fault-matrix"]',
        '#fault-candidate-matrix-body [data-blueprint-density="compact-workbench"]',
        '#fault-candidate-matrix-body [data-blueprint-row-pattern="shared-v1"]',
        "#fault-candidate-matrix-body .fault-matrix-path-token",
        "#fault-candidate-matrix-body .blueprint-row-token",
        "#fault-candidate-matrix-body .blueprint-row-chip",
        "#fault-candidate-matrix-body .fault-matrix-risk",
        "#fault-candidate-matrix-body .fault-matrix-status",
        '.fault-sidebar[data-unified-inspector="right-inspector"]',
        "#fault-sandbox-review-row-panel",
        '#fault-sandbox-review-rows[data-blueprint-density="compact-workbench"] [data-blueprint36-row="sandbox-review"]',
        "#fault-sandbox-review-rows [data-blueprint-review-row]",
        '#fault-sandbox-review-rows [data-blueprint36-row="sandbox-review"]',
        '#fault-sandbox-review-rows [data-blueprint-density="compact-workbench"]',
        '#fault-sandbox-review-rows [data-blueprint-row-pattern="shared-v1"]',
        "#fault-sandbox-review-rows .blueprint-row-token",
        "#fault-sandbox-review-rows .sandbox-review-row-decision",
        '#fault-sandbox-review-rows [data-blueprint36-row="sandbox-review"] [data-blueprint-col="trace-report"]',
        "#fault-sandbox-review-rows .sandbox-review-row-link-token",
        '#fault-sandbox-review-rows [data-blueprint-review-row="SR-06"]',
        "#fault-sandbox-diagnosis-inspector",
        '#fault-sandbox-diagnosis-inspector[data-unified-inspector="right-inspector"]',
        '#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node="failure-path"]',
        '#fault-sandbox-diagnosis-chain [data-blueprint-row-pattern="shared-v1"]',
        "#fault-sandbox-diagnosis-chain .sandbox-diagnosis-chain-link-token",
        '#fault-sandbox-diagnosis-evidence-links [data-blueprint36-evidence-link="diagnosis"]',
        '#fault-sandbox-evidence-trace-rows [data-evidence-trace-id="ET-04"]',
        '#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row="evidence-chain"]',
        '#fault-sandbox-evidence-trace-rows [data-blueprint-row-pattern="shared-v1"]',
        "#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-link-token",
        '#fault-sandbox-evidence-trace-rows [data-evidence-trace-id="ET-04"] [data-link-kind="report"]',
        "#fault-sandbox-report-preview",
        '#sandbox-report-strip[data-inspector-role="bottom-report-strip"]',
        '#fault-sandbox-report-section-rows [data-blueprint-report-row="review-package-section"]',
        '#fault-sandbox-report-section-rows [data-blueprint36-report-row="replay-report"]',
        '#fault-sandbox-report-section-rows [data-blueprint-row-pattern="shared-v1"]',
        "#fault-sandbox-report-section-rows .sandbox-report-section-decision",
        "#fault-sandbox-report-section-rows .sandbox-report-link-token",
        '#fault-sandbox-report-section-rows [data-report-section-id="RP-06"]',
        "#sandbox-review-package-panel",
        '#sandbox-review-package-panel[data-unified-aux-panel="review-package"][data-unified-panel-state="open"]',
        '#sandbox-review-package-panel [data-blueprint-row-pattern="shared-v1"]',
        '#sandbox-review-package-review-rows [data-blueprint36-package-row="review-package-review"]',
        '#sandbox-review-package-report-rows [data-blueprint36-package-row="review-package-report"]',
        "#sandbox-review-package-panel .blueprint-row-token",
        "#sandbox-review-package-panel .sandbox-review-package-link-token",
    ]:
        assert selector in script
    for token in [
        "vertical_scroll_ok",
        "horizontal_overflow_count",
        "logic_top_band_height",
        "max_logic_top_band_height",
        '"max_logic_top_band_height": 104',
        "clip_surfaces",
        "clipped_surfaces",
        "missing_visible_surfaces",
        "missing_existing_surfaces",
        "page.screenshot",
        "controller_truth_modified",
        "truth_effect",
        "certification_claim",
    ]:
        assert token in script


def test_deepseek_subproject_pages_declare_primary_flow_and_canvas_demotion():
    html_paths = [
        STATIC_ROOT / "requirements_intake" / "index.html",
        STATIC_ROOT / "logic_builder" / "index.html",
        STATIC_ROOT / "fault_injection_prepare" / "index.html",
        STATIC_ROOT / "fault_injection_sandbox" / "index.html",
    ]

    for path in html_paths:
        html = path.read_text(encoding="utf-8")
        assert 'data-primary-flow="deepseek-v4-pro-ui-workbench"' in html, path
        assert 'data-canvas-status="degraded-backup"' in html, path


def test_deepseek_v4_pro_routing_doc_freezes_canvas_branch():
    doc = (
        REPO_ROOT
        / "docs"
        / "coordination"
        / "deepseek-v4-pro-ui-workbench-routing.md"
    ).read_text(encoding="utf-8")

    assert "DeepSeek V4 Pro driven requirements" in doc
    assert "/requirements-intake" in doc
    assert "/logic-builder" in doc
    assert "/fault-injection-prepare" in doc
    assert "/fault-injection-sandbox" in doc
    assert "Canvas/workbench branch" in doc
    assert "frozen and downgraded to a backup feature module" in doc
    assert "unless the user explicitly asks for the canvas branch/module by name" in doc


def test_deepseek_live_full_chain_script_is_real_deepseek_only_and_gated():
    script = (REPO_ROOT / "scripts" / "deepseek_live_full_chain.py").read_text(encoding="utf-8")

    assert "DEEPSEEK_API_KEY" in script
    assert "DeepSeek_API_key" in script
    assert '"provider": "deepseek"' in script
    assert '"allow_fallback": False' in script
    assert "build_requirements_intake_analysis_response" in script
    assert "build_requirements_logic_drawing_response" in script
    assert "build_requirements_fault_injection_prepare_response" in script
    assert "build_requirements_fault_injection_sandbox_response" in script
    assert "artifacts/deepseek-live-full-chain" in script
    assert "minimax" not in script.lower()


def test_dev_server_resolves_deepseek_key_for_requirements_ui():
    script = (REPO_ROOT / "scripts" / "dev-serve.sh").read_text(encoding="utf-8")

    assert "resolve_deepseek_key" in script
    assert "DEEPSEEK_API_KEY" in script
    assert "DeepSeek_API_key" in script
    assert 'export DEEPSEEK_API_KEY="$KEY"' in script
    assert "DeepSeek key found" in script
    assert 'http://127.0.0.1:$PORT/index.html' in script
    assert 'http://127.0.0.1:$PORT/workbench' not in script
