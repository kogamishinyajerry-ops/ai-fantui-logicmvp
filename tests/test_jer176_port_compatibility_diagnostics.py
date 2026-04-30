from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_port_compatibility_report_is_exported_as_sandbox_evidence() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function buildPortCompatibilityReport" in js
    assert "function portCompatibilityForEdge" in js
    assert "well-harness-workbench-port-compatibility-report" in js
    assert "port_compatibility_report: portCompatibilityReport" in js
    assert "port_compatibility_report_checksum" in js
    assert 'truth_effect: "none"' in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js


def test_edge_inspector_displays_port_compatibility_metadata() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "source_port_value_type" in js
    assert "target_port_value_type" in js
    assert "port_compatibility_status" in js
    assert "Port compatibility" in js
    assert "value_type_mismatch" in js
    assert "missing_source_port" in js
    assert "missing_target_port" in js
