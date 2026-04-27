"""P50-08b — SLO transition history.

Locks down: record_transition appends only when the verdict
changes; load_history tolerates missing/corrupt files; the JSON
shape is stable for the dashboard contract; first-call GREEN is
silently absorbed but first-call YELLOW/RED does log.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from well_harness.skill_executor.slo import (
    SLOBreach,
    SLOSeverity,
    SLOStatus,
    SLOThresholds,
)
from well_harness.skill_executor.slo_history import (
    SLOTransition,
    history_path,
    load_history,
    record_transition,
)


# ─── Helpers ──────────────────────────────────────────────────────


@dataclasses.dataclass
class _FakeMetrics:
    total: int = 0
    pass_rate: float = 0.0
    pass_rate_recent: float | None = None
    recent_window_size: int = 20
    by_state: dict | None = None

    def __post_init__(self):
        if self.by_state is None:
            self.by_state = {}


def _status(severity: SLOSeverity, *, breaches=()):
    return SLOStatus(
        overall=severity,
        breaches=list(breaches),
        thresholds=SLOThresholds(),
    )


def _ts(*, t=0):
    """Sequential ISO timestamp generator for deterministic tests."""
    return f"2026-04-27T13:00:{t:02d}Z"


# ─── 1. First-call behavior ───────────────────────────────────────


def test_first_call_green_is_silent(tmp_path):
    """A brand-new deploy hitting GREEN on its first poll does NOT
    log a transition. A timeline entry should mean 'something
    changed' — initial GREEN is the boring case."""
    out = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.GREEN),
        metrics=_FakeMetrics(total=10, pass_rate=1.0),
    )
    assert out is None
    assert load_history(tmp_path) == []


def test_first_call_red_is_logged(tmp_path):
    """First sample is RED — that IS worth seeing on day-1.
    Suppress GREEN, not RED/YELLOW/NO_DATA."""
    out = record_transition(
        tmp_path,
        current_status=_status(
            SLOSeverity.RED,
            breaches=[
                SLOBreach(
                    slo="pass_rate",
                    severity=SLOSeverity.RED,
                    actual=0.3, threshold=0.5, note="x",
                )
            ],
        ),
        metrics=_FakeMetrics(
            total=10, pass_rate=0.3,
            by_state={"FAILED": 7, "LANDED": 3},
        ),
    )
    assert out is not None
    assert out.from_severity == "none"
    assert out.to_severity == "red"
    history = load_history(tmp_path)
    assert len(history) == 1
    assert history[0].to_severity == "red"


def test_first_call_yellow_is_logged(tmp_path):
    """Same logic for YELLOW — silence is reserved for GREEN."""
    out = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.YELLOW),
        metrics=_FakeMetrics(total=10, pass_rate=0.65),
    )
    assert out is not None
    assert out.to_severity == "yellow"


def test_first_call_no_data_is_logged(tmp_path):
    """NO_DATA on first sample is unusual but real (fresh deploy
    with <5 audits). Logging it gives the timeline its baseline."""
    out = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.NO_DATA),
        metrics=_FakeMetrics(total=2),
    )
    assert out is not None
    assert out.to_severity == "no_data"


# ─── 2. Steady state — no-op when severity unchanged ──────────────


def test_steady_state_does_not_bloat_log(tmp_path):
    """Six identical RED polls in a row → one log entry, not six."""
    status = _status(SLOSeverity.RED)
    metrics = _FakeMetrics(total=10, pass_rate=0.3)
    record_transition(tmp_path, current_status=status, metrics=metrics)
    for _ in range(5):
        out = record_transition(
            tmp_path, current_status=status, metrics=metrics,
        )
        assert out is None
    assert len(load_history(tmp_path)) == 1


# ─── 3. Real transitions ──────────────────────────────────────────


def test_green_to_red_logged(tmp_path):
    """Healthy → broken transition. Need to seed a non-GREEN first
    so the GREEN-suppression doesn't swallow our baseline."""
    # Seed: NO_DATA baseline
    record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.NO_DATA),
        metrics=_FakeMetrics(total=2),
    )
    # Recovery to GREEN — first GREEN AFTER a baseline IS logged
    out_green = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.GREEN),
        metrics=_FakeMetrics(total=10, pass_rate=1.0),
    )
    assert out_green is not None
    assert out_green.from_severity == "no_data"
    assert out_green.to_severity == "green"
    # Regression GREEN → RED
    out_red = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.RED),
        metrics=_FakeMetrics(total=10, pass_rate=0.3),
    )
    assert out_red is not None
    assert out_red.from_severity == "green"
    assert out_red.to_severity == "red"
    history = load_history(tmp_path)
    assert [t.to_severity for t in history] == ["no_data", "green", "red"]


