from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
import pytest

from well_harness.thrust_reverser_docx_sentence_map import (
    build_thrust_reverser_docx_sentence_circuit_map,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "demo_html_reconstruction_mvp_v0_1.schema.json"
)
FIXTURE_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "demo_html_reconstruction_mvp_v0_1.json"
)
CHECKER_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "verify_demo_html_reconstruction_mvp.py"
BROWSER_CHECKER_SCRIPT_PATH = (
    PROJECT_ROOT / "scripts" / "verify_demo_html_reconstruction_browser_acceptance.py"
)
MAKEFILE_PATH = PROJECT_ROOT / "Makefile"
GSD_AUTOMATION_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "gsd-automation.yml"
SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "demo_html_reconstruction_mvp_v0_1.schema.json"
)


def _script_env() -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    return env


def test_demo_html_reconstruction_mvp_schema_validates_fixture() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert schema["$id"] == SCHEMA_ID
    jsonschema.Draft202012Validator(schema).validate(fixture)
    assert fixture["kind"] == "ai-fantui-demo-html-reconstruction-mvp"
    assert fixture["mvp_id"] == "demo-html-reconstruction-mvp-v0.1"
    assert fixture["golden_reference"]["route"] == "/demo.html"
    assert fixture["replica_surface"]["route"] == "/demo-reconstruction"
    assert fixture["replica_surface"]["surface_role"] == "mvp_reconstruction_console_surface"
    assert fixture["homepage_entry"] == {
        "route": "/demo-reconstruction",
        "element_id": "home-first-phase-demo-entry",
        "priority": "first_phase_mvp",
        "label": "demo.html 复刻 MVP 控制台",
    }
    assert fixture["contract"]["expected_node_count"] == 20
    assert fixture["contract"]["expected_wire_count"] == 23
    assert fixture["contract"]["expected_preset_count"] == 5
    assert fixture["contract"]["expected_status_output_count"] == 6
    assert fixture["contract"]["expected_output_card_count"] == 4
    assert fixture["review_boundaries"] == {
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "truth_effect": "none",
        "certification_claim": "none",
    }


def test_demo_html_reconstruction_mvp_checker_converges() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["schema_valid"] is True
    assert payload["fixture_match"] is True
    assert payload["deterministic_gates"] == {
        "golden_demo_contract": "pass",
        "replica_surface_contract": "pass",
        "homepage_entry": "pass",
        "logic_builder_bridge": "pass",
        "local_routes": "pass",
        "boundary": "pass",
    }
    assert payload["observed"]["golden_demo"]["node_count"] == 20
    assert payload["observed"]["golden_demo"]["wire_count"] == 23
    assert payload["observed"]["replica_surface"]["claimed_node_count"] == "20/20"
    assert payload["observed"]["replica_surface"]["claimed_wire_count"] == "23/23"
    assert payload["observed"]["homepage_entry"] == {
        "entry_present": True,
        "route": "/demo-reconstruction",
        "priority": "first_phase_mvp",
        "label": "demo.html 复刻 MVP 控制台",
        "appears_before_default_mode_grid": True,
    }
    assert payload["observed"]["logic_builder_bridge"]["target_route"] == "/demo-reconstruction"
    assert payload["observed"]["routes"]["demo_html_status"] == 200
    assert payload["observed"]["routes"]["demo_reconstruction_status"] == 200
    assert payload["review_boundaries"]["controller_truth_modified"] is False
    assert payload["review_boundaries"]["ui_layout_modified"] is False


