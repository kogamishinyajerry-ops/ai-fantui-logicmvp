from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"


class WorkbenchParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.node_ids: set[str] = set()
        self.elements: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        self.elements.append(attr_map)
        if attr_map.get("id"):
            self.ids.add(attr_map["id"])
        if attr_map.get("data-editable-node-id"):
            self.node_ids.add(attr_map["data-editable-node-id"])


def _html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def _css() -> str:
    return CSS_PATH.read_text(encoding="utf-8")


def _js() -> str:
    return JS_PATH.read_text(encoding="utf-8")


def _parsed() -> WorkbenchParser:
    parser = WorkbenchParser()
    parser.feed(_html())
    return parser


def test_editable_canvas_shell_primary_regions_exist() -> None:
    ids = _parsed().ids

    assert "workbench-editable-shell" in ids
    assert "workbench-editable-status-bar" in ids
    assert "workbench-derive-draft-btn" in ids
    assert "workbench-editor-toolbar" in ids
    assert "workbench-editable-canvas" in ids
    assert "workbench-evidence-inspector" in ids
    assert "workbench-sandbox-timeline-strip" in ids


def test_goal_canvas_panel_exposes_first_screen_engineering_regions() -> None:
    html = _html()
    css = _css()

    required_ids = {
        "workbench-goal-canvas-panel",
        "workbench-open-onboarding-guide-btn",
        "workbench-close-onboarding-guide-btn",
        "workbench-onboarding-title",
        "workbench-onboarding-detail",
        "workbench-onboarding-step-list",
        "workbench-onboarding-progress",
        "workbench-onboarding-back-btn",
        "workbench-onboarding-action-btn",
        "workbench-onboarding-next-btn",
    }
    assert required_ids.issubset(_parsed().ids)
    assert 'data-status-density="compact"' in html
    assert 'data-onboarding-active-step="overview"' in html
    assert 'data-onboarding-state="collapsed"' in html
    assert "新手指引" in html
    assert "关闭指引" in html
    assert "workbench-editable-canvas-note" not in html
    assert "Sandbox candidate canvas · edits here prepare diff evidence" not in html
    assert html.count("data-onboarding-step=") >= 7
    for step in (
        "overview",
        "inspect_node",
        "proof_path",
        "blank_canvas",
        "add_node",
        "wire",
        "run_sandbox",
    ):
        assert f'data-onboarding-step="{step}"' in html
    for copy in (
        "新手流程",
        "先看完整反推链路",
        "点 L1 看规则",
        "高亮 L4 proof",
        "进入空白画布",
        "添加一个 block",
        "进入连线模式",
        "运行 sandbox",
    ):
        assert copy in html
    assert ".workbench-goal-canvas-panel" in css
    assert ".workbench-onboarding-reopen-btn" in css
    assert ".workbench-goal-canvas-panel[hidden]" in css
    assert ".workbench-onboarding-step-list" in css
    assert "[data-onboarding-highlight=\"true\"]" in css
    assert ".workbench-editable-canvas-note" not in css
    assert ".workbench-editable-status-bar[data-status-density=\"compact\"]" in css
    assert ".workbench-editable-status-chip[data-status-visibility=\"secondary\"]" in css


def test_reference_visual_and_outsider_tutorial_contracts_are_exposed() -> None:
    html = _html()
    css = _css()
    js = _js()

    required_ids = {
        "workbench-outsider-circuit-explainer",
        "workbench-outsider-trigger-flow",
        "workbench-outsider-fault-notes",
        "workbench-outsider-simulation-value",
    }
    assert required_ids.issubset(_parsed().ids)
    for copy in (
        "这个逻辑电路究竟在实现什么功能",
        "为什么这么画",
        "输入信号开始每一步会发生什么",
        "预期会如何触发",
        "如果遇到故障会发生什么",
        "仿真按钮按下之后会看到什么",
        "仿真有什么价值",
        "THR_LOCK",
    ):
        assert copy in html
    for copy in (
        "这个电路的功能",
        "为什么这样画",
        "触发顺序",
        "故障会发生什么",
        "仿真会看到什么",
        "仿真的价值",
    ):
        assert copy in js
    assert '.workbench-editable-canvas[data-reference-proof-mode="default_visible"] .workbench-editable-edges path' in css
    assert "stroke-width: 3" in css
    assert "stroke-dasharray: none" in css
    assert "stroke-linecap: round" in css
    assert "referenceEdgeLaneX" in js
    assert "data-edge-source-id" in js
    assert "data-edge-target-id" in js
    assert "well-harness-workbench-onboarding-guide-open-v1" in js
    assert "setOnboardingGuideExpanded" in js


def test_editable_canvas_shell_is_explicitly_sandbox_only() -> None:
    html = _html()

    assert "sandbox candidate" in html
    assert "not certified truth" in html
    assert "真值影响" in html
    assert "无 · 仅沙箱候选" in html


def test_editable_canvas_exposes_reference_logic_nodes() -> None:
    parser = _parsed()
    html = _html()

    required_reference_nodes = {
        "ra_ft",
        "sw1",
        "not_inhibited",
        "not_deployed",
        "logic1",
        "tls_unlocked",
        "sw2",
        "engine_running",
        "aircraft_on_ground",
        "eec_enable",
        "logic2",
        "n1k_limit",
        "tra_deploy",
        "pls_unlocked",
        "logic3",
        "vdt90",
        "logic4",
        "thr_lock",
    }
    assert required_reference_nodes.issubset(parser.node_ids)
    for node_id in required_reference_nodes:
        assert f'data-editable-node-id="{node_id}"' in html
        assert f'data-reference-proof-node="{node_id}"' in html
    assert 'data-reference-graph="c919-etras-thrust-reverser-proof"' in html
    assert 'data-node-op="and"' in html
    assert 'data-node-op="compare"' in html
    assert 'data-node-op="latch"' in html
    assert 'data-node-op="output"' in html
    assert 'data-hardware-evidence="evidence_gap"' in html


def test_evidence_inspector_has_editable_and_read_only_fields() -> None:
    html = _html()

    assert 'id="workbench-inspector-node-label"' in html
    assert 'id="workbench-inspector-node-op"' in html
    assert 'id="workbench-inspector-evidence-status"' in html
    assert 'id="workbench-inspector-source-ref"' in html
    assert 'id="workbench-generate-handoff-btn"' in html
    assert 'id="workbench-linear-handoff-output"' in html
    assert 'id="workbench-pr-proof-output"' in html
    assert 'id="workbench-changerequest-packet-output"' in html
    assert 'data-evidence-api="/api/hardware/evidence?system_id=thrust-reverser"' in html


