"""Webhook dispatch throttle — suppress repeat alerts to the same
severity within a configurable interval (P50-11).

Why: P50-09 fires on every real SLO transition. If a flaky test
causes the verdict to flap (RED→GREEN→RED→GREEN within minutes),
the operator gets pinged on every flip. That's the #1 reason
oncalls disable notifications. A per-severity throttle preserves
the *first* alert in each direction while suppressing the
follow-on noise.

Policy (`should_fire`):
  - Look up `last_dispatched[to_severity]` from the throttle state
  - If unset (first time we'd alert at this severity) → allow
  - If `now - last_dispatched[to_severity] >= min_interval_sec`
    → allow (the previous alert has aged out)
  - Otherwise → suppress (with a reason and the time-remaining)

Per-severity clocks: a RED→GREEN recovery has its own throttle
slot from a GREEN→RED breach. So a real flap pattern
(red, green, red, green) within the window yields:
  - red#1 fires (first red ever)
  - green#1 fires (first green ever)
  - red#2 suppressed (still in red's window)
  - green#2 suppressed (still in green's window)

State persistence: `slo_webhook_state.json` next to
slo_history.jsonl. Corruption-tolerant: a malformed file is
treated as fresh state, not fatal.

What this is NOT:
  - A circuit breaker. We never permanently mute alerts. Once
    the window passes, the next transition fires normally.
  - A digest queue. Suppressed alerts are dropped, not batched
    and re-sent. A future P50-12 could add a "while you were
    suppressed, here are the suppressed events" summary.
  - Cross-severity coupling. RED suppression doesn't affect
    GREEN's clock or vice-versa.
"""

from __future__ import annotations

import dataclasses
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path


THROTTLE_STATE_FILENAME: str = "slo_webhook_state.json"
THROTTLE_INTERVAL_ENV: str = "WORKBENCH_SLO_WEBHOOK_MIN_INTERVAL_SEC"
DEFAULT_MIN_INTERVAL_SEC: float = 300.0  # 5 minutes
_STATE_LOCK = threading.Lock()


@dataclasses.dataclass
class WebhookThrottleState:
    """In-memory representation of the throttle state file.

    `last_dispatched`: severity → ISO-8601 timestamp of the most-
    recent dispatch we made FOR that to_severity. Severities not
    yet seen are absent.

    `pending_suppressed` (P50-12): severity → list of suppressed
    transition events (as dicts) that were dropped by the throttle
    inside the active window. Once the window expires for a
    severity, take_digest_due returns and clears that bucket so
    the caller can fire a single "while you were silenced, these
    N transitions happened" digest webhook. Closes the gap where
    a flap-then-stable system would otherwise be silent about an
    hour of thrashing.
    """

    last_dispatched: dict[str, str]
    pending_suppressed: dict[str, list[dict]] = dataclasses.field(
        default_factory=dict,
    )

    @classmethod
    def empty(cls) -> "WebhookThrottleState":
        return cls(last_dispatched={}, pending_suppressed={})

    def to_json(self) -> dict:
        return {
            "last_dispatched": dict(self.last_dispatched),
            "pending_suppressed": {
                k: list(v) for k, v in self.pending_suppressed.items()
            },
        }

    @classmethod
    def from_json(cls, raw: dict) -> "WebhookThrottleState":
        ld = raw.get("last_dispatched") or {}
        if not isinstance(ld, dict):
            ld = {}
        # Backwards-compat: pre-P50-12 state files have no
        # pending_suppressed key. Default to empty so reading an
        # older file doesn't crash.
        ps = raw.get("pending_suppressed") or {}
        if not isinstance(ps, dict):
            ps = {}
        # Coerce values to str so caller doesn't have to handle
        # None/numeric drift in legacy state files
        return cls(
            last_dispatched={
                str(k): str(v) for k, v in ld.items() if v
            },
            pending_suppressed={
                str(k): list(v) for k, v in ps.items()
                if isinstance(v, list)
            },
        )


@dataclasses.dataclass
class ThrottleDecision:
    """Outcome of should_fire. `allow` is the only field the
    caller branches on; `reason` and `seconds_until_next_allowed`
    are diagnostic metadata for logs."""

    allow: bool
    reason: str
    seconds_until_next_allowed: float | None = None


def state_path(audit_dir: Path) -> Path:
    return audit_dir / THROTTLE_STATE_FILENAME


def resolve_min_interval_sec() -> float:
    raw = os.environ.get(THROTTLE_INTERVAL_ENV)
    if not raw:
        return DEFAULT_MIN_INTERVAL_SEC
    try:
        v = float(raw)
        if v < 0:
            return DEFAULT_MIN_INTERVAL_SEC
        return v
    except ValueError:
        return DEFAULT_MIN_INTERVAL_SEC


def read_state(audit_dir: Path) -> WebhookThrottleState:
    """Load throttle state from disk. Tolerates missing file
    (returns empty) and malformed JSON (treats as empty rather
    than crashing the alerting path)."""
    path = state_path(audit_dir)
    if not path.is_file():
        return WebhookThrottleState.empty()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return WebhookThrottleState.empty()
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        # Treat as fresh state. A corrupt throttle file should NOT
        # silently mute all future alerts.
        return WebhookThrottleState.empty()
    if not isinstance(raw, dict):
        return WebhookThrottleState.empty()
    return WebhookThrottleState.from_json(raw)


