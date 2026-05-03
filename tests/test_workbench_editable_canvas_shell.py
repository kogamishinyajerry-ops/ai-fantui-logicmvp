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


def test_editable_canvas_shell_is_explicitly_sandbox_only() -> None:
    html = _html()

    assert "sandbox candidate" in html
    assert "not certified truth" in html
    assert "Truth impact" in html
    assert "none · sandbox candidate only" in html


def test_editable_canvas_exposes_reference_logic_nodes() -> None:
    parser = _parsed()

    assert parser.node_ids == {"logic1", "logic2", "logic3", "logic4"}
    for node_id in parser.node_ids:
        assert f'data-editable-node-id="{node_id}"' in _html()
    assert 'data-node-op="and"' in _html()
    assert 'data-hardware-evidence="evidence_gap"' in _html()


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


def test_reference_svg_fragment_remains_as_sample_pack_not_primary_canvas() -> None:
    html = _html()

    sample_pack = re.search(
        r'<details class="workbench-reference-sample-pack">(.*?)</details>',
        html,
        re.DOTALL,
    )
    assert sample_pack is not None
    assert 'id="workbench-circuit-hero-mount"' in sample_pack.group(0)
    assert "Reference sample pack" in sample_pack.group(0)


def test_css_declares_editable_workbench_layout() -> None:
    css = _css()

    assert ".workbench-editable-shell" in css
    assert ".workbench-editable-main" in css
    assert "grid-template-columns: 46px minmax(420px, 1fr) minmax(260px, 340px)" in css
    assert ".workbench-evidence-inspector" in css
    assert ".workbench-sandbox-timeline-strip" in css
    assert ".workbench-selected-debug-timeline" in css


def test_editor_command_palette_controls_are_exposed_as_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-open-command-palette-btn"' in html
    assert 'id="workbench-command-palette"' in html
    assert 'id="workbench-command-palette-filter"' in html
    assert 'id="workbench-command-palette-status"' in html
    for command_id in [
        "create_node",
        "rename_subsystem",
        "duplicate_selection",
        "group_selection",
        "wire_edge",
        "run_sandbox",
        "debug_selection",
        "export_draft",
        "import_draft",
        "prepare_archive",
    ]:
        assert f'data-command-palette-command="{command_id}"' in html
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
    assert 'id="workbench-subsystem-name"' in html
    assert 'id="workbench-create-subsystem-btn"' in html
    assert 'id="workbench-rename-subsystem-btn"' in html
    assert 'id="workbench-ungroup-subsystem-btn"' in html
    assert "Subsystem edits are sandbox metadata only. Truth effect: none." in html
    assert ".workbench-subsystem-overlay" in css
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
    assert "Workspace document is sandbox evidence only. Truth effect: none." in html
    assert ".workbench-workspace-document-status" in css
    assert ".workbench-workspace-document-facts" in css


def test_canvas_interaction_status_controls_are_sandbox_only_ui() -> None:
    html = _html()
    css = _css()

    assert 'id="workbench-canvas-interaction-status"' in html
    assert 'id="workbench-canvas-selected-node-count"' in html
    assert 'id="workbench-canvas-selected-edge-count"' in html
    assert 'id="workbench-canvas-last-action"' in html
    assert "Canvas interactions are sandbox evidence only. Truth effect: none." in html
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
    assert "function renderSubsystemOverlays" in js
    assert "subsystem_groups" in js
    assert "subsystem_groups truth_effect must be none" in js
    assert "subsystem_groups_checksum" in js
    assert "data-subsystem-id" in js
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
    assert "edge_label" in js
    assert "route_metadata" in js
    assert "data-edge-label" in js
    assert "data-route-mode" in js
    assert "workbench-edge-label" in js
    assert "function beginPortHandleDrag" in js
    assert "function updatePortHandleDrag" in js
    assert "function completePortHandleDrag" in js
    assert "data-port-drag-state" in js
    assert "data-port-drag-compatibility" in js
    assert "workbench-port-drag-preview" in js
    assert "ui_draft.port_drag_wiring" in js
    assert "port_compatibility_report" in js
    assert "port_compatibility_report_checksum" in js
    assert ".workbench-port-drag-preview" in _css()
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