def test_runtime_generalization_proof_rail_is_adapter_backed_and_read_only() -> None:
    html = _html()
    css = _css()
    js = _js()

    assert 'id="workbench-runtime-generalization-proof"' in html
    assert 'id="workbench-runtime-proof-system-label"' in html
    assert 'id="workbench-runtime-proof-adapter-id"' in html
    assert 'id="workbench-runtime-proof-source"' in html
    assert 'id="workbench-runtime-proof-contracts"' in html
    assert 'id="workbench-runtime-proof-boundary"' in html
    assert 'data-runtime-proof-system="thrust-reverser"' in html
    assert "适配器运行证明" in html
    assert ".workbench-runtime-generalization-proof" in css
    assert ".workbench-runtime-proof-grid" in css
    assert "runtimeGeneralizationProofCatalog" in js
    assert "function renderRuntimeGeneralizationProofRail" in js
    assert "reference-deploy-controller" in js
    assert "c919-etras-controller-adapter" in js
    assert "src/well_harness/controller.py" in js
    assert "src/well_harness/adapters/c919_etras_adapter.py" in js
    assert "controller_truth_metadata" in js
    assert "control_system_spec" in js
    assert "playback_report" in js
    assert "fault_diagnosis_report" in js
    assert "knowledge_artifact" in js
    assert "ui_only_truth_path: false" in js
    assert "controller_truth_modified: false" in js
    assert 'truth_effect: "none"' in js


def test_evidence_inspector_declares_mode_tabs_and_default_node_mode() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-inspector-mode-tabs"' in html
    assert 'data-default-inspector-mode="node"' in html
    assert 'data-inspector-mode-active="node"' in html
    for mode, label in {
        "node": "节点详情",
        "run": "运行结果",
        "evidence": "硬件证据",
        "handoff": "交付包",
    }.items():
        assert f'data-inspector-mode="{mode}"' in html
        assert f'data-inspector-panel="{mode}"' in html
        assert f'id="workbench-inspector-{mode}-panel"' in html
        assert f'aria-controls="workbench-inspector-{mode}-panel"' in html
        assert label in html

    assert ".workbench-inspector-mode-tabs" in css
    assert '.workbench-inspector-mode-tabs button[aria-selected="true"]' in css
    assert (
        '.workbench-evidence-inspector[data-inspector-mode-active="node"] '
        '[data-inspector-panel]:not([data-inspector-panel="node"])'
    ) in css
    assert (
        '.workbench-evidence-inspector[data-inspector-mode-active="run"] '
        '[data-inspector-panel]:not([data-inspector-panel="run"])'
    ) in css
    assert (
        '.workbench-evidence-inspector[data-inspector-mode-active="evidence"] '
        '[data-inspector-panel]:not([data-inspector-panel="evidence"])'
    ) in css
    assert (
        '.workbench-evidence-inspector[data-inspector-mode-active="handoff"] '
        '[data-inspector-panel]:not([data-inspector-panel="handoff"])'
    ) in css


def test_reference_control_circuit_is_default_first_screen() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-reference-proof-strip"' in html
    assert 'id="workbench-canvas-first-guide"' in html
    assert 'id="workbench-canvas-first-start-btn"' in html
    assert 'id="workbench-load-reference-proof-btn"' in html
    assert 'id="workbench-reference-circuit-title"' in html
    assert 'id="workbench-reference-circuit-guide-strip"' in html
    assert 'data-reference-proof-target="logic1"' in html
    assert 'data-reference-proof-target="logic3"' in html
    assert 'data-reference-proof-target="logic4"' in html
    assert 'data-reference-proof-target="thr_lock"' in html
    assert 'data-reference-proof-mode="default_visible"' in html
    assert 'data-reference-proof-mode="canvas_first"' not in html
    assert "C919 E-TRAS / 反推逻辑控制电路" in html
    assert "看全图" in html
    assert "点节点" in html
    assert "选证明" in html
    assert "运行" in html
    assert "空白" in html
    assert "新建空白电路" in html
    assert "重置参考图" in html
    assert "C919 E-TRAS / 反推参考路径" in html
    assert "C919 E-TRAS 反推参考控制逻辑图 · Sandbox Draft Canvas" not in html
    assert "Reference sample pack" not in html
    assert '<details class="workbench-reference-sample-pack">' not in html
    assert '.workbench-editable-canvas[data-reference-proof-mode="empty_authoring"] .workbench-canvas-first-guide' in css
    assert '.workbench-reference-circuit-guide-strip' in css
    assert '.workbench-reference-circuit-title' in css


def test_reference_logic_proof_strip_and_highlights_are_styled() -> None:
    css = _css()

    assert ".workbench-reference-proof-strip" in css
    assert ".workbench-reference-proof-strip button" in css
    assert '.workbench-reference-proof-strip button[aria-pressed="true"]' in css
    assert '.workbench-editable-node[data-proof-highlight="true"]' in css
    assert '.workbench-editable-edges path[data-edge-proof-highlight="true"]' in css
    assert "data-edge-proof-highlight" in css


def test_reference_logic_rule_summary_has_inspector_surface() -> None:
    html = _html()

    assert 'id="workbench-inspector-rule-summary"' in html
    assert 'data-rule-summary="L4 同时要求' in html
    assert 'data-rule-summary="L1 同时要求' in html


def test_canvas_dominant_viewport_contracts_are_declared() -> None:
    html = _html()
    css = _css()
    js = _js()

    assert 'data-canvas-dominant="true"' in html
    assert 'data-guide-density="compact"' in html
    assert 'data-inspector-layout="overlay_rail"' in html
    assert 'data-free-canvas-pan="enabled"' in html
    assert '.workbench-editable-main[data-canvas-dominant="true"]' in css
    assert '.workbench-evidence-inspector[data-inspector-layout="overlay_rail"]' in css
    assert '.workbench-canvas-first-guide[data-guide-density="compact"]' in css
    assert "grid-template-columns: minmax(0, 1fr)" in css
    assert "function shouldBeginViewportPan" in js
    assert "direct_blank_canvas_drag" in js
    assert "wheel_mouse_anchor" in js


def test_reference_graph_readability_contracts_are_declared() -> None:
    html = _html()
    css = _css()
    js = _js()

    assert 'data-guide-entry="primary"' in html
    assert "新手指引" in html
    assert "function nodeDisplayLabel" in js
    assert "function nodeShortDisplayLabel" in js
    assert "data-node-short-label" in js
    assert "data-node-full-label" in js
    assert "function compactSignalDisplayLabel" in js
    assert "data-port-short-label" in js
    assert "data-edge-display-label" in js
    assert "function editableNodeRoutePosition" in js
    assert "halfXPercent" in js
    assert "data-node-label" in js
    assert ".workbench-editable-node[data-node-short-label] span" in css
    assert ".workbench-port-handle::after" in css
    assert ".workbench-reference-node-op" in css
    assert ".workbench-editor-toolstrip" in css
    assert "bottom: 0.65rem" in css
    assert ".workbench-reference-proof-strip" in css
    assert "bottom: 3.45rem" in css


def test_reference_graph_chinese_first_wire_visibility_contracts_are_declared() -> None:
    html = _html()
    css = _css()
    js = _js()

    for copy in (
        "无线电高度低于 6 英尺",
        "反推未抑制",
        "L1 高度/SW1 允许门",
        "L4 部署/油门锁门",
        "油门锁释放指令",
        "证据检查器",
        "候选节点名称",
        "规则摘要",
        "运行沙箱",
        "变更包",
    ):
        assert copy in html or copy in js

    assert 'data-inspector-open="false"' in html
    assert "function setInspectorOpen" in js
    assert "marker-end" in js
    assert "--reference-wire-color" in css
    assert "stroke-width: 5.25" in css
    assert ".workbench-editable-edges marker" in css
    for english_copy in (
        "Evidence Inspector",
        "Candidate label",
        "Operation",
        "Rule summary",
        "Run sandbox",
        "ChangeRequest packet",
        "Baseline loaded",
        "Draft editable",
        "Selected Debug Timeline",
    ):
        assert english_copy not in html


