"""P50-02c — compute_phase_timings extraction.

Locks down: walking the events log produces correct per-phase
durations, handles missing/unparseable timestamps gracefully,
and returns a deterministic shape regardless of how far the
execution progressed.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionEvent,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.phase_timings import (
    PhaseTiming,
    PhaseTimings,
    compute_phase_timings,
)
from well_harness.skill_executor.states import ExecutionState


def _record(
    *,
    state: str = ExecutionState.LANDED.value,
    started_at: str = "2026-04-27T12:00:00Z",
    finished_at: str = "2026-04-27T12:10:00Z",
    events: list[ExecutionEvent] | None = None,
) -> ExecutionRecord:
    return ExecutionRecord(
        exec_id="EXEC-20260427T120000000000-aaaaaa",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-test",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at=started_at,
        finished_at=finished_at,
        state=state,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
        events=events or [],
    )


def _trans(at: str, from_state: str, to_state: str) -> ExecutionEvent:
    return ExecutionEvent(
        at=at,
        kind="state_transition",
        from_state=from_state,
        to_state=to_state,
    )


# ─── 1. Empty audit — INIT only, never advanced ───────────────────


def test_empty_events_only_init_phase_populated():
    """Audit with no transitions: INIT lasts the whole started→finished
    window; other phases are None."""
    rec = _record(events=[])
    out = compute_phase_timings(rec)
    init_t = next(t for t in out.timings if t.phase == "INIT")
    assert init_t.duration_sec == 600.0  # 10 minutes
    # Other phases have None duration since they were never entered
    for phase in ["PLANNING", "ASKING", "EDITING", "TESTING", "PR_OPEN"]:
        t = next(p for p in out.timings if p.phase == phase)
        assert t.duration_sec is None


# ─── 2. Standard happy-path walk — INIT→PLANNING→ASKING→… ────────


def test_full_lifecycle_durations_computed_correctly():
    """A typical happy-path execution. Each phase's duration is
    the gap between its entry and the next state's entry."""
    rec = _record(
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:30:00Z",
        events=[
            _trans("2026-04-27T12:00:05Z", "INIT", "PLANNING"),
            _trans("2026-04-27T12:00:15Z", "PLANNING", "ASKING"),
            _trans("2026-04-27T12:25:15Z", "ASKING", "EDITING"),
            _trans("2026-04-27T12:25:20Z", "EDITING", "TESTING"),
            _trans("2026-04-27T12:25:30Z", "TESTING", "PR_OPEN"),
        ],
    )
    out = compute_phase_timings(rec)
    by_phase = {t.phase: t for t in out.timings}
    assert by_phase["INIT"].duration_sec == 5.0
    assert by_phase["PLANNING"].duration_sec == 10.0
    # ASKING took 25 minutes (waited on user)
    assert by_phase["ASKING"].duration_sec == 1500.0
    assert by_phase["EDITING"].duration_sec == 5.0
    assert by_phase["TESTING"].duration_sec == 10.0
    # PR_OPEN closed by finished_at: 12:30:00 - 12:25:30 = 4.5min
    assert by_phase["PR_OPEN"].duration_sec == 270.0


def test_total_duration_matches_started_finished_pair():
    rec = _record(
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:30:00Z",
    )
    out = compute_phase_timings(rec)
    assert out.total_duration_sec == 1800.0


# ─── 3. In-flight audit — finished_at empty ──────────────────────


def test_unfinished_last_phase_has_none_duration():
    """If the audit is still in flight, the current phase's
    exit_at is empty so its duration is None."""
    rec = _record(
        state=ExecutionState.ASKING.value,
        started_at="2026-04-27T12:00:00Z",
        finished_at="",  # still in flight
        events=[
            _trans("2026-04-27T12:00:05Z", "INIT", "PLANNING"),
            _trans("2026-04-27T12:00:15Z", "PLANNING", "ASKING"),
        ],
    )
    out = compute_phase_timings(rec)
    by_phase = {t.phase: t for t in out.timings}
    assert by_phase["INIT"].duration_sec == 5.0
    assert by_phase["PLANNING"].duration_sec == 10.0
    # ASKING still in progress: no exit_at, no duration
    assert by_phase["ASKING"].duration_sec is None
    # Total also None since finished_at is empty
    assert out.total_duration_sec is None


def test_current_phase_reported_from_record_state():
    rec = _record(state="ASKING", events=[])
    out = compute_phase_timings(rec)
    assert out.current_phase == "ASKING"


# ─── 4. ABORTED / FAILED termination ──────────────────────────────


