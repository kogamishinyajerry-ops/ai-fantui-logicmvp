#!/usr/bin/env python3
"""Generate first-screen visual acceptance evidence for the DeepSeek UI shell."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
DEFAULT_ARTIFACT_DIR = REPO_ROOT / "artifacts" / "deepseek-ui-visual-acceptance-20260514"

REQUIREMENTS_KEY = "ai-fantui-requirements-intake-ready-v1"
DRAWING_KEY = "ai-fantui-logic-builder-drawing-v1"
FAULT_KEY = "ai-fantui-fault-injection-preparation-v1"
SANDBOX_KEY = "ai-fantui-fault-injection-sandbox-plan-v1"

VIEWPORTS = [
    {"name": "desktop-1366x768", "width": 1366, "height": 768},
    {"name": "desktop-1280x820", "width": 1280, "height": 820},
]

ROUTES = [
    {
        "key": "requirements-intake",
        "path": "/requirements-intake",
        "visible_surfaces": {
            "compact_top_bar": '[data-command-strip="deepseek-step"]',
            "requirements_blueprint14_shell": '.requirements-shell[data-blueprint14-rhythm="compact-canvas"]',
            "requirements_blueprint14_topbar": '[data-blueprint14-compact-topbar="step-provider-next"]',
            "canvas_first_shell": '.requirements-shell[data-workstation-shell="canvas-first"]',
            "primary_canvas_stage": '.clarification-primary[data-workstation-stage="primary-canvas"]',
            "requirements_primary_canvas_rhythm": '.clarification-primary[data-blueprint14-canvas-rhythm="expanded-first-screen"]',
            "source_input_inspector": '.requirements-input-panel[data-workstation-inspector="source-input"]',
            "requirements_source_inspector_rhythm": '.requirements-input-panel[data-blueprint14-inspector="source-document-input"]',
            "requirements_decision_board": "#requirements-preflight-panel",
            "requirements_decision_density": '#requirements-preflight-panel[data-blueprint14-density="compact-decision-board"]',
            "requirements_single_provider_chip": '.requirements-provider-live[data-blueprint39-status="single-chip"]',
            "usage_path_cue": '#next-step-copy[data-usage-path-cue="requirements"]',
            "choice_checklist": "#requirements-confirmation-checklist",
            "primary_workbench": ".clarification-primary",
        },
        "existing_surfaces": {
            "workflow": "#requirements-workflow-overview",
            "generation_stream": "#requirements-generation-stream",
        },
        "clip_surfaces": {
            "requirements_preflight_panel": "#requirements-preflight-panel",
        },
    },
    {
        "key": "logic-builder",
        "path": "/logic-builder",
        "max_logic_top_band_height": 104,
        "visible_surfaces": {
            "compact_top_bar": '[data-command-strip="deepseek-step"]',
            "compact_logic_top_band": '#logic-page-system-strip[data-blueprint27-compact-topbar="step-progress-workflow"]',
            "logic_blueprint27_shell": '.logic-shell[data-blueprint27-rhythm="compact-canvas"]',
            "logic_blueprint27_topband": '#logic-page-system-strip[data-blueprint27-rhythm="compact-topband"]',
            "usage_path_cue": '#logic-workflow-detail[data-usage-path-cue="logic"]',
            "canvas_first_shell": '.logic-shell[data-workstation-shell="canvas-first"]',
            "primary_canvas_stage": '.logic-canvas-wrap[data-workstation-stage="primary-canvas"]',
            "logic_blueprint29_canvas_rhythm": '.logic-canvas-wrap[data-blueprint29-rhythm="primary-canvas-stage"]',
            "canvas_workstation": '#logic-canvas[data-workstation-canvas="logic-drawing"]',
            "primary_canvas": "#logic-canvas",
            "collapsed_left_rail": "#logic-collapsed-tool-rail",
            "collapsed_right_rail": '#logic-right-inspector-rail[data-blueprint38-rhythm="collapsed-inspector-rail"]',
            "mode_dock": '#logic-mode-dock[data-blueprint27-rhythm="five-entry-dock"]',
            "command_palette_advanced_entry": '#logic-command-palette-open[data-blueprint-advanced-entry="command-palette"]',
            "bottom_run_strip": '#logic-bottom-run-strip[data-blueprint38-rhythm="bottom-run-strip"]',
            "compact_drawing_stream": '#logic-drawing-stream-timeline[data-blueprint39-stream="compact-complete"]',
        },
        "existing_surfaces": {
            "command_palette": "#logic-command-palette",
            "blank_canvas_entry": "#logic-template-entry",
            "blank_canvas_template_rhythm": '#logic-template-entry[data-blueprint29-rhythm="blank-canvas-template-entry"]',
        },
    },
    {
        "key": "fault-injection-prepare",
        "path": "/fault-injection-prepare",
        "visible_surfaces": {
            "compact_top_bar": '[data-command-strip="deepseek-step"]',
            "fault_matrix_shell": "#fault-matrix",
            "fault_decision_board": "#fault-decision-board",
            "usage_path_cue": '#fault-decision-next-action[data-usage-path-cue="fault"]',
            "fault_candidate_matrix": "#fault-candidate-matrix-panel",
            "fault_matrix_density_shell": '.fault-candidate-matrix[data-blueprint-density="compact-workbench"]',
            "fault_matrix_rows": '#fault-candidate-matrix-body [data-blueprint-fault-row="matrix"]',
            "fault_matrix_blueprint33_rows": '#fault-candidate-matrix-body [data-blueprint33-row="fault-matrix"]',
            "fault_matrix_density_rows": '#fault-candidate-matrix-body [data-blueprint-density="compact-workbench"]',
            "fault_matrix_shared_rows": '#fault-candidate-matrix-body [data-blueprint-row-pattern="shared-v1"]',
            "fault_matrix_path_summary": "#fault-candidate-matrix-body .fault-matrix-path-summary",
            "fault_matrix_path_tokens": "#fault-candidate-matrix-body .fault-matrix-path-token",
            "fault_matrix_shared_tokens": "#fault-candidate-matrix-body .blueprint-row-token",
            "fault_matrix_shared_chips": "#fault-candidate-matrix-body .blueprint-row-chip",
            "fault_matrix_risk_chips": "#fault-candidate-matrix-body .fault-matrix-risk",
            "fault_matrix_state_chips": "#fault-candidate-matrix-body .fault-matrix-status",
            "fault_unified_inspector": '.fault-sidebar[data-unified-inspector="right-inspector"]',
            "bottom_action_strip": "#fault-bottom-action-strip",
        },
        "existing_surfaces": {
            "candidate_details": "#fault-candidate-details",
            "injection_point_details": "#fault-injection-point-details",
        },
        "clip_surfaces": {
            "fault_candidate_details": "#fault-candidate-details",
            "fault_injection_point_details": "#fault-injection-point-details",
        },
    },
    {
        "key": "fault-injection-sandbox-default",
        "path": "/fault-injection-sandbox",
        "visible_surfaces": {
            "compact_top_bar": '[data-command-strip="deepseek-step"]',
            "failure_path": "#failure-path",
            "usage_path_cue": '#fault-sandbox-decision-next-action[data-usage-path-cue="sandbox"]',
            "review_rows": "#fault-sandbox-review-row-panel",
            "review_row_density_shell": '#fault-sandbox-review-rows[data-blueprint-density="compact-workbench"] [data-blueprint36-row="sandbox-review"]',
            "review_row_link_sr06": '#fault-sandbox-review-rows [data-blueprint-review-row="SR-06"]',
            "diagnosis_inspector": "#fault-sandbox-diagnosis-inspector",
            "diagnosis_unified_inspector": '#fault-sandbox-diagnosis-inspector[data-unified-inspector="right-inspector"]',
            "active_path_summary": '#fault-sandbox-review-package-summary[data-package-state="active"]',
            "status_only_report_rail": '#fault-sandbox-main-report-rail[data-blueprint39-default="status-only"]',
            "active_path_text": "#fault-sandbox-affected-path",
            "diagnosis_chain_nodes": '#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node="failure-path"]',
            "evidence_trace": "#fault-sandbox-evidence-trace",
            "report_strip": "#sandbox-report-strip",
            "report_strip_inspector_role": '#sandbox-report-strip[data-inspector-role="bottom-report-strip"]',
            "replay_report_preview": "#fault-sandbox-report-preview",
        },
        "existing_surfaces": {
            "review_package_drawer": "#fault-sandbox-detail-drawer",
            "evidence_popover": "#sandbox-evidence-popover",
        },
    },
    {
        "key": "fault-injection-sandbox",
        "path": "/fault-injection-sandbox",
        "pre_capture_click": '[data-sandbox-report-action="export"]',
        "pre_capture_visible": "#sandbox-review-package-panel",
        "visible_surfaces": {
            "compact_top_bar": '[data-command-strip="deepseek-step"]',
            "failure_path": "#failure-path",
            "usage_path_cue": '#fault-sandbox-decision-next-action[data-usage-path-cue="sandbox"]',
            "review_rows": "#fault-sandbox-review-row-panel",
            "review_row_density_shell": '#fault-sandbox-review-rows[data-blueprint-density="compact-workbench"] [data-blueprint36-row="sandbox-review"]',
            "review_row_contract": "#fault-sandbox-review-rows [data-blueprint-review-row]",
            "review_row_blueprint36": '#fault-sandbox-review-rows [data-blueprint36-row="sandbox-review"]',
            "review_row_density_rows": '#fault-sandbox-review-rows [data-blueprint-density="compact-workbench"]',
            "review_row_shared_pattern": '#fault-sandbox-review-rows [data-blueprint-row-pattern="shared-v1"]',
            "review_row_shared_tokens": "#fault-sandbox-review-rows .blueprint-row-token",
            "review_row_decision_chips": "#fault-sandbox-review-rows .sandbox-review-row-decision",
            "review_row_trace_report_col": '#fault-sandbox-review-rows [data-blueprint36-row="sandbox-review"] [data-blueprint-col="trace-report"]',
            "review_row_link_tokens": "#fault-sandbox-review-rows .sandbox-review-row-link-token",
            "review_row_link_sr06": '#fault-sandbox-review-rows [data-blueprint-review-row="SR-06"]',
            "diagnosis_inspector": "#fault-sandbox-diagnosis-inspector",
            "diagnosis_unified_inspector": '#fault-sandbox-diagnosis-inspector[data-unified-inspector="right-inspector"]',
            "active_path_summary": '#fault-sandbox-review-package-summary[data-package-state="active"]',
            "status_only_report_rail": '#fault-sandbox-main-report-rail[data-blueprint39-default="status-only"]',
            "diagnosis_chain_nodes": '#fault-sandbox-diagnosis-chain [data-blueprint36-chain-node="failure-path"]',
            "diagnosis_chain_shared_pattern": '#fault-sandbox-diagnosis-chain [data-blueprint-row-pattern="shared-v1"]',
            "diagnosis_chain_link_tokens": "#fault-sandbox-diagnosis-chain .sandbox-diagnosis-chain-link-token",
            "diagnosis_evidence_links": '#fault-sandbox-diagnosis-evidence-links [data-blueprint36-evidence-link="diagnosis"]',
            "evidence_trace": "#fault-sandbox-evidence-trace",
            "evidence_trace_report_link": '#fault-sandbox-evidence-trace-rows [data-evidence-trace-id="ET-04"]',
            "evidence_trace_blueprint36_rows": '#fault-sandbox-evidence-trace-rows [data-blueprint36-evidence-row="evidence-chain"]',
            "evidence_trace_shared_pattern": '#fault-sandbox-evidence-trace-rows [data-blueprint-row-pattern="shared-v1"]',
            "evidence_trace_link_tokens": "#fault-sandbox-evidence-trace-rows .sandbox-evidence-trace-link-token",
            "evidence_trace_report_token": '#fault-sandbox-evidence-trace-rows [data-evidence-trace-id="ET-04"] [data-link-kind="report"]',
            "report_strip": "#sandbox-report-strip",
            "report_strip_inspector_role": '#sandbox-report-strip[data-inspector-role="bottom-report-strip"]',
            "replay_report_preview": "#fault-sandbox-report-preview",
            "replay_report_rows": '#fault-sandbox-report-section-rows [data-blueprint-report-row="review-package-section"]',
            "replay_report_blueprint36_rows": '#fault-sandbox-report-section-rows [data-blueprint36-report-row="replay-report"]',
            "replay_report_shared_pattern": '#fault-sandbox-report-section-rows [data-blueprint-row-pattern="shared-v1"]',
            "replay_report_decision_chips": "#fault-sandbox-report-section-rows .sandbox-report-section-decision",
            "replay_report_link_tokens": "#fault-sandbox-report-section-rows .sandbox-report-link-token",
            "replay_report_review_link": '#fault-sandbox-report-section-rows [data-report-section-id="RP-06"]',
            "review_package_export_preview": "#sandbox-review-package-panel",
            "review_package_unified_panel": '#sandbox-review-package-panel[data-unified-aux-panel="review-package"][data-unified-panel-state="open"]',
            "review_package_shared_pattern": '#sandbox-review-package-panel [data-blueprint-row-pattern="shared-v1"]',
            "review_package_blueprint36_review_rows": '#sandbox-review-package-review-rows [data-blueprint36-package-row="review-package-review"]',
            "review_package_blueprint36_report_rows": '#sandbox-review-package-report-rows [data-blueprint36-package-row="review-package-report"]',
            "review_package_shared_tokens": "#sandbox-review-package-panel .blueprint-row-token",
            "review_package_link_tokens": "#sandbox-review-package-panel .sandbox-review-package-link-token",
        },
        "existing_surfaces": {
            "review_package_drawer": "#fault-sandbox-detail-drawer",
            "evidence_popover": "#sandbox-evidence-popover",
        },
        "clip_surfaces": {
            "review_package_card": ".sandbox-review-package-card",
        },
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _requirements_payload() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-requirements-intake-analysis",
        "version": 1,
        "status": "ready_for_logic_builder",
        "ready_for_logic_builder": True,
        "summary_zh": "本地预解析已收敛出 L1-L4 反推链路，用于首屏视觉验收。",
        "open_questions": [],
        "concept_logic_nodes": [
            {"id": "ra_lt_6ft", "label": "RA<6ft", "node_kind": "input"},
            {"id": "sw1", "label": "SW1", "node_kind": "input"},
            {"id": "sw2", "label": "SW2", "node_kind": "input"},
            {"id": "tra_reverse_range", "label": "TRA 反推区", "node_kind": "input"},
            {"id": "logic1", "label": "L1", "node_kind": "logic"},
            {"id": "logic2", "label": "L2", "node_kind": "logic"},
            {"id": "logic3", "label": "L3", "node_kind": "logic"},
            {"id": "logic4", "label": "L4", "node_kind": "logic"},
            {"id": "thr_lock_release", "label": "THR_LOCK release", "node_kind": "output"},
        ],
        "concept_edges": [
            {"id": "e_ra_l1", "source": "ra_lt_6ft", "target": "logic1", "label": "高度门限"},
            {"id": "e_sw1_l1", "source": "sw1", "target": "logic1", "label": "SW1 条件"},
            {"id": "e_sw2_l2", "source": "sw2", "target": "logic2", "label": "SW2 条件"},
            {"id": "e_l2_l3", "source": "logic2", "target": "logic3", "label": "执行链汇合"},
            {"id": "e_l3_l4", "source": "logic3", "target": "logic4", "label": "展开反馈"},
            {"id": "e_l4_lock", "source": "logic4", "target": "thr_lock_release", "label": "释放"},
        ],
        "deterministic_preparse": {"available": True, "applied": True},
        "truth_effect": "none",
        "candidate_state": "concept_only",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
    }


def _circuit_view(requirements: dict[str, Any]) -> dict[str, Any] | None:
    try:
        from well_harness.requirements_intake.logic_builder import _build_l1_l4_circuit_view
    except Exception:
        return None
    try:
        return _build_l1_l4_circuit_view(requirements)
    except Exception:
        return None


def _drawing_payload(requirements: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "kind": "ai-fantui-logic-link-drawing",
        "version": 1,
        "status": "draft_ready",
        "summary_zh": "确定性 L1-L4 电路图已生成，用于首屏视觉验收。",
        "source_requirements_sha256": "visual-acceptance-l1-l4",
        "canvas": {"width": 900, "height": 400},
        "nodes": [
            {
                "id": "ra_lt_6ft",
                "label": "RA<6ft",
                "node_kind": "input",
                "x": 80,
                "y": 120,
                "width": 180,
                "height": 96,
            },
            {
                "id": "logic1",
                "label": "L1",
                "node_kind": "logic",
                "x": 380,
                "y": 120,
                "width": 190,
                "height": 104,
            },
            {
                "id": "thr_lock_release",
                "label": "THR_LOCK release",
                "node_kind": "output",
                "x": 690,
                "y": 120,
                "width": 220,
                "height": 104,
            },
        ],
        "edges": [
            {
                "id": "edge_ra_l1",
                "source": "ra_lt_6ft",
                "target": "logic1",
                "label": "RA<6ft",
                "route": [{"x": 260, "y": 168}, {"x": 380, "y": 168}],
            },
            {
                "id": "edge_l1_lock",
                "source": "logic1",
                "target": "thr_lock_release",
                "label": "L1 pass",
                "route": [{"x": 570, "y": 168}, {"x": 690, "y": 168}],
            },
        ],
        "parameter_panels": [],
        "drawing_notes": ["首屏视觉验收种子，不修改控制逻辑真值。"],
        "truth_effect": "none",
        "candidate_state": "concept_logic_drawing",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
    }
    circuit_view = _circuit_view(requirements)
    if circuit_view:
        payload["circuit_view"] = circuit_view
    return payload


def _fault_payload() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-fault-injection-preparation",
        "version": 1,
        "status": "fault_preparation_ready",
        "summary_zh": "蓝图候选故障矩阵已准备，仅用于 dry-run 沙盒候选。",
        "fault_scenarios": [
            {
                "id": "fault_ra_stuck_low",
                "label": "RA 低值卡滞",
                "node_id": "ra_lt_6ft",
                "fault_type": "stuck_low",
                "severity": "high",
                "rationale_zh": "RA 输入会直接影响释放门判断。",
                "expected_effect_zh": "可能提前满足释放条件。",
                "observable_signals": ["radio_altitude_ft", "release_gate"],
                "covered_path": ["ra_lt_6ft", "logic1", "thr_lock_release"],
            },
            {
                "id": "fault_sw2_drop",
                "label": "SW2 掉线",
                "node_id": "sw2",
                "fault_type": "dropout",
                "severity": "medium",
                "rationale_zh": "SW2 条件缺失会阻断执行链。",
                "expected_effect_zh": "应保持 THR_LOCK 不释放。",
                "observable_signals": ["sw2_valid", "logic2"],
                "covered_path": ["sw2", "logic2", "logic3"],
            },
        ],
        "injection_points": [
            {
                "id": "inject_ra",
                "node_id": "ra_lt_6ft",
                "signal_name": "radio_altitude_ft",
                "injection_mode": "override",
                "safe_boundary_zh": "仅 dry-run，RA 范围限制在 0 到 20ft。",
            },
            {
                "id": "inject_sw2",
                "node_id": "sw2",
                "signal_name": "sw2_valid",
                "injection_mode": "dropout",
                "safe_boundary_zh": "仅 dry-run，不写入控制器状态。",
            },
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
        "coverage_completion": {
            "strategy": "visual_acceptance_candidate",
            "completed_node_ids": ["thr_lock_release"],
            "semantic_gate": "critical_node_coverage",
        },
        "workflow_notes": ["完成边界确认后进入沙盒注入配置。"],
        "truth_effect": "none",
        "candidate_state": "fault_injection_preparation",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
    }


def _sandbox_payload() -> dict[str, Any]:
    return {
        "kind": "ai-fantui-fault-injection-sandbox-plan",
        "version": 1,
        "status": "sandbox_plan_ready",
        "summary_zh": "蓝图候选沙盒计划已生成，仅用于 dry-run 回放审查。",
        "sandbox_injection_plan": [
            {
                "id": "blueprint_plan_ra_override",
                "fault_scenario_id": "fault_ra_stuck_low",
                "node_id": "ra_lt_6ft",
                "injection_mode": "override",
                "safe_range_zh": "RA 输入限制在 0 到 20ft。",
                "expected_effect_zh": "观察释放门是否只在完整条件满足后放行。",
            },
            {
                "id": "blueprint_plan_sw2_dropout",
                "fault_scenario_id": "fault_sw2_drop",
                "node_id": "sw2",
                "injection_mode": "dropout",
                "safe_range_zh": "仅 dry-run 断链观察。",
                "expected_effect_zh": "确认执行链不会越过 SW2 缺失。",
            },
        ],
        "observation_points": [
            {
                "id": "observe_release_gate",
                "node_id": "logic1",
                "signal_name": "release_gate",
                "check_zh": "确认 RA 异常不会绕过 TRA、SW1、SW2、EEC 条件。",
            },
            {
                "id": "observe_thr_lock",
                "node_id": "thr_lock_release",
                "signal_name": "thr_lock_release",
                "check_zh": "确认 THR_LOCK 仍遵守 dry-run 计划边界。",
            },
        ],
        "review_checklist": [
            {
                "id": "review_dry_run",
                "category": "dry_run",
                "condition_zh": "确认沙盒配置只读且不运行 tick。",
                "pass_criteria_zh": "run_tick:false、simulate:false、dry_run_only:true。",
            },
            {
                "id": "review_truth",
                "category": "truth_boundary",
                "condition_zh": "确认候选不修改控制器真值。",
                "pass_criteria_zh": "controller_truth_modified:false。",
            },
        ],
        "execution_contract": {"run_tick": False, "simulate": False, "dry_run_only": True},
        "plan_coverage_completion": {
            "strategy": "visual_acceptance_candidate",
            "completed_fault_scenario_ids": ["fault_ra_stuck_low", "fault_sw2_drop"],
            "semantic_gate": "scenario_plan_coverage",
        },
        "truth_effect": "none",
        "candidate_state": "sandbox_candidate",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "llm": {"provider": "deepseek", "model": "DeepSeek V4 Pro"},
    }


def _seed_payloads() -> dict[str, dict[str, Any]]:
    requirements = _requirements_payload()
    return {
        REQUIREMENTS_KEY: requirements,
        DRAWING_KEY: _drawing_payload(requirements),
        FAULT_KEY: _fault_payload(),
        SANDBOX_KEY: _sandbox_payload(),
    }


def _normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def _url_ready(base_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{_normalize_base_url(base_url)}/requirements-intake", timeout=1.5) as response:
            return 200 <= response.status < 500
    except (OSError, urllib.error.URLError):
        return False


def _wait_ready(base_url: str, timeout_s: float) -> bool:
    start = time.monotonic()
    while time.monotonic() - start < timeout_s:
        if _url_ready(base_url):
            return True
        time.sleep(0.15)
    return False


def _spawn_server(port: int) -> subprocess.Popen[bytes]:
    env = os.environ.copy()
    src_path = str(REPO_ROOT / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path + (os.pathsep + existing if existing else "")
    return subprocess.Popen(
        [sys.executable, "-m", "well_harness.demo_server", "--port", str(port)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def _stop_server(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        proc.wait(timeout=2)


def _surface_state(page: Any, selector: str) -> dict[str, Any]:
    locator = page.locator(selector)
    count = locator.count()
    visible = False
    box = None
    if count:
        first = locator.first
        visible = first.is_visible()
        box = first.bounding_box()
    return {"selector": selector, "count": count, "visible": visible, "box": box}


def _clip_state(page: Any, selector: str) -> dict[str, Any]:
    return page.evaluate(
        """(selector) => {
          const element = document.querySelector(selector);
          if (!element) return {selector, count: 0, visible: false, clipped: false};
          const style = window.getComputedStyle(element);
          const visible = style.display !== "none"
            && style.visibility !== "hidden"
            && element.getClientRects().length > 0;
          const overflowHidden = [style.overflow, style.overflowX, style.overflowY].includes("hidden");
          const clipped = Boolean(visible && overflowHidden && (
            element.scrollHeight > element.clientHeight + 1
            || element.scrollWidth > element.clientWidth + 1
          ));
          return {
            selector,
            count: 1,
            visible,
            clipped,
            scrollHeight: element.scrollHeight,
            clientHeight: element.clientHeight,
            scrollWidth: element.scrollWidth,
            clientWidth: element.clientWidth,
            overflow: style.overflow,
            overflowX: style.overflowX,
            overflowY: style.overflowY,
          };
        }""",
        selector,
    )


def _page_geometry(page: Any, viewport: dict[str, int | str]) -> dict[str, Any]:
    return page.evaluate(
        """(viewport) => {
          const scrollHeight = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
          const scrollWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
          const overflow = Array.from(document.querySelectorAll("body *")).filter((el) => {
            const style = window.getComputedStyle(el);
            return style.display !== "none"
              && el.scrollWidth > el.clientWidth + 1
              && style.overflowX !== "hidden";
          }).map((el) => {
            const classes = Array.from(el.classList || []).slice(0, 3).join(".");
            const selector = el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}${classes ? "." + classes : ""}`;
            return {
              selector,
              scrollWidth: el.scrollWidth,
              clientWidth: el.clientWidth,
              overflowX: window.getComputedStyle(el).overflowX,
            };
          }).slice(0, 20);
          const strip = document.querySelector('[data-command-strip="deepseek-step"]');
          const main = document.querySelector("main");
          const stripBox = strip ? strip.getBoundingClientRect() : null;
          const mainBox = main ? main.getBoundingClientRect() : null;
          return {
            viewport,
            scroll_height: scrollHeight,
            scroll_width: scrollWidth,
            window_inner_height: window.innerHeight,
            window_inner_width: window.innerWidth,
            vertical_scroll_ok: scrollHeight <= window.innerHeight,
            horizontal_overflow_count: overflow.length,
            horizontal_overflow_nodes: overflow,
            topbar_height: stripBox ? stripBox.height : null,
            logic_top_band_height: mainBox && stripBox
              ? Math.round(stripBox.bottom - mainBox.top)
              : null,
            panel_strategy: main ? main.dataset.panelStrategy || null : null,
            active_aux_panel: main ? main.dataset.activeAuxPanel || null : null,
          };
        }""",
        viewport,
    )


def _blueprint_geometry(page: Any, route_key: str) -> dict[str, Any]:
    if route_key == "logic-builder":
        return page.evaluate(
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
              }
              const text_overflow = Array.from(document.querySelectorAll(
                ".logic-circuit-node-title, .logic-circuit-gate-label, .logic-circuit-node-subtitle, .logic-circuit-gate-caption"
              )).filter((label) => {
                const node = label.closest(".logic-circuit-node");
                const box = node?.querySelector(".logic-circuit-node-box, .logic-circuit-gate-box");
                const maxWidth = Number(box?.getAttribute("width") || 0) - 10;
                return maxWidth > 0
                  && typeof label.getComputedTextLength === "function"
                  && label.getComputedTextLength() > maxWidth + 1;
              }).map((label) => label.textContent || "");
              return {failures, text_overflow};
            }"""
        )
    if route_key == "fault-injection-sandbox":
        return page.evaluate(
            """() => {
              const canvas = document.querySelector("#fault-sandbox-replay-canvas-main");
              const canvasBox = canvas?.getBoundingClientRect();
              const failures = [];
              if (!canvas || !canvasBox) return {failures: ["missing replay canvas"], text_overflow: []};
              const nodeRects = new Map(Array.from(canvas.querySelectorAll("[data-replay-canvas-node]")).map((node) => {
                const box = node.getBoundingClientRect();
                return [node.dataset.replayCanvasNode || "", {
                  left: box.left - canvasBox.left,
                  right: box.right - canvasBox.left,
                  top: box.top - canvasBox.top,
                  bottom: box.bottom - canvasBox.top,
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
              }
              const text_overflow = Array.from(canvas.querySelectorAll(
                ".sandbox-replay-canvas-node strong, .sandbox-replay-canvas-node code, .sandbox-replay-canvas-metrics span"
              )).filter((element) => element.scrollWidth > element.clientWidth + 1)
                .map((element) => element.textContent || "");
              return {failures, text_overflow};
            }"""
        )
    return {"failures": [], "text_overflow": []}


def _capture_route(
    page: Any,
    base_url: str,
    route: dict[str, Any],
    viewport: dict[str, int | str],
    artifact_dir: Path,
) -> dict[str, Any]:
    page.set_viewport_size({"width": int(viewport["width"]), "height": int(viewport["height"])})
    page.goto(f"{base_url}{route['path']}", wait_until="networkidle")
    page.evaluate("() => window.scrollTo(0, 0)")
    if route.get("pre_capture_click"):
        page.locator(route["pre_capture_click"]).click()
    if route.get("pre_capture_visible"):
        page.locator(route["pre_capture_visible"]).wait_for(state="visible")
    visible = {name: _surface_state(page, selector) for name, selector in route["visible_surfaces"].items()}
    existing = {name: _surface_state(page, selector) for name, selector in route["existing_surfaces"].items()}
    clipped = {name: _clip_state(page, selector) for name, selector in route.get("clip_surfaces", {}).items()}
    geometry = _page_geometry(page, viewport)
    blueprint_geometry = _blueprint_geometry(page, route["key"])
    missing_visible = [name for name, state in visible.items() if not state["visible"]]
    missing_existing = [name for name, state in existing.items() if state["count"] < 1]
    clipped_surfaces = [name for name, state in clipped.items() if state["clipped"]]
    max_logic_top_band_height = route.get("max_logic_top_band_height")
    logic_top_band_ok = (
        max_logic_top_band_height is None
        or geometry["logic_top_band_height"] is None
        or geometry["logic_top_band_height"] <= max_logic_top_band_height
    )
    screenshot_name = f"{route['key']}--{viewport['name']}.png"
    screenshot_path = artifact_dir / screenshot_name
    page.screenshot(path=str(screenshot_path), full_page=False)
    route_ok = (
        geometry["vertical_scroll_ok"]
        and geometry["horizontal_overflow_count"] == 0
        and not missing_visible
        and not missing_existing
        and not clipped_surfaces
        and logic_top_band_ok
        and not blueprint_geometry["failures"]
        and not blueprint_geometry["text_overflow"]
    )
    return {
        "route": route["path"],
        "route_key": route["key"],
        "viewport": viewport,
        "screenshot": screenshot_name,
        "ok": route_ok,
        "geometry": geometry,
        "blueprint_geometry": blueprint_geometry,
        "visible_surfaces": visible,
        "existing_surfaces": existing,
        "clip_surfaces": clipped,
        "clipped_surfaces": clipped_surfaces,
        "logic_top_band_ok": logic_top_band_ok,
        "max_logic_top_band_height": max_logic_top_band_height,
        "missing_visible_surfaces": missing_visible,
        "missing_existing_surfaces": missing_existing,
    }


def _run_acceptance(base_url: str, artifact_dir: Path) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise SystemExit(f"Playwright is required for visual acceptance: {exc}") from exc

    def seed_payloads() -> None:
        page.evaluate(
            """(payloads) => {
              window.localStorage.clear();
              Object.entries(payloads).forEach(([key, value]) => {
                window.localStorage.setItem(key, JSON.stringify(value));
              });
            }""",
            _seed_payloads(),
        )

    artifact_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page()
            page.goto(f"{base_url}/index.html", wait_until="domcontentloaded")
            seed_payloads()
            for viewport in VIEWPORTS:
                for route in ROUTES:
                    seed_payloads()
                    entries.append(_capture_route(page, base_url, route, viewport, artifact_dir))
        finally:
            browser.close()

    failures = [
        {
            "route": entry["route"],
            "viewport": entry["viewport"]["name"],
            "missing_visible_surfaces": entry["missing_visible_surfaces"],
            "missing_existing_surfaces": entry["missing_existing_surfaces"],
            "vertical_scroll_ok": entry["geometry"]["vertical_scroll_ok"],
            "horizontal_overflow_count": entry["geometry"]["horizontal_overflow_count"],
            "horizontal_overflow_nodes": entry["geometry"]["horizontal_overflow_nodes"],
            "clipped_surfaces": entry["clipped_surfaces"],
            "blueprint_geometry_failures": entry["blueprint_geometry"]["failures"],
            "blueprint_text_overflow": entry["blueprint_geometry"]["text_overflow"],
            "logic_top_band_height": entry["geometry"]["logic_top_band_height"],
            "max_logic_top_band_height": entry["max_logic_top_band_height"],
            "logic_top_band_ok": entry["logic_top_band_ok"],
        }
        for entry in entries
        if not entry["ok"]
    ]
    summary = {
        "kind": "deepseek-ui-visual-acceptance",
        "generated_at": _utc_now(),
        "base_url": base_url,
        "viewports": VIEWPORTS,
        "route_count": len(ROUTES),
        "screenshot_count": len(entries),
        "ok": not failures,
        "failures": failures,
        "pages": entries,
    }
    summary_path = artifact_dir / "visual-acceptance-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="", help="Existing demo server base URL, for example http://127.0.0.1:8799")
    parser.add_argument("--port", type=int, default=8799, help="Port to use when --base-url is omitted")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR, help="Directory for PNG and JSON evidence")
    parser.add_argument("--ready-timeout", type=float, default=10.0, help="Seconds to wait for a spawned server")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(argv or sys.argv[1:]))
    proc: subprocess.Popen[bytes] | None = None
    if args.base_url:
        base_url = _normalize_base_url(args.base_url)
        if not _url_ready(base_url):
            print(f"Base URL is not ready: {base_url}", file=sys.stderr)
            return 2
    else:
        base_url = f"http://127.0.0.1:{args.port}"
        if not _url_ready(base_url):
            proc = _spawn_server(args.port)
            if not _wait_ready(base_url, args.ready_timeout):
                if proc:
                    _stop_server(proc)
                print(f"demo_server did not become ready at {base_url}", file=sys.stderr)
                return 2

    try:
        summary = _run_acceptance(base_url, args.artifact_dir)
    finally:
        if proc:
            _stop_server(proc)

    summary_path = args.artifact_dir / "visual-acceptance-summary.json"
    print(f"visual_acceptance_summary={summary_path}")
    print(f"screenshots={summary['screenshot_count']}")
    print(f"ok={str(summary['ok']).lower()}")
    if not summary["ok"]:
        print(json.dumps(summary["failures"], indent=2, ensure_ascii=False), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