def test_reference_logic_proof_canvas_is_low_text() -> None:
    html = _html()
    node_bodies = re.findall(
        r'<button[^>]+class="workbench-editable-node"[^>]*>(.*?)</button>',
        html,
        re.DOTALL,
    )

    assert len(node_bodies) >= 18
    for body in node_bodies:
        text = re.sub(r"<[^>]+>", " ", body)
        normalized = " ".join(text.split())
        assert normalized in {"IN", "OUT", "AND", "OR", "CMP", "BTW", "DLY", "LAT", "LCH"}
        assert "logic" not in normalized.lower()
        assert "source" not in normalized.lower()
        assert len(normalized) <= 4


def test_css_declares_editable_workbench_layout() -> None:
    css = _css()

    assert ".workbench-editable-shell" in css
    assert ".workbench-editable-main" in css
    assert "grid-template-rows: minmax(0, 1fr) auto auto" in css
    assert "grid-template-columns: minmax(0, 1fr)" in css
    assert '.workbench-editable-main[data-canvas-dominant="true"]' in css
    assert ".workbench-editor-toolbar" in css
    assert ".workbench-evidence-inspector" in css
    assert '.workbench-evidence-inspector[data-inspector-layout="overlay_rail"]' in css
    assert "grid-template-columns: repeat(5, minmax(0, 1fr))" in css
    assert "height: calc(100vh - 0.8rem)" in css
    assert "overflow: hidden" in css
    assert "overflow-y: auto" in css
    assert ".workbench-sandbox-timeline-strip" in css
    assert ".workbench-selected-debug-timeline" in css


def test_workbench_shell_exposes_local_release_maturity_rail() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-release-maturity-rail"' in html
    assert 'data-release-maturity-scope="local_only"' in html
    assert 'data-release-maturity-truth-effect="none"' in html
    assert "发布成熟度" in html
    assert "本地运行" in html
    assert "未声明" in html
    assert "仅本地证据" in html
    assert "controller truth unchanged" in html
    for status in ("pass", "warning", "blocked", "rerun_required", "not_claimed"):
        assert f'data-release-gate-status="{status}"' in html
        assert f'[data-release-gate-status="{status}"]' in css
    assert ".workbench-release-maturity-rail" in css


def test_cockpit_editor_skin_makes_canvas_the_primary_work_surface() -> None:
    html = _html()
    css = _css()
    js = _js()

    assert 'data-workbench-skin="cockpit-editor"' in html
    assert 'data-hud-role="cockpit-status"' in html
    assert 'data-hud-primary="canvas"' in html
    assert 'id="workbench-cockpit-guide-coach"' in html
    assert 'id="workbench-cockpit-guide-coach-title"' in html
    assert 'id="workbench-cockpit-guide-coach-detail"' in html
    assert 'id="workbench-cockpit-inspector-close-btn"' in html
    assert 'aria-label="关闭检查器"' in html
    assert "参考控制器 · 已认证" in html
    assert "初始化" in html
    assert "动作" in html
    assert "撤销" in html
    assert "重做" in html
    assert "节点" in html
    assert "连线" in html
    assert "名义着陆" in html
    assert "SW1 着陆卡滞" in html
    assert "未运行" in html
    assert "仅选择" in html
    assert "证据缺口" in html

    for internal_copy in (
        "reference-deploy-controller · certified",
        ">ui_draft_pending<",
        ">init<",
        "actions <b",
        "undo <b",
        "redo <b",
        "nodes <b",
        "edges <b",
        ">nominal_landing<",
        ">sw1_stuck_at_touchdown<",
        ">not_run<",
        ">selection_only<",
        ">evidence_gap<",
    ):
        assert internal_copy not in html

    assert "--workbench-cockpit-bg" in css
    assert "--workbench-cockpit-panel" in css
    assert "--workbench-cockpit-accent" in css
    assert "--workbench-cockpit-active" in css
    assert '.workbench-editable-shell[data-workbench-skin="cockpit-editor"]' in css
    assert '.workbench-editable-status-bar[data-hud-role="cockpit-status"]' in css
    assert ".workbench-cockpit-guide-coach" in css
    assert ".workbench-cockpit-guide-coach[hidden]" in css
    assert ".workbench-cockpit-inspector-close" in css
    assert "function displayStatusLabel" in js
    assert "function renderCockpitGuideCoach" in js
    assert "function closeCockpitInspectorOverlay" in js


def test_phase10_secondary_status_summaries_use_chinese_display_labels() -> None:
    js = _js()

    for expected in (
        'displayStatusLabel(summary.status || "unknown")',
        'displayStatusLabel(summary.status || "not_run")',
        'displayStatusLabel(summary.coverage_status || "missing")',
        'displayStatusLabel(summary.validation_status || "not_run")',
        'displayStatusLabel(summary.scenario_id || "nominal_landing")',
        'displayStatusLabel(summary.diff_verdict || "not_run")',
        'displayStatusLabel(summary.trace_link_status || "selection_only")',
        'displayStatusLabel(summary.verdict || "not_run")',
        'displayStatusLabel(summary.review_readiness || "run_required")',
        'displayStatusLabel(summary.archive_state || "not_archive_ready")',
        'displayStatusLabel(summary.classification || "needs_evidence")',
        'displayStatusLabel(summary.sandbox_report_freshness || "missing")',
    ):
        assert expected in js

    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_css_declares_compact_simulink_like_canvas_blocks() -> None:
    css = _css()

    assert "width: 138px" in css
    assert "width: 96px" in css
    assert "min-height: 48px" in css
    assert "border-radius: 3px" in css
    assert "font-size: 0.62rem" in css
    assert "width: 10px" in css
    assert "height: 10px" in css
    assert "border-radius: 1px" in css
    assert "data-simulink-skin" in _html()
    assert "stroke-dasharray: 6 4" in css
    assert ".workbench-edge-label" in css
    assert "display: none" in css


def test_simulink_blocks_hide_verbose_node_text_in_canvas_body() -> None:
    html = _html()
    node_bodies = re.findall(
        r'<button[^>]+class="workbench-editable-node"[^>]*>(.*?)</button>',
        html,
        re.DOTALL,
    )

    assert node_bodies
    for body in node_bodies:
        text = re.sub(r"<[^>]+>", " ", body)
        assert "rules" not in text
        assert "control_system_spec" not in text
        assert "binding" not in text.lower()
        assert re.search(r"\b(IN|OUT|AND|OR|CMP|BTW|DLY|LAT|LCH)\b", text)


def test_main_toolbar_is_compact_with_tooltips_and_deferred_toolstrip() -> None:
    html = _html()
    css = _css()

    required_main_tools = {
        "select": "选择：点选 block 或信号线",
        "node": "新建 block：使用当前原语添加节点",
        "edge": "连线：从输出端口拖到输入端口",
        "pan": "平移/缩放：拖动画布或使用缩放工具",
        "remove": "删除：移除选中的节点或连线",
    }
    for tool, tooltip in required_main_tools.items():
        assert f'data-editor-tool="{tool}"' in html
        assert f'data-tool-primary="true"' in html
        assert f'data-tooltip="{tooltip}"' in html
    assert 'id="workbench-open-command-palette-btn"' in html
    assert 'data-tool-primary="true"' in html
    assert 'data-tooltip="命令面板：搜索并执行工作台命令"' in html
    assert 'id="workbench-editor-toolstrip"' in html
    assert 'data-toolstrip-group="edit-history"' in html
    assert 'data-toolstrip-group="catalog"' in html
    assert 'data-toolstrip-group="library"' in html
    assert ".workbench-editor-toolstrip" in css
    assert ".workbench-tooltip-surface" in css
    assert 'data-viewport-tool="zoom-in">Z+' not in html
    assert 'data-viewport-tool="fit-selection">FIT' not in html
    assert ">CAP</button>" not in html
    assert ">INS</button>" not in html


