#!/usr/bin/env python3
"""Browser gate for M21 streamed revision, authorization, and queue advance."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import threading
import urllib.request
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from well_harness.demo_server import DemoRequestHandler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = PROJECT_ROOT / "artifacts" / "m21-streamed-authoring-revision-gate"
SUMMARY_NAME = "m21_streamed_authoring_revision_browser_gate.json"
STREAMED_PROPOSAL_PATH = "/api/requirements-intake/streamed-authoring/proposal"
CONTROL_TRUTH_PATHS = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
]
REQUIREMENTS_DOCUMENT_PATHS = [
    "docs/c919_etras",
    "docs/thrust_reverser/l0_functional_requirements_v0_1.md",
    "docs/thrust_reverser/requirements_supplement.md",
    "src/well_harness/static/c919_requirements.html",
    "src/well_harness/static/fantui_requirements.html",
    "src/well_harness/static/requirements_intake",
]
RESTRICTED_PATHS = [*CONTROL_TRUTH_PATHS, *REQUIREMENTS_DOCUMENT_PATHS]
AUTHORIZATION_PHRASE = "AUTHORIZE_REQUIREMENTS_EDIT"
STREAMED_AUTHORING_KEY = "ai-fantui-logic-builder-streamed-authoring-v1"
SCENARIOS = (
    "fantui",
    "c919_etras",
    "c919_etras_raw_intake",
    "c919_etras_real_doc_raw_intake",
    "c919_etras_cmd3_apwtla_real_doc_raw_intake",
    "c919_etras_deploy_cmd1_real_doc_raw_intake",
    "c919_etras_deploy_cmd1_thr_idle_lock_release_real_doc_raw_intake",
    "c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake",
    "fantui_demo_fanout_junction",
)


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value.strip()
    if value is None:
        return default
    return str(value).strip()


def _restricted_diff(paths: list[str] | None = None) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *(paths or RESTRICTED_PATHS)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ["<git status failed>"]
    return [line for line in result.stdout.splitlines() if line.strip()]


def _start_server() -> tuple[ThreadingHTTPServer, threading.Thread, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, thread, f"http://{host}:{port}"


def _route_point(point: Any) -> dict[str, float]:
    if not isinstance(point, dict):
        return {"x": 0.0, "y": 0.0}
    return {
        "x": float(point.get("x") or 0),
        "y": float(point.get("y") or 0),
    }


def _route_point_key(point: Any) -> str:
    normalized = _route_point(point)
    return f"{normalized['x']}:{normalized['y']}"


def _expected_fanout_junction_count(drawing_payload: dict[str, Any]) -> int:
    by_source: dict[str, list[list[dict[str, float]]]] = {}
    for edge in drawing_payload.get("edges", []):
        if not isinstance(edge, dict):
            continue
        source = _str(edge.get("source"))
        route = edge.get("route", [])
        if not source or not isinstance(route, list) or len(route) < 2:
            continue
        by_source.setdefault(source, []).append([_route_point(point) for point in route])

    junctions: set[str] = set()
    for source, routes in by_source.items():
        if len(routes) < 2:
            continue
        shared_interior: dict[str, int] = {}
        for route in routes:
            seen_for_edge: set[str] = set()
            for point in route[1:-1]:
                key = _route_point_key(point)
                if key in seen_for_edge:
                    continue
                seen_for_edge.add(key)
                shared_interior[key] = shared_interior.get(key, 0) + 1
        source_junctions = [
            key for key, count in shared_interior.items() if count >= 2
        ]
        if source_junctions:
            junctions.update(f"{source}:{key}" for key in source_junctions)
            continue
        first_point_key = _route_point_key(routes[0][0])
        if all(_route_point_key(route[0]) == first_point_key for route in routes):
            junctions.add(f"{source}:{first_point_key}")
    return len(junctions)


def _drawing_candidate_count(drawing_payload: dict[str, Any]) -> int:
    circuit_view = drawing_payload.get("circuit_view")
    if isinstance(circuit_view, dict) and circuit_view.get("kind"):
        nodes = circuit_view.get("nodes", [])
        wires = circuit_view.get("wires", [])
    else:
        nodes = drawing_payload.get("nodes", [])
        wires = drawing_payload.get("edges", [])
    return sum(1 for item in nodes if isinstance(item, dict)) + sum(
        1 for item in wires if isinstance(item, dict)
    )


def _fantui_requirements_payload() -> dict[str, Any]:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "summary_zh": "L1 到 L4 反推逻辑已澄清。",
        "open_questions": [],
        "concept_logic_nodes": [
            {
                "id": "RA",
                "label": "无线电高度",
                "node_kind": "input",
                "description_zh": "RA<6ft",
                "source_anchors": [
                    {
                        "id": "REQ-RA",
                        "kind": "正文条件",
                        "origin": "docx_body",
                        "quote_zh": "当无线电高度小于 6ft 时，L1 可进入下一逻辑。",
                    }
                ],
            },
            {
                "id": "L1",
                "label": "逻辑1",
                "node_kind": "logic",
                "description_zh": "TLS解锁逻辑",
            },
        ],
        "concept_edges": [
            {"id": "e1", "source": "RA", "target": "L1", "label": "高度<6ft"}
        ],
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _fantui_drawing_payload() -> dict[str, Any]:
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


def _fantui_demo_fanout_requirements_payload() -> dict[str, Any]:
    source_anchor = {
        "id": "FANOUT-L3-SOURCE",
        "kind": "demo.html#fan-chain-svg",
        "origin": "demo_html_reference",
        "quote_zh": "L3 输出通过 fan-out trunk 同时进入 EEC deploy、PLS power、PDU motor。",
    }
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_intake_analysis_v1.schema.json",
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "summary_zh": "demo.html 多分叉链路候选已抽取，用于验证 junction dot 语义。",
        "open_questions": [],
        "concept_logic_nodes": [
            {
                "id": "logic3_fanout",
                "label": "L3 fan-out",
                "node_kind": "logic",
                "description_zh": "L3 输出进入同一分叉 trunk。",
                "source_anchors": [source_anchor],
            },
            {
                "id": "eec_deploy",
                "label": "EEC deploy",
                "node_kind": "output",
                "description_zh": "L3 输出驱动 EEC deploy 候选输出。",
                "source_anchors": [source_anchor],
            },
            {
                "id": "pls_power",
                "label": "PLS power",
                "node_kind": "output",
                "description_zh": "L3 输出驱动 PLS power 候选输出。",
                "source_anchors": [source_anchor],
            },
            {
                "id": "pdu_motor",
                "label": "PDU motor",
                "node_kind": "output",
                "description_zh": "L3 输出驱动 PDU motor 候选输出。",
                "source_anchors": [source_anchor],
            },
        ],
        "concept_edges": [
            {
                "id": "fanout_e1",
                "source": "logic3_fanout",
                "target": "eec_deploy",
                "label": "L3 fan-out to EEC deploy",
                "source_anchors": [source_anchor],
            },
            {
                "id": "fanout_e2",
                "source": "logic3_fanout",
                "target": "pls_power",
                "label": "L3 fan-out to PLS power",
                "source_anchors": [source_anchor],
            },
            {
                "id": "fanout_e3",
                "source": "logic3_fanout",
                "target": "pdu_motor",
                "label": "L3 fan-out to PDU motor",
                "source_anchors": [source_anchor],
            },
        ],
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _fantui_demo_fanout_drawing_payload() -> dict[str, Any]:
    source_anchor = {
        "id": "FANOUT-L3-SOURCE",
        "kind": "demo.html#fan-chain-svg",
        "origin": "demo_html_reference",
        "quote_zh": "L3 fan-out trunk 在共享中间点产生 junction dot，而不是在线尾画端点点。",
    }
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": "fantui-demo-fanout",
        "summary_zh": "按 demo.html#fan-chain-svg 复刻 L3 到三个输出的 fan-out trunk。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "logic3_fanout",
                "label": "L3 fan-out",
                "node_kind": "logic",
                "x": 80,
                "y": 156,
                "width": 220,
                "height": 104,
                "description_zh": "共享 trunk 的上游逻辑节点。",
                "source_anchors": [source_anchor],
            },
            {
                "id": "eec_deploy",
                "label": "EEC deploy",
                "node_kind": "output",
                "x": 440,
                "y": 72,
                "width": 220,
                "height": 92,
                "description_zh": "第一路 fan-out 输出。",
                "source_anchors": [source_anchor],
            },
            {
                "id": "pls_power",
                "label": "PLS power",
                "node_kind": "output",
                "x": 440,
                "y": 168,
                "width": 220,
                "height": 92,
                "description_zh": "第二路 fan-out 输出。",
                "source_anchors": [source_anchor],
            },
            {
                "id": "pdu_motor",
                "label": "PDU motor",
                "node_kind": "output",
                "x": 440,
                "y": 264,
                "width": 220,
                "height": 92,
                "description_zh": "第三路 fan-out 输出。",
                "source_anchors": [source_anchor],
            },
        ],
        "edges": [
            {
                "id": "fanout_l3_eec",
                "source": "logic3_fanout",
                "target": "eec_deploy",
                "label": "L3 fan-out to EEC deploy",
                "route": [{"x": 300, "y": 208}, {"x": 360, "y": 208}, {"x": 360, "y": 118}, {"x": 440, "y": 118}],
                "source_anchors": [source_anchor],
            },
            {
                "id": "fanout_l3_pls",
                "source": "logic3_fanout",
                "target": "pls_power",
                "label": "L3 fan-out to PLS power",
                "route": [{"x": 300, "y": 208}, {"x": 360, "y": 208}, {"x": 440, "y": 208}],
                "source_anchors": [source_anchor],
            },
            {
                "id": "fanout_l3_pdu",
                "source": "logic3_fanout",
                "target": "pdu_motor",
                "label": "L3 fan-out to PDU motor",
                "route": [{"x": 300, "y": 208}, {"x": 360, "y": 208}, {"x": 360, "y": 310}, {"x": 440, "y": 310}],
                "source_anchors": [source_anchor],
            },
        ],
        "parameter_panels": [],
        "drawing_notes": ["按 demo.html#fan-chain-svg 的 L3 fan-out trunk 复刻 junction dot。"],
    }


def _c919_requirements_payload() -> dict[str, Any]:
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
                "source_anchors": [
                    {
                        "id": "C919-ETRAS-ARM",
                        "kind": "需求条款",
                        "origin": "c919_etras_doc",
                        "quote_zh": "ETRAS 仅在 WOW 有效且手柄解锁区间成立后进入预位。",
                    }
                ],
            },
        ],
        "concept_edges": [
            {
                "id": "c919_e1",
                "source": "wow_valid",
                "target": "etras_armed",
                "label": "WOW gating",
                "source_anchors": [
                    {
                        "id": "C919-ETRAS-WOW-EDGE",
                        "kind": "需求条款",
                        "origin": "c919_etras_doc",
                        "quote_zh": "WOW 有效是 ETRAS 预位的前置门限。",
                    }
                ],
            }
        ],
        "ready_for_logic_builder": True,
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _c919_raw_requirement_text() -> str:
    return "\n".join(
        [
            "C919 E-TRAS 原始需求片段。",
            "R-C919-WOW: 当 WOW 双通道有效且反推手柄进入解锁区间时，ETRAS 可进入预位。",
            "R-C919-ARM: ETRAS 仅在 WOW 有效且手柄解锁区间成立后进入预位。",
            "R-C919-GATE: WOW 有效是 ETRAS 预位的前置门限。",
            "边界: 本片段只用于候选解释，不修改控制器，不构成冻结版或认证声明。",
        ]
    )


def _c919_raw_intake_requirements_payload() -> dict[str, Any]:
    return {
        "source": "pending_local_preparse_endpoint",
        "document_text": _c919_raw_requirement_text(),
        "document_name": "c919-etras-raw-intake.txt",
    }


def _c919_real_doc_raw_intake_requirements_payload() -> dict[str, Any]:
    document_path = PROJECT_ROOT / "docs" / "c919_etras" / "requirements_v0_9.md"
    return {
        "source": "pending_local_preparse_endpoint",
        "document_text": document_path.read_text(encoding="utf-8"),
        "document_name": document_path.name,
        "document_path": str(document_path.relative_to(PROJECT_ROOT)),
    }


def _post_json(url: str, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20.0) as response:
        response_body = response.read().decode("utf-8")
        decoded = json.loads(response_body)
        if not isinstance(decoded, dict):
            raise RuntimeError("local-preparse endpoint returned a non-object payload")
        return response.status, decoded


def _c919_drawing_payload() -> dict[str, Any]:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": "c919abc123",
        "summary_zh": "C919 ETRAS 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "wow_valid",
                "label": "WOW 有效",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 190,
                "height": 96,
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
                "x": 420,
                "y": 120,
                "width": 200,
                "height": 104,
                "description_zh": "反推预位候选逻辑。",
            },
        ],
        "edges": [
            {
                "id": "c919_edge",
                "source": "wow_valid",
                "target": "etras_armed",
                "label": "WOW gating",
                "route": [{"x": 270, "y": 168}, {"x": 420, "y": 168}],
                "source_anchors": [
                    {
                        "id": "C919-ETRAS-WOW-EDGE",
                        "kind": "需求条款",
                        "origin": "c919_etras_doc",
                        "quote_zh": "WOW 有效是 ETRAS 预位的前置门限。",
                    }
                ],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["C919 ETRAS 第二域 fixture，仅候选图纸。"],
    }


def _c919_v09_cmd2_drawing_payload() -> dict[str, Any]:
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": "c919v09realdoc",
        "summary_zh": "C919 ETRAS V0.9 CMD2 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "mlg_wow",
                "label": "MLG_WOW",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 190,
                "height": 96,
                "description_zh": "主轮载荷/WOW 已解析单路输入。",
            },
            {
                "id": "cmd2_active",
                "label": "CMD2 单相解锁",
                "node_kind": "logic",
                "x": 420,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": "TLS 与吊挂锁 115VAC 单相解锁供电候选节点。",
            },
        ],
        "edges": [
            {
                "id": "c919_v09_cmd2_edge",
                "source": "mlg_wow",
                "target": "cmd2_active",
                "label": "CMD2 ground gate",
                "route": [{"x": 270, "y": 168}, {"x": 420, "y": 168}],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw intake gate，仅候选图纸。"],
    }


def _requirement_item_by_id(items: list[Any], item_id: str) -> dict[str, Any]:
    for item in items:
        if isinstance(item, dict) and _str(item.get("id")) == item_id:
            return item
    return {}


def _requirement_edge_by_pair(items: list[Any], source: str, target: str) -> dict[str, Any]:
    for item in items:
        if (
            isinstance(item, dict)
            and _str(item.get("source")) == source
            and _str(item.get("target")) == target
        ):
            return item
    return {}


def _payload_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _c919_v09_cmd2_drawing_from_requirements_payload(requirements_payload: dict[str, Any]) -> dict[str, Any]:
    nodes = requirements_payload.get("concept_logic_nodes", [])
    edges = requirements_payload.get("concept_edges", [])
    mlg_wow = _requirement_item_by_id(nodes, "mlg_wow")
    cmd2_active = _requirement_item_by_id(nodes, "cmd2_active")
    cmd2_edge = _requirement_edge_by_pair(edges, "mlg_wow", "cmd2_active")
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "summary_zh": "C919 ETRAS V0.9 raw preparse 派生 CMD2 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "mlg_wow",
                "label": _str(mlg_wow.get("label"), "MLG_WOW"),
                "node_kind": _str(mlg_wow.get("node_kind"), "input"),
                "x": 80,
                "y": 120,
                "width": 190,
                "height": 96,
                "description_zh": _str(mlg_wow.get("description_zh"), "主轮载荷/WOW 已解析单路输入。"),
                "source_anchors": mlg_wow.get("source_anchors") or [],
            },
            {
                "id": "cmd2_active",
                "label": _str(cmd2_active.get("label"), "CMD2 单相解锁"),
                "node_kind": _str(cmd2_active.get("node_kind"), "logic"),
                "x": 420,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": _str(
                    cmd2_active.get("description_zh"),
                    "TLS 与吊挂锁 115VAC 单相解锁供电候选节点。",
                ),
                "source_anchors": cmd2_active.get("source_anchors") or [],
            },
        ],
        "edges": [
            {
                "id": "c919_v09_cmd2_edge",
                "source": "mlg_wow",
                "target": "cmd2_active",
                "label": _str(cmd2_edge.get("label"), "CMD2 ground gate"),
                "route": [{"x": 270, "y": 168}, {"x": 420, "y": 168}],
                "source_anchors": cmd2_edge.get("source_anchors") or [],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw preparse 派生图纸，仅候选图纸。"],
        "derived_from": "raw_preparse_payload",
    }


def _c919_v09_cmd3_apwtla_drawing_from_requirements_payload(requirements_payload: dict[str, Any]) -> dict[str, Any]:
    nodes = requirements_payload.get("concept_logic_nodes", [])
    edges = requirements_payload.get("concept_edges", [])
    apwtla = _requirement_item_by_id(nodes, "apwtla")
    cmd3_output = _requirement_item_by_id(nodes, "cmd3_output")
    cmd3_edge = _requirement_edge_by_pair(edges, "apwtla", "cmd3_output")
    if not apwtla or not cmd3_output or not cmd3_edge:
        raise RuntimeError("raw preparse payload did not contain the CMD3/APWTLA candidate chain")
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "summary_zh": "C919 ETRAS V0.9 raw preparse 派生 CMD3/APWTLA 候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "apwtla",
                "label": _str(apwtla.get("label")),
                "node_kind": _str(apwtla.get("node_kind")),
                "x": 80,
                "y": 120,
                "width": 190,
                "height": 96,
                "description_zh": _str(apwtla.get("description_zh")),
                "source_anchors": apwtla.get("source_anchors") or [],
            },
            {
                "id": "cmd3_output",
                "label": _str(cmd3_output.get("label")),
                "node_kind": _str(cmd3_output.get("node_kind")),
                "x": 420,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": _str(cmd3_output.get("description_zh")),
                "source_anchors": cmd3_output.get("source_anchors") or [],
            },
        ],
        "edges": [
            {
                "id": "c919_v09_cmd3_apwtla_edge",
                "source": "apwtla",
                "target": "cmd3_output",
                "label": _str(cmd3_edge.get("label")),
                "route": [{"x": 270, "y": 168}, {"x": 420, "y": 168}],
                "source_anchors": cmd3_edge.get("source_anchors") or [],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw preparse 派生 CMD3/APWTLA 图纸，仅候选图纸。"],
        "derived_from": "raw_preparse_payload",
    }


def _c919_v09_mlg_wow_fanout_drawing_from_requirements_payload(requirements_payload: dict[str, Any]) -> dict[str, Any]:
    nodes = requirements_payload.get("concept_logic_nodes", [])
    edges = requirements_payload.get("concept_edges", [])
    mlg_wow = _requirement_item_by_id(nodes, "mlg_wow")
    cmd2_active = _requirement_item_by_id(nodes, "cmd2_active")
    cmd3_output = _requirement_item_by_id(nodes, "cmd3_output")
    cmd2_edge = _requirement_edge_by_pair(edges, "mlg_wow", "cmd2_active")
    cmd3_edge = _requirement_edge_by_pair(edges, "mlg_wow", "cmd3_output")
    if not mlg_wow or not cmd2_active or not cmd3_output or not cmd2_edge or not cmd3_edge:
        raise RuntimeError("raw preparse payload did not contain the MLG_WOW fan-out candidate chain")
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "summary_zh": "C919 ETRAS V0.9 raw preparse 派生 MLG_WOW 到 CMD2/CMD3 的真实多分叉候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "mlg_wow",
                "label": _str(mlg_wow.get("label")),
                "node_kind": _str(mlg_wow.get("node_kind")),
                "x": 80,
                "y": 176,
                "width": 190,
                "height": 96,
                "description_zh": _str(mlg_wow.get("description_zh")),
                "source_anchors": mlg_wow.get("source_anchors") or [],
            },
            {
                "id": "cmd2_active",
                "label": _str(cmd2_active.get("label")),
                "node_kind": _str(cmd2_active.get("node_kind")),
                "x": 460,
                "y": 92,
                "width": 220,
                "height": 104,
                "description_zh": _str(cmd2_active.get("description_zh")),
                "source_anchors": cmd2_active.get("source_anchors") or [],
            },
            {
                "id": "cmd3_output",
                "label": _str(cmd3_output.get("label")),
                "node_kind": _str(cmd3_output.get("node_kind")),
                "x": 460,
                "y": 244,
                "width": 220,
                "height": 104,
                "description_zh": _str(cmd3_output.get("description_zh")),
                "source_anchors": cmd3_output.get("source_anchors") or [],
            },
        ],
        "edges": [
            {
                "id": "c919_v09_mlg_wow_cmd2_edge",
                "source": "mlg_wow",
                "target": "cmd2_active",
                "label": _str(cmd2_edge.get("label")),
                "route": [
                    {"x": 270, "y": 224},
                    {"x": 360, "y": 224},
                    {"x": 360, "y": 144},
                    {"x": 460, "y": 144},
                ],
                "source_anchors": cmd2_edge.get("source_anchors") or [],
            },
            {
                "id": "c919_v09_mlg_wow_cmd3_edge",
                "source": "mlg_wow",
                "target": "cmd3_output",
                "label": _str(cmd3_edge.get("label")),
                "route": [
                    {"x": 270, "y": 224},
                    {"x": 360, "y": 224},
                    {"x": 360, "y": 296},
                    {"x": 460, "y": 296},
                ],
                "source_anchors": cmd3_edge.get("source_anchors") or [],
            },
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw preparse 派生 MLG_WOW fan-out 图纸，仅候选图纸。"],
        "derived_from": "raw_preparse_payload",
    }


def _c919_v09_deploy_cmd1_drawing_from_requirements_payload(requirements_payload: dict[str, Any]) -> dict[str, Any]:
    nodes = requirements_payload.get("concept_logic_nodes", [])
    edges = requirements_payload.get("concept_edges", [])
    cmd3_output = _requirement_item_by_id(nodes, "cmd3_output")
    deploy_cmd1_active = _requirement_item_by_id(nodes, "deploy_cmd1_active")
    deploy_edge = _requirement_edge_by_pair(edges, "cmd3_output", "deploy_cmd1_active")
    if not cmd3_output or not deploy_cmd1_active or not deploy_edge:
        raise RuntimeError("raw preparse payload did not contain the Deploy CMD1 candidate chain")
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "summary_zh": "C919 ETRAS V0.9 raw preparse 派生 Deploy CMD1 相邻阶段候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "cmd3_output",
                "label": _str(cmd3_output.get("label")),
                "node_kind": _str(cmd3_output.get("node_kind")),
                "x": 80,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": _str(cmd3_output.get("description_zh")),
                "source_anchors": cmd3_output.get("source_anchors") or [],
            },
            {
                "id": "deploy_cmd1_active",
                "label": _str(deploy_cmd1_active.get("label")),
                "node_kind": _str(deploy_cmd1_active.get("node_kind")),
                "x": 440,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": _str(deploy_cmd1_active.get("description_zh")),
                "source_anchors": deploy_cmd1_active.get("source_anchors") or [],
            },
        ],
        "edges": [
            {
                "id": "c919_v09_deploy_cmd1_edge",
                "source": "cmd3_output",
                "target": "deploy_cmd1_active",
                "label": _str(deploy_edge.get("label")),
                "route": [{"x": 300, "y": 172}, {"x": 440, "y": 172}],
                "source_anchors": deploy_edge.get("source_anchors") or [],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw preparse 派生 Deploy CMD1 相邻阶段图纸，仅候选图纸。"],
        "derived_from": "raw_preparse_payload",
    }


def _c919_v09_thr_idle_lock_release_drawing_from_requirements_payload(requirements_payload: dict[str, Any]) -> dict[str, Any]:
    nodes = requirements_payload.get("concept_logic_nodes", [])
    edges = requirements_payload.get("concept_edges", [])
    deploy_cmd1_active = _requirement_item_by_id(nodes, "deploy_cmd1_active")
    thr_idle_lock_release = _requirement_item_by_id(nodes, "thr_idle_lock_release")
    thr_idle_edge = _requirement_edge_by_pair(edges, "deploy_cmd1_active", "thr_idle_lock_release")
    if not deploy_cmd1_active or not thr_idle_lock_release or not thr_idle_edge:
        raise RuntimeError("raw preparse payload did not contain the THR idle lock release candidate chain")
    return {
        "$schema": "https://well-harness.local/json_schema/requirements_logic_drawing_v1.schema.json",
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "source_requirements_sha256": _payload_sha256(requirements_payload),
        "summary_zh": "C919 ETRAS V0.9 raw preparse 派生 Deploy 后续展开确认/慢车锁释放候选链路。",
        "canvas": {"width": 1280, "height": 760},
        "nodes": [
            {
                "id": "deploy_cmd1_active",
                "label": _str(deploy_cmd1_active.get("label")),
                "node_kind": _str(deploy_cmd1_active.get("node_kind")),
                "x": 80,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": _str(deploy_cmd1_active.get("description_zh")),
                "source_anchors": deploy_cmd1_active.get("source_anchors") or [],
            },
            {
                "id": "thr_idle_lock_release",
                "label": _str(thr_idle_lock_release.get("label")),
                "node_kind": _str(thr_idle_lock_release.get("node_kind")),
                "x": 440,
                "y": 120,
                "width": 220,
                "height": 104,
                "description_zh": _str(thr_idle_lock_release.get("description_zh")),
                "source_anchors": thr_idle_lock_release.get("source_anchors") or [],
            },
        ],
        "edges": [
            {
                "id": "c919_v09_thr_idle_lock_release_edge",
                "source": "deploy_cmd1_active",
                "target": "thr_idle_lock_release",
                "label": _str(thr_idle_edge.get("label")),
                "route": [{"x": 300, "y": 172}, {"x": 440, "y": 172}],
                "source_anchors": thr_idle_edge.get("source_anchors") or [],
            }
        ],
        "parameter_panels": [],
        "drawing_notes": ["真实 V0.9 文档 raw preparse 派生慢车锁释放后续确认图纸，仅候选图纸。"],
        "derived_from": "raw_preparse_payload",
    }


def _scenario_fixture(scenario: str) -> dict[str, Any]:
    if scenario == "c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake":
        raw_intake = _c919_real_doc_raw_intake_requirements_payload()
        return {
            "scenario": "c919_etras_mlg_wow_cmd2_cmd3_fanout_real_doc_raw_intake",
            "requirements_payload": {},
            "drawing_payload": {},
            "drawing_from_raw_preparse": "c919_v09_mlg_wow_fanout",
            "feedback_text": "MLG_WOW 分叉说明应写明这是 V0.9 中同时进入 CMD2 与 CMD3 的候选链路，不是两条无关连线。",
            "first_target_id": "mlg_wow",
            "second_target_id": "cmd2_active",
            "wire_target_id": "mlg_wow->cmd2_active",
            "first_target_key": "node:mlg_wow",
            "second_target_key": "node:cmd2_active",
            "wire_target_key": "wire:mlg_wow->cmd2_active",
            "confirm_until_active_target_key": "wire:mlg_wow->cmd2_active",
            "source_anchor_id": "C919-V09-MLG-WOW",
            "requires_fanout_junction": True,
            "expected_fanout_junction_count": 1,
            "raw_intake": {
                "endpoint_path": "/api/requirements-intake/local-preparse",
                "document_text": raw_intake["document_text"],
                "document_name": raw_intake["document_name"],
                "document_path": raw_intake["document_path"],
                "expected_source_document_name": "requirements_v0_9.md",
                "expected_strategy": "c919_etras_v09_rule_preparse",
                "required_node_ids": ["mlg_wow", "cmd2_active", "cmd3_output"],
                "forbidden_node_ids": ["etras_armed", "stow_cmd1_active"],
                "required_edge_ids": ["c919_v09_e1", "c919_v09_e3"],
                "required_edge_labels": ["CMD2 ground gate", "CMD3 ground gate"],
                "required_anchor_ids": [
                    "C919-V09-MLG-WOW",
                    "C919-V09-CMD2",
                    "C919-V09-CMD2-MLG-WOW",
                    "C919-V09-CMD3",
                    "C919-V09-CMD3-SR-OUTPUT",
                ],
                "required_anchor_texts": [
                    "`mlg_wow`",
                    "CMD2",
                    "CMD3",
                    "ThreePhaseTRCUPower_On = cmd3_output",
                ],
                "forbidden_anchor_text": "WOW 双通道有效且反推手柄进入解锁区间",
            },
        }
    if scenario == "fantui_demo_fanout_junction":
        return {
            "scenario": "fantui_demo_fanout_junction",
            "requirements_payload": _fantui_demo_fanout_requirements_payload(),
            "drawing_payload": _fantui_demo_fanout_drawing_payload(),
            "feedback_text": "L3 fan-out 节点说明应写明这是 demo.html 风格共享 trunk，不是三条独立端点点。",
            "first_target_id": "logic3_fanout",
            "second_target_id": "eec_deploy",
            "wire_target_id": "logic3_fanout->eec_deploy",
            "first_target_key": "node:logic3_fanout",
            "second_target_key": "node:eec_deploy",
            "wire_target_key": "wire:logic3_fanout->eec_deploy",
            "confirm_until_active_target_key": "wire:logic3_fanout->eec_deploy",
            "source_anchor_id": "FANOUT-L3-SOURCE",
            "requires_fanout_junction": True,
            "expected_fanout_junction_count": 1,
        }
    if scenario == "c919_etras_deploy_cmd1_thr_idle_lock_release_real_doc_raw_intake":
        raw_intake = _c919_real_doc_raw_intake_requirements_payload()
        return {
            "scenario": "c919_etras_deploy_cmd1_thr_idle_lock_release_real_doc_raw_intake",
            "requirements_payload": {},
            "drawing_payload": {},
            "drawing_from_raw_preparse": "c919_v09_thr_idle_lock_release",
            "feedback_text": "慢车锁释放连线说明应写明这是 Deploy 后续展开确认候选链路，不是 Deploy CMD1 的直接布尔门限。",
            "first_target_id": "deploy_cmd1_active",
            "second_target_id": "thr_idle_lock_release",
            "wire_target_id": "deploy_cmd1_active->thr_idle_lock_release",
            "first_target_key": "node:deploy_cmd1_active",
            "second_target_key": "node:thr_idle_lock_release",
            "wire_target_key": "wire:deploy_cmd1_active->thr_idle_lock_release",
            "source_anchor_id": "C919-V09-DEPLOY-CMD1-OUTPUT",
            "raw_intake": {
                "endpoint_path": "/api/requirements-intake/local-preparse",
                "document_text": raw_intake["document_text"],
                "document_name": raw_intake["document_name"],
                "document_path": raw_intake["document_path"],
                "expected_source_document_name": "requirements_v0_9.md",
                "expected_strategy": "c919_etras_v09_rule_preparse",
                "required_node_ids": ["deploy_cmd1_active", "thr_idle_lock_release"],
                "forbidden_node_ids": ["etras_armed", "stow_cmd1_active"],
                "required_edge_ids": ["c919_v09_e6"],
                "required_edge_labels": ["TR deployed confirmation"],
                "forbidden_edge_labels": [
                    "Deploy CMD1 directly releases THR idle lock",
                    "Deploy CMD1 gates thr idle lock release",
                ],
                "required_anchor_ids": [
                    "C919-V09-PRE-FREEZE",
                    "C919-V09-DEPLOY-CMD1",
                    "C919-V09-DEPLOY-CMD1-OUTPUT",
                    "C919-V09-DEPLOY-CMD1-ENGINE",
                    "C919-V09-DEPLOY-CMD1-INHIBITED",
                    "C919-V09-DEPLOY-CMD1-LOCKS",
                    "C919-V09-DEPLOY-CMD1-TR-WOW",
                    "C919-V09-DEPLOY-CMD1-N1K",
                    "C919-V09-DEPLOY-CMD1-TRA",
                    "C919-V09-THR-IDLE-LOCK",
                    "C919-V09-THR-IDLE-OUTPUT",
                    "C919-V09-THR-IDLE-TR-DEPLOYED",
                    "C919-V09-THR-IDLE-POS-CONF",
                    "C919-V09-EVAL-DEPLOY-CMD1",
                    "C919-V09-EVAL-THR-IDLE-LOCK",
                    "C919-V09-ACCEPT-THR-IDLE-LOCK",
                ],
                "required_anchor_texts": [
                    "FADEC_Deploy_Command = deploy_cmd1_active",
                    "engine_running OR maintenance_cycle",
                    "tr_inhibited",
                    "locks_unlocked_or_confirmed",
                    "tr_wow",
                    "max_n1k_deploy_limit_pct",
                    "tra_deg",
                    "`thr_idle_lock_release`",
                    "`tr_deployed_confirmed`",
                    "TR_Position ≥ 80%",
                    "持续 0.5s",
                    "10. 评估 油门慢车锁释放",
                    "TR_Deployed_Confirmed=TRUE",
                ],
                "forbidden_anchor_text": "WOW 双通道有效且反推手柄进入解锁区间",
            },
        }
    if scenario == "c919_etras_deploy_cmd1_real_doc_raw_intake":
        raw_intake = _c919_real_doc_raw_intake_requirements_payload()
        return {
            "scenario": "c919_etras_deploy_cmd1_real_doc_raw_intake",
            "requirements_payload": {},
            "drawing_payload": {},
            "drawing_from_raw_preparse": "c919_v09_deploy_cmd1",
            "feedback_text": "Deploy CMD1 连线说明应写明这是 CMD3 之后的相邻评估阶段候选解释，不是布尔门限。",
            "first_target_id": "cmd3_output",
            "second_target_id": "deploy_cmd1_active",
            "wire_target_id": "cmd3_output->deploy_cmd1_active",
            "first_target_key": "node:cmd3_output",
            "second_target_key": "node:deploy_cmd1_active",
            "wire_target_key": "wire:cmd3_output->deploy_cmd1_active",
            "source_anchor_id": "C919-V09-CMD3-SR-OUTPUT",
            "raw_intake": {
                "endpoint_path": "/api/requirements-intake/local-preparse",
                "document_text": raw_intake["document_text"],
                "document_name": raw_intake["document_name"],
                "document_path": raw_intake["document_path"],
                "expected_source_document_name": "requirements_v0_9.md",
                "expected_strategy": "c919_etras_v09_rule_preparse",
                "required_node_ids": ["cmd3_output", "deploy_cmd1_active"],
                "forbidden_node_ids": ["etras_armed", "stow_cmd1_active"],
                "required_edge_ids": ["c919_v09_e5"],
                "required_edge_labels": ["Deploy CMD1 evaluation after CMD3"],
                "forbidden_edge_labels": ["TRCU power before deploy", "CMD3 output gates deploy"],
                "required_anchor_ids": [
                    "C919-V09-CMD3-SR-OUTPUT",
                    "C919-V09-CMD3-RESET-PRIORITY",
                    "C919-V09-DEPLOY-CMD1",
                    "C919-V09-DEPLOY-CMD1-OUTPUT",
                    "C919-V09-DEPLOY-CMD1-LOCKS",
                    "C919-V09-DEPLOY-CMD1-TR-WOW",
                    "C919-V09-DEPLOY-CMD1-N1K",
                    "C919-V09-DEPLOY-CMD1-TRA",
                    "C919-V09-EVAL-CMD3-SR-OUTPUT",
                    "C919-V09-EVAL-DEPLOY-CMD1",
                ],
                "required_anchor_texts": [
                    "ThreePhaseTRCUPower_On = cmd3_output",
                    "Reset 优先",
                    "FADEC_Deploy_Command = deploy_cmd1_active",
                    "locks_unlocked_or_confirmed",
                    "tr_wow",
                    "max_n1k_deploy_limit_pct",
                    "tra_deg",
                    "6. 评估 CMD3 SR 锁存输出",
                    "8. 评估 Deploy CMD1",
                ],
                "forbidden_anchor_text": "WOW 双通道有效且反推手柄进入解锁区间",
            },
        }
    if scenario == "c919_etras_cmd3_apwtla_real_doc_raw_intake":
        raw_intake = _c919_real_doc_raw_intake_requirements_payload()
        return {
            "scenario": "c919_etras_cmd3_apwtla_real_doc_raw_intake",
            "requirements_payload": {},
            "drawing_payload": {},
            "drawing_from_raw_preparse": "c919_v09_cmd3_apwtla",
            "feedback_text": "APWTLA 节点说明应写明这是 CMD3 Set 的 SW2 置位候选解释，并补一个需求文档候选补丁。",
            "first_target_id": "apwtla",
            "second_target_id": "cmd3_output",
            "wire_target_id": "apwtla->cmd3_output",
            "first_target_key": "node:apwtla",
            "second_target_key": "node:cmd3_output",
            "wire_target_key": "wire:apwtla->cmd3_output",
            "source_anchor_id": "C919-V09-CMD3-SET-APWTLA",
            "raw_intake": {
                "endpoint_path": "/api/requirements-intake/local-preparse",
                "document_text": raw_intake["document_text"],
                "document_name": raw_intake["document_name"],
                "document_path": raw_intake["document_path"],
                "expected_source_document_name": "requirements_v0_9.md",
                "expected_strategy": "c919_etras_v09_rule_preparse",
                "required_node_ids": ["apwtla", "cmd3_output"],
                "forbidden_node_ids": ["etras_armed"],
                "required_edge_ids": ["c919_v09_e4"],
                "required_edge_labels": ["SW2 set gate"],
                "required_anchor_ids": [
                    "C919-V09-APWTLA",
                    "C919-V09-CMD3-SET",
                    "C919-V09-CMD3-SET-APWTLA",
                    "C919-V09-CMD3-SR-OUTPUT",
                    "C919-V09-CMD3-RESET-PRIORITY",
                ],
                "required_anchor_texts": [
                    "`apwtla`",
                    "CMD3 Set",
                    "ThreePhaseTRCUPower_On = cmd3_output",
                    "Reset 优先",
                ],
                "forbidden_anchor_text": "WOW 双通道有效且反推手柄进入解锁区间",
            },
        }
    if scenario == "c919_etras_real_doc_raw_intake":
        raw_intake = _c919_real_doc_raw_intake_requirements_payload()
        return {
            "scenario": "c919_etras_real_doc_raw_intake",
            "requirements_payload": {},
            "drawing_payload": {},
            "drawing_from_raw_preparse": "c919_v09_cmd2",
            "feedback_text": "MLG_WOW 节点说明应写明这是 C919 ETRAS V0.9 原文候选解释，并补一个需求文档候选补丁。",
            "first_target_id": "mlg_wow",
            "second_target_id": "cmd2_active",
            "wire_target_id": "mlg_wow->cmd2_active",
            "first_target_key": "node:mlg_wow",
            "second_target_key": "node:cmd2_active",
            "wire_target_key": "wire:mlg_wow->cmd2_active",
            "source_anchor_id": "C919-V09-MLG-WOW",
            "raw_intake": {
                "endpoint_path": "/api/requirements-intake/local-preparse",
                "document_text": raw_intake["document_text"],
                "document_name": raw_intake["document_name"],
                "document_path": raw_intake["document_path"],
                "expected_source_document_name": "requirements_v0_9.md",
                "expected_strategy": "c919_etras_v09_rule_preparse",
                "required_node_ids": ["mlg_wow", "cmd2_active"],
                "forbidden_node_ids": ["etras_armed"],
                "required_edge_labels": ["CMD2 ground gate"],
                "required_anchor_text": "`mlg_wow`",
                "forbidden_anchor_text": "WOW 双通道有效且反推手柄进入解锁区间",
            },
        }
    if scenario == "c919_etras_raw_intake":
        raw_intake = _c919_raw_intake_requirements_payload()
        return {
            "scenario": "c919_etras_raw_intake",
            "requirements_payload": {},
            "drawing_payload": _c919_drawing_payload(),
            "feedback_text": "WOW 有效节点说明应写明这是 C919 ETRAS 原始需求候选解释，并补一个需求文档候选补丁。",
            "first_target_id": "wow_valid",
            "second_target_id": "etras_armed",
            "wire_target_id": "wow_valid->etras_armed",
            "first_target_key": "node:wow_valid",
            "second_target_key": "node:etras_armed",
            "wire_target_key": "wire:wow_valid->etras_armed",
            "source_anchor_id": "C919-ETRAS-WOW",
            "raw_intake": {
                "endpoint_path": "/api/requirements-intake/local-preparse",
                "document_text": raw_intake["document_text"],
                "document_name": raw_intake["document_name"],
                "expected_source_document_name": "c919-etras-raw-intake.txt",
                "expected_strategy": "c919_etras_rule_preparse",
                "required_node_ids": ["wow_valid", "etras_armed"],
                "forbidden_node_ids": [],
                "required_edge_labels": ["WOW gating"],
                "required_anchor_text": "WOW 双通道有效",
                "forbidden_anchor_text": "",
            },
        }
    if scenario == "c919_etras":
        return {
            "scenario": "c919_etras",
            "requirements_payload": _c919_requirements_payload(),
            "drawing_payload": _c919_drawing_payload(),
            "feedback_text": "WOW 有效节点说明应写明这是 C919 ETRAS 候选解释，并补一个需求文档候选补丁。",
            "first_target_id": "wow_valid",
            "second_target_id": "etras_armed",
            "wire_target_id": "wow_valid->etras_armed",
            "first_target_key": "node:wow_valid",
            "second_target_key": "node:etras_armed",
            "wire_target_key": "wire:wow_valid->etras_armed",
            "source_anchor_id": "C919-ETRAS-WOW",
        }
    return {
        "scenario": "fantui",
        "requirements_payload": _fantui_requirements_payload(),
        "drawing_payload": _fantui_drawing_payload(),
        "feedback_text": "RA 节点说明应写明这是候选解释，并补一个需求文档候选补丁。",
        "first_target_id": "RA",
        "second_target_id": "L1",
        "wire_target_id": "RA->L1",
        "first_target_key": "node:RA",
        "second_target_key": "node:L1",
        "wire_target_key": "wire:RA->L1",
        "source_anchor_id": "REQ-RA",
    }


def _seed_script(fixture: dict[str, Any]) -> str:
    return """
