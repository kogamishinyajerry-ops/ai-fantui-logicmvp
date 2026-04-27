"""P50-12 — suppressed-events digest unit tests.

Locks down: record_suppressed stashes throttled transitions in
state; take_digest_due returns + clears them once the throttle
window expires; per-severity buckets stay independent; build_digest_event
produces the expected wire shape; dispatch_digest is no-op on
empty input + reliable on transport failures.
"""

from __future__ import annotations

import json
import urllib.error

import pytest

from well_harness.skill_executor.slo_history import SLOTransition
from well_harness.skill_executor.slo_webhook import (
    build_digest_event,
    dispatch_digest,
)
from well_harness.skill_executor.slo_webhook_throttle import (
    WebhookThrottleState,
    record_suppressed,
    take_digest_due,
    read_state,
    write_state,
)


# ─── Helpers ──────────────────────────────────────────────────────


def _t(*, frm="green", to="red", ts="2026-04-27T13:00:00Z",
       breaches=("pass_rate",)):
    return SLOTransition(
        ts=ts,
        from_severity=frm,
        to_severity=to,
        breach_slos=list(breaches),
        snapshot={"total": 50, "pass_rate": 0.4},
    )


# ─── 1. record_suppressed ─────────────────────────────────────────


def test_record_suppressed_appends_event():
    state = WebhookThrottleState.empty()
    record_suppressed(state, transition=_t(to="red"))
    assert "red" in state.pending_suppressed
    assert len(state.pending_suppressed["red"]) == 1
    # Stored as JSON dict, not the dataclass
    event = state.pending_suppressed["red"][0]
    assert event["to_severity"] == "red"
    assert event["from_severity"] == "green"


def test_record_suppressed_per_severity_independent():
    """Suppressed RED events go in 'red'; suppressed GREEN events
    go in 'green'. They never cross-pollinate."""
    state = WebhookThrottleState.empty()
    record_suppressed(state, transition=_t(to="red"))
    record_suppressed(state, transition=_t(to="red"))
    record_suppressed(state, transition=_t(frm="red", to="green"))
    assert len(state.pending_suppressed["red"]) == 2
    assert len(state.pending_suppressed["green"]) == 1


def test_record_suppressed_preserves_order():
    """When the digest fires, events come out in the same order
    they were suppressed — the timeline replay needs that to be
    accurate."""
    state = WebhookThrottleState.empty()
    record_suppressed(state, transition=_t(
        to="red", ts="2026-04-27T13:00:00Z",
    ))
    record_suppressed(state, transition=_t(
        to="red", ts="2026-04-27T13:01:00Z",
    ))
    record_suppressed(state, transition=_t(
        to="red", ts="2026-04-27T13:02:00Z",
    ))
    timestamps = [e["ts"] for e in state.pending_suppressed["red"]]
    assert timestamps == [
        "2026-04-27T13:00:00Z",
        "2026-04-27T13:01:00Z",
        "2026-04-27T13:02:00Z",
    ]


def test_record_suppressed_skips_missing_severity():
    """Defensive: a malformed transition with no to_severity
    shouldn't end up in a phantom bucket."""
    state = WebhookThrottleState.empty()
    bad = SLOTransition(
        ts="x", from_severity="green", to_severity="",
        breach_slos=[], snapshot={},
    )
    record_suppressed(state, transition=bad)
    assert state.pending_suppressed == {}


# ─── 2. take_digest_due — window expired releases + clears ───────


def test_take_digest_releases_when_window_expired():
    """RED last fired at 13:00, window=5min, now=13:06: window
    has expired → red's pending events are returned + cleared."""
    state = WebhookThrottleState(
        last_dispatched={"red": "2026-04-27T13:00:00Z"},
        pending_suppressed={"red": [
            {"ts": "2026-04-27T13:02:00Z", "to_severity": "red"},
            {"ts": "2026-04-27T13:04:00Z", "to_severity": "red"},
        ]},
    )
    due = take_digest_due(
        state,
        now_iso="2026-04-27T13:06:00Z",
        min_interval_sec=300.0,
    )
    assert "red" in due
    assert len(due["red"]) == 2
    # Cleared from state after release
    assert "red" not in state.pending_suppressed