def test_editor_command_palette_controls_are_exposed_as_sandbox_only_ui() -> None:
    html = _html()
    css = _css()
    palette_match = re.search(
        r'<section\s+id="workbench-command-palette"[\s\S]*?</section>',
        html,
    )
    assert palette_match is not None
    palette_html = palette_match.group(0)

    assert 'id="workbench-open-command-palette-btn"' in html
    assert 'id="workbench-command-palette"' in html
    assert 'id="workbench-command-palette-filter"' in html
    assert 'id="workbench-command-palette-status"' in html
    assert 'aria-label="关闭命令面板"' in palette_html
    assert "命令面板空闲。不会执行实时 Linear 写入。" in palette_html
    expected_commands = [
        ("create_node", "创建节点", "create add node primitive"),
        ("rename_subsystem", "重命名子系统", "rename subsystem group"),
        ("duplicate_selection", "复制选择", "duplicate copy selection node"),
        ("group_selection", "封装为子系统", "group subsystem selection"),
        ("wire_edge", "连接端口", "wire edge connect route"),
        ("run_sandbox", "运行沙箱", "run sandbox simulation"),
        ("debug_selection", "调试选择", "debug selection timeline probe"),
        ("export_draft", "导出草稿", "export draft json"),
        ("import_draft", "导入草稿", "import draft json restore"),
        ("prepare_archive", "准备归档", "archive evidence prepare handoff"),
    ]
    for command_id, label, keywords in expected_commands:
        assert f'data-command-palette-command="{command_id}"' in html
        assert f'data-command-palette-keywords="{keywords}"' in html
        assert f">{label}</button>" in palette_html
    for stale_label in (
        "Close command palette",
        "Rename subsystem",
        "Duplicate selection",
        "Group selection",
        "Wire edge",
        "Debug selection",
    ):
        assert stale_label not in palette_html
    assert ".workbench-command-palette" in css
    assert ".workbench-command-palette-list" in css


def test_component_library_templates_are_exposed_as_sandbox_toolbar_controls() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-component-library"' in html
    assert 'id="workbench-component-library-status"' in html
    assert 'id="workbench-capture-subsystem-template-btn"' in html
    assert 'id="workbench-insert-captured-template-btn"' in html
    assert 'data-component-template-id="single_and_gate"' in html
    assert 'data-component-template-id="compare_guard"' in html
    assert 'data-component-template-id="two_stage_interlock"' in html
    assert ".workbench-component-library" in css
    assert ".workbench-component-library-status" in css


def test_empty_canvas_authoring_controls_are_exposed_as_sandbox_toolbar_controls() -> None:
    html = _html()
    js = _js()

    assert 'id="workbench-start-empty-draft-btn"' in html
    assert 'data-op-catalog-op="input"' in html
    assert 'data-op-catalog-op="output"' in html
    assert '<option value="input">input</option>' in html
    assert '<option value="output">output</option>' in html
    assert "startEmptyCanvasDraft" in js
    assert "start_empty_canvas_draft" in js
    assert "canvas_authoring_mode" in js
    assert "empty_authoring" in js
    assert '"input"' in js
    assert '"output"' in js


def test_subsystem_group_editor_controls_are_exposed_as_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'data-editor-tool="group"' in html
    assert 'data-editor-tool="ungroup"' in html
    assert 'id="workbench-subsystem-editor"' in html
    assert 'data-subsystem-workflow-state="idle"' in html
    assert "子系统封装" in html
    assert 'id="workbench-subsystem-selection-count"' in html
    assert 'id="workbench-subsystem-active-name"' in html
    assert 'id="workbench-subsystem-workflow-state"' in html
    assert 'id="workbench-subsystem-name"' in html
    assert "子系统名称" in html
    assert 'id="workbench-create-subsystem-btn"' in html
    assert 'id="workbench-rename-subsystem-btn"' in html
    assert 'id="workbench-ungroup-subsystem-btn"' in html
    assert ">封装<" in html
    assert ">重命名<" in html
    assert ">解除封装<" in html
    assert 'id="workbench-subsystem-status"' in html
    assert 'role="status"' in html
    assert 'aria-live="polite"' in html
    assert 'data-status-tone="info"' in html
    assert "子系统编辑仅写入 sandbox metadata。Truth effect: none." in html
    assert ".workbench-subsystem-workflow-summary" in css
    assert ".workbench-subsystem-overlay" in css
    assert '.workbench-subsystem-overlay[data-subsystem-active="true"]' in css
    assert '.workbench-subsystem-overlay[data-subsystem-workflow-state="grouped"]' in css
    assert ".workbench-subsystem-overlay-label" in css
    assert ".workbench-subsystem-overlay-meta" in css
    assert '.workbench-editable-node[data-subsystem-id]:hover' in css
    assert '.workbench-editable-node[data-subsystem-active="true"]' in css
    assert '#workbench-subsystem-editor[data-subsystem-workflow-state="ready_to_group"]' in css
    assert '#workbench-subsystem-editor[data-subsystem-workflow-state="grouped"]' in css
    assert '#workbench-subsystem-editor[data-subsystem-workflow-state="ungrouped"]' in css
    assert '#workbench-subsystem-status[data-status-tone="success"]' in css
    assert '#workbench-subsystem-status[data-status-tone="warn"]' in css
    assert ".workbench-subsystem-editor" in css


def test_subsystem_interface_contract_editor_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-subsystem-interface-contract"' in html
    assert 'id="workbench-subsystem-interface-owner"' in html
    assert 'id="workbench-subsystem-interface-direction"' in html
    assert 'id="workbench-subsystem-interface-label"' in html
    assert 'id="workbench-subsystem-interface-signal-id"' in html
    assert 'id="workbench-subsystem-interface-value-type"' in html
    assert 'id="workbench-subsystem-interface-evidence-status"' in html
    assert 'id="workbench-add-subsystem-interface-port-btn"' in html
    assert 'id="workbench-remove-subsystem-interface-port-btn"' in html
    assert 'id="workbench-subsystem-interface-contract-list"' in html
    assert "Subsystem boundary ports are sandbox interface contracts only. Truth effect: none." in html
    assert ".workbench-subsystem-interface-contract" in css
    assert ".workbench-subsystem-interface-row" in css


def test_connector_pin_map_editor_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-connector-pin-map-editor"' in html
    assert 'id="workbench-export-connector-pin-map-btn"' in html
    assert 'id="workbench-apply-connector-pin-map-btn"' in html
    assert 'id="workbench-connector-pin-map-output"' in html
    assert 'id="workbench-connector-pin-map-status"' in html
    assert "Connector and pin metadata is local sandbox evidence only. Truth effect: none." in html
    assert ".workbench-connector-pin-map-editor" in css


