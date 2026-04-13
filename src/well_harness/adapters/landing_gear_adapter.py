from __future__ import annotations

from typing import Any, Mapping

from well_harness.controller_adapter import ControllerTruthMetadata, GenericTruthEvaluation
from well_harness.system_spec import (
    AcceptanceScenarioSpec,
    ComponentSpec,
    ControlSystemWorkbenchSpec,
    FaultModeSpec,
    KnowledgeCaptureSpec,
    LogicConditionSpec,
    LogicNodeSpec,
    SteadySignalSpec,
    TimedTransitionSpec,
    default_workbench_clarification_questions,
    workbench_spec_to_dict,
)


LANDING_GEAR_SYSTEM_ID = "minimal_landing_gear_extension"
LANDING_GEAR_SOURCE_OF_TRUTH = "src/well_harness/adapters/landing_gear_adapter.py"
LANDING_GEAR_PRESSURE_THRESHOLD_PSI = 2200.0
LANDING_GEAR_COMPLETE_POSITION_PERCENT = 99.0

LANDING_GEAR_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id="landing-gear-controller-adapter",
    system_id=LANDING_GEAR_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=LANDING_GEAR_SOURCE_OF_TRUTH,
    description="Minimal landing-gear extension truth adapter used to prove adapter-only runtime generalization.",
)


def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
    if key not in snapshot:
        raise KeyError(f"missing snapshot value: {key}")
    return snapshot[key]


def _snapshot_bool(snapshot: Mapping[str, Any], key: str) -> bool:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    raise TypeError(f"snapshot value {key!r} must be a bool-compatible value")


def _snapshot_float(snapshot: Mapping[str, Any], key: str) -> float:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        raise TypeError(f"snapshot value {key!r} must be numeric")
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"snapshot value {key!r} must be numeric")


def _snapshot_str(snapshot: Mapping[str, Any], key: str) -> str:
    value = _require_snapshot_value(snapshot, key)
    if not isinstance(value, str):
        raise TypeError(f"snapshot value {key!r} must be a string")
    return value


