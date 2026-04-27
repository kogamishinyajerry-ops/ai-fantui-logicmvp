"""P50-07 — frontend artifact lockdowns for SLO chip + breach panel.

Reads workbench HTML/JS/CSS as text and asserts the wiring shapes
are present so a future refactor can't silently disconnect the
SLO verdict from the dashboard surface.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── HTML — chip + breach container present ──────────────────────


def test_html_has_slo_chip_in_summary():
    """The SLO verdict chip lives in the panel <summary> so it's
    visible while the metrics panel is collapsed — the whole point
    is a glance-level health signal."""
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-slo-chip"' in html
    summary_idx = html.find('class="workbench-metrics-summary"')
    chip_idx = html.find('id="workbench-metrics-slo-chip"')
    summary_close = html.find("</summary>", summary_idx)
    assert summary_idx >= 0 and chip_idx >= 0 and summary_close >= 0
    # chip must be inside the <summary>, not in the body
    assert summary_idx < chip_idx < summary_close


def test_html_chip_default_severity_is_no_data():
    """Stale templates / pre-poll renders must show NO_DATA, never
    a false GREEN."""
    html = HTML_PATH.read_text(encoding="utf-8")
    chip_idx = html.find('id="workbench-metrics-slo-chip"')
    block = html[chip_idx : chip_idx + 300]
    assert 'data-slo-severity="no_data"' in block


def test_html_has_breach_list_container():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-slo-breaches"' in html
    assert 'id="workbench-metrics-slo-breach-list"' in html


def test_breach_list_hidden_by_default():
    """No breaches → no panel header. Container starts hidden,
    JS unhides only when breaches.length > 0."""
    html = HTML_PATH.read_text(encoding="utf-8")
    breaches_idx = html.find('id="workbench-metrics-slo-breaches"')
    assert breaches_idx >= 0
    block = html[breaches_idx : breaches_idx + 300]
    assert "hidden" in block


# ─── JS — reads slo_status, renders chip + list ──────────────────


def test_js_reads_slo_status_field():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "slo_status" in js


def test_js_sets_slo_severity_attribute():
    """The chip's color comes from data-slo-severity, set by JS
    from the backend's `overall` field."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "data-slo-severity" in js
    assert 'setAttribute("data-slo-severity"' in js


def test_js_handles_all_four_severities():
    """green / yellow / red / no_data must all be wired to a label
    so the chip never renders blank."""
    js = JS_PATH.read_text(encoding="utf-8")
    chip_block_start = js.find("workbench-metrics-slo-chip")
    assert chip_block_start >= 0
    block = js[chip_block_start : chip_block_start + 1500]
    for severity in ("green", "yellow", "red", "no_data"):
        assert severity in block, f"missing label for {severity}"


def test_js_iterates_breaches_array():
    js = JS_PATH.read_text(encoding="utf-8")
    breach_block = js.find("workbench-metrics-slo-breach-list")
    assert breach_block >= 0
    block = js[breach_block : breach_block + 1500]
    assert "breaches" in block
    # Each breach renders pill + name + note
    assert "b.severity" in block
    assert "b.slo" in block
    assert "b.note" in block


def test_js_hides_breach_list_when_empty():
    js = JS_PATH.read_text(encoding="utf-8")
    breach_block = js.find("workbench-metrics-slo-breaches")
    assert breach_block >= 0
    block = js[breach_block : breach_block + 1500]
    assert 'setAttribute("hidden"' in block


# ─── CSS — chip + breach pill use the canonical palette ──────────


def test_css_has_slo_chip_styling():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-slo-chip" in css


def test_css_chip_has_all_four_severity_colors():
    css = CSS_PATH.read_text(encoding="utf-8")
    for severity in ("green", "yellow", "red", "no_data"):
        assert (
            f'.workbench-metrics-slo-chip[data-slo-severity="{severity}"]' in css
        ), f"missing chip rule for {severity}"


def test_css_chip_green_is_green_family():
    """GREEN must be visually green, not red. Lock down the hue
    family so a refactor can't accidentally swap the palette."""
    css = CSS_PATH.read_text(encoding="utf-8")
    idx = css.find('.workbench-metrics-slo-chip[data-slo-severity="green"]')
    block = css[idx : idx + 300]
    # Green hex used throughout the dashboard for "healthy"
    assert "#6cd97a" in block or "rgba(108, 217, 122" in block


def test_css_chip_red_is_red_family():
    """RED must be visually red — same red family the dashboard
    uses for system failures (matching workbench-metrics-failure-
    cat-pill[data-failure-category=planner_error])."""
    css = CSS_PATH.read_text(encoding="utf-8")
    idx = css.find('.workbench-metrics-slo-chip[data-slo-severity="red"]')
    block = css[idx : idx + 300]
    assert "#ff6b6b" in block or "rgba(255, 92, 92" in block


def test_css_chip_yellow_matches_test_gate_yellow():
    """YELLOW chip and test_gate failure category should share
    the same yellow — same warning-class meaning, same color."""
    css = CSS_PATH.read_text(encoding="utf-8")
    chip_idx = css.find('.workbench-metrics-slo-chip[data-slo-severity="yellow"]')
    test_gate_idx = css.find(
        'workbench-metrics-failure-cat-pill[data-failure-category="test_gate"]'
    )
    assert chip_idx >= 0 and test_gate_idx >= 0
    chip_block = css[chip_idx : chip_idx + 300]
    test_gate_block = css[test_gate_idx : test_gate_idx + 300]
    # Both reference the same yellow hue
    assert "247, 188, 92" in chip_block
    assert "247, 188, 92" in test_gate_block


def test_css_breach_pill_has_severity_styling():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-slo-breach-pill" in css
    # Yellow + red rules at minimum (NO_DATA never appears as a
    # breach severity, GREEN means no breach at all)
    assert (
        '.workbench-metrics-slo-breach-pill[data-slo-severity="yellow"]' in css
    )
    assert (
        '.workbench-metrics-slo-breach-pill[data-slo-severity="red"]' in css
    )
