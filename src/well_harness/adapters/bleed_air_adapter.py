"""
Bleed Air Valve Controller Adapter

A simplified environmental control system adapter for aircraft bleed-air valve control.
Bleed air is extracted from the engine compressor and used for cabin pressurization,
wing anti-icing, and engine start.

FROZEN (2026-04-20) — demonstrative adapter, no authoritative upstream spec.

Status: frozen per Kogami 2026-04-20 directive. This adapter was built for
capability demonstration (runtime adapter generalization proof), NOT from an
authoritative requirement document. Its thresholds, logic nodes, timing
constants, and test assertions are illustrative and MUST NOT be cited as
truth in certification, testing, external documentation, or customer-facing
material.

See docs/provenance/adapter_truth_levels.md for the registry and upgrade path.
"""
from __future__ import annotations

from typing import Any, Mapping

from well_harness.controller_adapter import (
    ControllerTruthMetadata,
    GenericTruthEvaluation,
    GenericControllerTruthAdapter,
)
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

# ---------------------------------------------------------------------------
# Adapter metadata
# ---------------------------------------------------------------------------
BLEED_AIR_SYSTEM_ID = "bleed-air-valve"
BLEED_AIR_SOURCE_OF_TRUTH = "src/well_harness/adapters/bleed_air_adapter.py"
BLEED_AIR_DESCRIPTION = (
    "Simplified bleed-air valve control for environmental control system. "
    "Commands the bleed-air valve OPEN when inlet pressure is above the minimum "
    "threshold, and CLOSED when pressure drops below threshold or an overpressure "
    "condition is detected."
)

# Threshold constants (psi)
BLEED_AIR_PRESSURE_MIN_PSI = 35.0      # Minimum pressure to keep valve open
BLEED_AIR_PRESSURE_MAX_PSI = 65.0      # Overpressure threshold — close valve
BLEED_AIR_HYSTERESIS_PSI = 3.0         # Deadband to prevent chattering
BLEED_AIR_NOMINAL_OPEN_PSI = 45.0      # Normal operating inlet pressure

BLEED_AIR_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id="bleed-air-valve-controller-adapter",
    system_id=BLEED_AIR_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=BLEED_AIR_SOURCE_OF_TRUTH,
    description=BLEED_AIR_DESCRIPTION,
    truth_level="demonstrative",  # P42: FROZEN · aligned with docs/provenance/adapter_truth_levels.yaml
    status="Frozen",
)


# ---------------------------------------------------------------------------
# Helper: snapshot value extractors
# ---------------------------------------------------------------------------
def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
    """Return the value for key from snapshot, or raise KeyError."""
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


