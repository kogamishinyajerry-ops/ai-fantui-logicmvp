"""Timeline engine (PR-1) unit tests.

A stub Executor records every tick's (inputs, faults) pair so we can
assert the player's tick order, fault windowing, ramp interpolation,
and assertion semantics WITHOUT depending on either real control system.
PR-2 and PR-3 will test the FANTUI and C919 executors against their
respective controller contracts.
"""

from __future__ import annotations

import math
import unittest
from dataclasses import dataclass, field

from well_harness.timeline_engine import (
    Executor,
    ExecutorTickResult,
    Timeline,
    TimelineEvent,
    TimelinePlayer,
    ValidationError,
    compile_active_faults,
    parse_timeline,
)
from well_harness.timeline_engine.fault_schedule import compile_fault_schedule


@dataclass
class RecordingExecutor:
    """Stub executor that records each tick and returns scripted logic_states."""

    logic_program: dict[float, dict[str, str]] = field(default_factory=dict)
    # Output program: per-tick scripted outputs dict.
    output_program: dict[float, dict] = field(default_factory=dict)
    system_id: str = "fantui"
    logic_node_ids: tuple[str, ...] = ("logic1", "logic2", "logic3", "logic4")

    # Populated during run
    calls: list[dict] = field(default_factory=list)

    def reset(self, initial_inputs):
        self.calls.clear()

    def tick(self, t_s, dt_s, inputs, active_faults) -> ExecutorTickResult:
        self.calls.append(
            {
                "t_s": round(t_s, 6),
                "dt_s": dt_s,
                "inputs": dict(inputs),
                "active_faults": list(active_faults),
            }
        )
        # Pick the scripted state whose key is the largest key <= t_s.
        logic_states = self._latest(self.logic_program, t_s)
        outputs = self._latest(self.output_program, t_s) or {}
        return ExecutorTickResult(outputs=outputs, logic_states=logic_states)

    @staticmethod
    def _latest(program, t_s):
        # Use strict `<` to match the player's half-open tick interval
        # semantic: a scripted state change at t=T applies to the tick
        # whose interval [start, end) contains T — i.e. starting from
        # the first tick whose tick_end > T.
        active_key = None
        for key in program:
            if key < t_s - 1e-9 and (active_key is None or key > active_key):
                active_key = key
        return dict(program[active_key]) if active_key is not None else {}


class ValidatorTests(unittest.TestCase):
    def test_accepts_minimal_timeline(self):
        tl = parse_timeline(
            {
                "system": "fantui",
                "step_s": 0.1,
                "duration_s": 1.0,
                "events": [],
            }
        )
        self.assertEqual(tl.system, "fantui")
        self.assertEqual(tl.step_s, 0.1)

    def test_rejects_unknown_system(self):
        with self.assertRaises(ValidationError) as ctx:
            parse_timeline({"system": "xyz", "step_s": 0.1, "duration_s": 1.0})
        self.assertEqual(ctx.exception.field, "system")

    def test_rejects_nonpositive_step_s(self):
        with self.assertRaises(ValidationError):
            parse_timeline({"system": "fantui", "step_s": 0, "duration_s": 1.0})

    def test_rejects_ramp_without_duration(self):
        with self.assertRaises(ValidationError):
            parse_timeline(
                {
                    "system": "fantui",
                    "step_s": 0.1,
                    "duration_s": 2.0,
                    "events": [
                        {"t_s": 0.5, "kind": "ramp_input", "target": "tra_deg", "value": -14}
                    ],
                }
            )

    def test_sorts_events_by_time(self):
        tl = parse_timeline(
            {
                "system": "fantui",
                "step_s": 0.1,
                "duration_s": 5.0,
                "events": [
                    {"t_s": 2.0, "kind": "set_input", "target": "tra_deg", "value": -14},
                    {"t_s": 0.5, "kind": "set_input", "target": "tra_deg", "value": -2},
                ],
            }
        )
        times = [e.t_s for e in tl.events]
        self.assertEqual(times, [0.5, 2.0])


