"""P50-10 — frontend artifact lockdowns for the forensics
download link.

Asserts the link is in the panel summary (so it's reachable
without expanding), points at the right endpoint, has a
download attribute (browsers handle the file save), and the JS
stops the click from toggling the <details> panel open/closed.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── HTML ─────────────────────────────────────────────────────────


def test_html_has_forensics_link():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-forensics-link"' in html


def test_link_points_at_bundle_endpoint():
    html = HTML_PATH.read_text(encoding="utf-8")
    idx = html.find('id="workbench-metrics-forensics-link"')
    block = html[idx : idx + 500]
    assert 'href="/api/skill-executions/forensics-bundle"' in block


def test_link_has_download_attribute():
    """`download` attribute tells the browser to save the response
    rather than navigating to it. Without this the browser might
    try to render the zip body as text."""
    html = HTML_PATH.read_text(encoding="utf-8")
    idx = html.find('id="workbench-metrics-forensics-link"')
    block = html[idx : idx + 500]
    assert "download" in block


def test_link_lives_in_panel_summary():
    """The link is in <summary> so a collapsed panel still surfaces
    it. Operators alerted via webhook want the snapshot first,
    panel expansion second."""
    html = HTML_PATH.read_text(encoding="utf-8")
    summary_idx = html.find('class="workbench-metrics-summary"')
    link_idx = html.find('id="workbench-metrics-forensics-link"')
    summary_close = html.find("</summary>", summary_idx)
    assert summary_idx >= 0 and link_idx >= 0 and summary_close >= 0
    assert summary_idx < link_idx < summary_close


# ─── JS ───────────────────────────────────────────────────────────


def test_js_stops_click_propagation():
    """Without stopPropagation the link click toggles the
    <details> panel since the link lives inside <summary>. Lock
    down the behavior so a refactor can't reintroduce the bug."""
    js = JS_PATH.read_text(encoding="utf-8")
    fn_idx = js.find("_bindForensicsLink")
    assert fn_idx >= 0
    block = js[fn_idx : fn_idx + 1500]
    assert "stopPropagation" in block


def test_js_binds_on_metrics_refresh():
    """The bind helper is invoked from the metrics refresh path
    so it survives the page lifecycle (poll loop ensures binding
    even if the link gets re-rendered later)."""
    js = JS_PATH.read_text(encoding="utf-8")
    fn_idx = js.find("async function refreshExecutionMetrics")
    block = js[fn_idx : fn_idx + 500]
    assert "_bindForensicsLink" in block


def test_js_idempotent_binding():
    """Bind handler must not double-attach the listener if the
    metrics refresh fires multiple times. Lock down the guard."""
    js = JS_PATH.read_text(encoding="utf-8")
    fn_idx = js.find("_bindForensicsLink")
    block = js[fn_idx : fn_idx + 1500]
    # A flag-based guard or any equivalent presence check
    assert "__wbBound" in block or "removeEventListener" in block


# ─── CSS ──────────────────────────────────────────────────────────


def test_css_has_forensics_link_styling():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-forensics-link" in css


def test_css_link_has_hover_state():
    """A subtle hover state confirms the link is interactive."""
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-forensics-link:hover" in css


def test_css_link_quiet_resting_state():
    """Resting state should be muted so the link doesn't compete
    with the SLO chip for attention. The fade is enforced by
    using rgba with low alpha (<0.7) on the color."""
    css = CSS_PATH.read_text(encoding="utf-8")
    idx = css.find(".workbench-metrics-forensics-link {")
    block = css[idx : idx + 800]
    # The resting color pulls from rgba(... 0.55) which is below
    # 0.7 — visibly faded vs. the chip text
    assert "0.55" in block or "0.5" in block