# ---------------------------------------------------------------------------
# Workbench spec builder
# ---------------------------------------------------------------------------
def build_bleed_air_workbench_spec() -> dict[str, Any]:
    spec = ControlSystemWorkbenchSpec(
        system_id=BLEED_AIR_SYSTEM_ID,
        title="Bleed Air Valve Control System",
        objective=(
            "Maintain safe bleed-air supply by commanding the valve OPEN when inlet "
            "pressure is above minimum threshold, and CLOSED when pressure is "
            "insufficient or an overpressure condition is detected."
        ),
        source_of_truth=BLEED_AIR_SOURCE_OF_TRUTH,
        components=(
            # Valve body — the physical valve actuator
            ComponentSpec(
                id="valve_position",
                label="Valve Position",
                kind="sensor",
                state_shape="discrete",
                unit="state",
                description="Current physical position of the bleed-air valve.",
                allowed_states=("CLOSED", "OPEN"),
                monitor_priority="required",
            ),
            # Valve command — output from the control unit
            ComponentSpec(
                id="valve_cmd",
                label="Valve Command",
                kind="command",
                state_shape="binary",
                unit="state",
                description="Command signal from the control unit to the valve actuator (1=open, 0=close).",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
            # Inlet pressure — bleed-air pressure at valve入口
            ComponentSpec(
                id="inlet_pressure",
                label="Inlet Pressure",
                kind="sensor",
                state_shape="analog",
                unit="psi",
                description="Bleed-air pressure at the valve inlet, supplied by the engine compressor.",
                allowed_range=(0.0, 100.0),
                monitor_priority="required",
            ),
            # Outlet pressure — downstream pressure after valve
            ComponentSpec(
                id="outlet_pressure",
                label="Outlet Pressure",
                kind="sensor",
                state_shape="analog",
                unit="psi",
                description="Bleed-air pressure at the valve outlet, feeding the pneumatic system.",
                allowed_range=(0.0, 100.0),
                monitor_priority="required",
            ),
            # Control unit status
            ComponentSpec(
                id="control_unit_ready",
                label="Control Unit Ready",
                kind="sensor",
                state_shape="binary",
                unit="state",
                description="Control unit health and readiness signal.",
                allowed_states=("0", "1"),
                monitor_priority="required",
            ),
        ),
        logic_nodes=(
            # LN1: Open valve when inlet pressure is healthy (above minimum threshold)
            LogicNodeSpec(
                id="valve_open_logic",
                label="LN-Open",
                description=(
                    "The bleed-air valve may open when inlet pressure is above the "
                    "minimum operating threshold and the control unit is ready."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="inlet_pressure_above_min",
                        source_component_id="inlet_pressure",
                        comparison=">=",
                        threshold_value=BLEED_AIR_PRESSURE_MIN_PSI,
                        note="Inlet pressure must be above minimum to safely supply bleed air.",
                    ),
                    LogicConditionSpec(
                        name="control_unit_ready",
                        source_component_id="control_unit_ready",
                        comparison="==",
                        threshold_value=1,
                        note="Control unit must be operational before commanding the valve.",
                    ),
                ),
                downstream_component_ids=("valve_cmd",),
                evidence_priority="high",
            ),
            # LN2: Close valve when pressure is too low OR overpressure is detected
            LogicNodeSpec(
                id="valve_close_logic",
                label="LN-Close",
                description=(
                    "The bleed-air valve must close when inlet pressure drops below "
                    "the minimum threshold (with hysteresis) OR when an overpressure "
                    "condition is detected to protect downstream systems."
                ),
                conditions=(
                    LogicConditionSpec(
                        name="inlet_pressure_below_min_or_overpressure",
                        source_component_id="inlet_pressure",
                        comparison="<",
                        threshold_value=BLEED_AIR_PRESSURE_MIN_PSI - BLEED_AIR_HYSTERESIS_PSI,
                        note="With hysteresis deadband, close if pressure falls below (min - hysteresis).",
                    ),
                ),
                downstream_component_ids=("valve_cmd",),
                evidence_priority="high",
            ),
        ),
        acceptance_scenarios=(
            # Scenario 1: Nominal open — pressure rises above threshold, valve opens
            AcceptanceScenarioSpec(
                id="nominal_open",
                label="Nominal Open — Pressure Rise",
                description=(
                    "Inlet pressure rises from zero to nominal operating pressure. "
                    "Valve command transitions from 0 to 1 when pressure crosses "
                    "the minimum threshold, and valve position follows."
                ),
                time_scale_factor=1.0,
                total_duration_s=6.0,
                monitored_signal_ids=(
                    "inlet_pressure",
                    "valve_cmd",
                    "valve_position",
                    "outlet_pressure",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="inlet_pressure",
                        start_s=0.0,
                        end_s=2.0,
                        start_value=0.0,
                        end_value=BLEED_AIR_NOMINAL_OPEN_PSI,
                        unit="psi",
                        note="Pressure builds up from engine compressor as it accelerates.",
                    ),
                    TimedTransitionSpec(
                        signal_id="valve_cmd",
                        start_s=2.0,
                        end_s=2.5,
                        start_value=0.0,
                        end_value=1.0,
                        unit="state",
                        note="Control unit commands valve OPEN once pressure exceeds minimum threshold.",
                    ),
                    TimedTransitionSpec(
                        signal_id="valve_position",
                        start_s=2.5,
                        end_s=3.5,
                        start_value=0.0,
                        end_value=1.0,
                        unit="state",
                        note="Valve physically travels from CLOSED to OPEN position.",
                    ),
                    TimedTransitionSpec(
                        signal_id="outlet_pressure",
                        start_s=3.5,
                        end_s=5.0,
                        start_value=0.0,
                        end_value=BLEED_AIR_NOMINAL_OPEN_PSI,
                        unit="psi",
                        note="Outlet pressure rises as bleed air flows through open valve.",
                    ),
                ),
                completion_condition=(
                    "valve_cmd == 1 and inlet_pressure >= 40.0 and "
                    "outlet_pressure >= 40.0 and valve_position == 1"
                ),
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="control_unit_ready",
                        value=1,
                        unit="state",
                        note="Control unit is ready throughout the nominal open sequence.",
                    ),
                ),
            ),
            # Scenario 2: Nominal close — pressure drops below hysteresis threshold
            AcceptanceScenarioSpec(
                id="nominal_close",
                label="Nominal Close — Pressure Drop",
                description=(
                    "Engine decelerates, inlet pressure drops below the hysteresis "
                    "threshold. Control unit commands valve CLOSED, and valve "
                    "position follows."
                ),
                time_scale_factor=1.0,
                total_duration_s=6.0,
                monitored_signal_ids=(
                    "inlet_pressure",
                    "valve_cmd",
                    "valve_position",
                    "outlet_pressure",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="inlet_pressure",
                        start_s=0.0,
                        end_s=2.0,
                        start_value=BLEED_AIR_NOMINAL_OPEN_PSI,
                        end_value=0.0,
                        unit="psi",
                        note="Pressure drops as engine decelerates.",
                    ),
                    TimedTransitionSpec(
                        signal_id="valve_cmd",
                        start_s=2.0,
                        end_s=2.5,
                        start_value=1.0,
                        end_value=0.0,
                        unit="state",
                        note="Control unit commands valve CLOSED when pressure falls below hysteresis threshold.",
                    ),
                    TimedTransitionSpec(
                        signal_id="valve_position",
                        start_s=2.5,
                        end_s=3.5,
                        start_value=1.0,
                        end_value=0.0,
                        unit="state",
                        note="Valve physically travels from OPEN to CLOSED position.",
                    ),
                    TimedTransitionSpec(
                        signal_id="outlet_pressure",
                        start_s=3.5,
                        end_s=5.0,
                        start_value=BLEED_AIR_NOMINAL_OPEN_PSI,
                        end_value=0.0,
                        unit="psi",
                        note="Outlet pressure drops as valve closes and flow stops.",
                    ),
                ),
                completion_condition="valve_cmd == 0 and inlet_pressure <= 30.0 and valve_position == 0",
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="control_unit_ready",
                        value=1,
                        unit="state",
                        note="Control unit remains ready throughout the nominal close sequence.",
                    ),
                ),
            ),
            # Scenario 3: Pressure over-limit — valve must close for safety
            AcceptanceScenarioSpec(
                id="pressure_over_limit",
                label="Overpressure Protection — Valve Closes",
                description=(
                    "Inlet pressure rises above the overpressure threshold. "
                    "Control unit immediately commands valve CLOSED regardless "
                    "of valve state to protect downstream pneumatic components."
                ),
                time_scale_factor=1.0,
                total_duration_s=4.0,
                monitored_signal_ids=(
                    "inlet_pressure",
                    "valve_cmd",
                    "valve_position",
                    "outlet_pressure",
                ),
                transitions=(
                    TimedTransitionSpec(
                        signal_id="inlet_pressure",
                        start_s=0.0,
                        end_s=1.0,
                        start_value=BLEED_AIR_NOMINAL_OPEN_PSI,
                        end_value=BLEED_AIR_PRESSURE_MAX_PSI + 5.0,
                        unit="psi",
                        note="Pressure rises above overpressure threshold due to compressor surge.",
                    ),
                    TimedTransitionSpec(
                        signal_id="valve_cmd",
                        start_s=1.0,
                        end_s=1.5,
                        start_value=1.0,
                        end_value=0.0,
                        unit="state",
                        note="Control unit immediately commands valve CLOSED on overpressure detection.",
                    ),
                    TimedTransitionSpec(
                        signal_id="valve_position",
                        start_s=1.5,
                        end_s=2.5,
                        start_value=1.0,
                        end_value=0.0,
                        unit="state",
                        note="Valve travels to CLOSED position under overpressure protection.",
                    ),
                    TimedTransitionSpec(
                        signal_id="outlet_pressure",
                        start_s=2.5,
                        end_s=3.5,
                        start_value=BLEED_AIR_NOMINAL_OPEN_PSI,
                        end_value=0.0,
                        unit="psi",
                        note="Outlet pressure collapses as the valve closes and isolates the fault.",
                    ),
                ),
                completion_condition=(
                    "valve_cmd == 0 and inlet_pressure >= 65.0 and valve_position == 0"
                ),
                steady_signals=(
                    SteadySignalSpec(
                        signal_id="control_unit_ready",
                        value=1,
                        unit="state",
                        note="Control unit is healthy and actively enforcing overpressure protection.",
                    ),
                ),
            ),
        ),
        fault_modes=(
            # Fault 1: Valve stuck open — pressure drops but valve does not close
            FaultModeSpec(
                id="valve_stuck_open",
                target_component_id="valve_position",
                fault_kind="stuck_high",
                symptom=(
                    "Inlet pressure has dropped below the minimum threshold but the "
                    "valve remains OPEN and outlet pressure does not fall. "
                    "Downstream pneumatic equipment may continue operating unsafely."
                ),
                reasoning_scope_component_ids=(
                    "inlet_pressure",
                    "valve_cmd",
                    "valve_position",
                    "outlet_pressure",
                ),
                expected_diagnostic_sections=("symptoms", "blocked_logic", "repair_hint"),
                optimization_prompt=(
                    "Consider adding a hardware pressure-limiting valve as a passive "
                    "fail-safe in addition to the electronic control unit."
                ),
            ),
            # Fault 2: Valve stuck closed — pressure is healthy but valve does not open
            FaultModeSpec(
                id="valve_stuck_closed",
                target_component_id="valve_position",
                fault_kind="stuck_low",
                symptom=(
                    "Inlet pressure is healthy (above minimum threshold) and the "
                    "control unit commands OPEN, but the valve remains CLOSED. "
                    "No bleed-air reaches the downstream system."
                ),
                reasoning_scope_component_ids=(
                    "inlet_pressure",
                    "valve_cmd",
                    "valve_position",
                    "outlet_pressure",
                ),
                expected_diagnostic_sections=("symptoms", "blocked_logic", "repair_hint"),
                optimization_prompt=(
                    "Consider adding a manual bypass valve as a maintenance backup "
                    "for pneumatic system operation during controller failures."
                ),
            ),
            # Fault 3: Inlet pressure sensor misread — false high reading
            FaultModeSpec(
                id="sensor_misread_high",
                target_component_id="inlet_pressure",
                fault_kind="bias_high",
                symptom=(
                    "The inlet pressure sensor reads normal when the valve is "
                    "actually seeing low pressure due to a line blockage. "
                    "Control unit incorrectly believes supply is healthy."
                ),
                reasoning_scope_component_ids=(
                    "inlet_pressure",
                    "outlet_pressure",
                    "valve_cmd",
                    "valve_position",
                ),
                expected_diagnostic_sections=("symptoms", "repair_hint"),
                optimization_prompt=(
                    "Cross-check inlet pressure against outlet pressure delta "
                    "to detect sensor bias: a large delta with low outlet pressure "
                    "while inlet reads high is a strong misread indicator."
                ),
            ),
        ),
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=KnowledgeCaptureSpec(
            incident_fields=(
                "system_id",
                "scenario_id",
                "fault_mode_id",
                "observed_symptoms",
                "evidence_links",
                "valve_position_at_fault",
                "inlet_pressure_at_fault",
            ),
            resolution_fields=(
                "confirmed_root_cause",
                "repair_action",
                "valve_replaced",
                "sensor_calibrated",
                "validation_after_fix",
                "residual_risk",
            ),
            optimization_fields=(
                "suggested_logic_change",
                "reliability_gain_hypothesis",
                "redundancy_reduction_or_guardrail_note",
                "hysteresis_adjustment",
            ),
        ),
        tags=("bleed-air", "environmental-control", "pneumatic", "third-system"),
    )
    return workbench_spec_to_dict(spec)