def test_take_digest_holds_when_window_not_expired():
    """RED last fired at 13:00, now=13:02 (window=5min): too
    early → pending events stay in state, due is empty."""
    state = WebhookThrottleState(
        last_dispatched={"red": "2026-04-27T13:00:00Z"},
        pending_suppressed={"red": [
            {"ts": "2026-04-27T13:01:30Z", "to_severity": "red"},
        ]},
    )
    due = take_digest_due(
        state,
        now_iso="2026-04-27T13:02:00Z",
        min_interval_sec=300.0,
    )
    assert due == {}
    # Still pending
    assert len(state.pending_suppressed["red"]) == 1


def test_take_digest_per_severity_independent():
    """RED window expired but GREEN window still active → only
    red's digest is released."""
    state = WebhookThrottleState(
        last_dispatched={
            "red": "2026-04-27T13:00:00Z",
            "green": "2026-04-27T13:05:00Z",
        },
        pending_suppressed={
            "red": [{"ts": "2026-04-27T13:02:00Z", "to_severity": "red"}],
            "green": [{"ts": "2026-04-27T13:06:00Z", "to_severity": "green"}],
        },
    )
    # now=13:07: red elapsed=420s (expired), green elapsed=120s (still active)
    due = take_digest_due(
        state,
        now_iso="2026-04-27T13:07:00Z",
        min_interval_sec=300.0,
    )
    assert set(due.keys()) == {"red"}
    assert len(due["red"]) == 1
    # Green still pending
    assert "green" in state.pending_suppressed
    assert len(state.pending_suppressed["green"]) == 1


def test_take_digest_no_prior_dispatch_releases_immediately():
    """Edge case: a severity has pending events but NO
    last_dispatched entry. With no clock to wait on, release
    immediately — there's no throttle to honor."""
    state = WebhookThrottleState(
        last_dispatched={},
        pending_suppressed={"red": [
            {"ts": "2026-04-27T13:00:00Z", "to_severity": "red"},
        ]},
    )
    due = take_digest_due(
        state,
        now_iso="2026-04-27T13:01:00Z",
        min_interval_sec=300.0,
    )
    assert "red" in due
    assert state.pending_suppressed.get("red", []) == []


def test_take_digest_empty_state_returns_empty():
    state = WebhookThrottleState.empty()
    due = take_digest_due(
        state,
        now_iso="2026-04-27T13:00:00Z",
        min_interval_sec=300.0,
    )
    assert due == {}


# ─── 3. JSON persistence with new field ───────────────────────────


def test_state_with_pending_suppressed_round_trips(tmp_path):
    state = WebhookThrottleState(
        last_dispatched={"red": "2026-04-27T13:00:00Z"},
        pending_suppressed={"red": [
            {"ts": "2026-04-27T13:01:00Z", "to_severity": "red"},
        ]},
    )
    write_state(tmp_path, state)
    reloaded = read_state(tmp_path)
    assert reloaded.last_dispatched == state.last_dispatched
    assert reloaded.pending_suppressed == state.pending_suppressed


def test_legacy_state_file_without_pending_field_loads(tmp_path):
    """A pre-P50-12 state file has only `last_dispatched`. Reading
    it must NOT crash — pending_suppressed defaults to empty."""
    path = tmp_path / "slo_webhook_state.json"
    path.write_text(
        json.dumps({"last_dispatched": {"red": "2026-04-27T13:00:00Z"}}),
        encoding="utf-8",
    )
    reloaded = read_state(tmp_path)
    assert reloaded.last_dispatched == {"red": "2026-04-27T13:00:00Z"}
    assert reloaded.pending_suppressed == {}


def test_corrupt_pending_suppressed_field_treated_as_empty(tmp_path):
    """If pending_suppressed somehow becomes non-dict, defensive
    parse returns empty rather than crashing."""
    path = tmp_path / "slo_webhook_state.json"
    path.write_text(
        json.dumps({
            "last_dispatched": {"red": "2026-04-27T13:00:00Z"},
            "pending_suppressed": "not-a-dict",
        }),
        encoding="utf-8",
    )
    reloaded = read_state(tmp_path)
    assert reloaded.pending_suppressed == {}


