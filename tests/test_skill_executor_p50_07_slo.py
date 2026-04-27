"""P50-07 — SLO status computation.

Locks down: compute_slo_status produces the expected GREEN /
YELLOW / RED / NO_DATA verdict based on pass_rate and
active_failures_count, threshold overrides work, and the JSON
shape is stable for the dashboard contract.
"""

from __future__ import annotations

import dataclasses

import pytest

from well_harness.skill_executor.slo import (
    SLOBreach,
    SLOSeverity,
    SLOStatus,
    SLOThresholds,
    compute_slo_status,
)


# Stand-in for Metrics so this test stays a pure unit test of
# slo.py — we don't need to drag the audit-list pipeline in.
@dataclasses.dataclass
class _FakeMetrics:
    total: int = 0
    pass_rate: float = 0.0
    by_state: dict | None = None

    def __post_init__(self):
        if self.by_state is None:
            self.by_state = {}


# ─── 1. NO_DATA short-circuit ─────────────────────────────────────


def test_zero_total_returns_no_data():
    """No audits at all → NO_DATA, never GREEN. A fresh deploy
    shouldn't claim everything is fine."""
    status = compute_slo_status(_FakeMetrics(total=0, pass_rate=0.0))
    assert status.overall == SLOSeverity.NO_DATA
    assert status.breaches == []


def test_below_min_data_points_returns_no_data():
    """Even with a 0% pass rate, < min_data_points runs is too
    little signal to alarm on."""
    status = compute_slo_status(
        _FakeMetrics(total=4, pass_rate=0.0, by_state={"FAILED": 4})
    )
    # Default min_data_points=5 → still NO_DATA
    assert status.overall == SLOSeverity.NO_DATA
    assert status.breaches == []


def test_min_data_points_threshold_is_inclusive():
    """At total == min_data_points, NO_DATA short-circuit is OFF
    and the real SLOs apply."""
    # 5 runs, 5 passing → GREEN
    status = compute_slo_status(
        _FakeMetrics(total=5, pass_rate=1.0, by_state={"LANDED": 5})
    )
    assert status.overall == SLOSeverity.GREEN


# ─── 2. pass_rate SLO ─────────────────────────────────────────────


def test_pass_rate_above_yellow_is_green():
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.9, by_state={"LANDED": 9, "FAILED": 1})
    )
    assert status.overall == SLOSeverity.GREEN
    assert status.breaches == []


def test_pass_rate_at_yellow_threshold_is_green():
    """0.70 is the yellow boundary; AT 0.70 we're still healthy.
    The threshold semantic is `<` not `<=`."""
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.70, by_state={"LANDED": 7, "FAILED": 1})
    )
    # 1 FAILED stays under the failure SLO YELLOW at 3
    assert status.overall == SLOSeverity.GREEN


def test_pass_rate_just_below_yellow_is_yellow():
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.69, by_state={"LANDED": 6, "FAILED": 1})
    )
    assert status.overall == SLOSeverity.YELLOW
    pass_rate_breaches = [b for b in status.breaches if b.slo == "pass_rate"]
    assert len(pass_rate_breaches) == 1
    assert pass_rate_breaches[0].severity == SLOSeverity.YELLOW
    assert pass_rate_breaches[0].actual == pytest.approx(0.69)


def test_pass_rate_just_below_red_is_red():
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.49, by_state={"LANDED": 4, "FAILED": 1})
    )
    assert status.overall == SLOSeverity.RED
    pass_rate_breaches = [b for b in status.breaches if b.slo == "pass_rate"]
    assert len(pass_rate_breaches) == 1
    assert pass_rate_breaches[0].severity == SLOSeverity.RED


def test_pass_rate_zero_is_red():
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.0, by_state={"FAILED": 1})
    )
    # pass_rate breach is RED. failure count (1) is GREEN.
    assert status.overall == SLOSeverity.RED


# ─── 3. active_failures_count SLO ────────────────────────────────


def test_few_failures_is_green():
    """2 FAILED is still healthy (default failures_yellow=3)."""
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.8, by_state={"LANDED": 8, "FAILED": 2})
    )
    assert status.overall == SLOSeverity.GREEN


def test_failures_at_yellow_threshold_is_yellow():
    """3 FAILED hits the YELLOW threshold."""
    status = compute_slo_status(
        _FakeMetrics(total=20, pass_rate=0.85, by_state={"LANDED": 17, "FAILED": 3})
    )
    assert status.overall == SLOSeverity.YELLOW
    fail_breaches = [b for b in status.breaches if b.slo == "active_failures_count"]
    assert len(fail_breaches) == 1
    assert fail_breaches[0].severity == SLOSeverity.YELLOW
    assert fail_breaches[0].actual == 3.0


def test_failures_at_red_threshold_is_red():
    """6 FAILED hits the RED threshold."""
    status = compute_slo_status(
        _FakeMetrics(total=20, pass_rate=0.7, by_state={"LANDED": 14, "FAILED": 6})
    )
    assert status.overall == SLOSeverity.RED
    fail_breaches = [b for b in status.breaches if b.slo == "active_failures_count"]
    assert len(fail_breaches) == 1
    assert fail_breaches[0].severity == SLOSeverity.RED


