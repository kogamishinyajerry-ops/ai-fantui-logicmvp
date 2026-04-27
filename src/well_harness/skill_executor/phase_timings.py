"""Per-phase duration extraction — feeds the workbench timing
tooltip (P50-02c).

Reads an ExecutionRecord's events log and pairs up state_transition
events to compute how long the audit spent in each lifecycle phase.

What's the value: when a reviewer sees an execution that took
30 minutes, the inbox-level total isn't enough — they want to know
"was it 29 minutes of ASKING (waiting on me) or 29 minutes of
PLANNING (LLM stuck)?" Phase timings answer that.

The audit's events log already carries timestamps + from/to state
on every transition (orchestrator._transition emits ExecutionEvent
with from_state + to_state + at). This module just walks that
list and computes durations between adjacent transitions.

What we DON'T cover yet (deferred):
  - Sub-phase splits (e.g. "PLANNING split into LLM-call vs
    JSON-validate") — would require finer instrumentation in
    planner.py
  - Wall-clock timings of OS-level work (subprocess startup,
    git overhead) — those aren't in the audit record at all
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

from well_harness.skill_executor.models import ExecutionRecord
from well_harness.skill_executor.states import ExecutionState


# Phases we report timings for. ASKING and PR_OPEN are typically
# the two longest because they wait on humans/CI; the others are
# usually executor-bound.
_REPORTED_PHASES = (
    ExecutionState.INIT.value,
    ExecutionState.PLANNING.value,
    ExecutionState.ASKING.value,
    ExecutionState.EDITING.value,
    ExecutionState.TESTING.value,
    ExecutionState.PR_OPEN.value,
)


@dataclasses.dataclass
class PhaseTiming:
    """One phase's duration. None means "we couldn't determine"
    (e.g. audit was abandoned before reaching this phase, or the
    phase is still active and finished_at is empty)."""

    phase: str
    duration_sec: float | None
    entered_at: str  # ISO8601 or "" if never entered
    exited_at: str   # ISO8601 or "" if still in this phase / never entered

    def to_json(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class PhaseTimings:
    """Full breakdown for one execution. `current_phase` is the
    state the audit was in when last persisted — useful for the
    UI to highlight which row is in-flight."""

    timings: list[PhaseTiming]
    current_phase: str
    total_duration_sec: float | None  # started_at → finished_at, or None if still in flight

    def to_json(self) -> dict:
        return {
            "timings": [t.to_json() for t in self.timings],
            "current_phase": self.current_phase,
            "total_duration_sec": self.total_duration_sec,
        }


def compute_phase_timings(record: ExecutionRecord) -> PhaseTimings:
    """Walk the events log and produce per-phase durations.

    Algorithm:
      1. Collect every state_transition event in the order they
         were recorded — this gives us a chronological list of
         (entered_state, at_timestamp) pairs.
      2. The FIRST entry's from_state was active from the audit's
         started_at until the first transition's at.
      3. Each subsequent transition closes the previous state and
         opens the next.
      4. The LAST state in the chain is closed by record.finished_at
         if set, otherwise it's still in flight (duration=None).

    Robust against:
      - Audits with no events (returns all-None for phases that
        weren't reached, total=None)
      - Audits with malformed timestamps (None for that phase,
        no exception)
      - Backfill audits (typically only INIT entry; phase durations
        all 0 or None)
    """
    transitions: list[tuple[str, str, str, str]] = []
    # Each tuple: (at, from_state, to_state, kind)
    for ev in record.events:
        if ev.kind == "state_transition" and (ev.from_state or ev.to_state):
            transitions.append(
                (ev.at, ev.from_state, ev.to_state, ev.kind)
            )

    # Chronological list: (state, entered_at)
    # Bootstrap with INIT — the audit always starts there
    entry_log: list[tuple[str, str]] = [
        (ExecutionState.INIT.value, record.started_at)
    ]
    for at, from_state, to_state, _kind in transitions:
        # The transition's `at` is when we LEFT from_state and
        # ENTERED to_state.
        entry_log.append((to_state, at))

    # Now compute exit_at for each entry: it's the entered_at of
    # the NEXT row, or finished_at for the last row.
    timings_by_phase: dict[str, PhaseTiming] = {}
    for i, (state, entered_at) in enumerate(entry_log):
        if i + 1 < len(entry_log):
            exited_at = entry_log[i + 1][1]
        else:
            # Last row — closed by finished_at, or unclosed
            exited_at = record.finished_at or ""

        duration = _safe_duration(entered_at, exited_at)
        # If a phase appears twice (it can't given the state
        # machine, but be defensive), accumulate
        if state in timings_by_phase:
            existing = timings_by_phase[state]
            new_dur = (existing.duration_sec or 0) + (duration or 0)
            timings_by_phase[state] = PhaseTiming(
                phase=state,
                duration_sec=new_dur if new_dur > 0 else None,
                entered_at=existing.entered_at,
                exited_at=exited_at,
            )
        else:
            timings_by_phase[state] = PhaseTiming(
                phase=state,
                duration_sec=duration,
                entered_at=entered_at,
                exited_at=exited_at,
            )

    # Build the output list in canonical phase order.
    # Phases not entered get None duration + empty timestamps
    # so the UI can render an empty row.
    output: list[PhaseTiming] = []
    for phase in _REPORTED_PHASES:
        if phase in timings_by_phase:
            output.append(timings_by_phase[phase])
        else:
            output.append(
                PhaseTiming(
                    phase=phase,
                    duration_sec=None,
                    entered_at="",
                    exited_at="",
                )
            )

    total = _safe_duration(record.started_at, record.finished_at)

    return PhaseTimings(
        timings=output,
        current_phase=record.state,
        total_duration_sec=total,
    )


# ─── Helpers ──────────────────────────────────────────────────────


def _safe_duration(start_iso: str, end_iso: str) -> float | None:
    """Compute end - start in seconds, or None if either timestamp
    is missing/unparseable or the result is negative."""
    if not start_iso or not end_iso:
        return None
    s = _parse_iso(start_iso)
    e = _parse_iso(end_iso)
    if s is None or e is None:
        return None
    d = e - s
    if d < 0:
        return None
    return d


def _parse_iso(iso_str: str) -> float | None:
    """ISO 8601 → POSIX seconds. Tolerates trailing 'Z'.
    Returns None on parse failure."""
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
