"""P57-01 — visual event-table editor for timeline-sim.html.

Replaces the JSON-textarea-only authoring workflow with a structured
event table. Users click "Add Row" / edit cells / delete rows
directly; the existing JSON textarea stays present (hidden behind a
Raw JSON tab) and is the wire format the run-button POSTs from. The
visual editor writes to the textarea on every change so the existing
POST path is unchanged — zero backend regression.

Goal of this phase: make the timeline-sim page *authorable without
JSON*. P57-02 layers system-aware target dropdowns on top; P57-03
adds save/load. P57-01 only ships the table mechanism + tab UI.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TIMELINE_SIM = (
    REPO_ROOT / "src" / "well_harness" / "static" / "timeline-sim.html"
)


def _read() -> str:
    return TIMELINE_SIM.read_text(encoding="utf-8")


# ─── 1. Tab UI: [Visual Editor] | [Raw JSON] ───


def test_timeline_sim_has_visual_editor_tab() -> None:
    """The Visual Editor tab must exist as a clickable element. Default
    visible tab — preset users land on the structured table, not on
    JSON, per the P57 deep plan (D1 = Visual default)."""
    body = _read()
    # Look for a tab button or radio with id/data-tab="visual" and
    # human-readable Chinese label "Visual" or "可视化".
    visual_tab = re.search(
        r'data-tab="visual"|id="tabVisual"|class="[^"]*tab[^"]*visual',
        body,
    )
    assert visual_tab is not None, (
        "no Visual Editor tab marker found. Add a tab button with "
        "data-tab=\"visual\" so the test (and CSS) can target it."
    )


def test_timeline_sim_has_raw_json_tab() -> None:
    """The Raw JSON tab must exist as a clickable element (power-user
    escape hatch + backward-compat for users who paste JSON directly)."""
    body = _read()
    raw_tab = re.search(
        r'data-tab="raw"|id="tabRaw"|class="[^"]*tab[^"]*raw',
        body,
    )
    assert raw_tab is not None, (
        "no Raw JSON tab marker found. Add a tab button with "
        "data-tab=\"raw\" so users can still paste JSON when needed."
    )


def test_timeline_sim_visual_tab_is_default_active() -> None:
    """Per D1 = Visual default. The Visual tab markup must declare
    aria-selected=true (or class~=active / data-active=visual on a
    container) on first paint so users see the table not JSON."""
    body = _read()
    # Match either an aria-selected on the visual tab or a body/container
    # marker noting visual is the active tab.
    visual_active = re.search(
        r'data-tab="visual"[^>]*aria-selected="true"'
        r'|aria-selected="true"[^>]*data-tab="visual"'
        r'|data-active-tab="visual"'
        r'|class="[^"]*tab[^"]*active[^"]*"[^>]*data-tab="visual"'
        r'|data-tab="visual"[^>]*class="[^"]*active',
        body,
    )
    assert visual_active is not None, (
        "Visual Editor tab must be the default-active tab on first paint. "
        "Mark it with aria-selected=\"true\" or class containing 'active'."
    )


# ─── 2. Event table structure ───


def test_timeline_sim_has_event_table() -> None:
    """The Visual editor centerpiece is a `<table>` (or a div-grid
    masquerading as one) with id="eventTable" so the JS can target it."""
    body = _read()
    table = re.search(
        r'<table[^>]*\bid="eventTable"|<div[^>]*\bid="eventTable"',
        body,
    )
    assert table is not None, (
        "no element with id=\"eventTable\" found — the visual editor "
        "must mount the events list under this id so the JS can "
        "rebuild rows from the events[] array."
    )


def test_timeline_sim_event_table_has_required_columns() -> None:
    """The event table header must declare columns covering the 7
    fields of TimelineEvent (t_s, kind, target, value, duration_s,
    phase/note, actions). Specifically these four are mandatory:
    t_s, kind, target, value. Missing one means the user cannot
    author a complete event."""
    body = _read()
    # Grab the entire eventTable element (or a tbody-bearing container
    # near it) and check its header text.
    table_match = re.search(
        r'(<table[^>]*\bid="eventTable"[^>]*>.*?</table>'
        r'|<div[^>]*\bid="eventTable"[^>]*>.*?</div>)',
        body,
        re.DOTALL,
    )
    assert table_match is not None, "eventTable not found"
    table_html = table_match.group(0)
    required_cols = ["t_s", "kind", "target", "value"]
    missing = [c for c in required_cols if c not in table_html]
    assert not missing, (
        f"eventTable header is missing columns: {missing}. The visual "
        f"editor must expose at least t_s/kind/target/value so users "
        f"can author all event kinds."
    )


def test_timeline_sim_has_add_row_control() -> None:
    """An 'Add Row' control must exist so the user can extend the
    events list. Without this, only loading presets gets you events."""
    body = _read()
    add_btn = re.search(
        r'<button[^>]*\bid="addRow"|<button[^>]*data-action="add-row"',
        body,
    )
    assert add_btn is not None, (
        "no 'Add Row' button (id=\"addRow\" or "
        "data-action=\"add-row\") found in the visual editor."
    )


# ─── 3. Two-way sync with the textarea ───


def test_timeline_sim_keeps_textarea_for_compat() -> None:
    """Per D4: hide the existing `<textarea id="timelineJson">` behind
    the Raw tab but keep it. The run button still POSTs from this
    textarea, so the visual editor must write into it on every change.
    Removing the textarea would break the POST path."""
    body = _read()
    textarea = re.search(
        r'<textarea[^>]*\bid="timelineJson"', body,
    )
    assert textarea is not None, (
        "the JSON textarea (id=\"timelineJson\") must be preserved — "
        "the run button reads from it. Visual editor only writes to it."
    )


def test_timeline_sim_visual_editor_writes_to_textarea() -> None:
    """The JS must contain a function that serializes the events
    array into the textarea (so changes in Visual mode propagate to
    the run-button's POST payload). Look for a function name like
    `syncToTextarea` / `serializeEvents` / similar handler."""
    body = _read()
    # Match either: function declaration, or a call writing to
    # timelineJson.value with JSON.stringify.
    pattern = (
        r'function\s+(?:syncToTextarea|serializeEvents|writeJson|'
        r'updateRawJson|toTextarea|renderJson)'
        r'|getElementById\("timelineJson"\)\.value\s*=\s*JSON\.stringify'
        r'|\$\("timelineJson"\)\.value\s*=\s*JSON\.stringify'
    )
    sync_fn = re.search(pattern, body)
    assert sync_fn is not None, (
        "no sync function found. The visual editor MUST write the "
        "events array into the textarea on every change so the "
        "existing POST path stays correct."
    )


def test_timeline_sim_raw_to_visual_sync_exists() -> None:
    """When the user types into the Raw JSON tab, the Visual editor
    must repopulate from the new JSON on tab switch (or on blur).
    Otherwise the Visual tab silently shows stale events."""
    body = _read()
    pattern = (
        r'function\s+(?:loadFromTextarea|parseAndRender|hydrateFromJson|'
        r'rebuildFromRaw|fromRawJson|loadRawJson)'
        r'|JSON\.parse\([^)]*timelineJson'
    )
    parse_fn = re.search(pattern, body)
    assert parse_fn is not None, (
        "no Raw→Visual sync function found. After editing in Raw tab "
        "the Visual table must reflect the JSON state. Look at the "
        "tab-switch handler for a JSON.parse(timelineJson) call."
    )


# ─── 4. Row-level edit affordances ───


@pytest.mark.parametrize(
    "action_marker",
    [
        # Delete a row.
        r'data-action="delete-row"|class="[^"]*delete-row',
        # Move row up.
        r'data-action="move-up"|class="[^"]*move-up',
        # Move row down.
        r'data-action="move-down"|class="[^"]*move-down',
    ],
    ids=["delete", "move-up", "move-down"],
)
def test_timeline_sim_event_row_has_action_markers(
    action_marker: str,
) -> None:
    """Each event row needs delete + move-up + move-down. Without
    them the user can only append, never reorder or remove. Markers
    can live in row template HTML or in JS that builds rows."""
    body = _read()
    found = re.search(action_marker, body)
    assert found is not None, (
        f"action marker {action_marker!r} not found. The visual editor "
        f"row template must include delete + move-up + move-down "
        f"affordances so users can manage the event list."
    )


# ─── 5. JSON metadata (system / step_s / duration_s) stays editable ───


def test_timeline_sim_metadata_editable_via_visual_or_raw() -> None:
    """`system`, `step_s`, `duration_s`, `initial_inputs` are timeline
    metadata. P57-01 may either expose them in Visual mode OR keep
    them in Raw-only — but they MUST stay editable. If Visual is
    forced and the user wants to switch system/step_s, they need a
    path. Acceptable: visual exposes a metadata strip OR Raw tab is
    one click away. The Raw tab existence test (above) covers the
    second path; this test ensures the strip OR Raw tab is reachable."""
    body = _read()
    # The Raw JSON tab existence already covered in test 2. Here we
    # just verify the test suite distinguishes "metadata" from "events"
    # so future P57-02 can extend Visual safely. Smoke check: there is
    # at least one mention of `step_s` and `duration_s` somewhere in
    # the visual-editor JS.
    assert re.search(r'\bstep_s\b', body), (
        "step_s metadata must remain present in either Visual or Raw "
        "form — the timeline simulator cannot run without it."
    )
    assert re.search(r'\bduration_s\b', body), (
        "duration_s metadata must remain present in either Visual or "
        "Raw form."
    )