def test_demo_reconstruction_route_is_main_mvp_console_not_comparison_page() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "index.html"
    ).read_text(encoding="utf-8")
    stylesheet = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "demo_reconstruction.css"
    ).read_text(encoding="utf-8")
    script = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "demo_reconstruction.js"
    ).read_text(encoding="utf-8")

    assert 'data-ux-page-role="demo-mvp-console"' in html
    assert 'data-demo-mvp-console="true"' in html
    assert 'id="demo-reconstruction-console-frame"' in html
    assert 'src="/demo.html?embed=1&amp;palette=codex-light"' in html
    assert 'id="demo-reconstruction-browser-evidence"' in html
    assert 'id="demo-reconstruction-review-index"' in html
    assert 'id="demo-reconstruction-review-index-readiness"' in html
    assert 'id="demo-reconstruction-review-index-step"' in html
    assert 'id="demo-reconstruction-review-index-object"' in html
    assert 'id="demo-reconstruction-review-index-output"' in html
    assert 'id="demo-reconstruction-review-index-list"' in html
    assert 'id="demo-reconstruction-docx-circuit-map"' in html
    assert 'id="demo-reconstruction-requirement-ledger"' in html
    assert 'id="demo-reconstruction-requirement-ledger-search"' in html
    assert 'id="demo-reconstruction-requirement-ledger-filters"' in html
    assert 'id="demo-reconstruction-requirement-ledger-list"' in html
    assert 'id="demo-reconstruction-docx-trace-board"' in html
    assert 'id="demo-reconstruction-trace-card-list"' in html
    assert 'id="demo-reconstruction-selected-trace"' in html
    assert 'id="demo-reconstruction-embedded-highlight-status"' in html
    assert 'id="demo-reconstruction-logic-equation-board"' in html
    assert 'id="demo-reconstruction-logic-equation-summary"' in html
    assert 'id="demo-reconstruction-logic-equation-list"' in html
    assert 'id="demo-reconstruction-coverage-matrix"' in html
    assert 'id="demo-reconstruction-coverage-search"' in html
    assert 'id="demo-reconstruction-coverage-filter-status"' in html
    assert 'id="demo-reconstruction-topology-matrix"' in html
    assert 'id="demo-reconstruction-topology-summary"' in html
    assert 'id="demo-reconstruction-topology-readback"' in html
    assert 'id="demo-reconstruction-topology-search"' in html
    assert 'id="demo-reconstruction-topology-step-filter"' in html
    assert 'id="demo-reconstruction-topology-filter-status"' in html
    assert 'id="demo-reconstruction-output-path-lane"' in html
    assert 'id="demo-reconstruction-output-path-summary"' in html
    assert 'id="demo-reconstruction-output-path-targets"' in html
    assert 'id="demo-reconstruction-output-path-readback"' in html
    assert 'id="demo-reconstruction-output-path-list"' in html
    assert 'id="demo-reconstruction-output-maturity-matrix"' in html
    assert 'id="demo-reconstruction-output-maturity-summary"' in html
    assert 'id="demo-reconstruction-output-maturity-grid"' in html
    assert 'id="demo-reconstruction-topology-list"' in html
    assert 'id="demo-reconstruction-keyboard-review"' in html
    assert 'id="demo-reconstruction-review-anchor"' in html
    assert 'id="demo-reconstruction-review-object"' in html
    assert 'id="demo-reconstruction-review-sync"' in html
    assert 'id="demo-reconstruction-review-link"' in html
    assert 'id="demo-reconstruction-step-playback"' in html
    assert 'id="demo-reconstruction-playback-step-list"' in html
    assert 'id="demo-reconstruction-playback-active-step"' in html
    assert 'id="demo-reconstruction-playback-node-count"' in html
    assert 'id="demo-reconstruction-playback-wire-count"' in html
    assert 'id="demo-reconstruction-assembly-map"' in html
    assert 'id="demo-reconstruction-assembly-summary"' in html
    assert 'id="demo-reconstruction-assembly-list"' in html
    assert 'id="demo-reconstruction-assembly-final"' in html
    assert 'id="demo-reconstruction-object-provenance"' in html
    assert 'id="demo-reconstruction-provenance-object"' in html
    assert 'id="demo-reconstruction-provenance-source-count"' in html
    assert 'id="demo-reconstruction-provenance-step-count"' in html
    assert 'id="demo-reconstruction-provenance-source-list"' in html
    assert 'id="demo-reconstruction-provenance-step-list"' in html
    assert 'id="demo-reconstruction-signal-neighborhood"' in html
    assert 'id="demo-reconstruction-neighborhood-object"' in html
    assert 'id="demo-reconstruction-neighborhood-incoming"' in html
    assert 'id="demo-reconstruction-neighborhood-outgoing"' in html
    assert 'id="demo-reconstruction-neighborhood-adjacent"' in html
    assert 'id="demo-reconstruction-proof-path-object-inspector"' in html
    assert 'id="demo-reconstruction-proof-path-object-inspector-object"' in html
    assert 'id="demo-reconstruction-proof-path-object-inspector-source-count"' in html
    assert 'id="demo-reconstruction-proof-path-object-inspector-step-count"' in html
    assert 'id="demo-reconstruction-proof-path-object-inspector-edge-count"' in html
    assert 'id="demo-reconstruction-proof-path-object-inspector-neighbors"' in html
    assert 'id="demo-reconstruction-proof-path-output-map"' in html
    assert 'id="demo-reconstruction-proof-path-output-map-status"' in html
    assert 'id="demo-reconstruction-proof-path-output-map-list"' in html
    assert 'id="demo-reconstruction-proof-path-output-map-readback"' in html
    assert 'id="demo-reconstruction-circuit-ladder"' in html
    assert 'id="demo-reconstruction-ladder-summary"' in html
    assert 'id="demo-reconstruction-ladder-list"' in html
    assert 'id="demo-reconstruction-review-packet"' in html
    assert 'id="demo-reconstruction-review-packet-readiness"' in html
    assert 'id="demo-reconstruction-review-packet-dashboard"' in html
    assert 'id="demo-reconstruction-review-packet-dashboard-summary"' in html
    assert 'id="demo-reconstruction-review-packet-dashboard-metrics"' in html
    assert 'id="demo-reconstruction-review-packet-dashboard-checklist"' in html
    assert 'id="demo-reconstruction-review-packet-gates"' in html
    assert 'id="demo-reconstruction-review-verdict"' in html
    assert 'id="demo-reconstruction-review-verdict-status"' in html
    assert 'id="demo-reconstruction-review-verdict-readback"' in html
    assert 'data-review-verdict="first-screen"' in html
    assert 'data-review-verdict-card="boundary"' in html
    assert 'id="demo-reconstruction-custody-matrix"' in html
    assert 'id="demo-reconstruction-custody-summary"' in html
    assert 'id="demo-reconstruction-custody-active"' in html
    assert 'id="demo-reconstruction-custody-output"' in html
    assert 'id="demo-reconstruction-custody-list"' in html
    assert 'id="demo-reconstruction-output-mirror"' in html
    assert 'id="demo-reconstruction-output-mirror-status"' in html
    assert 'id="demo-reconstruction-output-mirror-thr-output"' in html
    assert 'id="demo-reconstruction-control-strip"' in html
    assert 'id="demo-reconstruction-control-strip-status"' in html
    assert 'id="demo-reconstruction-control-strip-step"' in html
    assert 'id="demo-reconstruction-control-strip-object"' in html
    assert 'id="demo-reconstruction-control-strip-output"' in html
    assert 'id="demo-reconstruction-control-strip-path"' in html
    assert 'data-demo-control-strip="first-screen"' in html
    assert 'data-control-strip-action="prove-thr"' in html
    assert 'id="demo-reconstruction-sentence-runner"' in html
    assert 'id="demo-reconstruction-sentence-runner-status"' in html
    assert 'id="demo-reconstruction-sentence-runner-list"' in html
    assert 'id="demo-reconstruction-sentence-runner-readback"' in html
    assert 'data-sentence-runner="first-screen"' in html
    assert 'id="demo-reconstruction-proof-path"' in html
    assert 'id="demo-reconstruction-proof-path-status"' in html
    assert 'id="demo-reconstruction-proof-path-list"' in html
    assert 'id="demo-reconstruction-proof-path-readback"' in html
    assert 'id="demo-reconstruction-proof-path-coverage-grid"' in html
    assert 'id="demo-reconstruction-proof-path-coverage-grid-status"' in html
    assert 'id="demo-reconstruction-proof-path-coverage-grid-list"' in html
    assert 'id="demo-reconstruction-proof-path-coverage-grid-readback"' in html
    assert 'data-proof-path="first-screen"' in html
    assert 'id="demo-reconstruction-scenario-comparator"' in html
    assert 'id="demo-reconstruction-scenario-comparator-status"' in html
    assert 'id="demo-reconstruction-scenario-comparator-readback"' in html
    assert 'data-scenario-comparator="first-screen"' in html
    assert 'data-scenario-comparator-action="max-reverse"' in html
    assert 'id="demo-reconstruction-scenario-ledger"' in html
    assert 'id="demo-reconstruction-scenario-ledger-status"' in html
    assert 'id="demo-reconstruction-scenario-ledger-list"' in html
    assert 'id="demo-reconstruction-scenario-truth-table"' in html
    assert 'id="demo-reconstruction-scenario-truth-status"' in html
    assert 'id="demo-reconstruction-scenario-truth-body"' in html
    assert 'id="demo-reconstruction-operator-runway"' in html
    assert 'id="demo-reconstruction-operator-runway-status"' in html
    assert 'id="demo-reconstruction-operator-runway-list"' in html
    assert 'id="demo-reconstruction-proof-transcript"' in html
    assert 'id="demo-reconstruction-proof-transcript-summary"' in html
    assert 'id="demo-reconstruction-proof-transcript-list"' in html
    assert 'id="demo-reconstruction-coverage-node-list"' in html
    assert 'id="demo-reconstruction-coverage-wire-list"' in html
    assert 'data-source-docx-circuit-map="true"' in html
    assert "uploads/20260409-thrust-reverser-control-logic.docx" in html
    assert "demo.html 复刻 MVP 控制台" in html
    assert "审阅路径索引" in html
    assert "原始 DOCX 逐句到完整电路" in html
    assert "需求覆盖账本" in html
    assert "逐句构建轨道" in html
    assert "逻辑方程板" in html
    assert "逐句装配总览" in html
    assert "对象反查证据板" in html
    assert "电路邻接读回" in html
    assert "电路完成阶梯" in html
    assert "审阅交付包" in html
    assert "审阅结论" in html
    assert "交付链路总览" in html
    assert "演示舱输出镜像" in html
    assert "场景读回记录" in html
    assert "演示导览轨" in html
    assert "逐句讲解稿" in html
    assert "证明路径图" in html
    assert "完整电路拓扑矩阵" in html
    assert "<h2>原版 demo.html</h2>" not in html
    assert "<h2>当前复刻</h2>" not in html
    assert "demo-reconstruction-comparison-table" not in html
    assert "demo-reconstruction-compare-grid" not in html
    assert "DeepSeek live replay" not in script
    assert "读取 golden demo 控制台" in script
    assert "DOCX_SENTENCE_CIRCUIT_ENDPOINT" in script
    assert "/api/demo-reconstruction/docx-sentence-circuit-map" in script
    assert "renderTraceBoard" in script
    assert "setSelectedTrace" in script
    assert "TRACE_WIRE_ENDPOINTS" not in script
    assert "updateWireEndpointMapFromWires" in script
    assert "wireEndpointsForId" in script
    assert "applyEmbeddedTraceHighlight" in script
    assert "applyEmbeddedTraceFocus" in script
    assert "renderCoverageMatrix" in script
    assert "updateCoverageFilter" in script
    assert "renderRequirementLedger" in script
    assert "requirementLedgerItems" in script
    assert "activateRequirementLedgerItem" in script
    assert "LOGIC_EQUATION_RECORDS" in script
    assert "renderLogicEquationBoard" in script
    assert "activateLogicEquationRecord" in script
    assert "logicEquationState" in script
    assert "wire_logic4_thr_lock" in script
    assert "circuitCoverageKind" in script
    assert "setTraceCardTabStops" in script
    assert "handleTraceCardKeydown" in script
    assert "handleCoverageKeyboardNavigation" in script
    assert "clearCircuitObjectFocus" in script
    assert "updateKeyboardReviewStatus" in script
    assert "readReviewHashState" in script
    assert "writeReviewHashState" in script
    assert "applyReviewHashState" in script
    assert "updateReviewLink" in script
    assert "updateReviewIndexStatus" in script
    assert "installReviewIndexNavigation" in script
    assert "setReviewIndexTarget" in script
    assert "renderStepPlaybackRail" in script
    assert "applyStepPlayback" in script
    assert "cumulativeTraceContract" in script
    assert "renderAssemblyMap" in script
    assert "assemblyOutputLabelForStep" in script
    assert "setAssemblyButtonState" in script
    assert "renderObjectProvenance" in script
    assert "objectProvenanceRecords" in script
    assert "renderSignalNeighborhood" in script
    assert "signalNeighborhoodRecords" in script
    assert "wireRecordsForNode" in script
    assert "renderTopologyMatrix" in script
    assert "topologyWireIds" in script
    assert "updateTopologyReadback" in script
    assert "resetTopologyReadback" in script
    assert "renderTopologyStepFilter" in script
    assert "updateTopologyFilter" in script
    assert 'params.get("topology")' in script
    assert 'params.set("topology"' in script
    assert 'params.set("tq"' in script
    assert "renderOutputPathLane" in script
    assert "upstreamPathForTarget" in script
    assert "renderOutputMaturityMatrix" in script
    assert "setOutputMaturityCellState" in script
    assert "outputMaturityTargetForFocus" in script
    assert "keepOutputMaturitySelection" in script
    assert "renderCircuitCompletionLadder" in script
    assert "ladderMilestonesForStep" in script
    assert "updateNodeMetadataFromNodes" in script
    assert "hasRenderedNode" in script
    assert "hasRenderedNode(wire.source)" in script
    assert "hasRenderedNode(wire.target)" in script
    assert "nodeKindMap" in script
    assert '"P035-S03": ["EEC", "PLS", "PDU"]' not in script
    assert "updateReviewPacketFromState" in script
    assert "renderReviewPacketGates" in script
    assert "renderReviewPacketDashboard" in script
    assert "updateReviewVerdictBoard" in script
    assert "reviewVerdictStatus" in script
    assert "requirementLedgerStats" in script
    assert "finalOutputReadinessCount" in script
    assert "renderCustodyMatrix" in script
    assert "updateCustodyActiveReadback" in script
    assert "updateCustodyOutputReadback" in script
    assert "updateScenarioLedgerFromFrame" in script
    assert "renderScenarioLedger" in script
    assert "renderScenarioTruthTable" in script
    assert "scenarioTruthTokens" in script
    assert "OPERATOR_RUNWAY_RECORDS" in script
    assert "renderOperatorRunway" in script
    assert "activateOperatorRunwayRecord" in script
    assert "refreshOperatorRunwayReadback" in script
    assert "runway-l4-thr-lock" in script
    assert "runway-inhibit" in script
    assert "renderProofTranscript" in script
    assert "proofTranscriptSourceText" in script
    assert "record.proofText ||" in script
    assert "抑制位为真时，展开链路保持阻塞，反推锁不释放。" in script
    assert "installControlStripActions" in script
    assert "activateControlStripAction" in script
    assert "updateControlStripStatus" in script
    assert "controlStripRecordForAction" in script
    assert "renderSentenceRunner" in script
    assert "applySentenceRunnerStep" in script
    assert "updateSentenceRunnerStatus" in script
    assert "sentenceRunnerOutputLabel" in script
    assert "renderProofPathTimeline" in script
    assert "applyProofPathStep" in script
    assert "applyProofPathObjectJump" in script
    assert "proofPathFocusRecords" in script
    assert "proofPathFocusTarget" in script
    assert "renderProofPathObjectInspector" in script
    assert "renderProofPathInspectorNeighbors" in script
    assert "applyProofPathInspectorJump" in script
    assert "proofPathInspectorFocusId" in script
    assert "renderProofPathCoverageGrid" in script
    assert "applyProofPathCoverageStep" in script
    assert "applyProofPathCoverageObject" in script
    assert "proofPathCoverageFocusId" in script
    assert "renderProofPathOutputMap" in script
    assert "applyProofPathOutputTarget" in script
    assert "proofPathOutputTarget" in script
    assert "等待源文证据" in script
    assert "本句" in script
    assert "installScenarioComparatorActions" in script
    assert "updateScenarioComparatorStatus" in script
    assert "scenarioComparatorSummary" in script
    assert "SCENARIO_COMPARATOR_IDS" in script
    assert "data-proof-transcript-row" in script
    assert "applyScenarioPreset" in script
    assert "installOutputMirrorObserver" in script
    assert "updateOutputMirrorFromFrame" in script
    assert "data-docx-trace-selected" in script
    assert "traceFocusKind" in script
    assert "sourceFocusKind" in script
    assert ".demo-reconstruction-console-stage" in stylesheet
    assert "#demo-reconstruction-console-frame" in stylesheet
    assert ".demo-reconstruction-review-index" in stylesheet
    assert ".demo-reconstruction-review-index-list" in stylesheet
    assert ".demo-reconstruction-source-map" in stylesheet
    assert ".demo-reconstruction-requirement-ledger" in stylesheet
    assert ".demo-reconstruction-requirement-ledger-row" in stylesheet
    assert ".demo-reconstruction-trace-board" in stylesheet
    assert ".demo-reconstruction-trace-card" in stylesheet
    assert ".demo-reconstruction-embedded-highlight-status" in stylesheet
    assert ".demo-reconstruction-logic-equation-board" in stylesheet
    assert ".demo-reconstruction-logic-equation-row" in stylesheet
    assert ".demo-reconstruction-coverage-matrix" in stylesheet
    assert ".demo-reconstruction-coverage-tools" in stylesheet
    assert ".demo-reconstruction-topology-matrix" in stylesheet
    assert ".demo-reconstruction-topology-controls" in stylesheet
    assert ".demo-reconstruction-topology-step-filter" in stylesheet
    assert ".demo-reconstruction-output-path-lane" in stylesheet
    assert ".demo-reconstruction-output-path-row" in stylesheet
    assert ".demo-reconstruction-output-maturity-matrix" in stylesheet
    assert ".demo-reconstruction-output-maturity-cell" in stylesheet
    assert ".demo-reconstruction-topology-list" in stylesheet
    assert ".demo-reconstruction-topology-row" in stylesheet
    assert ".demo-reconstruction-keyboard-review" in stylesheet
    assert ".demo-reconstruction-keyboard-review strong" in stylesheet
    assert ".demo-reconstruction-review-link" in stylesheet
    assert ".demo-reconstruction-step-playback" in stylesheet
    assert ".demo-reconstruction-playback-steps" in stylesheet
    assert ".demo-reconstruction-playback-button" in stylesheet
    assert ".demo-reconstruction-assembly-map" in stylesheet
    assert ".demo-reconstruction-assembly-list" in stylesheet
    assert ".demo-reconstruction-assembly-card" in stylesheet
    assert ".demo-reconstruction-object-provenance" in stylesheet
    assert ".demo-reconstruction-provenance-list" in stylesheet
    assert ".demo-reconstruction-signal-neighborhood" in stylesheet
    assert ".demo-reconstruction-neighborhood-list" in stylesheet
    assert ".demo-reconstruction-circuit-ladder" in stylesheet
    assert ".demo-reconstruction-ladder-item" in stylesheet
    assert ".demo-reconstruction-review-packet" in stylesheet
    assert ".demo-reconstruction-review-packet-dashboard" in stylesheet
    assert ".demo-reconstruction-review-packet-dashboard-metrics" in stylesheet
    assert ".demo-reconstruction-review-packet-dashboard-checklist" in stylesheet
    assert ".demo-reconstruction-review-packet-gates" in stylesheet
    assert ".demo-reconstruction-review-verdict" in stylesheet
    assert ".demo-reconstruction-review-verdict-grid" in stylesheet
    assert ".demo-reconstruction-custody-matrix" in stylesheet
    assert ".demo-reconstruction-custody-button" in stylesheet
    assert ".demo-reconstruction-custody-readback" in stylesheet
    assert ".demo-reconstruction-output-mirror" in stylesheet
    assert ".demo-reconstruction-output-mirror-values" in stylesheet
    assert ".demo-reconstruction-control-strip" in stylesheet
    assert ".demo-reconstruction-control-strip-actions" in stylesheet
    assert ".demo-reconstruction-sentence-runner" in stylesheet
    assert ".demo-reconstruction-sentence-runner-list" in stylesheet
    assert ".demo-reconstruction-proof-path" in stylesheet
    assert ".demo-reconstruction-proof-path-list" in stylesheet
    assert ".demo-reconstruction-proof-path-focus-list" in stylesheet
    assert ".demo-reconstruction-proof-path-object-inspector" in stylesheet
    assert ".demo-reconstruction-proof-path-object-inspector-metrics" in stylesheet
    assert ".demo-reconstruction-proof-path-object-inspector-neighbors" in stylesheet
    assert ".demo-reconstruction-proof-path-coverage-grid" in stylesheet
    assert ".demo-reconstruction-proof-path-coverage-step" in stylesheet
    assert ".demo-reconstruction-proof-path-coverage-focus-list" in stylesheet
    assert ".demo-reconstruction-proof-path-output-map" in stylesheet
    assert ".demo-reconstruction-proof-path-output-map-list" in stylesheet
    assert ".demo-reconstruction-proof-path-step em" in stylesheet
    assert ".demo-reconstruction-scenario-comparator" in stylesheet
    assert ".demo-reconstruction-scenario-comparator-list" in stylesheet
    assert ".demo-reconstruction-scenario-ledger" in stylesheet
    assert ".demo-reconstruction-scenario-row" in stylesheet
    assert ".demo-reconstruction-scenario-truth-table" in stylesheet
    assert ".demo-reconstruction-scenario-truth-row" in stylesheet
    assert ".demo-reconstruction-operator-runway" in stylesheet
    assert ".demo-reconstruction-operator-runway-row" in stylesheet
    assert ".demo-reconstruction-proof-transcript" in stylesheet
    assert ".demo-reconstruction-proof-transcript-row" in stylesheet
    assert "button.demo-reconstruction-chip" in stylesheet


