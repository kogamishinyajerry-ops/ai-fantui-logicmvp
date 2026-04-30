from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_HTML = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.html"
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_canvas_viewport_controls_and_helpers_are_sandbox_only() -> None:
    html = WORKBENCH_HTML.read_text(encoding="utf-8")
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert 'id="workbench-viewport-tools"' in html
    assert 'data-viewport-tool="zoom-in"' in html
    assert 'data-viewport-tool="zoom-out"' in html
    assert 'data-viewport-tool="reset"' in html
    assert 'data-viewport-tool="fit-selection"' in html
    assert "const viewportState = {" in js
    assert "function viewportStateSnapshot" in js
    assert "function applyViewportTransform" in js
    assert "function defaultViewportState" in js
    assert "function zoomViewportAt" in js
    assert "function fitViewportToSelection" in js
    assert "function beginViewportPan" in js
    assert 'applyViewportTransform("pan", { persist: false })' in js
    assert "function releaseSpacePanMode" in js
    assert 'window.addEventListener("blur"' in js
    assert "coordinate_effect: \"viewport_only\"" in js
    assert "viewport_state" in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js


def test_canvas_viewport_css_uses_transform_layer() -> None:
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert ".workbench-viewport-tools" in css
    assert "--viewport-scale" in css
    assert "--viewport-pan-x" in css
    assert "--viewport-pan-y" in css
    assert '.workbench-editable-canvas[data-viewport-panning="true"]' in css
