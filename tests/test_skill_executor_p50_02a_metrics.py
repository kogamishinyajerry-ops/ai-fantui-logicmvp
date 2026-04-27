"""P50-02a — compute_metrics() over ExecutionRecord lists.

Locks down: the metrics aggregator handles empty input, computes
correct state counts, pass rate, durations, and failure list.
Pure function, no IO.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.metrics import (
    Metrics,
    RecentFailure,
    compute_metrics,
)
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.states import ExecutionState


def _rec(
    exec_id: str = "EXEC-20260427T120000000000-aaaaaa",
    *,
    proposal_id: str = "PROP-test",
    state: str = ExecutionState.LANDED.value,
    started_at: str = "2026-04-27T12:00:00Z",
    finished_at: str = "2026-04-27T12:01:30Z",
    abort_reason: str = "",
    audit_source: AuditSource = AuditSource.LIVE,
    kind: ExecutionKind = ExecutionKind.MODIFY,
) -> ExecutionRecord:
    return ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id=proposal_id,
        kind=kind,
        audit_source=audit_source,
        started_at=started_at,
        finished_at=finished_at,
        state=state,
        executor_version="0.1-test",
        abort_reason=abort_reason,
        plan=PlannedChange(rationale="test", file_edits=[]),
    )


# ─── 1. Empty input ──────────────────────────────────────────────────


def test_empty_records_returns_zero_metrics():
    m = compute_metrics([])
    assert m.total == 0
    assert m.pass_rate == 0.0
    assert m.completed_count == 0
    assert m.median_duration_sec is None
    assert m.p95_duration_sec is None
    assert m.recent_failures == []
    assert m.backfill_count == 0
    # All 9 states pre-populated with 0
    for state in [s.value for s in ExecutionState]:
        assert m.by_state[state] == 0


# ─── 2. State counts ─────────────────────────────────────────────────


def test_by_state_counts_each_state_correctly():
    records = [
        _rec(exec_id=f"EXEC-2026042700000000000{i}-aaaaaa", state=s)
        for i, s in enumerate([
            ExecutionState.LANDED.value,
            ExecutionState.LANDED.value,
            ExecutionState.PR_OPEN.value,
            ExecutionState.ABORTED.value,
            ExecutionState.FAILED.value,
            ExecutionState.ASKING.value,
        ])
    ]
    m = compute_metrics(records)
    assert m.by_state["LANDED"] == 2
    assert m.by_state["PR_OPEN"] == 1
    assert m.by_state["ABORTED"] == 1
    assert m.by_state["FAILED"] == 1
    assert m.by_state["ASKING"] == 1
    assert m.by_state["INIT"] == 0


# ─── 3. Pass rate ────────────────────────────────────────────────────


def test_pass_rate_treats_landed_and_pr_open_as_pass():
    """PR_OPEN counts because the executor has produced a
    reviewable artifact; whether the human merges is out-of-scope."""
    records = [
        _rec(exec_id="EXEC-20260427T120000000001-aaaaaa", state="LANDED"),
        _rec(exec_id="EXEC-20260427T120000000002-aaaaaa", state="PR_OPEN"),
        _rec(exec_id="EXEC-20260427T120000000003-aaaaaa", state="FAILED"),
        _rec(exec_id="EXEC-20260427T120000000004-aaaaaa", state="ABORTED"),
    ]
    m = compute_metrics(records)
    # 2 passing / 4 total = 0.5
    assert m.pass_rate == 0.5


def test_pass_rate_zero_when_only_failures():
    records = [
        _rec(exec_id="EXEC-20260427T120000000001-aaaaaa", state="FAILED"),
        _rec(exec_id="EXEC-20260427T120000000002-aaaaaa", state="ABORTED"),
    ]
    m = compute_metrics(records)
    assert m.pass_rate == 0.0


def test_pass_rate_one_when_all_pass():
    records = [
        _rec(exec_id="EXEC-20260427T120000000001-aaaaaa", state="LANDED"),
        _rec(exec_id="EXEC-20260427T120000000002-aaaaaa", state="LANDED"),
    ]
    m = compute_metrics(records)
    assert m.pass_rate == 1.0


# ─── 4. Duration (median + p95) ─────────────────────────────────────


def test_durations_computed_from_started_finished_pair():
    """1 record at 60s, 1 at 90s, 1 at 120s → median=90, p95=120 (small N)."""
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            started_at="2026-04-27T12:00:00Z",
            finished_at="2026-04-27T12:01:00Z",  # 60s
        ),
        _rec(
            exec_id="EXEC-20260427T120000000002-aaaaaa",
            started_at="2026-04-27T12:00:00Z",
            finished_at="2026-04-27T12:01:30Z",  # 90s
        ),
        _rec(
            exec_id="EXEC-20260427T120000000003-aaaaaa",
            started_at="2026-04-27T12:00:00Z",
            finished_at="2026-04-27T12:02:00Z",  # 120s
        ),
    ]
    m = compute_metrics(records)
    assert m.completed_count == 3
    assert m.median_duration_sec == 90.0
    # p95 with 3 samples → nearest-rank picks last
    assert m.p95_duration_sec == 120.0


def test_unfinished_records_excluded_from_duration():
    """An audit with finished_at='' must not contribute to the
    duration set (it's still in flight)."""
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            state="ASKING",
            started_at="2026-04-27T12:00:00Z",
            finished_at="",  # still running
        ),
        _rec(
            exec_id="EXEC-20260427T120000000002-aaaaaa",
            started_at="2026-04-27T12:00:00Z",
            finished_at="2026-04-27T12:01:00Z",
        ),
    ]
    m = compute_metrics(records)
    assert m.completed_count == 1
    assert m.median_duration_sec == 60.0