def test_hardware_evidence_v2_inspector_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-hardware-evidence-v2"' in html
    assert 'id="workbench-hardware-evidence-v2-target"' in html
    assert 'id="workbench-hardware-evidence-v2-coverage"' in html
    assert 'id="workbench-hardware-evidence-v2-gap-count"' in html
    assert 'id="workbench-hardware-evidence-v2-pin-rows"' in html
    assert 'id="workbench-hardware-evidence-v2-fields"' in html
    assert "Hardware/interface fields are review evidence only" in html
    assert ".workbench-hardware-evidence-v2" in css
    assert ".workbench-hardware-evidence-v2-row" in css


def test_hardware_interface_designer_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-hardware-interface-designer"' in html
    assert 'id="workbench-export-hardware-interface-design-btn"' in html
    assert 'id="workbench-validate-hardware-interface-design-btn"' in html
    assert 'id="workbench-apply-hardware-interface-design-btn"' in html
    assert 'id="workbench-hardware-interface-design-output"' in html
    assert 'id="workbench-hardware-interface-design-validation-output"' in html
    assert 'id="workbench-hardware-interface-design-status"' in html
    assert "Hardware/interface design records are sandbox evidence only. Truth effect: none." in html
    assert ".workbench-hardware-interface-designer" in css


def test_selected_debug_timeline_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-selected-debug-timeline"' in html
    assert 'id="workbench-selected-debug-target"' in html
    assert 'id="workbench-selected-debug-scenario"' in html
    assert 'id="workbench-selected-debug-verdict"' in html
    assert 'id="workbench-selected-debug-link-status"' in html
    assert 'id="workbench-selected-debug-hardware"' in html
    assert 'id="workbench-selected-debug-context"' in html
    assert "Truth effect: none" in html
    assert ".workbench-selected-debug-timeline-facts" in css
    assert ".workbench-selected-debug-context" in css


def test_diff_review_v2_controls_are_sandbox_only_archive_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-diff-review-v2"' in html
    assert 'id="workbench-diff-review-v2-status"' in html
    assert 'id="workbench-diff-review-v2-target"' in html
    assert 'id="workbench-diff-review-v2-readiness"' in html
    assert 'id="workbench-diff-review-v2-archive-state"' in html
    assert 'id="workbench-diff-review-v2-divergence"' in html
    assert 'id="workbench-diff-review-v2-claim"' in html
    assert "Candidate diff review is archive evidence only" in html
    assert ".workbench-diff-review-v2" in css
    assert ".workbench-diff-review-v2-facts" in css


def test_candidate_debugger_view_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-candidate-debugger-view"' in html
    assert 'id="workbench-candidate-debugger-status"' in html
    assert 'id="workbench-candidate-debugger-target"' in html
    assert 'id="workbench-candidate-debugger-tick"' in html
    assert 'id="workbench-candidate-debugger-assertion"' in html
    assert 'id="workbench-candidate-debugger-observed"' in html
    assert 'id="workbench-candidate-debugger-trace"' in html
    assert "Candidate debugger is sandbox evidence only. Truth effect: none." in html
    assert ".workbench-candidate-debugger-view" in css
    assert ".workbench-candidate-debugger-facts" in css


def test_scenario_failure_explanation_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-scenario-failure-explanation"' in html
    assert 'id="workbench-failure-explanation-status"' in html
    assert 'id="workbench-failure-explanation-assertion"' in html
    assert 'id="workbench-failure-explanation-frame"' in html
    assert 'id="workbench-failure-explanation-owner"' in html
    assert 'id="workbench-failure-explanation-current"' in html
    assert 'id="workbench-failure-explanation-expected"' in html
    assert 'id="workbench-failure-explanation-upstream"' in html
    assert 'id="workbench-failure-explanation-truth-effect"' in html
    assert 'id="workbench-failure-explanation-focus-owner-btn"' in html
    assert 'id="workbench-failure-explanation-focus-frame-btn"' in html
    assert 'id="workbench-failure-explanation-navigation-status"' in html
    assert "定位责任元件" in html
    assert "标记时间帧" in html
    assert "Failure explanation is sandbox evidence only. Truth effect: none." in html
    assert ".workbench-scenario-failure-explanation" in css
    assert ".workbench-failure-explanation-facts" in css
    assert ".workbench-failure-explanation-actions" in css


def test_preflight_analyzer_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-preflight-analyzer"' in html
    assert 'id="workbench-run-preflight-btn"' in html
    assert 'id="workbench-preflight-classification"' in html
    assert 'id="workbench-preflight-findings-count"' in html
    assert 'id="workbench-preflight-actions"' in html
    assert 'id="workbench-preflight-output"' in html
    assert "Preflight analyzer is sandbox evidence only. Truth effect: none." in html
    assert ".workbench-preflight-analyzer" in css
    assert ".workbench-preflight-facts" in css


def test_workspace_document_status_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-workspace-document-status"' in html
    assert 'id="workbench-workspace-document-revision"' in html
    assert 'id="workbench-workspace-document-action-count"' in html
    assert 'id="workbench-workspace-document-undo-depth"' in html
    assert 'id="workbench-workspace-document-redo-depth"' in html
    assert "工作区文档仅作为沙箱证据。真值影响：无。" in html
    assert ".workbench-workspace-document-status" in css
    assert ".workbench-workspace-document-facts" in css


def test_canvas_interaction_status_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-canvas-interaction-status"' in html
    assert 'id="workbench-canvas-selected-node-count"' in html
    assert 'id="workbench-canvas-selected-edge-count"' in html
    assert 'id="workbench-canvas-last-action"' in html
    assert "画布交互仅作为沙箱证据。真值影响：无。" in html
    assert ".workbench-canvas-interaction-status" in css
    assert ".workbench-canvas-interaction-facts" in css


def test_js_wires_draft_derivation_node_selection_and_evidence_api() -> None:
    js = _js()

    assert "function installEditableWorkbenchShell" in js
    assert "well-harness-editable-workbench-draft-v1" in js
    assert "workbench-derive-draft-btn" in js
    assert "data-editable-node-id" in js
    assert "workbench-inspector-node-label" in js
    assert "data-evidence-api" in js


def test_js_wires_reference_proof_buttons_and_rule_summary() -> None:
    js = _js()

    assert "const referenceProofButtons" in js
    assert "function applyReferenceProofPath" in js
    assert "button.addEventListener(\"click\"" in js
    assert "applyReferenceProofPath(button.getAttribute(\"data-reference-proof-target\"))" in js
    assert "workbench-inspector-rule-summary" in js
    assert "data-rule-summary" in js
    assert "clearReferenceProofHighlight()" in js


