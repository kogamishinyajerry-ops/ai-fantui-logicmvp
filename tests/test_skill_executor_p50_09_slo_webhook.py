"""P50-09 — SLO alert webhook unit tests.

Locks down: should_dispatch policy (fire on entering YELLOW/RED
+ recovery to GREEN, silent otherwise); dispatch_transition POSTs
the right wire shape; failures are returned as DispatchResult,
never raised; URL/timeout env-var resolution.
"""

from __future__ import annotations

import dataclasses
import urllib.error

import pytest

from well_harness.skill_executor.slo_history import SLOTransition
from well_harness.skill_executor.slo_webhook import (
    DEFAULT_WEBHOOK_TIMEOUT_SEC,
    WEBHOOK_TIMEOUT_ENV,
    WEBHOOK_URL_ENV,
    DispatchResult,
    dispatch_transition,
    resolve_webhook_timeout,
    resolve_webhook_url,
    should_dispatch,
    transition_to_event,
)


# ─── Helpers ──────────────────────────────────────────────────────


def _t(*, frm="green", to="red", breaches=("pass_rate",)):
    return SLOTransition(
        ts="2026-04-27T13:00:00Z",
        from_severity=frm,
        to_severity=to,
        breach_slos=list(breaches),
        snapshot={"total": 50, "pass_rate": 0.4},
    )


# ─── 1. should_dispatch policy ────────────────────────────────────


@pytest.mark.parametrize(
    "frm,to,expected",
    [
        # Entering a breach → fire
        ("green", "red", True),
        ("green", "yellow", True),
        ("none", "red", True),       # first-call RED
        ("none", "yellow", True),    # first-call YELLOW
        ("no_data", "red", True),    # leaving NO_DATA into breach
        # Recovery → fire
        ("red", "green", True),
        ("yellow", "green", True),
        # Escalation between breach severities → fire (still going wrong way)
        ("yellow", "red", True),
        # De-escalation between breach severities → fire (improving)
        ("red", "yellow", True),
        # NO_DATA churn → silent
        ("none", "no_data", False),
        ("no_data", "green", False),
        ("green", "no_data", False),  # data dried up but not a breach
        # GREEN→GREEN (shouldn't happen since record_transition
        # dedupes, but be defensive)
        ("green", "green", False),
        # First-call green is silent at the recorder level, but
        # if a synthetic green-from-none ever shows up we still
        # don't fire
        ("none", "green", False),
    ],
)
def test_should_dispatch_policy(frm, to, expected):
    assert should_dispatch(_t(frm=frm, to=to)) is expected


# ─── 2. transition_to_event wire shape ────────────────────────────


def test_event_shape():
    t = _t(
        frm="green", to="red",
        breaches=("pass_rate", "pass_rate_recent"),
    )
    event = transition_to_event(t)
    assert set(event.keys()) == {
        "event_type", "ts", "from_severity", "to_severity",
        "breach_slos", "snapshot",
    }
    assert event["event_type"] == "slo_transition"
    assert event["from_severity"] == "green"
    assert event["to_severity"] == "red"
    assert event["breach_slos"] == ["pass_rate", "pass_rate_recent"]
    assert event["snapshot"]["total"] == 50


# ─── 3. URL / timeout env resolution ──────────────────────────────


def test_resolve_url_returns_none_when_unset(monkeypatch):
    monkeypatch.delenv(WEBHOOK_URL_ENV, raising=False)
    assert resolve_webhook_url() is None


def test_resolve_url_strips_whitespace(monkeypatch):
    monkeypatch.setenv(WEBHOOK_URL_ENV, "  https://hooks.example.com/abc  ")
    assert resolve_webhook_url() == "https://hooks.example.com/abc"


def test_resolve_url_treats_blank_as_none(monkeypatch):
    monkeypatch.setenv(WEBHOOK_URL_ENV, "   ")
    assert resolve_webhook_url() is None


def test_resolve_timeout_default(monkeypatch):
    monkeypatch.delenv(WEBHOOK_TIMEOUT_ENV, raising=False)
    assert resolve_webhook_timeout() == DEFAULT_WEBHOOK_TIMEOUT_SEC


def test_resolve_timeout_override(monkeypatch):
    monkeypatch.setenv(WEBHOOK_TIMEOUT_ENV, "2.5")
    assert resolve_webhook_timeout() == 2.5


def test_resolve_timeout_invalid_falls_back(monkeypatch):
    monkeypatch.setenv(WEBHOOK_TIMEOUT_ENV, "not-a-number")
    assert resolve_webhook_timeout() == DEFAULT_WEBHOOK_TIMEOUT_SEC


def test_resolve_timeout_negative_falls_back(monkeypatch):
    monkeypatch.setenv(WEBHOOK_TIMEOUT_ENV, "-5")
    assert resolve_webhook_timeout() == DEFAULT_WEBHOOK_TIMEOUT_SEC