def test_aborted_after_asking_phase_durations_correct():
    """Audit was cancelled in ASKING; finished_at marks the abort.
    INIT and PLANNING get full durations, ASKING up to the abort,
    EDITING/TESTING/PR_OPEN never reached."""
    rec = _record(
        state=ExecutionState.ABORTED.value,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:05:00Z",
        events=[
            _trans("2026-04-27T12:00:05Z", "INIT", "PLANNING"),
            _trans("2026-04-27T12:00:10Z", "PLANNING", "ASKING"),
            _trans("2026-04-27T12:05:00Z", "ASKING", "ABORTED"),
        ],
    )
    out = compute_phase_timings(rec)
    by_phase = {t.phase: t for t in out.timings}
    assert by_phase["INIT"].duration_sec == 5.0
    assert by_phase["PLANNING"].duration_sec == 5.0
    assert by_phase["ASKING"].duration_sec == 290.0  # ~5 min
    # Phases never reached
    assert by_phase["EDITING"].duration_sec is None
    assert by_phase["TESTING"].duration_sec is None
    assert by_phase["PR_OPEN"].duration_sec is None


# ─── 5. Robustness — malformed timestamps ─────────────────────────


def test_malformed_timestamp_returns_none_duration():
    rec = _record(
        events=[
            _trans("not-a-time", "INIT", "PLANNING"),
        ],
    )
    out = compute_phase_timings(rec)
    init_t = next(t for t in out.timings if t.phase == "INIT")
    # PLANNING entered at unparseable time → no clean duration for INIT
    assert init_t.duration_sec is None


def test_negative_duration_returns_none():
    """Clock skew: finished_at < started_at. Don't fake a negative."""
    rec = _record(
        started_at="2026-04-27T12:30:00Z",
        finished_at="2026-04-27T12:00:00Z",
        events=[],
    )
    out = compute_phase_timings(rec)
    assert out.total_duration_sec is None


def test_non_state_transition_events_ignored():
    """planner_invocation, edit_apply, etc. should NOT contribute
    to the transition chain."""
    rec = _record(
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:00:30Z",
        events=[
            ExecutionEvent(at="2026-04-27T12:00:01Z", kind="init", note="x"),
            _trans("2026-04-27T12:00:05Z", "INIT", "PLANNING"),
            ExecutionEvent(at="2026-04-27T12:00:08Z", kind="planner_invocation"),
            _trans("2026-04-27T12:00:10Z", "PLANNING", "ASKING"),
        ],
    )
    out = compute_phase_timings(rec)
    by_phase = {t.phase: t for t in out.timings}
    assert by_phase["INIT"].duration_sec == 5.0
    assert by_phase["PLANNING"].duration_sec == 5.0
    # ASKING from 12:00:10 to finished_at 12:00:30 = 20s
    assert by_phase["ASKING"].duration_sec == 20.0


# ─── 6. JSON serialization ──────────────────────────────────────


def test_to_json_shape_stable():
    """Lock down the JSON contract the frontend will rely on."""
    rec = _record()
    out = compute_phase_timings(rec)
    payload = out.to_json()
    assert "timings" in payload
    assert "current_phase" in payload
    assert "total_duration_sec" in payload
    # Each timing entry has the expected keys
    for t in payload["timings"]:
        assert set(t.keys()) == {
            "phase", "duration_sec", "entered_at", "exited_at"
        }


def test_phases_returned_in_canonical_order():
    rec = _record()
    out = compute_phase_timings(rec)
    expected_order = [
        "INIT", "PLANNING", "ASKING", "EDITING", "TESTING", "PR_OPEN"
    ]
    assert [t.phase for t in out.timings] == expected_order


# ─── 7. Backfill audits — minimal events ─────────────────────────


def test_backfill_audit_has_zero_or_none_durations():
    """Backfill records typically have started_at == finished_at
    and no transitions (state set directly to LANDED). All phase
    durations should be 0 or None."""
    rec = ExecutionRecord(
        exec_id="EXEC-20260427T120000000000-bf1234",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-backfilled",
        kind=ExecutionKind.BACKFILL,
        audit_source=AuditSource.BACKFILL,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:00:00Z",  # same time
        state=ExecutionState.LANDED.value,
        executor_version="0.0-backfill",
        plan=PlannedChange(rationale="backfilled", file_edits=[]),
        events=[],
    )
    out = compute_phase_timings(rec)
    init_t = next(t for t in out.timings if t.phase == "INIT")
    # Same start/finish → duration is 0
    assert init_t.duration_sec == 0.0