def build_landing_gear_workbench_spec() -> dict[str, Any]:
    spec = ControlSystemWorkbenchSpec(
        system_id=LANDING_GEAR_SYSTEM_ID,
        title="Minimal Landing-Gear Extension Control",
        objective="Release the uplock and drive extension once the handle is selected down and hydraulic pressure is healthy.",
        source_of_truth=LANDING_GEAR_SOURCE_OF_TRUTH,
        components=(
            ComponentSpec(
                id="gear_handle_position",
                label="Gear Handle",
                kind="pilot_input",
                state_shape="discrete",
                unit="state",
                description="Landing-gear cockpit handle position.",
                allowed_states=("UP", "DOWN"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="hydraulic_pressure_psi",
                label="Hyd Pressure",
                kind="sensor",
                state_shape="analog",
                unit="psi",
                description="Extension hydraulic pressure feeding the selector valve and actuator.",
                allowed_range=(0.0, 3000.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="uplock_released",
                label="Uplock Released",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="Discrete indication that the mechanical uplock has released.",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="selector_valve_cmd",
                label="Selector Valve Command",
                kind="command",
                state_shape="binary",
                unit="state",
                description="Command sent once the handle and pressure conditions are satisfied.",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="extend_actuator_cmd",
                label="Extend Actuator Command",
                kind="command",
                state_shape="binary",
                unit="state",
                description="Extension actuator drive command after uplock release.",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="gear_position_percent",
                label="Gear Position",
                kind="sensor",
                state_shape="analog",
                unit="percent",
                description="Landing-gear extension progress.",
                allowed_range=(0.0, 100.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="downlock_engaged",
                label="Downlock Engaged",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="Discrete indication that the gear reached the downlocked state.",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
        ),
        logic_nodes=(
            LogicNodeSpec(
                id="lg_l1_handle_and_pressure",
                label="LG-L1",
                description="The selector valve may energize only when the gear handle is down and hydraulic pressure is above the extension threshold.",
                conditions=(
                    LogicConditionSpec(
                        name="gear_handle_position",
                        source_component_id="gear_handle_position",
                        comparison="==",
                        threshold_value="DOWN",
                        note="Extension starts only after the pilot selects DOWN.",
                    ),
                    LogicConditionSpec(
                        name="hydraulic_pressure_psi",
                        source_component_id="hydraulic_pressure_psi",
                        comparison=">=",
                        threshold_value=LANDING_GEAR_PRESSURE_THRESHOLD_PSI,
                        note="Healthy pressure is required before commanding the selector valve.",
                    ),
                ),
                downstream_component_ids=("selector_valve_cmd",),
                evidence_priority="high",
            ),
            LogicNodeSpec(
                id="lg_l2_extend_after_uplock_release",
                label="LG-L2",
                description="The extend actuator may drive only after the selector valve is commanded and the uplock is confirmed released.",
                conditions=(
                    LogicConditionSpec(
                        name="selector_valve_cmd",
                        source_component_id="selector_valve_cmd",
                        comparison="==",
                        threshold_value=1,
                        note="The extension actuator depends on the upstream valve command.",
                    ),
                    LogicConditionSpec(
                        name="uplock_released",
                        source_component_id="uplock_released",
                        comparison="==",
                        threshold_value=1,
                        note="The gear must be mechanically released before extension drive continues.",
                    ),
                ),
                downstream_component_ids=("extend_actuator_cmd",),
                evidence_priority="high",
            ),
        ),
        acceptance_scenarios=(
            AcceptanceScenarioSpec(
                id="handle_down_nominal_extension",
                label="Handle Down Nominal Extension",
                description="Nominal extension path from handle-down through full downlock.",
                time_scale_factor=1.0,
                total_duration_s=6.0,
                monitored_signal_ids=(
                    "hydraulic_pressure_psi",
                    "selector_valve_cmd",
                    "uplock_released",
                    "extend_actuator_cmd",
                    "gear_position_percent",
                    "downlock_engaged",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="selector_valve_cmd",
                        start_s=0.0,
                        end_s=0.5,
                        start_value=0.0,
                        end_value=1.0,
                        unit="state",
                        note="Selector valve energizes immediately after the handle/pressure conditions are satisfied.",
                    ),
                    TimedTransitionSpec(
                        signal_id="uplock_released",
                        start_s=0.3,
                        end_s=1.0,
                        start_value=0.0,
                        end_value=1.0,
                        unit="state",
                        note="The uplock releases shortly after selector-valve command.",
                    ),
                    TimedTransitionSpec(
                        signal_id="gear_position_percent",
                        start_s=1.0,
                        end_s=5.5,
                        start_value=0.0,
                        end_value=100.0,
                        unit="percent",
                        note="The gear extends to full downlock travel.",
                    ),
                    TimedTransitionSpec(
                        signal_id="downlock_engaged",
                        start_s=5.0,
                        end_s=5.8,
                        start_value=0.0,
                        end_value=1.0,
                        unit="state",
                        note="The downlock indication turns on at the end of travel.",
                    ),
                ),
                completion_condition="extend_actuator_cmd == 1 and gear_position_percent >= 99 and downlock_engaged == 1",
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="gear_handle_position",
                        value="DOWN",
                        unit="state",
                        note="Pilot holds the gear handle DOWN for the entire extension sequence.",
                    ),
                    SteadySignalSpec(
                        signal_id="hydraulic_pressure_psi",
                        value=2850.0,
                        unit="psi",
                        note="Nominal extension pressure remains above the release threshold.",
                    ),
                ),
            ),
        ),
        fault_modes=(
            FaultModeSpec(
                id="uplock_stuck_locked",
                target_component_id="uplock_released",
                fault_kind="latched_no_unlock",
                symptom="Selector valve energizes but the uplock indication never releases, so extension cannot continue.",
                reasoning_scope_component_ids=("gear_handle_position", "hydraulic_pressure_psi", "selector_valve_cmd", "uplock_released"),
                expected_diagnostic_sections=("symptom", "blocked_logic", "repair_hint"),
                optimization_prompt="Check whether uplock release timing and selector valve evidence should be correlated in future maintenance traces.",
            ),
            FaultModeSpec(
                id="hydraulic_pressure_bias_low",
                target_component_id="hydraulic_pressure_psi",
                fault_kind="bias_low",
                symptom="Displayed hydraulic pressure stays below the threshold, blocking selector-valve command.",
                reasoning_scope_component_ids=("gear_handle_position", "hydraulic_pressure_psi", "selector_valve_cmd"),
                expected_diagnostic_sections=("symptom", "blocked_logic", "repair_hint"),
                optimization_prompt="Track pressure-sensor calibration drift against commanded extension attempts.",
            ),
        ),
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=KnowledgeCaptureSpec(
            incident_fields=("reported_condition", "captured_snapshot", "blocked_logic"),
            resolution_fields=("confirmed_root_cause", "repair_action", "validation_after_fix"),
            optimization_fields=("residual_risk", "follow_up_monitoring"),
        ),
        tags=("landing-gear", "runtime-generalization-proof", "second-system"),
    )
    return workbench_spec_to_dict(spec)


class LandingGearControllerAdapter:
    metadata = LANDING_GEAR_CONTROLLER_METADATA

    def load_spec(self) -> dict[str, Any]:
        return build_landing_gear_workbench_spec()

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        gear_handle_position = _snapshot_str(snapshot, "gear_handle_position")
        hydraulic_pressure_psi = _snapshot_float(snapshot, "hydraulic_pressure_psi")
        uplock_released = _snapshot_bool(snapshot, "uplock_released")
        gear_position_percent = _snapshot_float(snapshot, "gear_position_percent")
        downlock_engaged = _snapshot_bool(snapshot, "downlock_engaged")

        handle_down = gear_handle_position == "DOWN"
        pressure_ok = hydraulic_pressure_psi >= LANDING_GEAR_PRESSURE_THRESHOLD_PSI
        selector_valve_cmd = handle_down and pressure_ok
        extend_actuator_cmd = selector_valve_cmd and uplock_released
        completion_reached = (
            extend_actuator_cmd
            and gear_position_percent >= LANDING_GEAR_COMPLETE_POSITION_PERCENT
            and downlock_engaged
        )

        active_logic_node_ids: list[str] = []
        if selector_valve_cmd:
            active_logic_node_ids.append("lg_l1_handle_and_pressure")
        if extend_actuator_cmd:
            active_logic_node_ids.append("lg_l2_extend_after_uplock_release")

        blocked_reasons: list[str] = []
        if not handle_down:
            blocked_reasons.append("gear_handle_position must be DOWN")
        if not pressure_ok:
            blocked_reasons.append(
                f"hydraulic_pressure_psi below {LANDING_GEAR_PRESSURE_THRESHOLD_PSI:.1f}"
            )
        if selector_valve_cmd and not uplock_released:
            blocked_reasons.append("uplock_released is still false")
        if extend_actuator_cmd and gear_position_percent < LANDING_GEAR_COMPLETE_POSITION_PERCENT:
            blocked_reasons.append(
                f"gear_position_percent below {LANDING_GEAR_COMPLETE_POSITION_PERCENT:.1f}"
            )
        if gear_position_percent >= LANDING_GEAR_COMPLETE_POSITION_PERCENT and not downlock_engaged:
            blocked_reasons.append("downlock_engaged is still false")

        summary = (
            "Landing gear extension completed."
            if completion_reached
            else "Landing gear extension remains blocked or incomplete."
        )
        return GenericTruthEvaluation(
            system_id=LANDING_GEAR_SYSTEM_ID,
            active_logic_node_ids=tuple(active_logic_node_ids),
            asserted_component_values={
                "gear_handle_position": gear_handle_position,
                "hydraulic_pressure_psi": hydraulic_pressure_psi,
                "uplock_released": uplock_released,
                "selector_valve_cmd": selector_valve_cmd,
                "extend_actuator_cmd": extend_actuator_cmd,
                "gear_position_percent": gear_position_percent,
                "downlock_engaged": downlock_engaged,
            },
            completion_reached=completion_reached,
            blocked_reasons=tuple(blocked_reasons),
            summary=summary,
        )


def build_landing_gear_controller_adapter() -> LandingGearControllerAdapter:
    return LandingGearControllerAdapter()
