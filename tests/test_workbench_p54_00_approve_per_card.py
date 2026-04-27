"""P54-00 — approve drawer per-card actions, kill the ugly 3-lane zone.

User feedback: when reviewing a proposal, the approve/reject buttons
should sit ON the proposal card, not in a separate big-fonted ugly
zone below. Two structural fixes:

1. The standalone `#approval-center-panel` (3-lane grid with generic
   "Accept Proposal" / "Reject Proposal" buttons that don't even
   target a specific proposal) is removed — it was visual noise that
   reviewers couldn't actually use.
2. The per-card action buttons (rendered by workbench.js as
   `data-proposal-action="accept|reject"`) used to be gated behind
   `body[data-review-mode="on"]`, but the review-mode toggle lived
   in the topbar that P53-00 hid. P54-00 makes per-card actions
   visible whenever the approve drawer itself is open — that IS the
   reviewer surface, and clicking it is intent enough.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HTML = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.html").read_text(encoding="utf-8")
CSS = (REPO_ROOT / "src" / "well_harness" / "static" / "workbench.css").read_text(encoding="utf-8")


# ─── 1. dead surfaces removed ─────────────────────────────────


def test_standalone_approval_center_panel_removed():
    """The 3-lane #approval-center-panel was the 'ugly zone' the
    user objected to. Per-card buttons (rendered by JS) replace it."""
    assert 'id="approval-center-panel"' not in HTML, (
        "P54-00 deletes #approval-center-panel; the per-card buttons "
        "(rendered by JS) are the actual approval surface"
    )


def test_pending_signoff_banner_removed():
    """The 'Pending Kogami sign-off' info card was redundant — the
    presence of OPEN proposals + the approve drawer's title already
    convey 'this is awaiting your approval'."""
    assert 'id="workbench-pending-signoff-affordance"' not in HTML, (
        "P54-00 removes the pending-signoff banner"
    )


def test_bottom_bar_approval_center_entry_removed():
    """The bottom-bar with the '审批中心' entry button only existed
    to scroll-to / reveal the approval-center-panel that's now gone."""
    assert 'id="workbench-bottom-bar"' not in HTML, (
        "P54-00 removes the bottom-bar (only existed to gate access "
        "to the now-removed approval-center-panel)"
    )
    assert 'id="approval-center-entry"' not in HTML


# ─── 2. per-card actions are visible inside approve drawer ────


def test_per_card_actions_visible_in_approve_drawer():
    """The CSS rule that gates `.workbench-annotation-inbox-item-actions`
    visibility must reveal them when the approve drawer is open
    (`.workbench-tool-approve` ancestor), not only when review-mode
    is on (the toggle for that lives in the now-hidden topbar)."""
    pattern = re.compile(
        r'\.workbench-tool-approve\s+\.workbench-annotation-inbox-item\[data-status="OPEN"\]\s+\.workbench-annotation-inbox-item-actions',
    )
    assert pattern.search(CSS), (
        "expected a CSS selector that reveals per-card actions when "
        "inside #workbench-tool-approve (drawer-open == review intent)"
    )


def test_per_card_actions_compact_chip_styling():
    """Inside the approve drawer the action buttons should be small
    inline chips, not full-width bars. Cap padding y ≤0.32rem and
    font ≤0.72rem."""
    rule = re.search(
        r'\.workbench-tool-approve\s+\.workbench-annotation-inbox-item-actions\s+\.workbench-toolbar-button\s*\{[^}]*\}',
        CSS,
        re.DOTALL,
    )
    assert rule is not None, (
        "expected drawer-scoped per-card action button rule"
    )
    body = rule.group(0)
    pad_y = re.search(r'padding:\s*([\d.]+)rem', body)
    assert pad_y is not None
    val = float(pad_y.group(1))
    assert val <= 0.35, (
        f"per-card action button padding y should be ≤0.35rem; got "
        f"{val}rem"
    )
    fs = re.search(r'font-size:\s*([\d.]+)rem', body)
    assert fs is not None
    assert float(fs.group(1)) <= 0.72, (
        f"per-card action button font-size should be ≤0.72rem"
    )
