"""TimelinePlayer: the core loop.

Fixed per-tick order (Codex architecture guidance):
    1. Event application (set_input / ramp_input / mark_phase / start_deploy_sequence)
    2. Fault application (compile ActiveFaultSet from schedule)
    3. Executor.tick(inputs, active_faults) → outputs + logic_states
    4. Assertion check (assert_condition events AT this tick)

Time semantics:
    - Tick `n` covers simulated interval [n * step_s, (n+1) * step_s)
    - An event at t_s fires on the FIRST tick whose interval contains t_s.
    - Faults use half-open [start_s, end_s).
    - assert_condition at t_s is evaluated on the tick whose OUTPUT represents time t_s
      (i.e. after control logic has advanced through t_s).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from well_harness.timeline_engine.executors.base import Executor
from well_harness.timeline_engine.fault_schedule import (
    compile_active_faults,
    compile_fault_schedule,
)
from well_harness.timeline_engine.schema import (
    AssertionResult,
    Timeline,
    TimelineEvent,
    TimelineOutcome,
    TimelineTrace,
    TraceFrame,
)

_FLOAT_EPS = 1e-9


@dataclass
class _RampState:
    """Active ramp on one input field."""

    field: str
    start_t: float
    end_t: float
    start_value: float
    end_value: float

    def value_at(self, t_s: float) -> float:
        if t_s <= self.start_t:
            return self.start_value
        if t_s >= self.end_t:
            return self.end_value
        frac = (t_s - self.start_t) / max(_FLOAT_EPS, self.end_t - self.start_t)
        return self.start_value + frac * (self.end_value - self.start_value)


class TimelinePlayer:
    """Drives an Executor from a Timeline."""

    def __init__(self, timeline: Timeline, executor: Executor) -> None:
        if executor.system_id != timeline.system:
            raise ValueError(
                f"executor system_id {executor.system_id!r} does not match timeline.system {timeline.system!r}"
            )
        self._timeline = timeline
        self._executor = executor
        self._compiled_faults = compile_fault_schedule(timeline)

    def run(self) -> TimelineTrace:
        timeline = self._timeline
        executor = self._executor

        executor.reset(timeline.initial_inputs)

        # Sim state
        inputs = dict(timeline.initial_inputs)
        ramps: list[_RampState] = []
        current_phase = ""
        # Index into events; events are sorted by t_s
        event_cursor = 0
        events = timeline.events

        # Fault-attribution bookkeeping
        first_active_t_s: dict[str, float] = {}
        first_blocked_t_s: dict[str, float] = {}
        prev_logic_states: dict[str, str] = {}
        failure_cascade: list[dict[str, Any]] = []

        frames: list[TraceFrame] = []
        transitions: list[TraceFrame] = []
        assertion_results: list[AssertionResult] = []

        total_ticks = int(math.ceil(timeline.duration_s / timeline.step_s))

        for tick in range(total_ticks):
            tick_start = tick * timeline.step_s
            tick_end = tick_start + timeline.step_s

            events_fired_ids: list[str] = []

            # --- 1. Event application ---
            while event_cursor < len(events) and events[event_cursor].t_s < tick_end - _FLOAT_EPS:
                event = events[event_cursor]
                if event.t_s < tick_start - _FLOAT_EPS:
                    # Already passed; shouldn't happen due to sort but skip safely.
                    event_cursor += 1
                    continue
                self._apply_event(event, inputs, ramps, current_phase_ref=None)
                if event.kind == "mark_phase":
                    current_phase = event.target or event.phase or current_phase
                events_fired_ids.append(f"{event.kind}@{event.t_s:.3f}:{event.target}")
                event_cursor += 1

            # Resolve active ramps
            for ramp in ramps:
                inputs[ramp.field] = ramp.value_at(tick_end)

            # --- 2. Fault application ---
            active_set = compile_active_faults(self._compiled_faults, tick_end - _FLOAT_EPS)
            active_fault_ids = active_set.ids

            # --- 3. Executor tick ---
            result = executor.tick(
                t_s=tick_end,
                dt_s=timeline.step_s,
                inputs=dict(inputs),
                active_faults=active_fault_ids,
            )
            merged_inputs = dict(inputs)
            if result.resolved_inputs:
                merged_inputs.update(result.resolved_inputs)

            logic_states = dict(result.logic_states)

            # --- Attribution & transitions ---
            for node_id, state in logic_states.items():
                if state == "active" and node_id not in first_active_t_s:
                    first_active_t_s[node_id] = tick_end
                if state == "blocked" and node_id not in first_blocked_t_s:
                    first_blocked_t_s[node_id] = tick_end
            # Detect "first broken gate this tick" — a gate flipping from active → blocked.
            # Iterate the executor's canonical logic_node_ids ordering so
            # attribution is deterministic regardless of how the executor
            # built its logic_states dict. Only record when a fault is
            # actually active: the nominal FANTUI lifecycle flips L1 from
            # active → blocked post-deploy (reverser_not_deployed_eec goes
            # False once the plant starts moving), and that is not a
            # failure — it's the intended handoff to L2/L3/L4 (Codex PR-2
            # MAJOR #2).
            if active_fault_ids:
                for node_id in executor.logic_node_ids:
                    if node_id not in logic_states:
                        continue
                    state = logic_states[node_id]
                    prev = prev_logic_states.get(node_id)
                    if prev == "active" and state == "blocked":
                        failure_cascade.append(
                            {
                                "at_s": tick_end,
                                "broken_gate": node_id,
                                "active_faults": list(active_fault_ids),
                            }
                        )
                        break  # Only the first broken gate per tick (Codex guidance)

            frame = TraceFrame(
                tick=tick,
                t_s=tick_end,
                phase=current_phase,
                inputs=merged_inputs,
                outputs=dict(result.outputs),
                logic_states=logic_states,
                active_faults=list(active_fault_ids),
                events_fired=events_fired_ids,
            )
            frames.append(frame)

            # Transitions: only keep frames where logic_states or faults changed
            if (
                not transitions
                or transitions[-1].logic_states != logic_states
                or transitions[-1].active_faults != active_fault_ids
            ):
                transitions.append(frame)

            prev_logic_states = logic_states

            # --- 4. Assertions evaluated on this tick ---
            for event in events:
                if (
                    event.kind == "assert_condition"
                    and tick_start - _FLOAT_EPS <= event.t_s < tick_end - _FLOAT_EPS
                ):
                    assertion_results.append(
                        self._evaluate_assertion(event, result.outputs, logic_states)
                    )

        outcome = self._derive_outcome(
            frames,
            first_active_t_s,
            first_blocked_t_s,
            failure_cascade,
            executor.logic_node_ids,
        )
        return TimelineTrace(
            timeline=timeline,
            frames=frames,
            assertions=assertion_results,
            outcome=outcome,
            transitions=transitions,
        )

    # ---- helpers -------------------------------------------------------

    @staticmethod
    def _apply_event(
        event: TimelineEvent,
        inputs: dict[str, Any],
        ramps: list[_RampState],
        current_phase_ref: None,
    ) -> None:
        """Mutate `inputs` / `ramps` in place.

        `inject_fault` / `clear_fault` events are compiled into the
        schedule up-front, so this function intentionally does nothing
        for them at event-application time.
        `assert_condition` is handled in the assertion step.
        `mark_phase` is handled by the caller (to update current_phase).
        """
        kind = event.kind
        if kind == "set_input":
            inputs[event.target] = event.value
            # Cancel any active ramp on this field.
            ramps[:] = [r for r in ramps if r.field != event.target]
            return
        if kind == "ramp_input":
            start_value = _coerce_float(inputs.get(event.target, 0.0))
            end_value = _coerce_float(event.value)
            duration = float(event.duration_s or 0.0)
            # Remove any existing ramp on this field, then add the new one.
            ramps[:] = [r for r in ramps if r.field != event.target]
            ramps.append(
                _RampState(
                    field=event.target,
                    start_t=event.t_s,
                    end_t=event.t_s + duration,
                    start_value=start_value,
                    end_value=end_value,
                )
            )
            return
        if kind == "start_deploy_sequence":
            # Minimal PR-1 shorthand: ramp tra_deg to event.value over duration_s
            # (default 8 s). sw1/sw2 triggers emerge naturally from the TRA ramp
            # via the executor's latched switch model.
            duration = float(event.duration_s or 8.0)
            start_value = _coerce_float(inputs.get("tra_deg", 0.0))
            end_value = _coerce_float(event.value)
            ramps[:] = [r for r in ramps if r.field != "tra_deg"]
            ramps.append(
                _RampState(
                    field="tra_deg",
                    start_t=event.t_s,
                    end_t=event.t_s + duration,
                    start_value=start_value,
                    end_value=end_value,
                )
            )
            return
        # mark_phase / assert_condition / inject_fault / clear_fault: no direct input mutation.

    @staticmethod
    def _evaluate_assertion(
        event: TimelineEvent,
        outputs: dict[str, Any],
        logic_states: dict[str, str],
    ) -> AssertionResult:
        target = event.target
        expected = event.value

        # Assertion target may reference either outputs (e.g. "logic4_active")
        # or logic_states (e.g. "logic4" == "active").
        if target in outputs:
            observed = outputs[target]
        elif target in logic_states:
            observed = logic_states[target]
        else:
            return AssertionResult(
                at_s=event.t_s,
                target=target,
                expected=expected,
                observed=None,
                passed=False,
                note=f"assertion target {target!r} not found in outputs or logic_states",
            )
        return AssertionResult(
            at_s=event.t_s,
            target=target,
            expected=expected,
            observed=observed,
            passed=observed == expected,
            note=event.note,
        )

    def _derive_outcome(
        self,
        frames: list[TraceFrame],
        first_active_t_s: dict[str, float],
        first_blocked_t_s: dict[str, float],
        failure_cascade: list[dict[str, Any]],
        logic_node_ids: tuple[str, ...],
    ) -> TimelineOutcome:
        if not frames:
            return TimelineOutcome(
                deployed_successfully=False,
                thr_lock_released=False,
                logic_first_active_t_s={},
                logic_first_blocked_t_s={},
                failure_cascade=[],
            )
        # thr_lock release is the authoritative "deployed" signal — any
        # gate-stuck fault that prevents the terminal unlock command from
        # firing (e.g. thr_lock:cmd_blocked) must flip deployed_successfully
        # back to False even if L4 reported active mid-trace.
        thr_released = any(
            frame.outputs.get("throttle_electronic_lock_release_cmd") is True
            or frame.outputs.get("throttle_lock_release_cmd") is True
            or frame.outputs.get("thr_lock") == "active"
            for frame in frames
        )
        l4_ever_active = any(
            frame.logic_states.get("logic4") == "active"
            or frame.outputs.get("logic4_active") is True
            for frame in frames
        )
        deployed = l4_ever_active and thr_released
        return TimelineOutcome(
            deployed_successfully=deployed,
            thr_lock_released=thr_released,
            logic_first_active_t_s={k: first_active_t_s[k] for k in logic_node_ids if k in first_active_t_s},
            logic_first_blocked_t_s={k: first_blocked_t_s[k] for k in logic_node_ids if k in first_blocked_t_s},
            failure_cascade=failure_cascade,
        )


def _coerce_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
