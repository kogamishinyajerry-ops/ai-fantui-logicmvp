"""DeepSeek V4 Pro UI workbench demo-flow smoke test.

This is an opt-in Playwright e2e test. It verifies the downgraded Canvas
branch is not promoted by the four-page DeepSeek UI workbench, then drives the
actual browser route from requirements intake through sandbox review and back
to logic revision. Model endpoints are fulfilled locally so the demo acceptance
does not depend on live DeepSeek credentials.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator

import pytest

from well_harness.requirements_intake.logic_builder import _build_l1_l4_circuit_view

pytestmark = pytest.mark.e2e

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect, sync_playwright  # noqa: E402

ARTIFACT_DIR = Path("artifacts/deepseek-ui-workbench-e2e")
PRIMARY_FLOW = "deepseek-v4-pro-ui-workbench"
CANVAS_STATUS = "degraded-backup"

REQUIREMENTS_READY = {
    "kind": "ai-fantui-requirements-intake-analysis",
    "status": "ready_for_logic_builder",
    "ready_for_logic_builder": True,
    "summary_zh": "DeepSeek V4 Pro 已将反推逻辑需求整理为可绘制的概念链路。",
    "source_requirements_sha256": "deepseek-demo-sha256",
    "source_document": {
        "name": "deepseek-v4-pro-demo-requirements.md",
    },
    "open_questions": [],
    "concept_logic_nodes": [
        {
            "id": "input_ra",
            "label": "RA 高度",
            "node_kind": "input",
            "description_zh": "读取无线电高度并供门限判断使用。",
            "parameters": [{"id": "ra_threshold", "label": "RA 门限", "default": 6, "unit": "ft"}],
        },
        {
            "id": "gate_release",
            "label": "释放门",
            "node_kind": "logic",
            "description_zh": "汇总 TRA、SW1、SW2 与 EEC 条件。",
            "parameters": [],
        },
        {
            "id": "output_unlock",
            "label": "油门锁释放",
            "node_kind": "output",
            "description_zh": "输出概念级释放命令。",
            "parameters": [],
        },
    ],
    "concept_edges": [
        {"source": "input_ra", "target": "gate_release", "label": "RA < 6ft", "endpoint_status": "resolved"},
        {"source": "gate_release", "target": "output_unlock", "label": "all gates true", "endpoint_status": "resolved"},
    ],
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}

LOGIC_DRAWING = {
    "kind": "ai-fantui-logic-link-drawing",
    "status": "draft_ready",
    "summary_zh": "DeepSeek V4 Pro 已生成初版逻辑链路图，节点层级和连线可读。",
    "source_requirements_sha256": "deepseek-demo-sha256",
    "canvas": {"width": 1180, "height": 620},
    "nodes": [
        {
            "id": "input_ra",
            "label": "RA 高度",
            "node_kind": "input",
            "description_zh": "高度输入节点。",
            "x": 70,
            "y": 170,
            "width": 190,
            "height": 110,
        },
        {
            "id": "gate_release",
            "label": "释放门",
            "node_kind": "logic",
            "description_zh": "TRA、SW1、SW2、EEC 条件汇合。",
            "x": 450,
            "y": 155,
            "width": 220,
            "height": 126,
        },
        {
            "id": "output_unlock",
            "label": "油门锁释放",
            "node_kind": "output",
            "description_zh": "概念输出命令。",
            "x": 830,
            "y": 170,
            "width": 210,
            "height": 110,
        },
    ],
    "edges": [
        {
            "id": "edge_ra_gate",
            "source": "input_ra",
            "target": "gate_release",
            "route": [{"x": 260, "y": 225}, {"x": 450, "y": 225}],
        },
        {
            "id": "edge_gate_output",
            "source": "gate_release",
            "target": "output_unlock",
            "route": [{"x": 670, "y": 225}, {"x": 830, "y": 225}],
        },
    ],
    "parameter_panels": [
        {
            "id": "panel_ra_threshold",
            "node_id": "input_ra",
            "label": "RA 门限",
            "min": 0,
            "max": 20,
            "default": 6,
            "unit": "ft",
            "x": 80,
            "y": 330,
            "width": 180,
            "height": 80,
        },
    ],
    "drawing_notes": ["初版图纸用于演示级需求到逻辑链路走读，不修改控制逻辑真值。"],
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}

FAULT_PREPARATION = {
    "kind": "ai-fantui-fault-injection-preparation",
    "status": "fault_preparation_ready",
    "summary_zh": "已基于当前逻辑图准备故障候选和注入边界问题。",
    "fault_scenarios": [
        {
            "id": "fault_ra_stuck_low",
            "label": "RA 低值卡滞",
            "node_id": "input_ra",
            "fault_type": "stuck_low",
            "severity": "high",
            "rationale_zh": "RA 输入会直接影响释放门判断。",
            "expected_effect_zh": "可能提前满足释放条件。",
            "observable_signals": ["ra_ft", "release_gate"],
        }
    ],
    "injection_points": [
        {
            "id": "inject_ra",
            "node_id": "input_ra",
            "signal_name": "ra_ft",
            "injection_mode": "override",
            "safe_boundary_zh": "仅 dry-run，不触发真实执行。",
        }
    ],
    "boundary_questions": [
        {
            "id": "boundary_dry_run",
            "prompt_zh": "确认本次只生成 dry-run 沙盒建议？",
            "rationale_zh": "防止演示链路被误解为真实控制执行。",
        },
        {
            "id": "boundary_range",
            "prompt_zh": "确认 RA 注入范围限制在 0 到 20ft？",
            "rationale_zh": "保证沙盒观察点有明确范围。",
        },
    ],
    "workflow_notes": ["完成边界确认后进入沙盒注入配置。"],
    "coverage_completion": {
        "strategy": "deterministic_dry_run_candidate",
        "completed_node_ids": ["thr_lock_rel"],
        "semantic_gate": "critical_node_coverage",
    },
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}

SANDBOX_PLAN = {
    "kind": "ai-fantui-fault-injection-sandbox-plan",
    "status": "sandbox_plan_ready",
    "summary_zh": "已生成 dry-run 沙盒配置建议和人工审查清单。",
    "sandbox_injection_plan": [
        {
            "id": "plan_ra_override",
            "fault_scenario_id": "fault_ra_stuck_low",
            "node_id": "input_ra",
            "injection_mode": "override",
            "safe_range_zh": "RA 输入限制在 0 到 20ft。",
            "expected_effect_zh": "观察释放门是否只在完整条件满足后放行。",
        }
    ],
    "observation_points": [
        {
            "id": "observe_release_gate",
            "node_id": "gate_release",
            "signal_name": "release_gate",
            "check_zh": "确认 RA 异常不会绕过 TRA、SW1、SW2、EEC 条件。",
        }
    ],
    "review_checklist": [
        {
            "id": "review_dry_run",
            "category": "dry_run",
            "condition_zh": "确认沙盒配置只读且不运行 tick。",
            "pass_criteria_zh": "run_tick:false、simulate:false、dry_run_only:true。",
        }
    ],
    "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
    "plan_coverage_completion": {
        "strategy": "deterministic_dry_run_plan",
        "completed_fault_scenario_ids": ["auto_fault_thr_lock_rel"],
        "semantic_gate": "scenario_plan_coverage",
    },
    "controller_truth_modified": False,
    "certification_claim": "none",
    "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
}


def _dense_sandbox_plan() -> dict[str, Any]:
    payload = json.loads(json.dumps(SANDBOX_PLAN))
    payload["sandbox_injection_plan"] = [
        {
            "id": f"plan_{index}",
            "fault_scenario_id": f"fault_{index}",
            "node_id": f"node_{index}",
            "injection_mode": "override",
            "safe_range_zh": "仅 dry-run，范围由准备页边界限制。",
            "expected_effect_zh": "观察对应逻辑节点是否保持可解释状态。",
        }
        for index in range(1, 10)
    ]
    payload["observation_points"] = [
        {
            "id": f"observe_{index}",
            "node_id": f"node_{index}",
            "signal_name": f"signal_{index}",
            "check_zh": "记录 dry-run 输出，不触发仿真 tick。",
        }
        for index in range(1, 10)
    ]
    payload["review_checklist"] = [
        {
            "id": f"review_{index}",
            "category": "risk" if index % 2 else "coverage",
            "condition_zh": f"确认审查细项 {index}。",
            "pass_criteria_zh": "只作为折叠细项展示，不要求逐项勾选。",
        }
        for index in range(1, 9)
    ]
    return payload


def _l1_l4_circuit_requirements() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-requirements-intake-analysis",
        "status": "ready_for_logic_builder",
        "ready_for_logic_builder": True,
        "summary_zh": "本地预解析已收敛出 L1-L4 反推链路。",
        "concept_logic_nodes": [
            {"id": "logic1", "label": "L1", "node_kind": "logic"},
            {"id": "logic2", "label": "L2", "node_kind": "logic"},
            {"id": "logic3", "label": "L3", "node_kind": "logic"},
            {"id": "logic4", "label": "L4", "node_kind": "logic"},
        ],
        "concept_edges": [],
        "deterministic_preparse": {"available": True, "applied": True},
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
    }


def _circuit_view_drawing() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-logic-link-drawing",
        "status": "draft_ready",
        "summary_zh": "确定性 L1-L4 电路图已生成。",
        "source_requirements_sha256": "l1-l4-circuit-sha",
        "canvas": {"width": 900, "height": 400},
        "nodes": [],
        "edges": [],
        "parameter_panels": [],
        "drawing_notes": ["确定性电路视图复刻 demo.html 链路。"],
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "circuit_view": _build_l1_l4_circuit_view(_l1_l4_circuit_requirements()),
    }


@pytest.fixture(scope="module")
def browser() -> Iterator[Any]:
    with sync_playwright() as pw:
        try:
            instance = pw.chromium.launch()
        except Exception as exc:
            pytest.skip(f"chromium browser not installed: {exc}")
        try:
            yield instance
        finally:
            instance.close()


def _fulfill_json(route: Any, payload: dict[str, Any]) -> None:
    route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(payload, ensure_ascii=False),
    )


def _install_model_routes(page: Any) -> None:
    page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
        "provider": "deepseek",
        "model": "deepseek-v4-pro",
        "api_base": "https://api.deepseek.com",
        "key_available": True,
        "key_source": "env:DEEPSEEK_API_KEY",
        "live_ready": True,
    }))
    page.route("**/api/requirements-intake/analyze", lambda route: _fulfill_json(route, REQUIREMENTS_READY))
    page.route("**/api/requirements-intake/draw-logic", lambda route: _fulfill_json(route, _circuit_view_drawing()))
    page.route(
        "**/api/requirements-intake/prepare-fault-injection",
        lambda route: _fulfill_json(route, FAULT_PREPARATION),
    )
    page.route(
        "**/api/requirements-intake/prepare-fault-injection/sandbox",
        lambda route: _fulfill_json(route, SANDBOX_PLAN),
    )


def _replay_payload() -> dict[str, Any]:
    fault_payload = {
        **FAULT_PREPARATION,
        "boundary_answers": [
            {
                "id": "boundary_dry_run",
                "prompt_zh": "确认本次只生成 dry-run 沙盒建议？",
                "answer_zh": "确认只用于 dry-run 回放演示。",
            },
            {
                "id": "boundary_range",
                "prompt_zh": "确认 RA 注入范围限制在 0 到 20ft？",
                "answer_zh": "确认 RA 注入范围限制在 0 到 20ft。",
            },
        ],
    }
    return {
        "kind": "ai-fantui-deepseek-live-demo-replay",
        "source": "artifacts/deepseek-live-full-chain",
        "requirements_payload": REQUIREMENTS_READY,
        "drawing_payload": _circuit_view_drawing(),
        "fault_preparation_payload": FAULT_PREPARATION,
        "sandbox_plan_payload": SANDBOX_PLAN,
        "boundary_answers": fault_payload["boundary_answers"],
        "run_summary": {"ok": True, "model": "deepseek-v4-pro"},
        "replay_summary": {
            "ok": True,
            "model": "deepseek-v4-pro",
            "generated_at": "2026-05-13T10:30:00Z",
            "stage_counts": [
                {"id": "requirements", "label_zh": "需求理解", "primary": 3, "secondary": 2, "summary_zh": "3 concepts / 2 edges"},
                {"id": "drawing", "label_zh": "逻辑图", "primary": 20, "secondary": 23, "summary_zh": "20 circuit nodes / 23 wires"},
                {"id": "fault", "label_zh": "故障准备", "primary": 1, "secondary": 1, "summary_zh": "1 scenarios / 1 points / 2 questions"},
                {"id": "sandbox", "label_zh": "沙盒计划", "primary": 1, "secondary": 1, "summary_zh": "1 plans / 1 observations / 1 reviews"},
            ],
        },
        "local_storage_keys": {
            "requirements": "ai-fantui-requirements-intake-ready-v1",
            "drawing": "ai-fantui-logic-builder-drawing-v1",
            "change_history": "ai-fantui-logic-builder-change-history-v1",
            "fault": "ai-fantui-fault-injection-preparation-v1",
            "sandbox": "ai-fantui-fault-injection-sandbox-plan-v1",
        },
    }


def _assert_deepseek_page_contract(page: Any, active_key: str) -> dict[str, Any]:
    page.evaluate("window.scrollTo(0, 0)")
    expect(page.locator("body")).to_have_attribute("data-primary-flow", PRIMARY_FLOW)
    expect(page.locator("body")).to_have_attribute("data-canvas-status", CANVAS_STATUS)
    expect(page.locator("body")).to_have_attribute("data-nav-current", active_key)

    forbidden_links = page.eval_on_selector_all(
        "a[href]",
        """(links) => links
          .map((link) => link.getAttribute("href"))
          .filter((href) => href === "/workbench" || href === "/workbench/start")""",
    )
    assert forbidden_links == []

    expect(page.locator("#deepseek-nav-mainline")).to_be_visible()
    expect(page.locator("#deepseek-nav-mainline .unified-nav-link")).to_have_count(4)
    expect(page.locator(f'#deepseek-nav-mainline [data-nav-key="{active_key}"]')).to_be_visible()
    expect(page.locator("#deepseek-nav-advanced-modules")).to_be_visible()
    assert page.locator("#deepseek-nav-advanced-modules").evaluate("element => element.open") is False
    expect(page.locator('#deepseek-nav-advanced-modules a[href="/demo.html"]')).to_be_hidden()
    expect(page.locator('#deepseek-nav-advanced-modules a[href="/fantui_circuit.html"]')).to_be_hidden()

    nav_box = page.locator("header.unified-nav").bounding_box()
    topbar_box = page.locator("main > section").first.bounding_box()
    workflow_box = page.locator('[aria-label="流程总览"]').bounding_box()
    assert nav_box is not None
    assert topbar_box is not None
    if nav_box["width"] < 200:
        assert nav_box["height"] >= 700
        assert topbar_box["x"] >= nav_box["x"] + nav_box["width"] - 2
        assert topbar_box["y"] >= 0
    else:
        assert nav_box["width"] >= 900
        assert topbar_box["y"] >= nav_box["y"] + nav_box["height"] - 2
    if active_key == "logic-builder":
        assert workflow_box is not None
        assert workflow_box["y"] >= topbar_box["y"] - 2
        assert workflow_box["y"] + workflow_box["height"] <= topbar_box["y"] + topbar_box["height"] + 2
        assert workflow_box["height"] >= 48
    else:
        expect(page.locator('[aria-label="流程总览"]')).to_have_count(1)
        if workflow_box is not None:
            assert workflow_box["y"] >= topbar_box["y"] + topbar_box["height"] - 2
            assert workflow_box["height"] >= 1

    background = page.evaluate(
        """
        () => {
          const raw = getComputedStyle(document.body).backgroundColor;
          const parts = raw.match(/\\d+(?:\\.\\d+)?/g)?.slice(0, 3).map(Number) || [255, 255, 255];
          return {raw, average: (parts[0] + parts[1] + parts[2]) / 3};
        }
        """
    )
    assert background["average"] < 80 or background["average"] > 220

    return {
        "path": page.url,
        "active_key": active_key,
        "nav": nav_box,
        "topbar": topbar_box,
        "workflow": workflow_box,
        "background": background["raw"],
    }


def _screenshot(page: Any, name: str) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(ARTIFACT_DIR / f"{name}.png"), full_page=True)


def _assert_logic_circuit_blueprint_geometry(page: Any) -> None:
    geometry = page.evaluate(
        """() => {
          const failures = [];
          const nodeRects = new Map(Array.from(document.querySelectorAll(".logic-circuit-node")).map((node) => {
            const box = node.querySelector(".logic-circuit-node-box, .logic-circuit-gate-box");
            return [node.dataset.demoNodeId || node.dataset.nodeId || "", {
              x: Number(box?.getAttribute("x") || 0),
              y: Number(box?.getAttribute("y") || 0),
              width: Number(box?.getAttribute("width") || 0),
              height: Number(box?.getAttribute("height") || 0),
            }];
          }));
          const junctions = Array.from(document.querySelectorAll(".logic-circuit-junction")).map((junction) => ({
            x: Number(junction.getAttribute("cx") || 0),
            y: Number(junction.getAttribute("cy") || 0),
            source: junction.dataset.source || "",
          }));
          const parsePoints = (raw) => String(raw || "").trim().split(/\\s+/).map((pair) => {
            const [x, y] = pair.split(",").map(Number);
            return {x, y};
          }).filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));
          const pointOnRectEdge = (point, rect, tolerance = 3) => {
            const minX = rect.x;
            const maxX = rect.x + rect.width;
            const minY = rect.y;
            const maxY = rect.y + rect.height;
            const withinX = point.x >= minX - tolerance && point.x <= maxX + tolerance;
            const withinY = point.y >= minY - tolerance && point.y <= maxY + tolerance;
            const onVertical = Math.abs(point.x - minX) <= tolerance || Math.abs(point.x - maxX) <= tolerance;
            const onHorizontal = Math.abs(point.y - minY) <= tolerance || Math.abs(point.y - maxY) <= tolerance;
            return withinX && withinY && (onVertical || onHorizontal);
          };
          const pointOnJunction = (point, source) => junctions.some((junction) => (
            (!source || junction.source === source)
            && Math.hypot(point.x - junction.x, point.y - junction.y) <= 4
          ));
          const segmentCutsRect = (a, b, rect) => {
            const left = rect.x + 4;
            const right = rect.x + rect.width - 4;
            const top = rect.y + 4;
            const bottom = rect.y + rect.height - 4;
            if (Math.abs(a.y - b.y) < 0.01) {
              const y = a.y;
              const minX = Math.min(a.x, b.x);
              const maxX = Math.max(a.x, b.x);
              return y > top && y < bottom && maxX > left && minX < right;
            }
            if (Math.abs(a.x - b.x) < 0.01) {
              const x = a.x;
              const minY = Math.min(a.y, b.y);
              const maxY = Math.max(a.y, b.y);
              return x > left && x < right && maxY > top && minY < bottom;
            }
            return false;
          };
          for (const wire of document.querySelectorAll(".logic-circuit-wire")) {
            const points = parsePoints(wire.getAttribute("points"));
            const source = wire.dataset.source || "";
            const target = wire.dataset.target || "";
            const start = points[0];
            const end = points[points.length - 1];
            const sourceRect = nodeRects.get(source);
            const targetRect = nodeRects.get(target);
            const id = wire.dataset.wireId || `${source}->${target}`;
            if (!start || !end || !sourceRect || !targetRect) {
              failures.push(`${id}: missing endpoint or node`);
              continue;
            }
            if (!pointOnRectEdge(start, sourceRect) && !pointOnJunction(start, source)) {
              failures.push(`${id}: source endpoint floats`);
            }
            if (!pointOnRectEdge(end, targetRect) && !pointOnJunction(end, target)) {
              failures.push(`${id}: target endpoint floats`);
            }
            for (let index = 1; index < points.length; index += 1) {
              const a = points[index - 1];
              const b = points[index];
              for (const [nodeId, rect] of nodeRects) {
                if (nodeId === source || nodeId === target) continue;
                if (segmentCutsRect(a, b, rect)) {
                  failures.push(`${id}: segment ${index} cuts ${nodeId}`);
                }
              }
            }
          }
          const overflowingLabels = Array.from(document.querySelectorAll(
            ".logic-circuit-node-title, .logic-circuit-gate-label, .logic-circuit-node-subtitle, .logic-circuit-gate-caption"
          )).filter((label) => {
            const node = label.closest(".logic-circuit-node");
            const box = node?.querySelector(".logic-circuit-node-box, .logic-circuit-gate-box");
            const maxWidth = Number(box?.getAttribute("width") || 0) - 10;
            return maxWidth > 0
              && typeof label.getComputedTextLength === "function"
              && label.getComputedTextLength() > maxWidth + 1;
          }).map((label) => label.textContent || "");
          const stream = document.querySelector("#logic-drawing-stream-timeline");
          const streamBox = stream && !stream.hidden && stream.getClientRects().length
            ? stream.getBoundingClientRect()
            : null;
          const streamOverlaps = streamBox
            ? Array.from(document.querySelectorAll(".logic-circuit-node")).filter((node) => {
                const box = node.getBoundingClientRect();
                return !(streamBox.right < box.left
                  || streamBox.left > box.right
                  || streamBox.bottom < box.top
                  || streamBox.top > box.bottom);
              }).map((node) => node.dataset.demoNodeId || node.dataset.nodeId || "")
            : [];
          return {failures, overflowingLabels, streamOverlaps};
        }"""
    )
    assert geometry["failures"] == []
    assert geometry["overflowingLabels"] == []
    assert geometry["streamOverlaps"] == []


def _assert_sandbox_replay_blueprint_geometry(page: Any) -> None:
    geometry = page.evaluate(
        """() => {
          const canvas = document.querySelector("#fault-sandbox-replay-canvas-main");
          const canvasBox = canvas?.getBoundingClientRect();
          const failures = [];
          if (!canvas || !canvasBox) return {failures: ["missing replay canvas"], textOverflow: []};
          const nodeRects = new Map(Array.from(canvas.querySelectorAll("[data-replay-canvas-node]")).map((node) => {
            const box = node.getBoundingClientRect();
            return [node.dataset.replayCanvasNode || "", {
              left: box.left - canvasBox.left,
              right: box.right - canvasBox.left,
              top: box.top - canvasBox.top,
              bottom: box.bottom - canvasBox.top,
              width: box.width,
              height: box.height,
            }];
          }));
          const distanceToRectEdge = (point, rect) => {
            const clampedX = Math.max(rect.left, Math.min(point.x, rect.right));
            const clampedY = Math.max(rect.top, Math.min(point.y, rect.bottom));
            const inside = point.x >= rect.left && point.x <= rect.right && point.y >= rect.top && point.y <= rect.bottom;
            if (!inside) return Math.hypot(point.x - clampedX, point.y - clampedY);
            return Math.min(
              Math.abs(point.x - rect.left),
              Math.abs(point.x - rect.right),
              Math.abs(point.y - rect.top),
              Math.abs(point.y - rect.bottom),
            );
          };
          for (const link of canvas.querySelectorAll("[data-replay-canvas-link]")) {
            const source = link.dataset.sourceNode || "";
            const target = link.dataset.targetNode || "";
            const sourceRect = nodeRects.get(source);
            const targetRect = nodeRects.get(target);
            const start = {x: Number(link.dataset.startX), y: Number(link.dataset.startY)};
            const end = {x: Number(link.dataset.endX), y: Number(link.dataset.endY)};
            const id = link.dataset.replayCanvasLink || "link";
            if (!source || !target || !sourceRect || !targetRect || !Number.isFinite(start.x) || !Number.isFinite(end.x)) {
              failures.push(`${id}: missing source/target endpoint contract`);
              continue;
            }
            if (distanceToRectEdge(start, sourceRect) > 3.5) failures.push(`${id}: source endpoint floats`);
            if (distanceToRectEdge(end, targetRect) > 3.5) failures.push(`${id}: target endpoint floats`);
            if (Math.hypot(end.x - start.x, end.y - start.y) < 12) failures.push(`${id}: link too short`);
          }
          const textOverflow = Array.from(canvas.querySelectorAll(
            ".sandbox-replay-canvas-node strong, .sandbox-replay-canvas-node code, .sandbox-replay-canvas-metrics span"
          )).filter((element) => element.scrollWidth > element.clientWidth + 1)
            .map((element) => element.textContent || "");
          return {failures, textOverflow};
        }"""
    )
    assert geometry["failures"] == []
    assert geometry["textOverflow"] == []


def test_landing_page_defaults_to_five_entry_compact_shell(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="networkidle")
        expect(page.locator("#home-default-mode-grid")).to_be_visible()
        expect(page.locator("#home-default-mode-grid .home-mode-entry")).to_have_count(5)
        for label in ["画布", "运行", "参数", "证据", "报告"]:
            expect(page.locator("#home-default-mode-grid")).to_contain_text(label)
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#run-drawer"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#parameter-drawer"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#evidence"]')).to_be_visible()
        expect(page.locator('#home-default-mode-grid a[href="/logic-builder#report"]')).to_be_visible()
        expect(page.locator(".home-command-palette-hint")).to_be_visible()
        expect(page.locator("#home-primary-flow-grid")).to_be_hidden()
        expect(page.locator("#deepseek-live-replay-import")).to_be_hidden()
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
    finally:
        page.close()


def test_deepseek_subproject_nav_collapses_legacy_modules(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/logic-builder", wait_until="domcontentloaded")
        expect(page.locator("#deepseek-nav-mainline .unified-nav-link")).to_have_count(4)
        expect(page.locator('#deepseek-nav-mainline a[href="/requirements-intake"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-mainline a[href="/logic-builder"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-mainline a[href="/fault-injection-prepare"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-mainline a[href="/fault-injection-sandbox"]')).to_be_visible()
        assert page.locator("#deepseek-nav-advanced-modules").evaluate("element => element.open") is False
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/demo.html"]')).to_be_hidden()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/c919_etras_workstation.html"]')).to_be_hidden()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/fantui_requirements.html"]')).to_be_hidden()

        page.click("#deepseek-nav-advanced-modules summary")
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/demo.html"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/fantui_circuit.html"]')).to_be_visible()
        expect(page.locator('#deepseek-nav-advanced-modules a[href="/c919_requirements.html"]')).to_be_visible()
        assert page.evaluate(
            """() => {
              const menu = document.querySelector("#deepseek-nav-advanced-modules .unified-nav-advanced-links");
              if (!menu) return false;
              const box = menu.getBoundingClientRect();
              const hit = document.elementFromPoint(box.left + 12, box.top + 12);
              return Boolean(hit && menu.contains(hit));
            }"""
        ) is True
    finally:
        page.close()


def test_deepseek_four_page_command_strips_use_single_primary_next_cta(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page_contracts = [
        (
            "/requirements-intake",
            "1",
            "需求理解",
            "#logic-builder-next",
            "下一步：进入逻辑链路绘制",
            '[data-usage-path-cue="requirements"]',
            "下一页生成逻辑画布",
            [("#requirements-analyze", re.compile(r"^检查：(分析需求|本地预解析)$"))],
        ),
        (
            "/logic-builder",
            "2",
            "逻辑绘制",
            "#logic-fault-next",
            "下一步：进入故障准备",
            '[data-usage-path-cue="logic"]',
            "下一页生成故障矩阵",
            [
                ("#logic-regenerate", "检查：重新绘制"),
                ("#logic-back", "更多：返回需求"),
            ],
        ),
        (
            "/fault-injection-prepare",
            "3",
            "故障准备",
            "#fault-sandbox-next",
            "下一步：进入沙盒审查",
            '[data-usage-path-cue="fault"]',
            "候选矩阵",
            [
                ("#fault-generate", "检查：生成候选"),
                ("#fault-back", "更多：返回绘图"),
            ],
        ),
        (
            "/fault-injection-sandbox",
            "4",
            "沙盒注入",
            "#fault-sandbox-revision-next",
            "下一步：生成逻辑修订单",
            '[data-usage-path-cue="sandbox"]',
            "审查包",
            [
                ("#fault-sandbox-generate", "检查：生成配置"),
                ("#fault-sandbox-back", "更多：返回故障准备"),
            ],
        ),
    ]
    try:
        for path, step, title, primary_selector, primary_text, cue_selector, cue_text, secondary_buttons in page_contracts:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            strip = page.locator('[data-command-strip="deepseek-step"]')
            expect(strip).to_be_visible()
            expect(strip).to_have_attribute("data-command-step", step)
            expect(strip.locator("h1")).to_have_text(title)
            expect(strip.locator(".deepseek-step-kicker")).to_have_text(f"STEP {step}/4")
            expect(page.locator(cue_selector)).to_be_visible()
            expect(page.locator(cue_selector)).to_contain_text(cue_text)
            expect(strip.locator('[data-primary-next-action="true"]')).to_have_count(1)
            expect(strip.locator(primary_selector)).to_have_text(primary_text)
            expect(strip.locator(primary_selector)).to_have_attribute("data-primary-next-action", "true")
            for selector, text in secondary_buttons:
                expect(strip.locator(selector)).to_have_text(text)
                assert "secondary" in (strip.locator(selector).get_attribute("class") or "")
            box = strip.bounding_box()
            assert box is not None
            assert box["height"] <= 128
    finally:
        page.close()


def test_deepseek_low_cognitive_load_guardrails_hold_in_browser(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page_contracts = [
        (
            "/requirements-intake",
            "#requirements-workflow-steps",
            "#logic-builder-next",
            {
                "#requirements-analyze": "secondary",
                "#requirements-replay-import": "secondary",
                "#requirements-offline-action": "secondary",
                "#requirements-clear": "advanced",
            },
        ),
        (
            "/logic-builder",
            "#logic-workflow-steps",
            "#logic-fault-next",
            {
                "#logic-regenerate": "secondary",
                "#logic-back": "secondary",
                "#logic-fill-handoff-draft": "secondary",
                "#logic-clear-change": "advanced",
                "#logic-cancel-change": "advanced",
            },
        ),
        (
            "/fault-injection-prepare",
            "#fault-workflow-steps",
            "#fault-sandbox-next",
            {
                "#fault-generate": "secondary",
                "#fault-back": "secondary",
                "#fault-save-boundaries": "secondary",
            },
        ),
        (
            "/fault-injection-sandbox",
            "#fault-sandbox-workflow-steps",
            "#fault-sandbox-revision-next",
            {
                "#fault-sandbox-generate": "secondary",
                "#fault-sandbox-back": "secondary",
            },
        ),
    ]
    try:
        for path, workflow_selector, primary_selector, button_tiers in page_contracts:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            expect(page.locator("#deepseek-nav-mainline")).to_have_attribute("data-ux-main-flow", "four-step")
            expect(page.locator("#deepseek-nav-mainline .unified-nav-link")).to_have_count(4)
            expect(page.locator("#deepseek-nav-advanced-modules")).not_to_have_attribute("open", "")
            expect(page.locator(workflow_selector)).to_have_attribute("data-ux-main-flow", "four-step")
            expect(page.locator('[data-primary-next-action="true"]')).to_have_count(1)
            expect(page.locator(primary_selector)).to_have_attribute("data-ux-action-tier", "primary")

            for selector, tier in button_tiers.items():
                expect(page.locator(selector)).to_have_attribute("data-ux-action-tier", tier)

            mispromoted_tools = page.evaluate(
                """() => {
                  const riskText = /清空|取消|返回|重新|重绘|回放|本地|保存|生成修改意见草稿/;
                  return Array.from(document.querySelectorAll("button"))
                    .filter((button) => {
                      const box = button.getBoundingClientRect();
                      return box.width > 0 && box.height > 0 && riskText.test(button.textContent || "");
                    })
                    .filter((button) => {
                      const tier = button.dataset.uxActionTier;
                      return button.dataset.primaryNextAction === "true" || !["secondary", "advanced"].includes(tier);
                    })
                    .map((button) => `${button.id || button.textContent}:${button.dataset.uxActionTier || "missing"}`);
                }"""
            )
            assert mispromoted_tools == []

        page.goto(f"{demo_server}/demo-reconstruction", wait_until="networkidle")
        expect(page.locator("body")).to_have_attribute("data-ux-page-role", "comparison")
        expect(page.locator('[data-primary-next-action="true"]')).to_have_count(0)
        expect(page.locator("#demo-reconstruction-original-frame")).to_be_visible()
        expect(page.locator("#demo-reconstruction-current-panel")).to_be_visible()
    finally:
        page.close()


def test_requirements_intake_compacts_first_run_decision_board(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        board = page.locator('[data-decision-board="requirements"]')
        expect(board).to_be_visible()
        expect(board.locator(".requirements-decision-card")).to_have_count(3)
        expect(board.locator('[data-decision-card="path"] h2')).to_have_text("路径")
        expect(board.locator('[data-decision-card="verdict"] h2')).to_have_text("当前结论")
        expect(board.locator('[data-decision-card="next"] h2')).to_have_text("下一步")
        expect(board.locator("#requirements-preflight-live-state")).to_be_visible()
        expect(board.locator("#requirements-replay-import")).to_have_text("回放")
        expect(board.locator("#requirements-offline-action")).to_have_text("本地")
        expect(board.locator("#result-state")).to_have_text("尚未生成")
        expect(board.locator("#requirements-summary")).to_contain_text("等待模型")
        expect(board.locator("#next-step-copy")).to_contain_text("先上传需求")
        expect(board.locator('[data-usage-path-cue="requirements"]')).to_contain_text("下一页生成逻辑画布")
        expect(board.locator("#requirements-burden-action")).to_have_text("等待分析")
        expect(page.locator(".requirements-result-panel .result-header")).to_have_count(0)
        expect(page.locator(".requirements-result-panel #next-step-panel")).to_have_count(0)
        expect(page.locator(".requirements-result-panel #requirements-burden-summary")).to_have_count(0)

        board_box = board.bounding_box()
        layout_box = page.locator(".requirements-layout").bounding_box()
        assert board_box is not None
        assert layout_box is not None
        assert board_box["height"] <= 180
        assert layout_box["y"] <= 500
    finally:
        page.close()


def test_desktop_requirements_preflight_uses_compact_status_copy(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": False,
            "key_source": "",
            "live_ready": False,
            "checked": ["DEEPSEEK_API_KEY", "DeepSeek_API_key"],
        }))

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        board = page.locator('[data-decision-board="requirements"]')
        expect(board.locator('[data-decision-card="path"] h2')).to_have_text("路径")
        expect(board.locator("#requirements-preflight-live-card > span")).to_have_text("DeepSeek")
        expect(board.locator("#requirements-preflight-live-state")).to_have_text("未接入")
        expect(board.locator("#requirements-preflight-replay-state")).to_have_text("回放可用")
        expect(board.locator("#requirements-preflight-offline-state")).to_have_text("本地候选")
        expect(page.locator(".requirements-live-only-row span")).to_have_text("仅 DeepSeek")
        expect(page.locator("#requirements-provider-key-source")).to_have_text("env key 缺失")

        board_box = board.bounding_box()
        assert board_box is not None
        assert board_box["height"] <= 150
        assert "DEEPSEEK_API_KEY" not in (board.inner_text() + page.locator("#requirements-provider-key-source").inner_text())
    finally:
        page.close()


def test_desktop_requirements_page_draws_demo_cockpit_skin(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        cockpit = page.locator('[data-ui-skin="demo-cockpit"]')
        expect(cockpit).to_be_visible()
        expect(page.locator('[data-cockpit-role="canopy-frame"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="status-banner"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="instrument-rail"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="input-bay"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="mission-console"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="mission-strip"]')).to_be_hidden()

        expect(page.locator(".requirements-cockpit-canopy-window")).to_have_count(3)
        expect(page.locator('[data-cockpit-role="instrument-rail"] .requirements-decision-card')).to_have_count(3)
        expect(page.locator('[data-cockpit-role="mission-console"] .clarification-primary')).to_be_visible()

        cockpit_box = cockpit.bounding_box()
        rail_box = page.locator('[data-cockpit-role="instrument-rail"]').bounding_box()
        console_box = page.locator('[data-cockpit-role="mission-console"]').bounding_box()
        assert cockpit_box is not None
        assert rail_box is not None
        assert console_box is not None
        assert cockpit_box["width"] >= 1320
        assert rail_box["y"] < console_box["y"]
    finally:
        page.close()


def test_desktop_requirements_workbench_prioritizes_clarification_over_secondary_outputs(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        layout = page.locator(".requirements-layout")
        shell = page.locator(".requirements-shell")
        expect(shell).to_have_attribute("data-workstation-shell", "canvas-first")
        expect(shell).to_have_attribute("data-workstation-state", "primary")
        expect(shell).to_have_attribute("data-blueprint14-rhythm", "compact-canvas")
        expect(shell).to_have_attribute("data-active-aux-panel", "none")
        expect(shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator('[data-blueprint14-compact-topbar="step-provider-next"]')).to_be_visible()
        expect(page.locator('#requirements-preflight-panel[data-blueprint14-density="compact-decision-board"]')).to_be_visible()
        expect(layout).to_have_attribute("data-desktop-workbench", "input-clarification")
        expect(layout).to_have_attribute("data-workstation-layout", "primary-canvas-plus-inspector")
        expect(layout).to_have_attribute("data-blueprint14-layout", "source-inspector-primary-canvas")
        expect(page.locator(".requirements-input-panel")).to_be_visible()
        expect(page.locator('.requirements-input-panel[data-workstation-inspector="source-input"]')).to_be_visible()
        expect(page.locator('.requirements-input-panel[data-blueprint14-inspector="source-document-input"]')).to_be_visible()
        expect(page.locator(".clarification-primary")).to_be_visible()
        expect(page.locator('.clarification-primary[data-workstation-stage="primary-canvas"]')).to_be_visible()
        expect(page.locator('.clarification-primary[data-blueprint14-canvas-rhythm="expanded-first-screen"]')).to_be_visible()
        expect(page.locator("#requirements-secondary-panels > details")).to_have_count(4)

        for selector in [
            "#clarification-trace",
            "#requirements-questions-panel",
            "#requirements-concept-graph-panel",
            "#requirements-edges-panel",
        ]:
            assert page.locator(selector).evaluate(
                "element => element.tagName.toLowerCase() === 'details' && !element.open"
            )

        expect(page.locator("#requirements-graph")).not_to_be_visible()
        expect(page.locator("#requirements-edges")).not_to_be_visible()

        input_box = page.locator(".requirements-input-panel").bounding_box()
        primary_box = page.locator(".clarification-primary").bounding_box()
        assert input_box is not None
        assert primary_box is not None
        assert primary_box["x"] > input_box["x"] + input_box["width"] - 1
        assert primary_box["width"] >= 650
        assert primary_box["height"] >= 240
        assert abs(primary_box["y"] - input_box["y"]) <= 14
        expect(page.locator("#requirements-secondary-panels")).to_be_hidden()

        page.locator('[data-requirement-choice-row="l1"]').click()
        expect(shell).to_have_attribute("data-active-aux-panel", "source-popover")
        expect(shell).to_have_attribute("data-unified-inspector-state", "source-popover")
        expect(page.locator("#requirements-row-popover")).to_be_visible()
        expect(page.locator("#requirements-row-popover")).to_have_attribute("data-unified-panel-state", "open")

        page.click("#requirements-manual-toggle")
        expect(shell).to_have_attribute("data-active-aux-panel", "manual-bubble")
        expect(shell).to_have_attribute("data-unified-inspector-state", "manual-bubble")
        expect(page.locator("#requirements-row-popover")).to_be_hidden()
        expect(page.locator("#requirements-row-popover")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#requirements-manual-bubble")).to_have_attribute("data-unified-panel-state", "open")

        page.keyboard.press("Escape")
        expect(shell).to_have_attribute("data-active-aux-panel", "none")
        expect(shell).to_have_attribute("data-workstation-state", "primary")
        expect(page.locator("#requirements-manual-bubble")).to_be_hidden()
        expect(page.locator("#requirements-manual-bubble")).to_have_attribute("data-unified-panel-state", "closed")
    finally:
        page.close()


def test_fault_sandbox_review_uses_three_primary_gates_for_dense_plan(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-plan-count")).to_have_text("9 plans")
        expect(page.locator("#fault-sandbox-observation-count")).to_have_text("9 points")
        expect(page.locator("#fault-sandbox-review-count")).to_have_text("8 checks")
        expect(page.locator("#fault-sandbox-review-row-panel")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 rows")
        expect(page.locator("#fault-sandbox-review-rows[data-blueprint-density='compact-workbench']")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-header")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .blueprint-row--sandbox-review")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .blueprint-density-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-review-row]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-density='compact-workbench']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review'] [data-blueprint-col='trace-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-link-token")).to_have_count(14)
        assert page.locator("#fault-sandbox-review-rows .blueprint-row-token").count() >= 21
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-check input[disabled]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows")).to_contain_text("控制真相未修改")
        review_row_box = page.locator("#fault-sandbox-review-rows [data-blueprint-density='compact-workbench']").first.bounding_box()
        assert review_row_box
        assert review_row_box["height"] <= 58
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_be_visible()
        expect(page.locator("#fault-sandbox-diagnosis-summary")).to_contain_text("dry-run")
        expect(page.locator("#fault-sandbox-affected-path")).to_have_text("node 1 -> node 1")
        expect(page.locator("#fault-sandbox-first-abnormal-node")).to_have_text("node 1")
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node='failure-path']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .blueprint-row--diagnosis-chain")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint-row-pattern='shared-v1']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .sandbox-diagnosis-chain-link-token")).to_have_count(6)
        expect(page.locator("#fault-sandbox-diagnosis-evidence-links [data-blueprint36-evidence-link='diagnosis']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-repair-suggestions")).to_contain_text("修订单")
        expect(page.locator("#fault-sandbox-evidence-trace")).to_be_visible()
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-row")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .blueprint-row--evidence-chain")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-link-token")).to_have_count(8)
        expect(page.locator("[data-evidence-trace-id='ET-04'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-evidence-trace-rows")).to_contain_text("审查行")
        expect(page.locator("#fault-sandbox-report-preview")).to_be_visible()
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .blueprint-row--replay-report")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-report-row='review-package-section']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-link-token")).to_have_count(14)
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-report-section-rows")).to_contain_text("故障覆盖")
        page.locator('[data-blueprint-review-row="SR-06"]').press("Enter")
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_class(re.compile("is-active"))
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_have_attribute("data-active-review-row", "SR-06")
        expect(page.locator('[data-evidence-trace-id="ET-04"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator('[data-report-section-id="RP-06"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("报告可追溯")
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("对应报告章节")
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("RP-06")
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-blueprint-review-row="SR-07"]').press("Enter")
        expect(page.locator('[data-blueprint-review-row="SR-07"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator("[data-blueprint-review-row='SR-07'] .sandbox-review-row-decision")).to_have_text(re.compile("PASS|REVIEW|WAIT"))
        expect(page.locator('[data-report-section-id="RP-07"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("控制真相未修改")
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-evidence-trace-id="ET-03"]').click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("RP-07")
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("truth_effect:none")
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-sandbox-report-action="export"]').click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-review-count")).to_have_text("7 review rows")
        expect(page.locator("#sandbox-review-package-evidence-count")).to_have_text("4 evidence links")
        expect(page.locator("#sandbox-review-package-report-count")).to_have_text("7 report sections")
        expect(page.locator("#sandbox-review-package-review-rows [data-package-item-id^='SR-']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-evidence-rows [data-package-item-id^='ET-']")).to_have_count(4)
        expect(page.locator("#sandbox-review-package-report-rows [data-package-item-id^='RP-']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-panel .blueprint-row--review-package")).to_have_count(18)
        expect(page.locator("#sandbox-review-package-panel [data-blueprint-row-pattern='shared-v1']")).to_have_count(18)
        expect(page.locator("#sandbox-review-package-review-rows [data-blueprint36-package-row='review-package-review']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-report-rows [data-blueprint36-package-row='review-package-report']")).to_have_count(7)
        expect(page.locator("#sandbox-review-package-review-rows [data-blueprint36-package-row='review-package-review'] .sandbox-review-package-link-token")).to_have_count(14)
        expect(page.locator("#sandbox-review-package-report-rows [data-blueprint36-package-row='review-package-report'] .sandbox-review-package-link-token")).to_have_count(14)
        expect(page.locator("#sandbox-review-package-invariants")).to_contain_text("truth_effect:none")
        review_package_row = page.locator("#sandbox-review-package-review-rows [data-package-item-id='SR-04']")
        expect(review_package_row).to_have_attribute("data-package-target-trace-id", "ET-02")
        expect(review_package_row).to_have_attribute("data-package-target-report-id", "RP-05")
        expect(review_package_row.locator("[data-link-kind='trace']")).to_have_text("ET-02")
        expect(review_package_row.locator("[data-link-kind='report']")).to_have_text("RP-05")
        review_package_row.click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator('[data-blueprint-review-row="SR-04"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-evidence-trace-id="ET-02"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator('[data-report-section-id="RP-05"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("故障覆盖")
        page.locator("#sandbox-evidence-close").click()

        page.locator('[data-sandbox-report-action="export"]').click()
        evidence_package_row = page.locator("#sandbox-review-package-evidence-rows [data-package-item-id='ET-04']")
        expect(evidence_package_row).to_have_attribute("data-package-target-review-row", "SR-06")
        evidence_package_row.click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-evidence-trace-id="ET-04"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator('[data-report-section-id="RP-06"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("报告可追溯")
        page.locator("#sandbox-evidence-close").click()

        page.locator('[data-sandbox-report-action="export"]').click()
        report_package_row = page.locator("#sandbox-review-package-report-rows [data-package-item-id='RP-07']")
        expect(report_package_row).to_have_attribute("data-package-target-review-row", "SR-07")
        expect(report_package_row).to_have_attribute("data-package-target-trace-id", "ET-03")
        expect(report_package_row.locator(".sandbox-review-package-decision")).to_have_text(re.compile("PASS|REVIEW|WAIT"))
        expect(report_package_row.locator("[data-link-kind='trace']")).to_have_text("ET-03")
        expect(report_package_row.locator("[data-link-kind='report']")).to_have_text("RP-07")
        report_package_row.press("Enter")
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator('[data-blueprint-review-row="SR-07"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-report-section-id="RP-07"]')).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("#sandbox-evidence-title")).to_contain_text("控制真相未修改")
        page.locator("#sandbox-evidence-close").click()

        page.locator('[data-sandbox-report-action="export"]').click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        page.keyboard.press("Escape")
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        expect(page.locator("#fault-sandbox-primary-gates")).to_be_visible()
        expect(page.locator("#fault-sandbox-detail-groups")).to_be_hidden()
        expect(page.locator("input[data-sandbox-confirm]")).to_have_count(3)
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")
        assert page.locator("#fault-sandbox-detail-groups details").first.evaluate("element => element.open") is False

        page.locator('input[data-sandbox-confirm="dry-run"]').check()
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("已确认 1/3 个一级闸门")
        page.locator('input[data-sandbox-confirm="coverage"]').check()
        page.locator('input[data-sandbox-confirm="risk"]').check()
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("可进入逻辑修订")
    finally:
        page.close()


def test_fault_sandbox_unified_inspector_summary_tracks_review_evidence_and_report(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        page.locator('[data-blueprint-review-row="SR-06"]').press("Enter")
        inspector_summary = page.locator("#sandbox-evidence-link-summary")
        expect(inspector_summary).to_be_visible()
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(inspector_summary).to_have_attribute("data-inspector-source", "review-row")
        expect(inspector_summary).to_contain_text("SR-06")
        expect(inspector_summary).to_contain_text("ET-04")
        expect(inspector_summary).to_contain_text("RP-06")
        expect(inspector_summary).to_contain_text("truth_effect:none")
        expect(inspector_summary).to_contain_text("controller_truth_modified:false")

        page.locator('[data-blueprint-review-row="SR-07"]').press("Enter")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-07")

        page.locator('[data-blueprint-review-row="SR-06"]').press("Enter")
        page.locator('[data-evidence-trace-id="ET-04"]').press("Enter")
        expect(inspector_summary).to_have_attribute("data-inspector-source", "evidence-trace")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-report-section-id="RP-06"]')).to_have_class(re.compile("is-linked-active"))

        page.locator('[data-report-section-id="RP-07"]').press("Enter")
        expect(inspector_summary).to_have_attribute("data-inspector-source", "replay-report")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(page.locator('[data-blueprint-review-row="SR-07"]')).to_have_attribute("aria-selected", "true")
        expect(page.locator('[data-evidence-trace-id="ET-03"]')).to_have_class(re.compile("is-linked-active"))

        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-sandbox-report-action="export"]').click()
        page.locator("#sandbox-review-package-evidence-rows [data-package-item-id='ET-04']").click()
        expect(inspector_summary).to_be_visible()
        expect(inspector_summary).to_have_attribute("data-inspector-source", "review-package")
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_fault_sandbox_review_rows_remain_pointer_clickable_above_report_strip(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")

        target_row = page.locator('[data-blueprint-review-row="SR-06"]')
        expect(target_row).to_be_visible()
        target_row.click()
        inspector_summary = page.locator("#sandbox-evidence-link-summary")
        expect(inspector_summary).to_be_visible()
        expect(inspector_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(inspector_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(inspector_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator("#sandbox-report-strip")).to_be_visible()
        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-sandbox-report-action="export"]').click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_report_strip_prioritizes_review_package_action(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")

        report_strip = page.locator("#sandbox-report-strip")
        expect(report_strip).to_be_visible()
        export_action = report_strip.locator('[data-sandbox-report-action="export"]')
        expect(export_action).to_be_visible()
        expect(export_action).to_have_attribute("data-ux-action-tier", "primary")
        expect(export_action).to_have_attribute("data-report-primary-action", "review-package")
        expect(export_action).to_have_class(re.compile("sandbox-report-primary"))

        assert report_strip.locator('[data-ux-action-tier="primary"]').count() == 1
        for action_id in ["rerun", "evidence", "revision"]:
            secondary_action = report_strip.locator(f'[data-sandbox-report-action="{action_id}"]')
            expect(secondary_action).to_be_visible()
            expect(secondary_action).to_have_attribute("data-ux-action-tier", "secondary")
            expect(secondary_action).to_have_class(re.compile("sandbox-report-secondary"))

        for boundary in [
            "sandbox_candidate",
            "truth_effect:none",
            "certification_claim:none",
            "controller_truth_modified:false",
        ]:
            expect(report_strip).to_contain_text(boundary)

        assert report_strip.evaluate("(element) => element.getBoundingClientRect().height <= 132") is True
        export_action.click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_replay_report_workbench_tracks_blueprint37(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        report_strip = page.locator("#sandbox-report-strip")
        expect(report_strip).to_be_visible()
        expect(report_strip).to_have_attribute("data-blueprint37-surface", "replay-report-workbench")
        expect(report_strip).to_have_attribute(
            "data-blueprint37-contract",
            "controls-timeline-report-preview-candidate-footer",
        )
        expect(page.locator("#fault-sandbox-replay-workbench")).to_be_visible()
        expect(page.locator("#fault-sandbox-replay-controls [data-replay-control]")).to_have_count(4)
        for control_label in ["暂停", "停止", "单步", "重置"]:
            expect(page.locator("#fault-sandbox-replay-controls")).to_contain_text(control_label)
        expect(page.locator("#fault-sandbox-replay-clock")).to_have_text(re.compile(r"00:03:24\s*/\s*00:20:00"))

        timeline = page.locator("#fault-sandbox-replay-timeline")
        expect(timeline).to_be_visible()
        expect(timeline).to_have_attribute("data-blueprint37-contract", "time-markers-sr-et-rp-linkage")
        expect(timeline.locator("[data-replay-marker]")).to_have_count(10)
        expect(timeline.locator("[data-replay-report-id='RP-06']")).to_have_attribute("aria-current", "true")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("节点 20/20")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("连线 23/23")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("冲突 0")
        expect(page.locator("#fault-sandbox-replay-metrics")).to_contain_text("待确认 0")

        report_preview = page.locator("#fault-sandbox-report-preview")
        expect(report_preview).to_have_attribute("data-blueprint37-panel", "report-preview-rail")
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint37-report-row='preview-rail-section']")).to_have_count(7)

        timeline.locator("[data-replay-report-id='RP-07']").click()
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(timeline.locator("[data-replay-report-id='RP-07']")).to_have_attribute("aria-current", "true")

        for boundary in [
            "sandbox_candidate",
            "truth_effect:none",
            "certification_claim:none",
            "controller_truth_modified:false",
        ]:
            expect(report_strip).to_contain_text(boundary)

        assert report_strip.evaluate("(element) => element.getBoundingClientRect().height <= 132") is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_default_main_area_uses_replay_canvas_and_report_rail(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        shell = page.locator(".sandbox-shell")
        expect(shell).to_have_attribute("data-blueprint37-top-density", "compressed-progress-gates")
        topbar_box = page.locator(".sandbox-topbar").bounding_box()
        process_box = page.locator("#fault-sandbox-process").bounding_box()
        decision_box = page.locator("#fault-sandbox-decision-board").bounding_box()
        gates_box = page.locator(".sandbox-review-gate-panel").bounding_box()
        assert topbar_box and process_box and decision_box and gates_box
        assert topbar_box["height"] <= 74
        assert process_box["height"] <= 78
        assert decision_box["height"] <= 54
        assert gates_box["height"] <= 56

        primary_surface = page.locator("#failure-path")
        expect(primary_surface).to_have_attribute(
            "data-blueprint37-layout",
            "replay-canvas-report-rail-default",
        )
        replay_panel = page.locator("#fault-sandbox-review-row-panel")
        expect(replay_panel).to_be_visible()
        expect(replay_panel).to_have_attribute("data-blueprint37-surface", "replay-main-canvas")
        expect(replay_panel).to_have_attribute("data-default-role", "replay-canvas-primary")

        replay_canvas = page.locator("#fault-sandbox-replay-canvas-main")
        expect(replay_canvas).to_be_visible()
        expect(replay_canvas).to_have_attribute(
            "data-blueprint37-contract",
            "state-nodes-verified-path-warning-boundary",
        )
        expect(page.locator("#fault-sandbox-replay-canvas-nodes [data-replay-canvas-node]")).to_have_count(12)
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-canvas-link]")).to_have_count(11)
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-link-index]")).to_have_count(11)
        expect(page.locator("#fault-sandbox-replay-canvas-links .sandbox-replay-canvas-link-badge")).to_have_count(11)
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-canvas-link='latch-l1']")).to_have_attribute("aria-current", "true")
        expect(page.locator("#fault-sandbox-replay-canvas-links [data-replay-canvas-link='latch-l2']")).to_have_attribute("aria-current", "true")
        _assert_sandbox_replay_blueprint_geometry(page)
        expect(page.locator("#fault-sandbox-replay-canvas-nodes")).to_contain_text("RA")
        expect(page.locator("#fault-sandbox-replay-canvas-nodes")).to_contain_text("L1 告警")
        expect(page.locator("#fault-sandbox-replay-canvas-nodes")).to_contain_text("取消逻辑")
        expect(page.locator("#fault-sandbox-replay-canvas-metrics")).to_contain_text("节点 20/20")
        expect(page.locator("#fault-sandbox-replay-canvas-metrics")).to_contain_text("连线 23/23")

        report_rail = page.locator("#fault-sandbox-main-report-rail")
        inspector = page.locator("#fault-sandbox-diagnosis-inspector")
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        diagnosis_path = inspector.locator(".sandbox-diagnosis-path")
        diagnosis_chain = page.locator("#fault-sandbox-diagnosis-chain")
        evidence_trace = page.locator("#fault-sandbox-evidence-trace")
        diagnosis_summary = page.locator("#fault-sandbox-diagnosis-summary")
        expect(report_rail).to_be_visible()
        expect(inspector).to_have_attribute("data-blueprint37-right-density", "layered-report-evidence")
        expect(inspector).to_have_attribute("data-blueprint37-report-mode", "replay-report-final")
        expect(report_rail).to_have_attribute("data-blueprint37-panel", "right-report-rail")
        expect(report_rail).to_have_attribute("data-blueprint37-right-section", "report-preview")
        expect(report_rail).to_have_attribute("data-blueprint39-default", "status-only")
        expect(package_summary).to_have_attribute("data-blueprint37-right-section", "active-package")
        expect(package_summary).to_be_visible()
        expect(package_summary).to_have_attribute("data-package-state", "active")
        expect(diagnosis_path).to_have_attribute("data-blueprint37-right-section", "diagnosis-summary")
        expect(diagnosis_chain).to_have_attribute("data-blueprint37-right-section", "failure-path")
        expect(evidence_trace).to_have_attribute("data-blueprint37-right-section", "evidence-trace")
        expect(report_rail.locator("[data-main-report-id]")).to_have_count(7)
        expect(report_rail.locator(".sandbox-main-report-row:visible")).to_have_count(1)
        expect(report_rail.locator("[data-report-chapter-kind]")).to_have_count(7)
        expect(report_rail.locator("[data-report-chapter-state='pass']")).to_have_count(5)
        expect(report_rail.locator("[data-report-chapter-state='review']")).to_have_count(1)
        expect(report_rail.locator("[data-report-chapter-state='wait']")).to_have_count(1)
        expect(report_rail.locator(".sandbox-main-report-status")).to_have_count(7)
        expect(report_rail.locator("[data-main-report-id='RP-06']")).to_have_attribute("aria-current", "true")
        expect(report_rail.locator("[data-main-report-id='RP-06']")).to_have_attribute("data-link-state", "active")

        page.locator("#fault-sandbox-report-section-rows [data-report-section-id='RP-07']").click()
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(report_rail.locator(".sandbox-main-report-row:visible")).to_have_count(1)
        expect(report_rail.locator("[data-main-report-id='RP-07']")).to_have_attribute("aria-current", "true")
        expect(report_rail.locator("[data-main-report-id='RP-07']")).to_have_attribute("data-link-state", "active")
        expect(page.locator("#fault-sandbox-replay-timeline [data-replay-report-id='RP-07']")).to_have_attribute("data-link-state", "active")

        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row")).to_have_count(7)
        canvas_box = replay_canvas.bounding_box()
        inspector_box = inspector.bounding_box()
        evidence_trace_box = evidence_trace.bounding_box()
        rail_box = report_rail.bounding_box()
        report_rows_box = page.locator("#fault-sandbox-main-report-rows").bounding_box()
        diagnosis_summary_box = diagnosis_summary.bounding_box()
        visible_report_row = report_rail.locator(".sandbox-main-report-row:visible").first
        first_report_title = visible_report_row.locator("strong")
        first_report_row_box = visible_report_row.bounding_box()
        package_box = package_summary.bounding_box()
        path_box = diagnosis_path.bounding_box()
        chain_box = diagnosis_chain.bounding_box()
        evidence_rows_box = page.locator("#fault-sandbox-evidence-trace-rows").bounding_box()
        assert canvas_box and inspector_box and evidence_trace_box and rail_box and report_rows_box and diagnosis_summary_box and first_report_row_box and package_box and path_box and chain_box and evidence_rows_box
        assert canvas_box["height"] >= 154
        assert canvas_box["width"] >= 860
        assert rail_box["x"] > canvas_box["x"] + canvas_box["width"] - 8
        assert 250 <= rail_box["width"] <= 360
        assert package_box["y"] < rail_box["y"] < path_box["y"] < chain_box["y"]
        assert diagnosis_summary_box["height"] >= 26
        assert diagnosis_summary.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        assert 26 <= report_rows_box["height"] <= 44
        assert first_report_row_box["height"] >= 26
        assert first_report_title.evaluate("(element) => element.scrollWidth <= element.clientWidth + 1") is True
        assert report_rail.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        assert report_rows_box["height"] < package_box["height"]
        assert evidence_trace.evaluate("(element) => element.closest('#fault-sandbox-diagnosis-inspector') !== null") is True
        expect(evidence_trace.locator(".sandbox-evidence-trace-row:visible")).to_have_count(1)
        assert evidence_trace_box["x"] >= inspector_box["x"] - 1
        assert evidence_trace_box["x"] + evidence_trace_box["width"] <= inspector_box["x"] + inspector_box["width"] + 1
        assert evidence_trace_box["y"] > chain_box["y"]
        assert evidence_trace_box["height"] <= 94
        assert 26 <= evidence_rows_box["height"] <= 56
        assert inspector.evaluate("(element) => element.scrollHeight <= element.clientHeight + 1") is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_blueprint37_canvas_and_report_actions_share_visual_system(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )
        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )

        replay_canvas = page.locator("#fault-sandbox-replay-canvas-main")
        report_strip = page.locator("#sandbox-report-strip")
        report_rail = page.locator("#fault-sandbox-main-report-rail")
        expect(replay_canvas).to_have_attribute("data-blueprint37-density", "wide-replay-canvas")
        expect(report_strip).to_have_attribute("data-blueprint37-system", "replay-report-shared")
        expect(report_rail).to_have_attribute("data-blueprint37-system", "replay-report-shared")
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action]")).to_have_count(2)
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action='revision']")).to_have_text("生成报告")
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action='export']")).to_have_text("导出全部")
        expect(page.locator("#fault-sandbox-main-report-actions [data-main-report-action='export']")).to_have_attribute("data-report-primary-action", "review-package")

        canvas_box = replay_canvas.bounding_box()
        assert canvas_box
        assert canvas_box["height"] >= 154
        assert canvas_box["width"] >= 600
        assert canvas_box["width"] / canvas_box["height"] >= 3.0

        page.locator("#fault-sandbox-main-report-actions [data-main-report-action='export']").click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-invariants")).to_contain_text("truth_effect:none")
        page.locator("#sandbox-review-package-close").click()
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_prepare_and_sandbox_rows_share_density_scan_contract(
  demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirementsPayload, drawingPayload, faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirementsPayload));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawingPayload));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        matrix_rows = page.locator("#fault-candidate-matrix-body [data-row-scan-kind='fault-matrix']")
        expect(matrix_rows).to_have_count(1)
        matrix_row = matrix_rows.first
        expect(matrix_row).to_have_attribute("data-row-scan-contract", "id-status-evidence-link")
        for token in ["id", "status", "evidence", "link"]:
            expect(matrix_row.locator(f"[data-row-scan-token='{token}']")).to_be_visible()
        expect(matrix_row.locator("[data-row-scan-token='evidence']")).to_have_text("SRC-01")
        assert matrix_row.bounding_box()["height"] <= 60
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        review_row = page.locator("[data-blueprint-review-row='SR-06']")
        expect(page.locator("#fault-sandbox-review-rows [data-row-scan-kind='sandbox-review']")).to_have_count(7)
        expect(review_row).to_have_attribute("data-row-scan-contract", "id-status-evidence-link")
        for token in ["id", "status", "evidence", "link"]:
            expect(review_row.locator(f"[data-row-scan-token='{token}']")).to_be_visible()

        report_row = page.locator("[data-report-section-id='RP-06']")
        expect(page.locator("#fault-sandbox-report-section-rows [data-row-scan-kind='replay-report']")).to_have_count(7)
        expect(report_row).to_have_attribute("data-row-scan-contract", "id-status-evidence-link")
        for token in ["id", "status", "evidence", "link"]:
            expect(report_row.locator(f"[data-row-scan-token='{token}']")).to_be_visible()
        expect(report_row.locator("[data-row-scan-token='link'] [data-link-kind='trace']")).to_have_text("ET-04")
        assert report_row.bounding_box()["height"] <= 28
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_matrix_selection_carries_review_linkage_into_sandbox(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirementsPayload, drawingPayload, faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirementsPayload));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawingPayload));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        matrix_row = page.locator("#fault-candidate-matrix-body [data-row-scan-kind='fault-matrix']").first
        matrix_row.click()

        expect(matrix_row).to_have_class(re.compile("is-linked-active"))
        expect(matrix_row).to_have_attribute("data-linked-review-row", "SR-06")
        expect(matrix_row).to_have_attribute("data-linked-trace-id", "ET-04")
        expect(matrix_row).to_have_attribute("data-linked-report-id", "RP-06")
        summary = page.locator("#fault-context-link-summary")
        expect(summary).to_be_visible()
        expect(summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(summary).to_have_attribute("data-active-report-id", "RP-06")
        for token in ["沙盒预选", "SR-06", "ET-04", "RP-06", "sandbox_candidate", "truth_effect:none"]:
            expect(summary).to_contain_text(token)

        page.locator("#fault-context-close").click()
        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认 dry-run 演示边界。")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        page.locator("#fault-sandbox-next").click()
        page.wait_for_url(re.compile(r".*/fault-injection-sandbox\?review=SR-06&trace=ET-04&report=RP-06$"))

        review_row = page.locator("[data-blueprint-review-row='SR-06']")
        expect(review_row).to_have_attribute("aria-selected", "true")
        expect(review_row).to_have_class(re.compile("is-active"))
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_have_attribute("data-active-review-row", "SR-06")
        expect(page.locator("#fault-sandbox-affected-path")).to_have_attribute("data-linked-trace-id", "ET-04")
        expect(page.locator("[data-evidence-trace-id='ET-04']")).to_have_class(re.compile("is-linked-active"))
        expect(page.locator("[data-report-section-id='RP-06']")).to_have_class(re.compile("is-linked-active"))
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
    finally:
        page.close()


def test_fault_sandbox_active_review_package_summary_is_default_readable(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(
            f"{demo_server}/fault-injection-sandbox?review=SR-06&trace=ET-04&report=RP-06",
            wait_until="networkidle",
        )
        package_summary = page.locator("#fault-sandbox-review-package-summary")
        expect(package_summary).to_be_visible()
        expect(package_summary).to_have_attribute("data-blueprint-surface", "active-review-package-summary")
        expect(package_summary).to_have_attribute("data-package-state", "active")
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(package_summary.locator("[data-package-summary-token='review']")).to_have_text("SR-06")
        expect(package_summary.locator("[data-package-summary-token='trace']")).to_have_text("ET-04")
        expect(package_summary.locator("[data-package-summary-token='report']")).to_have_text("RP-06")
        for token in ["报告可追溯", "沙盒审查", "未决问题", "建议修复", "关键证据", "truth_effect:none", "controller_truth_modified:false"]:
            expect(package_summary).to_contain_text(token)
        expect(page.locator("#sandbox-review-package-panel")).to_be_hidden()
        package_summary_height = package_summary.bounding_box()["height"]
        assert 46 <= package_summary_height <= 54
        assert package_summary.evaluate(
            """(element) => {
              const summary = element.getBoundingClientRect();
              const inspector = document.querySelector("#fault-sandbox-diagnosis-inspector").getBoundingClientRect();
              return summary.bottom <= inspector.bottom;
            }"""
        ) is True
        assert page.evaluate("() => document.scrollingElement.scrollHeight <= window.innerHeight") is True

        page.locator('[data-blueprint-review-row="SR-07"]').click()
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-07")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-03")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-07")
        expect(package_summary).to_contain_text("未决风险")
        expect(package_summary).to_contain_text("控制真相未修改")

        page.locator("#sandbox-evidence-close").click()
        page.locator('[data-report-section-id="RP-06"]').click()
        expect(package_summary).to_have_attribute("data-active-review-row", "SR-06")
        expect(package_summary).to_have_attribute("data-active-trace-id", "ET-04")
        expect(package_summary).to_have_attribute("data-active-report-id", "RP-06")
        expect(page.locator('[data-blueprint-review-row="SR-06"]')).to_have_attribute("aria-selected", "true")
        assert page.evaluate("() => document.scrollingElement.scrollWidth <= window.innerWidth") is True
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_desktop_logic_builder_draws_cockpit_control_console_and_main_display(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="domcontentloaded")
        cockpit = page.locator('[data-ui-skin="demo-cockpit"]')
        console = page.locator('[data-cockpit-role="control-console"]')
        display = page.locator('[data-cockpit-role="primary-display"]')
        expect(cockpit).to_be_visible()
        expect(page.locator('[data-cockpit-role="canopy-frame"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="status-banner"]')).to_be_visible()
        expect(page.locator('[data-cockpit-role="mission-strip"]')).to_be_visible()
        expect(console).to_be_visible()
        expect(display).to_be_visible()
        expect(page.locator(".logic-cockpit-canopy-window")).to_have_count(3)
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is True
        for selector in [
            "#logic-circuit-tra",
            "#logic-circuit-ra",
            "#logic-circuit-n1k",
            "#logic-circuit-vdt",
        ]:
            expect(page.locator(selector)).to_be_visible()

        console_box = console.bounding_box()
        display_box = display.bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        assert console_box is not None
        assert display_box is not None
        assert canvas_box is not None
        assert display_box["y"] < console_box["y"]
        assert display_box["width"] >= 850
        assert canvas_box["height"] >= 360
    finally:
        page.close()


def test_fault_sandbox_source_deferred_replay_does_not_claim_config_generated(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    source_scope = {
        "fault_injection": {
            "status": "source_deferred",
            "reason_zh": "源文档声明故障注入本轮暂不考虑。",
        }
    }
    fault_payload = {
        **FAULT_PREPARATION,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入本轮暂不考虑。",
        "source_scope": source_scope,
        "fault_scenarios": [],
        "injection_points": [],
        "boundary_questions": [],
        "boundary_answers": [],
    }
    sandbox_payload = {
        **SANDBOX_PLAN,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入暂缓，未生成沙盒注入计划。",
        "source_scope": source_scope,
        "sandbox_injection_plan": [],
        "observation_points": [],
        "review_checklist": [],
    }
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [fault_payload, sandbox_payload],
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("源文档暂缓")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("未生成沙盒注入计划")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("源文档暂缓")
        expect(page.locator("#fault-sandbox-quality-summary")).to_contain_text("0 个沙盒计划")
        expect(page.locator("#fault-sandbox-revision-next")).to_be_disabled()
        for index in range(page.locator("input[data-sandbox-confirm]").count()):
            expect(page.locator("input[data-sandbox-confirm]").nth(index)).to_be_disabled()
    finally:
        page.close()


def test_fault_routes_first_visit_show_candidate_preview_without_seeded_storage(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("localStorage.clear()")
        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-result-summary")).to_contain_text("首次进入已载入本地蓝图候选预览")
        expect(page.locator("#fault-source-title")).to_have_text("蓝图候选预览")
        expect(page.locator("#fault-source-summary")).to_contain_text("不会调用模型")
        expect(page.locator("#fault-injection-workflow-stage")).to_have_text("蓝图候选预览")
        expect(page.locator("#fault-decision-candidate-summary")).to_have_text("2 scenarios · 2 points")
        expect(page.locator("#fault-boundary-progress")).to_have_text("2/2 已回答")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(2)
        assert page.locator("#fault-candidate-matrix-body .fault-matrix-path-token").count() >= 4

        preview_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                fault: {
                  first_visit_preview: fault.first_visit_preview,
                  candidate_state: fault.candidate_state,
                  truth_effect: fault.truth_effect,
                  certification_claim: fault.certification_claim,
                  controller_truth_modified: fault.controller_truth_modified,
                  model: fault.llm && fault.llm.model,
                },
                sandbox: {
                  first_visit_preview: sandbox.first_visit_preview,
                  candidate_state: sandbox.candidate_state,
                  truth_effect: sandbox.truth_effect,
                  certification_claim: sandbox.certification_claim,
                  controller_truth_modified: sandbox.controller_truth_modified,
                  execution_contract: sandbox.execution_contract,
                },
              };
            }"""
        )
        assert preview_contract == {
            "fault": {
                "first_visit_preview": True,
                "candidate_state": "fault_injection_preparation",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "model": "blueprint-candidate-preview",
            },
            "sandbox": {
                "first_visit_preview": True,
                "candidate_state": "sandbox_candidate",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
            },
        }

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("localStorage.clear()")
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="domcontentloaded")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("首次进入已载入本地蓝图沙盒预览")
        expect(page.locator("#fault-sandbox-source-title")).to_have_text("已载入故障准备草稿")
        expect(page.locator("#fault-sandbox-source-summary")).to_contain_text("首次进入已载入本地蓝图故障候选预览")
        expect(page.locator("#fault-sandbox-plan-count")).to_have_text("2 plans")
        expect(page.locator("#fault-sandbox-observation-count")).to_have_text("2 points")
        expect(page.locator("#fault-sandbox-review-count")).to_have_text("2 checks")
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 rows")
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node='failure-path']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")

        sandbox_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                faultFirstVisit: fault.first_visit_preview,
                sandboxFirstVisit: sandbox.first_visit_preview,
                candidateState: sandbox.candidate_state,
                truthEffect: sandbox.truth_effect,
                certificationClaim: sandbox.certification_claim,
                controllerTruthModified: sandbox.controller_truth_modified,
                executionContract: sandbox.execution_contract,
              };
            }"""
        )
        assert sandbox_contract == {
            "faultFirstVisit": True,
            "sandboxFirstVisit": True,
            "candidateState": "sandbox_candidate",
            "truthEffect": "none",
            "certificationClaim": "none",
            "controllerTruthModified": False,
            "executionContract": {"run_tick": False, "simulate": False, "dry_run_only": True},
        }
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_source_deferred_fault_path_can_load_blueprint_candidate_sandbox_preview(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    source_scope = {
        "fault_injection": {
            "status": "source_deferred",
            "reason_zh": "源文档声明故障注入本轮暂不考虑。",
            "source_anchors": [
                {"id": "B91", "kind": "范围约束", "origin": "docx_body", "quote_zh": "故障注入目前暂时不考虑，很复杂。"}
            ],
        }
    }
    requirements = {**REQUIREMENTS_READY, "source_scope": source_scope}
    fault_payload = {
        **FAULT_PREPARATION,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入本轮暂不考虑。",
        "source_scope": source_scope,
        "fault_scenarios": [],
        "injection_points": [],
        "boundary_questions": [],
        "boundary_answers": [],
    }
    sandbox_payload = {
        **SANDBOX_PLAN,
        "status": "source_deferred",
        "summary_zh": "源文档声明故障注入暂缓，未生成沙盒注入计划。",
        "source_scope": source_scope,
        "sandbox_injection_plan": [],
        "observation_points": [],
        "review_checklist": [],
    }
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [requirements, _circuit_view_drawing(), fault_payload, sandbox_payload],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        expect(page.locator("#fault-result-state")).to_have_text("源文档暂缓")
        expect(page.locator("#fault-source-defer")).to_be_visible()
        expect(page.locator("#fault-source-defer-summary")).to_contain_text("源文档声明故障注入本轮暂不考虑")
        expect(page.locator("#fault-blueprint-candidate-actions")).to_be_visible()
        expect(page.locator("#fault-load-blueprint-candidate")).to_be_enabled()
        page.click("#fault-load-blueprint-candidate")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-result-summary")).to_contain_text("蓝图候选演示已载入")
        expect(page.locator("#fault-blueprint-candidate-status")).to_have_text("已载入 sandbox candidate，不改变源文档范围")
        expect(page.locator("#fault-decision-candidate-summary")).to_have_text("2 scenarios · 2 points")
        expect(page.locator("#fault-boundary-progress")).to_have_text("2/2 已回答")
        expect(page.locator("#fault-decision-boundary-summary")).to_have_text("2/2 已回答")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("可进入沙盒")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("证据链和报告预览")
        expect(page.locator("#fault-candidate-matrix-panel")).to_be_visible()
        expect(page.locator("#fault-candidate-matrix-count")).to_have_text("2 rows")
        expect(page.locator(".fault-candidate-matrix[data-blueprint-density='compact-workbench']")).to_be_visible()
        expect(page.locator("#fault-candidate-matrix-body [data-fault-matrix-row]")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-fault-row='matrix']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-density='compact-workbench']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .blueprint-row--fault-matrix")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .blueprint-density-row")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-row-pattern='shared-v1']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='checkbox']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='injection-position']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='covered-path']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='risk']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col='state']")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-select input[disabled]")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-pathline")).to_have_count(2)
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-pathline").first).to_have_attribute(
            "data-blueprint39-detail", "selected-only"
        )
        expect(page.locator("#fault-candidate-matrix-body .fault-matrix-path-summary")).to_have_count(2)
        assert page.locator("#fault-candidate-matrix-body .fault-matrix-path-token").count() >= 4
        assert page.locator("#fault-candidate-matrix-body .blueprint-row-token").count() >= 6
        assert page.locator("#fault-candidate-matrix-body .blueprint-row-chip").count() >= 6
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']").first).to_have_attribute(
            "data-blueprint-columns", re.compile("covered-path")
        )
        fault_row_box = page.locator("#fault-candidate-matrix-body [data-blueprint-density='compact-workbench']").first.bounding_box()
        assert fault_row_box
        assert fault_row_box["height"] <= 60
        expect(page.locator("#fault-candidate-matrix-panel")).to_contain_text("覆盖路径")
        expect(page.locator("#fault-candidate-matrix-body")).to_contain_text("radio_altitude_ft")
        expect(page.locator(".fault-scenario-card")).to_have_count(2)
        expect(page.locator(".fault-point-card")).to_have_count(2)
        expect(page.locator("#fault-coverage-evidence-list .fault-coverage-row")).to_have_count(3)
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        preview_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                fault: {
                  ui_blueprint_preview: fault.ui_blueprint_preview,
                  candidate_state: fault.candidate_state,
                  truth_effect: fault.truth_effect,
                  certification_claim: fault.certification_claim,
                  controller_truth_modified: fault.controller_truth_modified,
                  model: fault.llm && fault.llm.model,
                },
                sandbox: {
                  ui_blueprint_preview: sandbox.ui_blueprint_preview,
                  candidate_state: sandbox.candidate_state,
                  truth_effect: sandbox.truth_effect,
                  certification_claim: sandbox.certification_claim,
                  controller_truth_modified: sandbox.controller_truth_modified,
                  execution_contract: sandbox.execution_contract,
                  completion_strategy: sandbox.plan_coverage_completion && sandbox.plan_coverage_completion.strategy,
                },
              };
            }"""
        )
        assert preview_contract == {
            "fault": {
                "ui_blueprint_preview": True,
                "candidate_state": "fault_injection_preparation",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "model": "blueprint-candidate-preview",
            },
            "sandbox": {
                "ui_blueprint_preview": True,
                "candidate_state": "sandbox_candidate",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
                "completion_strategy": "ui_blueprint_candidate_preview",
            },
        }

        page.click("#fault-sandbox-next")
        page.wait_for_url("**/fault-injection-sandbox")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("蓝图候选沙盒计划已载入")
        expect(page.locator("#fault-sandbox-contract")).to_contain_text("run_tick:false")
        expect(page.locator("#fault-sandbox-contract")).to_contain_text("simulate:false")
        expect(page.locator("#fault-sandbox-contract")).to_contain_text("dry_run_only:true")
        expect(page.locator("#fault-sandbox-plan-count")).to_have_text("2 plans")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")
        expect(page.locator(".sandbox-evidence-tile")).to_have_count(4)
        expect(page.locator("#fault-sandbox-review-row-panel")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 rows")
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-header")).to_be_visible()
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .blueprint-row--sandbox-review")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint-review-row]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review'] [data-blueprint-col='trace-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-link-token")).to_have_count(14)
        assert page.locator("#fault-sandbox-review-rows .blueprint-row-token").count() >= 21
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-blueprint-review-row='SR-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-review-rows .sandbox-review-row-check input[disabled]")).to_have_count(7)
        expect(page.locator("#fault-sandbox-review-rows")).to_contain_text("报告可追溯")
        expect(page.locator("#fault-sandbox-diagnosis-inspector")).to_be_visible()
        expect(page.locator("#fault-sandbox-diagnosis-summary")).to_contain_text("dry-run")
        expect(page.locator("#fault-sandbox-affected-path")).to_have_text("RA -> RA")
        expect(page.locator("#fault-sandbox-first-abnormal-node")).to_have_text("RA")
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node='failure-path']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .blueprint-row--diagnosis-chain")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain [data-blueprint-row-pattern='shared-v1']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-diagnosis-chain .sandbox-diagnosis-chain-link-token")).to_have_count(6)
        expect(page.locator("#fault-sandbox-diagnosis-evidence-links [data-blueprint36-evidence-link='diagnosis']")).to_have_count(3)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-row")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .blueprint-row--evidence-chain")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-link-token")).to_have_count(8)
        expect(page.locator("[data-evidence-trace-id='ET-04'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-evidence-trace-rows")).to_contain_text("报告预览")
        expect(page.locator("#fault-sandbox-report-preview")).to_be_visible()
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .blueprint-row--replay-report")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-report-row='review-package-section']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint-row-pattern='shared-v1']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-decision")).to_have_count(7)
        expect(page.locator("#fault-sandbox-report-section-rows .sandbox-report-link-token")).to_have_count(14)
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='trace']")).to_have_text("ET-04")
        expect(page.locator("[data-report-section-id='RP-06'] [data-link-kind='report']")).to_have_text("RP-06")
        expect(page.locator("#fault-sandbox-report-section-rows")).to_contain_text("沙盒审查")
        page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row").first.click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("report section")
        page.locator("#sandbox-evidence-close").click()
        expect(page.locator(".sandbox-review-item")).to_have_count(2)
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_hidden()
        expect(page.locator("#fault-sandbox-toggle-detail-panel")).to_have_attribute("aria-expanded", "false")
        page.click("#fault-sandbox-toggle-detail-panel")
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_visible()
        expect(page.locator("#fault-sandbox-toggle-detail-panel")).to_have_attribute("aria-expanded", "true")
        page.locator("#fault-sandbox-review-details > summary").click()
        expect(page.locator(".sandbox-review-item").first).to_be_visible()
        page.locator(".sandbox-review-item").first.click()
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-body")).to_contain_text("审查条件")
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_fault_prepare_defaults_to_candidate_boundary_decision_board(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        board = page.locator('[data-decision-board="fault-prepare"]')
        expect(board).to_be_visible()
        expect(board.locator(".fault-decision-card")).to_have_count(3)
        expect(board.locator('[data-fault-card="candidate"] h2')).to_have_text("候选状态")
        expect(board.locator('[data-fault-card="boundary"] h2')).to_have_text("边界确认")
        expect(board.locator('[data-fault-card="next"] h2')).to_have_text("下一步")
        expect(board.locator("#fault-decision-candidate-summary")).to_have_text("1 scenarios · 1 points")
        expect(board.locator("#fault-decision-boundary-summary")).to_have_text("0/2 已回答")
        expect(board.locator("#fault-decision-next-action")).to_contain_text("需完成边界确认")
        expect(page.locator("#fault-candidate-matrix-panel")).to_be_visible()
        expect(page.locator("#fault-candidate-matrix-count")).to_have_text("1 rows")
        expect(page.locator("#fault-candidate-matrix-body [data-fault-matrix-row]")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body .blueprint-row--fault-matrix")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-row-pattern='shared-v1']")).to_have_count(1)
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint-col]")).to_have_count(9)
        assert page.locator("#fault-candidate-matrix-body .fault-matrix-path-token").count() >= 2
        assert page.locator("#fault-candidate-matrix-body .blueprint-row-token").count() >= 3
        expect(page.locator("#fault-candidate-matrix-body")).to_contain_text("input_ra")
        expect(page.locator("#fault-candidate-details")).to_be_visible()
        expect(page.locator("#fault-injection-point-details")).to_be_visible()
        assert page.locator("#fault-candidate-details").evaluate("element => element.open") is False
        assert page.locator("#fault-injection-point-details").evaluate("element => element.open") is False

        board_box = board.bounding_box()
        assert board_box is not None
        assert board_box["height"] <= 132

        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认 dry-run 演示边界。")
        expect(board.locator("#fault-decision-boundary-summary")).to_have_text("2/2 已回答")
        expect(board.locator("#fault-decision-next-action")).to_contain_text("可进入沙盒")
        expect(board.locator("#fault-decision-next-action")).to_contain_text("候选矩阵")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
    finally:
        page.close()


