"""P50-08a — rolling-window pass_rate (last N runs).

Locks down: compute_metrics computes a recent-window slice when
total >= window_size; compute_slo_status raises a pass_rate_recent
breach when the recent window degrades even though lifetime is
healthy. The "lifetime green, recent red" scenario is the entire
reason this slice exists — without it, a system regression on the
freshest runs gets averaged out by old success.
"""

from __future__ import annotations

import dataclasses

import pytest

from well_harness.skill_executor.metrics import compute_metrics
from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    AuditSource,
    ExecutionKind,
    ExecutionRecord,
    PlannedChange,
)
from well_harness.skill_executor.slo import (
    SLOSeverity,
    SLOThresholds,
    compute_slo_status,
)
from well_harness.skill_executor.states import ExecutionState


# Stand-in Metrics for direct slo.py unit tests
@dataclasses.dataclass
class _FakeMetrics:
    total: int = 0
    pass_rate: float = 0.0
    by_state: dict | None = None
    pass_rate_recent: float | None = None
    recent_window_size: int = 20

    def __post_init__(self):
        if self.by_state is None:
            self.by_state = {}


def _rec(
    exec_id: str,
    *,
    state: str = ExecutionState.LANDED.value,
    started_at: str = "2026-04-27T12:00:00Z",
    finished_at: str = "2026-04-27T12:01:00Z",
) -> ExecutionRecord:
    return ExecutionRecord(
        exec_id=exec_id,
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-x",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at=started_at,
        finished_at=finished_at,
        state=state,
        executor_version="0.1-test",
        plan=PlannedChange(rationale="x", file_edits=[]),
    )


# ─── 1. compute_metrics computes the window correctly ──────────────


def test_window_below_threshold_leaves_recent_none():
    """5 records < default window 20 → pass_rate_recent stays None.
    Avoids a duplicate SLO when lifetime IS the recent dataset."""
    records = [
        _rec(f"EXEC-20260427T1200000{i:05d}-aaaaaa")
        for i in range(5)
    ]
    m = compute_metrics(records)
    assert m.pass_rate_recent is None
    assert m.recent_total == 0


def test_window_at_threshold_evaluates():
    """At total == window_size, pass_rate_recent is populated."""
    records = [
        _rec(f"EXEC-20260427T1200000{i:05d}-aaaaaa")
        for i in range(20)
    ]
    m = compute_metrics(records)
    assert m.pass_rate_recent == 1.0
    assert m.recent_total == 20
    assert m.recent_passing == 20


