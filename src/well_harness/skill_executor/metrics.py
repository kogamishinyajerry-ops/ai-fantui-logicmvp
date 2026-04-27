"""Aggregate metrics over skill_executor audits — feeds the
workbench observability panel (P50-02).

Reads ExecutionRecord lists, returns a typed Metrics dataclass.
Pure function, no IO. The HTTP layer (demo_server) is responsible
for getting audits via list_audits() and serializing the result.

What we compute:
  - total                count of all audits
  - by_state             count per ExecutionState (9 keys)
  - pass_rate            (LANDED + PR_OPEN) / total
  - completed_count      audits with finished_at populated
  - median_duration_sec  median time started_at → finished_at
  - p95_duration_sec     95th percentile of the same
  - recent_failures      last N FAILED/ABORTED with abort_reason
  - backfill_count       audit_source=backfill records

Why not Prometheus / OpenMetrics: this is workbench-internal
visibility for one engineer's local view. A Prometheus exporter
would be a separate slice (P50-02b) that exposes the same
computations through /metrics for ops tooling. Keeping the
internal dashboard JSON-shaped + Python-typed makes the
front-end code straightforward.

Why durations from started_at/finished_at instead of monotonic
clocks: started_at is the audit's authoritative timestamp; if a
crashed/cancelled audit never set finished_at, we just exclude
it from the duration set. Better to under-report than to fake
durations from log timestamps.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from typing import Iterable

from well_harness.skill_executor.models import ExecutionRecord
from well_harness.skill_executor.states import ExecutionState


# Order matters for deterministic JSON output. Mirrors the state
# machine declaration so the dashboard renders chronologically.
_ALL_STATES = (
    ExecutionState.INIT.value,
    ExecutionState.PLANNING.value,
    # P49-02a — sits between PLANNING and ASKING
    ExecutionState.GOVERNANCE_HOLD.value,
    ExecutionState.ASKING.value,
    ExecutionState.EDITING.value,
    ExecutionState.TESTING.value,
    ExecutionState.PR_OPEN.value,
    ExecutionState.LANDED.value,
    ExecutionState.ABORTED.value,
    ExecutionState.FAILED.value,
)


# States we treat as a "win" for pass_rate purposes. PR_OPEN
# counts as a pass because the executor produced a reviewable PR;
# whether the human merges it is outside the executor's scope.
_PASSING_STATES = frozenset({
    ExecutionState.LANDED.value,
    ExecutionState.PR_OPEN.value,
})


@dataclasses.dataclass
class RecentFailure:
    exec_id: str
    proposal_id: str
    state: str
    abort_reason: str
    finished_at: str

    def to_json(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Metrics:
    total: int
    by_state: dict[str, int]
    pass_rate: float
    completed_count: int
    median_duration_sec: float | None
    p95_duration_sec: float | None
    recent_failures: list[RecentFailure]
    backfill_count: int
    # P50-04: classified failure aggregate. Optional so older
    # callers that only read the existing fields keep working.
    # Type is `object` to avoid an import cycle (failure_classifier
    # imports from metrics for RecentFailure).
    failure_classification: object | None = None
    # P50-07: SLO verdict over the same dataset. Optional so the
    # dataclass stays back-compat with callers that only read pre-
    # P50-07 fields. Type is `object` to avoid an import cycle.
    slo_status: object | None = None
    # P50-08a: rolling window over the most recent N executions.
    # `pass_rate_recent` is None when total < recent_window_size
    # (not enough fresh signal). Lets the SLO catch a recent
    # regression even when the lifetime pass_rate is still healthy
    # — e.g. 200 runs at 90% lifetime but the last 20 are 30%.
    pass_rate_recent: float | None = None
    recent_window_size: int = 0
    recent_passing: int = 0
    recent_total: int = 0

    def to_json(self) -> dict:
        out = {
            "total": self.total,
            "by_state": dict(self.by_state),
            "pass_rate": self.pass_rate,
            "completed_count": self.completed_count,
            "median_duration_sec": self.median_duration_sec,
            "p95_duration_sec": self.p95_duration_sec,
            "recent_failures": [f.to_json() for f in self.recent_failures],
            "backfill_count": self.backfill_count,
        }
        if self.failure_classification is not None:
            out["failure_classification"] = (
                self.failure_classification.to_json()
            )
        if self.slo_status is not None:
            out["slo_status"] = self.slo_status.to_json()
        # P50-08a: rolling-window block. Always emitted (even when
        # under-windowed → null pass_rate) so the frontend can
        # render the "last N runs" eyebrow without conditional
        # shape checks.
        out["recent_window"] = {
            "pass_rate_recent": self.pass_rate_recent,
            "window_size": self.recent_window_size,
            "passing": self.recent_passing,
            "total": self.recent_total,
        }
        return out


def compute_metrics(
    records: Iterable[ExecutionRecord],
    *,
    recent_failure_limit: int = 5,
    recent_window_size: int = 20,
) -> Metrics:
    """Aggregate the audit list into a Metrics dataclass.

    `records` is consumed once — caller must pass a list if they
    want to iterate again afterward.

    Empty input produces all-zero metrics with no failures (NOT a
    None or error). The dashboard needs to render even when no
    executions have happened yet.
    """
    records = list(records)

    by_state: dict[str, int] = {s: 0 for s in _ALL_STATES}
    durations_sec: list[float] = []
    backfill_count = 0
    failures: list[RecentFailure] = []

    for r in records:
        # Defensive: unknown states surface as their own bucket so
        # we don't silently drop them. Future state-machine
        # additions will appear in the dashboard the moment a real
        # audit uses them.
        by_state[r.state] = by_state.get(r.state, 0) + 1

        if r.audit_source == "backfill" or (
            hasattr(r.audit_source, "value")
            and r.audit_source.value == "backfill"
        ):
            backfill_count += 1

        # Duration: only meaningful when both timestamps populated
        # AND parseable. Backfill audits typically have
        # started_at == finished_at; they contribute 0 to the
        # duration set, which is correct (they didn't actually run).
        if r.started_at and r.finished_at:
            start_s = _parse_iso_to_seconds(r.started_at)
            finish_s = _parse_iso_to_seconds(r.finished_at)
            if start_s is not None and finish_s is not None:
                d = finish_s - start_s
                if d >= 0:  # guard against clock skew
                    durations_sec.append(d)

        # Failure list — only ABORTED/FAILED with a reason
        if r.state in (
            ExecutionState.ABORTED.value,
            ExecutionState.FAILED.value,
        ):
            failures.append(
                RecentFailure(
                    exec_id=r.exec_id,
                    proposal_id=r.proposal_id,
                    state=r.state,
                    abort_reason=r.abort_reason or "(no reason recorded)",
                    finished_at=r.finished_at or "",
                )
            )

    total = len(records)
    passing = sum(by_state.get(s, 0) for s in _PASSING_STATES)
    pass_rate = (passing / total) if total else 0.0

    completed_count = len(durations_sec)
    median_duration = _median(durations_sec) if durations_sec else None
    p95_duration = _percentile(durations_sec, 0.95) if durations_sec else None

    # list_audits returns newest-first. Take the most recent N
    # failures so the panel shows the freshest pain.
    recent_failures = failures[:recent_failure_limit]

    # P50-04: classify failures for the dashboard's "what's been
    # breaking" panel. Lazy import avoids a cycle (failure_classifier
    # imports RecentFailure from this module). Classification is over
    # ALL failures in the dataset, not just the recent_failures slice
    # — so the bucket counts reflect the true population.
    from well_harness.skill_executor.failure_classifier import (
        classify_failures,
    )
    all_failures = [
        RecentFailure(
            exec_id=r.exec_id,
            proposal_id=r.proposal_id,
            state=r.state,
            abort_reason=r.abort_reason or "",
            finished_at=r.finished_at or "",
        )
        for r in records
        if r.state in (
            ExecutionState.ABORTED.value,
            ExecutionState.FAILED.value,
        )
    ]
    classification = classify_failures(all_failures)

    # P50-08a: rolling-window pass_rate over the most recent N
    # records. Caller passes records in newest-first order
    # (list_audits guarantees this); we just take the head slice.
    # Window only meaningful once total >= window_size — below
    # that, lifetime IS the recent dataset, so we leave
    # pass_rate_recent=None to suppress a duplicate SLO.
    pass_rate_recent: float | None = None
    recent_passing = 0
    recent_total = 0
    if total >= recent_window_size and recent_window_size > 0:
        recent_slice = records[:recent_window_size]
        recent_total = len(recent_slice)
        recent_passing = sum(
            1 for r in recent_slice if r.state in _PASSING_STATES
        )
        pass_rate_recent = (
            recent_passing / recent_total if recent_total else 0.0
        )

    metrics = Metrics(
        total=total,
        by_state=by_state,
        pass_rate=pass_rate,
        completed_count=completed_count,
        median_duration_sec=median_duration,
        p95_duration_sec=p95_duration,
        recent_failures=recent_failures,
        backfill_count=backfill_count,
        failure_classification=classification,
        pass_rate_recent=pass_rate_recent,
        recent_window_size=recent_window_size,
        recent_passing=recent_passing,
        recent_total=recent_total,
    )

    # P50-07: compute SLO verdict over the assembled metrics. Lazy
    # import sidesteps the cycle (slo.py reads Metrics attributes
    # but doesn't import the class). Done after Metrics is built so
    # slo can read .total/.pass_rate/.by_state by attribute.
    from well_harness.skill_executor.slo import compute_slo_status
    metrics.slo_status = compute_slo_status(metrics)

    return metrics


# ─── Helpers ───────────────────────────────────────────────────────


def _parse_iso_to_seconds(iso_str: str) -> float | None:
    """ISO 8601 → POSIX seconds. Tolerates the trailing 'Z' that
    audit timestamps use. Returns None on parse failure so the
    caller can skip the record entirely (don't fake a 1970 epoch
    delta into the metrics)."""
    if not iso_str:
        return None
    s = iso_str.strip()
    # datetime.fromisoformat doesn't handle 'Z' until 3.11; for
    # broader compat we substitute manually.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _median(values: list[float]) -> float:
    """50th percentile. Single-pass median for small lists; we
    expect <1000 audits in practice."""
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def _percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile. Matches numpy's default
    'lower' interpolation for small N."""
    if not values:
        return 0.0
    s = sorted(values)
    # Index = ceil(p * N) - 1, clamped
    idx = max(0, min(len(s) - 1, int(p * len(s))))
    return s[idx]
