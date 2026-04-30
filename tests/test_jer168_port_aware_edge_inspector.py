from __future__ import annotations

from pathlib import Path


def test_workbench_edge_paths_carry_port_and_signal_metadata() -> None:
    js = Path("src/well_harness/static/workbench.js").read_text(encoding="utf-8")

    assert "function edgeInspectorPayload" in js
    assert "data-source-port-id" in js
    assert "data-target-port-id" in js
    assert "data-edge-signal-id" in js
    assert "source_port_id" in js
    assert "target_port_id" in js
    assert "signal_id" in js
    assert "function edgeInterfaceBinding" in js
    assert "function setEdgeInterfaceBinding" in js


def test_workbench_edge_selection_renders_evidence_only_inspector() -> None:
    js = Path("src/well_harness/static/workbench.js").read_text(encoding="utf-8")
    css = Path("src/well_harness/static/workbench.css").read_text(encoding="utf-8")

    assert "function selectEditableEdge" in js
    assert "function renderEdgeInspector" in js
    assert "truth_effect: none" in js
    assert "evidence_gap" in js
    assert "workbench-inspector-edge-list" in js
    assert "workbench-interface-binding-owner" in js
    assert "workbench-interface-port-local" in js
    assert "workbench-interface-port-peer" in js
    assert "buildHardwareEvidenceV2Report(activeInterfaceBindingTarget(), [])" in js
    assert "workbench-hardware-evidence-v2-target" in Path(
        "src/well_harness/static/workbench.html"
    ).read_text(encoding="utf-8")
    assert ".workbench-editable-edges path[aria-pressed=\"true\"]" in css
    assert ".workbench-inspector-edge-list" in css


def test_workbench_edge_disconnect_prefers_selected_edge() -> None:
    js = Path("src/well_harness/static/workbench.js").read_text(encoding="utf-8")

    assert "selectedEdge" in js
    assert "selectedEdge.id" in js
    assert "disconnectSelectedEditableEdge" in js
    assert "applySelectedInterfaceBinding" in js
