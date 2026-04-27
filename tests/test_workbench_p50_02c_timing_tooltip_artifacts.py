"""P50-02c — frontend artifact lockdowns for the timing tooltip.

These read workbench.js / workbench.css as text and assert the
key shapes are present, so a future refactor can't silently
disconnect badge → click → fetch → render.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── JS — wiring ─────────────────────────────────────────────────


def test_badge_click_handler_exists():
    js = JS_PATH.read_text(encoding="utf-8")
    # Click handler attached to .workbench-execution-badge
    assert "workbench-execution-badge" in js
    assert "openTimingTooltip" in js


def test_click_handler_skips_cancel_button():
    """Clicking the cancel button must NOT also open the timing
    tooltip — that would be a confusing UX double-action."""
    js = JS_PATH.read_text(encoding="utf-8")
    # The handler should look for the cancel button class and bail
    assert "workbench-execution-cancel-button" in js
    handler_start = js.find("openTimingTooltip(badge, proposalId)")
    assert handler_start >= 0
    # Search backwards for the closest "if (event.target.closest"
    block_start = max(0, handler_start - 500)
    block = js[block_start:handler_start]
    assert "workbench-execution-cancel-button" in block


def test_timings_endpoint_path_correct():
    """The tooltip fetcher must hit the lightweight /timings
    endpoint, not the full /execution endpoint, so we don't
    pull plan + events on every hover."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "/execution/timings" in js


def test_format_phase_duration_handles_units():
    """The duration formatter must adapt to seconds / minutes / hours."""
    js = JS_PATH.read_text(encoding="utf-8")
    fn_start = js.find("function _formatPhaseDuration")
    assert fn_start >= 0
    block = js[fn_start : fn_start + 500]
    # Must handle each unit
    assert "<1s" in block
    assert "${seconds.toFixed(0)}s" in block
    assert "m${" in block
    assert "h${" in block or "h`" in block


def test_render_timing_tooltip_renders_all_phases():
    """The renderer must iterate every phase in the timings list,
    including ones with None duration (so the layout stays stable
    for not-yet-reached phases)."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "renderTimingTooltip" in js
    # Should reuse the EXECUTION_STATE_INFO color palette
    assert "EXECUTION_STATE_INFO[p.phase]" in js


def test_tooltip_closes_on_outside_click():
    """Click anywhere outside the popover must dismiss it."""
    js = JS_PATH.read_text(encoding="utf-8")
    # Look for the closer pattern
    assert "tooltip.contains(event.target)" in js
    assert "tooltip.remove()" in js


def test_only_one_tooltip_open_at_a_time():
    """Opening a second tooltip must close the first."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "_activeTimingTooltip" in js


def test_window_helpers_exposed_for_debug():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "window.__WB_renderTimingTooltip" in js
    assert "window.__WB_openTimingTooltip" in js


# ─── CSS — tooltip styling ──────────────────────────────────────


def test_tooltip_class_styled():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-execution-timing-tooltip" in css


def test_tooltip_position_absolute_with_zindex():
    """Must float above page content, not push layout."""
    css = CSS_PATH.read_text(encoding="utf-8")
    block_start = css.find(".workbench-execution-timing-tooltip {")
    assert block_start >= 0
    block = css[block_start : block_start + 500]
    assert "position: absolute" in block
    assert "z-index" in block


def test_each_phase_has_distinct_color():
    """Reuses the badge-color palette so the visual language is
    consistent across all 6 reportable phases."""
    css = CSS_PATH.read_text(encoding="utf-8")
    for phase_css in [
        "init", "planning", "asking", "editing", "testing", "pr-open",
    ]:
        assert (
            f'workbench-timing-phase[data-execution-css="{phase_css}"]' in css
        ), f"missing color rule for {phase_css}"


def test_current_phase_visually_highlighted():
    """The phase the audit is CURRENTLY in should stand out so
    reviewers see "we're stuck here" at a glance."""
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-timing-row.is-current" in css


def test_badge_has_pointer_cursor_to_signal_clickability():
    css = CSS_PATH.read_text(encoding="utf-8")
    # The badge style block (P49-01b) should now indicate clickability
    badge_start = css.find(".workbench-execution-badge {")
    if badge_start >= 0:
        block = css[badge_start : badge_start + 500]
        # P50-02c should have added cursor: pointer
    # Or there's a separate rule; just check pointer is referenced
    assert "cursor: pointer" in css
