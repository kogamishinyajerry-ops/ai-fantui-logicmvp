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


# ─── 4b. Codex R1 safety contracts (Raw-active guard / number coerce / bool fold) ───
#
# Codex R1 (PR #117) returned CHANGES_REQUIRED with 2 HIGH + 2 MEDIUM:
#   H1 — metadata edits in Raw mode silently overwrite Raw textarea
#        edits because syncToTextarea() runs against the stale model.
#   H2 — renderEventRow interpolates ev.t_s / ev.duration_s straight
#        into innerHTML; a hostile Raw payload with string values
#        could inject markup.
#   M3 — value parser treats "True" / "False" as strings; executors
#        bool() those silently the wrong way.
#   M4 — tests are source-regex only and don't catch the above.
# The four tests below close the M4 gap by asserting the source
# contracts that fix H1 / H2 / M3.


def test_metadata_handlers_guard_against_raw_active() -> None:
    """The metadata strip is always visible. When Raw tab is active
    and the user changes system/step_s/duration_s, the handler MUST
    refresh the model from the textarea before mutating, otherwise
    syncToTextarea() will overwrite the user's in-flight Raw edits.

    Codex R2 MEDIUM tightening: the guard MUST run BEFORE any
    `currentTimeline.<field> =` assignment in the same handler block.
    A regex hit on the helper name is not enough — the helper could
    be called after the mutation, defeating its purpose."""
    body = _read()
    # For each handler, extract its full body and assert the guard
    # call appears BEFORE any currentTimeline assignment.
    for handler_id in ("metaSystem", "metaStepS", "metaDurationS"):
        # Match: $("<id>").addEventListener("change", () => { ... });
        m = re.search(
            rf'\$\("{handler_id}"\)\.addEventListener\(\s*"change"\s*,'
            rf'\s*\(\)\s*=>\s*\{{(.*?)\}}\s*\)\s*;',
            body,
            re.DOTALL,
        )
        assert m is not None, f"handler for {handler_id} not found"
        h_body = m.group(1)
        guard_pos = re.search(
            r"(?:loadFromTextarea|refreshModelIfRawActive)\s*\(", h_body,
        )
        mut_pos = re.search(
            r"currentTimeline\.\w+\s*=", h_body,
        )
        assert guard_pos is not None, (
            f"{handler_id} handler missing raw-active guard call "
            f"(Codex R1 H1)."
        )
        if mut_pos is not None:
            assert guard_pos.start() < mut_pos.start(), (
                f"{handler_id} handler calls the guard AFTER mutating "
                f"currentTimeline. The guard must run first or it "
                f"can't refuse stale-model writes (Codex R2 MEDIUM)."
            )


def test_event_row_render_coerces_BOTH_t_s_and_duration_s() -> None:
    """`renderEventRow()` writes BOTH ev.t_s AND ev.duration_s into
    the DOM string. Codex R2 MEDIUM: R1 H2 fix only proven for t_s;
    duration_s is the equally dangerous sink. Both must go through
    a safe-number helper before interpolation."""
    body = _read()
    for field in ("t_s", "duration_s"):
        coerce_pattern = (
            rf'safeNumber\s*\(\s*ev\.{field}'
            rf'|Number\(\s*ev\.{field}\s*\)'
            rf'|parseFloat\(\s*ev\.{field}\s*\)'
        )
        has_coerce = re.search(coerce_pattern, body)
        assert has_coerce is not None, (
            f"renderEventRow does not coerce ev.{field} through a "
            f"safe number helper. Hostile Raw input could inject "
            f"markup via the {field} sink (Codex R2 MEDIUM)."
        )


