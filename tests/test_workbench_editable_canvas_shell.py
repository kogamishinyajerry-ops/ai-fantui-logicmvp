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


def test_js_wires_draft_derivation_node_selection_and_evidence_api() -> None:
    js = _js()

    assert "function installEditableWorkbenchShell" in js
    assert "well-harness-editable-workbench-draft-v1" in js
    assert "workbench-derive-draft-btn" in js
    assert "data-editable-node-id" in js
    assert "workbench-inspector-node-label" in js
    assert "data-evidence-api" in js


def test_js_builds_changerequest_linear_handoff_without_live_linear_mutation() -> None:
    js = _js()

    assert "function buildEditableHandoffPacket" in js
    assert "function buildChangeRequestProofPacket" in js
    assert "function linearIssueBodyFromProofPacket" in js
    assert "function prProofTextFromProofPacket" in js
    assert "workbench-generate-handoff-btn" in js
    assert "changerequest_proof_packet" in js
    assert 'issue: "JER-TBD"' in js
    assert "Candidate state:" in js
    assert "Certification claim:" in js
    assert "Truth-level impact:" in js
    assert "Red lines touched:" in js
    assert "No live Linear mutation" in js