def test_demo_reconstruction_mvp_console_has_first_screen_operator_guide() -> None:
    html = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "index.html"
    ).read_text(encoding="utf-8")
    stylesheet = (
        PROJECT_ROOT
        / "src"
        / "well_harness"
        / "static"
        / "demo_reconstruction"
        / "demo_reconstruction.css"
    ).read_text(encoding="utf-8")

    assert 'id="demo-reconstruction-operator-guide"' in html
    assert 'id="demo-reconstruction-control-strip"' in html
    assert 'id="demo-reconstruction-sentence-runner"' in html
    assert 'id="demo-reconstruction-scenario-comparator"' in html
    assert 'id="demo-reconstruction-operator-runway"' in html
    assert 'id="demo-reconstruction-proof-transcript"' in html
    assert 'data-demo-mvp-guide="first-screen"' in html
    assert 'data-operator-runway="demo-html-walkthrough"' in html
    assert 'data-proof-transcript="demo-html-walkthrough"' in html
    assert "演示导览轨" in html
    assert "演示控制条" in html
    assert "逐句复刻条" in html
    assert "场景对照板" in html
    assert "逐句讲解稿" in html
    assert "选择预设" in html
    assert "查看 HUD" in html
    assert "核对输出" in html
    assert ".demo-reconstruction-operator-guide" in stylesheet
    assert ".demo-reconstruction-control-strip" in stylesheet
    assert ".demo-reconstruction-control-strip-grid" in stylesheet
    assert ".demo-reconstruction-sentence-runner" in stylesheet
    assert ".demo-reconstruction-sentence-runner-list" in stylesheet
    assert ".demo-reconstruction-scenario-comparator" in stylesheet
    assert ".demo-reconstruction-scenario-comparator-list" in stylesheet
    assert ".demo-reconstruction-guide-step" in stylesheet
    assert ".demo-reconstruction-operator-runway" in stylesheet
    assert ".demo-reconstruction-operator-runway-row" in stylesheet
    assert ".demo-reconstruction-proof-transcript" in stylesheet
    assert ".demo-reconstruction-proof-transcript-row" in stylesheet