def test_recovery_red_to_green_logged(tmp_path):
    """RED then back to GREEN gets two entries — the recovery is
    just as informative as the breach."""
    record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.RED),
        metrics=_FakeMetrics(total=10, pass_rate=0.3),
    )
    record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.GREEN),
        metrics=_FakeMetrics(total=20, pass_rate=0.95),
    )
    h = load_history(tmp_path)
    assert len(h) == 2
    assert h[0].to_severity == "red"
    assert h[1].to_severity == "green"
    assert h[1].from_severity == "red"


# ─── 4. Snapshot fields ───────────────────────────────────────────


def test_snapshot_captures_pass_rate_and_failed_count(tmp_path):
    out = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.RED),
        metrics=_FakeMetrics(
            total=50, pass_rate=0.4,
            pass_rate_recent=0.2, recent_window_size=20,
            by_state={"FAILED": 10, "LANDED": 20},
        ),
    )
    assert out.snapshot["total"] == 50
    assert out.snapshot["pass_rate"] == pytest.approx(0.4)
    assert out.snapshot["pass_rate_recent"] == pytest.approx(0.2)
    assert out.snapshot["recent_window_size"] == 20
    assert out.snapshot["failed_count"] == 10


def test_breach_slos_extracted_from_status(tmp_path):
    breaches = [
        SLOBreach(
            slo="pass_rate",
            severity=SLOSeverity.RED,
            actual=0.3, threshold=0.5, note="x",
        ),
        SLOBreach(
            slo="pass_rate_recent",
            severity=SLOSeverity.RED,
            actual=0.2, threshold=0.5, note="y",
        ),
    ]
    out = record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.RED, breaches=breaches),
        metrics=_FakeMetrics(total=10, pass_rate=0.3),
    )
    assert out.breach_slos == ["pass_rate", "pass_rate_recent"]


# ─── 5. JSONL persistence + reload round-trip ────────────────────


def test_round_trip_persistence(tmp_path):
    record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.RED),
        metrics=_FakeMetrics(total=10, pass_rate=0.3),
    )
    record_transition(
        tmp_path,
        current_status=_status(SLOSeverity.GREEN),
        metrics=_FakeMetrics(total=20, pass_rate=0.95),
    )
    # Reload from disk via a fresh load — no cache
    h = load_history(tmp_path)
    assert len(h) == 2
    # JSON round-trip
    p = history_path(tmp_path)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    parsed = [json.loads(l) for l in lines]
    assert parsed[0]["to_severity"] == "red"
    assert parsed[1]["to_severity"] == "green"


def test_load_tolerates_missing_file(tmp_path):
    """First-time read on a clean tmp dir → empty list, not error."""
    assert load_history(tmp_path) == []


def test_load_skips_corrupt_lines(tmp_path):
    """A truncated / malformed line shouldn't poison the rest of
    the log. The dashboard wants the recoverable 99% of entries."""
    p = history_path(tmp_path)
    p.write_text(
        json.dumps({"ts": "2026-04-27T13:00:00Z",
                    "from_severity": "none",
                    "to_severity": "red",
                    "breach_slos": [], "snapshot": {}}) + "\n"
        + "this is not valid json {{\n"
        + json.dumps({"ts": "2026-04-27T13:00:01Z",
                      "from_severity": "red",
                      "to_severity": "green",
                      "breach_slos": [], "snapshot": {}}) + "\n",
        encoding="utf-8",
    )
    h = load_history(tmp_path)
    assert len(h) == 2  # two parseable, one skipped
    assert h[0].to_severity == "red"
    assert h[1].to_severity == "green"


def test_load_with_limit_returns_tail(tmp_path):
    for sev in [SLOSeverity.RED, SLOSeverity.GREEN, SLOSeverity.YELLOW]:
        record_transition(
            tmp_path,
            current_status=_status(sev),
            metrics=_FakeMetrics(total=10, pass_rate=0.5),
        )
    # Limit=2 → newest 2
    h = load_history(tmp_path, limit=2)
    assert len(h) == 2
    assert h[0].to_severity == "green"
    assert h[1].to_severity == "yellow"


# ─── 6. JSON shape lockdown ───────────────────────────────────────


def test_transition_to_json_shape_stable():
    t = SLOTransition(
        ts="2026-04-27T13:00:00Z",
        from_severity="green",
        to_severity="red",
        breach_slos=["pass_rate"],
        snapshot={"total": 10},
    )
    j = t.to_json()
    assert set(j.keys()) == {
        "ts", "from_severity", "to_severity",
        "breach_slos", "snapshot",
    }


def test_transition_from_json_round_trip():
    j = {
        "ts": "2026-04-27T13:00:00Z",
        "from_severity": "yellow",
        "to_severity": "red",
        "breach_slos": ["pass_rate", "active_failures_count"],
        "snapshot": {"total": 50, "pass_rate": 0.4},
    }
    t = SLOTransition.from_json(j)
    assert t.to_severity == "red"
    assert t.snapshot["total"] == 50
    assert t.to_json() == j
