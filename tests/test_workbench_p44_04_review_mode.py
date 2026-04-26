"""P44-04 — reviewer-mode glowing anchors.

When the reviewer toggles "审核视角 · Review Mode" ON, every OPEN
proposal in the inbox lights up its `interpretation.affected_gates`
on the SVG with a pulsing glow + a per-gate count badge. Click a
glowing anchor to scroll its matching ticket into view; click a
ticket card to spotlight its anchor on the SVG.

Tests below lock the seams the JS depends on:
  - body[data-review-mode] attribute (off by default)
  - topbar toggle button id + chip label slot
  - CSS class names: .is-review-anchor / .is-review-spotlight /
    .workbench-review-anchor-badge / .workbench-review-mode-chip
  - JS function names: installReviewModeToggle / setReviewMode /
    applyReviewAnchors / spotlightCircuitGate / spotlightInboxByGate
  - body[data-review-mode="off"] hides anchors via CSS
  - boot wiring: bootWorkbenchShell calls installReviewModeToggle
  - inbox→anchor coupling: loadProposalsInbox stashes _latestProposals
    and calls applyReviewAnchors
  - circuit-fragment hydration also calls applyReviewAnchors
  - truth-engine red line: review-mode wiring stays out of
    controller / runner / models / adapters / demo_server truth
    surface (it is a static-only feature; no new server endpoints).
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "src" / "well_harness" / "static"
SRC_DIR = REPO_ROOT / "src" / "well_harness"


# ─── 1. HTML anchors ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Body carries the explicit off-state attribute so CSS rules
        # like body[data-review-mode="off"] .is-review-anchor { display:none }
        # bind from first paint.
        'data-review-mode="off"',
        # Topbar toggle button must exist with the documented id.
        'id="workbench-review-mode-toggle"',
        # The chip is also a class hook for CSS theming.
        "workbench-review-mode-chip",
        # Initial state attribute the JS flips to "on" on click.
        'data-review-mode-state="off"',
        # ARIA — toggle buttons must expose pressed state.
        'aria-pressed="false"',
        # Bilingual label, both halves present.
        "审核视角 · Review Mode",
        # Initial label inside the chip strong.
        "关闭 · Off",
        # The label slot the JS swaps text into.
        "data-review-mode-label",
    ],
)
def test_workbench_html_carries_review_mode_toggle(needle):
    html = (STATIC_DIR / "workbench.html").read_text(encoding="utf-8")
    assert needle in html, f"workbench.html missing review-mode hook: {needle}"


# ─── 2. CSS hooks ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # Off-state hides anchors entirely (with !important so any
        # accidental inline style still loses).
        'body[data-review-mode="off"] .is-review-anchor',
        "display: none !important",
        # On-state glow with drop-shadow.
        'body[data-review-mode="on"] .workbench-circuit-hero-mount [data-gate-id].is-review-anchor',
        "drop-shadow(0 0 6px #4fb8ff)",
        # Pulse animation keyframes by exact name (the JS doesn't
        # reference it but a rename here would silently kill the glow).
        "@keyframes workbench-review-anchor-pulse",
        # Spotlight class for the click-driven flash.
        ".is-review-spotlight",
        "@keyframes workbench-review-spotlight-fade",
        # Per-gate count badge styling.
        ".workbench-review-anchor-badge",
        # Toggle chip styling tied to data-review-mode-state.
        '.workbench-review-mode-chip[data-review-mode-state="on"]',
    ],
)
def test_workbench_css_carries_review_mode_rules(needle):
    css = (STATIC_DIR / "workbench.css").read_text(encoding="utf-8")
    assert needle in css, f"workbench.css missing review-mode rule: {needle}"


# ─── 3. JS wiring ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    "needle",
    [
        # State seed for the proposal stash the review wiring reads.
        "let _latestProposals = [];",
        # Top-level functions the test contract locks by name.
        "function installReviewModeToggle()",
        "function setReviewMode(state)",
        "function applyReviewAnchors(proposals)",
        "function spotlightCircuitGate(gateId)",
        "function spotlightInboxByGate(gateId)",
        # Boot: shell installer must wire the toggle on first paint.
        "installReviewModeToggle();",
        # Hydration: re-apply anchors right after the SVG mounts so a
        # late-arriving fragment still picks up an already-loaded
        # inbox.
        "applyReviewAnchors(_latestProposals);",
        # Inbox→anchor coupling: cache stash + re-apply after every
        # /api/proposals refresh.
        "_latestProposals = proposals;",
        # Body attribute is the single CSS gate.
        'document.body.setAttribute("data-review-mode", enabled ? "on" : "off");',
        # Reverse coupling: clicking a ticket card spotlights its gate.
        "spotlightCircuitGate(gateId);",
        # Click-on-anchor → spotlight inbox card.
        "spotlightInboxByGate(gateId)",
        # Badge is created in the SVG namespace so it inherits the
        # circuit's coordinate system.
        '"http://www.w3.org/2000/svg"',
        # Per-gate aggregation only counts OPEN tickets.
        'p.status !== "OPEN"',
    ],
)
def test_workbench_js_wires_review_mode(needle):
    js = (STATIC_DIR / "workbench.js").read_text(encoding="utf-8")
    assert needle in js, f"workbench.js missing review-mode wiring: {needle}"


# ─── 4. Truth-engine red-line guard ─────────────────────────────────


def test_p44_04_does_not_leak_into_truth_engine():
    """Reviewer mode is a 100% static-only feature — no controller /
    runner / models / adapters changes, no new server endpoints. If
    any of those files end up referencing review-mode tokens, the
    feature has overstepped its scope and this test fails loudly."""
    truth_files: list[Path] = [
        SRC_DIR / "controller.py",
        SRC_DIR / "runner.py",
        SRC_DIR / "models.py",
        SRC_DIR / "demo_server.py",
    ]
    truth_files.extend((SRC_DIR / "adapters").rglob("*.py"))
    forbidden = (
        "review_mode",
        "is-review-anchor",
        "spotlightCircuitGate",
        "spotlightInboxByGate",
        "workbench-review-mode-toggle",
    )
    for path in truth_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(REPO_ROOT)} leaks P44-04 review-mode "
                f"token '{token}' — review mode must stay static-only"
            )