# ─── 4. dispatch_transition skip cases ────────────────────────────


def test_dispatch_skipped_when_policy_says_no():
    """No breach, no recovery → don't fire even with a URL set."""
    calls = []

    def fake_post(url, body, headers, timeout):
        calls.append((url, body))
        return 200, b"ok"

    result = dispatch_transition(
        _t(frm="green", to="green"),
        url="https://example.com/hook",
        post_fn=fake_post,
    )
    assert result.sent is False
    assert result.skipped_reason == "policy:not_a_breach_or_recovery"
    assert calls == []


def test_dispatch_skipped_when_no_url(monkeypatch):
    """Webhook URL not configured → silent skip, never crash."""
    monkeypatch.delenv(WEBHOOK_URL_ENV, raising=False)
    result = dispatch_transition(_t(frm="green", to="red"))
    assert result.sent is False
    assert result.skipped_reason == "config:no_webhook_url"


# ─── 5. dispatch_transition success path ──────────────────────────


def test_dispatch_posts_correct_body():
    """The wire shape sent over the network is exactly what
    transition_to_event produces."""
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured["url"] = url
        captured["body"] = body
        captured["headers"] = headers
        captured["timeout"] = timeout
        return 200, b"ok"

    transition = _t(
        frm="green", to="red",
        breaches=("pass_rate_recent",),
    )
    result = dispatch_transition(
        transition,
        url="https://hooks.example.com/abc",
        timeout=2.0,
        post_fn=fake_post,
    )
    assert result.sent is True
    assert result.success is True
    assert result.status_code == 200
    assert captured["url"] == "https://hooks.example.com/abc"
    assert captured["timeout"] == 2.0
    assert captured["headers"]["Content-Type"] == "application/json"
    # Body is JSON of the event
    import json
    parsed = json.loads(captured["body"].decode("utf-8"))
    assert parsed["event_type"] == "slo_transition"
    assert parsed["to_severity"] == "red"
    assert parsed["breach_slos"] == ["pass_rate_recent"]


def test_dispatch_success_for_2xx():
    def post_201(url, body, headers, timeout):
        return 201, b""
    result = dispatch_transition(
        _t(frm="green", to="red"),
        url="https://example.com",
        post_fn=post_201,
    )
    assert result.success is True
    assert result.status_code == 201


def test_dispatch_failure_for_5xx():
    """5xx response → success=False, sent=True. Caller can
    log / metric the error if needed."""
    def post_500(url, body, headers, timeout):
        return 500, b"server error"
    result = dispatch_transition(
        _t(frm="green", to="red"),
        url="https://example.com",
        post_fn=post_500,
    )
    assert result.sent is True
    assert result.success is False
    assert result.status_code == 500


# ─── 6. dispatch_transition transport-failure path ────────────────


def test_dispatch_swallows_url_error():
    """DNS / connection-refused → caught, returned as failed
    DispatchResult. Must NEVER raise."""
    def post_explodes(url, body, headers, timeout):
        raise urllib.error.URLError("connection refused")
    result = dispatch_transition(
        _t(frm="green", to="red"),
        url="https://example.com",
        post_fn=post_explodes,
    )
    assert result.sent is True
    assert result.success is False
    assert result.status_code is None


def test_dispatch_swallows_timeout():
    def post_timeout(url, body, headers, timeout):
        raise TimeoutError("read timed out")
    result = dispatch_transition(
        _t(frm="green", to="red"),
        url="https://example.com",
        post_fn=post_timeout,
    )
    assert result.sent is True
    assert result.success is False


def test_dispatch_swallows_os_error():
    def post_os(url, body, headers, timeout):
        raise OSError("network down")
    result = dispatch_transition(
        _t(frm="green", to="red"),
        url="https://example.com",
        post_fn=post_os,
    )
    assert result.sent is True
    assert result.success is False


# ─── 7. URL falls back to env when not passed ─────────────────────


def test_dispatch_url_falls_back_to_env(monkeypatch):
    monkeypatch.setenv(WEBHOOK_URL_ENV, "https://env-hook.example.com")
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured["url"] = url
        return 200, b""

    dispatch_transition(
        _t(frm="green", to="red"),
        post_fn=fake_post,
    )
    assert captured["url"] == "https://env-hook.example.com"


# ─── 8. Recovery transitions also fire ────────────────────────────


def test_dispatch_fires_on_recovery():
    """RED → GREEN is just as important as GREEN → RED for an
    operator. Verify the wire payload preserves the direction."""
    captured = {}

    def fake_post(url, body, headers, timeout):
        captured["body"] = body
        return 200, b""

    dispatch_transition(
        _t(frm="red", to="green", breaches=()),
        url="https://example.com",
        post_fn=fake_post,
    )
    import json
    event = json.loads(captured["body"].decode("utf-8"))
    assert event["from_severity"] == "red"
    assert event["to_severity"] == "green"
    assert event["breach_slos"] == []