def test_demo_reconstruction_docx_sentence_map_covers_complete_demo_circuit() -> None:
    payload = build_thrust_reverser_docx_sentence_circuit_map()
    entries = {entry["anchor"]: entry for entry in payload["source_entries"]}
    sequence_steps = {step["anchor"]: step for step in payload["sequence_steps"]}

    assert payload["kind"] == "ai-fantui-thrust-reverser-docx-sentence-circuit-map"
    assert payload["source"]["path"] == "uploads/20260409-thrust-reverser-control-logic.docx"
    assert payload["source"]["paragraph_count"] == 45
    assert payload["source"]["table_count"] == 2
    assert payload["source"]["table_row_count"] == 17
    assert payload["circuit_contract"]["source"] == "src/well_harness/static/demo.html#fan-chain-svg"
    assert payload["circuit_contract"]["node_count"] == 20
    assert payload["circuit_contract"]["wire_count"] == 23
    assert payload["coverage"]["covered_node_count"] == 20
    assert payload["coverage"]["covered_wire_count"] == 23
    assert payload["coverage"]["complete_demo_contract"] is True
    assert entries["P035"]["role"] == "动作顺序"
    assert "油门台内微动开关1" in entries["P035"]["text"]
    assert "工作逻辑1" in entries["P036"]["text"]
    assert "油门杆解析角度≤-11.74°" in entries["P041"]["text"]
    assert "故障注入目前暂时不考虑" in entries["P045"]["text"]
    assert "wire_logic4_thr_lock" in sequence_steps["P035-S05"]["wire_ids"]
    assert "wire_vdt90_logic4" in sequence_steps["P035-S05"]["wire_ids"]
    assert "thr_lock" in sequence_steps["P035-S05"]["node_ids"]