class FaultScheduleTests(unittest.TestCase):
    def test_inject_then_clear_half_open(self):
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=5.0,
            events=[
                TimelineEvent(t_s=1.0, kind="inject_fault", target="sw1:stuck_off"),
                TimelineEvent(t_s=3.0, kind="clear_fault", target="sw1:stuck_off"),
            ],
        )
        schedule = compile_fault_schedule(tl)
        self.assertEqual(len(schedule), 1)
        entry = schedule[0]
        self.assertEqual((entry.node_id, entry.fault_type), ("sw1", "stuck_off"))
        # [1.0, 3.0) → active at 1.0 and 2.999, inactive at 3.0
        self.assertFalse(entry.is_active_at(0.999))
        self.assertTrue(entry.is_active_at(1.0))
        self.assertTrue(entry.is_active_at(2.999))
        self.assertFalse(entry.is_active_at(3.0))

    def test_inject_with_duration(self):
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=5.0,
            events=[
                TimelineEvent(t_s=1.0, kind="inject_fault", target="sw2:stuck_on", duration_s=0.5),
            ],
        )
        schedule = compile_fault_schedule(tl)
        entry = schedule[0]
        self.assertAlmostEqual(entry.end_s, 1.5)

    def test_inject_without_clear_holds_until_end(self):
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=5.0,
            events=[
                TimelineEvent(t_s=2.0, kind="inject_fault", target="sw1:stuck_off"),
            ],
        )
        schedule = compile_fault_schedule(tl)
        # Clamped to duration_s
        self.assertEqual(schedule[0].end_s, 5.0)

    def test_compile_active_faults_half_open(self):
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=5.0,
            events=[
                TimelineEvent(t_s=1.0, kind="inject_fault", target="sw1:stuck_off"),
                TimelineEvent(t_s=3.0, kind="clear_fault", target="sw1:stuck_off"),
            ],
        )
        schedule = compile_fault_schedule(tl)
        self.assertEqual(compile_active_faults(schedule, 0.5).ids, [])
        self.assertEqual(compile_active_faults(schedule, 1.0).ids, ["sw1:stuck_off"])
        self.assertEqual(compile_active_faults(schedule, 3.0).ids, [])


class PlayerTickOrderTests(unittest.TestCase):
    """Verify events → faults → executor.tick → assertions order."""

    def test_set_input_fires_before_executor_tick(self):
        executor = RecordingExecutor(
            logic_program={0.0: {"logic1": "idle"}},
        )
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=0.3,
            initial_inputs={"tra_deg": 0.0},
            events=[
                TimelineEvent(t_s=0.1, kind="set_input", target="tra_deg", value=-7.0),
            ],
        )
        trace = TimelinePlayer(tl, executor).run()
        # Tick 0 (interval [0, 0.1)): event at 0.1 NOT yet fired → tra_deg still 0.0
        # Tick 1 (interval [0.1, 0.2)): event fires → tra_deg becomes -7.0
        self.assertEqual(executor.calls[0]["inputs"]["tra_deg"], 0.0)
        self.assertEqual(executor.calls[1]["inputs"]["tra_deg"], -7.0)
        self.assertEqual(len(trace.frames), 3)

    def test_fault_half_open_reaches_executor(self):
        executor = RecordingExecutor()
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=0.5,
            events=[
                TimelineEvent(t_s=0.2, kind="inject_fault", target="sw1:stuck_off"),
                TimelineEvent(t_s=0.4, kind="clear_fault", target="sw1:stuck_off"),
            ],
        )
        TimelinePlayer(tl, executor).run()
        # tick 0: t_s=0.1 → no fault
        # tick 1: t_s=0.2 → wait, fault is active on [0.2, 0.4). We sample at
        #   `tick_end - eps`. tick 1 covers [0.1, 0.2), sample time ≈ 0.2-eps → NOT yet active.
        # tick 2: [0.2, 0.3), sample ≈ 0.3-eps → active.
        # tick 3: [0.3, 0.4), sample ≈ 0.4-eps → active.
        # tick 4: [0.4, 0.5), sample ≈ 0.5-eps → cleared.
        fault_per_tick = [call["active_faults"] for call in executor.calls]
        self.assertEqual(fault_per_tick[0], [])
        self.assertEqual(fault_per_tick[1], [])
        self.assertEqual(fault_per_tick[2], ["sw1:stuck_off"])
        self.assertEqual(fault_per_tick[3], ["sw1:stuck_off"])
        self.assertEqual(fault_per_tick[4], [])


