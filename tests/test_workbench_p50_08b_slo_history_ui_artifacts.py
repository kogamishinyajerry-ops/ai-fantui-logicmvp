"""P50-08b — frontend artifact lockdowns for the SLO transition
timeline panel.

Asserts the wiring shapes (HTML container, JS fetch + reverse-
order render, CSS pip palette) so a refactor can't silently
disconnect the timeline from the dashboard surface.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── HTML ─────────────────────────────────────────────────────────


def test_html_has_timeline_container():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-slo-timeline"' in html
    assert 'id="workbench-metrics-slo-timeline-list"' in html


def test_timeline_hidden_by_default():
    """Empty timeline (fresh deploy) → container starts hidden so
    no orphan eyebrow renders before any transition has fired."""
    html = HTML_PATH.read_text(encoding="utf-8")
    idx = html.find('id="workbench-metrics-slo-timeline"')
    assert idx >= 0
    block = html[idx : idx + 250]
    assert "hidden" in block


# ─── JS ───────────────────────────────────────────────────────────


def test_js_has_history_endpoint_constant():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "/api/skill-executions/slo-history" in js


def test_js_fetches_history_on_metrics_refresh():
    """The 5s metrics poll also fetches the timeline so the panel
    stays in sync without a separate timer."""
    js = JS_PATH.read_text(encoding="utf-8")
    fn_idx = js.find("async function refreshExecutionMetrics")
    assert fn_idx >= 0
    block = js[fn_idx : fn_idx + 2500]
    assert "SLO_HISTORY_PATH" in block or "slo-history" in block
    assert "renderSloTimeline" in block


def test_js_reverses_for_newest_first_display():
    """API response is newest-last (file-order); UI must reverse
    so the freshest transition is at the top of the list."""
    js = JS_PATH.read_text(encoding="utf-8")
    render_idx = js.find("function renderSloTimeline")
    assert render_idx >= 0
    block = js[render_idx : render_idx + 3000]
    assert ".reverse()" in block


def test_js_renders_from_to_severity_pips():
    js = JS_PATH.read_text(encoding="utf-8")
    render_idx = js.find("function renderSloTimeline")
    block = js[render_idx : render_idx + 3000]
    assert "from_severity" in block
    assert "to_severity" in block
    assert "data-slo-severity" in block


def test_js_renders_breach_summary_in_row():
    js = JS_PATH.read_text(encoding="utf-8")
    render_idx = js.find("function renderSloTimeline")
    block = js[render_idx : render_idx + 3000]
    assert "breach_slos" in block


def test_js_hides_timeline_when_no_transitions():
    js = JS_PATH.read_text(encoding="utf-8")
    render_idx = js.find("function renderSloTimeline")
    block = js[render_idx : render_idx + 3000]
    assert 'setAttribute("hidden"' in block


# ─── CSS — pip palette consistent with chip ──────────────────────


def test_css_has_timeline_styling():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-slo-timeline" in css
    assert ".workbench-metrics-slo-timeline-list" in css
    assert ".workbench-metrics-slo-timeline-item" in css


def test_css_pip_has_all_severity_colors():
    """Pips must cover every severity that can appear in
    from_severity or to_severity: green, yellow, red, no_data,
    plus the synthetic 'none' baseline used on first transition."""
    css = CSS_PATH.read_text(encoding="utf-8")
    for severity in ("green", "yellow", "red", "no_data", "none"):
        assert (
            f'.workbench-metrics-slo-pip[data-slo-severity="{severity}"]' in css
        ), f"missing pip rule for {severity}"


def test_css_pip_palette_matches_chip():
    """Pips and the summary chip must share their hex/rgba values
    so a 'green' pip and a 'green' chip look the same."""
    css = CSS_PATH.read_text(encoding="utf-8")
    # Green
    chip_idx = css.find('.workbench-metrics-slo-chip[data-slo-severity="green"]')
    pip_idx = css.find('.workbench-metrics-slo-pip[data-slo-severity="green"]')
    chip_block = css[chip_idx : chip_idx + 300]
    pip_block = css[pip_idx : pip_idx + 300]
    assert "108, 217, 122" in chip_block and "108, 217, 122" in pip_block
    # Red
    chip_idx_r = css.find('.workbench-metrics-slo-chip[data-slo-severity="red"]')
    pip_idx_r = css.find('.workbench-metrics-slo-pip[data-slo-severity="red"]')
    chip_block_r = css[chip_idx_r : chip_idx_r + 300]
    pip_block_r = css[pip_idx_r : pip_idx_r + 300]
    assert "255, 92, 92" in chip_block_r and "255, 92, 92" in pip_block_r
