"""P50-04 — frontend artifact lockdowns for the failure breakdown
panel.

Reads workbench HTML/JS/CSS as text and asserts the wiring shapes
are present so a future refactor can't silently disconnect the
classification fetch from the rendered breakdown.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html"
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"
CSS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css"


# ─── HTML — container present ───────────────────────────────────────


def test_html_has_breakdown_container():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert 'id="workbench-metrics-failure-breakdown"' in html
    assert 'id="workbench-metrics-failure-categories"' in html


def test_breakdown_hidden_by_default():
    """When total=0 the dashboard must NOT render an empty
    'failure breakdown' header — that's noise. The container
    starts with `hidden` and JS removes it when there's data."""
    html = HTML_PATH.read_text(encoding="utf-8")
    breakdown_start = html.find('id="workbench-metrics-failure-breakdown"')
    assert breakdown_start >= 0
    block = html[breakdown_start : breakdown_start + 200]
    assert "hidden" in block


# ─── JS — read failure_classification block ────────────────────────


def test_js_reads_failure_classification_field():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "failure_classification" in js


def test_js_iterates_by_category_array():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "by_category" in js


def test_js_renders_category_pill_with_data_attribute():
    """Each category needs a data-failure-category attribute so
    CSS can color-code planner_error vs git_error vs cancel."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "data-failure-category" in js


def test_js_hides_breakdown_when_no_failures():
    """Empty state: setAttribute('hidden', '') so the section
    disappears when fc.total === 0."""
    js = JS_PATH.read_text(encoding="utf-8")
    fn_start = js.find("workbench-metrics-failure-breakdown")
    assert fn_start >= 0
    block = js[fn_start : fn_start + 1500]
    assert 'setAttribute("hidden"' in block


def test_js_renders_sample_details_as_code():
    """Sample details are abort_reason snippets — render as <code>
    so they're visually distinct from the category label."""
    js = JS_PATH.read_text(encoding="utf-8")
    assert "<code>${escape(s)}</code>" in js


# ─── CSS — per-category color rules ────────────────────────────────


def test_css_has_pill_styling():
    css = CSS_PATH.read_text(encoding="utf-8")
    assert ".workbench-metrics-failure-cat-pill" in css


def test_css_distinguishes_user_cancel_from_system_failure():
    """user_cancel is orange (engineer changed mind, not a bug);
    planner_error is red (system pain). They MUST have different
    colors so the dashboard distinguishes them at a glance."""
    css = CSS_PATH.read_text(encoding="utf-8")
    # Find planner_error rule
    planner_idx = css.find(
        'workbench-metrics-failure-cat-pill[data-failure-category="planner_error"]'
    )
    assert planner_idx >= 0
    # Find user_cancel rule
    cancel_idx = css.find(
        'workbench-metrics-failure-cat-pill[data-failure-category="user_cancel"]'
    )
    assert cancel_idx >= 0
    # They must be DIFFERENT rule blocks (different selectors).
    # Window must be large enough to include the property block
    # that follows the selector list — system-failure pill uses
    # a long comma-separated selector list, so 1500 chars is safe.
    planner_block = css[planner_idx : planner_idx + 1500]
    cancel_block = css[cancel_idx : cancel_idx + 500]
    # Different colors. planner = red, cancel = orange.
    assert "rgba(255, 92, 92" in planner_block  # red family
    assert "rgba(255, 145, 60" in cancel_block  # orange family


def test_css_user_reject_distinguishable_from_user_cancel():
    """Reject (disapprove plan) vs Cancel (stop now) are different
    actions — keep the visual distinction the audit makes."""
    css = CSS_PATH.read_text(encoding="utf-8")
    reject_idx = css.find(
        'workbench-metrics-failure-cat-pill[data-failure-category="user_reject"]'
    )
    assert reject_idx >= 0
    block = css[reject_idx : reject_idx + 300]
    # Cyan family — matches the ASKING badge
    assert "rgba(0, 200, 245" in block


def test_css_all_8_failure_categories_have_color():
    """Every category emitted by the backend must have a CSS rule
    so the pill never falls back to unstyled."""
    css = CSS_PATH.read_text(encoding="utf-8")
    for category in [
        "planner_error", "test_runner_error", "test_gate",
        "apply_error", "git_error", "gh_error",
        "user_cancel", "user_reject", "unhandled", "other",
    ]:
        assert (
            f'data-failure-category="{category}"' in css
        ), f"missing color rule for category {category}"