# ─── 4. build_digest_event wire shape ─────────────────────────────


def test_digest_event_shape_stable():
    suppressed = [
        {"ts": "2026-04-27T13:01:00Z", "to_severity": "red",
         "from_severity": "green", "breach_slos": ["pass_rate"]},
        {"ts": "2026-04-27T13:03:00Z", "to_severity": "red",
         "from_severity": "green", "breach_slos": ["pass_rate"]},
    ]
    event = build_digest_event(
        "red", suppressed, ts="2026-04-27T13:06:00Z",
    )
    assert set(event.keys()) == {
        "event_type", "ts", "severity", "suppressed_count",
        "first_suppressed_ts", "last_suppressed_ts", "transitions",
    }
    assert event["event_type"] == "slo_digest"
    assert event["severity"] == "red"
    assert event["suppressed_count"] == 2
    assert event["first_suppressed_ts"] == "2026-04-27T13:01:00Z"
    assert event["last_suppressed_ts"] == "2026-04-27T13:03:00Z"
    assert event["transitions"] == suppressed


def test_digest_event_handles_missing_timestamps():
    """A suppressed event with no `ts` shouldn't crash the
    build. first/last fall through to whichever do have one."""
    suppressed = [
        {"to_severity": "red"},  # no ts
        {"ts": "2026-04-27T13:01:00Z", "to_severity": "red"},
    ]
    event = build_digest_event(
        "red", suppressed, ts="2026-04-27T13:06:00Z",
    )
    # The single timestamped event becomes both first and last
    assert event["first_suppressed_ts"] == "2026-04-27T13:01:00Z"
    assert event["last_suppressed_ts"] == "2026-04-27T13:01:00Z"


# ─── 5. dispatch_digest reliability ───────────────────────────────


def test_dispatch_digest_skipped_when_empty():
    """No suppressed events → no fire."""
    result = dispatch_digest(
        "red", [], ts="2026-04-27T13:00:00Z",
        url="https://example.com",
    )
    assert result.sent is False
    assert result.skipped_reason == "empty:nothing_to_digest"


def test_dispatch_digest_skipped_when_no_url(monkeypatch):
    monkeypatch.delenv("WORKBENCH_SLO_WEBHOOK_URL", raising=False)
    suppressed = [
        {"ts": "2026-04-27T13:01:00Z", "to_severity": "red"},
    ]
    result = dispatch_digest(
        "red", suppressed, ts="2026-04-27T13:06:00Z",
    )
    assert result.sent is False
    assert result.skipped_reason == "config:no_webhook_url"


def test_dispatch_digest_posts_correct_body():
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured["body"] = body
        return 200, b"ok"

    suppressed = [
        {"ts": "2026-04-27T13:01:00Z", "to_severity": "red"},
        {"ts": "2026-04-27T13:03:00Z", "to_severity": "red"},
    ]
    result = dispatch_digest(
        "red", suppressed, ts="2026-04-27T13:06:00Z",
        url="https://hooks.example.com/abc",
        post_fn=fake_post,
    )
    assert result.sent is True
    assert result.success is True
    parsed = json.loads(captured["body"].decode("utf-8"))
    assert parsed["event_type"] == "slo_digest"
    assert parsed["severity"] == "red"
    assert parsed["suppressed_count"] == 2


def test_dispatch_digest_swallows_url_error():
    def post_explodes(url, body, headers, timeout):
        raise urllib.error.URLError("connection refused")
    suppressed = [{"ts": "x", "to_severity": "red"}]
    result = dispatch_digest(
        "red", suppressed, ts="x",
        url="https://example.com",
        post_fn=post_explodes,
    )
    assert result.sent is True
    assert result.success is False


def test_dispatch_digest_failure_for_5xx():
    def post_500(url, body, headers, timeout):
        return 500, b"error"
    suppressed = [{"ts": "x", "to_severity": "red"}]
    result = dispatch_digest(
        "red", suppressed, ts="x",
        url="https://example.com",
        post_fn=post_500,
    )
    assert result.sent is True
    assert result.success is False
    assert result.status_code == 500
