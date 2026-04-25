"""Full-process failure-rate simulation engine.

A unified timeline player that drives either the FANTUI reverser demo
(stateless + plant-evolving DeployController) or the C919 E-TRAS
stateful 12-step tick adapter from a single (time, event) table,
producing per-tick traces for failure-attribution analysis.

Core concepts:
    Timeline        user-authored (t_s, phase, event) table
    TimelineEvent   set_input / ramp_input / inject_fault / clear_fault / mark_phase / assert_condition / start_deploy_sequence
    Executor        system-specific adapter (FANTUI | C919) that runs one tick
    TimelinePlayer  fixed tick order: events → faults → executor.tick → assertions
    TimelineTrace   per-tick frames + derived transitions + assertion verdicts
"""

from well_harness.timeline_engine.schema import (
    Timeline,
    TimelineEvent,
    TimelineTrace,
    TraceFrame,
    FaultScheduleEntry,
    AssertionResult,
    TimelineOutcome,
)
from well_harness.timeline_engine.fault_schedule import ActiveFaultSet, compile_active_faults
from well_harness.timeline_engine.validator import ValidationError, parse_timeline
from well_harness.timeline_engine.player import TimelinePlayer
from well_harness.timeline_engine.executors.base import Executor, ExecutorTickResult

__all__ = [
    "Timeline",
    "TimelineEvent",
    "TimelineTrace",
    "TraceFrame",
    "FaultScheduleEntry",
    "AssertionResult",
    "TimelineOutcome",
    "ActiveFaultSet",
    "compile_active_faults",
    "ValidationError",
    "parse_timeline",
    "TimelinePlayer",
    "Executor",
    "ExecutorTickResult",
]