def test_window_takes_newest_records_only():
    """Records arrive newest-first (list_audits contract). Window
    must use records[:N], NOT the tail. Lifetime can be 100% while
    the newest 20 are 0% — the entire point of this slice."""
    # 100 records: first 20 (newest) are FAILED, rest LANDED → 80% lifetime
    # but recent 20 = 0%.
    failed_ids = [
        _rec(
            f"EXEC-20260427T9{i:011d}-aaaaaa",
            state=ExecutionState.FAILED.value,
        )
        for i in range(20)
    ]
    landed_ids = [
        _rec(
            f"EXEC-20260427T1{i:011d}-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
        for i in range(80)
    ]
    # Caller passes newest-first: failed first, then landed
    m = compute_metrics(failed_ids + landed_ids)
    assert m.total == 100
    assert m.pass_rate == 0.8  # lifetime
    assert m.pass_rate_recent == 0.0  # newest 20 all failed
    assert m.recent_passing == 0
    assert m.recent_total == 20


def test_custom_window_size_kwarg():
    """recent_window_size is configurable per-call."""
    records = [
        _rec(
            f"EXEC-20260427T1200000{i:05d}-aaaaaa",
            state=ExecutionState.LANDED.value,
        )
        for i in range(10)
    ]
    m = compute_metrics(records, recent_window_size=5)
    assert m.recent_window_size == 5
    assert m.recent_total == 5
    assert m.pass_rate_recent == 1.0


# ─── 2. SLO triggers on recent regression ─────────────────────────


def test_lifetime_green_but_recent_red_overall_red():
    """Lifetime healthy, recent disaster → overall RED via the new
    pass_rate_recent SLO. This is the headline scenario — without
    P50-08a the dashboard would say GREEN while the system is
    actively burning."""
    status = compute_slo_status(
        _FakeMetrics(
            total=100,
            pass_rate=0.85,  # lifetime GREEN
            by_state={"LANDED": 85, "FAILED": 15},
            pass_rate_recent=0.30,  # recent RED
            recent_window_size=20,
        )
    )
    assert status.overall == SLOSeverity.RED
    recent_breaches = [b for b in status.breaches if b.slo == "pass_rate_recent"]
    assert len(recent_breaches) == 1
    assert recent_breaches[0].severity == SLOSeverity.RED


def test_lifetime_green_recent_yellow_overall_yellow():
    """Mild recent dip → YELLOW overall."""
    status = compute_slo_status(
        _FakeMetrics(
            total=50,
            pass_rate=0.85,
            by_state={"LANDED": 42, "FAILED": 5},
            pass_rate_recent=0.65,
            recent_window_size=20,
        )
    )
    assert status.overall == SLOSeverity.YELLOW
    recent = next(b for b in status.breaches if b.slo == "pass_rate_recent")
    assert recent.severity == SLOSeverity.YELLOW


def test_recent_recovery_keeps_lifetime_breach_visible():
    """Reverse: lifetime degraded but recent runs are recovering.
    Lifetime SLO still fires (truth in advertising) — the recent
    SLO does NOT mask it. Both surfaces matter for diagnosis."""
    status = compute_slo_status(
        _FakeMetrics(
            total=50,
            pass_rate=0.40,  # lifetime RED
            by_state={"LANDED": 20, "FAILED": 25},
            pass_rate_recent=0.95,  # recent GREEN
            recent_window_size=20,
        )
    )
    # Overall is RED because lifetime breach is RED. recent is GREEN
    # so it does NOT contribute a breach.
    assert status.overall == SLOSeverity.RED
    slos = {b.slo for b in status.breaches}
    assert "pass_rate" in slos
    assert "pass_rate_recent" not in slos


def test_under_window_skips_recent_slo():
    """When total < window_size, compute_metrics leaves
    pass_rate_recent=None. SLO must skip it entirely — not
    treat None as 0%."""
    status = compute_slo_status(
        _FakeMetrics(
            total=10,
            pass_rate=0.9,
            by_state={"LANDED": 9, "FAILED": 1},
            pass_rate_recent=None,
            recent_window_size=20,
        )
    )
    assert status.overall == SLOSeverity.GREEN
    assert all(b.slo != "pass_rate_recent" for b in status.breaches)


# ─── 3. Threshold overrides for the recent window ─────────────────


def test_custom_recent_thresholds_can_be_stricter():
    """A deploy worried about regressions can demand a higher
    recent pass_rate without changing the lifetime threshold."""
    th = SLOThresholds(
        pass_rate_yellow=0.70, pass_rate_red=0.50,
        recent_pass_rate_yellow=0.95, recent_pass_rate_red=0.85,
    )
    status = compute_slo_status(
        _FakeMetrics(
            total=50,
            pass_rate=0.85,
            by_state={"LANDED": 42, "FAILED": 5},
            pass_rate_recent=0.90,  # under strict yellow=0.95
            recent_window_size=20,
        ),
        thresholds=th,
    )
    # lifetime 0.85 is above default yellow=0.70 → no lifetime breach
    # recent 0.90 is below custom yellow=0.95 → YELLOW breach
    assert status.overall == SLOSeverity.YELLOW
    recent = next(b for b in status.breaches if b.slo == "pass_rate_recent")
    assert recent.severity == SLOSeverity.YELLOW


# ─── 4. JSON shape additions ──────────────────────────────────────


def test_metrics_to_json_has_recent_window_block():
    records = [
        _rec(
            f"EXEC-20260427T1200000{i:05d}-aaaaaa",
            state=ExecutionState.LANDED.value if i < 15 else ExecutionState.FAILED.value,
        )
        for i in range(20)
    ]
    j = compute_metrics(records).to_json()
    assert "recent_window" in j
    rw = j["recent_window"]
    assert set(rw.keys()) == {
        "pass_rate_recent", "window_size", "passing", "total",
    }
    assert rw["window_size"] == 20
    assert rw["total"] == 20
    # 15 LANDED + 5 FAILED → 75% recent
    assert rw["passing"] == 15
    assert rw["pass_rate_recent"] == pytest.approx(0.75)


def test_metrics_to_json_recent_window_when_under_threshold():
    """Under-windowed → block still present, pass_rate_recent=null."""
    records = [
        _rec(f"EXEC-20260427T1200000{i:05d}-aaaaaa")
        for i in range(3)
    ]
    j = compute_metrics(records).to_json()
    assert j["recent_window"]["pass_rate_recent"] is None
    assert j["recent_window"]["total"] == 0


def test_thresholds_dict_has_recent_keys():
    j = compute_slo_status(_FakeMetrics(total=0)).to_json()
    assert "recent_pass_rate_yellow" in j["thresholds"]
    assert "recent_pass_rate_red" in j["thresholds"]
