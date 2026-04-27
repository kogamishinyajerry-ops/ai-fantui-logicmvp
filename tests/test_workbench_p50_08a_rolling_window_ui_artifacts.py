"""P50-08a — frontend artifact lockdowns for the rolling-window
metric.

Verifies the JS summary line reads `recent_window.pass_rate_recent`
and renders a `last N: %` segment when populated, so a divergence
between lifetime and recent is visible even with the panel
collapsed.
"""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
JS_PATH = REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js"


def test_js_reads_recent_window_field():
    js = JS_PATH.read_text(encoding="utf-8")
    assert "recent_window" in js


def test_js_summary_includes_recent_pass_rate():
    """When pass_rate_recent is populated, the collapsed summary
    line shows it alongside the lifetime pass rate."""
    js = JS_PATH.read_text(encoding="utf-8")
    summary_idx = js.find("workbench-metrics-summary-line")
    assert summary_idx >= 0
    block = js[summary_idx : summary_idx + 1500]
    # The window stats are read from recent_window
    assert "pass_rate_recent" in block
    # The label includes the window size
    assert "last ${" in block or "last " in block


def test_js_summary_skips_recent_when_null():
    """Under-windowed runs leave pass_rate_recent=null. The summary
    must NOT print 'last 20: null%' — there's a guard."""
    js = JS_PATH.read_text(encoding="utf-8")
    summary_idx = js.find("workbench-metrics-summary-line")
    block = js[summary_idx : summary_idx + 1500]
    # Looks for a null-check on pass_rate_recent
    assert (
        "pass_rate_recent != null" in block
        or "pass_rate_recent !== null" in block
        or "pass_rate_recent ==" in block  # any explicit comparison
    )
