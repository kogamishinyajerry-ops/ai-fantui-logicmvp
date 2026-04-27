"""P49-02b — frontend artifact lockdowns for the governance
review panel.

Verifies the HTML container is hidden by default, JS polls the
right endpoint and binds approve/reject click handlers, and the
CSS uses a distinct amber palette so a gate-pending audit isn't
confused with the cyan ASKING cards.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── HTML ─────────────────────────────────────────────────────────


def test_html_has_governance_panel():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-governance-panel"' in html
    assert 'id="workbench-governance-list"' in html


def test_panel_hidden_by_default():
    """Empty queue (no GOVERNANCE_HOLD audits) → panel stays
    invisible. Otherwise a stale empty panel takes screen space
    above the metrics for no reason."""
    html = HTML_PATH.read_text(encoding="utf-8")
    idx = html.find('id="workbench-governance-panel"')
    block = html[idx : idx + 400]
    assert "hidden" in block


def test_panel_aria_live_polite():
    """The list updates every 5s; aria-live=polite ensures
    screen-readers announce gate-pending arrivals without
    stealing focus."""
    html = HTML_PATH.read_text(encoding="utf-8")
    idx = html.find('id="workbench-governance-panel"')
    block = html[idx : idx + 400]
    assert 'aria-live="polite"' in block


# ─── JS ───────────────────────────────────────────────────────────


def test_js_has_governance_list_endpoint_constant():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "/api/skill-executions?state=GOVERNANCE_HOLD" in js


def test_js_has_refresh_function():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "function refreshGovernancePanel" in js


def test_js_refresh_runs_on_metrics_tick():
    """Same 5s poll loop drives both metrics + governance — no
    separate timer needed, and the UI stays in sync."""
    js = JS_PATH.read_text(encoding="utf-8")
    idx = js.find("async function refreshExecutionMetrics")
    block = js[idx : idx + 400]
    assert "refreshGovernancePanel" in block


def test_js_renders_verdict_reasons():
    """Each match.rule_id + match.reason is surfaced so the
    reviewer can see exactly which criterion held the run up."""
    js = JS_PATH.read_text(encoding="utf-8")
    idx = js.find("function refreshGovernancePanel")
    block = js[idx : idx + 5000]
    assert "rule_id" in block
    assert "reason" in block


def test_js_buttons_have_data_attributes():
    """Approve/reject buttons carry their action + exec_id so the
    delegated click handler can route correctly."""
    js = JS_PATH.read_text(encoding="utf-8")
    idx = js.find("function refreshGovernancePanel")
    block = js[idx : idx + 5000]
    assert "data-governance-action" in block
    assert "data-governance-exec-id" in block


def test_js_click_handler_posts_to_endpoint():
    """Click → POST to /governance-approve or /governance-reject.
    Lock down the URL shape so a refactor can't silently route
    the click somewhere else."""
    js = JS_PATH.read_text(encoding="utf-8")
    idx = js.find("function _bindGovernanceClickHandlers")
    block = js[idx : idx + 3000]
    assert "/governance-approve" in block
    assert "/governance-reject" in block
    assert 'method: "POST"' in block


def test_js_click_handler_idempotent_binding():
    """The bind helper guards against double-attach so multiple
    poll ticks don't stack listeners."""
    js = JS_PATH.read_text(encoding="utf-8")
    idx = js.find("function _bindGovernanceClickHandlers")
    block = js[idx : idx + 3000]
    assert "__wbGovBound" in block


def test_js_hides_panel_when_no_audits():
    """Empty list response → setAttribute('hidden', '') so the
    panel disappears instead of rendering an empty frame."""
    js = JS_PATH.read_text(encoding="utf-8")
    idx = js.find("function refreshGovernancePanel")
    block = js[idx : idx + 5000]
    assert 'setAttribute("hidden"' in block


# ─── CSS — distinct from ASKING palette ──────────────────────────


def test_css_has_panel_styling():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-governance-panel" in css
    assert ".workbench-governance-card" in css
    assert ".workbench-governance-rule-pill" in css


def test_css_uses_amber_family():
    """Amber/gold (rgba 247, 188, 92) so the gate pops visually
    and isn't mistaken for the cyan ASKING palette. Cancel buttons
    elsewhere use red — these reasons are warning-class."""
    css = CSS_PATH.read_text(encoding="utf-8")
    idx = css.find(".workbench-governance-panel")
    block = css[idx : idx + 600]
    assert "247, 188, 92" in block


def test_css_approve_button_green():
    """Approve action has the green palette to match the
    GREEN/healthy intent. The btn uses a combined selector for
    shared base styles plus a per-button selector for color, so
    we scan the whole approve-btn declaration block (~1500 char
    window covers both the combined and standalone rule)."""
    css = CSS_PATH.read_text(encoding="utf-8")
    idx = css.find(".workbench-governance-approve-btn")
    block = css[idx : idx + 1500]
    assert "108, 217, 122" in block


def test_css_reject_button_red():
    css = CSS_PATH.read_text(encoding="utf-8")
    idx = css.find(".workbench-governance-reject-btn")
    block = css[idx : idx + 1500]
    assert "255, 92, 92" in block
