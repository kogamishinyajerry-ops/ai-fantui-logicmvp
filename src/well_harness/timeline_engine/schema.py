"""Timeline engine data model.

All timestamps are floats in seconds.
All time ranges use half-open intervals [start, end): the start instant
is INSIDE, the end instant is OUTSIDE. This eliminates double-fire on
boundary ticks when step_s divides the boundary timestamps evenly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# Seven event kinds — Codex architecture consultation recommendation.
EVENT_KINDS = (
    "set_input",              # target input field takes value at t_s and holds
    "ramp_input",             # target input linearly ramps to value over duration_s
    "inject_fault",           # fault with (node_id, mode) activates at t_s
    "clear_fault",            # matching fault deactivates at t_s
    "mark_phase",             # pure annotation: "descent" / "landing" / "deploy" / ...
    "assert_condition",       # assertion against trace (does NOT affect control logic)
    "start_deploy_sequence",  # shorthand: schedules sw1/sw2 triggers + tra_deg ramp
)

SystemId = Literal["fantui", "c919-etras"]


@dataclass(frozen=True)
class TimelineEvent:
    """A single (time, action) entry authored by the user.

    For `set_input`:
        target = input field name (e.g. "tra_deg", "radio_altitude_ft")
        value  = scalar or bool
    For `ramp_input`:
        target = input field name
        value  = endpoint scalar
        duration_s = ramp duration; linear interpolation from current value
    For `inject_fault` / `clear_fault`:
        target = fault id (e.g. "sw1:stuck_off")
        value  = ignored (None)
        duration_s (on inject_fault) = auto-clear after N seconds; None = until clear_fault
    For `mark_phase`:
        target = phase name
        value  = None
    For `assert_condition`:
        target = condition key (e.g. "logic4_active", "thr_lock_state")
        value  = expected value
    For `start_deploy_sequence`:
        target = "descent_to_deploy"   (only this key supported in PR-1)
        value  = target TRA deg (e.g. -26)
        duration_s = total ramp duration (default 8.0)
    """

    t_s: float
    kind: str
    target: str
    value: Any = None
    duration_s: float | None = None
    phase: str = ""          # optional phase label
    note: str = ""

    def __post_init__(self) -> None:
        if self.kind not in EVENT_KINDS:
            raise ValueError(f"unknown event kind: {self.kind!r}; expected one of {EVENT_KINDS}")
        if self.t_s < 0:
            raise ValueError(f"t_s must be non-negative; got {self.t_s}")
        if self.kind == "ramp_input" and (self.duration_s is None or self.duration_s <= 0):
            raise ValueError("ramp_input requires positive duration_s")
        if self.kind == "inject_fault" and self.duration_s is not None and self.duration_s <= 0:
            raise ValueError("inject_fault duration_s must be positive (or null for open-ended)")
        if self.kind == "start_deploy_sequence" and self.duration_s is not None and self.duration_s <= 0:
            raise ValueError("start_deploy_sequence duration_s must be positive")


@dataclass(frozen=True)
class FaultScheduleEntry:
    """Internal compiled form of `inject_fault` events.

    Active on [start_s, end_s). end_s = math.inf means "until end of sim".
    """

    node_id: str
    fault_type: str
    start_s: float
    end_s: float

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("FaultScheduleEntry.node_id must be non-empty")
        if self.start_s < 0:
            raise ValueError(f"start_s must be non-negative; got {self.start_s}")
        if self.end_s <= self.start_s:
            raise ValueError(
                f"end_s ({self.end_s}) must be > start_s ({self.start_s})"
            )

    def is_active_at(self, t_s: float) -> bool:
        return self.start_s <= t_s < self.end_s


@dataclass
class Timeline:
    """Top-level user-authored simulation script."""

    system: SystemId
    step_s: float
    duration_s: float
    initial_inputs: dict[str, Any] = field(default_factory=dict)
    events: list[TimelineEvent] = field(default_factory=list)
    # Flat static fault_schedule (backward compat shim for pre-existing
    # static fault_injections). Equivalent to inject_fault events with
    # start_s=0 / end_s=duration_s.
    fault_schedule: list[FaultScheduleEntry] = field(default_factory=list)
    title: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if self.step_s <= 0:
            raise ValueError(f"step_s must be positive; got {self.step_s}")
        if self.duration_s <= 0:
            raise ValueError(f"duration_s must be positive; got {self.duration_s}")
        if self.system not in ("fantui", "c919-etras"):
            raise ValueError(f"unknown system {self.system!r}")


@dataclass
class AssertionResult:
    """Outcome of one `assert_condition` event."""

    at_s: float
    target: str
    expected: Any
    observed: Any
    passed: bool
    note: str = ""


@dataclass
class TraceFrame:
    """Per-tick execution snapshot."""

    tick: int
    t_s: float
    phase: str                     # last-seen mark_phase label
    inputs: dict[str, Any]         # resolved inputs after set_input / ramp_input
    outputs: dict[str, Any]        # controller outputs this tick
    logic_states: dict[str, str]   # {"logic1": "active"|"blocked"|"idle", ...}
    active_faults: list[str]       # fault ids active this tick (e.g. ["sw1:stuck_off"])
    events_fired: list[str]        # event indices fired this tick (audit)


@dataclass
class TimelineOutcome:
    """Derived summary from frames."""

    deployed_successfully: bool
    thr_lock_released: bool
    logic_first_active_t_s: dict[str, float]  # e.g. {"logic1": 0.3, "logic4": 14.2}
    logic_first_blocked_t_s: dict[str, float]
    failure_cascade: list[dict[str, Any]]     # [{at_s, trigger_fault, broken_gate, downstream}]


@dataclass
class TimelineTrace:
    """Full simulation output."""

    timeline: Timeline
    frames: list[TraceFrame]
    assertions: list[AssertionResult]
    outcome: TimelineOutcome
    # Event-driven compression for UI: only frames where logic_states or
    # active_faults differ from the previous frame.
    transitions: list[TraceFrame] = field(default_factory=list)
