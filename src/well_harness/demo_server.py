"""Small local UI server for the deterministic demo reasoning layer."""

from __future__ import annotations

import argparse
from dataclasses import replace
from functools import lru_cache
import json
import re
from typing import Any
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from well_harness.demo import answer_demo_prompt, demo_answer_to_payload
from well_harness.controller_adapter import build_reference_controller_adapter
from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
from well_harness.adapters.bleed_air_adapter import build_bleed_air_controller_adapter
from well_harness.adapters.efds_adapter import build_efds_controller_adapter
from well_harness.document_intake import (
    apply_safe_schema_repairs,
    assess_intake_packet,
    build_clarification_brief,
    intake_packet_from_dict,
    intake_packet_to_dict,
    intake_template_payload,
)
from well_harness.models import HarnessConfig, PilotInputs, ResolvedInputs
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.switches import LatchedThrottleSwitches, SwitchState
from well_harness.workbench_bundle import (
    archive_workbench_bundle,
    build_workbench_bundle,
    load_workbench_archive_manifest,
    load_workbench_archive_restore_payload,
)
from well_harness.ai_doc_analyzer import (
    P14SessionStore,
    analyze_document,
    convert_markdown_to_intake,
    evaluate_clarification,
    generate_prompt_document,
    run_pipeline_from_intake,
    _build_questions_from_ambiguities,
)


STATIC_DIR = Path(__file__).with_name("static")
REFERENCE_PACKET_DIR = Path(__file__).with_name("reference_packets")
REFERENCE_PACKET_PATH = REFERENCE_PACKET_DIR / "custom_reverse_control_v1.json"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}
SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"
SYSTEM_SNAPSHOT_POST_PATH = "/api/system-snapshot"
TRA_L4_LOCK_DEG = -14.0
MONITOR_TIMELINE_PATH = "/api/monitor-timeline"
WORKBENCH_BOOTSTRAP_PATH = "/api/workbench/bootstrap"
WORKBENCH_BUNDLE_PATH = "/api/workbench/bundle"
WORKBENCH_REPAIR_PATH = "/api/workbench/repair"
WORKBENCH_ARCHIVE_RESTORE_PATH = "/api/workbench/archive-restore"
WORKBENCH_RECENT_ARCHIVES_PATH = "/api/workbench/recent-archives"
MONITOR_RA_START_FT = 7.0
MONITOR_RA_RATE_FT_PER_S = 1.0
MONITOR_TRA_START_S = 1.0
MONITOR_TRA_RATE_DEG_PER_S = 10.0
MONITOR_TRA_LOCK_DEG = -14.0
MONITOR_VDT_START_S = 2.4
MONITOR_VDT_RATE_PERCENT_PER_S = 50.0
MONITOR_ACTIVE_END_S = 4.4
MONITOR_TIMELINE_END_S = 7.0
MONITOR_TIMELINE_COMPRESSION_RATIO = 10.0
MONITOR_ENGINE_RUNNING = True
MONITOR_AIRCRAFT_ON_GROUND = True
MONITOR_REVERSER_INHIBITED = False
MONITOR_EEC_ENABLE = True

# P14 AI Document Analyzer routes
P14_ANALYZE_PATH = "/api/p14/analyze-document"
P14_CLARIFY_PATH = "/api/p14/clarify"
P14_GENERATE_PATH = "/api/p14/generate-prompt"
# P15 Pipeline Integration routes
P15_CONVERT_PATH = "/api/p15/convert-to-intake"
P15_RUN_PIPELINE_PATH = "/api/p15/run-pipeline"
# Chat AI explain route (MiniMax LLM integration)
CHAT_EXPLAIN_PATH = "/api/chat/explain"
MONITOR_N1K = 35.0
MONITOR_MAX_N1K_DEPLOY_LIMIT = 60.0
LEVER_NUMERIC_INPUTS = {
    "tra_deg": {"default": 0.0, "min": -32.0, "max": 0.0},
    "radio_altitude_ft": {"default": 5.0, "min": 0.0, "max": 20.0},
    "n1k": {"default": 35.0, "min": 0.0, "max": 120.0},
    "max_n1k_deploy_limit": {"default": 60.0, "min": 0.1, "max": 120.0},
}
LEVER_BOOLEAN_INPUTS = {
    "engine_running": True,
    "aircraft_on_ground": True,
    "reverser_inhibited": False,
    "eec_enable": True,
}
LEVER_FEEDBACK_MODES = {
    "auto_scrubber",
    "manual_feedback_override",
}
LEVER_SNAPSHOT_FAULT_NODE_ALIASES = {
    "sw1_input": "sw1",
    "sw2_input": "sw2",
}
LEVER_SNAPSHOT_FAULT_NODES = {
    "sw1",
    "sw2",
    "radio_altitude_ft",
    "n1k",
    "tls115",
    "logic1",
    "logic2",
    "logic3",
    "logic4",
    "thr_lock",
    "vdt90",
    "sw1_input",
    "sw2_input",
}
LEVER_SNAPSHOT_FAULT_TYPES = {
    "stuck_off",
    "stuck_on",
    "sensor_zero",
    "logic_stuck_false",
    "cmd_blocked",
}
FAULT_INJECTION_REASON = "fault_injection"