class PlayerRampTests(unittest.TestCase):
    def test_ramp_input_linearly_interpolates(self):
        executor = RecordingExecutor()
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=1.1,
            initial_inputs={"tra_deg": 0.0},
            events=[
                TimelineEvent(
                    t_s=0.1, kind="ramp_input", target="tra_deg", value=-10.0, duration_s=1.0
                ),
            ],
        )
        TimelinePlayer(tl, executor).run()
        # Ramp window [0.1, 1.1). At t=0.1 start_value=0, at 1.1 end_value=-10.
        # tick 1 end (0.2) → 10% of 1s → -1.0
        # tick 5 end (0.6) → 50% → -5.0
        # tick 10 end (1.1) → 100% → -10.0
        self.assertAlmostEqual(executor.calls[1]["inputs"]["tra_deg"], -1.0, places=3)
        self.assertAlmostEqual(executor.calls[5]["inputs"]["tra_deg"], -5.0, places=3)
        self.assertAlmostEqual(executor.calls[10]["inputs"]["tra_deg"], -10.0, places=3)


class PlayerAssertionTests(unittest.TestCase):
    def test_assertion_on_logic_state_records_pass_and_fail(self):
        executor = RecordingExecutor(
            logic_program={
                0.0: {"logic1": "idle", "logic4": "idle"},
                0.3: {"logic1": "active", "logic4": "idle"},
                0.6: {"logic1": "active", "logic4": "active"},
            },
            output_program={0.0: {"logic4_active": False}, 0.6: {"logic4_active": True}},
        )
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=1.0,
            events=[
                TimelineEvent(
                    t_s=0.6, kind="assert_condition", target="logic4", value="active",
                    note="post-deploy",
                ),
                TimelineEvent(
                    t_s=0.2, kind="assert_condition", target="logic4_active", value=True,
                    note="too early — should fail",
                ),
            ],
        )
        trace = TimelinePlayer(tl, executor).run()
        self.assertEqual(len(trace.assertions), 2)
        by_target = {(a.target, a.at_s): a for a in trace.assertions}
        self.assertTrue(by_target[("logic4", 0.6)].passed)
        self.assertFalse(by_target[("logic4_active", 0.2)].passed)


class PlayerOutcomeTests(unittest.TestCase):
    def test_failure_cascade_records_first_broken_gate(self):
        # logic1 flips active at 0.2, then blocked at 0.5 (fault-driven)
        executor = RecordingExecutor(
            logic_program={
                0.0: {"logic1": "idle", "logic2": "idle"},
                0.2: {"logic1": "active", "logic2": "active"},
                0.5: {"logic1": "blocked", "logic2": "active"},
            },
        )
        tl = Timeline(
            system="fantui",
            step_s=0.1,
            duration_s=0.8,
            events=[
                TimelineEvent(t_s=0.5, kind="inject_fault", target="sw1:stuck_off"),
            ],
        )
        trace = TimelinePlayer(tl, executor).run()
        self.assertEqual(len(trace.outcome.failure_cascade), 1)
        cascade = trace.outcome.failure_cascade[0]
        self.assertEqual(cascade["broken_gate"], "logic1")
        self.assertIn("sw1:stuck_off", cascade["active_faults"])

    def test_transitions_compression(self):
        executor = RecordingExecutor(
            logic_program={
                0.0: {"logic1": "idle"},
                0.3: {"logic1": "active"},
            },
        )
        tl = Timeline(system="fantui", step_s=0.1, duration_s=0.6)
        trace = TimelinePlayer(tl, executor).run()
        # frames: 6, but only 2 transition rows (idle → active)
        self.assertEqual(len(trace.frames), 6)
        self.assertEqual(len(trace.transitions), 2)

    def test_executor_system_id_mismatch_raises(self):
        executor = RecordingExecutor(system_id="c919_etras")
        tl = Timeline(system="fantui", step_s=0.1, duration_s=0.3)
        with self.assertRaises(ValueError):
            TimelinePlayer(tl, executor)


if __name__ == "__main__":
    unittest.main()