@pytest.mark.e2e
def test_demo_html_reconstruction_browser_acceptance_script_captures_interaction_evidence(
    tmp_path: Path,
) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(BROWSER_CHECKER_SCRIPT_PATH),
            "--artifact-dir",
            str(tmp_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["route"] == "/demo-reconstruction"
    assert payload["screenshots"]["first_screen"].endswith(".png")
    assert payload["screenshots"]["mobile_first_screen"].endswith(".png")
    assert payload["screenshots"]["review_index"].endswith(".png")
    assert payload["screenshots"]["assembly_map"].endswith(".png")
    assert payload["screenshots"]["logic_equation_board"].endswith(".png")
    assert payload["screenshots"]["topology_matrix"].endswith(".png")
    assert payload["screenshots"]["chain_svg"].endswith(".png")
    assert payload["screenshots"]["keyboard_review"].endswith(".png")
    assert payload["screenshots"]["review_deep_link"].endswith(".png")
    assert payload["screenshots"]["step_playback"].endswith(".png")
    assert payload["screenshots"]["object_provenance"].endswith(".png")
    assert payload["screenshots"]["signal_neighborhood"].endswith(".png")
    assert payload["screenshots"]["completion_ladder"].endswith(".png")
    assert payload["screenshots"]["review_packet"].endswith(".png")
    assert payload["screenshots"]["custody_matrix"].endswith(".png")
    assert payload["screenshots"]["scenario_ledger"].endswith(".png")
    assert payload["screenshots"]["scenario_truth_table"].endswith(".png")
    assert payload["screenshots"]["operator_runway"].endswith(".png")
    assert payload["screenshots"]["proof_transcript"].endswith(".png")
    assert payload["screenshots"]["control_strip"].endswith(".png")
    assert payload["screenshots"]["sentence_runner"].endswith(".png")
    assert payload["screenshots"]["proof_path"].endswith(".png")
    assert payload["screenshots"]["scenario_comparator"].endswith(".png")
    assert payload["screenshots"]["review_verdict"].endswith(".png")
    assert payload["screenshots"]["max_reverse_outputs"].endswith(".png")
    assert payload["screenshots"]["inhibit_block_outputs"].endswith(".png")
    assert payload["pixel_visibility"]["chain_svg"]["status"] == "pass"
    assert payload["pixel_visibility"]["chain_svg"]["node_count"] == 20
    assert payload["pixel_visibility"]["chain_svg"]["wire_count"] == 23
    assert payload["first_screen_review"] == {
        "review_index_visible": True,
        "assembly_map_visible": True,
        "topology_matrix_visible": True,
        "source_map_visible": True,
        "requirement_ledger_visible": True,
        "trace_board_visible": True,
        "logic_equation_board_visible": True,
        "operator_guide_visible": True,
        "output_mirror_visible": True,
        "control_strip_visible": True,
        "sentence_runner_visible": True,
        "proof_path_visible": True,
        "scenario_comparator_visible": True,
        "review_verdict_visible": True,
        "scenario_ledger_visible": True,
        "scenario_truth_table_visible": True,
        "operator_runway_visible": True,
        "proof_transcript_visible": True,
        "console_frame_visible": True,
        "evidence_rail_visible": True,
    }
    assert payload["source_map_review"]["sourceEntryCount"] >= 10
    assert payload["source_map_review"]["reviewIndexButtonCount"] == 11
    assert payload["source_map_review"]["requirementLedgerRowCount"] == 67
    assert payload["source_map_review"]["requirementLedgerMappedCount"] == 44
    assert payload["source_map_review"]["requirementLedgerContextCount"] == 18
    assert payload["source_map_review"]["requirementLedgerP035Count"] == 5
    assert "67 条" in payload["source_map_review"]["requirementLedgerSummary"]
    assert "44 已映射" in payload["source_map_review"]["requirementLedgerSummary"]
    assert payload["source_map_review"]["requirementLedgerStatus"] == "67/67 条"
    assert payload["requirement_ledger_context_review"]["selectedFilters"] == ["context"]
    assert payload["requirement_ledger_context_review"]["visibleRows"] == 18
    assert "18/67" in payload["requirement_ledger_context_review"]["statusText"]
    assert payload["requirement_ledger_action_review"]["query"] == "logic4"
    assert payload["requirement_ledger_action_review"]["visibleRows"] >= 3
    assert payload["requirement_ledger_action_review"]["selectedRows"] == ["step:P035-S05"]
    assert payload["requirement_ledger_action_review"]["selectedAnchor"] == "P035-S05"
    assert payload["requirement_ledger_action_review"]["highlightedCount"] >= 4
    assert payload["source_map_review"]["sequenceStepCount"] == 5
    assert payload["source_map_review"]["traceCardCount"] == 5
    assert payload["source_map_review"]["playbackStepCount"] == 5
    assert payload["source_map_review"]["assemblyStepCount"] == 5
    assert payload["source_map_review"]["topologyRowCount"] == 23
    assert payload["source_map_review"]["ladderStepCount"] == 5
    assert payload["source_map_review"]["custodyStepCount"] == 5
    assert payload["source_map_review"]["coverageNodeButtonCount"] == 20
    assert payload["source_map_review"]["coverageWireButtonCount"] == 23
    assert payload["source_map_review"]["selectedNodeChipCount"] > 0
    assert payload["source_map_review"]["selectedWireChipCount"] > 0
    assert payload["source_map_review"]["nodeCoverage"] == "20/20"
    assert payload["source_map_review"]["wireCoverage"] == "23/23"
    assert payload["review_index_review"]["visible"] is True
    assert payload["review_index_review"]["buttonCount"] == 11
    assert payload["review_index_review"]["activeTargets"] == [
        "demo-reconstruction-docx-circuit-map"
    ]
    assert "P035-S01" in payload["review_index_review"]["stepText"]
    assert payload["review_index_navigation"]["activeTargets"] == [
        "demo-reconstruction-scenario-ledger"
    ]
    assert payload["review_index_navigation"]["scrollY"] > 0
    assert "P035-S05" in payload["review_index_after_trace"]["stepText"]
    assert "等待聚焦" in payload["review_index_after_trace"]["objectText"]
    assert payload["logic_equation_review"]["visible"] is True
    assert payload["logic_equation_review"]["rowCount"] == 4
    assert payload["logic_equation_review"]["passCount"] == 4
    assert "4/4 方程" in payload["logic_equation_review"]["summaryText"]
    assert "20/20 节点" in payload["logic_equation_review"]["summaryText"]
    assert "23/23 连线" in payload["logic_equation_review"]["summaryText"]
    assert "RA < 6 ft" in payload["logic_equation_review"]["l1Text"]
    assert "TLS115" in payload["logic_equation_review"]["l1Text"]
    assert "VDT90" in payload["logic_equation_review"]["l4Text"]
    assert "THR_LOCK release" in payload["logic_equation_review"]["l4Text"]
    assert payload["logic_equation_focus_review"]["activeRows"] == ["logic4"]
    assert payload["logic_equation_focus_review"]["selectedAnchor"] == "P035-S05"
    assert "wire_logic4_thr_lock" in payload["logic_equation_focus_review"]["reviewObjectText"]
    assert payload["logic_equation_focus_review"]["highlightedWireCount"] == 1
    assert payload["assembly_map_review"]["visible"] is True
    assert payload["assembly_map_review"]["itemCount"] == 5
    assert payload["assembly_map_review"]["actionCount"] == 5
    assert payload["assembly_map_review"]["focusChipCount"] >= 43
    assert payload["assembly_map_review"]["completeCount"] == 1
    assert "5/5" in payload["assembly_map_review"]["summaryText"]
    assert "20/20" in payload["assembly_map_review"]["summaryText"]
    assert "23/23" in payload["assembly_map_review"]["summaryText"]
    assert "THR_LOCK" in payload["assembly_map_review"]["finalText"]
    assert "完整 demo 电路闭合" in payload["assembly_map_review"]["s05Text"]
    assert "TLS 解锁" in payload["assembly_map_review"]["s01Text"]
    assert payload["topology_matrix_review"]["visible"] is True
    assert payload["topology_matrix_review"]["rowCount"] == 23
    assert payload["topology_matrix_review"]["buttonCount"] == 23
    assert "23/23" in payload["topology_matrix_review"]["summaryText"]
    assert "23/23" in payload["topology_matrix_review"]["readbackText"]
    assert "wire_ra_logic1" in payload["topology_matrix_review"]["firstText"]
    assert "wire_logic4_thr_lock" in payload["topology_matrix_review"]["s05Text"]
    assert "P035-S05" in payload["topology_matrix_review"]["s05Text"]
    assert payload["topology_focus_review"]["activeRows"] == ["wire_logic4_thr_lock"]
    assert payload["topology_focus_review"]["highlightedWireCount"] == 1
    assert "P035-S05" in payload["topology_focus_review"]["readbackText"]
    assert "wire_logic4_thr_lock" in payload["topology_focus_review"]["reviewObjectText"]
    assert payload["topology_filter_review"]["query"] == "THR_LOCK"
    assert "step=P035-S05" in payload["topology_filter_review"]["hash"]
    assert "topology=P035-S05" in payload["topology_filter_review"]["hash"]
    assert "tq=THR_LOCK" in payload["topology_filter_review"]["hash"]
    assert "focus=" not in payload["topology_filter_review"]["hash"]
    assert payload["topology_filter_review"]["selectedFilters"] == ["P035-S05"]
    assert payload["topology_filter_review"]["visibleRows"] == ["wire_logic4_thr_lock"]
    assert payload["topology_filter_review"]["selectedAnchor"] == "P035-S05"
    assert "1/23" in payload["topology_filter_review"]["statusText"]
    assert payload["topology_filter_restore_review"]["query"] == "THR_LOCK"
    assert payload["topology_filter_restore_review"]["hash"] == payload["topology_filter_review"]["hash"]
    assert payload["topology_filter_restore_review"]["selectedFilters"] == ["P035-S05"]
    assert payload["topology_filter_restore_review"]["visibleRows"] == ["wire_logic4_thr_lock"]
    assert payload["topology_filter_restore_review"]["selectedAnchor"] == "P035-S05"
    assert "1/23" in payload["topology_filter_restore_review"]["statusText"]
    assert payload["output_path_review"]["visible"] is True
    assert payload["output_path_review"]["targetCount"] == 5
    assert payload["output_path_review"]["selectedTargets"] == ["thr_lock"]
    assert payload["output_path_review"]["rowCount"] == 15
    assert payload["output_path_review"]["pathOrder"][-1] == "wire_logic4_thr_lock"
    assert payload["output_path_review"]["pathOrder"].index("wire_pdu_vdt90") < payload[
        "output_path_review"
    ]["pathOrder"].index("wire_vdt90_logic4")
    assert payload["output_path_review"]["pathOrder"].index("wire_vdt90_logic4") < payload[
        "output_path_review"
    ]["pathOrder"].index("wire_logic4_thr_lock")
    assert "THR_LOCK" in payload["output_path_review"]["summaryText"]
    assert "15/23" in payload["output_path_review"]["summaryText"]
    assert "wire_logic4_thr_lock" in payload["output_path_review"]["finalText"]
    assert payload["output_path_focus_review"]["activeRows"] == ["wire_logic4_thr_lock"]
    assert payload["output_path_focus_review"]["highlightedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["output_path_focus_review"]["reviewObjectText"]
    assert payload["stored_output_path_review"]["rowCount"] == 15
    assert "15/23" in payload["stored_output_path_review"]["summaryText"]
    assert "P035-S05" in payload["stored_output_path_review"]["finalText"]
    assert "DOCX" in payload["stored_output_path_review"]["finalText"]
    assert payload["output_maturity_review"]["visible"] is True
    assert payload["output_maturity_review"]["stepCount"] == 5
    assert payload["output_maturity_review"]["cellCount"] == 25
    assert payload["output_maturity_review"]["s01TlsActive"] == "true"
    assert payload["output_maturity_review"]["s02EtracActive"] == "true"
    assert payload["output_maturity_review"]["s03EecActive"] == "true"
    assert payload["output_maturity_review"]["s03PduActive"] == "true"
    assert payload["output_maturity_review"]["s05ThrActive"] == "true"
    assert payload["output_maturity_focus_review"]["selectedCells"] == ["P035-S05:thr_lock"]
    assert payload["output_maturity_focus_review"]["highlightedNodeCount"] == 1
    assert "thr_lock" in payload["output_maturity_focus_review"]["reviewObjectText"]
    assert payload["output_maturity_restore_review"]["selectedCells"] == ["P035-S05:thr_lock"]
    assert "step=P035-S05" in payload["output_maturity_restore_review"]["hash"]
    assert "focus=node%3Athr_lock" in payload["output_maturity_restore_review"]["hash"]
    assert payload["output_maturity_restore_review"]["highlightedNodeCount"] == 1
    assert "thr_lock" in payload["output_maturity_restore_review"]["reviewObjectText"]
    assert payload["output_maturity_clear_review"]["selectedCells"] == []
    assert payload["output_maturity_clear_review"]["activeRows"] == ["wire_logic4_thr_lock"]
    assert "wire_logic4_thr_lock" in payload["output_maturity_clear_review"]["reviewObjectText"]
    assert payload["trace_selection_review"] == {
        "selectedAnchorAfterClick": "P035-S05",
        "selectedLastPressed": True,
        "pressedTraceCount": 1,
    }
    assert payload["embedded_trace_highlight_review"]["selectedNodeCount"] == 4
    assert payload["embedded_trace_highlight_review"]["selectedWireCount"] == 3
    assert payload["embedded_trace_highlight_review"]["stylePresent"] is True
    assert "P035-S05" in payload["embedded_trace_highlight_review"]["statusText"]
    assert payload["embedded_trace_chip_focus_review"]["focusNodeChipPresent"] is True
    assert payload["embedded_trace_chip_focus_review"]["focusWireChipPresent"] is True
    assert payload["embedded_trace_chip_focus_review"]["focusedNodeCount"] == 0
    assert payload["embedded_trace_chip_focus_review"]["focusedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["embedded_trace_chip_focus_review"]["statusText"]
    assert payload["coverage_matrix_review"]["nodeButtonCount"] == 20
    assert payload["coverage_matrix_review"]["wireButtonCount"] == 23
    assert "20/20" in payload["coverage_matrix_review"]["contractText"]
    assert "23/23" in payload["coverage_matrix_review"]["contractText"]
    assert payload["coverage_matrix_review"]["focusedNodeCount"] == 0
    assert payload["coverage_matrix_review"]["focusedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["coverage_matrix_review"]["statusText"]
    assert payload["coverage_filter_review"]["query"] == "logic4"
    assert payload["coverage_filter_review"]["visibleNodeCount"] == 1
    assert payload["coverage_filter_review"]["visibleWireCount"] == 3
    assert "4/43" in payload["coverage_filter_review"]["statusText"]
    assert payload["coverage_filter_review"]["focusedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["coverage_filter_review"]["focusStatusText"]
    assert payload["keyboard_review"]["traceSelectedAnchor"] == "P035-S05"
    assert payload["keyboard_review"]["traceActiveAnchor"] == "P035-S05"
    assert payload["keyboard_review"]["traceTabStopAnchors"] == ["P035-S05"]
    assert payload["keyboard_review"]["coverageActiveKind"] == "wire"
    assert payload["keyboard_review"]["coverageActiveId"] == "wire_logic4_thr_lock"
    assert payload["keyboard_review"]["coverageTabStopIds"] == ["wire_logic4_thr_lock"]
    assert payload["keyboard_review"]["focusedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["keyboard_review"]["statusText"]
    assert "P035-S05" in payload["keyboard_review"]["reviewAnchorText"]
    assert "wire_logic4_thr_lock" in payload["keyboard_review"]["reviewObjectText"]
    assert payload["trace_switch_focus_reset_review"]["selectedAnchor"] == "P035-S02"
    assert payload["trace_switch_focus_reset_review"]["coverageTabStopIds"] == ["logic4"]
    assert payload["trace_switch_focus_reset_review"]["pressedCoverageIds"] == []
    assert "整句链路" in payload["trace_switch_focus_reset_review"]["reviewObjectText"]
    assert payload["step_playback_review"]["selectedAnchor"] == "P035-S04"
    assert payload["step_playback_review"]["activeStep"] == "P035-S04"
    assert payload["step_playback_review"]["activeButtonCount"] == 1
    assert payload["step_playback_review"]["highlightedNodeCount"] == 18
    assert payload["step_playback_review"]["highlightedWireCount"] == 20
    assert "18/20" in payload["step_playback_review"]["nodeCountText"]
    assert "20/23" in payload["step_playback_review"]["wireCountText"]
    assert "累计构建" in payload["step_playback_review"]["reviewObjectText"]
    assert payload["assembly_map_action_review"]["activeStep"] == "P035-S05"
    assert payload["assembly_map_action_review"]["activeButtonCount"] == 1
    assert payload["assembly_map_action_review"]["highlightedNodeCount"] == 20
    assert payload["assembly_map_action_review"]["highlightedWireCount"] == 23
    assert "累计构建" in payload["assembly_map_action_review"]["reviewObjectText"]
    assert "logic4" in payload["object_provenance_review"]["objectText"]
    assert payload["object_provenance_review"]["sourceCount"] >= 2
    assert payload["object_provenance_review"]["stepCount"] >= 1
    assert any("logic4" in item for item in payload["object_provenance_review"]["sourceItems"])
    assert any("P035-S05" in item for item in payload["object_provenance_review"]["stepItems"])
    assert "logic4" in payload["signal_neighborhood_review"]["objectText"]
    assert payload["signal_neighborhood_review"]["incomingCount"] == 2
    assert payload["signal_neighborhood_review"]["outgoingCount"] == 1
    assert payload["signal_neighborhood_review"]["adjacentCount"] == 3
    assert "wire_vdt90_logic4" in payload["signal_neighborhood_review"]["incomingText"]
    assert "wire_logic3_logic4" in payload["signal_neighborhood_review"]["incomingText"]
    assert "wire_logic4_thr_lock" in payload["signal_neighborhood_review"]["outgoingText"]
    assert "THR_LOCK" in payload["signal_neighborhood_review"]["adjacentText"]
    assert "wire_logic4_thr_lock" in payload["signal_neighborhood_wire_review"]["objectText"]
    assert "L4" in payload["signal_neighborhood_wire_review"]["incomingText"]
    assert "THR_LOCK" in payload["signal_neighborhood_wire_review"]["outgoingText"]
    assert "wire_logic4_thr_lock" in payload["wire_provenance_review"]["objectText"]
    assert payload["wire_provenance_review"]["sourceCount"] >= 2
    assert payload["wire_provenance_review"]["stepCount"] >= 1
    assert any("logic4" in item or "thr_lock" in item for item in payload["wire_provenance_review"]["sourceItems"])
    assert any("P035-S05" in item for item in payload["wire_provenance_review"]["stepItems"])
    assert payload["completion_ladder_review"]["stepCount"] == 5
    assert "5/5" in payload["completion_ladder_review"]["summaryText"]
    assert "EEC" in payload["completion_ladder_review"]["s03Text"]
    assert "PLS" in payload["completion_ladder_review"]["s03Text"]
    assert "PDU" in payload["completion_ladder_review"]["s03Text"]
    assert "THR_LOCK" in payload["completion_ladder_review"]["s05Text"]
    assert "20/20" in payload["completion_ladder_review"]["s05Text"]
    assert "23/23" in payload["completion_ladder_review"]["s05Text"]
    assert payload["review_packet_review"]["visible"] is True
    assert payload["review_packet_review"]["dashboardVisible"] is True
    assert payload["review_packet_review"]["dashboardMetricCount"] == 5
    assert payload["review_packet_review"]["dashboardPassMetricCount"] >= 4
    assert payload["review_packet_review"]["dashboardChecklistCount"] == 5
    assert payload["review_packet_review"]["dashboardPassChecklistCount"] >= 4
    assert "67 覆盖项" in payload["review_packet_review"]["dashboardSummary"]
    assert "5/5 输出" in payload["review_packet_review"]["dashboardSummary"]
    assert any("覆盖账本" in item for item in payload["review_packet_review"]["dashboardMetricLabels"])
    assert payload["review_packet_review"]["gateCount"] == 5
    assert payload["review_packet_review"]["passGateCount"] >= 4
    assert payload["review_packet_after_wire_focus"]["passGateCount"] == 5
    assert payload["review_packet_after_wire_focus"]["dashboardPassMetricCount"] == 5
    assert payload["review_packet_after_wire_focus"]["dashboardPassChecklistCount"] == 5
    assert "5/5 gate" in payload["review_packet_after_wire_focus"]["dashboardSummary"]
    assert "uploads/20260409-thrust-reverser-control-logic.docx" in payload["review_packet_review"]["sourceText"]
    assert "20/20" in payload["review_packet_review"]["contractText"]
    assert "23/23" in payload["review_packet_review"]["contractText"]
    assert "P035-S05" in payload["review_packet_review"]["stepText"]
    assert "wire_logic4_thr_lock" in payload["review_packet_after_wire_focus"]["objectText"]
    assert payload["custody_matrix_review"]["stepCount"] == 5
    assert payload["custody_matrix_review"]["activeButtonCount"] == 1
    assert "5/5" in payload["custody_matrix_review"]["summaryText"]
    assert "20/20" in payload["custody_matrix_review"]["summaryText"]
    assert "23/23" in payload["custody_matrix_review"]["summaryText"]
    assert "P035-S04" in payload["custody_matrix_review"]["activeText"]
    assert "18/20" in payload["custody_matrix_review"]["activeText"]
    assert "20/23" in payload["custody_matrix_review"]["activeText"]
    assert "18/20" in payload["custody_matrix_review"]["s04Text"]
    assert "20/23" in payload["custody_matrix_review"]["s04Text"]
    assert "THR_LOCK" in payload["custody_matrix_review"]["s05Text"]
    assert payload["custody_matrix_review"]["highlightedNodeCount"] == 18
    assert payload["custody_matrix_review"]["highlightedWireCount"] == 20
    assert "step=P035-S05" in payload["review_deep_link"]["hash"]
    assert "focus=wire%3Awire_logic4_thr_lock" in payload["review_deep_link"]["hash"]
    assert "q=logic4" in payload["review_deep_link"]["hash"]
    assert "/demo-reconstruction#" in payload["review_deep_link"]["linkHref"]
    assert payload["review_deep_link"]["restoredSelectedAnchor"] == "P035-S05"
    assert payload["review_deep_link"]["restoredQuery"] == "logic4"
    assert payload["review_deep_link"]["restoredVisibleNodeCount"] == 1
    assert payload["review_deep_link"]["restoredVisibleWireCount"] == 3
    assert payload["review_deep_link"]["restoredFocusedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["review_deep_link"]["restoredObjectText"]
    assert "wire_logic4_thr_lock" in payload["review_deep_link"]["restoredStatusText"]
    assert payload["source_chip_focus_review"]["sourceNodeFocusChipCount"] >= 20
    assert payload["source_chip_focus_review"]["sourceWireFocusChipCount"] >= 23
    assert payload["source_chip_focus_review"]["focusedNodeCount"] == 0
    assert payload["source_chip_focus_review"]["focusedWireCount"] == 1
    assert "wire_logic4_thr_lock" in payload["source_chip_focus_review"]["statusText"]
    assert payload["responsive_geometry"]["desktop"]["noHorizontalOverflow"] is True
    assert payload["responsive_geometry"]["mobile"]["noHorizontalOverflow"] is True
    assert payload["embedded_palette"]["html_class"] is True
    assert payload["embedded_palette"]["palette"] == "codex-light"
    assert payload["embedded_palette"]["body_background"] == "rgb(247, 248, 251)"
    assert payload["embedded_palette"]["panel_background"] == "rgb(255, 255, 255)"
    assert payload["interactions"]["max-reverse"]["status_badge"] == "DEPLOYED"
    assert payload["interactions"]["max-reverse"]["hud_thr_lock"] == "RELEASED"
    assert payload["interactions"]["max-reverse"]["outputs"]["thr_lock"] == "ON"
    assert payload["interactions"]["inhibit-block"]["status_badge"] == "FAULT"
    assert payload["interactions"]["inhibit-block"]["outputs"]["thr_lock"] != "ON"
    assert payload["output_mirror"]["max-reverse"]["status"] == "DEPLOYED"
    assert payload["output_mirror"]["max-reverse"]["outputs"]["thr_lock"] == "ON"
    assert "DEPLOYED" in payload["output_mirror"]["max-reverse"]["custody"]
    assert "ON" in payload["output_mirror"]["max-reverse"]["custody"]
    assert "L4:ON" in payload["output_mirror"]["max-reverse"]["logic"]
    assert payload["output_mirror"]["inhibit-block"]["status"] == "FAULT"
    assert payload["output_mirror"]["inhibit-block"]["outputs"]["thr_lock"] == "BLOCKED"
    assert "FAULT" in payload["output_mirror"]["inhibit-block"]["custody"]
    assert "BLOCKED" in payload["output_mirror"]["inhibit-block"]["custody"]
    assert "BLOCKED" in payload["output_mirror"]["inhibit-block"]["thr"]
    assert payload["scenario_ledger_review"]["rowCount"] == 5
    assert "2/5" in payload["scenario_ledger_review"]["statusText"]
    assert payload["scenario_ledger_review"]["truthRowCount"] == 5
    assert payload["scenario_ledger_review"]["truthCapturedCount"] == 2
    assert "2/5" in payload["scenario_ledger_review"]["truthStatusText"]
    assert payload["scenario_ledger_review"]["activeRows"] == ["inhibit-block"]
    assert payload["scenario_ledger_review"]["truthActiveRows"] == ["inhibit-block"]
    assert "DEPLOYED" in payload["scenario_ledger_review"]["maxReverseText"]
    assert "THR:ON" in payload["scenario_ledger_review"]["maxReverseText"]
    assert "FAULT" in payload["scenario_ledger_review"]["inhibitText"]
    assert "THR:BLOCKED" in payload["scenario_ledger_review"]["inhibitText"]
    assert "L4:ON" in payload["scenario_ledger_review"]["truthMaxReverseText"]
    assert "THR:ON" in payload["scenario_ledger_review"]["truthMaxReverseText"]
    assert "FAULT" in payload["scenario_ledger_review"]["truthInhibitText"]
    assert "THR:BLOCKED" in payload["scenario_ledger_review"]["truthInhibitText"]
    assert payload["scenario_ledger_outer_control"]["status"] == "DEPLOYED"
    assert payload["scenario_ledger_outer_control"]["output"] == "ON"
    assert payload["scenario_ledger_outer_control"]["activeRows"] == ["max-reverse"]
    assert payload["scenario_ledger_outer_control"]["truthActiveRows"] == ["max-reverse"]
    assert "L4:ON" in payload["scenario_ledger_outer_control"]["truthMaxReverseText"]
    assert "THR:ON" in payload["scenario_ledger_outer_control"]["truthMaxReverseText"]
    assert payload["operator_runway_review"]["rowCount"] == 6
    assert payload["operator_runway_review"]["readyRowCount"] == 6
    assert "6/6" in payload["operator_runway_review"]["statusText"]
    assert "THR_LOCK" in payload["operator_runway_review"]["l4Text"]
    assert "BLOCKED" in payload["operator_runway_review"]["inhibitText"]
    assert payload["operator_runway_l4_review"]["activeRows"] == ["runway-l4-thr-lock"]
    assert "05/06" in payload["operator_runway_l4_review"]["statusText"]
    assert "P035-S05" in payload["operator_runway_l4_review"]["stepText"]
    assert "wire_logic4_thr_lock" in payload["operator_runway_l4_review"]["objectText"]
    assert payload["operator_runway_l4_review"]["output"] == "ON"
    assert "DEPLOYED" in payload["operator_runway_l4_review"]["readbackText"]
    assert payload["operator_runway_inhibit_review"]["activeRows"] == ["runway-inhibit"]
    assert "06/06" in payload["operator_runway_inhibit_review"]["statusText"]
    assert "P035-S01" in payload["operator_runway_inhibit_review"]["stepText"]
    assert "reverser_inhibited" in payload["operator_runway_inhibit_review"]["objectText"]
    assert payload["operator_runway_inhibit_review"]["output"] == "BLOCKED"
    assert "FAULT" in payload["operator_runway_inhibit_review"]["readbackText"]
    assert payload["proof_transcript_review"]["rowCount"] == 6
    assert payload["proof_transcript_review"]["readyRowCount"] == 6
    assert "6/6" in payload["proof_transcript_review"]["summaryText"]
    assert "THR_LOCK" in payload["proof_transcript_review"]["l4Text"]
    assert "抑制" in payload["proof_transcript_review"]["inhibitText"]
    assert "反推锁不释放" in payload["proof_transcript_review"]["inhibitText"]
    assert "RA/SW1/TLS" not in payload["proof_transcript_review"]["inhibitText"]
    assert payload["proof_transcript_l4_review"]["activeRows"] == ["runway-l4-thr-lock"]
    assert payload["proof_transcript_l4_review"]["runwayActiveRows"] == ["runway-l4-thr-lock"]
    assert "wire_logic4_thr_lock" in payload["proof_transcript_l4_review"]["objectText"]
    assert payload["proof_transcript_l4_review"]["output"] == "ON"
    assert payload["proof_transcript_inhibit_review"]["activeRows"] == ["runway-inhibit"]
    assert payload["proof_transcript_inhibit_review"]["runwayActiveRows"] == ["runway-inhibit"]
    assert "reverser_inhibited" in payload["proof_transcript_inhibit_review"]["objectText"]
    assert payload["proof_transcript_inhibit_review"]["output"] == "BLOCKED"
    assert payload["control_strip_review"]["actionCount"] == 3
    assert "THR" in payload["control_strip_review"]["outputText"]
    assert payload["control_strip_l4_review"]["activeActions"] == ["prove-thr"]
    assert "05/06" in payload["control_strip_l4_review"]["statusText"]
    assert "P035-S05" in payload["control_strip_l4_review"]["stepText"]
    assert "wire_logic4_thr_lock" in payload["control_strip_l4_review"]["objectText"]
    assert "THR ON" in payload["control_strip_l4_review"]["outputText"]
    assert "THR_LOCK" in payload["control_strip_l4_review"]["pathText"]
    assert payload["control_strip_l4_review"]["runwayActiveRows"] == ["runway-l4-thr-lock"]
    assert payload["control_strip_l4_review"]["transcriptActiveRows"] == ["runway-l4-thr-lock"]
    assert payload["control_strip_inhibit_review"]["activeActions"] == ["block-inhibit"]
    assert "06/06" in payload["control_strip_inhibit_review"]["statusText"]
    assert "P035-S01" in payload["control_strip_inhibit_review"]["stepText"]
    assert "reverser_inhibited" in payload["control_strip_inhibit_review"]["objectText"]
    assert "THR BLOCKED" in payload["control_strip_inhibit_review"]["outputText"]
    assert "BLOCKED" in payload["control_strip_inhibit_review"]["pathText"]
    assert payload["control_strip_inhibit_review"]["runwayActiveRows"] == ["runway-inhibit"]
    assert payload["control_strip_inhibit_review"]["transcriptActiveRows"] == ["runway-inhibit"]
    assert payload["sentence_runner_review"]["buttonCount"] == 5
    assert "P035-S01" in payload["sentence_runner_review"]["firstText"]
    assert "20/20 节点" in payload["sentence_runner_review"]["finalText"]
    assert "23/23 连线" in payload["sentence_runner_review"]["finalText"]
    assert payload["sentence_runner_s03_review"]["activeSteps"] == ["P035-S03"]
    assert "3/5" in payload["sentence_runner_s03_review"]["statusText"]
    assert "P035-S03" in payload["sentence_runner_s03_review"]["selectedAnchor"]
    assert "17/20" in payload["sentence_runner_s03_review"]["reviewSync"]
    assert payload["sentence_runner_s05_review"]["activeSteps"] == ["P035-S05"]
    assert "5/5" in payload["sentence_runner_s05_review"]["statusText"]
    assert "完整电路闭合" in payload["sentence_runner_s05_review"]["statusText"]
    assert "20/20 节点" in payload["sentence_runner_s05_review"]["readbackText"]
    assert "23/23 连线" in payload["sentence_runner_s05_review"]["readbackText"]
    assert "P035-S05" in payload["sentence_runner_s05_review"]["selectedAnchor"]
    assert "P035-S05" in payload["sentence_runner_s05_review"]["controlStep"]
    assert payload["proof_path_review"]["stepCount"] == 5
    assert payload["proof_path_review"]["finalCount"] == 1
    assert payload["proof_path_review"]["focusChipCount"] >= 10
    assert "tls_unlocked" in payload["proof_path_review"]["firstFocusIds"]
    assert "wire_logic4_thr_lock" in payload["proof_path_review"]["finalFocusIds"]
    assert "P035-S01" in payload["proof_path_review"]["firstText"]
    assert "飞机离地小于6ft" in payload["proof_path_review"]["firstText"]
    assert "本句 6 节点 / 5 连线" in payload["proof_path_review"]["firstText"]
    assert "P035-S05" in payload["proof_path_review"]["finalText"]
    assert "反推电子锁解锁" in payload["proof_path_review"]["finalText"]
    assert "本句 4 节点 / 3 连线" in payload["proof_path_review"]["finalText"]
    assert "20/20 节点" in payload["proof_path_review"]["finalText"]
    assert "23/23 连线" in payload["proof_path_review"]["finalText"]
    assert payload["proof_path_final_review"]["activeSteps"] == ["P035-S05"]
    assert "5/5" in payload["proof_path_final_review"]["statusText"]
    assert "20/20 节点" in payload["proof_path_final_review"]["readbackText"]
    assert "23/23 连线" in payload["proof_path_final_review"]["readbackText"]
    assert payload["proof_path_final_review"]["selectedAnchor"] == "P035-S05"
    assert "wire_logic4_thr_lock" in payload["proof_path_final_review"]["reviewObjectText"]
    assert "聚焦连线" in payload["proof_path_final_review"]["reviewSyncText"]
    assert "wire_logic4_thr_lock" in payload["proof_path_object_inspector_final_review"]["objectText"]
    assert "连线" in payload["proof_path_object_inspector_final_review"]["coverageText"]
    assert payload["proof_path_object_inspector_final_review"]["neighborCount"] >= 2
    assert "THR_LOCK" in payload["proof_path_object_inspector_final_review"]["neighborText"]
    assert "logic4" in payload["proof_path_object_inspector_neighbor_review"]["reviewObjectText"]
    assert "logic4" in payload["proof_path_object_inspector_neighbor_review"]["readbackText"]
    assert "logic4" in payload["proof_path_object_inspector_neighbor_review"]["inspectorObjectText"]
    assert payload["proof_path_chip_review"]["selectedAnchor"] == "P035-S01"
    assert "tls_unlocked" in payload["proof_path_chip_review"]["reviewObjectText"]
    assert "聚焦节点" in payload["proof_path_chip_review"]["reviewSyncText"]
    assert "tls_unlocked" in payload["proof_path_chip_review"]["readbackText"]
    assert "tls_unlocked" in payload["proof_path_object_inspector_chip_review"]["objectText"]
    assert "节点" in payload["proof_path_object_inspector_chip_review"]["coverageText"]
    assert payload["proof_path_object_inspector_chip_review"]["neighborCount"] >= 2
    assert "L3" in payload["proof_path_object_inspector_chip_review"]["neighborText"]
    assert payload["proof_path_coverage_grid_review"]["stepCount"] == 5
    assert payload["proof_path_coverage_grid_review"]["focusChipCount"] >= 10
    assert "5/5 步" in payload["proof_path_coverage_grid_review"]["statusText"]
    assert "20/20 节点" in payload["proof_path_coverage_grid_review"]["statusText"]
    assert "23/23 连线" in payload["proof_path_coverage_grid_review"]["statusText"]
    assert "TLS 115VAC" in payload["proof_path_coverage_grid_review"]["firstText"]
    assert "THR_LOCK" in payload["proof_path_coverage_grid_review"]["finalText"]
    assert payload["proof_path_coverage_grid_final_review"]["activeSteps"] == ["P035-S05"]
    assert payload["proof_path_coverage_grid_final_review"]["highlightedNodeCount"] == 20
    assert payload["proof_path_coverage_grid_final_review"]["highlightedWireCount"] == 23
    assert "累计构建" in payload["proof_path_coverage_grid_final_review"]["reviewObjectText"]
    assert payload["proof_path_coverage_grid_focus_review"]["activeSteps"] == ["P035-S05"]
    assert payload["proof_path_coverage_grid_focus_review"]["activeFocusIds"] == [
        "wire_logic4_thr_lock"
    ]
    assert "wire_logic4_thr_lock" in payload["proof_path_coverage_grid_focus_review"]["readbackText"]
    assert "wire_logic4_thr_lock" in payload["proof_path_coverage_grid_focus_review"]["reviewObjectText"]
    assert "wire_logic4_thr_lock" in payload["proof_path_coverage_grid_focus_review"]["inspectorObjectText"]
    assert payload["proof_path_output_map_review"]["targetCount"] == 5
    assert payload["proof_path_output_map_review"]["activeTargets"] == ["thr_lock"]
    assert "5/5" in payload["proof_path_output_map_review"]["statusText"]
    assert "wire_logic4_thr_lock" in payload["proof_path_output_map_review"]["thrText"]
    assert "wire_logic1_tls115" in payload["proof_path_output_map_review"]["tlsText"]
    assert payload["proof_path_output_map_tls_review"]["activeTargets"] == ["tls115"]
    assert "TLS 115VAC" in payload["proof_path_output_map_tls_review"]["readbackText"]
    assert "wire_logic1_tls115" in payload["proof_path_output_map_tls_review"]["reviewObjectText"]
    assert "wire_logic1_tls115" in payload["proof_path_output_map_tls_review"]["inspectorObjectText"]
    assert payload["scenario_comparator_review"]["buttonCount"] == 2
    assert "最大反推" in payload["scenario_comparator_review"]["maxText"]
    assert "抑制阻塞" in payload["scenario_comparator_review"]["inhibitText"]
    assert payload["scenario_comparator_max_review"]["activeActions"] == ["max-reverse"]
    assert "/2" in payload["scenario_comparator_max_review"]["statusText"]
    assert "最大反推" in payload["scenario_comparator_max_review"]["readbackText"]
    assert "THR ON" in payload["scenario_comparator_max_review"]["readbackText"]
    assert payload["scenario_comparator_max_review"]["output"] == "ON"
    assert payload["scenario_comparator_inhibit_review"]["activeActions"] == ["inhibit-block"]
    assert "2/2" in payload["scenario_comparator_inhibit_review"]["statusText"]
    assert "抑制阻塞" in payload["scenario_comparator_inhibit_review"]["readbackText"]
    assert "THR BLOCKED" in payload["scenario_comparator_inhibit_review"]["readbackText"]
    assert payload["scenario_comparator_inhibit_review"]["output"] == "BLOCKED"
    assert payload["review_verdict_review"]["cardCount"] == 5
    assert "5/5" in payload["review_verdict_review"]["statusText"]
    assert "源记录" in payload["review_verdict_review"]["sourceText"]
    assert "20/20" in payload["review_verdict_review"]["circuitText"]
    assert "23/23" in payload["review_verdict_review"]["circuitText"]
    assert "5/5" in payload["review_verdict_review"]["outputsText"]
    assert "wire_logic4_thr_lock" in payload["review_verdict_review"]["focusText"]
    assert "控制逻辑未改动" in payload["review_verdict_review"]["boundaryText"]
    assert "证据可审" in payload["review_verdict_review"]["readbackText"]
    assert payload["deterministic_gates"] == {
        "browser_boot": "pass",
        "screenshots": "pass",
        "first_screen_operator_guide": "pass",
        "docx_sentence_circuit_map": "pass",
        "requirement_coverage_ledger": "pass",
        "review_index_navigation": "pass",
        "logic_equation_board_readback": "pass",
        "assembly_map_readback": "pass",
        "topology_matrix_readback": "pass",
        "topology_filter_workbench": "pass",
        "output_path_lane_readback": "pass",
        "output_maturity_matrix_readback": "pass",
        "trace_selection_interaction": "pass",
        "embedded_trace_highlight": "pass",
        "embedded_trace_chip_focus": "pass",
        "coverage_matrix_focus": "pass",
        "coverage_matrix_filter": "pass",
        "keyboard_trace_navigation": "pass",
        "coverage_keyboard_navigation": "pass",
        "review_cursor_status": "pass",
        "trace_switch_clears_object_focus": "pass",
        "step_playback_cumulative_circuit": "pass",
        "object_provenance_traceability": "pass",
        "signal_neighborhood_readback": "pass",
        "completion_ladder_readback": "pass",
        "review_packet_readiness": "pass",
        "custody_matrix_readback": "pass",
        "review_hash_link": "pass",
        "review_hash_restore": "pass",
        "source_chip_focus": "pass",
        "responsive_geometry": "pass",
        "embedded_codex_light_palette": "pass",
        "node_wire_pixels": "pass",
        "preset_interactions": "pass",
        "hud_output_linkage": "pass",
        "output_mirror_sync": "pass",
        "scenario_ledger_readback": "pass",
        "operator_runway_readback": "pass",
        "proof_transcript_readback": "pass",
        "control_strip_readback": "pass",
        "sentence_runner_readback": "pass",
        "proof_path_timeline": "pass",
        "proof_path_coverage_grid": "pass",
        "proof_path_output_map": "pass",
        "scenario_comparator_readback": "pass",
        "review_verdict_readback": "pass",
        "boundary": "pass",
    }


def test_demo_html_reconstruction_mvp_checker_rejects_fixture_drift(tmp_path: Path) -> None:
    drifted_fixture = tmp_path / "demo_html_reconstruction_mvp_v0_1.json"
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    fixture["contract"]["expected_node_count"] = 21
    drifted_fixture.write_text(json.dumps(fixture), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(CHECKER_SCRIPT_PATH),
            "--fixture",
            str(drifted_fixture),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_script_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert payload["schema_valid"] is True
    assert payload["fixture_match"] is False
    assert "golden_demo.node_count" in payload["mismatches"]


def test_demo_html_reconstruction_mvp_gate_is_wired_into_make_and_ci() -> None:
    makefile = MAKEFILE_PATH.read_text(encoding="utf-8")
    workflow = GSD_AUTOMATION_WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "demo-html-reconstruction-mvp" in makefile
    assert "demo-html-reconstruction-browser-acceptance" in makefile
    assert "scripts/verify_demo_html_reconstruction_mvp.py --format json" in makefile
    assert "scripts/verify_demo_html_reconstruction_browser_acceptance.py --format json" in makefile
    assert "test: demo-html-reconstruction-mvp" in makefile
    assert "Verify demo.html reconstruction MVP" in workflow
    assert "scripts/verify_demo_html_reconstruction_mvp.py --format json" in workflow