def write_state(audit_dir: Path, state: WebhookThrottleState) -> None:
    """Atomic write: tmp+rename. Failures (read-only fs) are
    swallowed by the caller; alerting must not break the dashboard."""
    target = state_path(audit_dir)
    payload = json.dumps(state.to_json(), ensure_ascii=False)
    tmp = target.with_suffix(".json.tmp")
    with _STATE_LOCK:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, target)


def _parse_iso_to_seconds(iso_str: str) -> float | None:
    if not iso_str:
        return None
    s = iso_str.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def should_fire(
    transition: object,
    *,
    state: WebhookThrottleState,
    now_iso: str,
    min_interval_sec: float,
) -> ThrottleDecision:
    """Decide whether to dispatch this transition's webhook.
    Pure function — no IO. `transition` is an SLOTransition; we
    read by attribute to avoid the circular import.

    Per-severity throttle: a transition's `to_severity` is the
    notification slot. Recovery (red→green) competes on the
    GREEN clock; a re-breach (green→red) on the RED clock.
    """
    to_sev = str(getattr(transition, "to_severity", "")).lower()
    if not to_sev:
        return ThrottleDecision(
            allow=False, reason="invalid:missing_to_severity",
        )
    last_iso = state.last_dispatched.get(to_sev)
    if not last_iso:
        return ThrottleDecision(allow=True, reason="first_for_severity")
    last_s = _parse_iso_to_seconds(last_iso)
    now_s = _parse_iso_to_seconds(now_iso)
    if last_s is None or now_s is None:
        # Defensive: treat unparseable timestamps as "no record"
        # rather than mute forever. Bias toward firing on bad data.
        return ThrottleDecision(allow=True, reason="unparseable_timestamp")
    elapsed = now_s - last_s
    if elapsed >= min_interval_sec:
        return ThrottleDecision(
            allow=True,
            reason="window_elapsed",
        )
    remaining = max(0.0, min_interval_sec - elapsed)
    return ThrottleDecision(
        allow=False,
        reason="within_window",
        seconds_until_next_allowed=remaining,
    )


def record_fire(
    state: WebhookThrottleState,
    *,
    to_severity: str,
    now_iso: str,
) -> None:
    """Mutate `state` to record that we just dispatched at the
    given severity. Caller persists via write_state. Separated
    from should_fire so a test can inspect the decision without
    mutating state."""
    if not to_severity:
        return
    state.last_dispatched[to_severity.lower()] = now_iso


# ─── P50-12: suppressed-events digest ─────────────────────────────


def record_suppressed(
    state: WebhookThrottleState,
    *,
    transition: object,
) -> None:
    """Stash a transition that the throttle just dropped, so we
    can emit it later in a digest. Mutates `state` in place;
    caller persists. We store the SLOTransition's JSON form (not
    the dataclass) so the state file is still plain JSON.

    `transition` is an SLOTransition. We import its to_json by
    duck-typing to avoid a circular import.
    """
    to_sev = str(getattr(transition, "to_severity", "")).lower()
    if not to_sev:
        return
    if hasattr(transition, "to_json") and callable(transition.to_json):
        event = transition.to_json()
    else:
        # Fallback for tests that pass a plain dict
        event = dict(transition) if isinstance(transition, dict) else {}
    state.pending_suppressed.setdefault(to_sev, []).append(event)


def take_digest_due(
    state: WebhookThrottleState,
    *,
    now_iso: str,
    min_interval_sec: float,
) -> dict[str, list[dict]]:
    """For each severity whose throttle window has expired AND
    has pending suppressed events, return those events and CLEAR
    them from state. Caller is responsible for firing the digest
    webhook + persisting state.

    Why "expired": we only release the digest once the operator's
    quiet period is over. Releasing earlier would defeat the
    throttle (every flap would still page). After expiry the
    operator is again receptive, so the digest summarizes "what
    you missed while we were silencing".

    Returns: severity → list of suppressed event dicts, in the
    order they were suppressed. Empty severities are omitted.
    """
    if not state.pending_suppressed:
        return {}
    now_s = _parse_iso_to_seconds(now_iso)
    if now_s is None:
        return {}
    due: dict[str, list[dict]] = {}
    for severity, events in list(state.pending_suppressed.items()):
        if not events:
            continue
        last_iso = state.last_dispatched.get(severity)
        last_s = _parse_iso_to_seconds(last_iso) if last_iso else None
        # No prior dispatch → can't be in a throttle window for
        # this severity, so any pending events are due immediately.
        if last_s is None:
            due[severity] = list(events)
            state.pending_suppressed[severity] = []
            continue
        elapsed = now_s - last_s
        if elapsed >= min_interval_sec:
            due[severity] = list(events)
            state.pending_suppressed[severity] = []
    # Clean empty buckets so the state file doesn't grow stale
    # entries forever.
    state.pending_suppressed = {
        k: v for k, v in state.pending_suppressed.items() if v
    }
    return due
