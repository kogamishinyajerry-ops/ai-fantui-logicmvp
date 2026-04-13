from __future__ import annotations
from typing import Any, Mapping
from well_harness.controller_adapter import (
    ControllerTruthMetadata,
)
from well_harness.system_spec import (
    ComponentSpec,
    ControlSystemWorkbenchSpec,
    LogicConditionSpec,
    LogicNodeSpec,
    FaultModeSpec,
    KnowledgeCaptureSpec,
    default_workbench_clarification_questions,
    workbench_spec_to_dict,
)

EFDS_SYSTEM_ID = "emergency_flare_deployment_system"
EFDS_SOURCE_OF_TRUTH = "src/well_harness/adapters/efds_adapter.py"

EFDS_CONTROLLER_METADATA = ControllerTruthMetadata(
    adapter_id="efds-controller-adapter",
    system_id=EFDS_SYSTEM_ID,
    truth_kind="python-generic-truth-adapter",
    source_of_truth=EFDS_SOURCE_OF_TRUTH,
    description="Emergency Flare Deployment System — infrared countermeasure flare deployment controller adapter.",
)


def _require_snapshot_value(snapshot: Mapping[str, Any], key: str) -> Any:
    if key not in snapshot:
        raise KeyError(f"missing snapshot value: {key}")
    return snapshot[key]


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


def _snapshot_bool(snapshot: Mapping[str, Any], key: str) -> bool:
    value = _require_snapshot_value(snapshot, key)
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    raise TypeError(f"snapshot value {key!r} must be bool-compatible")


