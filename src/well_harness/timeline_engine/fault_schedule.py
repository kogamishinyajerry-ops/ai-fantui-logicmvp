"""Per-tick active-fault set compilation.

Rules (half-open [start, end)):
    - `inject_fault` at t_s without duration: active on [t_s, ∞) until a
      matching `clear_fault` at the same target.
    - `inject_fault` at t_s WITH duration_s: active on [t_s, t_s + duration_s).
    - `clear_fault` at t_s: the matching fault's end_s is clamped to t_s.
    - Flat `fault_schedule` entries on the Timeline are merged in as-is.
    - "Matching" means identical `target` string (e.g. "sw1:stuck_off").
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from well_harness.timeline_engine.schema import FaultScheduleEntry, Timeline


def _parse_fault_target(target: str) -> tuple[str, str]:
    """Split 'node_id:fault_type' into (node_id, fault_type).

    Accepts either 'sw1:stuck_off' or 'sw1' (fault_type = '').
    """
    if ":" in target:
        node_id, fault_type = target.split(":", 1)
        return node_id.strip(), fault_type.strip()
    return target.strip(), ""


def compile_fault_schedule(timeline: Timeline) -> list[FaultScheduleEntry]:
    """Resolve all `inject_fault` / `clear_fault` events into concrete entries.

    Also merges any pre-existing flat `timeline.fault_schedule` entries.
    """
    compiled: list[FaultScheduleEntry] = list(timeline.fault_schedule)

    # Group open injects by target so clear_fault can close them.
    # Each entry is (index_in_compiled, FaultScheduleEntry).
    open_by_target: dict[str, list[tuple[int, FaultScheduleEntry]]] = {}

    for event in timeline.events:
        if event.kind == "inject_fault":
            node_id, fault_type = _parse_fault_target(event.target)
            end_s = (
                event.t_s + event.duration_s
                if event.duration_s is not None
                else math.inf
            )
            entry = FaultScheduleEntry(
                node_id=node_id,
                fault_type=fault_type,
                start_s=event.t_s,
                end_s=min(end_s, timeline.duration_s),
            )
            idx = len(compiled)
            compiled.append(entry)
            open_by_target.setdefault(event.target, []).append((idx, entry))
        elif event.kind == "clear_fault":
            pending = open_by_target.get(event.target) or []
            # Drop entries that have already expired by the time this
            # clear_fault fires — their end_s ≤ event.t_s so they are
            # no longer active and cannot be closed further.
            pending = [
                (idx, entry) for idx, entry in pending if entry.end_s > event.t_s
            ]
            open_by_target[event.target] = pending
            if not pending:
                continue
            # Close the EARLIEST still-active injection (FIFO match):
            # this preserves the intuitive "open/close" pairing when a
            # script does inject → short-duration inject → clear.
            idx, pending_entry = pending.pop(0)
            clamped_end = min(event.t_s, pending_entry.end_s)
            compiled[idx] = FaultScheduleEntry(
                node_id=pending_entry.node_id,
                fault_type=pending_entry.fault_type,
                start_s=pending_entry.start_s,
                end_s=clamped_end,
            )
    return compiled


@dataclass
class ActiveFaultSet:
    """Faults currently active at a given tick."""

    entries: list[FaultScheduleEntry]

    @property
    def ids(self) -> list[str]:
        return [
            f"{e.node_id}:{e.fault_type}" if e.fault_type else e.node_id
            for e in self.entries
        ]

    def as_injection_list(self) -> list[dict[str, str]]:
        """Legacy fault_injections shape: [{"node_id": ..., "fault_type": ...}]."""
        return [
            {"node_id": e.node_id, "fault_type": e.fault_type}
            for e in self.entries
        ]


def compile_active_faults(
    compiled_schedule: list[FaultScheduleEntry], t_s: float
) -> ActiveFaultSet:
    """Return faults active at time `t_s` per half-open [start, end)."""
    return ActiveFaultSet(
        entries=[e for e in compiled_schedule if e.is_active_at(t_s)]
    )