class DemoRequestHandler(BaseHTTPRequestHandler):
    """Serve the static demo shell and a thin JSON API around DemoAnswer."""

    server_version = "WellHarnessDemo/1.0"

    def log_message(self, format, *args):  # noqa: A002 - BaseHTTPRequestHandler API
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == MONITOR_TIMELINE_PATH:
            self._send_json(200, monitor_timeline_payload())
            return
        if parsed.path == WORKBENCH_BOOTSTRAP_PATH:
            self._send_json(200, workbench_bootstrap_payload())
            return
        if parsed.path == SYSTEM_SNAPSHOT_PATH:
            system_id = parsed.query.split("system_id=")[1].split("&")[0] if "system_id=" in parsed.query else "thrust-reverser"
            self._send_json(200, system_snapshot_payload(system_id))
            return
        if parsed.path == WORKBENCH_RECENT_ARCHIVES_PATH:
            self._send_json(200, workbench_recent_archives_payload())
            return

        # Phase 3: chat.html is the new default entry point
        if parsed.path in ("", "/"):
            self._serve_static("chat.html")
            return

        # Backward-compat aliases (expert sub-path)
        if parsed.path in ("/demo.html", "/expert/demo.html"):
            self._serve_static("demo.html")
            return

        if parsed.path in ("/workbench.html", "/expert/workbench.html"):
            self._serve_static("workbench.html")
            return

        if parsed.path in ("/ai-doc-analyzer.html", "/expert/ai-doc-analyzer.html"):
            self._serve_static("ai-doc-analyzer.html")
            return

        relative_path = unquote(parsed.path.lstrip("/"))
        if relative_path and Path(relative_path).suffix in CONTENT_TYPES:
            self._serve_static(relative_path)
            return

        self._send_json(404, {"error": "not_found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path not in {
            "/api/demo",
            "/api/lever-snapshot",
            SYSTEM_SNAPSHOT_POST_PATH,
            WORKBENCH_BUNDLE_PATH,
            WORKBENCH_REPAIR_PATH,
            WORKBENCH_ARCHIVE_RESTORE_PATH,
            P14_ANALYZE_PATH,
            P14_CLARIFY_PATH,
            P14_GENERATE_PATH,
            P15_CONVERT_PATH,
            P15_RUN_PIPELINE_PATH,
            CHAT_EXPLAIN_PATH,
        }:
            self._send_json(404, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            self._send_json(400, {"error": "invalid_content_length"})
            return

        # Guard: reject oversized payloads before reading
        if content_length and content_length > _MAX_DOCUMENT_BYTES:
            self._send_json(413, {"error": "payload_too_large", "message": f"Request body exceeds maximum of {_MAX_DOCUMENT_BYTES} bytes."})
            return

        # Guard: enforce Content-Type whitelist (defense-in-depth; browser enforces this too)
        content_type = self.headers.get("Content-Type", "").split(";")[0].strip()
        allowed_types = {"application/json", "text/plain", "application/x-www-form-urlencoded"}
        if content_type and content_type not in allowed_types:
            self._send_json(415, {"error": "unsupported_media_type", "message": f"Content-Type '{content_type}' is not supported. Use application/json or text/plain."})
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            request_payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "invalid_json"})
            return
        if not isinstance(request_payload, dict):
            self._send_json(400, {"error": "invalid_json_object"})
            return

        if parsed.path == "/api/lever-snapshot":
            lever_inputs, error_payload = parse_lever_snapshot_request(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return

            fault_injections = lever_inputs.pop("_fault_injections", None)
            self._send_json(
                200,
                lever_snapshot_payload(
                    **lever_inputs,
                    fault_injections=fault_injections,
                ),
            )
            return
        if parsed.path == SYSTEM_SNAPSHOT_POST_PATH:
            system_id = request_payload.get("system_id")
            snapshot = request_payload.get("snapshot")
            if not system_id:
                self._send_json(400, {"error": "missing system_id"})
                return
            if not isinstance(snapshot, dict):
                self._send_json(400, {"error": "snapshot must be a dict"})
                return
            result = system_snapshot_post_payload(system_id, snapshot)
            if result.get("error"):
                self._send_json(404, result)
                return
            self._send_json(200, result)
            return
        if parsed.path == WORKBENCH_BUNDLE_PATH:
            response_payload, error_payload = build_workbench_bundle_response(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == WORKBENCH_REPAIR_PATH:
            response_payload, error_payload = build_workbench_safe_repair_response(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == WORKBENCH_ARCHIVE_RESTORE_PATH:
            response_payload, error_payload = build_workbench_archive_restore_response(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return

        # P14 AI Document Analyzer handlers
        if parsed.path == P14_ANALYZE_PATH:
            response_payload, error_payload = _handle_p14_analyze(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == P14_CLARIFY_PATH:
            response_payload, error_payload = _handle_p14_clarify(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == P14_GENERATE_PATH:
            response_payload, error_payload = _handle_p14_generate(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return

        # Chat AI explain handler (MiniMax LLM)
        if parsed.path == CHAT_EXPLAIN_PATH:
            response_payload, error_payload = _handle_chat_explain(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return

        # P15 Pipeline Integration handlers
        if parsed.path == P15_CONVERT_PATH:
            response_payload, error_payload = _handle_p15_convert(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return
        if parsed.path == P15_RUN_PIPELINE_PATH:
            response_payload, error_payload = _handle_p15_run_pipeline(request_payload)
            if error_payload is not None:
                self._send_json(400, error_payload)
                return
            self._send_json(200, response_payload)
            return

        prompt = str(request_payload.get("prompt", "")).strip()
        if not prompt:
            self._send_json(400, {"error": "missing_prompt"})
            return

        answer = answer_demo_prompt(prompt)
        self._send_json(200, demo_answer_to_payload(answer))

    def _serve_static(self, relative_path: str):
        static_root = STATIC_DIR.resolve()
        target_path = (static_root / relative_path).resolve()
        if target_path.parent != static_root or not target_path.is_file():
            self._send_json(404, {"error": "not_found"})
            return

        content_type = CONTENT_TYPES.get(target_path.suffix, "application/octet-stream")
        self._send_bytes(200, target_path.read_bytes(), content_type)

    def _send_json(self, status_code: int, payload: dict):
        # Compact JSON: no indentation (machine-to-machine API, not human-readable)
        response = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(status_code, response, "application/json; charset=utf-8")

    def _send_bytes(self, status_code: int, body: bytes, content_type: str):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# P14 AI Document Analyzer handlers
# ---------------------------------------------------------------------------

# Module-level session store singleton (created lazily via P14SessionStore())
_p14_session_store: P14SessionStore | None = None


def _get_p14_store() -> P14SessionStore:
    global _p14_session_store
    if _p14_session_store is None:
        _p14_session_store = P14SessionStore()
    return _p14_session_store


# Server-side DoS guard: 10 MB, aligned with browser client limit.
_MAX_DOCUMENT_BYTES = 10 * 1024 * 1024  # 10 MB production limit


_MINIMAX_API_KEY: str | None = None


def _get_minimax_api_key() -> str:
    global _MINIMAX_API_KEY
    if _MINIMAX_API_KEY is None:
        key_path = Path.home() / ".minimax_key"
        if key_path.exists():
            _MINIMAX_API_KEY = key_path.read_text().strip()
        else:
            _MINIMAX_API_KEY = ""
    return _MINIMAX_API_KEY


def _handle_chat_explain(request_payload: dict) -> tuple[dict | None, dict | None]:
    """Handle POST /api/chat/explain — use MiniMax LLM to generate a contextual explanation.

    Input:  {
        "question": str,          # user's natural language question
        "system_id": str,         # e.g. "thrust-reverser"
        "prompt": str,           # original user text
        "tra_deg": float,
        "radio_altitude_ft": float,
        "engine_running": bool,
        "aircraft_on_ground": bool,
        "reverser_inhibited": bool,
        "eec_enable": bool,
        "n1k": float,
        "feedback_mode": str,
        "lever_snapshot": dict | None,   # optional pre-fetched lever-snapshot data
        "node_states": dict[str, str],   # optional truth-engine node state map
    }

    Output: {
        "explanation": str,
        "highlighted_nodes": list[str],
        "suggestion_nodes": list[str],
        "confidence": float,
    }
    """
    question = request_payload.get("question", "")
    system_id = request_payload.get("system_id", "thrust-reverser")
    snapshot = request_payload.get("lever_snapshot") or {}
    demo_answer = request_payload.get("demo_answer") or {}
    node_states = request_payload.get("node_states", {})

    if not question:
        return None, {"error": "missing_question", "message": "question field is required."}
    if not isinstance(node_states, dict):
        node_states = {}

    api_key = _get_minimax_api_key()
    if not api_key:
        return None, {"error": "minimax_api_key_missing", "message": "MiniMax API key not found. Add to ~/.minimax_key."}

    # Build a concise context summary from the snapshot data
    nodes = snapshot.get("nodes", [])
    logic = snapshot.get("logic", {})
    outputs = snapshot.get("outputs", {})

    # Build node state summary
    node_lines = []
    for node in nodes:
        state_label = {"active": "亮(激活)", "inactive": "暗(未激活)", "blocked": "红(阻塞)"}.get(
            node.get("state", ""), node.get("state", "?")
        )
        node_lines.append(f"  {node.get('id', '?')}: {state_label}")
    node_summary = "\n".join(node_lines) if node_lines else "  (无节点数据)"

    # Build logic gate summary
    logic_lines = []
    for gate_id in ("logic1", "logic2", "logic3", "logic4"):
        info = logic.get(gate_id, {})
        active = info.get("active", False)
        failed = info.get("failed_conditions", [])
        status = f"激活" if active else (f"阻塞: {', '.join(failed)}" if failed else "未激活")
        logic_lines.append(f"  {gate_id}: {status}")
    logic_summary = "\n".join(logic_lines)

    # Build output summary
    output_lines = [
        f"  THR_LOCK: {'已释放' if outputs.get('throttle_electronic_lock_release_cmd') else '未释放'}",
        f"  VDT90: {'触发' if outputs.get('deploy_90_percent_vdt') else '未触发'}",
    ]
    output_summary = "\n".join(output_lines)

    if not node_states and nodes:
        for node in nodes:
            node_id = node.get("id")
            node_state = node.get("state")
            if isinstance(node_id, str) and isinstance(node_state, str):
                node_states[node_id] = node_state

    node_state_lines: list[str] = []
    for node_id, node_state in node_states.items():
        state_label = {"active": "active(已激活)", "inactive": "inactive(未激活)", "blocked": "blocked(阻塞)"}.get(
            str(node_state), str(node_state)
        )
        node_state_lines.append(f"  {node_id}: {state_label}")
    node_states_summary = "\n".join(node_state_lines) if node_state_lines else "  (未提供 node_states)"

    # Phase C: When demo_answer is provided (non-thrust-reverser systems),
    # build context from the demo answer instead of lever-snapshot
    if demo_answer and not nodes:
        matched = demo_answer.get("matched_node", "")
        intent = demo_answer.get("intent", "")
        target_logic = demo_answer.get("target_logic", "")
        evidence = demo_answer.get("evidence", [])
        demo_text = demo_answer.get("answer", "") or demo_answer.get("reasoning", "")
        node_summary = f"  匹配节点: {matched}" if matched else "  (通用问题)"
        logic_summary = f"  目标逻辑: {target_logic}" if target_logic else ""
        evidence_str = "\n  ".join(f"- {e}" for e in evidence) if evidence else "  无"
        output_summary = f"""  推理结果: {demo_text[:200]}
  证据链:
  {evidence_str}""" if demo_text else "  (无推理结果)"

    system_labels = {
        "thrust-reverser": "Thrust Reverser（反推力系统）",
        "landing-gear": "Landing Gear（起落架）",
        "bleed-air": "Bleed Air Valve（引气系统）",
        "efds": "EFDS（干扰弹系统）",
    }
    system_label = system_labels.get(system_id, system_id)

    # Build system prompt for MiniMax
    system_prompt = f"""你是控制逻辑分析助手。用户正在使用一个确定性控制逻辑推理引擎来诊断 {system_label} 的状态。

你会收到：
1. 用户的问题
2. 真值引擎返回的节点状态（node_states）—— 这是100%准确的
3. 当前系统的逻辑链路定义和补充上下文

你的任务：
- 用中文解释节点状态变化的原因和影响
- 在 highlighted_nodes 中列出你讨论到的所有节点ID（如 L1, TLS, VDT90, THR_LOCK）
- 在 suggestion_nodes 中列出你建议用户进一步检查的节点ID
- 在 confidence 中评估你对自己回答的信心（0.0-1.0）

你绝对不能：
- 自己推断节点应该是 active 还是 blocked
- 与 node_states 中的真值结果矛盾
- 编造不在当前系统中的节点ID

当前 node_states（真值）：
{node_states_summary}

当前链路补充上下文：
=== 节点状态 ===
{node_summary}

=== 逻辑门状态 ===
{logic_summary}

=== 输出指令状态 ===
{output_summary}

你的回复要求：
1. 基于以上真实数据，用中文（夹杂必要英文技术术语）解释当前链路状态
2. 重点回答用户的问题："{question}"
3. 如果某个逻辑门被阻塞，分析原因并说明下游影响
4. 如果链路完整激活，解释激活路径
5. 保持专业但易懂，适合航空工程师阅读
6. explanation 控制在 200-400 字以内
7. 只返回 JSON，不要加 markdown 代码块

请用以下 JSON 格式回复：
{{"explanation": "你的中文解释", "highlighted_nodes": ["节点ID1", "节点ID2"], "suggestion_nodes": ["建议检查的ID"], "confidence": 0.95}}"""

    user_prompt = f"用户问题：{question}"

    try:
        import urllib.request
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "minimax-m2.7-highspeed",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 600,
            "stream": False,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        # MiniMax API response structure: choices[0].message.content
        choices = result.get("choices", [])
        if choices:
            raw_content = choices[0].get("message", {}).get("content", "")
        else:
            raw_content = result.get("choices", [{}])[0].get("text", "")

        if not raw_content:
            # Fallback: try alternative response field
            raw_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not raw_content:
                return None, {"error": "minimax_empty_response", "message": "MiniMax returned empty explanation."}

        try:
            json_str = re.sub(r"^```json\s*", "", raw_content.strip())
            json_str = re.sub(r"^```\s*", "", json_str)
            json_str = re.sub(r"\s*```$", "", json_str)
            parsed = json.loads(json_str)
            if not isinstance(parsed, dict):
                raise ValueError("MiniMax response was not a JSON object.")
            explanation = parsed.get("explanation", raw_content)
            highlighted_nodes = parsed.get("highlighted_nodes", [])
            suggestion_nodes = parsed.get("suggestion_nodes", [])
            confidence_raw = parsed.get("confidence", 0.5)
        except (json.JSONDecodeError, TypeError, ValueError):
            explanation = raw_content
            highlighted_nodes = []
            suggestion_nodes = []
            confidence_raw = 0.5

        if not isinstance(highlighted_nodes, list):
            highlighted_nodes = []
        if not isinstance(suggestion_nodes, list):
            suggestion_nodes = []
        try:
            confidence = max(0.0, min(1.0, float(confidence_raw)))
        except (TypeError, ValueError):
            confidence = 0.5

        return {
            "explanation": str(explanation).strip(),
            "highlighted_nodes": [str(node_id).strip() for node_id in highlighted_nodes if str(node_id).strip()],
            "suggestion_nodes": [str(node_id).strip() for node_id in suggestion_nodes if str(node_id).strip()],
            "confidence": confidence,
        }, None

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return None, {"error": "minimax_http_error", "message": f"HTTP {e.code}: {body}"}
    except Exception as exc:
        return None, {"error": "minimax_error", "message": str(exc)}


def _handle_p14_analyze(request_payload: dict) -> tuple[dict | None, dict | None]:
    """Handle POST /api/p14/analyze-document."""
    session_id = request_payload.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return None, {"error": "missing_session_id", "message": "session_id is required and must be a non-empty string."}

    document_text = request_payload.get("document_text")
    if not isinstance(document_text, str):
        return None, {"error": "missing_document_text", "message": "document_text is required."}
    if not document_text.strip():
        return None, {"error": "empty_document", "message": "document_text must not be empty."}
    if len(document_text.encode("utf-8")) > _MAX_DOCUMENT_BYTES:
        return None, {
            "error": "document_too_large",
            "message": f"document_text exceeds maximum size of {_MAX_DOCUMENT_BYTES} bytes (10MB server-side limit).",
        }

    document_name = request_payload.get("document_name", "untitled")
    if not isinstance(document_name, str) or len(document_name) > 255:
        return None, {"error": "invalid_document_name", "message": "document_name must be a string of at most 255 characters."}

    store = _get_p14_store()
    session = store.create(session_id.strip(), document_text, document_name.strip() or "untitled")
    ambiguities_or_error = analyze_document(document_text)
    if isinstance(ambiguities_or_error, dict):
        return None, {
            "error": ambiguities_or_error.get("error", "analysis_failed"),
            "message": ambiguities_or_error.get("message", str(ambiguities_or_error)),
        }
    ambiguities = ambiguities_or_error
    session.ambiguities = ambiguities
    session.questions = _build_questions_from_ambiguities(ambiguities)
    # If no ambiguities were detected, mark session complete immediately
    if not session.questions:
        session.is_complete = True
    store.update(session)

    # Return first question alongside ambiguities so UI can start the loop immediately
    first_q = session.next_question()
    return {
        "session_id": session_id,
        "ambiguities": [a.to_dict() for a in ambiguities],
        "total_count": len(ambiguities),
        "first_question": first_q.to_dict() if first_q else None,
        "progress": session.progress(),
        "is_complete": session.is_complete,
    }, None


def _handle_p14_clarify(request_payload: dict) -> tuple[dict | None, dict | None]:
    """Handle POST /api/p14/clarify."""
    session_id = request_payload.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return None, {"error": "missing_session_id", "message": "session_id is required."}

    answer = request_payload.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        return None, {"error": "empty_answer", "message": "answer must be a non-empty string."}

    store = _get_p14_store()
    session = store.get(session_id.strip())
    if session is None:
        return None, {"error": "session_not_found", "message": f"Session '{session_id}' not found."}

    result = evaluate_clarification(session, answer.strip())
    store.update(session)

    return {
        "session_id": session_id,
        "next_question": result.next_question.to_dict() if result.next_question else None,
        "progress": result.progress,
        "is_complete": result.is_complete,
    }, None


def _handle_p14_generate(request_payload: dict) -> tuple[dict | None, dict | None]:
    """Handle POST /api/p14/generate-prompt."""
    session_id = request_payload.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return None, {"error": "missing_session_id", "message": "session_id is required."}

    store = _get_p14_store()
    session = store.get(session_id.strip())
    if session is None:
        return None, {"error": "session_not_found", "message": f"Session '{session_id}' not found."}

    if not session.is_complete:
        return None, {"error": "session_incomplete", "message": "Cannot generate prompt until all clarification questions are answered."}

    if session.generated_prompt is None:
        prompt_doc = generate_prompt_document(session)
        # generate_prompt_document returns str | dict; dict = error
        if isinstance(prompt_doc, dict):
            return None, {"error": prompt_doc.get("error", "generation_failed"), "message": prompt_doc.get("message", str(prompt_doc))}
        session.generated_prompt = prompt_doc
        store.update(session)

    word_count = len(session.generated_prompt.split())
    return {
        "session_id": session_id,
        "prompt_document": session.generated_prompt,
        "word_count": word_count,
    }, None


# ---------------------------------------------------------------------------
# P15 Pipeline Integration handlers
# ---------------------------------------------------------------------------


def _handle_p15_convert(request_payload: dict) -> tuple[dict | None, dict | None]:
    """Handle POST /api/p15/convert-to-intake.

    Input:  {session_id: str, system_id?: str}
    Output: {intake_packet: dict, validation: {valid: bool, errors: list}}
    """
    session_id = request_payload.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return None, {"error": "missing_session_id", "message": "session_id is required and must be a non-empty string."}

    system_id = request_payload.get("system_id", "generated-system")

    store = _get_p14_store()
    session = store.get(session_id.strip())
    if session is None:
        return None, {"error": "session_not_found", "message": f"Session '{session_id}' not found."}

    prompt_doc = session.generated_prompt
    if prompt_doc is None:
        # Try to generate it on demand
        if not session.is_complete:
            return None, {"error": "session_incomplete", "message": "Cannot convert: session clarification not complete."}
        result = generate_prompt_document(session)
        if isinstance(result, dict):
            return None, {"error": result.get("error", "generation_failed"), "message": result.get("message", str(result))}
        prompt_doc = result
        session.generated_prompt = prompt_doc
        store.update(session)

    intake_dict = convert_markdown_to_intake(prompt_doc, system_id)
    if isinstance(intake_dict, dict) and "error" in intake_dict:
        return None, {"error": intake_dict.get("error", "conversion_failed"), "message": intake_dict.get("message", str(intake_dict))}

    # Basic validation
    errors: list[str] = []
    required_fields = ["system_id", "title", "objective", "components", "logic_nodes"]
    for field in required_fields:
        if field not in intake_dict or not intake_dict[field]:
            errors.append(f"Missing required field: {field}")

    return {
        "intake_packet": intake_dict,
        "validation": {"valid": len(errors) == 0, "errors": errors},
    }, None


def _handle_p15_run_pipeline(request_payload: dict) -> tuple[dict | None, dict | None]:
    """Handle POST /api/p15/run-pipeline.

    Input:  {intake_packet: dict}
    Output: {assessment, bundle, system_snapshot}
    """
    intake_packet = request_payload.get("intake_packet")
    if not isinstance(intake_packet, dict):
        return None, {"error": "missing_intake_packet", "message": "intake_packet is required and must be a dict."}

    result = run_pipeline_from_intake(intake_packet)
    if isinstance(result, dict) and "error" in result:
        return None, {"error": result.get("error", "pipeline_failed"), "message": result.get("message", str(result))}

    return result, None


def _clamp_tra(tra_deg: float, config: HarnessConfig) -> float:
    return max(config.reverse_travel_min_deg, min(config.reverse_travel_max_deg, tra_deg))


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _parse_float_input(request_payload: dict, field_name: str, options: dict) -> tuple[float | None, dict | None]:
    raw_value = request_payload.get(field_name, options["default"])
    if isinstance(raw_value, bool):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    return _clamp(value, options["min"], options["max"]), None


def _parse_bool_input(request_payload: dict, field_name: str, default: bool) -> tuple[bool | None, dict | None]:
    raw_value = request_payload.get(field_name, default)
    if isinstance(raw_value, bool):
        return raw_value, None
    if isinstance(raw_value, str):
        normalized = raw_value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True, None
        if normalized in {"false", "0", "no", "off"}:
            return False, None
    return None, {
        "error": "invalid_lever_snapshot_input",
        "field": field_name,
        "message": f"{field_name} must be boolean.",
    }


def _parse_feedback_mode(request_payload: dict) -> tuple[str | None, dict | None]:
    raw_value = request_payload.get("feedback_mode", "auto_scrubber")
    if not isinstance(raw_value, str):
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": "feedback_mode",
            "message": "feedback_mode must be a string.",
        }
    normalized = raw_value.strip()
    if normalized not in LEVER_FEEDBACK_MODES:
        return None, {
            "error": "invalid_lever_snapshot_input",
            "field": "feedback_mode",
            "message": "feedback_mode must be auto_scrubber or manual_feedback_override.",
        }
    return normalized, None


def _normalize_fault_injection_node_id(node_id: str) -> str:
    normalized = str(node_id or "").strip()
    return LEVER_SNAPSHOT_FAULT_NODE_ALIASES.get(normalized, normalized)


def _fault_injection_map(fault_injections: list[dict] | None) -> dict[str, str]:
    fault_map: dict[str, str] = {}
    for fault in fault_injections or []:
        node_id = _normalize_fault_injection_node_id(fault.get("node_id", ""))
        fault_type = str(fault.get("fault_type", "")).strip()
        if node_id and fault_type:
            fault_map[node_id] = fault_type
    return fault_map


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _apply_switch_fault_injections(
    switch_state: SwitchState,
    fault_map: dict[str, str],
) -> SwitchState:
    sw1 = switch_state.sw1
    if fault_map.get("sw1") == "stuck_off":
        sw1 = False
    elif fault_map.get("sw1") == "stuck_on":
        sw1 = True

    sw2 = switch_state.sw2
    if fault_map.get("sw2") == "stuck_off":
        sw2 = False
    elif fault_map.get("sw2") == "stuck_on":
        sw2 = True

    if sw1 == switch_state.sw1 and sw2 == switch_state.sw2:
        return switch_state

    return SwitchState(
        previous_tra_deg=switch_state.previous_tra_deg,
        sw1=sw1,
        sw2=sw2,
    )


def _apply_sensor_fault_injections(sensors, fault_map: dict[str, str]):
    sensor_updates = {}

    if fault_map.get("tls115") == "sensor_zero":
        sensor_updates["tls_unlocked_ls"] = False

    if fault_map.get("vdt90") == "cmd_blocked":
        sensor_updates["deploy_90_percent_vdt"] = False

    if not sensor_updates:
        return sensors

    return replace(sensors, **sensor_updates)


def _apply_output_fault_injections(outputs, fault_map: dict[str, str]):
    output_updates = {}

    if fault_map.get("tls115") == "sensor_zero":
        output_updates["tls_115vac_cmd"] = False

    if fault_map.get("logic1") == "logic_stuck_false":
        output_updates["logic1_active"] = False
        output_updates["tls_115vac_cmd"] = False

    if fault_map.get("logic2") == "logic_stuck_false":
        output_updates["logic2_active"] = False
        output_updates["etrac_540vdc_cmd"] = False

    if fault_map.get("logic3") == "logic_stuck_false":
        output_updates["logic3_active"] = False
        output_updates["eec_deploy_cmd"] = False
        output_updates["pls_power_cmd"] = False
        output_updates["pdu_motor_cmd"] = False

    if fault_map.get("logic4") == "logic_stuck_false":
        output_updates["logic4_active"] = False
        output_updates["throttle_electronic_lock_release_cmd"] = False

    if fault_map.get("thr_lock") == "cmd_blocked":
        output_updates["throttle_electronic_lock_release_cmd"] = False

    if not output_updates:
        return outputs

    return replace(outputs, **output_updates)


def _fault_reason(fault_type: str) -> str:
    return f"{FAULT_INJECTION_REASON}:{fault_type}"


def _set_faulted_node_state(
    node_payload: dict | None,
    *,
    state: str,
    reason: str | None = None,
) -> None:
    if node_payload is None:
        return
    node_payload["state"] = state
    if state == "blocked":
        blocked_by = list(node_payload.get("blocked_by") or [])
        if reason:
            _append_unique(blocked_by, reason)
        node_payload["blocked_by"] = blocked_by
        return
    node_payload["blocked_by"] = []


def _apply_fault_injections_to_snapshot_payload(
    result: dict,
    fault_injections: list[dict] | None,
) -> dict:
    fault_map = _fault_injection_map(fault_injections)
    if not fault_map:
        return result

    nodes_by_id = {
        node["id"]: node
        for node in result.get("nodes", [])
        if isinstance(node, dict) and "id" in node
    }
    input_payload = result.get("input")
    hud_payload = result.get("hud")
    outputs_payload = result.get("outputs")
    logic_payload = result.get("logic")

    for node_id, fault_type in fault_map.items():
        reason = _fault_reason(fault_type)

        if node_id == "sw1":
            active = fault_type == "stuck_on"
            if isinstance(hud_payload, dict):
                hud_payload["sw1"] = active
            _set_faulted_node_state(
                nodes_by_id.get("sw1"),
                state="active" if active else "inactive",
            )
            continue

        if node_id == "sw2":
            active = fault_type == "stuck_on"
            if isinstance(hud_payload, dict):
                hud_payload["sw2"] = active
            _set_faulted_node_state(
                nodes_by_id.get("sw2"),
                state="active" if active else "inactive",
            )
            continue

        if node_id == "radio_altitude_ft" and fault_type == "sensor_zero":
            if isinstance(input_payload, dict):
                input_payload["radio_altitude_ft"] = 0.0
            if isinstance(hud_payload, dict):
                hud_payload["radio_altitude_ft"] = 0.0
            _set_faulted_node_state(nodes_by_id.get("radio_altitude_ft"), state="inactive")
            continue

        if node_id == "n1k" and fault_type == "sensor_zero":
            if isinstance(input_payload, dict):
                input_payload["n1k"] = 0.0
            if isinstance(hud_payload, dict):
                hud_payload["n1k"] = 0.0
            _set_faulted_node_state(nodes_by_id.get("n1k"), state="inactive")
            continue

        if node_id == "tls115" and fault_type == "sensor_zero":
            if isinstance(outputs_payload, dict):
                outputs_payload["tls_115vac_cmd"] = False
            _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
            continue

        if node_id in {"logic1", "logic2", "logic3", "logic4"} and fault_type == "logic_stuck_false":
            logic_entry = logic_payload.get(node_id) if isinstance(logic_payload, dict) else None
            if isinstance(logic_entry, dict):
                logic_entry["active"] = False
                failed_conditions = list(logic_entry.get("failed_conditions") or [])
                _append_unique(failed_conditions, reason)
                logic_entry["failed_conditions"] = failed_conditions

            if isinstance(outputs_payload, dict):
                outputs_payload[f"{node_id}_active"] = False

            _set_faulted_node_state(nodes_by_id.get(node_id), state="blocked", reason=reason)

            if node_id == "logic1":
                if isinstance(outputs_payload, dict):
                    outputs_payload["tls_115vac_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("tls115"), state="inactive")
            elif node_id == "logic2":
                if isinstance(outputs_payload, dict):
                    outputs_payload["etrac_540vdc_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("etrac_540v"), state="inactive")
            elif node_id == "logic3":
                if isinstance(outputs_payload, dict):
                    outputs_payload["eec_deploy_cmd"] = False
                    outputs_payload["pls_power_cmd"] = False
                    outputs_payload["pdu_motor_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("eec_deploy"), state="inactive")
                _set_faulted_node_state(nodes_by_id.get("pls_power"), state="inactive")
                _set_faulted_node_state(nodes_by_id.get("pdu_motor"), state="inactive")
            elif node_id == "logic4":
                if isinstance(outputs_payload, dict):
                    outputs_payload["throttle_electronic_lock_release_cmd"] = False
                _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
            continue

        if node_id == "thr_lock" and fault_type == "cmd_blocked":
            if isinstance(outputs_payload, dict):
                outputs_payload["throttle_electronic_lock_release_cmd"] = False
            _set_faulted_node_state(nodes_by_id.get("thr_lock"), state="blocked", reason=reason)
            continue

        if node_id == "vdt90" and fault_type == "cmd_blocked":
            if isinstance(hud_payload, dict):
                hud_payload["deploy_90_percent_vdt"] = False
            _set_faulted_node_state(nodes_by_id.get("vdt90"), state="blocked", reason=reason)

    result["active_fault_node_ids"] = list(fault_map.keys())
    result["fault_injections"] = fault_injections or []
    return result


def parse_lever_snapshot_request(request_payload: dict) -> tuple[dict | None, dict | None]:
    lever_inputs = {}
    for field_name, options in LEVER_NUMERIC_INPUTS.items():
        value, error_payload = _parse_float_input(request_payload, field_name, options)
        if error_payload is not None:
            return None, error_payload
        lever_inputs[field_name] = value

    config = HarnessConfig()
    lever_inputs["tra_deg"] = _clamp_tra(lever_inputs["tra_deg"], config)

    for field_name, default in LEVER_BOOLEAN_INPUTS.items():
        value, error_payload = _parse_bool_input(request_payload, field_name, default)
        if error_payload is not None:
            return None, error_payload
        lever_inputs[field_name] = value

    feedback_mode, error_payload = _parse_feedback_mode(request_payload)
    if error_payload is not None:
        return None, error_payload
    lever_inputs["feedback_mode"] = feedback_mode

    deploy_position_percent, error_payload = _parse_float_input(
        request_payload,
        "deploy_position_percent",
        {"default": 0.0, "min": 0.0, "max": 100.0},
    )
    if error_payload is not None:
        return None, error_payload
    lever_inputs["deploy_position_percent"] = deploy_position_percent

    fault_injections = request_payload.get("fault_injections")
    if fault_injections is not None:
        if not isinstance(fault_injections, list):
            return None, {
                "error": "invalid_fault_injections",
                "message": "fault_injections must be a list",
            }
        normalized_faults = []
        for fault in fault_injections:
            if not isinstance(fault, dict):
                return None, {
                    "error": "invalid_fault_injections",
                    "message": "each fault_injection must be an object",
                }
            node_id = str(fault.get("node_id", "")).strip()
            fault_type = str(fault.get("fault_type", "")).strip()
            if node_id not in LEVER_SNAPSHOT_FAULT_NODES:
                return None, {
                    "error": "invalid_fault_injection_node",
                    "message": f"Unknown node_id: {node_id}",
                }
            if fault_type not in LEVER_SNAPSHOT_FAULT_TYPES:
                return None, {
                    "error": "invalid_fault_type",
                    "message": f"Unknown fault_type: {fault_type}",
                }
            normalized_faults.append(
                {
                    "node_id": _normalize_fault_injection_node_id(node_id),
                    "fault_type": fault_type,
                }
            )
        if normalized_faults:
            lever_inputs["_fault_injections"] = normalized_faults
    return lever_inputs, None


def default_workbench_archive_root() -> Path:
    return (Path.cwd() / "artifacts" / "workbench-bundles").resolve()


def reference_workbench_packet_payload() -> dict:
    return json.loads(REFERENCE_PACKET_PATH.read_text(encoding="utf-8"))


def recent_workbench_archive_summaries(*, limit: int = 6) -> list[dict]:
    archive_root = default_workbench_archive_root()
    if not archive_root.is_dir():
        return []

    summaries: list[dict] = []
    for archive_dir in archive_root.iterdir():
        if not archive_dir.is_dir():
            continue
        manifest_path = archive_dir / "archive_manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = load_workbench_archive_manifest(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue

        bundle = manifest.get("bundle") if isinstance(manifest.get("bundle"), dict) else {}
        files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
        summaries.append(
            {
                "archive_dir": str(archive_dir.resolve()),
                "manifest_path": str(manifest_path.resolve()),
                "created_at_utc": manifest.get("created_at_utc"),
                "system_id": bundle.get("system_id"),
                "system_title": bundle.get("system_title"),
                "bundle_kind": bundle.get("bundle_kind"),
                "ready_for_spec_build": bundle.get("ready_for_spec_build"),
                "selected_scenario_id": bundle.get("selected_scenario_id"),
                "selected_fault_mode_id": bundle.get("selected_fault_mode_id"),
                "has_workspace_handoff": files.get("workspace_handoff_json") is not None,
                "has_workspace_snapshot": files.get("workspace_snapshot_json") is not None,
            }
        )

    summaries.sort(
        key=lambda item: (
            str(item.get("created_at_utc") or ""),
            str(item.get("archive_dir") or ""),
        ),
        reverse=True,
    )
    return summaries[:limit]


def workbench_bootstrap_payload() -> dict:
    return {
        "template_packet": intake_template_payload(),
        "reference_packet": reference_workbench_packet_payload(),
        "default_archive_root": str(default_workbench_archive_root()),
        "recent_archives": recent_workbench_archive_summaries(),
    }


def workbench_recent_archives_payload() -> dict:
    return {
        "default_archive_root": str(default_workbench_archive_root()),
        "recent_archives": recent_workbench_archive_summaries(),
    }


def _optional_request_str(payload: dict, field_name: str) -> tuple[str | None, dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return None, None
    if not isinstance(raw_value, str):
        return None, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be a string when provided.",
        }
    normalized = raw_value.strip()
    return (normalized or None), None


def _optional_request_string_list(payload: dict, field_name: str) -> tuple[tuple[str, ...] | None, dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return None, None
    if not isinstance(raw_value, list) or any(not isinstance(item, str) for item in raw_value):
        return None, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be a list of strings when provided.",
        }
    return tuple(item.strip() for item in raw_value if item.strip()), None


def _optional_request_float(payload: dict, field_name: str, *, default: float) -> tuple[float, dict | None]:
    raw_value = payload.get(field_name, default)
    if isinstance(raw_value, bool):
        return default, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return default, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be numeric.",
        }
    if value <= 0:
        return default, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be greater than zero.",
        }
    return value, None


def _optional_request_object(payload: dict, field_name: str) -> tuple[dict | None, dict | None]:
    raw_value = payload.get(field_name)
    if raw_value is None:
        return None, None
    if not isinstance(raw_value, dict):
        return None, {
            "error": "invalid_workbench_request",
            "field": field_name,
            "message": f"{field_name} must be a JSON object when provided.",
        }
    return raw_value, None


def build_workbench_bundle_response(request_payload: dict) -> tuple[dict | None, dict | None]:
    packet_payload = request_payload.get("packet_payload")
    if not isinstance(packet_payload, dict):
        return None, {
            "error": "invalid_workbench_request",
            "field": "packet_payload",
            "message": "packet_payload must be a JSON object.",
        }
    try:
        packet = intake_packet_from_dict(packet_payload)
    except ValueError as exc:
        return None, {
            "error": "invalid_workbench_packet",
            "field": "packet_payload",
            "message": str(exc),
        }

    scenario_id, error_payload = _optional_request_str(request_payload, "scenario_id")
    if error_payload is not None:
        return None, error_payload
    fault_mode_id, error_payload = _optional_request_str(request_payload, "fault_mode_id")
    if error_payload is not None:
        return None, error_payload
    observed_symptoms, error_payload = _optional_request_str(request_payload, "observed_symptoms")
    if error_payload is not None:
        return None, error_payload
    evidence_links, error_payload = _optional_request_string_list(request_payload, "evidence_links")
    if error_payload is not None:
        return None, error_payload
    confirmed_root_cause, error_payload = _optional_request_str(request_payload, "confirmed_root_cause")
    if error_payload is not None:
        return None, error_payload
    repair_action, error_payload = _optional_request_str(request_payload, "repair_action")
    if error_payload is not None:
        return None, error_payload
    validation_after_fix, error_payload = _optional_request_str(request_payload, "validation_after_fix")
    if error_payload is not None:
        return None, error_payload
    residual_risk, error_payload = _optional_request_str(request_payload, "residual_risk")
    if error_payload is not None:
        return None, error_payload
    suggested_logic_change, error_payload = _optional_request_str(request_payload, "suggested_logic_change")
    if error_payload is not None:
        return None, error_payload
    reliability_gain_hypothesis, error_payload = _optional_request_str(
        request_payload,
        "reliability_gain_hypothesis",
    )
    if error_payload is not None:
        return None, error_payload
    guardrail_note, error_payload = _optional_request_str(request_payload, "guardrail_note")
    if error_payload is not None:
        return None, error_payload
    sample_period_s, error_payload = _optional_request_float(
        request_payload,
        "sample_period_s",
        default=0.5,
    )
    if error_payload is not None:
        return None, error_payload
    workspace_handoff, error_payload = _optional_request_object(request_payload, "workspace_handoff")
    if error_payload is not None:
        return None, error_payload
    workspace_snapshot, error_payload = _optional_request_object(request_payload, "workspace_snapshot")
    if error_payload is not None:
        return None, error_payload
    if workspace_handoff is None and workspace_snapshot is not None:
        derived_handoff = workspace_snapshot.get("handoff")
        if isinstance(derived_handoff, dict):
            workspace_handoff = derived_handoff

    archive_bundle = bool(request_payload.get("archive_bundle", False))
    try:
        bundle = build_workbench_bundle(
            packet,
            scenario_id=scenario_id,
            fault_mode_id=fault_mode_id,
            observed_symptoms=observed_symptoms,
            evidence_links=evidence_links or (),
            confirmed_root_cause=confirmed_root_cause,
            repair_action=repair_action,
            validation_after_fix=validation_after_fix,
            residual_risk=residual_risk,
            suggested_logic_change=suggested_logic_change,
            reliability_gain_hypothesis=reliability_gain_hypothesis,
            redundancy_reduction_or_guardrail_note=guardrail_note,
            sample_period_s=sample_period_s,
        )
    except ValueError as exc:
        return None, {
            "error": "invalid_workbench_selection",
            "message": str(exc),
        }

    archive = None
    if archive_bundle:
        archive = archive_workbench_bundle(
            bundle,
            default_workbench_archive_root(),
            workspace_handoff=workspace_handoff,
            workspace_snapshot=workspace_snapshot,
        )
    return {
        "bundle": bundle.to_dict(),
        "archive": archive.to_dict() if archive is not None else None,
        "archive_bundle": archive_bundle,
        "default_archive_root": str(default_workbench_archive_root()),
    }, None


def build_workbench_safe_repair_response(request_payload: dict) -> tuple[dict | None, dict | None]:
    packet_payload = request_payload.get("packet_payload")
    if not isinstance(packet_payload, dict):
        return None, {
            "error": "invalid_workbench_request",
            "field": "packet_payload",
            "message": "packet_payload must be a JSON object.",
        }
    if not request_payload.get("apply_all_safe", False):
        return None, {
            "error": "invalid_workbench_request",
            "field": "apply_all_safe",
            "message": "apply_all_safe must be true for safe schema repair requests.",
        }
    try:
        packet = intake_packet_from_dict(packet_payload)
    except ValueError as exc:
        return None, {
            "error": "invalid_workbench_packet",
            "field": "packet_payload",
            "message": str(exc),
        }

    repaired_packet, applied_suggestion_ids = apply_safe_schema_repairs(packet)
    if not applied_suggestion_ids:
        return None, {
            "error": "no_safe_schema_repairs",
            "message": "No safe schema repair suggestions are currently available for this packet.",
        }

    return {
        "packet_payload": intake_packet_to_dict(repaired_packet),
        "applied_suggestion_ids": list(applied_suggestion_ids),
        "intake_assessment": assess_intake_packet(repaired_packet),
        "clarification_brief": build_clarification_brief(repaired_packet),
    }, None


def build_workbench_archive_restore_response(request_payload: dict) -> tuple[dict | None, dict | None]:
    manifest_path, error_payload = _optional_request_str(request_payload, "manifest_path")
    if error_payload is not None:
        return None, error_payload
    if manifest_path is None:
        return None, {
            "error": "invalid_workbench_request",
            "field": "manifest_path",
            "message": "manifest_path must be a non-empty string.",
        }

    # SECURITY: reject path traversal attempts in relative paths
    if not Path(manifest_path).is_absolute():
        if ".." in str(manifest_path):
            return None, {"error": "invalid_manifest_path", "message": "Relative manifest_path with traversal is not allowed."}

    try:
        restore_payload = load_workbench_archive_restore_payload(manifest_path)
    except FileNotFoundError as exc:
        return None, {
            "error": "workbench_archive_not_found",
            "field": "manifest_path",
            "message": str(exc),
        }
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return None, {
            "error": "invalid_workbench_archive",
            "field": "manifest_path",
            "message": str(exc),
        }

    restore_payload["default_archive_root"] = str(default_workbench_archive_root())
    return restore_payload, None


def _canonical_pullback_sequence(tra_deg: float, config: HarnessConfig) -> list[float]:
    """Return a tiny canonical pullback path for the interactive UI scrubber."""
    target = _clamp_tra(tra_deg, config)
    if target >= 0.0:
        return [0.0]

    sequence: list[float] = []
    if target <= config.sw1_window.near_zero_deg:
        sequence.extend([-2.0] * 4)
    if target <= config.sw2_window.near_zero_deg:
        sequence.extend([-7.0] * 4)

    final_repeats = 4 if target <= config.logic3_tra_deg_threshold else 2
    sequence.extend([target] * final_repeats)
    return sequence


def _condition_payload(condition) -> dict:
    return {
        "name": condition.name,
        "current_value": condition.current_value,
        "comparison": condition.comparison,
        "threshold_value": condition.threshold_value,
        "passed": condition.passed,
    }


def _logic_payload(logic) -> dict:
    return {
        "logic_name": logic.logic_name,
        "active": logic.active,
        "failed_conditions": [condition.name for condition in logic.failed_conditions],
        "conditions": [_condition_payload(condition) for condition in logic.conditions],
    }


def _node(node_id: str, label: str, state: str, source: str, blocked_by: list[str] | None = None) -> dict:
    return {
        "id": node_id,
        "label": label,
        "state": state,
        "source": source,
        "blocked_by": blocked_by or [],
    }


def _logic_node_state(active: bool, completed: bool = False) -> str:
    return "active" if active or completed else "blocked"


def _lever_summary(
    tra_deg: float,
    inputs: ResolvedInputs,
    sensors,
    outputs,
    explain,
    feedback_mode: str,
    tra_lock: dict | None = None,
) -> dict:
    summary = None
    if not inputs.sw1:
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：拉杆还没进入 SW1 窗口，反推链路保持待命。",
            "blocker": "当前卡在 SW1：继续拉入 -1.4° 到 -6.2° 窗口会触发第一段链路。",
            "next_step": "下一步：把拉杆继续向反推方向拉到 SW1 window。",
        }
    elif not outputs.logic1_active and not sensors.tls_unlocked_ls:
        failed = ", ".join(condition.name for condition in explain.logic1.failed_conditions)
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW1 已触发，但 L1 / TLS115 尚未放行。",
            "blocker": f"当前卡在 L1：{failed or 'logic1 条件未完全满足'}。",
            "next_step": "下一步：恢复 RA / inhibited / EEC feedback 等 L1 条件，或回到默认演示条件。",
        }
    elif not inputs.sw2:
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW1 / L1 / TLS115 已点亮，正在建立 TLS 解锁反馈。",
            "blocker": "当前卡在 SW2：还没有进入 -5.0° 到 -9.8° 窗口。",
            "next_step": "下一步：继续拉到 SW2 window，点亮 L2 / 540V。",
        }
    elif not outputs.logic2_active:
        failed = ", ".join(condition.name for condition in explain.logic2.failed_conditions)
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW2 已触发，但 L2 / 540V 尚未放行。",
            "blocker": f"当前卡在 L2：{failed or 'logic2 条件未完全满足'}。",
            "next_step": "下一步：恢复 engine / ground / inhibited / EEC enable 等 L2 条件。",
        }
    elif not outputs.logic3_active:
        failed = ", ".join(condition.name for condition in explain.logic3.failed_conditions)
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：SW1、SW2 与 L2/540V 已点亮，L3 尚未放行。",
            "blocker": f"当前卡在 L3：{failed or 'logic3 条件未完全满足'}。",
            "next_step": "下一步：继续拉到 TRA <= -11.74°，并保持 N1K / TLS 等条件满足。",
        }
    elif not outputs.logic4_active:
        failed = ", ".join(condition.name for condition in explain.logic4.failed_conditions)
        next_step = "下一步：在受控轨迹中继续保持反推，等 deploy_90_percent_vdt / VDT90 反馈出现。"
        if feedback_mode == "manual_feedback_override" and "deploy_90_percent_vdt" in failed:
            next_step = "下一步：把 deploy feedback override 推到 >= 90%，演示 VDT90 -> L4 -> THR_LOCK。"
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：L3 已点亮，EEC / PLS / PDU 命令正在驱动受控演示轨迹。",
            "blocker": f"THR_LOCK 仍未释放：L4 还在等待 {failed or 'VDT90 / plant feedback'}。",
            "next_step": next_step,
        }
    elif feedback_mode == "manual_feedback_override":
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：manual feedback override 已把 VDT90 推到触发态，L4 / THR_LOCK 已点亮。",
            "blocker": "当前无 L4 blocker；这是 simplified plant feedback override 的诊断演示结果。",
            "next_step": "下一步：切回 auto scrubber，或降低 deploy feedback 观察 VDT90 / THR_LOCK 退回 blocked。",
        }
    else:
        summary = {
            "headline": f"TRA {tra_deg:.1f}°：L4 已满足，THR_LOCK release command 已触发。",
            "blocker": "当前无 L4 blocker。",
            "next_step": "下一步：查看证据或返回问答抽屉做诊断解释。",
        }

    if tra_lock and tra_lock["clamped"]:
        summary["blocker"] = (
            f"{summary['blocker']} TRA 深拉区仍未开放：请求 {tra_lock['requested_tra_deg']:.1f}° "
            f"已被限制在 {tra_lock['lock_deg']:.1f}°，当前只开放 {tra_lock['lock_deg']:.1f}° 到 0.0° 的自由拖动范围。"
        )
    return summary


def _simulate_lever_state(
    target_tra: float,
    *,
    config: HarnessConfig,
    radio_altitude_ft: float,
    engine_running: bool,
    aircraft_on_ground: bool,
    reverser_inhibited: bool,
    eec_enable: bool,
    n1k: float,
    max_n1k_deploy_limit: float,
    feedback_mode: str,
    deploy_position_percent: float,
    fault_injections: list[dict] | None = None,
) -> dict:
    controller_adapter = build_reference_controller_adapter(config)
    switches = LatchedThrottleSwitches(config)
    plant = SimplifiedDeployPlant(config)
    switch_state = SwitchState(previous_tra_deg=0.0)
    plant_state = PlantState()
    fault_map = _fault_injection_map(fault_injections)

    snapshot = None
    for tick, current_tra in enumerate(_canonical_pullback_sequence(target_tra, config)):
        switch_state = switches.update(switch_state, current_tra)
        switch_state = _apply_switch_fault_injections(switch_state, fault_map)
        sensors = plant_state.sensors(config)
        sensors = _apply_sensor_fault_injections(sensors, fault_map)
        pilot_inputs = PilotInputs(
            radio_altitude_ft=(
                0.0
                if fault_map.get("radio_altitude_ft") == "sensor_zero"
                else radio_altitude_ft
            ),
            tra_deg=current_tra,
            engine_running=engine_running,
            aircraft_on_ground=aircraft_on_ground,
            reverser_inhibited=reverser_inhibited,
            eec_enable=eec_enable,
            n1k=0.0 if fault_map.get("n1k") == "sensor_zero" else n1k,
            max_n1k_deploy_limit=max_n1k_deploy_limit,
        )
        resolved_inputs = ResolvedInputs(
            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
            tra_deg=pilot_inputs.tra_deg,
            sw1=switch_state.sw1,
            sw2=switch_state.sw2,
            engine_running=pilot_inputs.engine_running,
            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
            reverser_inhibited=pilot_inputs.reverser_inhibited,
            eec_enable=pilot_inputs.eec_enable,
            n1k=pilot_inputs.n1k,
            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )
        outputs, explain = controller_adapter.evaluate_with_explain(resolved_inputs)
        outputs = _apply_output_fault_injections(outputs, fault_map)
        snapshot = {
            "time_s": round(tick * config.step_s, 3),
            "plant_state": plant_state,
            "sensors": sensors,
            "pilot_inputs": pilot_inputs,
            "inputs": resolved_inputs,
            "outputs": outputs,
            "explain": explain,
        }
        plant_state = plant.advance(plant_state, outputs, config.step_s)

    assert snapshot is not None

    if feedback_mode == "manual_feedback_override":
        # Respect causal chain: deploy_position_percent feedback is only valid when L3
        # (pdu_motor_cmd) is active. In manual override mode the user drives the physical
        # lever, but the VDT90 sensor still only reads real travel — which only exists if
        # the PDU motor was actually commanded by L3 (physical因果链: L3 → pdu_motor_cmd →
        # deploy_position_percent ≥ 90% → VDT90 → L4).
        deploy_position = deploy_position_percent if outputs.pdu_motor_cmd else 0.0
        manual_plant_state = PlantState(
            tls_powered_s=snapshot["plant_state"].tls_powered_s,
            pls_powered_s=snapshot["plant_state"].pls_powered_s,
            tls_unlocked_ls=snapshot["plant_state"].tls_unlocked_ls,
            pls_unlocked_ls=snapshot["plant_state"].pls_unlocked_ls,
            deploy_position_percent=deploy_position,
        )
        sensors = manual_plant_state.sensors(config)
        sensors = _apply_sensor_fault_injections(sensors, fault_map)
        pilot_inputs = snapshot["pilot_inputs"]
        inputs = ResolvedInputs(
            radio_altitude_ft=pilot_inputs.radio_altitude_ft,
            tra_deg=pilot_inputs.tra_deg,
            sw1=snapshot["inputs"].sw1,
            sw2=snapshot["inputs"].sw2,
            engine_running=pilot_inputs.engine_running,
            aircraft_on_ground=pilot_inputs.aircraft_on_ground,
            reverser_inhibited=pilot_inputs.reverser_inhibited,
            eec_enable=pilot_inputs.eec_enable,
            n1k=pilot_inputs.n1k,
            max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )
        controller_adapter = build_reference_controller_adapter(config)
        outputs, explain = controller_adapter.evaluate_with_explain(inputs)
        outputs = _apply_output_fault_injections(outputs, fault_map)
        snapshot.update(
            {
                "plant_state": manual_plant_state,
                "sensors": sensors,
                "inputs": inputs,
                "outputs": outputs,
                "explain": explain,
            }
        )
    return snapshot


def _build_tra_lock_payload(
    *,
    config: HarnessConfig,
    requested_tra_deg: float,
    effective_tra_deg: float,
    lock_deg: float,
    boundary_unlock_ready: bool,
    deep_range_open: bool,
    unlock_blockers: list[str],
) -> dict:
    blocker_text = " / ".join(unlock_blockers) if unlock_blockers else "L4 条件"
    locked = not deep_range_open
    clamped = effective_tra_deg != requested_tra_deg
    allowed_reverse_min_deg = config.reverse_travel_min_deg if deep_range_open else lock_deg
    if deep_range_open:
        message = (
            f"L4 已满足：TRA 现在可以在 {config.reverse_travel_min_deg:.1f}° 到 0.0° 区间自由拖动。"
        )
    elif clamped:
        message = (
            f"L4 未满足：请求 {requested_tra_deg:.1f}° 已锁回 {lock_deg:.1f}°；"
            f"当前只能在 {lock_deg:.1f}° 到 0.0° 范围内拖动。"
        )
    else:
        message = (
            f"L4 未满足：当前自由拖动范围只开放 {lock_deg:.1f}° 到 0.0°；"
            f"满足 {blocker_text} 后，{config.reverse_travel_min_deg:.1f}° 到 {lock_deg:.1f}° 深拉区间才开放。"
        )
    return {
        "locked": locked,
        "clamped": clamped,
        "unlock_ready": deep_range_open,
        "boundary_unlock_ready": boundary_unlock_ready,
        "lock_deg": lock_deg,
        "requested_tra_deg": requested_tra_deg,
        "effective_tra_deg": effective_tra_deg,
        "allowed_reverse_min_deg": allowed_reverse_min_deg,
        "visual_reverse_min_deg": config.reverse_travel_min_deg,
        "deep_reverse_limit_deg": config.reverse_travel_min_deg,
        "unlock_logic": "logic4",
        "unlock_blockers": unlock_blockers,
        "message": message,
    }


def _monitor_ra_ft(time_s: float) -> float:
    return max(0.0, MONITOR_RA_START_FT - MONITOR_RA_RATE_FT_PER_S * time_s)


def _monitor_tra_deg(time_s: float) -> float:
    if time_s < MONITOR_TRA_START_S:
        return 0.0
    return max(MONITOR_TRA_LOCK_DEG, -(time_s - MONITOR_TRA_START_S) * MONITOR_TRA_RATE_DEG_PER_S)


def _monitor_vdt_percent(time_s: float) -> float:
    if time_s < MONITOR_VDT_START_S:
        return 0.0
    return min(100.0, (time_s - MONITOR_VDT_START_S) * MONITOR_VDT_RATE_PERCENT_PER_S)


def _monitor_series_definition() -> list[dict]:
    return [
        {"id": "ra", "label": "RA", "unit": "ft", "display_min": 0.0, "display_max": 7.0, "color": "#ff6f91", "category": "input"},
        {"id": "tra", "label": "TRA", "unit": "deg", "display_min": -32.0, "display_max": 0.0, "color": "#ffaa33", "category": "input"},
        {"id": "sw1", "label": "SW1", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#28f4ff", "category": "logic"},
        {"id": "logic1", "label": "L1", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "tls", "label": "TLS", "unit": "V", "display_min": 0.0, "display_max": 115.0, "color": "#7dff9a", "category": "power"},
        {"id": "sw2", "label": "SW2", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#28f4ff", "category": "logic"},
        {"id": "logic2", "label": "L2", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "etrac", "label": "ETRAC", "unit": "V", "display_min": 0.0, "display_max": 540.0, "color": "#86ffbf", "category": "power"},
        {"id": "logic3", "label": "L3", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "eec", "label": "EEC", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
        {"id": "pls", "label": "PLS", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
        {"id": "pdu", "label": "PDU", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ffd65c", "category": "command"},
        {"id": "vdt", "label": "VDT", "unit": "%", "display_min": 0.0, "display_max": 100.0, "color": "#b69dff", "category": "sensor"},
        {"id": "logic4", "label": "L4", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#34d4ff", "category": "logic"},
        {"id": "thr_lock", "label": "THR_LOCK", "unit": "state", "display_min": 0.0, "display_max": 1.0, "color": "#ff8c7a", "category": "command"},
    ]


def _monitor_transition_time(rows: list[dict], field_name: str, target_value) -> float | None:
    for row in rows:
        if row[field_name] == target_value:
            return row["time_s"]
    return None


def _monitor_rows(config: HarnessConfig) -> list[dict]:
    controller_adapter = build_reference_controller_adapter(config)
    switches = LatchedThrottleSwitches(config)
    switch_state = SwitchState(previous_tra_deg=0.0)
    tls_powered_s = 0.0
    pls_powered_s = 0.0
    tls_unlocked_ls = False
    all_pls_unlocked_ls = False
    rows: list[dict] = []

    step_count = int(round(MONITOR_TIMELINE_END_S / config.step_s))
    for step_index in range(step_count + 1):
        time_s = round(step_index * config.step_s, 3)
        radio_altitude_ft = _monitor_ra_ft(time_s)
        tra_deg = _monitor_tra_deg(time_s)
        vdt_percent = _monitor_vdt_percent(time_s)
        switch_state = switches.update(switch_state, tra_deg)

        inputs = ResolvedInputs(
            radio_altitude_ft=radio_altitude_ft,
            tra_deg=tra_deg,
            sw1=switch_state.sw1,
            sw2=switch_state.sw2,
            engine_running=MONITOR_ENGINE_RUNNING,
            aircraft_on_ground=MONITOR_AIRCRAFT_ON_GROUND,
            reverser_inhibited=MONITOR_REVERSER_INHIBITED,
            eec_enable=MONITOR_EEC_ENABLE,
            n1k=MONITOR_N1K,
            max_n1k_deploy_limit=MONITOR_MAX_N1K_DEPLOY_LIMIT,
            tls_unlocked_ls=tls_unlocked_ls,
            all_pls_unlocked_ls=all_pls_unlocked_ls,
            reverser_not_deployed_eec=vdt_percent <= 0.0,
            reverser_fully_deployed_eec=vdt_percent >= 100.0,
            deploy_90_percent_vdt=vdt_percent >= config.deploy_90_threshold_percent,
        )
        outputs, explain = controller_adapter.evaluate_with_explain(inputs)

        rows.append(
            {
                "time_s": time_s,
                "ra": round(radio_altitude_ft, 3),
                "tra": round(tra_deg, 3),
                "sw1": 1.0 if inputs.sw1 else 0.0,
                "logic1": 1.0 if outputs.logic1_active else 0.0,
                "tls": 115.0 if outputs.tls_115vac_cmd else 0.0,
                "sw2": 1.0 if inputs.sw2 else 0.0,
                "logic2": 1.0 if outputs.logic2_active else 0.0,
                "etrac": 540.0 if outputs.etrac_540vdc_cmd else 0.0,
                "logic3": 1.0 if outputs.logic3_active else 0.0,
                "eec": 1.0 if outputs.eec_deploy_cmd else 0.0,
                "pls": 1.0 if outputs.pls_power_cmd else 0.0,
                "pdu": 1.0 if outputs.pdu_motor_cmd else 0.0,
                "vdt": round(vdt_percent, 3),
                "logic4": 1.0 if outputs.logic4_active else 0.0,
                "thr_lock": 1.0 if outputs.throttle_electronic_lock_release_cmd else 0.0,
                "logic4_failed_conditions": [condition.name for condition in explain.logic4.failed_conditions],
            }
        )

        tls_powered_s = tls_powered_s + config.step_s if outputs.tls_115vac_cmd else 0.0
        tls_unlocked_ls = tls_unlocked_ls or (
            outputs.tls_115vac_cmd and tls_powered_s >= config.tls_unlock_delay_s
        )

        pls_powered_s = pls_powered_s + config.step_s if outputs.pls_power_cmd else 0.0
        pls_ready = outputs.pls_power_cmd and pls_powered_s >= config.pls_unlock_delay_s
        all_pls_unlocked_ls = all_pls_unlocked_ls or pls_ready

        if not (
            outputs.tls_115vac_cmd
            or outputs.etrac_540vdc_cmd
            or outputs.pls_power_cmd
            or outputs.pdu_motor_cmd
        ):
            tls_unlocked_ls = False
            all_pls_unlocked_ls = False

    return rows


def monitor_timeline_payload() -> dict:
    config = HarnessConfig()
    rows = _monitor_rows(config)
    series = []
    for definition in _monitor_series_definition():
        samples = [[row["time_s"], row[definition["id"]]] for row in rows]
        series.append({**definition, "samples": samples})

    l4_ready_time = _monitor_transition_time(rows, "logic4", 1.0)
    events = [
        {
            "time_s": 0.0,
            "label": "流程开始",
            "detail": "RA 从 7.0 ft 起步；TRA=0°；VDT=0%。",
        },
        {
            "time_s": 1.0,
            "label": "RA=6.0 ft",
            "detail": "TRA 从 0° 开始以 10°/s 推向 -14°。",
        },
        {
            "time_s": 2.4,
            "label": "TRA=-14°",
            "detail": "碰到 L4 条件限位；VDT 开始以 50%/s 从 0% 变化。",
        },
        {
            "time_s": 4.2,
            "label": "VDT90",
            "detail": "VDT 达到 90%，L4 / THR_LOCK 首次满足。",
        },
        {
            "time_s": MONITOR_ACTIVE_END_S,
            "label": "监测结束",
            "detail": "VDT=100%，主动监测流程完成。",
        },
        {
            "time_s": MONITOR_TIMELINE_END_S,
            "label": "RA=0 ft",
            "detail": "展示保持段：RA 继续匀速降到 0 ft 后保持。",
        },
    ]

    return {
        "mode": "timeline_monitor",
        "title": "受控状态监控时间线",
        "time_start_s": 0.0,
        "time_end_s": MONITOR_TIMELINE_END_S,
        "active_end_s": MONITOR_ACTIVE_END_S,
        "compression_ratio": MONITOR_TIMELINE_COMPRESSION_RATIO,
        "step_s": config.step_s,
        "model_note": (
            "这条监控图按用户定义的 RA -> TRA -> VDT 受控时间线生成；"
            "整段时间已压缩为原来的 1/10；VDT 按现有 demo 反馈语义绘制为 0%-100% 监测量，"
            "控制逻辑仍由 DeployController 评估。"
        ),
        "timeline_summary": {
            "ra_start_ft": MONITOR_RA_START_FT,
            "ra_hits_six_ft_at_s": 1.0,
            "tra_lock_deg": MONITOR_TRA_LOCK_DEG,
            "tra_reaches_lock_at_s": 2.4,
            "vdt_reaches_90_percent_at_s": 4.2,
            "vdt_reaches_100_percent_at_s": MONITOR_ACTIVE_END_S,
            "ra_reaches_zero_ft_at_s": MONITOR_TIMELINE_END_S,
            "l4_ready_at_s": l4_ready_time,
        },
        "events": events,
        "series": series,
}


# ---------------------------------------------------------------------------
# Multi-system snapshot support (P13)
# ---------------------------------------------------------------------------
SYSTEM_REGISTRY = {
    "thrust-reverser": build_reference_controller_adapter,
    "landing-gear": build_landing_gear_controller_adapter,
    "bleed-air": build_bleed_air_controller_adapter,
    "efds": build_efds_controller_adapter,
}

# Cache built (stateless) adapters — avoid per-request instantiation overhead.
@lru_cache(maxsize=4)
def _cached_adapter(system_id: str) -> Any:
    builder = SYSTEM_REGISTRY.get(system_id)
    if builder is None:
        return None
    return builder()

SYSTEM_SNAPSHOT_PATH = "/api/system-snapshot"


def _default_snapshot_for_system(system_id: str) -> dict:
    """Return a minimal/default snapshot for each registered system."""
    if system_id == "thrust-reverser":
        return {
            "radio_altitude_ft": 5.0,
            "tra_deg": 0.0,
            "sw1": False,
            "sw2": False,
            "engine_running": True,
            "aircraft_on_ground": True,
            "reverser_inhibited": False,
            "eec_enable": True,
            "n1k": 35.0,
            "max_n1k_deploy_limit": 60.0,
            "tls_unlocked_ls": False,
            "all_pls_unlocked_ls": False,
            "reverser_not_deployed_eec": True,
            "reverser_fully_deployed_eec": False,
            "deploy_90_percent_vdt": False,
        }
    elif system_id == "landing-gear":
        return {
            "gear_handle_position": "UP",
            "hydraulic_pressure_psi": 0.0,
            "uplock_released": False,
            "gear_position_percent": 0.0,
            "downlock_engaged": False,
        }
    elif system_id == "bleed-air":
        return {
            "valve_position": "CLOSED",
            "inlet_pressure": 0.0,
            "outlet_pressure": 0.0,
            "control_unit_ready": True,
        }
    elif system_id == "efds":
        return {
            "sensor.alt.radar": 5000.0,
            "sensor.alt.baro": 5200.0,
            "sensor.temp.external": 15.0,
            "sensor.threat.mls": "IDLE",
            "sensor.g.load": 1.0,
            "logic.armed_relay": "OPEN",
            "logic.firing_channel": "READY",
            "logic.crosslink_validator": "FALSE",
            "pilot.arm_switch": "SAFE",
            "pilot.manual_dispense": "RELEASED",
            "pilot.altitude_override": "AUTO",
            "actuator.flare_array": 24.0,
            "actuator.limiter_valve": "REGULATED",
        }
    return {}


def _spec_to_nodes(spec: dict, truth_evaluation: Any = None) -> list[dict]:
    """Build a nodes array from spec.components + spec.logic_nodes.

    Nodes are ordered to reflect the control flow: input conditions first,
    then parallel logic gates, then merge gates, then final outputs.
    This ordering is derived from the spec's logic_node downstream relationships.
    """
    active_ids: set[str] = set()
    if truth_evaluation is not None:
        active_ids = set(truth_evaluation.active_logic_node_ids)

    # Separate components into inputs vs intermediate/output components
    components = spec.get("components", [])
    logic_nodes = spec.get("logic_nodes", [])

    # Identify which components are upstream inputs (no logic_node depends on them as downstream)
    downstream_ids: set[str] = set()
    for ln in logic_nodes:
        for cid in ln.get("downstream_component_ids", []):
            downstream_ids.add(cid)

    # Components that appear as downstream of logic nodes → intermediate/output nodes
    # Components that don't → upstream input nodes
    upstream_input_ids: set[str] = set()
    intermediate_output_ids: set[str] = set()
    for comp in components:
        cid = comp["id"]
        if cid in downstream_ids:
            intermediate_output_ids.add(cid)
        else:
            upstream_input_ids.add(cid)

    # Build ordered node list:
    # 1. Upstream input components (sensors/pilot inputs)
    # 2. Logic nodes in dependency order
    # 3. Intermediate/output components (commands/power)
    nodes: list[dict] = []

    # Sort logic nodes by dependency: nodes whose downstream_component_ids feed into other logic nodes come first
    # For thrust-reverser: L1 and L2 are parallel (no cross-dependency), L3 depends on both, L4 depends on L3
    # Build a dependency graph to determine order
    node_ids = {ln["id"] for ln in logic_nodes}
    resolved: list[dict] = []
    remaining = list(logic_nodes)
    while remaining:
        made_progress = False
        for i, ln in enumerate(remaining):
            deps_met = True
            for cid in ln.get("downstream_component_ids", []):
                # Check if this component feeds into any remaining logic node
                for remaining_ln in remaining[i + 1:]:
                    if cid in remaining_ln.get("downstream_component_ids", []):
                        deps_met = False
                        break
                if not deps_met:
                    break
            if deps_met:
                resolved.append(remaining.pop(i))
                made_progress = True
                break
        if not made_progress:
            # Fallback: append remaining in order
            resolved.extend(remaining)
            break

    # Layer 1: upstream input components
    for comp in components:
        if comp["id"] in upstream_input_ids:
            nodes.append(_node(comp["id"], comp["label"], "inactive", "spec.components"))

    # Layer 2: logic nodes in dependency order
    for ln in resolved:
        state = "active" if ln["id"] in active_ids else "inactive"
        nodes.append(_node(ln["id"], ln["label"], state, "spec.logic_nodes"))

    # Layer 3: intermediate/output components (commands/power)
    for comp in components:
        if comp["id"] in intermediate_output_ids:
            nodes.append(_node(comp["id"], comp["label"], "inactive", "spec.components"))

    return nodes


def system_snapshot_payload(system_id: str) -> dict:
    """Build the payload for GET /api/system-snapshot."""
    adapter = _cached_adapter(system_id)
    if adapter is None:
        return {"error": "unknown_system", "system_id": system_id}
    spec = adapter.load_spec()
    default_snapshot = _default_snapshot_for_system(system_id)
    truth_eval = adapter.evaluate_snapshot(default_snapshot)
    nodes = _spec_to_nodes(spec, truth_eval)
    return {
        "system_id": system_id,
        "title": spec.get("title", system_id),
        "spec": spec,
        "nodes": nodes,
        "truth_evaluation": truth_eval.to_dict(),
        "default_snapshot": default_snapshot,
    }


def system_snapshot_post_payload(system_id: str, snapshot: dict) -> dict:
    """Evaluate a user-modified snapshot for a given system. Used by non-thrust systems."""
    adapter = _cached_adapter(system_id)
    if adapter is None:
        return {"error": "unknown_system", "system_id": system_id}
    spec = adapter.load_spec()
    truth_eval = adapter.evaluate_snapshot(snapshot)
    nodes = _spec_to_nodes(spec, truth_eval)
    return {
        "system_id": system_id,
        "title": spec.get("title", system_id),
        "spec": spec,
        "nodes": nodes,
        "truth_evaluation": truth_eval.to_dict(),
        "snapshot": snapshot,
    }


def lever_snapshot_payload(
    tra_deg: float,
    radio_altitude_ft: float = 5.0,
    engine_running: bool = True,
    aircraft_on_ground: bool = True,
    reverser_inhibited: bool = False,
    eec_enable: bool = True,
    n1k: float = 35.0,
    max_n1k_deploy_limit: float = 60.0,
    feedback_mode: str = "auto_scrubber",
    deploy_position_percent: float = 0.0,
    fault_injections: list[dict] | None = None,
) -> dict:
    config = HarnessConfig()
    requested_tra = _clamp_tra(tra_deg, config)
    lock_deg = _clamp_tra(TRA_L4_LOCK_DEG, config)
    requested_snapshot = _simulate_lever_state(
        requested_tra,
        config=config,
        radio_altitude_ft=radio_altitude_ft,
        engine_running=engine_running,
        aircraft_on_ground=aircraft_on_ground,
        reverser_inhibited=reverser_inhibited,
        eec_enable=eec_enable,
        n1k=n1k,
        max_n1k_deploy_limit=max_n1k_deploy_limit,
        feedback_mode=feedback_mode,
        deploy_position_percent=deploy_position_percent,
        fault_injections=fault_injections,
    )
    lock_probe = _simulate_lever_state(
        lock_deg,
        config=config,
        radio_altitude_ft=radio_altitude_ft,
        engine_running=engine_running,
        aircraft_on_ground=aircraft_on_ground,
        reverser_inhibited=reverser_inhibited,
        eec_enable=eec_enable,
        n1k=n1k,
        max_n1k_deploy_limit=max_n1k_deploy_limit,
        feedback_mode=feedback_mode,
        deploy_position_percent=deploy_position_percent,
        fault_injections=fault_injections,
    )
    boundary_unlock_ready = lock_probe["outputs"].logic4_active
    effective_tra = (
        requested_tra
        if boundary_unlock_ready or requested_tra >= lock_deg
        else lock_deg
    )
    snapshot = (
        requested_snapshot
        if effective_tra == requested_tra
        else lock_probe
    )

    time_s = snapshot["time_s"]
    plant_debug_state = snapshot["plant_state"]
    sensors = snapshot["sensors"]
    pilot_inputs = snapshot["pilot_inputs"]
    inputs = snapshot["inputs"]
    outputs = snapshot["outputs"]
    explain = snapshot["explain"]
    deep_range_open = boundary_unlock_ready
    tra_lock = _build_tra_lock_payload(
        config=config,
        requested_tra_deg=requested_tra,
        effective_tra_deg=effective_tra,
        lock_deg=lock_deg,
        boundary_unlock_ready=boundary_unlock_ready,
        deep_range_open=deep_range_open,
        unlock_blockers=[condition.name for condition in lock_probe["explain"].logic4.failed_conditions],
    )
    logic1_completed = sensors.tls_unlocked_ls
    logic4_blockers = [condition.name for condition in explain.logic4.failed_conditions]
    logic3_blockers = [condition.name for condition in explain.logic3.failed_conditions]

    nodes = [
        _node("sw1", "SW1", "active" if inputs.sw1 else "inactive", "LatchedThrottleSwitches"),
        _node("logic1", "L1", _logic_node_state(outputs.logic1_active, logic1_completed), "DeployController.explain(logic1)", [condition.name for condition in explain.logic1.failed_conditions]),
        _node("tls115", "TLS115", "active" if outputs.tls_115vac_cmd or sensors.tls_unlocked_ls else "inactive", "DeployController outputs"),
        _node("tls_unlocked", "TLS 解锁", "active" if sensors.tls_unlocked_ls else "inactive", "SimplifiedDeployPlant sensors"),
        _node("sw2", "SW2", "active" if inputs.sw2 else "inactive", "LatchedThrottleSwitches"),
        _node("logic2", "L2", _logic_node_state(outputs.logic2_active), "DeployController.explain(logic2)", [condition.name for condition in explain.logic2.failed_conditions]),
        _node("etrac_540v", "540V", "active" if outputs.etrac_540vdc_cmd else "inactive", "DeployController outputs"),
        _node("logic3", "L3", _logic_node_state(outputs.logic3_active), "DeployController.explain(logic3)", logic3_blockers),
        _node("eec_deploy", "EEC", "active" if outputs.eec_deploy_cmd else "inactive", "DeployController outputs"),
        _node("pls_power", "PLS", "active" if outputs.pls_power_cmd else "inactive", "DeployController outputs"),
        _node("pdu_motor", "PDU", "active" if outputs.pdu_motor_cmd else "inactive", "DeployController outputs"),
        _node("vdt90", "VDT90", "active" if sensors.deploy_90_percent_vdt else "inactive", "SimplifiedDeployPlant sensors"),
        _node("logic4", "L4", _logic_node_state(outputs.logic4_active), "DeployController.explain(logic4)", logic4_blockers),
        _node(
            "thr_lock",
            "THR_LOCK",
            "active"
            if outputs.throttle_electronic_lock_release_cmd
            else (
                "blocked"
                if explain.logic4.failed_conditions
                else "inactive"
            ),
            # Use explain.logic4.failed_conditions to determine "blocked" vs "inactive".
            # This correctly handles the causal chain: when L4 is blocked (has unmet
            # conditions like tra_deg), THR_LOCK is "blocked" (waiting on L4).
            # When L4 has no failed conditions but is simply not active, THR_LOCK is "inactive".
            "DeployController outputs",
            logic4_blockers if not outputs.throttle_electronic_lock_release_cmd else [],
        ),
    ]
    summary = _lever_summary(effective_tra, inputs, sensors, outputs, explain, feedback_mode, tra_lock)
    model_note = (
        "受控拉杆轨迹：复用现有 switch/controller/plant 代码做演示快照；不是完整飞控实时物理仿真。"
        if feedback_mode == "auto_scrubber"
        else "manual feedback override：用 simplified plant feedback / diagnostic override 推动 VDT / deploy feedback；不是新的控制真值，也不是完整实时物理仿真。"
    )

    result = {
        "mode": (
            "canonical_pullback_scrubber"
            if feedback_mode == "auto_scrubber"
            else "manual_feedback_override"
        ),
        "model_note": model_note,
        "tra_lock": tra_lock,
        "input": {
            "requested_tra_deg": requested_tra,
            "tra_deg": effective_tra,
            "radio_altitude_ft": inputs.radio_altitude_ft,
            "engine_running": inputs.engine_running,
            "aircraft_on_ground": inputs.aircraft_on_ground,
            "reverser_inhibited": inputs.reverser_inhibited,
            "eec_enable": inputs.eec_enable,
            "n1k": inputs.n1k,
            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
            "feedback_mode": feedback_mode,
            "deploy_position_percent": deploy_position_percent,
        },
        "time_s": time_s,
        "hud": {
            "requested_tra_deg": requested_tra,
            "tra_deg": effective_tra,
            "sw1": inputs.sw1,
            "sw2": inputs.sw2,
            "radio_altitude_ft": inputs.radio_altitude_ft,
            "engine_running": inputs.engine_running,
            "aircraft_on_ground": inputs.aircraft_on_ground,
            "reverser_inhibited": inputs.reverser_inhibited,
            "eec_enable": inputs.eec_enable,
            "n1k": inputs.n1k,
            "max_n1k_deploy_limit": inputs.max_n1k_deploy_limit,
            "tls_unlocked_ls": sensors.tls_unlocked_ls,
            "pls_unlocked_ls": sensors.pls_unlocked_ls,
            "all_pls_unlocked_ls": sensors.all_pls_unlocked,
            "deploy_position_percent": sensors.deploy_position_percent,
            "deploy_90_percent_vdt": sensors.deploy_90_percent_vdt,
            "feedback_mode": feedback_mode,
        },
        "outputs": {
            "logic1_active": outputs.logic1_active,
            "logic2_active": outputs.logic2_active,
            "logic3_active": outputs.logic3_active,
            "logic4_active": outputs.logic4_active,
            "tls_115vac_cmd": outputs.tls_115vac_cmd,
            "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
            "eec_deploy_cmd": outputs.eec_deploy_cmd,
            "pls_power_cmd": outputs.pls_power_cmd,
            "pdu_motor_cmd": outputs.pdu_motor_cmd,
            "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
        },
        "logic": {
            "logic1": _logic_payload(explain.logic1),
            "logic2": _logic_payload(explain.logic2),
            "logic3": _logic_payload(explain.logic3),
            "logic4": _logic_payload(explain.logic4),
        },
        "plant_state": {
            "tls_powered_s": plant_debug_state.tls_powered_s,
            "pls_powered_s": plant_debug_state.pls_powered_s,
            "tls_unlocked_ls": plant_debug_state.tls_unlocked_ls,
            "pls_unlocked_ls": plant_debug_state.pls_unlocked_ls,
            "deploy_position_percent": plant_debug_state.deploy_position_percent,
        },
        "nodes": nodes,
        "summary": summary,
        "evidence": [
            "switches=LatchedThrottleSwitches.update(...)",
            "controller=DeployController.evaluate_with_explain(...)",
            "explain=DeployController.explain(...)",
            "plant=SimplifiedDeployPlant first-cut feedback model",
            "tra_lock=L4 gate at -14° before deeper reverse travel",
        ],
        "risks": [
            "PLS / VDT feedback comes from simplified first-cut plant timing.",
            "Manual feedback override is only a diagnostic demo control, not new control truth.",
            "THR_LOCK release must not be read as complete physical root-cause proof.",
        ],
    }
    return _apply_fault_injections_to_snapshot_payload(result, fault_injections)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the local well-harness demo UI.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host interface to bind.")
    parser.add_argument("--port", default=DEFAULT_PORT, type=int, help="Port to bind.")
    parser.add_argument(
        "--open",
        action="store_true",
        help=(
            "Open the local UI URL with Python's standard-library webbrowser.open; "
            "this is a launch convenience, not browser E2E automation."
        ),
    )
    return parser


def demo_url(host: str, port: int) -> str:
    return f"http://{host}:{port}/chat.html"


def open_browser(url: str, opener=webbrowser.open) -> bool:
    try:
        opened = bool(opener(url))
    except Exception as exc:  # pragma: no cover - exact browser backends vary by host
        print(f"Could not open browser automatically: {exc}. Open {url} manually.")
        return False
    if not opened:
        print(f"Could not open browser automatically. Open {url} manually.")
    return opened


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), DemoRequestHandler)
    host, port = server.server_address
    url = demo_url(host, port)
    print(f"Serving well-harness demo UI at {url}")
    if args.open:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping well-harness demo UI.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