def build_efds_workbench_spec() -> dict[str, Any]:
    spec = ControlSystemWorkbenchSpec(
        system_id=EFDS_SYSTEM_ID,
        title="Emergency Flare Deployment System (EFDS)",
        objective="Automatically or manually deploy IR countermeasure flares when the aircraft enters a prescribed threat envelope, ensuring pilot survival while preventing accidental deployment.",
        source_of_truth=EFDS_SOURCE_OF_TRUTH,
        components=(
            # === SENSORS ===
            ComponentSpec(
                id="sensor.alt.radar",
                label="Radar Altimeter",
                kind="sensor",
                state_shape="analog",
                unit="feet AGL",
                description="Measures altitude above ground level from radar return.",
                allowed_range=(0.0, 50000.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="sensor.alt.baro",
                label="Barometric Altimeter",
                kind="sensor",
                state_shape="analog",
                unit="feet MSL",
                description="Standard atmospheric pressure-derived altitude for cruise reporting.",
                allowed_range=(-1000.0, 60000.0),
                monitor_priority="optional",
            ),
            ComponentSpec(
                id="sensor.temp.external",
                label="External Air Temperature",
                kind="sensor",
                state_shape="analog",
                unit="deg C",
                description="Total Air Temperature probe. Below -20C reduces pyrotechnic reliability.",
                allowed_range=(-80.0, 70.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="sensor.threat.mls",
                label="Missile Launch Sensor (MLS)",
                kind="sensor",
                state_shape="discrete",
                unit="state",
                description="UV plume detector for missile launch. States: IDLE, THREAT_DETECTED, MISSLE_INBOUND, CLEAR.",
                allowed_states=("IDLE", "THREAT_DETECTED", "MISSLE_INBOUND", "CLEAR"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="sensor.g.load",
                label="Load Factor Sensor",
                kind="sensor",
                state_shape="analog",
                unit="g",
                description="Instantaneous airframe load factor.",
                allowed_range=(-4.0, 12.0),
                monitor_priority="optional",
            ),
            # === LOGIC GATES ===
            ComponentSpec(
                id="logic.armed_relay",
                label="Arm Relay Contact",
                kind="logic_gate",
                state_shape="discrete",
                unit="state",
                description="Primary safety relay controlling electrical continuity to flare initiator circuits.",
                allowed_states=("OPEN", "CLOSED", "FAULT"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="logic.firing_channel",
                label="Firing Channel Timer",
                kind="logic_gate",
                state_shape="discrete",
                unit="state",
                description="Monotonic countdown timer defining the firing window. States: READY, COUNTING, EXPIRED, INHIBITED.",
                allowed_states=("READY", "COUNTING", "EXPIRED", "INHIBITED"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="logic.crosslink_validator",
                label="Crosslink Validator",
                kind="logic_gate",
                state_shape="binary",
                unit="state",
                description="Validates two independent sensor channels agree on threat classification.",
                allowed_states=("TRUE", "FALSE"),
                monitor_priority="required",
            ),
            # === PILOT INPUTS ===
            ComponentSpec(
                id="pilot.arm_switch",
                label="Flare Arm Switch",
                kind="pilot_input",
                state_shape="discrete",
                unit="state",
                description="Three-position guarded switch: SAFE, ARM, AUTO.",
                allowed_states=("SAFE", "ARM", "AUTO"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="pilot.manual_dispense",
                label="Manual Dispense Button",
                kind="pilot_input",
                state_shape="discrete",
                unit="state",
                description="Momentary pushbutton. Requires ~0.5s hold to CONFIRM.",
                allowed_states=("RELEASED", "PRESSED", "CONFIRMED"),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="pilot.altitude_override",
                label="Altitude Override Selector",
                kind="pilot_input",
                state_shape="discrete",
                unit="state",
                description="Rotary altitude floor selector: AUTO, 1000FT, 2000FT, 5000FT, NONE.",
                allowed_states=("AUTO", "1000FT", "2000FT", "5000FT", "NONE"),
                monitor_priority="required",
            ),
            # === ACTUATORS ===
            ComponentSpec(
                id="actuator.flare_array",
                label="Flare Cartridge Array",
                kind="actuator",
                state_shape="analog",
                unit="cartridges",
                description="Bank of 24 IR countermeasure cartridges. Each ejection decrements count.",
                allowed_range=(0.0, 24.0),
                monitor_priority="required",
            ),
            ComponentSpec(
                id="actuator.limiter_valve",
                label="Pyrotechnic Bus Voltage Limiter",
                kind="actuator",
                state_shape="discrete",
                unit="state",
                description="Solid-state voltage limiter clamping pyrotechnic bus to 22V DC.",
                allowed_states=("REGULATED", "BYPASS", "TRIPPED"),
                monitor_priority="optional",
            ),
        ),
        logic_nodes=(
            LogicNodeSpec(
                id="ln.01",
                label="LN-01 Threat Classification",
                description="Entry condition for automatic deployment sequence. Fires on THREAT_DETECTED or MISSLE_INBOUND.",
                conditions=(
                    LogicConditionSpec(
                        name="MLS_Threat_State",
                        source_component_id="sensor.threat.mls",
                        comparison="IN",
                        threshold_value="THREAT_DETECTED",
                        note="LN-01 fires on THREAT_DETECTED or MISSLE_INBOUND — both treated identically.",
                    ),
                ),
                downstream_component_ids=("logic.crosslink_validator", "logic.firing_channel"),
            ),
            LogicNodeSpec(
                id="ln.02",
                label="LN-02 Altitude Floor Inhibit",
                description="Prevents auto-deployment below pilot-selected altitude floor.",
                conditions=(
                    LogicConditionSpec(
                        name="Altitude_vs_Floor",
                        source_component_id="sensor.alt.radar",
                        comparison=">=",
                        threshold_value=None,
                        note="AUTO uses baro altimeter; NONE disables inhibit; scalar comparison with enum foot values.",
                    ),
                ),
                downstream_component_ids=("logic.firing_channel",),
            ),
            LogicNodeSpec(
                id="ln.03",
                label="LN-03 Temperature Reliability Gate",
                description="Inhibits firing below -20C where pyrotechnic initiator reliability degrades.",
                conditions=(
                    LogicConditionSpec(
                        name="Temperature_Threshold",
                        source_component_id="sensor.temp.external",
                        comparison=">",
                        threshold_value=-20.0,
                        note="Threshold is nominal -20C. Actual field threshold may vary by unit age / PID tuning.",
                    ),
                ),
                downstream_component_ids=("logic.firing_channel",),
            ),
            LogicNodeSpec(
                id="ln.04",
                label="LN-04 Firing Authorization AND",
                description="Final AND gate: arm_relay CLOSED AND crosslink_validator TRUE AND firing_channel COUNTING.",
                conditions=(
                    LogicConditionSpec(
                        name="Arm_Relay_CLOSED",
                        source_component_id="logic.armed_relay",
                        comparison="==",
                        threshold_value="CLOSED",
                        note="FAULT state causes AND to output FALSE regardless of other inputs.",
                    ),
                    LogicConditionSpec(
                        name="Crosslink_TRUE",
                        source_component_id="logic.crosslink_validator",
                        comparison="==",
                        threshold_value="TRUE",
                        note="Requires two independent sensor channels to agree.",
                    ),
                    LogicConditionSpec(
                        name="Firing_Channel_COUNTING",
                        source_component_id="logic.firing_channel",
                        comparison="==",
                        threshold_value="COUNTING",
                        note="COUNTING begins when LN-01 fires and LN-02 confirms altitude clearance.",
                    ),
                ),
                downstream_component_ids=("actuator.flare_array",),
            ),
        ),
        fault_modes=(
            FaultModeSpec(
                id="fm.01",
                target_component_id="logic.armed_relay",
                fault_kind="open_circuit",
                symptom="Arm relay contact welded in OPEN position — cannot be commanded to CLOSED. Continuity check fails at power-up BIT. EMER FAIL displayed on MFD.",
                reasoning_scope_component_ids=("logic.armed_relay", "actuator.flare_array"),
                expected_diagnostic_sections=("fault_isolation", "layer_investigation", "pinpoint", "root_cause_analysis"),
                optimization_prompt="Can the system detect a stuck-open relay earlier than power-up BIT? Consider adding periodic in-flight continuity checks.",
            ),
            FaultModeSpec(
                id="fm.02",
                target_component_id="sensor.threat.mls",
                fault_kind="bias_high",
                symptom="MLS UV plume detector misclassifies solar reflection off cloud deck as missile launch. MLS transitions to THREAT_DETECTED without actual threat present.",
                reasoning_scope_component_ids=("sensor.threat.mls", "logic.crosslink_validator"),
                expected_diagnostic_sections=("fault_isolation", "layer_investigation", "pinpoint", "root_cause_analysis"),
                optimization_prompt="Add a solar elevation angle check — if sun elevation > threshold and MLS triggers, consider false-positive hypothesis.",
            ),
            FaultModeSpec(
                id="fm.03",
                target_component_id="logic.firing_channel",
                fault_kind="latched_no_unlock",
                symptom="Rapid re-trigger causes timer state machine to transition READY→COUNTING→EXPIRED→COUNTING faster than processing cycle updates UI. Firing channel appears to be in COUNTING but rapidly oscillates.",
                reasoning_scope_component_ids=("logic.firing_channel", "sensor.threat.mls"),
                expected_diagnostic_sections=("fault_isolation", "layer_investigation", "pinpoint", "root_cause_analysis"),
                optimization_prompt="Add a minimum dwell time in EXPIRED state before allowing re-transition to COUNTING to prevent race conditions.",
            ),
        ),
        acceptance_scenarios=(),
        onboarding_questions=default_workbench_clarification_questions(),
        knowledge_capture=KnowledgeCaptureSpec(
            incident_fields=(
                "timestamp",
                "flight_phase",
                "sensor.alt.radar",
                "sensor.alt.baro",
                "sensor.temp.external",
                "sensor.threat.mls",
                "pilot.arm_switch",
                "pilot.altitude_override",
                "logic.armed_relay",
                "logic.firing_channel",
            ),
            resolution_fields=("root_cause", "component_replaced", "maintenance_action"),
            optimization_fields=("threshold_revision", "guard_band_addition", "new_sensor_channel"),
        ),
        tags=("efds", "runtime-generalization-proof", "third-system"),
    )
    return spec


class EFDSControllerAdapter:
    """EFDS controller truth adapter — evaluates firing authorization logic."""

    metadata = EFDS_CONTROLLER_METADATA

    def __init__(self, harness_config: Any = None):
        pass

    def load_spec(self) -> dict[str, Any]:
        return workbench_spec_to_dict(build_efds_workbench_spec())

    def evaluate_snapshot(self, snapshot: Mapping[str, Any]) -> Any:
        """Evaluate EFDS firing authorization logic and return a GenericTruthEvaluation."""
        from well_harness.controller_adapter import GenericTruthEvaluation
        result = self.evaluate(snapshot)

        active_logic_node_ids: list[str] = []
        blocked_reasons: list[str] = []

        ln01 = result["ln01.threat_classification.fired"]
        ln02 = result["ln02.altitude_floor.passed"]
        ln03 = result["ln03.temperature_gate.passed"]
        ln04 = result["ln04.firing_authorization.fired"]

        if ln01:
            active_logic_node_ids.append("ln.01")
        else:
            blocked_reasons.append("MLS state must be THREAT_DETECTED or MISSLE_INBOUND")

        if ln02:
            active_logic_node_ids.append("ln.02")
        else:
            blocked_reasons.append(f"Radar altitude {result['ln02.altitude_floor.radar_alt']}ft below floor {result['ln02.altitude_floor.floor']}ft")

        if ln03:
            active_logic_node_ids.append("ln.03")
        else:
            blocked_reasons.append(f"External temperature {result['ln03.temperature_gate.temp_c']}C at or below -20C threshold")

        if ln04:
            active_logic_node_ids.append("ln.04")
        else:
            conds = result["ln04.firing_authorization.conditions_met"]
            if not conds["arm_relay_closed"]:
                blocked_reasons.append("Arm relay is not CLOSED")
            if not conds["crosslink_true"]:
                blocked_reasons.append("Crosslink validator is not TRUE")
            if not conds["firing_channel_counting"]:
                blocked_reasons.append("Firing channel is not COUNTING")

        completion_reached = bool(result["flare.deploy_now"])

        return GenericTruthEvaluation(
            system_id=EFDS_SYSTEM_ID,
            active_logic_node_ids=tuple(active_logic_node_ids),
            asserted_component_values={
                # Raw signal values (for UI node display)
                "sensor.threat.mls": _snapshot_str(snapshot, "sensor.threat.mls"),
                "sensor.alt.radar": _snapshot_float(snapshot, "sensor.alt.radar"),
                "sensor.alt.baro": _snapshot_float(snapshot, "sensor.alt.baro"),
                "sensor.temp.external": _snapshot_float(snapshot, "sensor.temp.external"),
                "pilot.arm_switch": _snapshot_str(snapshot, "pilot.arm_switch"),
                "pilot.altitude_override": _snapshot_str(snapshot, "pilot.altitude_override"),
                "logic.armed_relay": _snapshot_str(snapshot, "logic.armed_relay"),
                "logic.firing_channel": _snapshot_str(snapshot, "logic.firing_channel"),
                "logic.crosslink_validator": _snapshot_str(snapshot, "logic.crosslink_validator"),
                "actuator.flare_array": _snapshot_float(snapshot, "actuator.flare_array"),
                # Derived logic node results
                "ln01.threat_classification.fired": ln01,
                "ln02.altitude_floor.passed": ln02,
                "ln03.temperature_gate.passed": ln03,
                "ln04.firing_authorization.fired": ln04,
                "flare.deploy_now": result["flare.deploy_now"],
                "flare.remaining_count": result["flare.remaining_count"],
                "system.armed": result["system.armed"],
                "system.mode": result["system.mode"],
                "pilot.manual_confirmed": result["pilot.manual_confirmed"],
            },
            completion_reached=completion_reached,
            blocked_reasons=tuple(blocked_reasons),
            summary=(
                f"Flare deployment {'authorized' if completion_reached else 'not authorized'}. "
                f"Mode={result['system.mode']}, Armed={result['system.armed']}, "
                f"Remaining={result['flare.remaining_count']}."
            ),
        )

    def evaluate(self, snapshot: Mapping[str, Any]) -> dict[str, Any]:
        """Evaluate EFDS firing authorization logic."""
        # --- Read signals ---
        radar_alt = _snapshot_float(snapshot, "sensor.alt.radar")
        baro_alt = _snapshot_float(snapshot, "sensor.alt.baro")
        temp_ext = _snapshot_float(snapshot, "sensor.temp.external")
        mls_state = _snapshot_str(snapshot, "sensor.threat.mls")
        g_load = _snapshot_float(snapshot, "sensor.g.load")
        arm_relay = _snapshot_str(snapshot, "logic.armed_relay")
        firing_channel = _snapshot_str(snapshot, "logic.firing_channel")
        crosslink = _snapshot_str(snapshot, "logic.crosslink_validator")
        arm_switch = _snapshot_str(snapshot, "pilot.arm_switch")
        manual_dispense = _snapshot_str(snapshot, "pilot.manual_dispense")
        alt_override = _snapshot_str(snapshot, "pilot.altitude_override")
        flare_count = _snapshot_float(snapshot, "actuator.flare_array")

        # --- LN-01: Threat Classification ---
        ln01_fired = mls_state in ("THREAT_DETECTED", "MISSLE_INBOUND")

        # --- LN-02: Altitude Floor ---
        alt_floor_map = {"AUTO": baro_alt, "1000FT": 1000.0, "2000FT": 2000.0, "5000FT": 5000.0, "NONE": 0.0}
        alt_floor = alt_floor_map.get(alt_override, 0.0)
        ln02_passed = radar_alt >= alt_floor

        # --- LN-03: Temperature Gate ---
        ln03_passed = temp_ext > -20.0

        # --- LN-04: Firing Authorization AND ---
        ln04_fired = (
            arm_relay == "CLOSED"
            and crosslink == "TRUE"
            and firing_channel == "COUNTING"
        )

        # Final authorization: all conditions satisfied
        firing_authorized = ln01_fired and ln02_passed and ln03_passed and ln04_fired

        # --- Outputs ---
        flare_to_deploy = 1 if (firing_authorized and flare_count >= 1) else 0

        return {
            "ln01.threat_classification.fired": ln01_fired,
            "ln01.threat_classification.mls_state": mls_state,
            "ln02.altitude_floor.passed": ln02_passed,
            "ln02.altitude_floor.radar_alt": radar_alt,
            "ln02.altitude_floor.floor": alt_floor,
            "ln03.temperature_gate.passed": ln03_passed,
            "ln03.temperature_gate.temp_c": temp_ext,
            "ln04.firing_authorization.fired": ln04_fired,
            "firing.authorized": firing_authorized,
            "ln04.firing_authorization.conditions_met": {
                "arm_relay_closed": arm_relay == "CLOSED",
                "crosslink_true": crosslink == "TRUE",
                "firing_channel_counting": firing_channel == "COUNTING",
            },
            "flare.deploy_now": flare_to_deploy,
            "flare.remaining_count": flare_count - flare_to_deploy,
            "system.armed": arm_switch in ("ARM", "AUTO"),
            "system.mode": arm_switch,
            "pilot.manual_confirmed": manual_dispense == "CONFIRMED",
        }

    def get_answer(self, question: str, snapshot: Mapping[str, Any]) -> str:
        result = self.evaluate(snapshot)
        q_lower = question.lower()
        if "ln01" in q_lower or "threat" in q_lower or "mls" in q_lower:
            return f"LN-01 fired: {result['ln01.threat_classification.fired']}, MLS state: {result['ln01.threat_classification.mls_state']}"
        if "ln02" in q_lower or "altitude" in q_lower:
            return f"LN-02 passed: {result['ln02.altitude_floor.passed']}, radar alt: {result['ln02.altitude_floor.radar_alt']}ft vs floor: {result['ln02.altitude_floor.floor']}ft"
        if "ln03" in q_lower or "temperature" in q_lower or "temp" in q_lower:
            return f"LN-03 passed: {result['ln03.temperature_gate.passed']}, temp: {result['ln03.temperature_gate.temp_c']}C"
        if "ln04" in q_lower or "firing" in q_lower or "authorize" in q_lower:
            return f"LN-04 fired: {result['ln04.firing_authorization.fired']}, conditions: {result['ln04.firing_authorization.conditions_met']}"
        if "flare" in q_lower or "deploy" in q_lower:
            return f"Deploy now: {result['flare.deploy_now']}, remaining: {result['flare.remaining_count']}"
        if "armed" in q_lower or "arm" in q_lower:
            return f"System armed: {result['system.armed']}, mode: {result['system.mode']}"
        return str(result)


def build_efds_controller_adapter() -> EFDSControllerAdapter:
    return EFDSControllerAdapter()
