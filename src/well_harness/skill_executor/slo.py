"""SLO (Service Level Objective) status computation — feeds the
workbench dashboard's color-coded health indicator (P50-07).

Why: P50-02a's dashboard shows raw numbers — 47 executions, 73%
pass rate, etc. — but a reviewer has to interpret what's healthy.
P50-07 adds a single GREEN / YELLOW / RED / NO_DATA verdict so a
glance at the panel's summary line says "system is fine" or
"something needs attention".

What this is NOT:
  - A real SRE-grade SLO (no error budget tracking, no historical
    burn rate). The dashboard is a single-engineer tool, not a
    paging system.
  - Notifications / pages / alerts. The status is purely visual.
  - Time-windowed (e.g. "pass rate in last hour"). All thresholds
    apply to the lifetime aggregate. Future P50-08 may add
    rolling windows if the lifetime view turns out to be too coarse.

Default SLOs:
  - pass_rate >= 70% → GREEN
                50%-70% → YELLOW
                <50% → RED
  - active_failures_count (FAILED state) <= 2 → GREEN
                                          3-5 → YELLOW
                                          >5 → RED

Both can be overridden by passing custom `thresholds` to
compute_slo_status. NO_DATA verdict overrides everything when
total < `min_data_points` (default 5) — too few executions to
draw conclusions from.
"""

from __future__ import annotations

import dataclasses
import enum


class SLOSeverity(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    NO_DATA = "no_data"


@dataclasses.dataclass
class SLOThresholds:
    """Thresholds for the default SLO set. Override per-deployment
    by passing to compute_slo_status."""

    pass_rate_yellow: float = 0.70  # below this → YELLOW
    pass_rate_red: float = 0.50     # below this → RED
    failures_yellow: int = 3        # at or above → YELLOW
    failures_red: int = 6           # at or above → RED
    min_data_points: int = 5        # below this → NO_DATA


@dataclasses.dataclass
class SLOBreach:
    """One SLO whose actual value crossed a threshold."""

    slo: str
    severity: SLOSeverity
    actual: float
    threshold: float
    note: str

    def to_json(self) -> dict:
        return {
            "slo": self.slo,
            "severity": self.severity.value,
            "actual": self.actual,
            "threshold": self.threshold,
            "note": self.note,
        }


@dataclasses.dataclass
class SLOStatus:
    """Roll-up of all SLOs for one Metrics snapshot.

    `overall` is the WORST severity across all breaches:
      RED > YELLOW > GREEN > NO_DATA (no_data only when no data exists)
    """

    overall: SLOSeverity
    breaches: list[SLOBreach]
    thresholds: SLOThresholds

    def to_json(self) -> dict:
        return {
            "overall": self.overall.value,
            "breaches": [b.to_json() for b in self.breaches],
            "thresholds": dataclasses.asdict(self.thresholds),
        }


def compute_slo_status(
    metrics: object,
    *,
    thresholds: SLOThresholds | None = None,
) -> SLOStatus:
    """Evaluate every SLO against the given metrics. `metrics` is
    an instance of `Metrics` (passed as `object` to avoid an
    import cycle since metrics.py is going to import this module
    for the sidecar field).

    Empty / sparse data: if metrics.total < min_data_points,
    overall = NO_DATA regardless of pass_rate. The dashboard
    shouldn't sound the alarm on 1-2 failures — that's normal noise.
    """
    th = thresholds or SLOThresholds()
    breaches: list[SLOBreach] = []

    # Type-ducking access — metrics is `Metrics` but we don't import
    # to avoid a cycle. .total / .pass_rate / .by_state are part of
    # the Metrics public contract.
    total = getattr(metrics, "total", 0) or 0

    # NO_DATA short-circuit
    if total < th.min_data_points:
        return SLOStatus(
            overall=SLOSeverity.NO_DATA,
            breaches=[],
            thresholds=th,
        )

    # ── SLO 1: pass rate ──
    pass_rate = float(getattr(metrics, "pass_rate", 0.0) or 0.0)
    if pass_rate < th.pass_rate_red:
        breaches.append(
            SLOBreach(
                slo="pass_rate",
                severity=SLOSeverity.RED,
                actual=pass_rate,
                threshold=th.pass_rate_red,
                note=(
                    f"pass rate {pass_rate:.1%} below RED threshold "
                    f"{th.pass_rate_red:.1%} — system mostly failing"
                ),
            )
        )
    elif pass_rate < th.pass_rate_yellow:
        breaches.append(
            SLOBreach(
                slo="pass_rate",
                severity=SLOSeverity.YELLOW,
                actual=pass_rate,
                threshold=th.pass_rate_yellow,
                note=(
                    f"pass rate {pass_rate:.1%} below YELLOW threshold "
                    f"{th.pass_rate_yellow:.1%}"
                ),
            )
        )

    # ── SLO 2: lifetime failed count ──
    by_state = getattr(metrics, "by_state", {}) or {}
    failed_count = int(by_state.get("FAILED", 0) or 0)
    if failed_count >= th.failures_red:
        breaches.append(
            SLOBreach(
                slo="active_failures_count",
                severity=SLOSeverity.RED,
                actual=float(failed_count),
                threshold=float(th.failures_red),
                note=(
                    f"{failed_count} executions in FAILED state, "
                    f">= RED threshold {th.failures_red}"
                ),
            )
        )
    elif failed_count >= th.failures_yellow:
        breaches.append(
            SLOBreach(
                slo="active_failures_count",
                severity=SLOSeverity.YELLOW,
                actual=float(failed_count),
                threshold=float(th.failures_yellow),
                note=(
                    f"{failed_count} executions in FAILED state, "
                    f">= YELLOW threshold {th.failures_yellow}"
                ),
            )
        )

    overall = _worst_severity(breaches)
    return SLOStatus(overall=overall, breaches=breaches, thresholds=th)


def _worst_severity(breaches: list[SLOBreach]) -> SLOSeverity:
    """RED > YELLOW > GREEN. No breaches = GREEN."""
    if any(b.severity == SLOSeverity.RED for b in breaches):
        return SLOSeverity.RED
    if any(b.severity == SLOSeverity.YELLOW for b in breaches):
        return SLOSeverity.YELLOW
    return SLOSeverity.GREEN
