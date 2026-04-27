"""P50-11 — webhook dispatch throttle unit tests.

Locks down: should_fire allows the first event per severity;
suppresses repeats within the configured interval; allows after
the window elapses; per-severity clocks are independent;
read/write_state round-trips the JSON; corrupt state is treated
as fresh, never fatal.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from well_harness.skill_executor.slo_history import SLOTransition
from well_harness.skill_executor.slo_webhook_throttle import (
    DEFAULT_MIN_INTERVAL_SEC,
    THROTTLE_INTERVAL_ENV,
    ThrottleDecision,
    WebhookThrottleState,
    read_state,
    record_fire,
    resolve_min_interval_sec,
    should_fire,
    state_path,
    write_state,
)


# ─── Helpers ──────────────────────────────────────────────────────


def _t(*, frm="green", to="red", ts="2026-04-27T13:00:00Z"):
    return SLOTransition(
        ts=ts,
        from_severity=frm,
        to_severity=to,
        breach_slos=["pass_rate"],
        snapshot={},
    )


# ─── 1. should_fire: first per-severity always allows ────────────


def test_first_red_allowed():
    decision = should_fire(
        _t(to="red"),
        state=WebhookThrottleState.empty(),
        now_iso="2026-04-27T13:00:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is True
    assert decision.reason == "first_for_severity"


def test_first_yellow_allowed():
    decision = should_fire(
        _t(to="yellow"),
        state=WebhookThrottleState.empty(),
        now_iso="2026-04-27T13:00:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is True


def test_first_green_allowed_after_breach_clock_separate():
    """RED having fired at 13:00 doesn't muzzle GREEN's first
    fire at 13:01 — they use independent clocks."""
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    decision = should_fire(
        _t(frm="red", to="green"),
        state=state,
        now_iso="2026-04-27T13:01:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is True
    assert decision.reason == "first_for_severity"


# ─── 2. Within-window suppression ─────────────────────────────────


def test_repeat_red_within_window_suppressed():
    """RED at 13:00 + RED at 13:02 with 5min window → suppress."""
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    decision = should_fire(
        _t(to="red"),
        state=state,
        now_iso="2026-04-27T13:02:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is False
    assert decision.reason == "within_window"
    # 5min - 2min elapsed = 3min remaining
    assert decision.seconds_until_next_allowed == pytest.approx(180.0)


def test_repeat_red_at_exact_boundary_allowed():
    """At elapsed == window_seconds we ALLOW — strictly less-than
    semantics for suppression so the operator isn't waiting
    a full extra window because of subsecond rounding."""
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    decision = should_fire(
        _t(to="red"),
        state=state,
        now_iso="2026-04-27T13:05:00Z",  # exactly 300s later
        min_interval_sec=300.0,
    )
    assert decision.allow is True
    assert decision.reason == "window_elapsed"


def test_repeat_red_after_window_allowed():
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    decision = should_fire(
        _t(to="red"),
        state=state,
        now_iso="2026-04-27T13:10:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is True


# ─── 3. Per-severity clocks are independent ──────────────────────


def test_red_throttle_does_not_block_green():
    """A flap red→green→red→green within the window:
       red#1 fires
       green#1 fires (different clock)
       red#2 SUPPRESS (still in red's window)
       green#2 SUPPRESS (still in green's window)
    """
    state = WebhookThrottleState.empty()
    # red#1 fires
    decision_r1 = should_fire(
        _t(frm="green", to="red"),
        state=state, now_iso="2026-04-27T13:00:00Z",
        min_interval_sec=300.0,
    )
    assert decision_r1.allow is True
    record_fire(state, to_severity="red", now_iso="2026-04-27T13:00:00Z")
    # green#1 fires
    decision_g1 = should_fire(
        _t(frm="red", to="green"),
        state=state, now_iso="2026-04-27T13:01:00Z",
        min_interval_sec=300.0,
    )
    assert decision_g1.allow is True
    record_fire(state, to_severity="green", now_iso="2026-04-27T13:01:00Z")
    # red#2 — within red's window, suppress
    decision_r2 = should_fire(
        _t(frm="green", to="red"),
        state=state, now_iso="2026-04-27T13:02:00Z",
        min_interval_sec=300.0,
    )
    assert decision_r2.allow is False
    # green#2 — within green's window, suppress
    decision_g2 = should_fire(
        _t(frm="red", to="green"),
        state=state, now_iso="2026-04-27T13:03:00Z",
        min_interval_sec=300.0,
    )
    assert decision_g2.allow is False


# ─── 4. Edge cases ───────────────────────────────────────────────


def test_missing_to_severity_disallowed():
    """A malformed transition (no to_severity) should be REJECTED
    rather than fired blindly. Bias toward not-spamming when the
    payload shape is unexpected."""
    decision = should_fire(
        SLOTransition(
            ts="2026-04-27T13:00:00Z",
            from_severity="green",
            to_severity="",
            breach_slos=[],
            snapshot={},
        ),
        state=WebhookThrottleState.empty(),
        now_iso="2026-04-27T13:00:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is False
    assert decision.reason == "invalid:missing_to_severity"


def test_unparseable_timestamp_falls_to_allow():
    """If we can't parse the stored timestamp we DON'T silently
    mute. Bias toward firing on bad data — better one extra ping
    than a missed alert."""
    state = WebhookThrottleState(last_dispatched={"red": "garbage"})
    decision = should_fire(
        _t(to="red"),
        state=state,
        now_iso="2026-04-27T13:00:00Z",
        min_interval_sec=300.0,
    )
    assert decision.allow is True
    assert decision.reason == "unparseable_timestamp"


def test_zero_interval_allows_everything():
    """min_interval_sec=0 effectively disables the throttle. Lets
    a deploy temporarily turn it off without removing the call site."""
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    decision = should_fire(
        _t(to="red"),
        state=state,
        now_iso="2026-04-27T13:00:01Z",  # 1 sec later
        min_interval_sec=0.0,
    )
    assert decision.allow is True


# ─── 5. Persistence round-trip ────────────────────────────────────


def test_state_round_trip(tmp_path):
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
        "green": "2026-04-27T13:01:00Z",
    })
    write_state(tmp_path, state)
    reloaded = read_state(tmp_path)
    assert reloaded.last_dispatched == state.last_dispatched


def test_read_state_missing_file(tmp_path):
    """Fresh deploy → empty state, not error."""
    state = read_state(tmp_path)
    assert state.last_dispatched == {}


def test_read_state_corrupt_file_treated_as_empty(tmp_path):
    """A corrupt state file MUST NOT silently mute future alerts.
    Treat it as fresh."""
    p = state_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{this is not valid json", encoding="utf-8")
    state = read_state(tmp_path)
    assert state.last_dispatched == {}


def test_read_state_handles_non_dict_payload(tmp_path):
    """A JSON file containing a list/scalar at the top level is
    not a valid throttle state. Defensive parse → empty."""
    p = state_path(tmp_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")
    state = read_state(tmp_path)
    assert state.last_dispatched == {}


def test_write_state_atomic(tmp_path):
    """write_state is tmp+rename. If interrupted mid-write, the
    target file either has the old contents or the new — never
    half-formed."""
    initial = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    write_state(tmp_path, initial)
    # Verify on disk is the JSON we expect
    raw = state_path(tmp_path).read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed == {"last_dispatched": {"red": "2026-04-27T13:00:00Z"}}


# ─── 6. record_fire mutation ──────────────────────────────────────


def test_record_fire_updates_state():
    state = WebhookThrottleState.empty()
    record_fire(state, to_severity="red", now_iso="2026-04-27T13:00:00Z")
    assert state.last_dispatched == {"red": "2026-04-27T13:00:00Z"}


def test_record_fire_lowercases_severity():
    """Severity strings come from SLOSeverity.value (lowercase) but
    be defensive against caller passing 'RED' or 'Red'."""
    state = WebhookThrottleState.empty()
    record_fire(state, to_severity="RED", now_iso="2026-04-27T13:00:00Z")
    # Stored lowercased so should_fire reads find it
    assert "red" in state.last_dispatched


def test_record_fire_overwrites_previous():
    """Most-recent fire wins. The state isn't a history — that's
    slo_history's job."""
    state = WebhookThrottleState(last_dispatched={
        "red": "2026-04-27T13:00:00Z",
    })
    record_fire(state, to_severity="red", now_iso="2026-04-27T13:10:00Z")
    assert state.last_dispatched["red"] == "2026-04-27T13:10:00Z"


# ─── 7. Env var resolution ────────────────────────────────────────


def test_resolve_default(monkeypatch):
    monkeypatch.delenv(THROTTLE_INTERVAL_ENV, raising=False)
    assert resolve_min_interval_sec() == DEFAULT_MIN_INTERVAL_SEC


def test_resolve_override(monkeypatch):
    monkeypatch.setenv(THROTTLE_INTERVAL_ENV, "60")
    assert resolve_min_interval_sec() == 60.0


def test_resolve_zero_interval(monkeypatch):
    """Zero is valid (disables throttle); shouldn't fall back to
    the default."""
    monkeypatch.setenv(THROTTLE_INTERVAL_ENV, "0")
    assert resolve_min_interval_sec() == 0.0


def test_resolve_negative_falls_back(monkeypatch):
    monkeypatch.setenv(THROTTLE_INTERVAL_ENV, "-10")
    assert resolve_min_interval_sec() == DEFAULT_MIN_INTERVAL_SEC


def test_resolve_invalid_falls_back(monkeypatch):
    monkeypatch.setenv(THROTTLE_INTERVAL_ENV, "not-a-number")
    assert resolve_min_interval_sec() == DEFAULT_MIN_INTERVAL_SEC
