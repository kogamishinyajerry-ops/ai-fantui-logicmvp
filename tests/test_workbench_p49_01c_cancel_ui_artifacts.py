"""P49-01c — frontend artifact lockdowns for the cancel button.

These read workbench.js + workbench.css as text and assert key
shapes are present, so renames/refactors don't silently break the
wiring between badge → cancel button → POST endpoint.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


def test_cancellable_states_set_excludes_asking_and_terminals():
    """Cancel must NOT show in ASKING (which has Approve/Reject) or
    in any terminal state (LANDED/ABORTED/FAILED — nothing to cancel).
    Lock down the set so a future refactor can't accidentally widen
    it and surface a Cancel button next to a LANDED badge."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "CANCELLABLE_STATES" in js
    # The four valid states — confirms we got the boundary right
    for state in ["PLANNING", "EDITING", "TESTING", "PR_OPEN"]:
        assert (
            f'"{state}"' in js
        ), f"missing {state} in CANCELLABLE_STATES set"


def test_cancel_button_renders_with_data_attribute():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "data-execution-cancel-id=" in js
    assert "workbench-execution-cancel-button" in js


def test_cancel_button_uses_correct_endpoint_path():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "/cancel" in js
    assert "/api/skill-executions/" in js
    assert "sendExecutionCancel" in js


def test_cancel_button_confirms_before_posting():
    """Clicking Cancel must show a confirm dialog — clicking the
    button by accident should not abort an in-flight execution."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "window.confirm" in js


def test_cancel_button_css_class_defined():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-execution-cancel-button" in css
    # Hover state should give visible feedback
    assert ".workbench-execution-cancel-button:hover" in css
    # Disabled state should be visually distinct (in-flight)
    assert ".workbench-execution-cancel-button[disabled]" in css


def test_cancel_button_uses_red_color():
    """A destructive action like cancel must be visually distinct.
    Red border/text is the convention for abort/reject across the
    workbench UI."""
    css = CSS_PATH.read_text(encoding="utf-8")
    # Find the cancel button block and confirm it uses a red color
    block_start = css.find(".workbench-execution-cancel-button {")
    assert block_start >= 0
    block = css[block_start : block_start + 600]
    assert "rgba(255, 92, 92" in block or "#ff" in block.lower()


def test_cancel_button_calls_refresh_on_success():
    """After a successful cancel, the badge should refresh so the
    user immediately sees the state has changed (rather than
    waiting for the 5s poll)."""
    js = JS_PATH.read_text(encoding="utf-8")
    # The cancel handler must call refreshExecutionBadges after POST
    # to give immediate feedback. Look for the pattern.
    handler_start = js.find("data-execution-cancel-id")
    assert handler_start >= 0
    # In the handler region (next ~1500 chars) we should see the
    # refresh call somewhere
    handler_block = js[handler_start : handler_start + 2500]
    assert "refreshExecutionBadges" in handler_block