def test_narrow_logic_builder_prioritizes_canvas_and_stream_before_engineering_rail(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        board_box = page.locator("#logic-detail-decision-board").bounding_box()
        stream_box = page.locator("#logic-drawing-stream-timeline").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        assert board_box is None
        assert stream_box is not None
        assert canvas_box is not None
        assert rail_box is not None
        assert stream_box["y"] < canvas_box["y"]
        assert canvas_box["y"] < rail_box["y"]
        assert canvas_box["y"] < 500
    finally:
        page.close()


def test_narrow_fault_prepare_prioritizes_decision_board_before_sidebar(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION],
        )

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        board_box = page.locator("#fault-decision-board").bounding_box()
        sidebar_box = page.locator(".fault-sidebar").bounding_box()
        candidate_box = page.locator("#fault-candidate-details").bounding_box()
        assert board_box is not None
        assert sidebar_box is not None
        assert candidate_box is not None
        assert board_box["y"] < sidebar_box["y"]
        assert board_box["y"] < candidate_box["y"]
        assert board_box["y"] < 760
    finally:
        page.close()


def test_narrow_fault_sandbox_prioritizes_review_gates_before_long_lists(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([faultPayload, sandboxPayload]) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandboxPayload));
            }""",
            [FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="domcontentloaded")
        gate_panel_box = page.locator(".sandbox-review-gate-panel").bounding_box()
        sidebar_box = page.locator(".sandbox-sidebar").bounding_box()
        details_box = page.locator("#fault-sandbox-detail-groups").bounding_box()
        revision_button_box = page.locator("#fault-sandbox-revision-next").bounding_box()
        assert gate_panel_box is not None
        assert sidebar_box is not None
        assert details_box is not None
        assert revision_button_box is not None
        assert revision_button_box["y"] < 760
        assert gate_panel_box["y"] < sidebar_box["y"]
        assert gate_panel_box["y"] < details_box["y"]
        assert gate_panel_box["y"] < 760
    finally:
        page.close()


def test_narrow_four_step_pages_share_first_screen_density(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    pages = [
        ("/requirements-intake", "#requirements-preflight-panel", 220),
        ("/logic-builder", "#logic-canvas", 520),
        ("/fault-injection-prepare", "#fault-decision-board", 300),
        ("/fault-injection-sandbox", ".sandbox-review-gate-panel", 220),
    ]
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        strip_heights: list[float] = []
        for path, first_screen_selector, max_first_screen_height in pages:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            strip_box = page.locator('[data-command-strip="deepseek-step"]').bounding_box()
            first_screen_box = page.locator(first_screen_selector).bounding_box()
            control_heights = page.locator(
                '[data-command-strip="deepseek-step"] select, '
                '[data-command-strip="deepseek-step"] button'
            ).evaluate_all("(nodes) => nodes.map((node) => node.getBoundingClientRect().height)")
            overflow_count = page.evaluate(
                """() => Array.from(document.querySelectorAll("body *")).filter((el) => {
                  const style = window.getComputedStyle(el);
                  return style.display !== "none"
                    && el.scrollWidth > el.clientWidth + 1
                    && style.overflowX !== "hidden";
                }).length"""
            )
            assert strip_box is not None
            assert first_screen_box is not None
            assert strip_box["height"] <= 116, path
            assert first_screen_box["y"] <= 500, path
            assert first_screen_box["height"] <= max_first_screen_height, path
            assert all(height <= 34 for height in control_heights), path
            assert overflow_count == 0, path
            strip_heights.append(strip_box["height"])

        assert max(strip_heights) - min(strip_heights) <= 48
    finally:
        page.close()


def test_phase1_blueprint_shell_defaults_fit_1366x768(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    pages = [
        "/requirements-intake",
        "/logic-builder",
        "/fault-injection-prepare",
        "/fault-injection-sandbox",
    ]
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        for path in pages:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            assert page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") <= 768, path
            strip_box = page.locator('[data-command-strip="deepseek-step"]').bounding_box()
            assert strip_box is not None
            assert strip_box["height"] <= 118, path

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        shell = page.locator(".logic-shell")
        expect(shell).to_have_attribute("data-blueprint-phase", "phase-1-shell")
        expect(page.locator("#logic-collapsed-tool-rail")).to_be_visible()
        expect(page.locator("#logic-right-inspector-rail")).to_be_visible()
        expect(page.locator("#logic-bottom-run-strip")).to_be_visible()
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()
        expect(page.locator("#logic-command-palette-open")).to_have_attribute(
            "data-blueprint-advanced-entry", "command-palette"
        )
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        assert shell.evaluate("el => !el.classList.contains('is-left-open') && !el.classList.contains('is-right-open')")

        page.click('#logic-collapsed-tool-rail [data-panel-toggle="left"]')
        assert shell.evaluate("el => el.classList.contains('is-left-open')")
        page.click('#logic-right-inspector-rail [data-panel-toggle="right"]')
        assert shell.evaluate("el => el.classList.contains('is-right-open')")
        expect(page.locator("#logic-object-context-drawer")).to_be_visible()

        page.click("#logic-command-palette-open")
        expect(page.locator("#logic-command-palette")).to_be_visible()
        for label in ["运行仿真", "打开参数抽屉", "单步回放", "注入故障", "打开失败路径", "导出审查包", "主画布专注", "收起全部面板"]:
            expect(page.locator("#logic-command-palette")).to_contain_text(label)
        page.click('[data-command-close-panels="true"]')
        assert shell.evaluate("el => !el.classList.contains('is-left-open') && !el.classList.contains('is-right-open')")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
    finally:
        page.close()


def test_panel_state_strategy_keeps_one_auxiliary_panel_open(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        logic_shell = page.locator(".logic-shell")
        expect(logic_shell).to_have_attribute("data-panel-strategy", "single-auxiliary")
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(logic_shell).to_have_attribute("data-workstation-state", "primary")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-run-parameter-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-command-palette")).to_be_hidden()
        expect(page.locator("#logic-command-palette")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()

        page.click('#logic-right-inspector-rail [data-panel-toggle="right"]')
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "right-inspector")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "right-inspector")
        expect(page.locator("#logic-object-context-drawer")).to_be_visible()
        expect(page.locator("#logic-object-context-drawer")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()

        page.click('#logic-mode-dock [data-logic-mode="parameters"]')
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "bottom-drawer")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "bottom-drawer")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_visible()
        expect(page.locator("#logic-run-parameter-drawer")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()
        expect(page.locator("#logic-object-context-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        assert logic_shell.evaluate("el => !el.classList.contains('is-left-open') && !el.classList.contains('is-right-open')")

        page.click("#logic-command-palette-open")
        expect(logic_shell).to_have_attribute("data-active-aux-panel", "command-palette")
        expect(logic_shell).to_have_attribute("data-unified-inspector-state", "command-palette")
        expect(page.locator("#logic-command-palette")).to_be_visible()
        expect(page.locator("#logic-command-palette")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#logic-run-parameter-drawer")).to_be_hidden()
        expect(page.locator("#logic-run-parameter-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#logic-object-context-drawer")).to_be_hidden()

        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="networkidle")
        fault_shell = page.locator(".fault-shell")
        expect(fault_shell).to_have_attribute("data-panel-strategy", "single-auxiliary")
        expect(fault_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(fault_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator('.fault-sidebar[data-unified-inspector="right-inspector"]')).to_be_visible()
        expect(page.locator("#fault-context-popover")).to_be_hidden()
        expect(page.locator("#fault-context-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.locator("#fault-candidate-matrix-body [data-blueprint-fault-row='matrix']").first.click()
        expect(fault_shell).to_have_attribute("data-active-aux-panel", "fault-context-popover")
        expect(fault_shell).to_have_attribute("data-unified-inspector-state", "fault-context-popover")
        expect(page.locator("#fault-context-popover")).to_be_visible()
        expect(page.locator("#fault-context-popover")).to_have_attribute("data-unified-panel-state", "open")

        page.click("#fault-context-close")
        expect(fault_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(fault_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#fault-context-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="networkidle")
        sandbox_shell = page.locator(".sandbox-shell")
        expect(sandbox_shell).to_have_attribute("data-panel-strategy", "single-auxiliary")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator('#fault-sandbox-diagnosis-inspector[data-unified-inspector="right-inspector"]')).to_be_visible()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_hidden()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_have_attribute("data-unified-panel-state", "closed")
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()
        expect(page.locator("#sandbox-evidence-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.click("#fault-sandbox-toggle-detail-panel")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "detail-drawer")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "detail-drawer")
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_visible()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()

        page.locator("#fault-sandbox-report-section-rows .sandbox-report-section-row").first.click()
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "evidence-popover")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "evidence-popover")
        expect(page.locator("#sandbox-evidence-popover")).to_be_visible()
        expect(page.locator("#sandbox-evidence-popover")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#fault-sandbox-detail-drawer")).to_be_hidden()
        expect(page.locator("#fault-sandbox-detail-drawer")).to_have_attribute("data-unified-panel-state", "closed")

        page.click("#sandbox-evidence-close")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#sandbox-evidence-popover")).to_have_attribute("data-unified-panel-state", "closed")

        page.click('[data-sandbox-report-action="export"]')
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "review-package")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "review-package")
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-panel")).to_have_attribute("data-unified-panel-state", "open")
        expect(page.locator("#sandbox-evidence-popover")).to_be_hidden()

        page.click("#sandbox-review-package-close")
        expect(sandbox_shell).to_have_attribute("data-active-aux-panel", "none")
        expect(sandbox_shell).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#sandbox-review-package-panel")).to_have_attribute("data-unified-panel-state", "closed")
    finally:
        page.close()


def test_logic_builder_blank_canvas_template_entry_can_seed_local_blueprint_candidate(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/draw-logic", reject_model_call)

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-blueprint27-rhythm", "compact-canvas")
        expect(page.locator("#logic-page-system-strip")).to_have_attribute("data-blueprint27-rhythm", "compact-topband")
        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        main_box = page.locator("main.logic-shell").bounding_box()
        assert strip_box is not None
        assert main_box is not None
        assert strip_box["height"] <= 84
        assert strip_box["y"] + strip_box["height"] - main_box["y"] <= 104
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()
        expect(page.locator("#logic-command-palette")).to_be_hidden()
        expect(page.locator('#logic-template-entry[data-blueprint29-rhythm="blank-canvas-template-entry"]')).to_be_visible()
        expect(page.locator("#logic-start-blank-canvas")).to_be_visible()
        expect(page.locator("#logic-load-docx-template")).to_be_visible()
        expect(page.locator("#logic-restore-recent-sandbox")).to_be_visible()
        expect(page.locator("#logic-drawing-stream-timeline")).to_be_hidden()
        expect(page.locator("#logic-reconstruction-mode-panel")).to_be_hidden()
        expect(page.locator("#logic-annotation-submit-bar")).to_be_hidden()
        assert page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") <= 768

        page.click("#logic-load-docx-template")
        expect(page.locator("#logic-template-entry")).to_be_hidden()
        expect(page.locator("#logic-result-state")).to_have_text("模型已完成绘制")
        expect(page.locator("#logic-bottom-run-node-count")).to_contain_text("节点 6/6")
        stored = page.evaluate(
            """
            () => {
              const payload = JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1"));
              return {
                truth_effect: payload.truth_effect,
                candidate_state: payload.candidate_state,
                certification_claim: payload.certification_claim,
                controller_truth_modified: payload.controller_truth_modified,
                node_count: payload.nodes.length,
                edge_count: payload.edges.length,
              };
            }
            """
        )
        assert stored == {
            "truth_effect": "none",
            "candidate_state": "sandbox_candidate",
            "certification_claim": "none",
            "controller_truth_modified": False,
            "node_count": 6,
            "edge_count": 5,
        }
        assert model_calls == []
    finally:
        page.close()


def test_docx_template_entry_carries_usage_path_cues_to_fault_and_sandbox(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1366, "height": 768})
    model_calls: list[str] = []
    tick_calls: list[str] = []
    try:
        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/draw-logic", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)
        page.route("**/api/tick", lambda route: (tick_calls.append(route.request.url), route.abort()))

        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate("() => localStorage.clear()")
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-template-entry")).to_be_visible()
        page.click("#logic-load-docx-template")
        expect(page.locator("#logic-template-entry")).to_be_hidden()
        expect(page.locator("#logic-result-state")).to_have_text("模型已完成绘制")
        expect(page.locator("#logic-result-summary")).to_contain_text("DOCX L1-L4")
        expect(page.locator("#logic-workflow-detail")).to_contain_text("故障矩阵")
        expect(page.locator("#logic-fault-next")).to_be_enabled()

        page.click("#logic-fault-next")
        page.wait_for_url("**/fault-injection-prepare")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-result-summary")).to_contain_text("DOCX L1-L4 模板候选")
        expect(page.locator("#fault-source-title")).to_have_text("DOCX L1-L4 模板候选")
        expect(page.locator("#fault-source-summary")).to_contain_text("来自逻辑绘制页")
        expect(page.locator("#fault-source-summary")).not_to_contain_text("未发现已保存图纸")
        expect(page.locator("#fault-injection-workflow-stage")).to_have_text("DOCX 模板候选")
        expect(page.locator("#fault-injection-workflow-detail")).to_contain_text("candidate-only 故障矩阵和沙盒入口")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("可进入沙盒")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("候选矩阵")
        expect(page.locator("#fault-decision-next-action")).to_contain_text("证据链和报告预览")
        expect(page.locator("#fault-candidate-matrix-body [data-blueprint33-row='fault-matrix']")).to_have_count(2)
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()

        template_contract = page.evaluate(
            """() => {
              const fault = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1"));
              const sandbox = JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1"));
              return {
                fault: {
                  template_preview: fault.template_preview,
                  first_visit_preview: Boolean(fault.first_visit_preview),
                  candidate_state: fault.candidate_state,
                  truth_effect: fault.truth_effect,
                  certification_claim: fault.certification_claim,
                  controller_truth_modified: fault.controller_truth_modified,
                  source_status: fault.source_scope && fault.source_scope.fault_injection && fault.source_scope.fault_injection.status,
                },
                sandbox: {
                  template_preview: sandbox.template_preview,
                  first_visit_preview: Boolean(sandbox.first_visit_preview),
                  candidate_state: sandbox.candidate_state,
                  truth_effect: sandbox.truth_effect,
                  certification_claim: sandbox.certification_claim,
                  controller_truth_modified: sandbox.controller_truth_modified,
                  execution_contract: sandbox.execution_contract,
                },
              };
            }"""
        )
        assert template_contract == {
            "fault": {
                "template_preview": True,
                "first_visit_preview": False,
                "candidate_state": "fault_injection_preparation",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "source_status": "ui_template_preview",
            },
            "sandbox": {
                "template_preview": True,
                "first_visit_preview": False,
                "candidate_state": "sandbox_candidate",
                "truth_effect": "none",
                "certification_claim": "none",
                "controller_truth_modified": False,
                "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
            },
        }

        page.click("#fault-sandbox-next")
        page.wait_for_url("**/fault-injection-sandbox")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("DOCX L1-L4 模板候选沙盒计划已载入")
        expect(page.locator("#fault-sandbox-source-summary")).to_contain_text("DOCX L1-L4 模板候选已接入故障矩阵")
        expect(page.locator("#fault-sandbox-decision-next-action")).to_contain_text("确认后用审查包和回放报告")
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 rows")
        expect(page.locator("#fault-sandbox-review-rows [data-blueprint36-row='sandbox-review']")).to_have_count(7)
        expect(page.locator("#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row='evidence-chain']")).to_have_count(4)
        expect(page.locator("#fault-sandbox-report-section-rows [data-blueprint36-report-row='replay-report']")).to_have_count(7)

        page.click("#fault-sandbox-generate")
        expect(page.locator("#fault-sandbox-result-summary")).to_contain_text("DOCX L1-L4 模板候选沙盒计划已刷新")
        expect(page.locator("#fault-sandbox-review-row-count")).to_have_text("7 rows")
        expect(page.locator("#fault-sandbox-decision-next-action")).to_contain_text("确认后用审查包和回放报告")

        page.click('[data-sandbox-report-action="export"]')
        expect(page.locator("#sandbox-review-package-panel")).to_be_visible()
        expect(page.locator("#sandbox-review-package-review-count")).to_have_text("7 review rows")
        expect(page.locator("#sandbox-review-package-invariants")).to_contain_text("truth_effect:none")
        assert model_calls == []
        assert tick_calls == []
    finally:
        page.close()


def test_desktop_four_step_pages_prioritize_primary_decision_surfaces(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    pages = [
        ("/requirements-intake", "#requirements-preflight-panel", 230, 220),
        ("/logic-builder", "#logic-canvas", 330, 620),
        ("/fault-injection-prepare", "#fault-decision-board", 360, 150),
        ("/fault-injection-sandbox", ".sandbox-review-gate-panel", 620, 380),
    ]
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing, fault, sandbox]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(fault));
              localStorage.setItem("ai-fantui-fault-injection-sandbox-plan-v1", JSON.stringify(sandbox));
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing(), FAULT_PREPARATION, _dense_sandbox_plan()],
        )

        for path, primary_selector, max_y, max_height in pages:
            page.goto(f"{demo_server}{path}", wait_until="networkidle")
            strip_box = page.locator('[data-command-strip="deepseek-step"]').bounding_box()
            primary_box = page.locator(primary_selector).bounding_box()
            overflow_count = page.evaluate(
                """() => Array.from(document.querySelectorAll("body *")).filter((el) => {
                  const style = window.getComputedStyle(el);
                  return style.display !== "none"
                    && el.scrollWidth > el.clientWidth + 1
                    && style.overflowX !== "hidden";
                }).length"""
            )
            assert strip_box is not None
            assert primary_box is not None
            assert strip_box["height"] <= 118, path
            assert primary_box["y"] <= max_y, path
            assert primary_box["height"] <= max_height, path
            assert overflow_count == 0, path
            assert page.evaluate("() => Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)") <= 820, path
    finally:
        page.close()


def test_deepseek_visual_acceptance_script_generates_first_screen_bundle(
    demo_server: str, tmp_path: Path
) -> None:
    artifact_dir = tmp_path / "deepseek-visual-acceptance"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/deepseek_ui_visual_acceptance.py",
            "--base-url",
            demo_server,
            "--artifact-dir",
            str(artifact_dir),
        ],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    summary_path = artifact_dir / "visual-acceptance-summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["kind"] == "deepseek-ui-visual-acceptance"
    assert summary["ok"] is True
    assert summary["route_count"] == 5
    assert summary["screenshot_count"] == 10
    assert len(list(artifact_dir.glob("*.png"))) == 10

    routes = {entry["route"] for entry in summary["pages"]}
    assert routes == {
        "/requirements-intake",
        "/logic-builder",
        "/fault-injection-prepare",
        "/fault-injection-sandbox",
    }
    route_keys = {entry["route_key"] for entry in summary["pages"]}
    assert route_keys == {
        "requirements-intake",
        "logic-builder",
        "fault-injection-prepare",
        "fault-injection-sandbox-default",
        "fault-injection-sandbox",
    }
    for entry in summary["pages"]:
        assert entry["missing_visible_surfaces"] == [], entry
        assert entry["missing_existing_surfaces"] == [], entry
        assert entry["geometry"]["vertical_scroll_ok"] is True, entry
        assert entry["geometry"]["horizontal_overflow_count"] == 0, entry
        assert entry["screenshot"].endswith(".png")


def test_deepseek_v4_pro_ui_workbench_demo_flow_without_canvas_mainline(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    geometry: list[dict[str, Any]] = []
    try:
        _install_model_routes(page)

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        geometry.append(_assert_deepseek_page_contract(page, "requirements-intake"))
        expect(page.locator("#requirements-provider")).to_have_value("deepseek")
        page.fill("#requirements-text", "RA 小于 6ft 且 TRA/SW1/SW2/EEC 条件满足时，释放油门锁。")
        page.click("#requirements-analyze")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#logic-builder-next")).to_be_enabled()
        _screenshot(page, "01-requirements-intake-ready")

        page.click("#logic-builder-next")
        page.wait_for_url("**/logic-builder")
        expect(page.locator("#logic-result-state")).to_have_text("电路图已完成绘制")
        expect(page.locator("#logic-canvas-counts")).to_contain_text("20 circuit nodes")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        assert page.locator("#logic-circuit-status-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("DEPLOYED")
        expect(page.locator('[data-demo-node-id="thr_lock"]')).to_have_attribute("data-state", "active")
        geometry.append(_assert_deepseek_page_contract(page, "logic-builder"))
        _screenshot(page, "02-logic-builder-drawing")

        page.click("#logic-fault-next")
        page.wait_for_url("**/fault-injection-prepare")
        expect(page.locator("#fault-result-state")).to_have_text("候选已生成")
        expect(page.locator("#fault-scenario-count")).to_have_text("1 scenarios")
        expect(page.locator("#fault-coverage-evidence")).to_be_hidden()
        expect(page.locator("#fault-coverage-evidence")).to_contain_text("自动补齐证据")
        expect(page.locator("#fault-coverage-evidence")).to_contain_text("thr_lock_rel")
        for index in range(page.locator("textarea[data-boundary-id]").count()):
            page.locator("textarea[data-boundary-id]").nth(index).fill("确认 dry-run 演示边界。")
        expect(page.locator("#fault-sandbox-next")).to_be_enabled()
        geometry.append(_assert_deepseek_page_contract(page, "fault-injection-prepare"))
        _screenshot(page, "03-fault-injection-prepare")

        page.click("#fault-sandbox-next")
        page.wait_for_url("**/fault-injection-sandbox")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("需确认 3 个一级闸门")
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_be_hidden()
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_contain_text("自动补齐证据")
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_contain_text("auto_fault_thr_lock_rel")
        for index in range(page.locator("input[data-sandbox-confirm]").count()):
            page.locator("input[data-sandbox-confirm]").nth(index).check()
        expect(page.locator("#fault-sandbox-review-gate")).to_have_text("可进入逻辑修订")
        geometry.append(_assert_deepseek_page_contract(page, "fault-injection-sandbox"))
        _screenshot(page, "04-fault-injection-sandbox")

        page.click("#fault-sandbox-revision-next")
        page.wait_for_url("**/logic-builder")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "change")
        expect(page.locator('#logic-workbench-drawers [data-workbench-tab="change"]')).to_have_attribute(
            "aria-selected",
            "true",
        )
        expect(page.locator("#logic-revision-handoff")).to_be_visible()
        expect(page.locator("#logic-revision-handoff-title")).to_have_text("来自沙盒审查")
        geometry.append(_assert_deepseek_page_contract(page, "logic-builder"))
        _screenshot(page, "05-logic-builder-revision-handoff")
    finally:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        (ARTIFACT_DIR / "geometry-evidence.json").write_text(
            json.dumps(geometry, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        page.close()


def test_deepseek_ui_reports_live_key_and_submits_live_only_request(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 840})
    captured_requests: list[dict[str, Any]] = []
    try:
        page.route(
            "**/api/requirements-intake/provider-status?provider=deepseek",
            lambda route: _fulfill_json(
                route,
                {
                    "provider": "deepseek",
                    "model": "deepseek-v4-pro",
                    "api_base": "https://api.deepseek.com",
                    "key_available": True,
                    "key_source": "env:DEEPSEEK_API_KEY",
                    "live_ready": True,
                },
            ),
        )

        def capture_analyze(route: Any) -> None:
            captured_requests.append(json.loads(route.request.post_data or "{}"))
            _fulfill_json(route, REQUIREMENTS_READY)

        page.route("**/api/requirements-intake/analyze", capture_analyze)
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-provider-status")).to_contain_text("DeepSeek 已接入")
        expect(page.locator("#requirements-provider-key-source")).to_contain_text("env:DEEPSEEK_API_KEY")
        expect(page.locator("#requirements-live-only")).to_be_checked()

        page.fill("#requirements-text", "RA 小于 6ft 且 TRA/SW1/SW2/EEC 条件满足时，释放油门锁。")
        page.click("#requirements-analyze")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
    finally:
        page.close()

    assert captured_requests
    assert captured_requests[0]["provider"] == "deepseek"
    assert captured_requests[0]["allow_fallback"] is False


def test_requirements_intake_renders_local_preparse_before_deepseek_enhancement(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    calls: list[str] = []
    pending_deepseek_routes: list[Any] = []
    local_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "本地预解析已先产出 L1-L4 结构。",
        "llm": {"provider": "local-preparse", "response_source": "deterministic_preparse"},
        "deterministic_preparse": {
            "available": True,
            "applied": True,
            "reason": "local_preparse_first",
        },
        "concept_logic_nodes": [{"id": f"local_{index}", "label": f"L{index}", "node_kind": "logic"} for index in range(1, 14)],
        "concept_edges": [{"source": f"local_{index}", "target": f"local_{index + 1}", "label": "local"} for index in range(1, 13)],
    }
    deepseek_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "DeepSeek 增强结果已刷新。",
        "concept_logic_nodes": REQUIREMENTS_READY["concept_logic_nodes"] + [
            {"id": "deepseek_extra", "label": "VDT", "node_kind": "component"},
        ],
    }
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": True,
            "key_source": "env:DEEPSEEK_API_KEY",
            "live_ready": True,
        }))

        def fulfill_local(route: Any) -> None:
            calls.append("local")
            _fulfill_json(route, local_payload)

        def fulfill_deepseek(route: Any) -> None:
            calls.append("deepseek")
            pending_deepseek_routes.append(route)

        page.route("**/api/requirements-intake/local-preparse", fulfill_local)
        page.route("**/api/requirements-intake/analyze", fulfill_deepseek)

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        stream = page.locator("#requirements-generation-stream")
        expect(stream).to_be_attached()
        expect(stream.locator("[data-stream-step]")).to_have_count(4)
        expect(stream.locator("[data-stream-step='read']")).to_have_attribute("data-state", "idle")

        page.fill("#requirements-text", "RA 小于 6ft，SW1/SW2 有效，TRA 进入反推区，VDT 90%。")
        page.click("#requirements-analyze")
        expect(stream).to_be_visible()

        expect(page.locator("#requirements-status")).to_have_text("本地预解析已就绪")
        expect(page.locator("#requirements-summary")).to_have_text("本地预解析已先产出 L1-L4 结构。")
        expect(page.locator("#graph-counts")).to_have_text("13 nodes · 12 edges")
        expect(stream.locator("[data-stream-step='read']")).to_have_attribute("data-state", "complete")
        expect(stream.locator("[data-stream-step='parse']")).to_have_attribute("data-state", "complete")
        expect(stream.locator("[data-stream-step='send']")).to_have_attribute("data-state", "active")
        expect(page.locator("#process-title")).to_have_text("本地预解析已就绪")

        assert pending_deepseek_routes
        _fulfill_json(pending_deepseek_routes.pop(0), deepseek_payload)
        expect(page.locator("#requirements-summary")).to_have_text("DeepSeek 增强结果已刷新。")
        expect(page.locator("#requirements-status")).to_have_text("完成")
        expect(stream.locator("[data-stream-step='render']")).to_have_attribute("data-state", "complete")
        expect(page.locator("#process-title")).to_have_text("分析完成")
    finally:
        page.close()

    assert calls == ["local", "deepseek"]


def test_requirements_intake_missing_key_uses_local_preparse_without_live_call(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    calls: list[str] = []
    local_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "本地预解析已生成可继续的 L1-L4 候选。",
        "llm": {"provider": "local-preparse", "response_source": "deterministic_preparse"},
        "deterministic_preparse": {"available": True, "applied": True, "reason": "local_preparse_first"},
        "concept_logic_nodes": [{"id": f"local_{index}", "label": f"L{index}", "node_kind": "logic"} for index in range(1, 14)],
        "concept_edges": [{"source": f"local_{index}", "target": f"local_{index + 1}", "label": "local"} for index in range(1, 13)],
    }
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": False,
            "key_source": "",
            "live_ready": False,
            "checked": ["DEEPSEEK_API_KEY"],
        }))

        def fulfill_local(route: Any) -> None:
            calls.append("local")
            _fulfill_json(route, local_payload)

        def reject_live(route: Any) -> None:
            calls.append("deepseek")
            route.fulfill(status=503, content_type="application/json", body='{"error":"missing_api_key"}')

        page.route("**/api/requirements-intake/local-preparse", fulfill_local)
        page.route("**/api/requirements-intake/analyze", reject_live)

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-preflight-panel")).to_be_visible()
        expect(page.locator("#requirements-preflight-live-state")).to_have_text("未接入")
        expect(page.locator("#requirements-analyze")).to_have_text("检查：本地预解析")
        page.fill("#requirements-text", "RA 小于 6ft，SW1/SW2 有效，TRA 进入反推区，VDT 90%。")
        page.click("#requirements-analyze")

        expect(page.locator("#requirements-status")).to_have_text("本地候选可继续")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#requirements-summary")).to_have_text("本地预解析已生成可继续的 L1-L4 候选。")
        expect(page.locator("#graph-counts")).to_have_text("13 nodes · 12 edges")
        expect(page.locator("#logic-builder-next")).to_be_enabled()
    finally:
        page.close()

    assert calls == ["local"]


def test_requirements_intake_preserves_local_candidate_when_deepseek_enhancement_fails(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    local_payload = {
        **REQUIREMENTS_READY,
        "summary_zh": "本地预解析已先产出 L1-L4 结构。",
        "llm": {"provider": "local-preparse", "response_source": "deterministic_preparse"},
        "deterministic_preparse": {"available": True, "applied": True, "reason": "local_preparse_first"},
        "concept_logic_nodes": [{"id": f"local_{index}", "label": f"L{index}", "node_kind": "logic"} for index in range(1, 14)],
        "concept_edges": [{"source": f"local_{index}", "target": f"local_{index + 1}", "label": "local"} for index in range(1, 13)],
    }
    try:
        page.route("**/api/requirements-intake/provider-status?provider=deepseek", lambda route: _fulfill_json(route, {
            "provider": "deepseek",
            "model": "deepseek-v4-pro",
            "api_base": "https://api.deepseek.com",
            "key_available": True,
            "key_source": "env:DEEPSEEK_API_KEY",
            "live_ready": True,
        }))
        page.route("**/api/requirements-intake/local-preparse", lambda route: _fulfill_json(route, local_payload))
        page.route(
            "**/api/requirements-intake/analyze",
            lambda route: route.fulfill(
                status=503,
                content_type="application/json",
                body='{"error":"missing_api_key"}',
            ),
        )

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        page.fill("#requirements-text", "RA 小于 6ft，SW1/SW2 有效，TRA 进入反推区，VDT 90%。")
        page.click("#requirements-analyze")

        expect(page.locator("#requirements-status")).to_have_text("DeepSeek 增强失败")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#process-title")).to_have_text("DeepSeek 增强失败，可稍后重试")
        expect(page.locator("#requirements-summary")).to_have_text("本地预解析已先产出 L1-L4 结构。")
        expect(page.locator("#graph-counts")).to_have_text("13 nodes · 12 edges")
        expect(page.locator("#logic-builder-next")).to_be_enabled()
    finally:
        page.close()


def test_requirements_intake_preflight_imports_replay_and_hydrates_draft(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    model_calls: list[str] = []
    try:
        page.route("**/api/requirements-intake/deepseek-live-demo-replay", lambda route: _fulfill_json(route, _replay_payload()))

        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/analyze", reject_model_call)
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-replay-import")).to_be_visible()
        page.click("#requirements-replay-import")

        expect(page.locator("#requirements-status")).to_have_text("回放已导入")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#graph-counts")).to_have_text("3 nodes · 2 edges")
        expect(page.locator("#logic-builder-next")).to_be_enabled()

        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-status")).to_have_text("已恢复回放草稿")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#graph-counts")).to_have_text("3 nodes · 2 edges")
        assert model_calls == []
    finally:
        page.close()


def test_logic_builder_circuit_view_uses_demo_snapshot_presets(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-canvas-counts")).to_contain_text("20 circuit nodes")
        assert page.locator("#logic-circuit-status-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")

        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-preset-status")).to_contain_text("最大反推")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("DEPLOYED")
        expect(page.locator('[data-demo-node-id="thr_lock"]')).to_have_attribute("data-state", "active")
        expect(page.locator('.logic-circuit-wire[data-source="logic4"][data-target="thr_lock"]')).to_have_attribute(
            "data-state",
            "active",
        )

        page.select_option("#logic-circuit-preset-select", "inhibit-block")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("FAULT")
        expect(page.locator('.logic-circuit-wire[data-source="reverser_inhibited"][data-target="logic1"]')).to_have_attribute(
            "data-state",
            "fault",
        )
    finally:
        page.close()


def test_logic_builder_shows_demo_reconstruction_mode_and_concept_mode_warning(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-reconstruction-mode-panel")).to_be_visible()
        expect(page.locator("#logic-reconstruction-mode")).to_have_text("当前模式：演示舱一致电路图")
        expect(page.locator("#logic-reconstruction-fidelity")).to_have_text("链路覆盖：20/20 节点 · 23/23 连线")
        expect(page.locator("#logic-demo-bridge")).to_have_text("打开对齐视图")
        expect(page.locator("#logic-demo-bridge")).to_have_attribute("href", "/demo-reconstruction")
        assert page.locator("#logic-demo-bridge").get_attribute("data-primary-next-action") is None

        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            LOGIC_DRAWING,
        )
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-reconstruction-mode")).to_have_text("当前模式：概念图，尚未对齐演示舱电路")
        expect(page.locator("#logic-reconstruction-fidelity")).to_have_text("链路覆盖：未启用")
        expect(page.locator("#logic-demo-bridge")).to_have_text("打开对照视图")
        expect(page.locator("#logic-canvas-counts")).to_have_text("3 nodes · 2 edges · 1 panels")
    finally:
        page.close()


def test_demo_reconstruction_comparison_page_shows_original_and_current_replica(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        page.click("#logic-demo-bridge")
        page.wait_for_url("**/demo-reconstruction")
        page.wait_for_load_state("networkidle")

        expect(page.locator("#demo-reconstruction-original-frame")).to_be_visible()
        expect(page.locator("#demo-reconstruction-current-panel")).to_be_visible()
        expect(page.locator("#demo-reconstruction-mode")).to_have_text("当前模式：demo.html 高保真复刻")
        expect(page.locator("#demo-reconstruction-fidelity")).to_have_text("复刻度：20/20 节点 · 23/23 连线")
        expect(page.locator("#demo-reconstruction-comparison-table")).to_contain_text("节点")
        expect(page.locator("#demo-reconstruction-comparison-table")).to_contain_text("连线")
        expect(page.locator("#demo-reconstruction-comparison-table")).to_contain_text("预设场景")
        expect(page.locator("#demo-reconstruction-comparison-table")).to_contain_text("状态输出")
        expect(page.locator("#demo-reconstruction-preset-list")).to_contain_text("着陆展开")
        expect(page.locator("#demo-reconstruction-status-list")).to_contain_text("THR_LOCK")
        expect(page.locator("#demo-reconstruction-node-list li")).to_have_count(20)
        expect(page.locator("#demo-reconstruction-wire-list li")).to_have_count(23)

        original_box = page.locator("#demo-reconstruction-original-frame").bounding_box()
        current_box = page.locator("#demo-reconstruction-current-panel").bounding_box()
        assert original_box is not None and current_box is not None
        assert original_box["width"] > 360
        assert current_box["width"] > 360
    finally:
        page.close()


def test_deepseek_workflow_streams_chunks_before_model_final_response(
    demo_server: str,
    browser: Any,
) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    try:
        logic_routes: list[Any] = []
        page.route("**/api/requirements-intake/draw-logic", lambda route: logic_routes.append(route))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(requirements) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.removeItem("ai-fantui-logic-builder-drawing-v1");
              localStorage.removeItem("ai-fantui-fault-injection-preparation-v1");
              localStorage.removeItem("ai-fantui-fault-injection-sandbox-plan-v1");
            }""",
            REQUIREMENTS_READY,
        )
        page.goto(f"{demo_server}/logic-builder", wait_until="domcontentloaded")
        expect(page.locator("#logic-stream-chunks")).to_be_visible()
        expect(page.locator('#logic-stream-chunks [data-stream-chunk="load"]')).to_contain_text("已读取需求")
        expect(page.locator('#logic-stream-chunks [data-stream-chunk="model"]')).to_contain_text("DeepSeek 正在绘制")
        expect(page.locator("#logic-step-model")).to_have_attribute("data-state", "active")
        assert logic_routes
        _fulfill_json(logic_routes.pop(0), _circuit_view_drawing())
        expect(page.locator('#logic-stream-chunks [data-stream-chunk="render"]')).to_contain_text("渲染电路")

        fault_routes: list[Any] = []
        page.route("**/api/requirements-intake/prepare-fault-injection", lambda route: fault_routes.append(route))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-fault-injection-preparation-v1");
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing()],
        )
        page.goto(f"{demo_server}/fault-injection-prepare", wait_until="domcontentloaded")
        expect(page.locator('#fault-stream-chunks [data-stream-chunk="load"]')).to_contain_text("已读取图纸")
        expect(page.locator('#fault-stream-chunks [data-stream-chunk="model"]')).to_contain_text("DeepSeek 正在准备")
        expect(page.locator("#fault-step-model")).to_have_attribute("data-state", "active")
        assert fault_routes
        _fulfill_json(fault_routes.pop(0), FAULT_PREPARATION)
        expect(page.locator('#fault-stream-chunks [data-stream-chunk="boundary"]')).to_contain_text("边界确认")

        sandbox_routes: list[Any] = []
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", lambda route: sandbox_routes.append(route))
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(faultPayload) => {
              localStorage.setItem("ai-fantui-fault-injection-preparation-v1", JSON.stringify(faultPayload));
              localStorage.removeItem("ai-fantui-fault-injection-sandbox-plan-v1");
            }""",
            FAULT_PREPARATION,
        )
        page.goto(f"{demo_server}/fault-injection-sandbox", wait_until="domcontentloaded")
        expect(page.locator('#sandbox-stream-chunks [data-stream-chunk="load"]')).to_contain_text("已读取准备")
        expect(page.locator('#sandbox-stream-chunks [data-stream-chunk="model"]')).to_contain_text("DeepSeek 正在配置")
        expect(page.locator("#fault-sandbox-step-model")).to_have_attribute("data-state", "active")
        assert sandbox_routes
        _fulfill_json(sandbox_routes.pop(0), SANDBOX_PLAN)
        expect(page.locator('#sandbox-stream-chunks [data-stream-chunk="review"]')).to_contain_text("审查清单")
    finally:
        page.close()


def test_logic_builder_circuit_inputs_default_to_compact_details(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-circuit-status-badge")).to_be_visible()
        expect(page.locator("#logic-circuit-preset-select")).to_be_visible()
        expect(page.locator('#logic-circuit-preset-select option[value="max-reverse"]')).to_have_text("最大反推")
        expect(page.locator("button[data-circuit-preset]")).to_have_count(0)
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-circuit-tra")).to_be_hidden()
        expect(page.locator("#logic-circuit-engine-running")).to_be_hidden()
        expect(page.locator("#logic-circuit-status-details")).to_be_hidden()

        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("DEPLOYED")
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is False

        page.click("#logic-circuit-input-details > summary")
        expect(page.locator("#logic-circuit-tra")).to_be_visible()
        expect(page.locator("#logic-circuit-engine-running")).to_be_visible()
        expect(page.locator("#logic-circuit-status-details")).to_be_visible()
        page.locator("#logic-circuit-tra").evaluate(
            """(input) => {
              input.value = "-15";
              input.dispatchEvent(new Event("input", {bubbles: true}));
              input.dispatchEvent(new Event("change", {bubbles: true}));
            }"""
        )
        expect(page.locator("#logic-circuit-tra-value")).to_have_text("-15.0°")
    finally:
        page.close()


def test_logic_builder_left_rail_merges_source_status_and_trust_counts(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    drawing = _circuit_view_drawing()
    for node in drawing["circuit_view"]["nodes"]:
        if node["id"] == "radio_altitude_ft":
            node["source_anchors"] = [{"id": "B81", "kind": "正文条件", "quote_zh": "飞机离地小于6ft时"}]
            break
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-engineering-rail")).to_be_visible()
        expect(page.locator("#logic-engineering-rail #logic-status-rail")).to_be_visible()
        expect(page.locator("#logic-engineering-rail #logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-status-rail [data-status-rail-section]")).to_have_count(3)
        expect(page.locator('#logic-status-rail [data-status-rail-section="trust"]')).to_be_visible()
        expect(page.locator('#logic-status-rail [data-status-rail-section="source"]')).to_be_hidden()
        expect(page.locator('#logic-status-rail [data-status-rail-section="drawing"]')).to_be_hidden()
        expect(page.locator("#logic-rail-detail-details")).to_be_visible()
        assert page.locator("#logic-rail-detail-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-status-source-count")).to_have_text("1")
        expect(page.locator("#logic-status-local-count")).to_have_text("19")
        expect(page.locator("#logic-status-assumption-count")).to_have_text("0")
        expect(page.locator("#logic-source-trust-summary")).to_have_text("来源覆盖已确认")
        expect(page.locator("#logic-circuit-core-inputs")).to_be_visible()
        expect(page.locator("#logic-circuit-core-inputs [data-core-input]")).to_have_count(4)
        expect(page.locator('[data-core-input="tra"]')).to_contain_text("TRA")
        expect(page.locator('[data-core-input="ra"]')).to_contain_text("RA")
        expect(page.locator('[data-core-input="n1k"]')).to_contain_text("N1K")
        expect(page.locator('[data-core-input="vdt"]')).to_contain_text("VDT")
        expect(page.locator("#logic-circuit-preset-menu")).to_be_visible()
        expect(page.locator("#logic-circuit-preset-select")).to_be_visible()
        expect(page.locator("button[data-circuit-preset]")).to_have_count(0)
        expect(page.locator("#logic-circuit-input-details")).to_be_visible()
        assert page.locator("#logic-circuit-input-details").evaluate("element => element.open") is False
        expect(page.locator("#logic-circuit-tra")).to_be_hidden()

        direct_panels = page.eval_on_selector_all(
            "aside.logic-inspector > section.logic-panel",
            """(panels) => panels.map((panel) => ({
              id: panel.id || "",
              text: panel.innerText,
            }))""",
        )
        assert [panel["id"] for panel in direct_panels] == ["logic-engineering-rail"]
        direct_kickers = page.eval_on_selector_all(
            "aside.logic-inspector > section.logic-panel > .logic-kicker",
            "(kickers) => kickers.map((kicker) => kicker.textContent.trim())",
        )
        assert direct_kickers == ["ENGINEERING RAIL"]
        for old_kicker in ("INPUT", "MODEL OUTPUT", "READING LOAD"):
            assert old_kicker not in direct_kickers

        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        assert rail_box is not None
        assert rail_box["height"] <= 455
    finally:
        page.close()


def test_logic_builder_detail_area_defaults_to_three_decision_cards(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1200, "height": 820})
    drawing = _circuit_view_drawing()
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        board = page.locator('[data-decision-board="logic-details"]')
        expect(board).to_be_hidden()
        expect(board.locator(".logic-detail-card")).to_have_count(3)
        expect(board.locator('[data-detail-card="selection"] h2')).to_have_text("当前选择")
        expect(board.locator('[data-detail-card="source"] h2')).to_have_text("来源判断")
        expect(board.locator('[data-detail-card="next"] h2')).to_have_text("下一步")
        expect(board.locator("#logic-detail-selected-node")).to_have_text("未选择")
        expect(board.locator("#logic-detail-source-summary")).to_have_text("来源覆盖已确认")
        expect(board.locator("#logic-detail-next-action")).to_contain_text("THR_LOCK")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-drawing-notes-details")).to_be_hidden()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
        expect(page.locator("#logic-change-history-details")).to_be_hidden()

        page.click('[data-demo-node-id="sw1"]')
        expect(board.locator("#logic-detail-selected-node")).to_have_text("sw1")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(page.locator("#logic-selected-target-label")).to_contain_text("sw1")
    finally:
        page.close()


def test_logic_builder_page_reframes_around_circuit_workbench_shell(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-workstation-shell", "canvas-first")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-workstation-state", "primary")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-blueprint27-rhythm", "compact-canvas")
        expect(page.locator("main.logic-shell")).to_have_attribute("data-unified-inspector-state", "none")
        expect(page.locator("#logic-page-system-strip")).to_be_visible()
        expect(page.locator("#logic-page-system-strip")).to_have_class(re.compile(r"logic-command-strip"))
        expect(page.locator("#logic-page-system-strip")).to_have_attribute(
            "data-blueprint27-compact-topbar", "step-progress-workflow"
        )
        expect(page.locator("#logic-page-system-strip")).to_have_attribute("data-blueprint27-rhythm", "compact-topband")
        expect(page.locator(".logic-topbar")).to_have_count(0)
        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        main_box = page.locator("main.logic-shell").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        assert strip_box is not None
        assert main_box is not None
        assert canvas_box is not None
        assert strip_box["height"] <= 84
        assert strip_box["y"] + strip_box["height"] - main_box["y"] <= 104
        expect(page.locator("#logic-page-system-strip .logic-command-title h1")).to_have_text("逻辑绘制")
        expect(page.locator("#logic-page-system-strip #logic-process")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-workflow-overview")).to_be_visible()
        expect(page.locator("#logic-page-system-strip .logic-controls")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-provider")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-regenerate")).to_be_visible()
        expect(page.locator("#logic-page-system-strip #logic-fault-next")).to_be_visible()
        expect(page.locator("#logic-regenerate")).to_have_text("检查：重新绘制")
        expect(page.locator("#logic-fault-next")).to_have_text("下一步：进入故障准备")
        expect(page.locator("#logic-back")).to_have_text("更多：返回需求")
        expect(page.locator("#logic-canvas-compact-toolbar")).to_be_visible()
        expect(page.locator("#logic-canvas-compact-toolbar")).to_have_class(re.compile(r"logic-canvas-compact-toolbar"))
        expect(page.locator("#logic-canvas-compact-toolbar #logic-canvas-counts")).to_contain_text("20 circuit nodes")
        expect(page.locator("#logic-canvas-compact-toolbar #logic-provenance-filter")).to_be_visible()
        expect(page.locator("#logic-canvas-compact-toolbar #logic-canvas-source")).to_be_visible()
        expect(page.locator("#logic-mode-dock [data-logic-mode]")).to_have_count(5)
        expect(page.locator("#logic-mode-dock button")).to_have_count(5)
        expect(page.locator("#logic-mode-dock #logic-command-palette-open")).to_have_count(0)
        expect(page.locator("#logic-command-palette-open")).to_be_visible()
        expect(page.locator("#logic-command-palette-open")).to_have_attribute(
            "data-blueprint-advanced-entry", "command-palette"
        )
        expect(page.locator('.logic-canvas-wrap[data-workstation-stage="primary-canvas"]')).to_be_visible()
        expect(page.locator('.logic-canvas-wrap[data-blueprint29-rhythm="primary-canvas-stage"]')).to_be_visible()
        expect(page.locator('#logic-canvas[data-workstation-canvas="logic-drawing"]')).to_be_visible()
        expect(page.locator('#logic-mode-dock[data-workstation-surface="default-mode-dock"][data-blueprint27-rhythm="five-entry-dock"]')).to_be_visible()
        expect(page.locator('#logic-right-inspector-rail[data-blueprint38-rhythm="collapsed-inspector-rail"]')).to_be_visible()
        expect(page.locator('#logic-bottom-run-strip[data-blueprint38-rhythm="bottom-run-strip"]')).to_be_visible()
        expect(page.locator("#logic-canvas")).to_be_visible()
        _assert_logic_circuit_blueprint_geometry(page)

        strip_box = page.locator("#logic-page-system-strip").bounding_box()
        process_box = page.locator("#logic-process").bounding_box()
        workflow_box = page.locator("#logic-workflow-overview").bounding_box()
        controls_box = page.locator("#logic-page-system-strip .logic-controls").bounding_box()
        toolbar_box = page.locator("#logic-canvas-compact-toolbar").bounding_box()
        provenance_box = page.locator("#logic-provenance-filter").bounding_box()
        source_box = page.locator("#logic-canvas-source").bounding_box()
        canvas_wrap_box = page.locator(".logic-canvas-wrap").bounding_box()
        canvas_box = page.locator("#logic-canvas").bounding_box()
        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        bottom_strip_box = page.locator("#logic-bottom-run-strip").bounding_box()
        assert strip_box is not None
        assert process_box is not None
        assert workflow_box is not None
        assert controls_box is not None
        assert toolbar_box is not None
        assert provenance_box is not None
        assert source_box is not None
        assert canvas_wrap_box is not None
        assert canvas_box is not None
        assert rail_box is not None
        assert bottom_strip_box is not None
        assert strip_box["height"] <= 84
        assert process_box["height"] <= 82
        assert workflow_box["height"] <= 82
        assert controls_box["height"] <= 82
        assert toolbar_box["height"] <= 44
        assert provenance_box["y"] < toolbar_box["y"] + toolbar_box["height"]
        assert source_box["y"] < toolbar_box["y"] + toolbar_box["height"]
        assert canvas_box["y"] < 325
        assert canvas_wrap_box["y"] < rail_box["y"]
        assert bottom_strip_box["height"] <= 54
    finally:
        page.close()


def test_logic_builder_cockpit_stream_replay_and_direct_annotations(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
              localStorage.removeItem("ai-fantui-logic-builder-annotation-batch-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("main.logic-cockpit-shell")).to_have_attribute("data-logic-experience", "cockpit-annotation-stream")
        expect(page.locator(".logic-cockpit-canopy")).to_be_visible()
        expect(page.locator("#logic-canvas")).to_be_visible()
        expect(page.locator("#logic-drawing-stream-timeline")).to_be_visible()
        expect(page.locator("#logic-drawing-stream-timeline")).to_have_attribute("data-ai-stream", "logic-drawing-replay")
        expect(page.locator("#logic-drawing-stream-timeline")).to_have_attribute("data-blueprint39-stream", "compact-complete")
        expect(page.locator("#logic-drawing-stream-timeline .logic-stream-event")).to_have_count(8)
        expect(page.locator("#logic-drawing-stream-timeline")).to_contain_text("生成节点")
        expect(page.locator("#logic-drawing-stream-timeline")).to_contain_text("生成连线")
        expect(page.locator("#logic-drawing-stream-timeline")).to_contain_text("来源")
        stream_box = page.locator("#logic-drawing-stream-timeline").bounding_box()
        assert stream_box is not None
        assert stream_box["height"] <= 34
        stream_overlaps_nodes = page.evaluate(
            """() => {
              const stream = document.querySelector("#logic-drawing-stream-timeline");
              if (!stream) return [];
              const streamBox = stream.getBoundingClientRect();
              return Array.from(document.querySelectorAll(".logic-circuit-node")).filter((node) => {
                const box = node.getBoundingClientRect();
                return streamBox.left < box.right
                  && streamBox.right > box.left
                  && streamBox.top < box.bottom
                  && streamBox.bottom > box.top;
              }).map((node) => node.dataset.demoNodeId || node.dataset.nodeId || node.textContent.trim());
            }"""
        )
        assert stream_overlaps_nodes == []
        expect(page.locator("#logic-annotation-submit-bar")).to_be_visible()
        expect(page.locator("#logic-bottom-provider")).to_be_visible()
        expect(page.locator("#logic-submit-annotations")).to_have_text("提交此次标注意见")
        expect(page.locator("#logic-submit-annotations")).to_be_disabled()

        canvas_box = page.locator("#logic-canvas").bounding_box()
        rail_box = page.locator("#logic-engineering-rail").bounding_box()
        assert canvas_box is not None
        assert canvas_box["y"] < 310
        if rail_box is not None:
            assert rail_box["y"] > canvas_box["y"]

        page.click('[data-demo-node-id="sw1"]')
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(page.locator("#logic-selected-target-label")).to_contain_text("sw1")
        page.fill("#logic-node-comment-text", "SW1 节点需要补充来源锚点。")
        page.click("#logic-add-annotation")
        expect(page.locator("#logic-annotation-count")).to_have_text("1 条标注意见")
        expect(page.locator("#logic-annotation-list .logic-annotation-item")).to_have_count(1)

        page.click('.logic-circuit-wire[data-source="sw1"][data-target="logic1"]')
        expect(page.locator("#logic-selected-target-label")).to_contain_text("sw1 → logic1")
        page.fill("#logic-node-comment-text", "这条连线需要说明 SW1 如何进入 L1。")
        page.click("#logic-add-annotation")
        expect(page.locator("#logic-annotation-count")).to_have_text("2 条标注意见")
        expect(page.locator("#logic-annotation-list .logic-annotation-item")).to_have_count(2)
        expect(page.locator("#logic-submit-annotations")).to_be_enabled()
        page.click("#logic-submit-annotations")
        expect(page.locator("#logic-annotation-submit-state")).to_have_text("已提交 2 条标注意见")

        submitted = page.evaluate(
            """() => {
              const batch = JSON.parse(localStorage.getItem("ai-fantui-logic-builder-annotation-batch-v1"));
              return {
                count: batch.annotations.length,
                targets: batch.annotations.map((item) => `${item.target_type}:${item.target_id}`),
              };
            }"""
        )
        assert submitted["count"] == 2
        assert "node:sw1" in submitted["targets"]
        assert "wire:sw1->logic1" in submitted["targets"]
    finally:
        page.close()


def test_logic_builder_annotation_batch_calls_ai_revision_interpreter(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    captured_requests: list[dict[str, Any]] = []
    captured_updates: list[dict[str, Any]] = []
    try:
        page.route(
            "**/api/requirements-intake/interpret-logic-change",
            lambda route: (
                captured_requests.append(json.loads(route.request.post_data or "{}")),
                _fulfill_json(
                    route,
                    {
                        "kind": "ai-fantui-logic-change-interpretation",
                        "version": 1,
                        "status": "needs_user_confirmation",
                        "truth_effect": "none",
                        "candidate_state": "concept_logic_drawing_change",
                        "certification_claim": "none",
                        "controller_truth_modified": False,
                        "target_node_id": "sw1",
                        "annotation_text": "批量标注意见：SW1 节点需要补充来源锚点；sw1 → logic1 连线需要说明输入关系。",
                        "understanding_zh": "AI 已将两条标注归并为 SW1 到 L1 输入解释修订。",
                        "requirements_match_zh": "匹配 SW1/RA/L1 相关输入逻辑。",
                        "affected_nodes": ["sw1", "logic1"],
                        "affected_edges": ["sw1->logic1"],
                        "affected_parameter_panels": [],
                        "proposed_changes": ["补充 SW1 来源锚点。", "更新 sw1→logic1 连线说明。"],
                        "annotation_batch_summary_zh": "2 条标注意见归并为 1 个 SW1 输入解释修订包。",
                        "conflict_summary_zh": "未发现冲突。",
                        "annotation_groups": [
                            {
                                "group_label": "SW1 输入解释",
                                "annotation_ids": ["annotation_1", "annotation_2"],
                                "summary_zh": "节点和连线批注均指向 SW1 输入说明。",
                            }
                        ],
                        "selected_nodes": ["sw1"],
                        "selected_edges": ["sw1->logic1"],
                        "confirmation_question_zh": "是否确认按该批注包生成逻辑修订？",
                        "llm": {"provider": "deepseek", "model": "deepseek-v4-pro"},
                    },
                ),
            ),
        )
        page.route(
            "**/api/requirements-intake/update-logic-drawing",
            lambda route: (
                captured_updates.append(json.loads(route.request.post_data or "{}")),
                _fulfill_json(
                    route,
                    {
                        **_circuit_view_drawing(),
                        "summary_zh": "已按批量标注意见生成修订版逻辑电路图。",
                        "change_applied": {"source": "annotation_batch"},
                    },
                ),
            ),
        )
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """([requirements, drawing]) => {
              localStorage.setItem("ai-fantui-requirements-intake-ready-v1", JSON.stringify(requirements));
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-logic-builder-annotation-batch-v1");
            }""",
            [REQUIREMENTS_READY, _circuit_view_drawing()],
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        page.click('[data-demo-node-id="sw1"]')
        expect(page.locator("#logic-annotation-source")).not_to_have_text("选择节点或连线后显示来源。")
        expect(page.locator("#logic-annotation-params")).to_contain_text("role:")
        page.fill("#logic-node-comment-text", "SW1 节点需要补充来源锚点。")
        page.click("#logic-add-annotation")
        page.click('.logic-circuit-wire[data-source="sw1"][data-target="logic1"]')
        page.fill("#logic-node-comment-text", "这条连线需要说明 SW1 如何进入 L1。")
        page.click("#logic-add-annotation")
        page.click("#logic-submit-annotations")

        expect(page.locator("#logic-annotation-submit-state")).to_have_text("AI 已生成结构化修订建议")
        expect(page.locator("#logic-batch-interpretation-panel")).to_be_visible()
        expect(page.locator("#logic-batch-summary")).to_contain_text("2 条标注意见归并")
        expect(page.locator("#logic-batch-conflict-summary")).to_have_text("未发现冲突。")
        expect(page.locator("#logic-batch-proposed-changes li")).to_have_count(2)
        expect(page.locator("#logic-batch-confirmation-question")).to_contain_text("是否确认")
        expect(page.locator("#logic-batch-confirm-update")).to_be_enabled()

        assert len(captured_requests) == 1
        body = captured_requests[0]
        assert body["annotation_batch"][0]["target_type"] == "node"
        assert body["annotation_batch"][1]["target_type"] == "wire"
        assert body["selected_nodes"] == ["sw1"]
        assert body["selected_edges"] == ["sw1->logic1"]
        assert "批量标注意见" in body["annotation_text"]

        history_before = page.evaluate(
            """() => JSON.parse(localStorage.getItem("ai-fantui-logic-builder-change-history-v1") || "[]")"""
        )
        assert history_before[-1]["annotation_batch_count"] == 2
        assert history_before[-1]["status"] == "needs_confirmation"

        page.click("#logic-batch-confirm-update")
        expect(page.locator("#logic-process-title")).to_have_text("更新完成")
        expect(page.locator("#logic-batch-interpretation-panel")).to_be_hidden()
        assert len(captured_updates) == 1
        update_body = captured_updates[0]
        assert update_body["interpretation_payload"]["status"] == "confirmed_by_user"
        assert update_body["interpretation_payload"]["annotation_batch"][0]["target_id"] == "sw1"
        history_after = page.evaluate(
            """() => JSON.parse(localStorage.getItem("ai-fantui-logic-builder-change-history-v1") || "[]")"""
        )
        assert history_after[-1]["status"] == "updated"
    finally:
        page.close()


def test_logic_builder_combines_notes_change_and_history_into_tabbed_canvas_drawer(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 960})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-workbench-drawers")).to_be_hidden()
        expect(page.locator(".logic-canvas-wrap > #logic-workbench-drawers")).to_be_hidden()
        expect(page.locator("aside.logic-inspector > details")).to_have_count(0)
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-detail-decision-board")).to_be_hidden()
        expect(page.locator("#logic-detail-decision-board .logic-detail-card")).to_have_count(3)
        expect(page.locator("#logic-workbench-drawers [role='tab']")).to_have_count(3)
        expect(page.locator("#logic-workbench-drawers > details")).to_have_count(0)
        expect(page.locator('#logic-workbench-drawers [aria-selected="true"]')).to_have_count(0)
        expect(page.locator("#logic-drawing-notes-details")).to_be_hidden()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
        expect(page.locator("#logic-change-history-details")).to_be_hidden()

        canvas_box = page.locator("#logic-canvas").bounding_box()
        canvas_wrap_box = page.locator(".logic-canvas-wrap").bounding_box()
        assert canvas_box is not None
        assert canvas_wrap_box is not None
        assert canvas_wrap_box["height"] <= 800

        page.click('[data-demo-node-id="sw1"]')
        expect(page.locator("#logic-selected-node")).to_have_text("sw1")
        expect(page.locator("#logic-detail-selected-node")).to_have_text("sw1")
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "none")
        expect(page.locator("#logic-annotation-popover")).to_be_visible()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
        expect(page.locator("#logic-drawing-notes-details")).to_be_hidden()

        page.click('#logic-collapsed-tool-rail [data-workbench-tab="history"]')
        expect(page.locator("#logic-workbench-drawers")).to_have_attribute("data-active-tab", "history")
        expect(page.locator("#logic-workbench-drawers")).to_be_visible()
        expect(page.locator("#logic-change-history-details")).to_be_visible()
        expect(page.locator("#logic-change-loop-details")).to_be_hidden()
    finally:
        page.close()


def test_logic_builder_circuit_view_reduces_label_density_and_protects_sw_lane(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 900, "height": 760})
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            _circuit_view_drawing(),
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        expect(page.locator("#logic-canvas")).to_have_attribute("data-fit-mode", "fit-to-view")
        expect(page.locator("#logic-canvas")).to_have_attribute("data-readable-lanes", "sw")
        fit_scale = float(page.locator("#logic-canvas").get_attribute("data-fit-scale") or "0")
        assert 0.62 <= fit_scale <= 1

        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_attribute("data-readable-lane", "sw")
        expect(page.locator('[data-demo-node-id="sw2"]')).to_have_attribute("data-readable-lane", "sw")
        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_attribute("data-technical-id", "sw1")
        expect(page.locator('[data-demo-node-id="sw2"]')).to_have_attribute("data-technical-id", "sw2")
        expect(page.locator('[data-demo-node-id="sw1"] .logic-circuit-node-title')).to_have_text("SW1")
        expect(page.locator('[data-demo-node-id="sw2"] .logic-circuit-node-title')).to_have_text("SW2")
        assert "TRA" not in (page.locator('[data-demo-node-id="sw1"] .logic-circuit-node-title').text_content() or "")
        assert "TRA" not in (page.locator('[data-demo-node-id="sw2"] .logic-circuit-node-title').text_content() or "")

        sw1_title = page.locator('[data-demo-node-id="sw1"] title').text_content() or ""
        assert "技术 id: sw1" in sw1_title
        assert "TRA [-1.4°,-6.2°]" in sw1_title
        expect(page.locator('[data-demo-node-id="sw1"] .logic-circuit-tech-id')).to_have_text("sw1")
        expect(page.locator('[data-demo-node-id="sw2"] .logic-circuit-tech-id')).to_have_text("sw2")

        expect(page.locator('.logic-circuit-lane-guide[data-readable-lane="sw"]')).to_have_count(1)
        expect(page.locator('.logic-circuit-lane-guide[data-readable-lane="sw"] .logic-circuit-lane-label')).to_contain_text(
            "SW1/SW2"
        )
        expect(page.locator('.logic-circuit-wire[data-source="sw1"][data-target="logic1"]')).to_have_attribute(
            "data-readable-lane",
            "sw",
        )
        expect(page.locator('.logic-circuit-wire[data-source="sw2"][data-target="logic2"]')).to_have_attribute(
            "data-readable-lane",
            "sw",
        )
        _assert_logic_circuit_blueprint_geometry(page)
    finally:
        page.close()


def test_logic_builder_circuit_view_provenance_legend_filters_node_sources(
    demo_server: str, browser: Any
) -> None:
    page = browser.new_page(viewport={"width": 980, "height": 760})
    drawing = _circuit_view_drawing()
    view = drawing["circuit_view"]
    for node in view["nodes"]:
        if node["id"] == "radio_altitude_ft":
            node["source_anchors"] = [
                {
                    "id": "B37",
                    "kind": "正文条件",
                    "quote_zh": "无线电高度低于 6ft 时进入反推条件判断。",
                }
            ]
            break
    view["nodes"].append(
        {
            "id": "model_gap_probe",
            "label": "模型推断条件",
            "circuit_role": "input",
            "state": "idle",
            "x": 700,
            "y": 330,
            "width": 132,
            "height": 28,
        }
    )
    try:
        page.goto(f"{demo_server}/index.html", wait_until="domcontentloaded")
        page.evaluate(
            """(drawing) => {
              localStorage.setItem("ai-fantui-logic-builder-drawing-v1", JSON.stringify(drawing));
              localStorage.removeItem("ai-fantui-requirements-intake-ready-v1");
            }""",
            drawing,
        )

        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-provenance-filter")).to_be_visible()
        expect(page.locator('[data-provenance-filter="source"] [data-provenance-count]')).to_have_text("1")
        expect(page.locator('[data-provenance-filter="local"] [data-provenance-count]')).to_have_text("19")
        expect(page.locator('[data-provenance-filter="assumption"] [data-provenance-count]')).to_have_text("1")
        expect(page.locator('[data-demo-node-id="radio_altitude_ft"]')).to_have_attribute("data-provenance-kind", "source")
        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_attribute("data-provenance-kind", "local")
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).to_have_attribute("data-provenance-kind", "assumption")
        assert "来源: 本地补齐" in (page.locator('[data-demo-node-id="sw1"] title').text_content() or "")

        page.click('[data-provenance-filter="assumption"]')
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "assumption")
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).to_have_class(re.compile(r"is-provenance-match"))
        expect(page.locator('[data-demo-node-id="sw1"]')).to_have_class(re.compile(r"is-provenance-muted"))

        page.click('[data-provenance-filter="source"]')
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "source")
        expect(page.locator('[data-demo-node-id="radio_altitude_ft"]')).to_have_class(re.compile(r"is-provenance-match"))
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).to_have_class(re.compile(r"is-provenance-muted"))

        page.click('[data-provenance-filter="all"]')
        expect(page.locator("#logic-canvas")).to_have_attribute("data-provenance-filter", "all")
        expect(page.locator('[data-demo-node-id="model_gap_probe"]')).not_to_have_class(re.compile(r"is-provenance-muted"))
    finally:
        page.close()


def test_deepseek_live_replay_import_seeds_workbench_without_model_calls(demo_server: str, browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    model_calls: list[str] = []
    try:
        page.route("**/api/requirements-intake/deepseek-live-demo-replay", lambda route: _fulfill_json(route, _replay_payload()))

        def reject_model_call(route: Any) -> None:
            model_calls.append(route.request.url)
            route.fulfill(status=500, content_type="application/json", body='{"error":"model_call_forbidden"}')

        page.route("**/api/requirements-intake/analyze", reject_model_call)
        page.route("**/api/requirements-intake/draw-logic", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection", reject_model_call)
        page.route("**/api/requirements-intake/prepare-fault-injection/sandbox", reject_model_call)

        page.goto(f"{demo_server}/index.html", wait_until="networkidle")
        expect(page.locator("#deepseek-live-replay-import")).to_be_visible()
        expect(page.locator("#deepseek-live-replay-meta")).to_contain_text("deepseek-v4-pro")
        expect(page.locator("#deepseek-live-replay-meta")).to_contain_text("2026-05-13 10:30")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("需求理解")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("沙盒计划")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("1 plans")
        page.click("#deepseek-live-replay-import")
        page.wait_for_url("**/fault-injection-sandbox?replay=deepseek-live")
        expect(page.locator("#fault-sandbox-result-state")).to_have_text("配置已生成")
        expect(page.locator("#fault-sandbox-plan-coverage-evidence")).to_contain_text("auto_fault_thr_lock_rel")
        expect(page.locator("#fault-sandbox-source-metrics")).to_contain_text("2 answers")
        stored = page.evaluate(
            """
            () => ({
              requirements: JSON.parse(localStorage.getItem("ai-fantui-requirements-intake-ready-v1")).kind,
              drawing: JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1")).kind,
              drawingHasCircuitView: Boolean(JSON.parse(localStorage.getItem("ai-fantui-logic-builder-drawing-v1")).circuit_view),
              history: JSON.parse(localStorage.getItem("ai-fantui-logic-builder-change-history-v1")).length,
              faultAnswers: JSON.parse(localStorage.getItem("ai-fantui-fault-injection-preparation-v1")).boundary_answers.length,
              sandbox: JSON.parse(localStorage.getItem("ai-fantui-fault-injection-sandbox-plan-v1")).kind,
            })
            """
        )
        assert stored == {
            "requirements": "ai-fantui-requirements-intake-analysis",
            "drawing": "ai-fantui-logic-link-drawing",
            "drawingHasCircuitView": True,
            "history": 0,
            "faultAnswers": 2,
            "sandbox": "ai-fantui-fault-injection-sandbox-plan",
        }
        assert model_calls == []
        page.goto(f"{demo_server}/logic-builder", wait_until="networkidle")
        expect(page.locator("#logic-circuit-eval-panel")).to_be_visible()
        page.select_option("#logic-circuit-preset-select", "max-reverse")
        expect(page.locator("#logic-circuit-status-badge")).to_have_text("DEPLOYED")
        page.goto(f"{demo_server}/requirements-intake", wait_until="networkidle")
        expect(page.locator("#requirements-status")).to_have_text("已恢复回放草稿")
        expect(page.locator("#result-state")).to_have_text("可进入逻辑链路")
        expect(page.locator("#graph-counts")).to_have_text("3 nodes · 2 edges")
        _screenshot(page, "06-deepseek-live-replay-import")
    finally:
        page.close()


def test_deepseek_live_replay_file_mode_explains_local_server_requirement(browser: Any) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 820})
    replay_api_requests: list[str] = []

    def collect_replay_api_request(request: Any) -> None:
        if "/api/requirements-intake/deepseek-live-demo-replay" in request.url:
            replay_api_requests.append(request.url)

    page.on("request", collect_replay_api_request)
    try:
        page.goto((Path("src/well_harness/static/index.html").resolve()).as_uri(), wait_until="networkidle")
        expect(page.locator("#deepseek-live-replay-import")).to_be_visible()
        expect(page.locator("#deepseek-live-replay-status")).to_contain_text("file:// 无法读取回放 API")
        expect(page.locator("#deepseek-live-replay-meta")).to_contain_text("需启动本地服务")
        expect(page.locator("#deepseek-live-replay-counts")).to_contain_text("python3 -m well_harness.demo_server")

        page.click("#deepseek-live-replay-import")
        expect(page.locator("#deepseek-live-replay-status")).to_contain_text("请先启动服务")
        expect(page.locator("#deepseek-live-replay-status")).not_to_contain_text("Failed to fetch")
        assert replay_api_requests == []
    finally:
        page.close()
