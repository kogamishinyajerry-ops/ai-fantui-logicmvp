from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKBENCH_JS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.js"
WORKBENCH_CSS = PROJECT_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_port_handle_wiring_helpers_are_sandbox_only() -> None:
    js = WORKBENCH_JS.read_text(encoding="utf-8")

    assert "let pendingPortHandleSource = null" in js
    assert "function portHandlePayload" in js
    assert "function renderEditablePortHandles" in js
    assert "function handlePortHandleClick" in js
    assert "data-port-handle-owner-id" in js
    assert "data-port-handle-direction" in js
    assert "ui_draft.port_handle_wiring" in js
    assert "port handle edge" in js
    assert "truth_effect: \"none\"" in js
    assert "controller_truth_modified: false" in js
    assert "api.linear.app" not in js


def test_port_handle_visuals_are_explicit() -> None:
    css = WORKBENCH_CSS.read_text(encoding="utf-8")

    assert ".workbench-port-handle" in css
    assert '.workbench-port-handle[data-port-handle-direction="in"]' in css
    assert '.workbench-port-handle[data-port-handle-direction="out"]' in css
    assert '.workbench-port-handle[data-port-handle-armed="true"]' in css
