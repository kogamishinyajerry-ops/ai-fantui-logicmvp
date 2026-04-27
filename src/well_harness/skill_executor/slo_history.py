"""SLO transition history — append-only JSONL log of every
GREEN→YELLOW/RED (and reverse) transition so a reviewer can
answer "when did this start breaking?" (P50-08b).

Why: P50-07 gives the current verdict; P50-08a catches the
freshest regression. Neither answers WHEN. Without a transition
timeline a reviewer can see "RED right now" but has to scroll
audits chronologically to find the inflection point. The history
log makes the timeline a single endpoint hit.

Shape of one line (one transition):
  {
    "ts": "2026-04-27T13:00:00Z",
    "from_severity": "green",
    "to_severity": "red",
    "breach_slos": ["pass_rate_recent", "active_failures_count"],
    "snapshot": {
      "total": 100,
      "pass_rate": 0.85,
      "pass_rate_recent": 0.30,
      "failed_count": 8
    }
  }

What this is NOT:
  - A full audit replay log. The transition log only records
    severity changes — steady-state polls don't append.
  - A first-write of the verdict. We don't synthesize a
    "transition from None to GREEN" on the very first poll.
    Only real transitions count.
  - Synchronous with audits. Recorded by the metrics endpoint
    when its compute_slo_status returns a verdict that differs
    from the last logged one. Polling cadence drives
    timestamp resolution.
"""

from __future__ import annotations

import dataclasses
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path


SLO_HISTORY_FILENAME: str = "slo_history.jsonl"
_HISTORY_LOCK = threading.Lock()


@dataclasses.dataclass
class SLOTransition:
    """One severity transition. Stored as a JSON line; the on-disk
    representation matches `to_json` exactly so reload round-trips."""

    ts: str
    from_severity: str
    to_severity: str
    breach_slos: list[str]
    snapshot: dict

    def to_json(self) -> dict:
        return {
            "ts": self.ts,
            "from_severity": self.from_severity,
            "to_severity": self.to_severity,
            "breach_slos": list(self.breach_slos),
            "snapshot": dict(self.snapshot),
        }

    @classmethod
    def from_json(cls, raw: dict) -> "SLOTransition":
        return cls(
            ts=str(raw.get("ts", "")),
            from_severity=str(raw.get("from_severity", "")),
            to_severity=str(raw.get("to_severity", "")),
            breach_slos=list(raw.get("breach_slos", [])),
            snapshot=dict(raw.get("snapshot", {})),
        )


def history_path(audit_dir: Path) -> Path:
    """The append-only JSONL file inside the audit dir. Doesn't
    create the file — record_transition does that on first write."""
    return audit_dir / SLO_HISTORY_FILENAME


def load_history(audit_dir: Path, *, limit: int | None = None) -> list[SLOTransition]:
    """Read the transition log. Tolerates a missing file (returns
    [] on first run) and silently drops malformed lines so a
    corrupt write can't poison the dashboard.

    `limit` returns the most recent N entries (newest-last in the
    file → newest-last in the result; caller can reverse if it
    wants newest-first).
    """
    path = history_path(audit_dir)
    if not path.is_file():
        return []
    transitions: list[SLOTransition] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            # Skip a corrupt line rather than fail the whole load.
            # The dashboard would rather show 99/100 transitions
            # than nothing because byte 487 got truncated.
            continue
        transitions.append(SLOTransition.from_json(raw))
    if limit is not None and limit >= 0:
        transitions = transitions[-limit:]
    return transitions


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def record_transition(
    audit_dir: Path,
    *,
    current_status: object,
    metrics: object,
    now_fn=None,
) -> SLOTransition | None:
    """Append a transition record IFF the current verdict differs
    from the last logged one.

    `current_status` is an SLOStatus; `metrics` is a Metrics. Both
    are passed as `object` to avoid circular imports — we read by
    attribute / getattr.

    Returns the appended SLOTransition, or None if no transition
    happened (steady-state poll).

    First-call behavior: NO_DATA → GREEN/YELLOW/RED counts as a
    transition (the system is now seeing real data). But a fresh
    deploy that immediately hits GREEN — with no prior log — does
    NOT get a synthesized "from None to GREEN" entry; the very
    first verdict establishes the baseline silently.

    Why first GREEN is silent: a reviewer scrolling the timeline
    expects every entry to mean "something changed". Logging an
    initial GREEN would be noise. The reverse — first sample is
    YELLOW or RED — DOES log, because that IS news worth seeing
    on day-1 of a deploy.
    """
    if now_fn is None:
        now_fn = _now_iso

    overall = getattr(current_status, "overall", None)
    if overall is None:
        return None
    # SLOSeverity → string for storage stability
    current_severity = (
        overall.value if hasattr(overall, "value") else str(overall)
    )

    history = load_history(audit_dir)
    last_severity = history[-1].to_severity if history else None

    # No-op when nothing changed. Steady-state polls do NOT bloat
    # the log.
    if last_severity == current_severity:
        return None

    # Suppress the first GREEN entry. See the docstring rationale.
    if last_severity is None and current_severity == "green":
        return None

    breaches = getattr(current_status, "breaches", []) or []
    breach_slos = [
        b.slo if hasattr(b, "slo") else str(b) for b in breaches
    ]

    by_state = getattr(metrics, "by_state", {}) or {}
    snapshot = {
        "total": int(getattr(metrics, "total", 0) or 0),
        "pass_rate": float(getattr(metrics, "pass_rate", 0.0) or 0.0),
        "pass_rate_recent": getattr(metrics, "pass_rate_recent", None),
        "recent_window_size": int(
            getattr(metrics, "recent_window_size", 0) or 0
        ),
        "failed_count": int(by_state.get("FAILED", 0) or 0),
    }

    transition = SLOTransition(
        ts=now_fn(),
        from_severity=last_severity or "none",
        to_severity=current_severity,
        breach_slos=breach_slos,
        snapshot=snapshot,
    )

    # Append. Atomic-enough for a single-engineer dashboard:
    # serialize one line at a time inside a process lock; crash
    # mid-write at worst leaves a malformed line which load_history
    # silently skips.
    line = json.dumps(transition.to_json(), ensure_ascii=False) + "\n"
    path = history_path(audit_dir)
    with _HISTORY_LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                # Some filesystems / mount options don't support fsync;
                # the line is already written, just not durably-synced.
                pass

    return transition
