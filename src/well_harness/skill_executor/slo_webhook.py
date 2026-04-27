"""SLO alert webhook — fires an HTTP POST when an SLO transition
crosses a notification-worthy boundary (P50-09).

Why: P50-08b records every transition to disk so a reviewer
scrolling the dashboard can see when things broke. But the
dashboard only helps if the engineer is already looking. A
webhook means they get pinged whether or not the workbench tab
is open.

Notification policy (`should_dispatch`):
  - to_severity is YELLOW or RED → fire (a breach occurred)
  - from_severity in {YELLOW, RED} and to_severity == GREEN
    → fire (a recovery happened)
  - everything else (NO_DATA churn, GREEN→GREEN no-op) → silent

Steady-state RED→RED isn't observed here because P50-08b's
record_transition only persists actual changes. So this module
naturally inherits "fire-once-per-incident" semantics — no
custom dedup needed.

Wire shape (single JSON POST):
  {
    "event_type": "slo_transition",
    "ts": "2026-04-27T13:00:00Z",
    "from_severity": "green",
    "to_severity": "red",
    "breach_slos": ["pass_rate_recent"],
    "snapshot": {"total": 50, "pass_rate": 0.85, ...}
  }

Generic shape lets any webhook listener consume it (custom
service, Slack incoming-webhook with a thin adapter, etc.). We
don't ship Slack-specific formatting — that's a layer above.

Failure mode: dispatch failures (DNS, timeout, 5xx) are swallowed
by the caller (demo_server). The webhook is best-effort
notification, NOT a control-plane signal — the dashboard remains
authoritative.
"""

from __future__ import annotations

import dataclasses
import json
import os
import urllib.error as _urlerr
import urllib.request as _urlreq

from well_harness.skill_executor.errors import SkillExecutorError


# Env var resolution order
WEBHOOK_URL_ENV: str = "WORKBENCH_SLO_WEBHOOK_URL"
WEBHOOK_TIMEOUT_ENV: str = "WORKBENCH_SLO_WEBHOOK_TIMEOUT"
DEFAULT_WEBHOOK_TIMEOUT_SEC: float = 5.0


# Severities that trigger a notification when entered.
_BREACH_SEVERITIES = frozenset({"yellow", "red"})


class WebhookDispatchError(SkillExecutorError):
    """Webhook POST failed (network, timeout, non-2xx). Caller is
    expected to swallow this — alerting failures must not break
    the dashboard."""


@dataclasses.dataclass
class DispatchResult:
    sent: bool                # True if we actually attempted a POST
    success: bool             # True if 2xx response received
    status_code: int | None   # HTTP status, or None on transport failure
    skipped_reason: str | None  # Why we didn't fire (policy / no URL)


def resolve_webhook_url() -> str | None:
    """Env-var override. Returns None when unset/empty so the
    metrics endpoint can no-op cleanly without a config file."""
    raw = os.environ.get(WEBHOOK_URL_ENV)
    if raw and raw.strip():
        return raw.strip()
    return None


def resolve_webhook_timeout() -> float:
    raw = os.environ.get(WEBHOOK_TIMEOUT_ENV)
    if not raw:
        return DEFAULT_WEBHOOK_TIMEOUT_SEC
    try:
        v = float(raw)
        if v <= 0:
            return DEFAULT_WEBHOOK_TIMEOUT_SEC
        return v
    except ValueError:
        return DEFAULT_WEBHOOK_TIMEOUT_SEC


def should_dispatch(transition: object) -> bool:
    """Return True iff this transition crosses a notification
    boundary. Pure function — no IO. `transition` is an
    SLOTransition (passed as `object` to avoid the slo_history
    import cycle).

    Boundaries:
      - Entering YELLOW or RED (a breach started or escalated)
      - RED/YELLOW → GREEN (a recovery completed)
    """
    to_sev = str(getattr(transition, "to_severity", "")).lower()
    from_sev = str(getattr(transition, "from_severity", "")).lower()
    if to_sev in _BREACH_SEVERITIES:
        return True
    if to_sev == "green" and from_sev in _BREACH_SEVERITIES:
        return True
    return False


def transition_to_event(transition: object) -> dict:
    """Serialize an SLOTransition into the webhook wire shape.
    Adds an `event_type` discriminator so a listener can route
    by message kind if other event types are added later."""
    return {
        "event_type": "slo_transition",
        "ts": str(getattr(transition, "ts", "")),
        "from_severity": str(getattr(transition, "from_severity", "")),
        "to_severity": str(getattr(transition, "to_severity", "")),
        "breach_slos": list(getattr(transition, "breach_slos", []) or []),
        "snapshot": dict(getattr(transition, "snapshot", {}) or {}),
    }


