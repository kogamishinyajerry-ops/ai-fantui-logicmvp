from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_edge_paths_expose_port_compatibility_status() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "data-port-compatibility" in js
    assert "payload.port_compatibility_status" in js
    assert "port_compatibility_status" in js
    assert 'truth_effect: "none"' in js
    assert "api.linear.app" not in js


def test_port_compatibility_badge_styles_are_visible_and_stable() -> None:
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert '[data-port-compatibility="warn"]' in css
    assert '[data-port-compatibility="fail"]' in css
    assert "stroke-dasharray: 3 3" in css
    assert "stroke-dasharray: 2 2" in css
    assert ".workbench-editable-edges path[aria-pressed=\"true\"][data-port-compatibility=\"warn\"]" in css
    assert ".workbench-editable-edges path[aria-pressed=\"true\"][data-port-compatibility=\"fail\"]" in css