localStorage.setItem(
  'ai-fantui-requirements-intake-ready-v1',
  JSON.stringify(%s)
);
localStorage.setItem(
  'ai-fantui-logic-builder-drawing-v1',
  JSON.stringify(%s)
);
localStorage.removeItem('%s');
""" % (
        json.dumps(fixture["requirements_payload"], ensure_ascii=False),
        json.dumps(fixture["drawing_payload"], ensure_ascii=False),
        STREAMED_AUTHORING_KEY,
    )


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify_m21_revision_browser_gate(
    artifact_dir: Path = DEFAULT_ARTIFACT_DIR,
    *,
    scenario: str = "fantui",
) -> dict[str, Any]:
    fixture = _scenario_fixture(scenario)
    artifact_dir = artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_stamp = _utc_stamp()
    summary_path = artifact_dir / SUMMARY_NAME
    screenshot_path = artifact_dir / (
        f"m21-streamed-authoring-{fixture['scenario']}-queue-{artifact_stamp}.png"
    )
    step_confirmation_screenshot_path = artifact_dir / (
        f"m21-streamed-authoring-{fixture['scenario']}-natural-language-step-{artifact_stamp}.png"
    )
    revision_confirmation_screenshot_path = artifact_dir / (
        f"m21-streamed-authoring-{fixture['scenario']}-feedback-revision-{artifact_stamp}.png"
    )
    restricted_before = _restricted_diff()
    console_errors: list[str] = []
    feedback_text = fixture["feedback_text"]
    natural_language_prompt = fixture.get(
        "natural_language_prompt",
        "请按需求原文逐步提出下一个节点或连线候选，等待工程师确认。",
    )
    natural_language_start_session: dict[str, Any] = {}
    revision_session: dict[str, Any] = {}
    after_revised_confirm_session: dict[str, Any] = {}
    after_second_confirm_session: dict[str, Any] = {}
    raw_intake_endpoint: dict[str, Any] = {}
    confirm_next_sessions: list[dict[str, Any]] = []
    first_target_id = fixture["first_target_id"]
    second_target_id = fixture["second_target_id"]
    wire_target_id = fixture["wire_target_id"]
    first_target_key = fixture["first_target_key"]
    second_target_key = fixture["second_target_key"]
    wire_target_key = fixture["wire_target_key"]
    confirm_until_active_target_key = _str(
        fixture.get("confirm_until_active_target_key")
    ) or wire_target_key

    server, thread, base_url = _start_server()
    try:
        if fixture.get("raw_intake"):
            raw_intake = fixture["raw_intake"]
            status_code, requirements_payload = _post_json(
                f"{base_url}{raw_intake['endpoint_path']}",
                {
                    "document_text": raw_intake["document_text"],
                    "document_name": raw_intake["document_name"],
                },
            )
            fixture["requirements_payload"] = requirements_payload
            raw_preparse_payload_sha256 = _payload_sha256(requirements_payload)
            raw_preparse_payload_path = artifact_dir / (
                f"{fixture['scenario']}-raw-preparse-payload.json"
            )
            _write_json(raw_preparse_payload_path, requirements_payload)
            if fixture.get("drawing_from_raw_preparse") == "c919_v09_cmd2":
                fixture["drawing_payload"] = _c919_v09_cmd2_drawing_from_requirements_payload(
                    requirements_payload
                )
            elif fixture.get("drawing_from_raw_preparse") == "c919_v09_mlg_wow_fanout":
                fixture["drawing_payload"] = _c919_v09_mlg_wow_fanout_drawing_from_requirements_payload(
                    requirements_payload
                )
            elif fixture.get("drawing_from_raw_preparse") == "c919_v09_cmd3_apwtla":
                fixture["drawing_payload"] = _c919_v09_cmd3_apwtla_drawing_from_requirements_payload(
                    requirements_payload
                )
            elif fixture.get("drawing_from_raw_preparse") == "c919_v09_deploy_cmd1":
                fixture["drawing_payload"] = _c919_v09_deploy_cmd1_drawing_from_requirements_payload(
                    requirements_payload
                )
            elif fixture.get("drawing_from_raw_preparse") == "c919_v09_thr_idle_lock_release":
                fixture["drawing_payload"] = _c919_v09_thr_idle_lock_release_drawing_from_requirements_payload(
                    requirements_payload
                )
            raw_intake_endpoint = {
                "endpoint_path": raw_intake["endpoint_path"],
                "http_status": status_code,
                "document_name": raw_intake["document_name"],
                "payload_kind": requirements_payload.get("kind", ""),
                "raw_preparse_payload_artifact": str(raw_preparse_payload_path),
                "raw_preparse_payload_sha256": raw_preparse_payload_sha256,
            }
        expected_total_candidate_count = _drawing_candidate_count(fixture["drawing_payload"])
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                context = browser.new_context(
                    viewport={"width": 1440, "height": 980},
                    device_scale_factor=1,
                )
                context.add_init_script(_seed_script(fixture))
                page = context.new_page()
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                page.on(
                    "console",
                    lambda msg: console_errors.append(msg.text)
                    if msg.type == "error"
                    else None,
                )
                page.goto(f"{base_url}/logic-builder", wait_until="networkidle")
                page.wait_for_selector("#logic-streamed-panel-toggle", timeout=10000)
                page.wait_for_function(
                    """() => {
                      const visibleButtons = Array.from(document.querySelectorAll('button'))
                        .filter((button) => button.getClientRects().length > 0);
                      const input = document.querySelector('#logic-natural-language-input');
                      const shell = document.querySelector('.logic-shell');
                      const command = document.querySelector('#logic-command-palette-open');
                      const dock = document.querySelector('#logic-mode-dock');
                      const bottom = document.querySelector('#logic-bottom-run-strip');
                      return document.body.dataset.logicInteractionMode === 'natural-language'
                        && shell
                        && shell.dataset.workbenchInputModel === 'natural-language'
                        && input
                        && input.getClientRects().length > 0
                        && visibleButtons.length <= 3
                        && command
                        && getComputedStyle(command).display === 'none'
                        && dock
                        && getComputedStyle(dock).display === 'none'
                        && bottom
                        && getComputedStyle(bottom).display === 'none';
                    }""",
                    timeout=10000,
                )
                natural_language_visible_button_count = page.evaluate(
                    """() => Array.from(document.querySelectorAll('button'))
                      .filter((button) => button.getClientRects().length > 0)
                      .length"""
                )
                natural_language_input_visible = page.locator(
                    "#logic-natural-language-input"
                ).evaluate("el => el.getClientRects().length > 0")
                natural_language_command_trigger_display = page.locator(
                    "#logic-command-palette-open"
                ).evaluate("el => getComputedStyle(el).display")
                natural_language_mode_dock_display = page.locator(
                    "#logic-mode-dock"
                ).evaluate("el => getComputedStyle(el).display")
                natural_language_bottom_run_display = page.locator(
                    "#logic-bottom-run-strip"
                ).evaluate("el => getComputedStyle(el).display")
                natural_language_interaction_mode = page.locator("body").get_attribute(
                    "data-logic-interaction-mode"
                )
                natural_language_input_model = page.locator(".logic-shell").get_attribute(
                    "data-workbench-input-model"
                )
                page.fill("#logic-natural-language-input", natural_language_prompt)
                page.wait_for_function(
                    "!document.querySelector('#logic-natural-language-send').disabled",
                    timeout=10000,
                )
                with page.expect_response(
                    lambda response: response.url.endswith(STREAMED_PROPOSAL_PATH)
                    and response.request.method == "POST",
                    timeout=10000,
                ) as natural_language_start_response:
                    page.click("#logic-natural-language-send")
                natural_language_start_session = natural_language_start_response.value.json()
                page.wait_for_selector(
                    (
                        '#logic-streamed-authoring-panel'
                        '[data-state="awaiting-confirmation"]'
                        '[data-panel-visibility="expanded"]'
                        '[data-launch-source="natural-language"]'
                        '[data-natural-language-step-confirmation="awaiting-engineer"]'
                    ),
                    timeout=10000,
                )
                page.wait_for_selector(
                    (
                        '#logic-streamed-current'
                        '[data-natural-language-confirmation="candidate-awaiting-engineer-confirmation"]'
                        '[data-source-excerpt-present="true"]'
                        f'[data-target-id="{first_target_id}"]'
                        '[data-active-sequence-index="1"]'
                    ),
                    timeout=10000,
                )
                page.wait_for_function(
                    """() => {
                      const source = document.querySelector('#logic-streamed-source');
                      const explanation = document.querySelector('#logic-streamed-explanation');
                      const neighborhood = document.querySelector('#logic-streamed-neighborhood');
                      return source
                        && explanation
                        && neighborhood
                        && source.dataset.sourceHighlight === 'active'
                        && explanation.dataset.logicHighlight === 'active'
                        && neighborhood.dataset.wireLogicHighlight === 'active'
                        && document.querySelectorAll('.is-streamed-authoring-active').length > 0;
                    }""",
                    timeout=10000,
                )
                page.wait_for_function(
                    "!document.querySelector('#logic-streamed-revise').disabled",
                    timeout=10000,
                )
                natural_language_streamed_panel_visibility_after_submit = page.locator(
                    "#logic-streamed-authoring-panel"
                ).get_attribute("data-panel-visibility")
                natural_language_streamed_launch_source = page.locator(
                    "#logic-streamed-authoring-panel"
                ).get_attribute("data-launch-source")
                natural_language_streamed_launch_prompt_present = page.locator(
                    "#logic-streamed-authoring-panel"
                ).get_attribute("data-launch-prompt-present")
                natural_language_streamed_step_confirmation = page.locator(
                    "#logic-streamed-authoring-panel"
                ).get_attribute("data-natural-language-step-confirmation")
                natural_language_streamed_current_confirmation = page.locator(
                    "#logic-streamed-current"
                ).get_attribute("data-natural-language-confirmation")
                natural_language_streamed_source_highlight = page.locator(
                    "#logic-streamed-source"
                ).get_attribute("data-source-highlight")
                natural_language_streamed_logic_highlight = page.locator(
                    "#logic-streamed-explanation"
                ).get_attribute("data-logic-highlight")
                natural_language_streamed_wire_logic_highlight = page.locator(
                    "#logic-streamed-neighborhood"
                ).get_attribute("data-wire-logic-highlight")
                natural_language_streamed_highlight_count = page.locator(
                    ".is-streamed-authoring-active"
                ).count()
                natural_language_streamed_confirm_enabled = page.locator(
                    "#logic-streamed-confirm"
                ).evaluate("el => !el.disabled")
                natural_language_streamed_active_target_id = page.locator(
                    "#logic-streamed-current"
                ).get_attribute("data-target-id")
                natural_language_streamed_active_sequence_index = page.locator(
                    "#logic-streamed-current"
                ).get_attribute("data-active-sequence-index")
                natural_language_streamed_replay_event_count = page.locator(
                    "#logic-streamed-history [data-stream-replay-event]"
                ).count()
                natural_language_step_visual_framing = page.evaluate(
                    """() => {
                      function rectFor(selector) {
                        const element = document.querySelector(selector);
                        if (!element) return null;
                        const rect = element.getBoundingClientRect();
                        return {
                          left: rect.left,
                          top: rect.top,
                          right: rect.right,
                          bottom: rect.bottom,
                          width: rect.width,
                          height: rect.height,
                        };
                      }
                      const canvas = rectFor('#logic-canvas');
                      const active = rectFor('.is-streamed-authoring-active');
                      const panel = rectFor('#logic-streamed-authoring-panel');
                      const viewport = {
                        width: Math.max(1, window.innerWidth || 1),
                        height: Math.max(1, window.innerHeight || 1),
                      };
                      const activeVisibleInCanvas = Boolean(
                        canvas
                        && active
                        && active.left >= canvas.left
                        && active.right <= canvas.right
                        && active.top >= canvas.top
                        && active.bottom <= canvas.bottom
                      );
                      const activeCenter = active
                        ? {
                          x: active.left + (active.width / 2),
                          y: active.top + (active.height / 2),
                        }
                        : {x: -1, y: -1};
                      const activeHitTestVisible = Boolean(
                        active
                        && document.elementsFromPoint(activeCenter.x, activeCenter.y)
                          .some((element) => (
                            element.classList
                            && element.classList.contains('is-streamed-authoring-active')
                          ) || (
                            typeof element.closest === 'function'
                            && element.closest('.is-streamed-authoring-active')
                          ))
                      );
                      const boxes = [canvas, active, panel].filter(Boolean);
                      const minTop = boxes.length
                        ? Math.min(...boxes.map((box) => box.top))
                        : 0;
                      const maxBottom = boxes.length
                        ? Math.max(...boxes.map((box) => box.bottom))
                        : viewport.height;
                      const clipTop = Math.max(0, Math.floor(minTop - 18));
                      const clipBottom = Math.min(
                        viewport.height,
                        Math.ceil(maxBottom + 24),
                      );
                      const clipHeight = Math.max(
                        240,
                        Math.min(620, clipBottom - clipTop),
                      );
                      return {
                        canvas_height_after_submit: Math.round(canvas ? canvas.height : 0),
                        active_target_visible_in_canvas: activeVisibleInCanvas,
                        active_target_hit_test_visible: activeHitTestVisible,
                        panel_visible_for_step_screenshot: Boolean(
                          panel
                          && panel.bottom > clipTop
                          && panel.top < clipTop + clipHeight
                        ),
                        active_visible_for_step_screenshot: Boolean(
                          active
                          && active.bottom > clipTop
                          && active.top < clipTop + clipHeight
                        ),
                        screenshot_clip: {
                          x: 0,
                          y: clipTop,
                          width: viewport.width,
                          height: clipHeight,
                        },
                      };
                    }"""
                )
                natural_language_step_screenshot_clip = (
                    natural_language_step_visual_framing.get("screenshot_clip", {})
                    if isinstance(natural_language_step_visual_framing, dict)
                    else {}
                )
                page.screenshot(
                    path=str(step_confirmation_screenshot_path),
                    clip=natural_language_step_screenshot_clip,
                )
                page.fill("#logic-streamed-feedback", feedback_text)
                page.check("#logic-streamed-doc-edit-request")
                page.fill("#logic-streamed-doc-edit-authorization", AUTHORIZATION_PHRASE)
                with page.expect_response(
                    lambda response: response.url.endswith(STREAMED_PROPOSAL_PATH)
                    and response.request.method == "POST",
                    timeout=10000,
                ) as response_info:
                    page.click("#logic-streamed-revise")
                revision_session = response_info.value.json()
                page.wait_for_selector(
                    '#logic-streamed-history '
                    '[data-stream-replay-event="candidate_edit_revision_requested"]'
                    '[data-requirements-patch-status="authorized_candidate_patch"]',
                    timeout=10000,
                )
                page.wait_for_function(
                    """() => {
                      const gate = document.querySelector('[data-m21-gate-summary]');
                      return gate && gate.dataset.requirementsDocumentEditStatus === 'authorized_candidate_patch';
                    }""",
                    timeout=10000,
                )
                page.wait_for_selector(
                    (
                        '#logic-streamed-current'
                        '[data-proposal-status="revised_proposal_ready"]'
                        f'[data-target-id="{first_target_id}"]'
                        '[data-feedback-revision-state="candidate-recomputed"]'
                        '[data-revision-candidate="ready"]'
                    ),
                    timeout=10000,
                )
                page.wait_for_selector(
                    (
                        '#logic-streamed-authoring-panel'
                        '[data-revision-flow="candidate-recomputed"] '
                        '#logic-streamed-revision-receipt'
                        '[data-feedback-revision-state="candidate-recomputed"]'
                        '[data-feedback-applied="true"]'
                    ),
                    timeout=10000,
                )
                feedback_revision_panel_flow = page.locator(
                    "#logic-streamed-authoring-panel"
                ).get_attribute("data-revision-flow")
                feedback_revision_current_state = page.locator(
                    "#logic-streamed-current"
                ).get_attribute("data-feedback-revision-state")
                feedback_revision_candidate_state = page.locator(
                    "#logic-streamed-current"
                ).get_attribute("data-revision-candidate")
                feedback_revision_receipt_state = page.locator(
                    "#logic-streamed-revision-receipt"
                ).get_attribute("data-feedback-revision-state")
                feedback_revision_feedback_applied = page.locator(
                    "#logic-streamed-revision-receipt"
                ).get_attribute("data-feedback-applied")
                feedback_revision_status_text = page.locator(
                    "#logic-streamed-revision-status"
                ).inner_text(timeout=5000)
                feedback_revision_feedback_text = page.locator(
                    "#logic-streamed-revision-feedback"
                ).inner_text(timeout=5000)
                feedback_revision_boundary_text = page.locator(
                    "#logic-streamed-revision-boundary"
                ).inner_text(timeout=5000)
                feedback_revision_confirm_text = page.locator(
                    "#logic-streamed-confirm"
                ).inner_text(timeout=5000)
                feedback_revision_revise_text = page.locator(
                    "#logic-streamed-revise"
                ).inner_text(timeout=5000)
                feedback_revision_confirm_enabled = page.locator(
                    "#logic-streamed-confirm"
                ).evaluate("el => !el.disabled")
                feedback_revision_revise_enabled = page.locator(
                    "#logic-streamed-revise"
                ).evaluate("el => !el.disabled")
                feedback_revision_replay_event_count = page.locator(
                    '#logic-streamed-history [data-stream-replay-event="candidate_edit_revision_requested"]'
                ).count()
                feedback_revision_visual_framing = page.evaluate(
                    """() => {
                      function rectFor(selector) {
                        const element = document.querySelector(selector);
                        if (!element) return null;
                        const rect = element.getBoundingClientRect();
                        return {
                          left: rect.left,
                          top: rect.top,
                          right: rect.right,
                          bottom: rect.bottom,
                          width: rect.width,
                          height: rect.height,
                        };
                      }
                      const active = rectFor('.is-streamed-authoring-active');
                      const panel = rectFor('#logic-streamed-authoring-panel');
                      const receipt = rectFor('#logic-streamed-revision-receipt');
                      const viewport = {
                        width: Math.max(1, window.innerWidth || 1),
                        height: Math.max(1, window.innerHeight || 1),
                      };
                      const activeCenter = active
                        ? {
                          x: active.left + (active.width / 2),
                          y: active.top + (active.height / 2),
                        }
                        : {x: -1, y: -1};
                      const activeHitTestVisible = Boolean(
                        active
                        && document.elementsFromPoint(activeCenter.x, activeCenter.y)
                          .some((element) => (
                            element.classList
                            && element.classList.contains('is-streamed-authoring-active')
                          ) || (
                            typeof element.closest === 'function'
                            && element.closest('.is-streamed-authoring-active')
                          ))
                      );
                      const boxes = [active, panel, receipt].filter(Boolean);
                      const minTop = boxes.length
                        ? Math.min(...boxes.map((box) => box.top))
                        : 0;
                      const maxBottom = boxes.length
                        ? Math.max(...boxes.map((box) => box.bottom))
                        : viewport.height;
                      const clipTop = Math.max(0, Math.floor(minTop - 18));
                      const clipBottom = Math.min(
                        viewport.height,
                        Math.ceil(maxBottom + 24),
                      );
                      const clipHeight = Math.max(
                        240,
                        Math.min(620, clipBottom - clipTop),
                      );
                      return {
                        active_target_hit_test_visible: activeHitTestVisible,
                        panel_visible_for_revision_screenshot: Boolean(
                          panel
                          && panel.bottom > clipTop
                          && panel.top < clipTop + clipHeight
                        ),
                        receipt_visible_for_revision_screenshot: Boolean(
                          receipt
                          && receipt.bottom > clipTop
                          && receipt.top < clipTop + clipHeight
                        ),
                        active_visible_for_revision_screenshot: Boolean(
                          active
                          && active.bottom > clipTop
                          && active.top < clipTop + clipHeight
                        ),
                        screenshot_clip: {
                          x: 0,
                          y: clipTop,
                          width: viewport.width,
                          height: clipHeight,
                        },
                      };
                    }"""
                )
                feedback_revision_screenshot_clip = (
                    feedback_revision_visual_framing.get("screenshot_clip", {})
                    if isinstance(feedback_revision_visual_framing, dict)
                    else {}
                )
                page.screenshot(
                    path=str(revision_confirmation_screenshot_path),
                    clip=feedback_revision_screenshot_clip,
                )
                with page.expect_response(
                    lambda response: response.url.endswith(STREAMED_PROPOSAL_PATH)
                    and response.request.method == "POST",
                    timeout=10000,
                ) as confirm_revised_response:
                    page.click("#logic-streamed-confirm")
                after_revised_confirm_session = confirm_revised_response.value.json()
                page.wait_for_selector(
                    (
                        '#logic-streamed-current'
                        '[data-proposal-status="candidate_proposal_ready"]'
                        f'[data-target-id="{second_target_id}"]'
                        '[data-active-sequence-index="2"]'
                    ),
                    timeout=10000,
                )
                page.wait_for_function(
                    f"""() => {{
                      const gate = document.querySelector('[data-m21-gate-summary]');
                      return gate
                        && gate.dataset.committedEditCount === '1'
                        && gate.dataset.acceptedCandidateCount === '1'
                        && gate.dataset.activeTargetKey === {json.dumps(second_target_key)};
                    }}""",
                    timeout=10000,
                )
                for _ in range(max(expected_total_candidate_count, 1)):
                    current_target_key = page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-active-target-key")
                    if current_target_key == confirm_until_active_target_key:
                        break
                    with page.expect_response(
                        lambda response: response.url.endswith(STREAMED_PROPOSAL_PATH)
                        and response.request.method == "POST",
                        timeout=10000,
                    ) as confirm_next_response:
                        page.click("#logic-streamed-confirm")
                    after_second_confirm_session = confirm_next_response.value.json()
                    confirm_next_sessions.append(after_second_confirm_session)
                    next_key = (
                        after_second_confirm_session.get("candidate_queue", {}).get(
                            "active_target_key", ""
                        )
                        if isinstance(
                            after_second_confirm_session.get("candidate_queue"), dict
                        )
                        else ""
                    )
                    if next_key:
                        page.wait_for_function(
                            f"""() => {{
                              const gate = document.querySelector('[data-m21-gate-summary]');
                              return gate && gate.dataset.activeTargetKey === {json.dumps(next_key)};
                            }}""",
                            timeout=10000,
                        )
                if not confirm_next_sessions:
                    raise RuntimeError("streamed queue did not advance after revised candidate confirmation")
                expected_final_accepted_count = 1 + len(confirm_next_sessions)
                expected_final_sequence_index = expected_final_accepted_count + 1
                expected_final_replay_event_count = 1 + expected_final_accepted_count
                expected_final_pending_count = max(
                    expected_total_candidate_count - expected_final_accepted_count,
                    0,
                )
                page.wait_for_function(
                    f"""() => {{
                      const current = document.querySelector('#logic-streamed-current');
                      const gate = document.querySelector('[data-m21-gate-summary]');
                      return current
                        && gate
                        && current.dataset.targetType === 'wire'
                        && current.dataset.targetId === {json.dumps(wire_target_id)}
                        && current.dataset.activeSequenceIndex === {json.dumps(str(expected_final_sequence_index))}
                        && gate.dataset.committedEditCount === {json.dumps(str(expected_final_accepted_count))}
                        && gate.dataset.acceptedCandidateCount === {json.dumps(str(expected_final_accepted_count))}
                        && gate.dataset.activeTargetKey === {json.dumps(wire_target_key)};
                    }}""",
                    timeout=10000,
                )
                history_text = page.locator("#logic-streamed-history").inner_text(timeout=5000)
                page.click("#logic-streamed-panel-toggle")
                page.wait_for_function(
                    """() => {
                      const panel = document.querySelector('#logic-streamed-authoring-panel');
                      const toggle = document.querySelector('#logic-streamed-panel-toggle');
                      return panel
                        && toggle
                        && panel.hidden
                        && panel.dataset.panelVisibility === 'collapsed'
                        && toggle.getAttribute('aria-expanded') === 'false';
                    }""",
                    timeout=10000,
                )
                page.click("#logic-presentation-mode-toggle")
                page.wait_for_function(
                    """() => {
                      const body = document.body;
                      const shell = document.querySelector('.logic-shell');
                      const canvas = document.querySelector('#logic-canvas');
                      const controls = document.querySelector('#logic-presentation-controls');
                      const nav = document.querySelector('.unified-nav');
                      const systemStrip = document.querySelector('#logic-page-system-strip');
                      const bottomRunStrip = document.querySelector('#logic-bottom-run-strip');
                      return body
                        && shell
                        && canvas
                        && controls
                        && nav
                        && systemStrip
                        && bottomRunStrip
                        && body.dataset.logicPresentationMode === 'circuit-only'
                        && shell.dataset.presentationMode === 'circuit-only'
                        && canvas.dataset.presentationMode === 'circuit-only'
                        && !controls.hidden
                        && getComputedStyle(nav).display === 'none'
                        && getComputedStyle(systemStrip).display === 'none'
                        && getComputedStyle(bottomRunStrip).display === 'none';
                    }""",
                    timeout=10000,
                )
                streamed_panel_visibility_for_screenshot = page.locator(
                    "#logic-streamed-authoring-panel"
                ).get_attribute("data-panel-visibility")
                streamed_panel_display_for_screenshot = page.locator(
                    "#logic-streamed-authoring-panel"
                ).evaluate("el => getComputedStyle(el).display")
                reconstruction_panel_display_for_screenshot = page.locator(
                    "#logic-reconstruction-mode-panel"
                ).evaluate("el => getComputedStyle(el).display")
                annotation_submit_bar_display_for_screenshot = page.locator(
                    "#logic-annotation-submit-bar"
                ).evaluate("el => getComputedStyle(el).display")
                body_presentation_mode_for_screenshot = page.locator("body").get_attribute(
                    "data-logic-presentation-mode"
                )
                shell_presentation_mode_for_screenshot = page.locator(
                    ".logic-shell"
                ).get_attribute("data-presentation-mode")
                canvas_presentation_mode_for_screenshot = page.locator(
                    "#logic-canvas"
                ).get_attribute("data-presentation-mode")
                unified_nav_display_for_presentation = page.locator(
                    ".unified-nav"
                ).evaluate("el => getComputedStyle(el).display")
                system_strip_display_for_presentation = page.locator(
                    "#logic-page-system-strip"
                ).evaluate("el => getComputedStyle(el).display")
                inspector_display_for_presentation = page.locator(
                    ".logic-inspector"
                ).evaluate("el => getComputedStyle(el).display")
                mode_dock_display_for_presentation = page.locator(
                    "#logic-mode-dock"
                ).evaluate("el => getComputedStyle(el).display")
                compact_toolbar_display_for_presentation = page.locator(
                    "#logic-canvas-compact-toolbar"
                ).evaluate("el => getComputedStyle(el).display")
                bottom_run_strip_display_for_presentation = page.locator(
                    "#logic-bottom-run-strip"
                ).evaluate("el => getComputedStyle(el).display")
                presentation_controls_display_for_screenshot = page.locator(
                    "#logic-presentation-controls"
                ).evaluate("el => getComputedStyle(el).display")
                presentation_controls_button_count = page.locator(
                    "#logic-presentation-controls button"
                ).count()
                presentation_scale_for_screenshot = page.locator(
                    "#logic-canvas"
                ).get_attribute("data-presentation-scale")
                presentation_offset_x_for_screenshot = page.locator(
                    "#logic-canvas"
                ).get_attribute("data-presentation-offset-x")
                presentation_offset_y_for_screenshot = page.locator(
                    "#logic-canvas"
                ).get_attribute("data-presentation-offset-y")
                page.screenshot(path=str(screenshot_path), full_page=True)
                decision_payload = page.evaluate(
                    """(key) => {
                      const raw = localStorage.getItem(key);
                      return raw ? JSON.parse(raw) : {};
                    }""",
                    STREAMED_AUTHORING_KEY,
                )
                first_decision = (
                    decision_payload.get("decisions", [{}])[0]
                    if isinstance(decision_payload, dict)
                    else {}
                )
                decisions = (
                    decision_payload.get("decisions", [])
                    if isinstance(decision_payload, dict)
                    and isinstance(decision_payload.get("decisions"), list)
                    else []
                )
                observed = {
                    "scenario": fixture["scenario"],
                    "expected_total_candidate_count": expected_total_candidate_count,
                    "expected_final_accepted_count": expected_final_accepted_count,
                    "expected_final_sequence_index": expected_final_sequence_index,
                    "expected_final_replay_event_count": expected_final_replay_event_count,
                    "expected_final_pending_count": expected_final_pending_count,
                    "confirm_until_active_target_key": confirm_until_active_target_key,
                    "confirm_next_session_count": len(confirm_next_sessions),
                    "natural_language_interaction_mode": natural_language_interaction_mode,
                    "natural_language_input_model": natural_language_input_model,
                    "natural_language_visible_button_count": natural_language_visible_button_count,
                    "natural_language_input_visible": natural_language_input_visible,
                    "natural_language_command_trigger_display": natural_language_command_trigger_display,
                    "natural_language_mode_dock_display": natural_language_mode_dock_display,
                    "natural_language_bottom_run_display": natural_language_bottom_run_display,
                    "natural_language_streamed_panel_visibility_after_submit": natural_language_streamed_panel_visibility_after_submit,
                    "natural_language_streamed_launch_source": natural_language_streamed_launch_source,
                    "natural_language_streamed_launch_prompt_present": natural_language_streamed_launch_prompt_present,
                    "natural_language_streamed_step_confirmation": natural_language_streamed_step_confirmation,
                    "natural_language_streamed_current_confirmation": natural_language_streamed_current_confirmation,
                    "natural_language_streamed_source_highlight": natural_language_streamed_source_highlight,
                    "natural_language_streamed_logic_highlight": natural_language_streamed_logic_highlight,
                    "natural_language_streamed_wire_logic_highlight": natural_language_streamed_wire_logic_highlight,
                    "natural_language_streamed_highlight_count": natural_language_streamed_highlight_count,
                    "natural_language_streamed_confirm_enabled": natural_language_streamed_confirm_enabled,
                    "natural_language_streamed_active_target_id": natural_language_streamed_active_target_id,
                    "natural_language_streamed_active_sequence_index": natural_language_streamed_active_sequence_index,
                    "natural_language_streamed_replay_event_count": natural_language_streamed_replay_event_count,
                    "natural_language_canvas_height_after_submit": natural_language_step_visual_framing.get(
                        "canvas_height_after_submit",
                        0,
                    ),
                    "natural_language_active_target_visible_in_canvas": natural_language_step_visual_framing.get(
                        "active_target_visible_in_canvas",
                        False,
                    ),
                    "natural_language_active_target_hit_test_visible": natural_language_step_visual_framing.get(
                        "active_target_hit_test_visible",
                        False,
                    ),
                    "natural_language_step_panel_visible_for_screenshot": natural_language_step_visual_framing.get(
                        "panel_visible_for_step_screenshot",
                        False,
                    ),
                    "natural_language_step_active_visible_for_screenshot": natural_language_step_visual_framing.get(
                        "active_visible_for_step_screenshot",
                        False,
                    ),
                    "natural_language_step_screenshot_clip": natural_language_step_screenshot_clip,
                    "feedback_revision_panel_flow": feedback_revision_panel_flow,
                    "feedback_revision_current_state": feedback_revision_current_state,
                    "feedback_revision_candidate_state": feedback_revision_candidate_state,
                    "feedback_revision_receipt_state": feedback_revision_receipt_state,
                    "feedback_revision_feedback_applied": feedback_revision_feedback_applied,
                    "feedback_revision_status_text": feedback_revision_status_text,
                    "feedback_revision_feedback_text": feedback_revision_feedback_text,
                    "feedback_revision_boundary_text": feedback_revision_boundary_text,
                    "feedback_revision_feedback_matches": feedback_revision_feedback_text == feedback_text,
                    "feedback_revision_confirm_text": feedback_revision_confirm_text,
                    "feedback_revision_revise_text": feedback_revision_revise_text,
                    "feedback_revision_confirm_enabled": feedback_revision_confirm_enabled,
                    "feedback_revision_revise_enabled": feedback_revision_revise_enabled,
                    "feedback_revision_replay_event_count": feedback_revision_replay_event_count,
                    "feedback_revision_active_target_hit_test_visible": feedback_revision_visual_framing.get(
                        "active_target_hit_test_visible",
                        False,
                    ),
                    "feedback_revision_panel_visible_for_screenshot": feedback_revision_visual_framing.get(
                        "panel_visible_for_revision_screenshot",
                        False,
                    ),
                    "feedback_revision_receipt_visible_for_screenshot": feedback_revision_visual_framing.get(
                        "receipt_visible_for_revision_screenshot",
                        False,
                    ),
                    "feedback_revision_active_visible_for_screenshot": feedback_revision_visual_framing.get(
                        "active_visible_for_revision_screenshot",
                        False,
                    ),
                    "feedback_revision_screenshot_clip": feedback_revision_screenshot_clip,
                    "natural_language_start_session": {
                        "status": natural_language_start_session.get("status", ""),
                        "active_target_id": (
                            natural_language_start_session.get("active_proposal", {})
                            .get("target_id", "")
                            if isinstance(
                                natural_language_start_session.get("active_proposal"),
                                dict,
                            )
                            else ""
                        ),
                        "active_sequence_index": (
                            natural_language_start_session.get("candidate_queue", {})
                            .get("active_sequence_index", 0)
                            if isinstance(
                                natural_language_start_session.get("candidate_queue"),
                                dict,
                            )
                            else 0
                        ),
                        "accepted_count": (
                            natural_language_start_session.get("candidate_queue", {})
                            .get("accepted_count", -1)
                            if isinstance(
                                natural_language_start_session.get("candidate_queue"),
                                dict,
                            )
                            else -1
                        ),
                        "replay_event_count": (
                            natural_language_start_session.get("candidate_queue", {})
                            .get("replay_event_count", -1)
                            if isinstance(
                                natural_language_start_session.get("candidate_queue"),
                                dict,
                            )
                            else -1
                        ),
                    },
                    "panel_state": page.locator(
                        "#logic-streamed-authoring-panel"
                    ).get_attribute("data-state"),
                    "streamed_panel_visibility_for_screenshot": streamed_panel_visibility_for_screenshot,
                    "streamed_panel_display_for_screenshot": streamed_panel_display_for_screenshot,
                    "reconstruction_panel_display_for_screenshot": reconstruction_panel_display_for_screenshot,
                    "annotation_submit_bar_display_for_screenshot": annotation_submit_bar_display_for_screenshot,
                    "presentation_mode_for_screenshot": body_presentation_mode_for_screenshot,
                    "shell_presentation_mode_for_screenshot": shell_presentation_mode_for_screenshot,
                    "canvas_presentation_mode_for_screenshot": canvas_presentation_mode_for_screenshot,
                    "unified_nav_display_for_presentation": unified_nav_display_for_presentation,
                    "system_strip_display_for_presentation": system_strip_display_for_presentation,
                    "inspector_display_for_presentation": inspector_display_for_presentation,
                    "mode_dock_display_for_presentation": mode_dock_display_for_presentation,
                    "compact_toolbar_display_for_presentation": compact_toolbar_display_for_presentation,
                    "bottom_run_strip_display_for_presentation": bottom_run_strip_display_for_presentation,
                    "presentation_controls_display_for_screenshot": presentation_controls_display_for_screenshot,
                    "presentation_controls_button_count": presentation_controls_button_count,
                    "presentation_scale_for_screenshot": presentation_scale_for_screenshot,
                    "presentation_offset_x_for_screenshot": presentation_offset_x_for_screenshot,
                    "presentation_offset_y_for_screenshot": presentation_offset_y_for_screenshot,
                    "demo_html_aesthetic_reference": page.locator(
                        "#logic-streamed-authoring-panel"
                    ).get_attribute("data-demo-html-aesthetic-reference"),
                    "demo_canvas_reference": page.locator(
                        ".logic-canvas-wrap"
                    ).get_attribute("data-demo-canvas-reference"),
                    "canvas_visual_contract": page.locator(
                        "#logic-canvas"
                    ).get_attribute("data-canvas-visual-contract"),
                    "canvas_default_display": page.locator(
                        "#logic-canvas"
                    ).get_attribute("data-default-display"),
                    "canvas_background_image": page.locator(
                        "#logic-canvas"
                    ).evaluate("el => getComputedStyle(el).backgroundImage"),
                    "chain_wire_linejoin": page.locator(
                        ".logic-wire"
                    ).first.evaluate("el => getComputedStyle(el).strokeLinejoin"),
                    "chain_wire_linecap": page.locator(
                        ".logic-wire"
                    ).first.evaluate("el => getComputedStyle(el).strokeLinecap"),
                    "chain_wire_marker_end": page.locator(
                        ".logic-wire"
                    ).first.evaluate("el => el.getAttribute('marker-end')"),
                    "chain_wire_count": page.locator(".logic-wire").count(),
                    "chain_wires_with_marker_count": page.locator(
                        ".logic-wire"
                    ).evaluate_all(
                        """elements => elements.filter(
                          element => element.getAttribute('marker-end') === 'url(#logic-demo-chain-arrow-idle)'
                        ).length"""
                    ),
                    "chain_wire_marker_end_values": page.locator(
                        ".logic-wire"
                    ).evaluate_all(
                        """elements => Array.from(new Set(
                          elements.map(element => element.getAttribute('marker-end') || '')
                        )).sort()"""
                    ),
                    "chain_wire_visible_label_count": page.locator(
                        "#logic-svg > text"
                    ).count(),
                    "chain_node_desc_count": page.locator(
                        ".logic-node .logic-node-desc"
                    ).count(),
                    "chain_node_code_count": page.locator(
                        ".logic-node code"
                    ).count(),
                    "chain_node_anchor_count": page.locator(
                        ".logic-node .logic-node-anchor"
                    ).count(),
                    "chain_arrow_marker_count": page.locator(
                        "#logic-svg marker#logic-demo-chain-arrow-idle"
                    ).count(),
                    "chain_endpoint_dot_count": page.locator(
                        "#logic-svg .logic-endpoint-dot"
                    ).count(),
                    "chain_unclassified_circle_count": page.locator(
                        "#logic-svg > circle:not(.logic-junction)"
                    ).count(),
                    "chain_junction_count": page.locator(
                        "#logic-svg .logic-junction"
                    ).count(),
                    "chain_node_font_family": page.locator(
                        ".logic-node"
                    ).first.evaluate("el => getComputedStyle(el).fontFamily"),
                    "requirements_document_edit_status": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-requirements-document-edit-status"),
                    "committed_candidate_graph_status": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-committed-candidate-graph-status"),
                    "committed_edit_count": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-committed-edit-count"),
                    "candidate_queue_status": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-candidate-queue-status"),
                    "active_target_key": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-active-target-key"),
                    "accepted_candidate_count": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-accepted-candidate-count"),
                    "pending_candidate_count": page.locator(
                        "[data-m21-gate-summary]"
                    ).get_attribute("data-pending-candidate-count"),
                    "active_sequence_index": page.locator(
                        "#logic-streamed-current"
                    ).get_attribute("data-active-sequence-index"),
                    "active_target_type": page.locator(
                        "#logic-streamed-current"
                    ).get_attribute("data-target-type"),
                    "active_target_id": page.locator(
                        "#logic-streamed-current"
                    ).get_attribute("data-target-id"),
                    "active_proposal_status": page.locator(
                        "#logic-streamed-current"
                    ).get_attribute("data-proposal-status"),
                    "replay_event_count": page.locator(
                        "#logic-streamed-history [data-stream-replay-event]"
                    ).count(),
                    "committed_replay_event_count": page.locator(
                        '#logic-streamed-history [data-stream-replay-event="candidate_edit_committed"]'
                    ).count(),
                    "revision_replay_event_count": page.locator(
                        '#logic-streamed-history [data-stream-replay-event="candidate_edit_revision_requested"]'
                    ).count(),
                    "active_highlight_count": page.locator(
                        ".is-streamed-authoring-active"
                    ).count(),
                    "history_text": history_text,
                    "local_storage_decision_count": len(decisions),
                    "local_storage_decision": {
                        "decision": first_decision.get("decision", ""),
                        "requirements_document_edit_requested": first_decision.get(
                            "requirements_document_edit_requested"
                        ),
                        "requirements_document_edit_authorized": first_decision.get(
                            "requirements_document_edit_authorized"
                        ),
                        "source_requirements_sha256_present": bool(
                            first_decision.get("source_requirements_sha256")
                        ),
                        "source_drawing_sha256_present": bool(
                            first_decision.get("source_drawing_sha256")
                        ),
                        "truth_effect": first_decision.get("truth_effect", ""),
                        "controller_truth_modified": first_decision.get(
                            "controller_truth_modified"
                        ),
                    },
                }
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    restricted_after = _restricted_diff()
    control_truth_diff_after = _restricted_diff(CONTROL_TRUTH_PATHS)
    requirements_document_diff_after = _restricted_diff(REQUIREMENTS_DOCUMENT_PATHS)
    server_session = after_second_confirm_session
    revision_active_proposal = (
        revision_session.get("active_proposal")
        if isinstance(revision_session.get("active_proposal"), dict)
        else {}
    )
    revision_stream_replay = (
        revision_session.get("stream_replay")
        if isinstance(revision_session.get("stream_replay"), list)
        else []
    )
    revision_replay_event = (
        revision_stream_replay[0]
        if revision_stream_replay and isinstance(revision_stream_replay[0], dict)
        else {}
    )
    revision_requirements_document_edit = (
        revision_session.get("requirements_document_edit")
        if isinstance(revision_session.get("requirements_document_edit"), dict)
        else {}
    )
    revision_feedback_applied = (
        revision_active_proposal.get("feedback_applied")
        if isinstance(revision_active_proposal.get("feedback_applied"), dict)
        else {}
    )
    revision_candidate_recalculation = (
        revision_replay_event.get("candidate_recalculation")
        if isinstance(revision_replay_event.get("candidate_recalculation"), dict)
        else {}
    )
    after_revised_queue = (
        after_revised_confirm_session.get("candidate_queue")
        if isinstance(after_revised_confirm_session.get("candidate_queue"), dict)
        else {}
    )
    after_revised_replay = (
        after_revised_confirm_session.get("stream_replay")
        if isinstance(after_revised_confirm_session.get("stream_replay"), list)
        else []
    )
    after_revised_committed_graph = (
        after_revised_confirm_session.get("committed_candidate_graph")
        if isinstance(after_revised_confirm_session.get("committed_candidate_graph"), dict)
        else {}
    )
    active_proposal = (
        server_session.get("active_proposal")
        if isinstance(server_session.get("active_proposal"), dict)
        else {}
    )
    candidate_queue = (
        server_session.get("candidate_queue")
        if isinstance(server_session.get("candidate_queue"), dict)
        else {}
    )
    stream_replay = (
        server_session.get("stream_replay")
        if isinstance(server_session.get("stream_replay"), list)
        else []
    )
    replay_event = stream_replay[0] if stream_replay and isinstance(stream_replay[0], dict) else {}
    requirements_document_edit = (
        server_session.get("requirements_document_edit")
        if isinstance(server_session.get("requirements_document_edit"), dict)
        else {}
    )
    feedback_applied = (
        active_proposal.get("feedback_applied")
        if isinstance(active_proposal.get("feedback_applied"), dict)
        else {}
    )
    candidate_recalculation = (
        replay_event.get("candidate_recalculation")
        if isinstance(replay_event.get("candidate_recalculation"), dict)
        else {}
    )
    committed_revision_event = (
        after_revised_replay[1]
        if len(after_revised_replay) > 1 and isinstance(after_revised_replay[1], dict)
        else {}
    )
    confirmed_revision_pairs = (
        after_revised_committed_graph.get("confirmed_revision_pairs")
        if isinstance(after_revised_committed_graph.get("confirmed_revision_pairs"), list)
        else []
    )
    observed["revision_server_session"] = {
        "status": revision_session.get("status", ""),
        "truth_effect": revision_session.get("truth_effect", ""),
        "controller_truth_modified": revision_session.get("controller_truth_modified"),
        "requirements_document_edit_status": revision_requirements_document_edit.get("status", ""),
        "requirements_document_modified": revision_requirements_document_edit.get(
            "requirements_document_modified"
        ),
        "automatic_document_mutation": revision_requirements_document_edit.get(
            "automatic_document_mutation"
        ),
        "pending_candidate_patch_sha256_present": bool(
            revision_requirements_document_edit.get("pending_candidate_patch_sha256")
        ),
        "replay_event_type": revision_replay_event.get("event_type", ""),
        "replay_requirements_patch_status": revision_replay_event.get(
            "requirements_document_patch_status", ""
        ),
        "replay_requirements_patch_sha256_present": bool(
            revision_replay_event.get("requirements_document_patch_sha256")
        ),
        "replay_candidate_recalculation_status": revision_candidate_recalculation.get("status", ""),
        "active_proposal_status": revision_active_proposal.get("proposal_status", ""),
        "active_target_id": revision_active_proposal.get("target_id", ""),
        "source_anchor_ids": revision_active_proposal.get("source_anchor_ids", []),
        "active_proposal_revision_of_present": bool(
            revision_active_proposal.get("revision_of")
        ),
        "active_proposal_revision_gate_status": (
            revision_active_proposal.get("revision_gate", {}).get("status", "")
            if isinstance(revision_active_proposal.get("revision_gate"), dict)
            else ""
        ),
        "feedback_sha256_present": bool(revision_feedback_applied.get("feedback_sha256")),
        "feedback_text_matches": revision_feedback_applied.get("feedback_text") == feedback_text,
    }
    observed["after_revised_confirm_server_session"] = {
        "status": after_revised_confirm_session.get("status", ""),
        "active_target_key": after_revised_queue.get("active_target_key", ""),
        "active_sequence_index": after_revised_queue.get("active_sequence_index", 0),
        "active_target_id": (
            after_revised_confirm_session.get("active_proposal", {}).get("target_id", "")
            if isinstance(after_revised_confirm_session.get("active_proposal"), dict)
            else ""
        ),
        "accepted_count": after_revised_queue.get("accepted_count", 0),
        "pending_count": after_revised_queue.get("pending_count", 0),
        "replay_event_count": after_revised_queue.get("replay_event_count", 0),
        "can_continue_after_revision": after_revised_queue.get(
            "can_continue_after_revision"
        ),
        "confirmed_revision_pair_count": len(confirmed_revision_pairs),
        "committed_event_proposal_id": committed_revision_event.get("proposal_id", ""),
        "committed_event_commits_revision": committed_revision_event.get(
            "commits_revision"
        ),
        "committed_event_confirmed_revision_of": committed_revision_event.get(
            "confirmed_revision_of", ""
        ),
    }
    observed["server_session"] = {
        "status": server_session.get("status", ""),
        "truth_effect": server_session.get("truth_effect", ""),
        "controller_truth_modified": server_session.get("controller_truth_modified"),
        "requirements_document_edit_status": requirements_document_edit.get("status", ""),
        "requirements_document_modified": requirements_document_edit.get(
            "requirements_document_modified"
        ),
        "automatic_document_mutation": requirements_document_edit.get(
            "automatic_document_mutation"
        ),
        "pending_candidate_patch_sha256_present": bool(
            requirements_document_edit.get("pending_candidate_patch_sha256")
        ),
        "replay_event_type": replay_event.get("event_type", ""),
        "replay_requirements_patch_status": replay_event.get(
            "requirements_document_patch_status", ""
        ),
        "replay_requirements_patch_sha256_present": bool(
            replay_event.get("requirements_document_patch_sha256")
        ),
        "replay_candidate_recalculation_status": candidate_recalculation.get("status", ""),
        "active_proposal_status": active_proposal.get("proposal_status", ""),
        "active_target_id": active_proposal.get("target_id", ""),
        "source_anchor_ids": active_proposal.get("source_anchor_ids", []),
        "active_proposal_revision_of_present": bool(active_proposal.get("revision_of")),
        "active_proposal_revision_gate_status": (
            active_proposal.get("revision_gate", {}).get("status", "")
            if isinstance(active_proposal.get("revision_gate"), dict)
            else ""
        ),
        "feedback_sha256_present": bool(feedback_applied.get("feedback_sha256")),
        "feedback_text_matches": feedback_applied.get("feedback_text") == feedback_text,
        "source_requirements_sha256_present": bool(
            server_session.get("source_requirements_sha256")
        ),
        "source_drawing_sha256_present": bool(server_session.get("source_drawing_sha256")),
        "candidate_queue_status": candidate_queue.get("status", ""),
        "candidate_queue_active_target_key": candidate_queue.get("active_target_key", ""),
        "candidate_queue_active_sequence_index": candidate_queue.get(
            "active_sequence_index", 0
        ),
        "candidate_queue_accepted_count": candidate_queue.get("accepted_count", 0),
        "candidate_queue_pending_count": candidate_queue.get("pending_count", 0),
        "candidate_queue_replay_event_count": candidate_queue.get("replay_event_count", 0),
    }
    observed["file_boundary"] = {
        "restricted_diff_before": restricted_before,
        "restricted_diff_after": restricted_after,
        "control_truth_diff_after": control_truth_diff_after,
        "requirements_document_diff_after": requirements_document_diff_after,
        "watched_control_truth_paths": CONTROL_TRUTH_PATHS,
        "watched_requirements_document_paths": REQUIREMENTS_DOCUMENT_PATHS,
    }
    requirements_preparse = (
        fixture["requirements_payload"].get("deterministic_preparse")
        if isinstance(fixture["requirements_payload"].get("deterministic_preparse"), dict)
        else {}
    )
    requirement_node_ids = [
        _str(item.get("id"))
        for item in fixture["requirements_payload"].get("concept_logic_nodes", [])
        if isinstance(item, dict)
    ]
    requirement_edge_labels = [
        _str(item.get("label"))
        for item in fixture["requirements_payload"].get("concept_edges", [])
        if isinstance(item, dict)
    ]
    requirement_edge_ids = [
        _str(item.get("id"))
        for item in fixture["requirements_payload"].get("concept_edges", [])
        if isinstance(item, dict)
    ]
    drawing_node_ids = [
        _str(item.get("id"))
        for item in fixture["drawing_payload"].get("nodes", [])
        if isinstance(item, dict)
    ]
    drawing_edge_labels = [
        _str(item.get("label"))
        for item in fixture["drawing_payload"].get("edges", [])
        if isinstance(item, dict)
    ]
    expected_chain_junction_count = _expected_fanout_junction_count(
        fixture["drawing_payload"]
    )
    observed["expected_chain_junction_count"] = expected_chain_junction_count
    observed["requires_fanout_junction"] = bool(fixture.get("requires_fanout_junction"))
    source_scope_anchors = [
        anchor
        for scope in fixture["requirements_payload"].get("source_scope", {}).values()
        if isinstance(scope, dict)
        for anchor in scope.get("source_anchors", [])
        if isinstance(anchor, dict)
    ]
    requirement_anchor_quotes = [
        _str(anchor.get("quote_zh") or anchor.get("quote"))
        for item in [
            *fixture["requirements_payload"].get("concept_logic_nodes", []),
            *fixture["requirements_payload"].get("concept_edges", []),
            {"source_anchors": source_scope_anchors},
        ]
        if isinstance(item, dict)
        for anchor in item.get("source_anchors", [])
        if isinstance(anchor, dict)
    ]
    requirement_anchor_ids = [
        _str(anchor.get("id"))
        for item in [
            *fixture["requirements_payload"].get("concept_logic_nodes", []),
            *fixture["requirements_payload"].get("concept_edges", []),
            {"source_anchors": source_scope_anchors},
        ]
        if isinstance(item, dict)
        for anchor in item.get("source_anchors", [])
        if isinstance(anchor, dict)
    ]
    requirement_anchor_origins = [
        _str(anchor.get("origin"))
        for item in [
            *fixture["requirements_payload"].get("concept_logic_nodes", []),
            *fixture["requirements_payload"].get("concept_edges", []),
            {"source_anchors": source_scope_anchors},
        ]
        if isinstance(item, dict)
        for anchor in item.get("source_anchors", [])
        if isinstance(anchor, dict)
    ]
    raw_intake_expectation = (
        fixture.get("raw_intake") if isinstance(fixture.get("raw_intake"), dict) else {}
    )
    observed["raw_intake"] = {
        "scenario_uses_raw_intake": bool(raw_intake_expectation),
        "endpoint_path": raw_intake_endpoint.get("endpoint_path", ""),
        "endpoint_http_status": raw_intake_endpoint.get("http_status", 0),
        "endpoint_payload_kind": raw_intake_endpoint.get("payload_kind", ""),
        "raw_preparse_payload_artifact": raw_intake_endpoint.get("raw_preparse_payload_artifact", ""),
        "raw_preparse_payload_artifact_exists": bool(
            raw_intake_endpoint.get("raw_preparse_payload_artifact")
            and Path(raw_intake_endpoint.get("raw_preparse_payload_artifact", "")).exists()
        ),
        "raw_preparse_payload_sha256": raw_intake_endpoint.get("raw_preparse_payload_sha256", ""),
        "document_path": raw_intake_expectation.get("document_path", ""),
        "source_document_name": fixture["requirements_payload"].get("source_document", {}).get("name", ""),
        "source_document_sha256_present": bool(
            fixture["requirements_payload"].get("source_document", {}).get("sha256")
        ),
        "requirements_status": fixture["requirements_payload"].get("status", ""),
        "ready_for_logic_builder": fixture["requirements_payload"].get("ready_for_logic_builder"),
        "deterministic_preparse_applied": requirements_preparse.get("applied"),
        "deterministic_preparse_strategy": requirements_preparse.get("strategy", ""),
        "requirement_node_ids": requirement_node_ids,
        "requirement_edge_ids": requirement_edge_ids,
        "requirement_edge_labels": requirement_edge_labels,
        "drawing_derived_from": fixture["drawing_payload"].get("derived_from", ""),
        "drawing_source_requirements_sha256": fixture["drawing_payload"].get("source_requirements_sha256", ""),
        "drawing_node_ids": drawing_node_ids,
        "drawing_edge_labels": drawing_edge_labels,
        "requirement_anchor_ids": requirement_anchor_ids,
        "requirement_anchor_origins": requirement_anchor_origins,
        "requirement_anchor_quotes": requirement_anchor_quotes,
        "source_scope_status": (
            fixture["requirements_payload"]
            .get("source_scope", {})
            .get("c919_etras", {})
            .get("status", "")
        ),
        "truth_effect": fixture["requirements_payload"].get("truth_effect", ""),
        "controller_truth_modified": fixture["requirements_payload"].get("controller_truth_modified"),
    }
    gates = {
        "browser_boot": _gate_status(not console_errors),
        "screenshot": _gate_status(
            screenshot_path.exists() and screenshot_path.stat().st_size > 0
        ),
        "demo_html_aesthetic_reference": _gate_status(
            observed["demo_html_aesthetic_reference"]
            == "src/well_harness/static/demo.html#fan-chain-svg"
        ),
        "demo_html_canvas_contract": _gate_status(
            observed["demo_canvas_reference"]
            == "src/well_harness/static/demo.html#fan-chain-svg"
            and observed["canvas_visual_contract"] == "demo-html-chain-svg"
            and observed["canvas_default_display"] == "logic-circuit-only"
            and observed["canvas_background_image"] == "none"
            and observed["chain_wire_linejoin"] == "miter"
            and observed["chain_wire_linecap"] == "butt"
            and observed["chain_wire_marker_end"] == "url(#logic-demo-chain-arrow-idle)"
            and observed["chain_wire_count"] > 0
            and observed["chain_wires_with_marker_count"] == observed["chain_wire_count"]
            and observed["chain_arrow_marker_count"] == 1
            and observed["chain_endpoint_dot_count"] == 0
            and observed["chain_unclassified_circle_count"] == 0
            and observed["chain_wire_visible_label_count"] == 0
            and observed["chain_node_desc_count"] == 0
            and observed["chain_node_code_count"] == 0
            and observed["chain_node_anchor_count"] == 0
            and observed["chain_junction_count"] == expected_chain_junction_count
            and "Courier" in observed["chain_node_font_family"]
        ),
        "circuit_only_default_display_contract": _gate_status(
            observed["canvas_default_display"] == "logic-circuit-only"
            and observed["chain_wire_visible_label_count"] == 0
            and observed["chain_node_desc_count"] == 0
            and observed["chain_node_code_count"] == 0
            and observed["chain_node_anchor_count"] == 0
        ),
        "natural_language_workbench_contract": _gate_status(
            observed["natural_language_interaction_mode"] == "natural-language"
            and observed["natural_language_input_model"] == "natural-language"
            and observed["natural_language_input_visible"] is True
            and observed["natural_language_visible_button_count"] <= 3
            and observed["natural_language_command_trigger_display"] == "none"
            and observed["natural_language_mode_dock_display"] == "none"
            and observed["natural_language_bottom_run_display"] == "none"
        ),
        "natural_language_streamed_confirmation_contract": _gate_status(
            observed["natural_language_streamed_panel_visibility_after_submit"] == "expanded"
            and observed["natural_language_streamed_launch_source"] == "natural-language"
            and observed["natural_language_streamed_launch_prompt_present"] == "true"
            and observed["natural_language_streamed_step_confirmation"] == "awaiting-engineer"
            and observed["natural_language_streamed_current_confirmation"]
            == "candidate-awaiting-engineer-confirmation"
            and observed["natural_language_streamed_source_highlight"] == "active"
            and observed["natural_language_streamed_logic_highlight"] == "active"
            and observed["natural_language_streamed_wire_logic_highlight"] == "active"
            and observed["natural_language_streamed_highlight_count"] > 0
            and observed["natural_language_streamed_confirm_enabled"] is True
            and observed["natural_language_streamed_active_target_id"] == first_target_id
        ),
        "one_candidate_per_natural_language_submit_contract": _gate_status(
            observed["natural_language_streamed_active_sequence_index"] == "1"
            and observed["natural_language_streamed_replay_event_count"] == 0
            and observed["natural_language_start_session"]["status"]
            == "awaiting_user_confirmation"
            and observed["natural_language_start_session"]["active_target_id"]
            == first_target_id
            and observed["natural_language_start_session"]["active_sequence_index"] == 1
            and observed["natural_language_start_session"]["accepted_count"] == 0
            and observed["natural_language_start_session"]["replay_event_count"] == 0
        ),
        "natural_language_step_visual_framing_contract": _gate_status(
            int(observed["natural_language_canvas_height_after_submit"] or 0) >= 420
            and observed["natural_language_active_target_visible_in_canvas"] is True
            and observed["natural_language_active_target_hit_test_visible"] is True
            and observed["natural_language_step_panel_visible_for_screenshot"] is True
            and observed["natural_language_step_active_visible_for_screenshot"] is True
            and int(
                observed["natural_language_step_screenshot_clip"].get("width", 0)
                if isinstance(observed["natural_language_step_screenshot_clip"], dict)
                else 0
            )
            >= 960
            and 240
            <= int(
                observed["natural_language_step_screenshot_clip"].get("height", 0)
                if isinstance(observed["natural_language_step_screenshot_clip"], dict)
                else 0
            )
            <= 620
        ),
        "natural_language_step_confirmation_screenshot": _gate_status(
            step_confirmation_screenshot_path.exists()
            and step_confirmation_screenshot_path.stat().st_size > 0
        ),
        "feedback_revision_frontstage_contract": _gate_status(
            observed["feedback_revision_panel_flow"] == "candidate-recomputed"
            and observed["feedback_revision_current_state"] == "candidate-recomputed"
            and observed["feedback_revision_candidate_state"] == "ready"
            and observed["feedback_revision_receipt_state"] == "candidate-recomputed"
            and observed["feedback_revision_feedback_applied"] == "true"
            and observed["feedback_revision_feedback_matches"] is True
            and observed["feedback_revision_confirm_text"] == "确认修订候选"
            and observed["feedback_revision_revise_text"] == "继续修改候选"
            and observed["feedback_revision_confirm_enabled"] is True
            and observed["feedback_revision_revise_enabled"] is True
            and observed["feedback_revision_replay_event_count"] == 1
            and observed["feedback_revision_active_target_hit_test_visible"] is True
            and "candidate graph only" in observed["feedback_revision_boundary_text"]
        ),
        "feedback_revision_confirmation_screenshot": _gate_status(
            revision_confirmation_screenshot_path.exists()
            and revision_confirmation_screenshot_path.stat().st_size > 0
            and observed["feedback_revision_panel_visible_for_screenshot"] is True
            and observed["feedback_revision_receipt_visible_for_screenshot"] is True
            and observed["feedback_revision_active_visible_for_screenshot"] is True
            and int(
                observed["feedback_revision_screenshot_clip"].get("width", 0)
                if isinstance(observed["feedback_revision_screenshot_clip"], dict)
                else 0
            )
            >= 960
            and 240
            <= int(
                observed["feedback_revision_screenshot_clip"].get("height", 0)
                if isinstance(observed["feedback_revision_screenshot_clip"], dict)
                else 0
            )
            <= 620
        ),
        "streamed_panel_collapsed_for_screenshot_contract": _gate_status(
            observed["streamed_panel_visibility_for_screenshot"] == "collapsed"
            and observed["streamed_panel_display_for_screenshot"] == "none"
            and observed["reconstruction_panel_display_for_screenshot"] == "none"
            and observed["annotation_submit_bar_display_for_screenshot"] == "none"
        ),
        "pure_canvas_presentation_contract": _gate_status(
            observed["presentation_mode_for_screenshot"] == "circuit-only"
            and observed["shell_presentation_mode_for_screenshot"] == "circuit-only"
            and observed["canvas_presentation_mode_for_screenshot"] == "circuit-only"
            and observed["unified_nav_display_for_presentation"] == "none"
            and observed["system_strip_display_for_presentation"] == "none"
            and observed["inspector_display_for_presentation"] == "none"
            and observed["mode_dock_display_for_presentation"] == "none"
            and observed["compact_toolbar_display_for_presentation"] == "none"
            and observed["bottom_run_strip_display_for_presentation"] == "none"
            and observed["presentation_controls_display_for_screenshot"] == "flex"
            and observed["presentation_controls_button_count"] == 4
        ),
        "pure_canvas_framing_contract": _gate_status(
            float(observed["presentation_scale_for_screenshot"] or 0) > 0
            and (
                abs(int(observed["presentation_offset_x_for_screenshot"] or 0))
                + abs(int(observed["presentation_offset_y_for_screenshot"] or 0))
            )
            > 0
        ),
        "all_wires_marker_contract": _gate_status(
            observed["chain_wire_count"] > 0
            and observed["chain_wires_with_marker_count"] == observed["chain_wire_count"]
            and observed["chain_wire_marker_end_values"]
            == ["url(#logic-demo-chain-arrow-idle)"]
        ),
        "fanout_junction_contract": _gate_status(
            not fixture.get("requires_fanout_junction")
            or (
                expected_chain_junction_count
                == int(fixture.get("expected_fanout_junction_count") or 0)
                and expected_chain_junction_count > 0
                and observed["chain_junction_count"] == expected_chain_junction_count
                and observed["chain_endpoint_dot_count"] == 0
                and observed["chain_unclassified_circle_count"] == 0
                and observed["chain_wires_with_marker_count"] == observed["chain_wire_count"]
            )
        ),
        "scenario_fixture": _gate_status(
            observed["scenario"] == fixture["scenario"]
            and observed["revision_server_session"]["active_target_id"] == first_target_id
            and fixture["source_anchor_id"]
            in observed["revision_server_session"]["source_anchor_ids"]
        ),
        "raw_intake_payload": _gate_status(
            not raw_intake_expectation
            or (
                observed["raw_intake"]["source_document_name"]
                == raw_intake_expectation.get("expected_source_document_name")
                and observed["raw_intake"]["endpoint_path"]
                == "/api/requirements-intake/local-preparse"
                and observed["raw_intake"]["endpoint_http_status"] == 200
                and observed["raw_intake"]["endpoint_payload_kind"]
                == "ai-fantui-requirements-intake-analysis"
                and observed["raw_intake"]["raw_preparse_payload_artifact_exists"] is True
                and bool(observed["raw_intake"]["raw_preparse_payload_sha256"])
                and observed["raw_intake"]["requirements_status"] == "ready_for_logic_builder"
                and observed["raw_intake"]["ready_for_logic_builder"] is True
                and observed["raw_intake"]["deterministic_preparse_applied"] is True
                and observed["raw_intake"]["deterministic_preparse_strategy"]
                == raw_intake_expectation.get("expected_strategy")
                and all(
                    node_id in observed["raw_intake"]["requirement_node_ids"]
                    for node_id in raw_intake_expectation.get("required_node_ids", [])
                )
                and not any(
                    node_id in observed["raw_intake"]["requirement_node_ids"]
                    for node_id in raw_intake_expectation.get("forbidden_node_ids", [])
                )
                and all(
                    edge_label in observed["raw_intake"]["requirement_edge_labels"]
                    for edge_label in raw_intake_expectation.get("required_edge_labels", [])
                )
                and not any(
                    edge_label in observed["raw_intake"]["requirement_edge_labels"]
                    for edge_label in raw_intake_expectation.get("forbidden_edge_labels", [])
                )
                and all(
                    edge_id in observed["raw_intake"]["requirement_edge_ids"]
                    for edge_id in raw_intake_expectation.get("required_edge_ids", [])
                )
                and (
                    not fixture.get("drawing_from_raw_preparse")
                    or (
                        observed["raw_intake"]["drawing_derived_from"]
                        == "raw_preparse_payload"
                        and observed["raw_intake"]["drawing_source_requirements_sha256"]
                        == observed["raw_intake"]["raw_preparse_payload_sha256"]
                        and all(
                            node_id in observed["raw_intake"]["drawing_node_ids"]
                            for node_id in raw_intake_expectation.get("required_node_ids", [])
                        )
                        and all(
                            edge_label in observed["raw_intake"]["drawing_edge_labels"]
                            for edge_label in raw_intake_expectation.get("required_edge_labels", [])
                        )
                    )
                )
                and (
                    not raw_intake_expectation.get("required_anchor_text")
                    or any(
                        raw_intake_expectation["required_anchor_text"] in quote
                        for quote in observed["raw_intake"]["requirement_anchor_quotes"]
                    )
                )
                and all(
                    any(anchor_text in quote for quote in observed["raw_intake"]["requirement_anchor_quotes"])
                    for anchor_text in raw_intake_expectation.get("required_anchor_texts", [])
                )
                and all(
                    anchor_id in observed["raw_intake"]["requirement_anchor_ids"]
                    for anchor_id in raw_intake_expectation.get("required_anchor_ids", [])
                )
                and (
                    not raw_intake_expectation.get("required_anchor_ids")
                    or all(
                        origin == "c919_etras_doc"
                        for origin in observed["raw_intake"]["requirement_anchor_origins"]
                        if origin
                    )
                )
                and (
                    not raw_intake_expectation.get("forbidden_anchor_text")
                    or not any(
                        raw_intake_expectation["forbidden_anchor_text"] in quote
                        for quote in observed["raw_intake"]["requirement_anchor_quotes"]
                    )
                )
                and observed["raw_intake"]["source_scope_status"] == "candidate_only"
                and observed["raw_intake"]["truth_effect"] == "none"
                and observed["raw_intake"]["controller_truth_modified"] is False
            )
        ),
        "revision_replay": _gate_status(
            observed["revision_replay_event_count"] == 1
            and "已反馈重算" in observed["history_text"]
            and "revision_candidate_ready" in observed["history_text"]
        ),
        "server_revision_candidate": _gate_status(
            observed["revision_server_session"]["status"] == "awaiting_user_confirmation"
            and observed["revision_server_session"]["replay_event_type"]
            == "candidate_edit_revision_requested"
            and observed["revision_server_session"]["replay_candidate_recalculation_status"]
            == "revision_candidate_ready"
            and observed["revision_server_session"]["active_proposal_status"]
            == "revised_proposal_ready"
            and observed["revision_server_session"]["active_proposal_revision_of_present"]
            and observed["revision_server_session"]["active_proposal_revision_gate_status"]
            == "revision_candidate_ready"
            and observed["revision_server_session"]["feedback_sha256_present"]
            and observed["revision_server_session"]["feedback_text_matches"]
        ),
        "requirements_patch_authorized": _gate_status(
            observed["requirements_document_edit_status"] == "authorized_candidate_patch"
            and "需求文档候选补丁已授权" in observed["history_text"]
        ),
        "server_requirements_patch_authorized": _gate_status(
            observed["revision_server_session"]["requirements_document_edit_status"]
            == "authorized_candidate_patch"
            and observed["revision_server_session"]["replay_requirements_patch_status"]
            == "authorized_candidate_patch"
            and observed["revision_server_session"]["pending_candidate_patch_sha256_present"]
            and observed["revision_server_session"]["replay_requirements_patch_sha256_present"]
            and observed["revision_server_session"]["requirements_document_modified"] is False
            and observed["revision_server_session"]["automatic_document_mutation"] is False
        ),
        "revised_candidate_confirmed": _gate_status(
            observed["after_revised_confirm_server_session"]["active_target_key"] == second_target_key
            and observed["after_revised_confirm_server_session"]["active_sequence_index"] == 2
            and observed["after_revised_confirm_server_session"]["active_target_id"] == second_target_id
            and observed["after_revised_confirm_server_session"]["accepted_count"] == 1
            and observed["after_revised_confirm_server_session"]["pending_count"]
            == max(observed["expected_total_candidate_count"] - 1, 0)
            and observed["after_revised_confirm_server_session"]["replay_event_count"] == 2
            and observed["after_revised_confirm_server_session"]["can_continue_after_revision"] is True
            and observed["after_revised_confirm_server_session"]["confirmed_revision_pair_count"] == 1
            and observed["after_revised_confirm_server_session"]["committed_event_commits_revision"] is True
            and bool(
                observed["after_revised_confirm_server_session"][
                    "committed_event_confirmed_revision_of"
                ]
            )
            and observed["after_revised_confirm_server_session"]["committed_event_proposal_id"]
            != observed["after_revised_confirm_server_session"][
                "committed_event_confirmed_revision_of"
            ]
        ),
        "multi_step_queue_advance": _gate_status(
            observed["replay_event_count"] == observed["expected_final_replay_event_count"]
            and observed["committed_replay_event_count"]
            == observed["expected_final_accepted_count"]
            and observed["committed_edit_count"]
            == str(observed["expected_final_accepted_count"])
            and observed["accepted_candidate_count"]
            == str(observed["expected_final_accepted_count"])
            and observed["pending_candidate_count"]
            == str(observed["expected_final_pending_count"])
            and observed["candidate_queue_status"] == "candidate_queue_active"
            and observed["active_sequence_index"]
            == str(observed["expected_final_sequence_index"])
            and observed["active_target_type"] == "wire"
            and observed["active_target_id"] == wire_target_id
            and observed["active_target_key"] == wire_target_key
            and observed["server_session"]["candidate_queue_active_target_key"] == wire_target_key
            and observed["server_session"]["candidate_queue_active_sequence_index"]
            == observed["expected_final_sequence_index"]
            and observed["server_session"]["candidate_queue_accepted_count"]
            == observed["expected_final_accepted_count"]
            and observed["server_session"]["candidate_queue_pending_count"]
            == observed["expected_final_pending_count"]
            and observed["server_session"]["candidate_queue_replay_event_count"]
            == observed["expected_final_replay_event_count"]
            and observed["server_session"]["active_target_id"] == wire_target_id
            and observed["local_storage_decision_count"]
            == observed["expected_final_replay_event_count"]
        ),
        "candidate_boundary": _gate_status(
            not restricted_before
            and not restricted_after
            and not control_truth_diff_after
            and not requirements_document_diff_after
            and observed["server_session"]["truth_effect"] == "none"
            and observed["server_session"]["controller_truth_modified"] is False
            and observed["server_session"]["requirements_document_modified"] is False
            and observed["local_storage_decision"]["truth_effect"] == "none"
            and observed["local_storage_decision"]["controller_truth_modified"] is False
        ),
        "source_hash_binding": _gate_status(
            observed["server_session"]["source_requirements_sha256_present"]
            and observed["server_session"]["source_drawing_sha256_present"]
            and
            observed["local_storage_decision"]["source_requirements_sha256_present"]
            and observed["local_storage_decision"]["source_drawing_sha256_present"]
        ),
        "active_highlight": _gate_status(observed["active_highlight_count"] >= 1),
        "local_gate": "fail",
    }
    status = "pass" if all(value == "pass" for key, value in gates.items() if key != "local_gate") else "fail"
    gates["local_gate"] = status
    payload = {
        "kind": "ai-fantui-m21-streamed-authoring-revision-and-queue-browser-gate",
        "scenario": fixture["scenario"],
        "status": status,
        "artifact_paths": {
            "summary": str(summary_path),
            "screenshot": str(screenshot_path),
            "step_confirmation_screenshot": str(step_confirmation_screenshot_path),
            "revision_confirmation_screenshot": str(revision_confirmation_screenshot_path),
            "raw_preparse_payload": raw_intake_endpoint.get("raw_preparse_payload_artifact", ""),
        },
        "console_errors": console_errors,
        "deterministic_gates": gates,
        "observed": observed,
        "restricted_diff": restricted_after,
        "restricted_diff_before": restricted_before,
        "control_truth_diff_after": control_truth_diff_after,
        "requirements_document_diff_after": requirements_document_diff_after,
        "truth_effect": "none",
        "controller_truth_modified": False,
        "requirements_document_modified": bool(requirements_document_diff_after),
        "recommended_next_step": (
            "Use this gate as M21 evidence for feedback recalculation, "
            "requirements-document candidate patch authorization, and "
            "multi-step candidate queue advance."
        ),
    }
    _write_json(summary_path, payload)
    return payload


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify M21 streamed revision authoring and queue advance in a browser.",
    )
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--scenario", choices=SCENARIOS, default="fantui")
    return parser.parse_args(argv)


def _emit(payload: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload["status"] == "pass":
        print("PASS: M21 streamed revision and queue browser gate verified")
        print(f"screenshot: {payload['artifact_paths']['screenshot']}")
    else:
        print("FAIL: M21 streamed revision browser gate failed")
        print(json.dumps(payload["deterministic_gates"], ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    payload = verify_m21_revision_browser_gate(args.artifact_dir, scenario=args.scenario)
    _emit(payload, args.format)
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