def test_value_parser_case_folds_all_three_keywords() -> None:
    """The event-value parser must fold "true"/"false"/"null"
    (case-insensitive) BEFORE JSON.parse — not just one or two of
    them. Codex R2 MEDIUM: R1 M3 only required "true"; the "false"
    and "null" branches must also exist with the same case-folded
    comparison so all three executor-relevant literals are honored."""
    body = _read()
    # The case-folded variable name is consistent across our impl;
    # just check each of the three string literals is compared after
    # a toLowerCase() in the same neighborhood.
    for keyword in ("true", "false", "null"):
        pattern = rf'toLowerCase\(\)[\s\S]{{0,300}}["\']{keyword}["\']'
        m = re.search(pattern, body)
        assert m is not None, (
            f"value parser missing case-folded branch for {keyword!r}. "
            f"All three (true/false/null) must be handled before "
            f"JSON.parse (Codex R2 MEDIUM)."
        )


def test_value_parser_case_fold_runs_before_json_parse() -> None:
    """Codex R2 MEDIUM: ordering matters. If JSON.parse runs first,
    "True" throws SyntaxError and falls through to string. The
    case-fold (toLowerCase + literal compares) must appear in the
    source BEFORE the JSON.parse(raw) call inside the same handler
    branch."""
    body = _read()
    # Find the value-field handler block (where 'value' field is
    # processed). It contains both the toLowerCase block and the
    # JSON.parse(raw) call. Confirm the toLowerCase appears first.
    fold_pos = body.find("toLowerCase()")
    parse_pos = body.find("JSON.parse(raw)")
    assert fold_pos != -1, "value parser missing toLowerCase()"
    assert parse_pos != -1, "value parser missing JSON.parse(raw)"
    assert fold_pos < parse_pos, (
        "toLowerCase() case-fold runs AFTER JSON.parse(raw). The "
        "fold must run first or 'True' / 'FALSE' fall through to "
        "string (Codex R2 MEDIUM)."
    )


def test_metadata_strip_re_renders_after_guard_failure() -> None:
    """Codex R2 LOW: when the guard rejects the change (Raw JSON
    invalid OR step/duration <= 0), the user-typed value would
    otherwise stay visible in the control while the model + textarea
    are unchanged. After a guard failure, the handler must call
    `renderMetaStrip()` (or set the input.value back) so the strip
    doesn't lie about the active model."""
    body = _read()
    for handler_id in ("metaSystem", "metaStepS", "metaDurationS"):
        m = re.search(
            rf'\$\("{handler_id}"\)\.addEventListener\(\s*"change"\s*,'
            rf'\s*\(\)\s*=>\s*\{{(.*?)\}}\s*\)\s*;',
            body,
            re.DOTALL,
        )
        assert m is not None, f"handler for {handler_id} not found"
        h_body = m.group(1)
        # Each handler must call renderMetaStrip() somewhere on the
        # rejection path (or set the input.value back). The simplest
        # contract: renderMetaStrip is referenced at least once.
        assert "renderMetaStrip" in h_body or (
            f'$("{handler_id}").value' in h_body
        ), (
            f"{handler_id} handler does not re-render the metadata "
            f"strip on guard failure. The control would show the "
            f"user-typed value while the model is unchanged "
            f"(Codex R2 LOW)."
        )


def test_load_from_textarea_returns_status_for_guard() -> None:
    """`loadFromTextarea()` must return a truthy-on-success / falsy-on-
    failure status so the metadata handlers can use it as a guard
    (`if (!refreshModelIfRawActive()) return;`). A void function
    can't be guarded against — re-check that the function has an
    explicit `return true` / `return false` branch."""
    body = _read()
    # Find the loadFromTextarea function body and check it returns
    # both true and false (success vs parse-failure paths).
    fn_match = re.search(
        r'function\s+loadFromTextarea\s*\([^)]*\)\s*\{(.*?)\n\}',
        body,
        re.DOTALL,
    )
    assert fn_match is not None, "loadFromTextarea function not found"
    fn_body = fn_match.group(1)
    assert "return true" in fn_body and "return false" in fn_body, (
        "loadFromTextarea must return true on parse success and false "
        "on failure so refreshModelIfRawActive can guard metadata "
        "handlers (Codex R1 H1)."
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