def test_negative_duration_skipped():
    """If finished_at < started_at (clock skew), skip rather than
    report a meaningless negative duration."""
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            started_at="2026-04-27T12:01:00Z",
            finished_at="2026-04-27T12:00:00Z",  # before start
        ),
    ]
    m = compute_metrics(records)
    assert m.completed_count == 0
    assert m.median_duration_sec is None


def test_unparseable_timestamp_treated_as_zero():
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            started_at="not-a-timestamp",
            finished_at="2026-04-27T12:01:00Z",
        ),
    ]
    m = compute_metrics(records)
    # Negative guard: 0 - parsed-finished is negative; excluded
    assert m.completed_count == 0


# ─── 5. Recent failures ─────────────────────────────────────────────


def test_recent_failures_only_aborted_and_failed():
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            state="LANDED",
            abort_reason="",  # success doesn't get listed
        ),
        _rec(
            exec_id="EXEC-20260427T120000000002-aaaaaa",
            state="FAILED",
            abort_reason="planner: minimax 503",
        ),
        _rec(
            exec_id="EXEC-20260427T120000000003-aaaaaa",
            state="ABORTED",
            abort_reason="cancelled by Kogami",
        ),
    ]
    m = compute_metrics(records)
    assert len(m.recent_failures) == 2
    states = {f.state for f in m.recent_failures}
    assert states == {"FAILED", "ABORTED"}


def test_recent_failures_capped_by_limit():
    records = [
        _rec(
            exec_id=f"EXEC-2026042712000000000{i}-aaaaaa",
            state="FAILED",
            abort_reason=f"f{i}",
        )
        for i in range(8)
    ]
    m = compute_metrics(records, recent_failure_limit=3)
    assert len(m.recent_failures) == 3


def test_recent_failures_default_reason_when_blank():
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            state="FAILED",
            abort_reason="",
        ),
    ]
    m = compute_metrics(records)
    assert m.recent_failures[0].abort_reason == "(no reason recorded)"


# ─── 6. Backfill counter ────────────────────────────────────────────


def test_backfill_records_counted():
    records = [
        _rec(
            exec_id="EXEC-20260427T120000000001-aaaaaa",
            audit_source=AuditSource.BACKFILL,
            kind=ExecutionKind.BACKFILL,
        ),
        _rec(
            exec_id="EXEC-20260427T120000000002-aaaaaa",
            audit_source=AuditSource.LIVE,
        ),
    ]
    m = compute_metrics(records)
    assert m.backfill_count == 1


# ─── 7. JSON serialization ──────────────────────────────────────────


def test_metrics_to_json_round_trip_shape():
    records = [
        _rec(exec_id="EXEC-20260427T120000000001-aaaaaa", state="LANDED"),
        _rec(
            exec_id="EXEC-20260427T120000000002-aaaaaa",
            state="FAILED",
            abort_reason="planner crash",
        ),
    ]
    m = compute_metrics(records)
    payload = m.to_json()
    # Must be a JSON-serializable dict with expected top-level keys
    # P50-04 added failure_classification — required when produced
    # via compute_metrics (which is the only path tested here).
    assert set(payload.keys()) == {
        "total", "by_state", "pass_rate", "completed_count",
        "median_duration_sec", "p95_duration_sec",
        "recent_failures", "backfill_count",
        "failure_classification",
    }
    # by_state is itself a dict
    assert isinstance(payload["by_state"], dict)
    # recent_failures items are dicts (not RecentFailure objects)
    assert isinstance(payload["recent_failures"][0], dict)


def test_recent_failure_to_json_carries_all_fields():
    f = RecentFailure(
        exec_id="EXEC-X",
        proposal_id="PROP-X",
        state="FAILED",
        abort_reason="boom",
        finished_at="2026-04-27T13:00:00Z",
    )
    j = f.to_json()
    assert j["exec_id"] == "EXEC-X"
    assert j["proposal_id"] == "PROP-X"
    assert j["state"] == "FAILED"
    assert j["abort_reason"] == "boom"
    assert j["finished_at"] == "2026-04-27T13:00:00Z"


# ─── 8. Determinism ─────────────────────────────────────────────────


def test_state_keys_always_present_for_deterministic_dashboard():
    """Even if no record is in EDITING, the dashboard's bar chart
    needs the key present so it renders an empty column instead
    of disappearing."""
    m = compute_metrics([])
    for state in [
        "INIT", "PLANNING", "ASKING", "EDITING", "TESTING",
        "PR_OPEN", "LANDED", "ABORTED", "FAILED",
    ]:
        assert state in m.by_state


def test_by_state_keyset_does_not_grow_when_unknown_state_seen():
    """Future state machine additions should appear in the count
    without the old keys disappearing — guards against accidental
    schema drift in the dashboard."""
    rec = _rec(exec_id="EXEC-20260427T120000000001-aaaaaa", state="WEIRD_FUTURE_STATE")
    m = compute_metrics([rec])
    # Old keys still there
    for state in [
        "INIT", "PLANNING", "ASKING", "EDITING", "TESTING",
        "PR_OPEN", "LANDED", "ABORTED", "FAILED",
    ]:
        assert state in m.by_state
    # New key surfaced (defensive bucket)
    assert m.by_state["WEIRD_FUTURE_STATE"] == 1
