"""P55-02 — Stately Studio-style always-on gate proposal indicators.

Stately's defining UX choice: semantic feedback at the element
level, always visible, never behind a toggle. Their state nodes
carry icons (warning on unreachable, info clickable for details)
the engineer sees at-a-glance without flipping a "review mode"
switch first.

We adopt the same pattern for our circuit gates. Pre-P55-02 the
per-gate OPEN-proposal count was rendered as an amber SVG <text>
badge gated behind body[data-review-mode="on"] — the engineer had
to know review mode existed AND remember to toggle it before they
could see "L1 has 3 open tickets". P55-02 splits that into two
layers:

  - Always-on Stately marker: small accent-toned rounded rect at
    the gate's top-right corner, count rendered, click opens the
    approve drawer + spotlights the matching inbox card. Visible
    the moment the page loads.

  - Review-mode spotlight: the heavier glow + pulse (preserved
    from P44-04) stays gated by the review-mode toggle — that's
    the auditor's "reviewing now" lens, not the at-a-glance read.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
JS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.js").read_text(
    encoding="utf-8"
)
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(
    encoding="utf-8"
)


# ─── 1. Two-layer split exists in JS ───


def test_js_splits_marker_and_spotlight_into_two_functions() -> None:
    """The amber-toggle-gated badge code must split into:
       applyGateProposalMarkers — always-on (Stately-style)
       applyReviewSpotlight     — review-mode-gated (legacy glow)
    The legacy applyReviewAnchors entry point stays as a thin
    wrapper so existing call sites don't churn."""
    assert "function applyGateProposalMarkers(" in JS
    assert "function applyReviewSpotlight(" in JS
    # Wrapper must invoke both.
    wrapper = re.search(
        r"function applyReviewAnchors\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert wrapper is not None
    body = wrapper.group(1)
    assert "applyGateProposalMarkers(proposals)" in body
    assert "applyReviewSpotlight(proposals)" in body


def test_marker_function_does_not_check_review_mode() -> None:
    """The always-on layer must NOT short-circuit on
    data-review-mode. That gate is the legacy behavior we're
    explicitly fixing — markers belong in the at-a-glance lens."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'getAttribute("data-review-mode")' not in body, (
        "applyGateProposalMarkers must not gate on review-mode "
        "(that's the spotlight layer's job)"
    )


def test_spotlight_function_keeps_review_mode_gate() -> None:
    """The auditor lens (heavy glow + pulse) stays gated."""
    fn = re.search(
        r"function applyReviewSpotlight\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'data-review-mode' in body, (
        "applyReviewSpotlight must continue to gate on review-mode"
    )


# ─── 2. Marker DOM shape ───


def test_marker_emits_svg_group_with_rect_label_and_title() -> None:
    """Each marker is an SVG <g> carrying:
       <title>     — accessible tooltip
       <rect>      — accent-tinted background
       <text>      — count label
    All three must be createElementNS'd against the SVG namespace."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'createElementNS(NS, "g")' in body
    assert 'createElementNS(NS, "rect")' in body
    assert 'createElementNS(NS, "text")' in body
    assert 'createElementNS(NS, "title")' in body


def test_marker_carries_data_attributes_for_test_hooks() -> None:
    """Each marker exposes its target gate id + count via data-*
    attributes so DOM-level tests + future debugging surfaces can
    reach in cleanly."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'setAttribute("data-marker-for"' in body
    assert 'setAttribute("data-open-count"' in body


# ─── 3. Click behaviour ───


def test_marker_click_opens_approve_drawer_and_spotlights() -> None:
    """Click on the marker must (a) open the approve drawer if it
    isn't already, and (b) spotlight the matching inbox card.
    Stately's "info icon opens the inspector" pattern."""
    assert "function openApproveDrawerAndSpotlight(" in JS
    fn = re.search(
        r"function openApproveDrawerAndSpotlight\(gateId\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert 'data-dock-target="approve"' in body, (
        "must locate the approve dock button to open the drawer"
    )
    assert "spotlightInboxByGate(gateId)" in body
    # Marker click handler must call this helper.
    marker_fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert marker_fn is not None
    assert "openApproveDrawerAndSpotlight(gateId)" in marker_fn.group(1)


def test_marker_click_uses_stoppropagation() -> None:
    """The gate <use> elements may also have click handlers (review
    spotlight). The marker click must stop propagation so it
    doesn't double-fire the gate-level handler."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    assert "stopPropagation" in fn.group(1)


# ─── 4. Pure-helper extraction ───


def test_count_aggregator_is_pure_and_reusable() -> None:
    """computeOpenProposalCountsByGate must be a pure helper —
    no DOM access, no side effects — so both layers and tests can
    consume it without setting up a fake DOM."""
    assert "function computeOpenProposalCountsByGate(" in JS
    fn = re.search(
        r"function computeOpenProposalCountsByGate\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "document" not in body, (
        "helper must be pure (no DOM access)"
    )
    # Filter must keep ONLY OPEN proposals — accepted/rejected don't
    # belong on the at-a-glance marker.
    assert 'p.status !== "OPEN"' in body or "p.status != 'OPEN'" in body


# ─── 5. CSS — Stately aesthetic, accent-toned ───


@pytest.mark.parametrize(
    "selector",
    [
        ".workbench-gate-proposal-marker",
        ".workbench-gate-proposal-marker-bg",
        ".workbench-gate-proposal-marker-label",
    ],
)
def test_css_declares_marker_styles(selector: str) -> None:
    assert selector in CSS, f"missing CSS rule: {selector}"


def test_marker_styles_use_accent_tokens_not_hardcoded_colors() -> None:
    """The marker is the ONE place we want the brand accent in the
    canvas — Linear's discipline. It must derive from the LCH
    accent tokens established in P55-01, not bare hex/rgba."""
    rule = re.search(
        r"\.workbench-gate-proposal-marker-bg\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None
    body = rule.group(0)
    assert "var(--accent-tint" in body, (
        "marker bg fill must use --accent-tint-* token"
    )
    assert "var(--accent)" in body, (
        "marker stroke must use --accent token"
    )
    label_rule = re.search(
        r"\.workbench-gate-proposal-marker-label\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert label_rule is not None
    label_body = label_rule.group(0)
    assert "var(--accent)" in label_body
    # Monospace for the digit — Stately + Linear discipline.
    assert any(
        font in label_body for font in ("SF Mono", "Menlo", "Consolas")
    ), "count digit must render in a monospace face"


def test_marker_has_hover_affordance() -> None:
    """Hover lifts the bg fill so the click affordance is obvious.
    Stately's clickable info icons get a subtle on-hover boost."""
    rule = re.search(
        r"\.workbench-gate-proposal-marker:hover\s+"
        r"\.workbench-gate-proposal-marker-bg\s*\{[^}]+\}",
        CSS,
        re.DOTALL,
    )
    assert rule is not None, "missing hover bg lift"


# ─── 6. The legacy amber badge is GONE ───


def test_legacy_amber_review_anchor_badge_removed() -> None:
    """Pre-P55-02 the badge was the amber `.workbench-review-anchor-badge`.
    P55-02 replaces it with the new accent-toned marker. The
    create/append code path for the old class name must be gone
    so we don't paint two surfaces on the same gate."""
    fn = re.search(
        r"function applyGateProposalMarkers\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert fn is not None
    body = fn.group(1)
    assert "workbench-review-anchor-badge" not in body, (
        "applyGateProposalMarkers must not paint the legacy amber badge"
    )
    spot_fn = re.search(
        r"function applyReviewSpotlight\(proposals\) \{(.*?)^}",
        JS,
        re.DOTALL | re.MULTILINE,
    )
    assert spot_fn is not None
    spot_body = spot_fn.group(1)
    # The spotlight layer also stops creating amber badges.
    assert "createElementNS" not in spot_body or (
        "workbench-review-anchor-badge" not in spot_body
    ), "applyReviewSpotlight must not paint the legacy amber badge either"