def test_js_wires_component_library_round_trip_as_sandbox_only_metadata() -> None:
    js = _js()

    assert "editable-component-library.v1" in js
    assert "componentLibraryTemplates" in js
    assert "capturedSubsystemTemplates" in js
    assert "function captureSelectedSubsystemTemplate" in js
    assert "function insertLatestCapturedSubsystemTemplate" in js
    assert "function instantiateComponentTemplate" in js
    assert "function buildComponentLibrarySummary" in js
    assert "captured_subsystem_templates" in js
    assert "captured_templates" in js
    assert "ui_draft.component_library" in js
    assert "component_template" in js
    assert "component_library" in js
    assert 'component_library truth_effect must be none' in js
    assert 'captured subsystem template truth_effect must be none' in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_subsystem_group_round_trip_as_sandbox_only_metadata() -> None:
    js = _js()

    assert "function groupSelectedDraftNodes" in js
    assert "function renameSelectedSubsystemGroup" in js
    assert "function ungroupSelectedSubsystem" in js
    assert "function updateSubsystemWorkflowSummary" in js
    assert "function setSubsystemWorkflowState" in js
    assert "function renderSubsystemOverlays" in js
    assert "function setSubsystemStatus" in js
    assert "function syncSubsystemActiveAffordance" in js
    assert "let hoveredSubsystemGroupId" in js
    assert "function setHoveredSubsystemGroupFromNode" in js
    assert 'addEventListener("mouseenter"' in js
    assert 'addEventListener("mouseleave"' in js
    assert 'setAttribute("data-status-tone", tone)' in js
    assert 'setAttribute("data-subsystem-workflow-state", state)' in js
    assert 'setAttribute("data-subsystem-selected-count"' in js
    assert 'setAttribute("data-subsystem-name"' in js
    assert '"ready_to_group"' in js
    assert '"grouped"' in js
    assert '"renamed"' in js
    assert '"ungrouped"' in js
    assert "subsystem_groups" in js
    assert "subsystem_groups truth_effect must be none" in js
    assert "subsystem_groups_checksum" in js
    assert "data-subsystem-id" in js
    assert "data-subsystem-active" in js
    assert "data-subsystem-node-count" in js
    assert "Sandbox metadata. Truth effect none." in js
    assert "truth effect none" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_subsystem_interface_contracts_as_sandbox_only_metadata() -> None:
    js = _js()

    assert "function normalizeSubsystemInterfaceContractRecord" in js
    assert "function addSubsystemInterfaceContractPort" in js
    assert "function removeSubsystemInterfaceContractPort" in js
    assert "function buildSubsystemInterfaceContractsSummary" in js
    assert "subsystem_interface_contracts" in js
    assert "subsystem_interface_contracts_checksum" in js
    assert "subsystem interface contracts truth_effect must be none" in js
    assert "data-subsystem-interface-port-id" in js
    assert 'kind: "well-harness-workbench-subsystem-interface-contracts"' in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_workspace_document_round_trip_as_sandbox_only_metadata() -> None:
    js = _js()

    assert "workbench-workspace-document.v1" in js
    assert "well-harness-workbench-workspace-document" in js
    assert "function currentWorkspaceDocument" in js
    assert "function updateWorkspaceDocumentRevision" in js
    assert "function renderWorkspaceDocumentStatus" in js
    assert "workspace_document" in js
    assert "workspace_document_checksum" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_canvas_interaction_summary_as_sandbox_only_metadata() -> None:
    js = _js()

    assert "well-harness-workbench-canvas-interaction-summary" in js
    assert "function currentCanvasInteractionSummary" in js
    assert "function renderCanvasInteractionStatus" in js
    assert "function recordCanvasInteractionAction" in js
    assert "canvas_interaction_summary" in js
    assert "canvas_interaction_summary_checksum" in js
    assert "canvas_interaction_summary truth_effect must be none" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_editable_graph_document_as_canonical_sandbox_metadata() -> None:
    js = _js()

    assert "well-harness-workbench-editable-graph-document" in js
    assert "workbench-editable-graph-document.v2" in js
    assert "workbench-editable-graph-document.v1" in js
    assert "function buildEditableGraphDocumentFromSnapshot" in js
    assert "function buildEditableGraphCanonicalModel" in js
    assert "function buildEditableGraphDomAdapterBoundary" in js
    assert "function graphDocumentDraftState" in js
    assert "editable_graph_document" in js
    assert "editable_graph_document_checksum" in js
    assert "editable_graph_document truth_effect must be none" in js
    assert "editable_graph_document ${key} must match draft payload" in js
    assert "canonical_model" in js
    assert "dom_adapter" in js
    assert "accepted_import_versions" in js
    assert "top_level_compatibility" in js
    assert "position_digest" in js
    assert "node_count" in js
    assert "edge_count" in js
    assert "typed_port_count" in js
    assert "subsystem_group_count" in js
    assert "selected_state" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_port_wire_route_metadata_as_sandbox_only_graph_evidence() -> None:
    js = _js()

    assert "workbench-edge-route-metadata.v1" in js
    assert "function normalizeEdgeRouteMetadata" in js
    assert "function edgeWireLabel" in js
    assert "function edgeWireDisplayLabel" in js
    assert "function orthogonalRouteResult" in js
    assert "function edgeRouteGuideMetadata" in js
    assert "function edgeRouteGuideAttributes" in js
    assert "edge_label" in js
    assert "route_metadata" in js
    assert "data-edge-label" in js
    assert "data-edge-display-label" in js
    assert "data-route-mode" in js
    assert "data-route-guide" in js
    assert "data-route-guide-effect" in js
    assert "data-route-segment-count" in js
    assert "data-route-lane-axis" in js
    assert "data-route-direction" in js
    assert "data-route-guide-truth-effect" in js
    assert "workbench-edge-label" in js
    assert "workbench-edge-route-guide" in js
    assert ".workbench-edge-route-guide" in _css()
    assert 'data-route-guide-edge-id' in js
    assert "function beginPortHandleDrag" in js
    assert "function updatePortHandleDrag" in js
    assert "function completePortHandleDrag" in js
    assert "function portShortDisplayLabel" in js
    assert "data-port-short-label" in js
    assert "data-port-signal-short-label" in js
    assert "data-port-drag-state" in js
    assert "data-port-drag-compatibility" in js
    assert "workbench-port-drag-preview" in js
    assert "ui_draft.port_drag_wiring" in js
    assert "port_compatibility_report" in js
    assert "port_compatibility_report_checksum" in js
    assert ".workbench-port-drag-preview" in _css()
    assert ".workbench-port-handle::after" in _css()
    assert 'truth_effect: "none"' in js


def test_sandbox_scenario_test_bench_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-sandbox-test-bench"' in html
    assert 'id="workbench-test-case-library-select"' in html
    assert 'id="workbench-test-case-name"' in html
    assert 'id="workbench-create-test-case-btn"' in html
    assert 'id="workbench-save-test-case-btn"' in html
    assert 'id="workbench-duplicate-test-case-btn"' in html
    assert 'id="workbench-delete-test-case-btn"' in html
    assert 'id="workbench-test-bench-inputs-json"' in html
    assert 'id="workbench-test-bench-assertions-json"' in html
    assert 'id="workbench-test-case-expected-outputs-json"' in html
    assert 'id="workbench-test-case-notes"' in html
    assert 'id="workbench-run-test-bench-btn"' in html
    assert 'id="workbench-test-case-library-status"' in html
    assert 'id="workbench-test-bench-status"' in html
    assert 'id="workbench-test-bench-report-output"' in html
    assert "Scenario tests are local sandbox evidence only. Truth effect: none." in html
    assert "Saved test cases are sandbox_candidate evidence only." in html
    assert ".workbench-sandbox-test-bench" in css
    assert ".workbench-test-case-library-actions" in css


