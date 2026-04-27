"""P50-02a — frontend artifact lockdowns for the metrics panel.

Reads the workbench HTML/JS/CSS as text and asserts key shapes
are present, so renames/refactors don't silently disconnect the
metrics fetch from the dashboard render.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── HTML — panel structure ──────────────────────────────────────────


def test_html_has_metrics_panel_container():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-panel"' in html
    assert 'class="workbench-metrics-panel"' in html


def test_html_has_summary_line_for_collapsed_view():
    """When the panel is collapsed, the summary line must still
    be visible so the reviewer sees the headline numbers."""
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-summary-line"' in html


def test_html_has_four_metric_card_targets():
    """The four header cards must have stable IDs the JS can fill."""
    html = HTML_PATH.read_text(encoding="utf-8")
    for stub in [
        "workbench-metric-total",
        "workbench-metric-pass-rate",
        "workbench-metric-median-duration",
        "workbench-metric-p95-duration",
    ]:
        assert f'id="{stub}"' in html, f"missing metric card target {stub}"


def test_html_has_state_bars_container():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-state-bars"' in html


def test_html_has_failures_container():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-failures"' in html


# ─── JS — fetch + render ─────────────────────────────────────────────


def test_js_fetches_metrics_endpoint():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "/api/skill-executions/metrics" in js
    assert "refreshExecutionMetrics" in js


def test_js_renders_all_9_states_in_bar_chart():
    js = JS_PATH.read_text(encoding="utf-8")
    # The state order array should list every state, in canonical order
    for state in [
        "INIT", "PLANNING", "ASKING", "EDITING", "TESTING",
        "PR_OPEN", "LANDED", "ABORTED", "FAILED",
    ]:
        assert f'"{state}"' in js, f"state {state} not referenced in JS"


def test_js_format_helpers_handle_null():
    """_formatDuration(null) and _formatPassRate(null) must not
    throw — the dashboard renders even with a fresh empty backend."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "_formatDuration" in js
    assert "_formatPassRate" in js
    # Both should have a null-guard
    assert "== null" in js


def test_js_metrics_refresh_wired_to_poll_loop():
    """The 5s poll loop must call refreshExecutionMetrics so the
    panel stays current without a separate timer."""
    js = JS_PATH.read_text(encoding="utf-8")
    # Find startPendingExecPoll body and confirm it includes the
    # metrics refresher
    poll_start = js.find("function startPendingExecPoll")
    assert poll_start >= 0
    block = js[poll_start : poll_start + 1000]
    assert "refreshExecutionMetrics" in block


def test_js_exposes_render_helper_on_window():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "window.__WB_renderExecutionMetrics" in js
    assert "window.__WB_refreshExecutionMetrics" in js


# ─── CSS — styles for the panel ─────────────────────────────────────


def test_css_metrics_panel_styled():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-panel" in css
    assert ".workbench-metrics-summary" in css
    assert ".workbench-metrics-grid" in css


def test_css_state_bars_have_per_state_colors():
    """Each of the 9 states needs a fill color for its bar so
    the chart is glanceable."""
    css = CSS_PATH.read_text(encoding="utf-8")
    for css_class in [
        "init", "planning", "asking", "editing", "testing",
        "pr-open", "landed", "aborted", "failed",
    ]:
        # Bar fill rule should mention this css class
        assert (
            f'workbench-metrics-state-bar-fill[data-execution-css="{css_class}"]'
            in css
        ), f"missing bar-fill rule for {css_class}"


def test_css_failures_list_styled():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-failures-list" in css
    assert ".workbench-metrics-failures-state" in css
