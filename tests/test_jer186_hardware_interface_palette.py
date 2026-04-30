from __future__ import annotations

from pathlib import Path

from well_harness.hardware_evidence_report import build_hardware_evidence_report  # type: ignore[import-untyped]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_hardware_interface_palette_dom_and_js_contract_are_sandbox_only() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    js = WORKBENCH_JS.read_text(encoding="utf-8")
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert 'id="workbench-hardware-palette"' in html
    assert 'id="workbench-hardware-palette-filter"' in html
    assert 'id="workbench-hardware-palette-action"' in html
    assert 'value="create-node"' in html
    assert 'value="apply-binding"' in html
    assert "function hardwarePaletteItemsFromEvidence" in js
    assert "function addHardwarePaletteNode" in js
    assert "function applyHardwarePaletteBinding" in js
    assert "function buildHardwarePaletteSummary" in js
    assert "read_only_hardware_evidence_api" in js
    assert "source_ref: normalizedInterfaceField" in js
    assert "controller_truth_modified: false" in js
    assert "truth_effect: \"none\"" in js
    assert ".workbench-hardware-palette-list" in css
    assert ".workbench-hardware-palette-item" in css


def test_hardware_evidence_report_feeds_lru_and_signal_palette_items() -> None:
    report = build_hardware_evidence_report(system_id="thrust-reverser")
    evidence_index = report["evidence_index"]

    assert report["boundaries"]["read_only"] is True
    assert report["boundaries"]["controller_truth_modified"] is False
    assert report["truth_level_impact"] == "none"
    assert evidence_index["truth_effect"] == "none"
    assert evidence_index["lru_inventory_count"] == 11
    assert evidence_index["signal_binding_count"] == 18
    assert any(item["id"] == "etrac" for item in evidence_index["lru_inventory"])
    assert any(item["signal_id"] == "SW1" for item in evidence_index["signal_bindings"])
    assert all(row["truth_effect"] == "none" for row in evidence_index["signal_bindings"])
