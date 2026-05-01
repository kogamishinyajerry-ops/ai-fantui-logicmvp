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
