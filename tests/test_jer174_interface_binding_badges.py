from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_interface_binding_badge_dom_and_styles_are_present() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert 'id="workbench-interface-binding-quality"' in html
    assert 'id="workbench-interface-binding-coverage"' in html
    assert 'data-binding-quality="missing"' in html
    assert ".workbench-editable-node::after" in css
    assert '[data-binding-quality="partial"]' in css
    assert '[data-binding-quality="complete"]' in css
    assert ".workbench-binding-quality" in css


def test_interface_binding_quality_functions_are_truth_neutral() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "function interfaceBindingQualityReport" in js
    assert "function buildInterfaceBindingCoverageSummary" in js
    assert "data-binding-quality" in js
    assert "binding_coverage: bindingCoverage" in js
    assert "binding_coverage_checksum" in js
    assert 'truth_effect: "none"' in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js