def test_js_wires_sandbox_scenario_test_bench_as_sandbox_only_run_report() -> None:
    js = _js()

    assert "well-harness-workbench-sandbox-test-bench" in js
    assert "workbench-sandbox-test-bench.v1" in js
    assert "well-harness-workbench-sandbox-test-run-report" in js
    assert "workbench-sandbox-test-run-report.v1" in js
    assert "well-harness-workbench-scenario-test-case-library" in js
    assert "workbench-scenario-test-case-library.v1" in js
    assert "function currentScenarioTestCaseLibrary" in js
    assert "function restoreScenarioTestCaseLibrary" in js
    assert "function currentSandboxTestBenchDefinition" in js
    assert "function evaluateSandboxTestBench" in js
    assert "function renderSandboxTestBenchReport" in js
    assert "scenario_test_case_library" in js
    assert "selected_test_case_id" in js
    assert "active_test_case_id" in js
    assert "sandbox_test_bench" in js
    assert "sandbox_test_run_report" in js
    assert "scenario_test_case_library_checksum" in js
    assert "sandbox_test_bench_checksum" in js
    assert "sandbox_test_run_report_checksum" in js
    assert "sandbox_test_run_report truth_effect must be none" in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_sandbox_runner_trace_kernel_v2_as_sandbox_only_report() -> None:
    js = _js()

    assert "well-harness-workbench-sandbox-runner-trace-kernel" in js
    assert "workbench-sandbox-runner-trace-kernel.v2" in js
    assert "function buildSandboxRunnerTraceKernel" in js
    assert "function prepareSandboxRunnerGraph" in js
    assert "function sandboxRunnerTraceKernelChecksum" in js
    assert "sandbox_runner_trace_kernel" in js
    assert "sandbox_runner_trace_kernel_checksum" in js
    assert "node_values" in js
    assert "port_values" in js
    assert "edge_values" in js
    assert "assertion_results" in js
    assert "evaluation_order" in js
    assert "cycle_detected" in js
    assert "dangling_edge" in js
    assert "unsupported_op" in js
    assert "missing_input" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_connector_pin_map_round_trip_as_sandbox_only_metadata() -> None:
    js = _js()

    assert "function buildWorkbenchConnectorPinMap" in js
    assert "function validateConnectorPinMapPayload" in js
    assert "function applyWorkbenchConnectorPinMap" in js
    assert "connector_pin_map" in js
    assert "connector_pin_map_checksum" in js
    assert "pin_local" in js
    assert "pin_peer" in js
    assert "connector pin map truth_effect must be none" in js
    assert 'truth_effect: "none"' in js


def test_js_wires_hardware_evidence_v2_as_sandbox_only_selected_owner_packet() -> None:
    js = _js()

    assert "function buildHardwareEvidenceV2Report" in js
    assert "function currentHardwareEvidenceV2Report" in js
    assert "function renderHardwareEvidenceV2Report" in js
    assert "hardwareEvidenceV2GapFields" in js
    assert "hardware_evidence_v2" in js
    assert "hardware_evidence_v2_checksum" in js
    assert "hardware_evidence_v2 truth_effect must be none" in js
    assert "Hardware evidence v2:" in js
    assert 'kind: "well-harness-workbench-hardware-evidence-inspector-v2"' in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_hardware_evidence_attachment_v2_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "well-harness-workbench-hardware-evidence-attachment" in js
    assert "workbench-hardware-evidence-attachment.v2" in js
    assert "function currentHardwareEvidenceAttachmentV2Packet" in js
    assert "function buildHardwareEvidenceAttachmentValidationReport" in js
    assert "hardware_evidence_attachment_v2" in js
    assert "hardware_evidence_attachment_v2_checksum" in js
    assert "duplicate_hardware_evidence_attachment_id" in js
    assert "broken_hardware_evidence_attachment_reference" in js
    assert "hardware_evidence_attachment_v2 truth_effect must be none" in js
    assert "Hardware evidence attachment v2:" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_editor_command_palette_as_sandbox_only_command_surface() -> None:
    js = _js()

    assert "function openWorkbenchCommandPalette" in js
    assert "function closeWorkbenchCommandPalette" in js
    assert "function executeWorkbenchCommandPaletteCommand" in js
    assert "function renderWorkbenchCommandPalette" in js
    assert "command_palette.create_node" in js
    assert "command_palette.prepare_archive" in js
    assert "workbench-command-palette.v1" in js
    assert "No live Linear mutation" in js
    assert "个命令" in js
    assert "命令面板空闲" in js
    assert "已记录为沙箱工作台元数据" in js
    assert "图验证：已从命令面板进入连线模式" in js
    assert "本地执行失败" in js