def test_no_failed_state_is_green():
    """by_state with no FAILED key → 0 failures → GREEN on that SLO."""
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=1.0, by_state={"LANDED": 10})
    )
    assert status.overall == SLOSeverity.GREEN


# ─── 4. Multiple breaches → worst severity wins ──────────────────


def test_red_pass_rate_with_yellow_failures_is_red():
    """Worst-of: RED pass_rate and YELLOW failures → overall RED."""
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.3, by_state={"LANDED": 3, "FAILED": 4})
    )
    assert status.overall == SLOSeverity.RED
    # Both breaches captured for the dashboard's expanded view
    slos = {b.slo for b in status.breaches}
    assert slos == {"pass_rate", "active_failures_count"}


def test_yellow_pass_rate_with_red_failures_is_red():
    """Reverse: YELLOW pass_rate, RED failures → RED."""
    status = compute_slo_status(
        _FakeMetrics(total=20, pass_rate=0.6, by_state={"LANDED": 12, "FAILED": 8})
    )
    assert status.overall == SLOSeverity.RED


def test_two_yellow_breaches_stay_yellow():
    """Worst severity stops at YELLOW if no breach is RED."""
    status = compute_slo_status(
        _FakeMetrics(total=20, pass_rate=0.65, by_state={"LANDED": 13, "FAILED": 4})
    )
    assert status.overall == SLOSeverity.YELLOW
    assert len(status.breaches) == 2
    assert all(b.severity == SLOSeverity.YELLOW for b in status.breaches)


# ─── 5. Threshold overrides ──────────────────────────────────────


def test_custom_thresholds_can_tighten():
    """A stricter pass_rate_yellow flips an otherwise GREEN system
    to YELLOW. Lets ops dial the dashboard for their tolerance."""
    strict = SLOThresholds(pass_rate_yellow=0.95, pass_rate_red=0.80)
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.85, by_state={"LANDED": 8, "FAILED": 1}),
        thresholds=strict,
    )
    # 0.85 < strict yellow=0.95 but >= strict red=0.80 → YELLOW
    assert status.overall == SLOSeverity.YELLOW


def test_custom_thresholds_can_relax():
    """Lower min_data_points lets the dashboard say something on
    smaller deployments."""
    relaxed = SLOThresholds(min_data_points=2)
    status = compute_slo_status(
        _FakeMetrics(total=2, pass_rate=1.0, by_state={"LANDED": 2}),
        thresholds=relaxed,
    )
    assert status.overall == SLOSeverity.GREEN


# ─── 6. Defensive missing-attribute handling ─────────────────────


def test_missing_attributes_treated_as_zero():
    """A bare object with no Metrics attrs → zero total → NO_DATA.
    Makes the type-ducking access safe for partial Metrics shapes
    (forward-compatibility with future Metrics fields)."""
    class Empty:
        pass
    status = compute_slo_status(Empty())
    assert status.overall == SLOSeverity.NO_DATA


# ─── 7. JSON serialization shape ────────────────────────────────


def test_json_shape_is_stable():
    """Front-end consumes status.to_json(); locking down the keys
    so the dashboard contract doesn't drift."""
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.4, by_state={"FAILED": 6, "LANDED": 4})
    )
    j = status.to_json()
    assert set(j.keys()) == {"overall", "breaches", "thresholds"}
    assert j["overall"] in {"green", "yellow", "red", "no_data"}
    assert isinstance(j["breaches"], list)
    for b in j["breaches"]:
        assert set(b.keys()) == {
            "slo", "severity", "actual", "threshold", "note"
        }
    # Thresholds dict mirrors the dataclass fields
    assert set(j["thresholds"].keys()) == {
        "pass_rate_yellow", "pass_rate_red",
        "failures_yellow", "failures_red",
        "min_data_points",
        # P50-08a: rolling-window pass_rate thresholds
        "recent_pass_rate_yellow", "recent_pass_rate_red",
    }


def test_no_data_json_has_no_breaches():
    j = compute_slo_status(_FakeMetrics(total=0)).to_json()
    assert j["overall"] == "no_data"
    assert j["breaches"] == []


def test_breach_note_mentions_threshold():
    """The note text should help an operator understand WHY the
    SLO breached. Lock down that the threshold value is in there."""
    status = compute_slo_status(
        _FakeMetrics(total=10, pass_rate=0.3, by_state={"LANDED": 3, "FAILED": 1})
    )
    pass_rate_breach = next(
        b for b in status.breaches if b.slo == "pass_rate"
    )
    # Default RED threshold is 50%
    assert "50" in pass_rate_breach.note or "0.5" in pass_rate_breach.note


# ─── 8. SLOBreach dataclass round-trip ──────────────────────────


def test_slo_breach_to_json():
    b = SLOBreach(
        slo="pass_rate",
        severity=SLOSeverity.RED,
        actual=0.3,
        threshold=0.5,
        note="pass rate 30% below RED threshold 50%",
    )
    j = b.to_json()
    assert j == {
        "slo": "pass_rate",
        "severity": "red",
        "actual": 0.3,
        "threshold": 0.5,
        "note": "pass rate 30% below RED threshold 50%",
    }