# ---------------------------------------------------------------------------
# Controller adapter class
# ---------------------------------------------------------------------------
class BleedAirValveControllerAdapter:
    """
    Truth adapter for the bleed-air valve control system.

    Evaluates snapshots containing:
      - valve_position (str: "CLOSED" / "OPEN")
      - inlet_pressure (float: psi)
      - outlet_pressure (float: psi)
      - control_unit_ready (bool / 0/1)
    """
    metadata = BLEED_AIR_CONTROLLER_METADATA

    def load_spec(self) -> dict[str, Any]:
        return build_bleed_air_workbench_spec()

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> GenericTruthEvaluation:
        # Extract signals
        valve_position = _snapshot_str(snapshot, "valve_position")
        inlet_pressure = _snapshot_float(snapshot, "inlet_pressure")
        outlet_pressure = _snapshot_float(snapshot, "outlet_pressure")
        control_unit_ready = _snapshot_bool(snapshot, "control_unit_ready")

        # Derived states
        valve_open = valve_position == "OPEN"
        pressure_healthy = inlet_pressure >= BLEED_AIR_PRESSURE_MIN_PSI
        pressure_too_low = inlet_pressure < (BLEED_AIR_PRESSURE_MIN_PSI - BLEED_AIR_HYSTERESIS_PSI)
        overpressure = inlet_pressure >= BLEED_AIR_PRESSURE_MAX_PSI

        # Command logic: open if healthy pressure and control unit ready; close if low or overpressure
        valve_cmd = (
            pressure_healthy
            and control_unit_ready
            and not overpressure
        )

        # Active logic nodes
        active_logic_node_ids: list[str] = []
        if valve_cmd:
            active_logic_node_ids.append("valve_open_logic")
        if pressure_too_low or overpressure:
            active_logic_node_ids.append("valve_close_logic")

        # Blocked reasons — ordered so most actionable comes first
        blocked_reasons: list[str] = []
        if not control_unit_ready:
            blocked_reasons.append("control_unit_ready is false — valve cannot be commanded")
        if overpressure:
            blocked_reasons.append(
                f"inlet_pressure {inlet_pressure:.1f} psi exceeds overpressure threshold "
                f"{BLEED_AIR_PRESSURE_MAX_PSI:.1f} psi — valve must close"
            )
        if pressure_too_low and not overpressure:
            blocked_reasons.append(
                f"inlet_pressure {inlet_pressure:.1f} psi below hysteresis floor "
                f"({BLEED_AIR_PRESSURE_MIN_PSI - BLEED_AIR_HYSTERESIS_PSI:.1f} psi)"
            )

        # Completion: valve is open and outlet pressure is healthy
        completion_reached = valve_open and outlet_pressure >= BLEED_AIR_PRESSURE_MIN_PSI

        summary = (
            "Bleed-air valve open and pressurizing."
            if completion_reached
            else "Bleed-air valve closed or pressurization incomplete."
        )

        return GenericTruthEvaluation(
            system_id=BLEED_AIR_SYSTEM_ID,
            active_logic_node_ids=tuple(active_logic_node_ids),
            asserted_component_values={
                "valve_position": valve_position,
                "inlet_pressure": inlet_pressure,
                "outlet_pressure": outlet_pressure,
                "control_unit_ready": control_unit_ready,
                "valve_cmd": valve_cmd,
            },
            completion_reached=completion_reached,
            blocked_reasons=tuple(blocked_reasons),
            summary=summary,
        )


def _snapshot_str(snapshot: Mapping[str, Any], key: str) -> str:
    value = _require_snapshot_value(snapshot, key)
    if not isinstance(value, str):
        raise TypeError(f"snapshot value {key!r} must be a string")
    return value


def build_bleed_air_controller_adapter() -> BleedAirValveControllerAdapter:
    """Factory function — call this to get a ready-to-use adapter instance."""
    return BleedAirValveControllerAdapter()