def test_js_wires_hardware_interface_designer_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "well-harness-editable-hardware-interface-design" in js
    assert "editable_hardware_interface_design_v1.schema.json" in js
    assert "function validateHardwareInterfaceDesignerPayload" in js
    assert "function buildHardwareInterfaceDesignerValidationReport" in js
    assert "hardware_interface_designer" in js
    assert "hardware_interface_designer_validation" in js
    assert "hardware_interface_designer_checksum" in js
    assert "hardware_interface_designer truth_effect must be none" in js
    assert "duplicate_hardware_interface_id" in js
    assert "broken_hardware_interface_reference" in js
    assert 'runtime_truth_effect: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_selected_debug_timeline_as_sandbox_only_packet() -> None:
    js = _js()

    assert "function currentSelectedDebugTimelinePacket" in js
    assert "function renderSelectedDebugTimeline" in js
    assert "selected_debug_timeline" in js
    assert "selected_debug_timeline_checksum" in js
    assert "selected_debug_timeline truth_effect must be none" in js
    assert "Selected debug timeline:" in js
    assert 'kind: "well-harness-workbench-selected-debug-timeline"' in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_diff_review_v2_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "function currentCandidateBaselineDiffReviewV2Report" in js
    assert "function renderCandidateBaselineDiffReviewV2" in js
    assert "candidate_baseline_diff_review_v2" in js
    assert "candidate_baseline_diff_review_v2_checksum" in js
    assert "candidate_baseline_diff_review_v2 truth_effect must be none" in js
    assert "Diff review v2:" in js
    assert 'kind: "well-harness-workbench-candidate-baseline-diff-review-v2"' in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_candidate_debugger_view_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "well-harness-workbench-candidate-debugger-view" in js
    assert "workbench-candidate-debugger-view.v1" in js
    assert "function currentCandidateDebuggerView" in js
    assert "function renderCandidateDebuggerView" in js
    assert "candidate_debugger_view" in js
    assert "candidate_debugger_view_checksum" in js
    assert "candidate_debugger_view truth_effect must be none" in js
    assert "first_failing_assertion" in js
    assert "observed_values" in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_scenario_failure_explanation_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "well-harness-workbench-scenario-failure-explanation" in js
    assert "workbench-scenario-failure-explanation.v1" in js
    assert "function currentScenarioFailureExplanation" in js
    assert "function renderScenarioFailureExplanation" in js
    assert "function focusScenarioFailureOwner" in js
    assert "function focusScenarioFailureFrame" in js
    assert "scenario_failure_explanation" in js
    assert "scenario_failure_explanation_checksum" in js
    assert "scenario_failure_explanation truth_effect must be none" in js
    assert "upstream_dependencies" in js
    assert "timeline_frame" in js
    assert "data-failure-navigation" in js
    assert "data-failure-frame-tick" in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_debug_probe_timeline_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "well-harness-workbench-debug-probe-timeline" in js
    assert "workbench-debug-probe-timeline.v3" in js
    assert "function currentDebugProbeTimeline" in js
    assert "debug_probe_timeline" in js
    assert "debug_probe_timeline_checksum" in js
    assert "debug_probe_timeline truth_effect must be none" in js
    assert "watched_values" in js
    assert "selection_sync" in js
    assert "Debug probe timeline:" in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_preflight_analyzer_as_sandbox_only_archive_packet() -> None:
    js = _js()

    assert "well-harness-workbench-preflight-analyzer-report" in js
    assert "workbench-preflight-analyzer.v1" in js
    assert "function buildWorkbenchPreflightAnalyzerReport" in js
    assert "function renderWorkbenchPreflightAnalyzerReport" in js
    assert "preflight_analyzer_report" in js
    assert "preflight_analyzer_report_checksum" in js
    assert "preflight_analyzer_report truth_effect must be none" in js
    assert "invalid_candidate" in js
    assert "needs_evidence" in js
    assert "ready" in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_builds_release_maturity_snapshot_as_local_only_not_truth_claim() -> None:
    js = _js()

    assert "function buildWorkbenchReleaseMaturitySnapshot" in js
    assert "function renderWorkbenchReleaseMaturitySnapshot" in js
    assert "well-harness-workbench-release-maturity-snapshot" in js
    assert "workbench-release-maturity.v1" in js
    assert "local_operator_runbook" in js
    assert "local_only" in js
    assert "pass" in js
    assert "warning" in js
    assert "blocked" in js
    assert "rerun_required" in js
    assert "not_claimed" in js
    assert 'controller_truth_modified: false' in js
    assert 'candidate_state: "sandbox_candidate"' in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_workbench_exposes_local_release_readiness_packet_export() -> None:
    html = _html()
    js = _js()

    assert 'id="workbench-generate-release-readiness-btn"' in html
    assert 'id="workbench-release-readiness-output"' in html
    assert "生成本地发布包" in html
    assert "Release readiness packet" in html
    assert "function buildWorkbenchReleaseReadinessPacket" in js
    assert "function renderWorkbenchReleaseReadinessPacket" in js
    assert "well-harness-workbench-release-readiness-packet" in js
    assert "workbench-release-readiness.v1" in js
    assert "local_operator_commands" in js
    assert "PYTHONPATH=src python3 tools/run_gsd_validation_suite.py --format json" in js
    assert "PYTHONPATH=src python3 -m pytest -q -m e2e tests/e2e/test_workbench_js_boot_smoke.py" in js
    assert "release_maturity_snapshot_checksum" in js
    assert "gate_status_counts" in js
    assert 'controller_truth_modified: false' in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_js_wires_foundation_review_archive_as_sandbox_only_bundle() -> None:
    js = _js()

    assert "well-harness-workbench-foundation-review-archive" in js
    assert "workbench-foundation-review-archive.v1" in js
    assert "function buildFoundationReviewArchiveBundle" in js
    assert "function validateFoundationReviewArchiveBundle" in js
    assert "foundation_review_archive" in js
    assert "foundation_review_archive_validation" in js
    assert "foundation_review_archive_checksum" in js
    assert "foundation_review_archive_validation_checksum" in js
    assert "foundation review archive truth_effect must be none" in js
    assert "workspace_document" in js
    assert "editable_graph_document" in js
    assert "sandbox_test_run_report" in js
    assert "candidate_debugger_view" in js
    assert "preflight_analyzer_report" in js
    assert "hardware_interface_designer" in js
    assert "changerequest_handoff_packet" in js
    assert "live_linear_mutation: false" in js
    assert 'certification_claim: "none"' in js
    assert 'truth_effect: "none"' in js


def test_review_archive_restore_v3_controls_and_regression_bundle_are_sandbox_only() -> None:
    html = _html()
    js = _js()

    assert 'id="workbench-restore-review-archive-btn"' in html
    assert 'id="workbench-review-archive-restore-output"' in html
    assert 'id="workbench-regression-bundle-output"' in html
    assert 'id="workbench-archive-restore-review-checklist"' in html
    assert 'id="workbench-archive-review-checklist-status"' in html
    assert 'data-archive-review-check="graph"' in html
    assert 'data-archive-review-check="tests"' in html
    assert 'data-archive-review-check="traces"' in html
    assert 'data-archive-review-check="evidence"' in html
    assert 'data-archive-review-check="checksums"' in html
    assert 'data-archive-review-check="handoff"' in html
    assert "恢复审查清单" in html
    assert "well-harness-workbench-review-archive-restore-validation" in js
    assert "workbench-review-archive-restore.v3" in js
    assert "well-harness-workbench-review-archive-regression-bundle" in js
    assert "workbench-review-archive-regression-bundle.v3" in js
    assert "well-harness-workbench-archive-restore-review-checklist" in js
    assert "workbench-archive-restore-review-checklist.v1" in js
    assert "function validateReviewArchiveRestoreV3" in js
    assert "function buildArchiveRestoreReviewChecklist" in js
    assert "function renderArchiveRestoreReviewChecklist" in js
    assert "function buildReviewArchiveRegressionBundleV3" in js
    assert "function restoreReviewArchiveFromTextarea" in js
    assert "review_archive_restore_v3" in js
    assert "review_archive_restore_v3_checksum" in js
    assert "review_archive_regression_bundle_v3" in js
    assert "review_archive_regression_bundle_v3_checksum" in js
    assert "restore_review_checklist" in js
    assert "graph_review" in js
    assert "tests_review" in js
    assert "traces_review" in js
    assert "evidence_review" in js
    assert "checksums_review" in js
    assert "handoff_review" in js
    assert "checksum_mismatch_count" in js
    assert "checksum_path" in js
    assert "checksum_key" in js
    assert "evidence_path" in js
    assert "full_e2e_49_49_claim" in js
    assert "mypy_strict_clean_claim" in js
    assert 'controller_truth_modified: false' in js
    assert 'truth_effect: "none"' in js


def test_js_builds_changerequest_linear_handoff_without_live_linear_mutation() -> None:
    js = _js()

    assert "function buildEditableHandoffPacket" in js
    assert "function buildChangeRequestProofPacket" in js
    assert "function buildChangeRequestHandoffPacket" in js
    assert "function linearIssueBodyFromProofPacket" in js
    assert "function prProofTextFromProofPacket" in js
    assert "workbench-generate-handoff-btn" in js
    assert "changerequest_proof_packet" in js
    assert "changerequest_handoff_packet" in js
    assert "changerequest_handoff_packet_checksum" in js
    assert "changerequest_handoff_packet truth_effect must be none" in js
    assert "workbench_changerequest_handoff_v1.schema.json" in js
    assert "json.sort_keys.separators.v1" in js
    assert "function stableEvidenceArchiveJson" in js
    assert 'issue: "JER-TBD"' in js
    assert "Candidate state:" in js
    assert "Certification claim:" in js
    assert "Truth-level impact:" in js
    assert "Red lines touched:" in js
    assert "## Red Lines" in js
    assert "## Test Delta" in js
    assert 'kind: "well-harness-workbench-changerequest-handoff-packet"' in js
    assert "No live Linear mutation" in js