def dispatch_transition(
    transition: object,
    *,
    url: str | None = None,
    timeout: float | None = None,
    post_fn=None,
) -> DispatchResult:
    """POST the transition event to the webhook URL.

    Args:
      url: webhook destination. Falls back to env var
           `WORKBENCH_SLO_WEBHOOK_URL`.
      timeout: per-request timeout. Falls back to env or 5s.
      post_fn: injection point for tests. Signature:
           (url, body_bytes, headers, timeout) → (status_code, body)
           Default uses urllib.

    Returns:
      DispatchResult — `sent` is False when policy/url skipped
      the call; `success` is False when transport or HTTP failed.
    """
    if not should_dispatch(transition):
        return DispatchResult(
            sent=False, success=False, status_code=None,
            skipped_reason="policy:not_a_breach_or_recovery",
        )
    target = url if url is not None else resolve_webhook_url()
    if not target:
        return DispatchResult(
            sent=False, success=False, status_code=None,
            skipped_reason="config:no_webhook_url",
        )
    timeout_sec = timeout if timeout is not None else resolve_webhook_timeout()
    payload = json.dumps(
        transition_to_event(transition), ensure_ascii=False,
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    poster = post_fn or _default_post
    try:
        status_code, _body = poster(target, payload, headers, timeout_sec)
    except (_urlerr.URLError, _urlerr.HTTPError, OSError, TimeoutError):
        return DispatchResult(
            sent=True, success=False, status_code=None,
            skipped_reason=None,
        )
    success = 200 <= int(status_code) < 300
    return DispatchResult(
        sent=True, success=success, status_code=int(status_code),
        skipped_reason=None,
    )


def _default_post(url: str, body: bytes, headers: dict, timeout: float):
    request = _urlreq.Request(url, data=body, headers=headers, method="POST")
    with _urlreq.urlopen(request, timeout=timeout) as response:
        # urllib's HTTPResponse.status is the only thing we need;
        # body is consumed but typically empty / acknowledgement
        return response.status, response.read()


# ─── P50-12: suppressed-events digest dispatcher ─────────────────


def build_digest_event(
    severity: str,
    suppressed: list[dict],
    *,
    ts: str,
) -> dict:
    """Build the digest wire shape. Separate from the live
    `transition_to_event` so a webhook listener can route on
    `event_type` (digest vs single transition) without parsing
    the body.

    Fields:
      severity: which to_severity bucket this digest covers
      suppressed_count: len(suppressed)
      first_suppressed_ts / last_suppressed_ts: time window
      transitions: the suppressed events themselves (for replay)
    """
    timestamps = [str(t.get("ts", "")) for t in suppressed]
    timestamps = [t for t in timestamps if t]
    return {
        "event_type": "slo_digest",
        "ts": ts,
        "severity": severity,
        "suppressed_count": len(suppressed),
        "first_suppressed_ts": timestamps[0] if timestamps else None,
        "last_suppressed_ts": timestamps[-1] if timestamps else None,
        "transitions": list(suppressed),
    }


def dispatch_digest(
    severity: str,
    suppressed: list[dict],
    *,
    ts: str,
    url: str | None = None,
    timeout: float | None = None,
    post_fn=None,
) -> DispatchResult:
    """POST a digest of suppressed transitions. Same reliability
    contract as dispatch_transition: never raises, transport
    failures returned as DispatchResult.

    No-op when suppressed is empty — the caller shouldn't even
    call us in that case, but be defensive.
    """
    if not suppressed:
        return DispatchResult(
            sent=False, success=False, status_code=None,
            skipped_reason="empty:nothing_to_digest",
        )
    target = url if url is not None else resolve_webhook_url()
    if not target:
        return DispatchResult(
            sent=False, success=False, status_code=None,
            skipped_reason="config:no_webhook_url",
        )
    timeout_sec = timeout if timeout is not None else resolve_webhook_timeout()
    payload = json.dumps(
        build_digest_event(severity, suppressed, ts=ts),
        ensure_ascii=False,
    ).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    poster = post_fn or _default_post
    try:
        status_code, _body = poster(target, payload, headers, timeout_sec)
    except (_urlerr.URLError, _urlerr.HTTPError, OSError, TimeoutError):
        return DispatchResult(
            sent=True, success=False, status_code=None,
            skipped_reason=None,
        )
    success = 200 <= int(status_code) < 300
    return DispatchResult(
        sent=True, success=success, status_code=int(status_code),
        skipped_reason=None,
    )
