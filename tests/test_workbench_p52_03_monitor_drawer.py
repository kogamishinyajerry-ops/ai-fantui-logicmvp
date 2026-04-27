"""P52-03 — DOM reshape: metrics + live-log into the monitor drawer.

Encodes the contract:
- a single `<section id="workbench-tool-monitor">` is the monitor
  drawer, marked with `data-dock-section="monitor"`
- it CONTAINS both the metrics panel and the live-log panel (so dock
  activation reveals them together as one drawer)
- the inbox aside no longer hosts the metrics panel (the inbox is
  the annotate-tool surface, monitor is its own surface)
- all original element IDs survive the move (JS wiring + CSS rules
  keep working without per-call updates)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")


def _section(html: str, section_id: str) -> str:
    """Return the substring from `<section id="X"` up to the matching
    `</section>` (best-effort — uses non-greedy match, fine for this
    static template)."""
    pattern = re.compile(
        r'<section[^>]*id="' + re.escape(section_id) + r'"[^>]*>(.*?)</section>',
        re.DOTALL,
    )
    m = pattern.search(html)
    assert m is not None, f"section #{section_id} not found"
    return m.group(0)


# ─── 1. monitor drawer wrapper exists ────────────────────────────


def test_monitor_drawer_section_exists():
    """The monitor drawer is a real section with the expected
    dock-section attribute and the drawer-section class."""
    block = _section(HTML, "workbench-tool-monitor")
    assert 'data-dock-section="monitor"' in block, (
        "workbench-tool-monitor must be tagged data-dock-section=monitor"
    )
    assert "workbench-tool-drawer-section" in block, (
        "monitor drawer must carry workbench-tool-drawer-section class"
    )


def test_monitor_drawer_has_drawer_header():
    """Drawer must lead with the standard eyebrow + h2 + close-button
    header so the visual rhythm matches the other drawers."""
    block = _section(HTML, "workbench-tool-monitor")
    assert "workbench-tool-drawer-header" in block
    assert 'data-dock-close' in block, (
        "monitor drawer header must include the close button"
    )


# ─── 2. metrics panel moved INTO the monitor drawer ──────────────


def test_metrics_panel_is_inside_monitor_drawer():
    block = _section(HTML, "workbench-tool-monitor")
    assert 'id="workbench-metrics-panel"' in block, (
        "metrics panel must live inside the monitor drawer (P52-03)"
    )


def test_metrics_panel_no_longer_inside_inbox():
    """The annotation inbox aside should no longer host the metrics
    panel — the inbox is the annotate-tool surface only now."""
    aside_match = re.search(
        r'<aside[^>]*workbench-annotation-inbox[^>]*>(.*?)</aside>',
        HTML,
        re.DOTALL,
    )
    if aside_match is None:
        # Fallback: hunt for any aside that contains the inbox list.
        aside_match = re.search(
            r'<aside[^>]*>(?:(?!</aside>).)*?id="annotation-inbox-list"(?:(?!</aside>).)*?</aside>',
            HTML,
            re.DOTALL,
        )
    assert aside_match is not None, "annotation inbox aside not found"
    aside_block = aside_match.group(0)
    assert 'id="workbench-metrics-panel"' not in aside_block, (
        "P52-03 moved metrics out of the inbox aside; reverting "
        "would force annotate users to see ops metrics they don't "
        "need."
    )


@pytest.mark.parametrize(
    "metric_id",
    [
        "workbench-metric-total",
        "workbench-metric-pass-rate",
        "workbench-metric-median-duration",
        "workbench-metric-p95-duration",
        "workbench-metrics-slo-chip",
        "workbench-metrics-state-bars",
        "workbench-metrics-failures",
    ],
)
def test_metric_ids_preserved_in_monitor_drawer(metric_id):
    """Every metric ID JS hooks onto must still exist inside the
    monitor drawer — the JS code never had to learn it moved."""
    block = _section(HTML, "workbench-tool-monitor")
    assert f'id="{metric_id}"' in block, (
        f"metric ID {metric_id} must be preserved inside the new "
        f"monitor drawer; refresh code in workbench.js binds to it"
    )


# ─── 3. live log panel inside the monitor drawer ─────────────────


def test_live_log_panel_inside_monitor_drawer():
    block = _section(HTML, "workbench-tool-monitor")
    assert 'id="workbench-live-log-panel"' in block, (
        "live log panel must live inside the monitor drawer"
    )


def test_live_log_stream_id_preserved():
    """SSE handler binds to #workbench-live-log-stream."""
    block = _section(HTML, "workbench-tool-monitor")
    assert 'id="workbench-live-log-stream"' in block
    assert 'id="workbench-live-log-status"' in block


def test_live_log_panel_is_not_a_dock_section_anymore():
    """Two siblings sharing data-dock-section="monitor" would
    position-fixed-stack on top of each other. After P52-03 the live
    log panel is wrapped inside the monitor drawer and MUST NOT
    carry its own data-dock-section."""
    # Find the live-log panel element start tag specifically (not the
    # surrounding monitor wrapper).
    log_open = re.search(
        r'<[a-zA-Z]+[^>]*id="workbench-live-log-panel"[^>]*>',
        HTML,
    )
    assert log_open is not None
    tag = log_open.group(0)
    assert 'data-dock-section' not in tag, (
        "live-log panel must no longer be a dock-section host; "
        "the wrapping #workbench-tool-monitor handles dock toggling"
    )


# ─── 4. ordering: metrics renders ABOVE live-log inside the drawer ──


def test_metrics_appears_before_live_log_in_drawer():
    """Visual rhythm: metrics summary up top (operator's first
    glance), log stream below it (the long scroll). Reverse order
    would push the metrics off-screen on short viewports."""
    block = _section(HTML, "workbench-tool-monitor")
    metrics_pos = block.find('id="workbench-metrics-panel"')
    log_pos = block.find('id="workbench-live-log-panel"')
    assert metrics_pos != -1 and log_pos != -1
    assert metrics_pos < log_pos, (
        "metrics panel must render before live-log inside the "
        "monitor drawer"
    )
