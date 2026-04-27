"""P54-02 — multi-view canvas + dock view-group.

User feedback: the main canvas only shows one view (反推控制电路图).
The thrust-reverser product has FOUR companion surfaces that are
"a set" and must be switchable from the canvas:
  1. 反推控制电路图 (control circuit) — the existing default
  2. 反推仿真模拟面板 (simulation panel)
  3. 反推控制演示舱 (demo cockpit)
  4. 反推需求文档 (requirements doc)

The left dock now carries TWO groups separated by a hairline divider:
  - VIEWS group (top): 4 buttons that switch the canvas
  - TOOLS group (bottom): the original 4 drawer triggers (新建/批注/
    审批/监控)

Canvas state is driven by `body[data-active-view]`; tool drawer
state by `body[data-active-tool]` (orthogonal — opening a drawer
doesn't change which canvas is showing underneath).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")
JS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js").read_text(encoding="utf-8")


# ─── 1. dock has a view-group with 4 buttons ─────────────────


@pytest.mark.parametrize(
    "view_id",
    ["circuit", "sim", "cockpit", "spec"],
)
def test_dock_view_button_present(view_id):
    """Each canvas view has its own dock trigger button keyed via
    data-view-target=<id>."""
    pattern = re.compile(
        r'<button[^>]*data-view-target="' + re.escape(view_id) + r'"[^>]*>',
    )
    assert pattern.search(HTML), (
        f"missing dock view-button for {view_id}"
    )


def test_dock_has_hairline_divider_between_groups():
    """The dock physically separates the views group from the tools
    group with a small hairline element (or a CSS-styled :empty
    `<hr>` element). Encoded via class name so CSS can style it."""
    assert (
        "workbench-dock-divider" in HTML
        or 'class="workbench-dock-group"' in HTML
    ), (
        "dock must structurally separate views vs tools — either "
        "a `.workbench-dock-divider` element or two `.workbench-"
        "dock-group` containers"
    )


# ─── 2. four canvas mounts, only the matching one paints ─────


@pytest.mark.parametrize(
    "view_id,expected_id",
    [
        ("circuit", "workbench-circuit-hero"),
        ("sim", "workbench-sim-panel"),
        ("cockpit", "workbench-cockpit-panel"),
        ("spec", "workbench-spec-panel"),
    ],
)
def test_canvas_view_mount_exists(view_id, expected_id):
    """Each view has a canvas mount with id matching the convention."""
    assert f'id="{expected_id}"' in HTML, (
        f"missing canvas mount for view={view_id} (expected "
        f"#{expected_id})"
    )


@pytest.mark.parametrize(
    "view_id",
    ["circuit", "sim", "cockpit", "spec"],
)
def test_canvas_view_mount_carries_dataset(view_id):
    """Each canvas mount must carry data-canvas-view=<id> so CSS
    can drive visibility off body[data-active-view]."""
    pattern = re.compile(
        r'data-canvas-view="' + re.escape(view_id) + r'"',
    )
    assert pattern.search(HTML), (
        f"missing data-canvas-view={view_id}"
    )


def test_view_visibility_rule_per_pair():
    """CSS must hide all canvas-views by default, then show only
    the one matching body[data-active-view]."""
    # Default-hide
    default_hide = re.search(
        r'\[data-canvas-view\]\s*\{[^}]*display:\s*none',
        CSS,
        re.DOTALL,
    )
    assert default_hide is not None, (
        "expected `[data-canvas-view] { display: none }` default-"
        "hide rule"
    )
    # Per-view show
    for v in ("circuit", "sim", "cockpit", "spec"):
        pattern = re.compile(
            r'body\[data-active-view="' + re.escape(v) + r'"\]\s+\[data-canvas-view="' + re.escape(v) + r'"\]',
        )
        assert pattern.search(CSS), (
            f"missing show-rule for view={v}"
        )


# ─── 3. JS wires view switching ──────────────────────────────


def test_js_view_switching_handler_present():
    """workbench.js must include a boot block that wires the dock
    view-buttons to set body[data-active-view]."""
    has_handler = (
        "data-view-target" in JS
        and "data-active-view" in JS
    )
    assert has_handler, (
        "workbench.js must wire data-view-target buttons → set "
        "body[data-active-view] dataset"
    )


# ─── 4. view stubs are real, not "Coming soon" ───────────────


@pytest.mark.parametrize(
    "panel_id,iframe_src",
    [
        # P54-04 (2026-04-28): mapping corrected. The original P54-03
        # had 仿真→timeline-sim and 演示→fan_console, both wrong:
        # - 仿真 is the operator console with adjustable parameters,
        #   which is fan_console.html
        # - 演示 is the cockpit with lever + condition panels, which
        #   is demo.html
        ("workbench-sim-panel", "/fan_console.html"),
        ("workbench-cockpit-panel", "/demo.html"),
        # P54-05: spec view repointed to /workbench_spec.html — a
        # workbench-native rebuild with summary KPIs, REQ cards, and
        # a traceability matrix. The legacy /fantui_requirements.html
        # remains for the standalone /fantui_requirements.html route.
        ("workbench-spec-panel", "/workbench_spec.html"),
    ],
)
def test_canvas_view_embeds_existing_mature_page(panel_id, iframe_src):
    """The sim / cockpit / requirements views embed the EXISTING
    mature pages via <iframe>, not re-implemented stubs. The iframe
    src may carry a `?embed=1` querystring (P54-04 added it as a
    defense-in-depth signal so the embedded page can suppress its
    unified-nav)."""
    block = re.search(
        r'<section[^>]*id="' + re.escape(panel_id) + r'"[^>]*>(.*?)</section>',
        HTML,
        re.DOTALL,
    )
    assert block is not None, f"#{panel_id} section missing"
    body = block.group(0)
    iframe_match = re.search(
        r'<iframe[^>]*src="' + re.escape(iframe_src) + r'(?:\?[^"]*)?"[^>]*>',
        body,
    )
    assert iframe_match is not None, (
        f"#{panel_id} must embed `{iframe_src}` via <iframe> "
        f"(not a fresh stub); body sample: {body[:400]!r}"
    )


@pytest.mark.parametrize(
    "page_path",
    [
        "src/well_harness/static/fan_console.html",
        "src/well_harness/static/demo.html",
        "src/well_harness/static/workbench_spec.html",
    ],
)
def test_embedded_mature_page_exists_on_disk(page_path):
    """Sanity check: the iframe source pages still exist in the repo.
    A renamed/deleted page would break the embed silently — this test
    catches that as a build-time tripwire."""
    assert (REPO_ROOT / page_path).is_file(), (
        f"missing mature page on disk: {page_path}"
    )
