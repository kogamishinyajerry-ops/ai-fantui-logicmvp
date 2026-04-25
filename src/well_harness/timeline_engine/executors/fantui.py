"""FANTUI executor: wraps DeployController + plant + latched switches.

One tick:
    1. Build PilotInputs from `inputs` dict (with fault overrides for
       sensor zero / radio_altitude_ft / n1k).
    2. Update latched switches based on TRA history.
    3. Apply switch-stuck faults.
    4. Read plant sensors; apply sensor faults.
    5. Evaluate DeployController.
    6. Apply output-stuck faults (logic_stuck_false / cmd_blocked).
    7. Advance plant by dt_s using (faulted) outputs.
    8. Return ExecutorTickResult with outputs + logic_states.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from well_harness.controller_adapter import build_reference_controller_adapter
from well_harness.models import ControllerOutputs, HarnessConfig, ResolvedInputs
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.switches import LatchedThrottleSwitches, SwitchState
from well_harness.timeline_engine.executors.base import ExecutorTickResult


# Keys the player sets on `inputs` that we recognise as pilot-facing.
_PILOT_INPUT_KEYS = {
    "radio_altitude_ft",
    "tra_deg",
    "engine_running",
    "aircraft_on_ground",
    "reverser_inhibited",
    "eec_enable",
    "n1k",
    "max_n1k_deploy_limit",
}


# Whitelist of (node_id, fault_type) pairs the FANTUI executor knows how to apply.
# Unknown faults raise ValueError so they surface as 400 responses instead of being
# silently ignored (Codex PR-2 MAJOR #4).
_FANTUI_FAULT_WHITELIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("sw1", "stuck_off"),
        ("sw1", "stuck_on"),
        ("sw2", "stuck_off"),
        ("sw2", "stuck_on"),
        ("tls115", "sensor_zero"),
        ("vdt90", "cmd_blocked"),
        ("radio_altitude_ft", "sensor_zero"),
        ("n1k", "sensor_zero"),
        ("logic1", "logic_stuck_false"),
        ("logic2", "logic_stuck_false"),
        ("logic3", "logic_stuck_false"),
        ("logic4", "logic_stuck_false"),
        ("thr_lock", "cmd_blocked"),
    }
)


class FantuiExecutor:
    """Stateful FANTUI tick runner conforming to the Executor protocol."""

    system_id = "fantui"
    logic_node_ids = ("logic1", "logic2", "logic3", "logic4")

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self._config = config or HarnessConfig()
        self._controller = build_reference_controller_adapter(self._config)
        self._switches = LatchedThrottleSwitches(self._config)
        self._plant = SimplifiedDeployPlant(self._config)
        # Mutable state set in reset():
        self._switch_state: SwitchState = SwitchState(previous_tra_deg=0.0)
        self._plant_state: PlantState = PlantState()
        # Cache the most recent resolved inputs so we can echo them in the frame.
        self._last_resolved: dict[str, Any] = {}

    # ---- Executor protocol -------------------------------------------------

    def reset(self, initial_inputs: dict[str, Any]) -> None:
        self._switch_state = SwitchState(
            previous_tra_deg=float(initial_inputs.get("tra_deg", 0.0))
        )
        self._plant_state = PlantState()
        self._last_resolved = {}

    def tick(
        self,
        t_s: float,
        dt_s: float,
        inputs: dict[str, Any],
        active_faults: list[str],
    ) -> ExecutorTickResult:
        fault_map = _build_fault_map(active_faults)

        # Resolve pilot inputs (with sensor_zero sensor faults pre-applied).
        pilot = _build_pilot(inputs, fault_map)

        # Advance latched switches based on TRA transition, then apply stuck faults.
        self._switch_state = self._switches.update(self._switch_state, pilot["tra_deg"])
        self._switch_state = _apply_switch_faults(self._switch_state, fault_map)

        sensors = self._plant_state.sensors(self._config)
        sensors = _apply_sensor_faults(sensors, fault_map)

        resolved = ResolvedInputs(
            radio_altitude_ft=pilot["radio_altitude_ft"],
            tra_deg=pilot["tra_deg"],
            sw1=self._switch_state.sw1,
            sw2=self._switch_state.sw2,
            engine_running=pilot["engine_running"],
            aircraft_on_ground=pilot["aircraft_on_ground"],
            reverser_inhibited=pilot["reverser_inhibited"],
            eec_enable=pilot["eec_enable"],
            n1k=pilot["n1k"],
            max_n1k_deploy_limit=pilot["max_n1k_deploy_limit"],
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=sensors.all_pls_unlocked,
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )

        outputs, explain = self._controller.evaluate_with_explain(resolved)
        outputs = _apply_output_faults(outputs, fault_map)

        # Advance plant AFTER the controller sees the pre-advance sensors.
        self._plant_state = self._plant.advance(self._plant_state, outputs, dt_s)

        output_dict = _outputs_to_dict(outputs)
        logic_states = _logic_states_from_outputs_and_explain(outputs, explain, fault_map)
        resolved_dict = _resolved_inputs_to_dict(resolved, sensors)
        self._last_resolved = resolved_dict

        return ExecutorTickResult(
            outputs=output_dict,
            logic_states=logic_states,
            resolved_inputs=resolved_dict,
        )


# ---- Helpers ---------------------------------------------------------------


def _build_fault_map(active_faults: list[str]) -> dict[str, str]:
    """Convert ['sw1:stuck_off'] to {'sw1': 'stuck_off'}.

    Later entries override earlier ones on the same node_id. Unknown fault
    ids raise ValueError so /api/timeline-simulate returns 400 rather than
    silently dropping a typo like "sw1:stuckoff" (Codex PR-2 MAJOR #4).
    """
    fault_map: dict[str, str] = {}
    for entry in active_faults:
        if ":" in entry:
            node_id, fault_type = entry.split(":", 1)
            node_id = node_id.strip()
            fault_type = fault_type.strip()
        elif entry:
            node_id, fault_type = entry.strip(), ""
        else:
            continue
        if (node_id, fault_type) not in _FANTUI_FAULT_WHITELIST:
            raise ValueError(
                f"unknown FANTUI fault {node_id!r}:{fault_type!r} — not in executor whitelist"
            )
        fault_map[node_id] = fault_type
    return fault_map


_DEFAULT_MAX_N1K_DEPLOY_LIMIT = 60.0  # matches demo / controller defaults


def _build_pilot(inputs: dict[str, Any], fault_map: dict[str, str]) -> dict[str, Any]:
    """Pull pilot fields from the raw input dict with sensor_zero faults applied."""
    ra = float(inputs.get("radio_altitude_ft", 0.0))
    if fault_map.get("radio_altitude_ft") == "sensor_zero":
        ra = 0.0

    n1k = float(inputs.get("n1k", 0.35))
    if fault_map.get("n1k") == "sensor_zero":
        n1k = 0.0

    return {
        "radio_altitude_ft": ra,
        "tra_deg": float(inputs.get("tra_deg", 0.0)),
        "engine_running": bool(inputs.get("engine_running", True)),
        "aircraft_on_ground": bool(inputs.get("aircraft_on_ground", False)),
        "reverser_inhibited": bool(inputs.get("reverser_inhibited", False)),
        "eec_enable": bool(inputs.get("eec_enable", True)),
        "n1k": n1k,
        "max_n1k_deploy_limit": float(
            inputs.get("max_n1k_deploy_limit", _DEFAULT_MAX_N1K_DEPLOY_LIMIT)
        ),
    }


def _apply_switch_faults(state: SwitchState, fault_map: dict[str, str]) -> SwitchState:
    sw1 = state.sw1
    sw2 = state.sw2
    if fault_map.get("sw1") == "stuck_off":
        sw1 = False
    elif fault_map.get("sw1") == "stuck_on":
        sw1 = True
    if fault_map.get("sw2") == "stuck_off":
        sw2 = False
    elif fault_map.get("sw2") == "stuck_on":
        sw2 = True
    if sw1 == state.sw1 and sw2 == state.sw2:
        return state
    return SwitchState(previous_tra_deg=state.previous_tra_deg, sw1=sw1, sw2=sw2)


def _apply_sensor_faults(sensors, fault_map: dict[str, str]):
    updates: dict[str, Any] = {}
    if fault_map.get("tls115") == "sensor_zero":
        updates["tls_unlocked_ls"] = False
    if fault_map.get("vdt90") == "cmd_blocked":
        updates["deploy_90_percent_vdt"] = False
    if not updates:
        return sensors
    return replace(sensors, **updates)


def _apply_output_faults(outputs: ControllerOutputs, fault_map: dict[str, str]) -> ControllerOutputs:
    updates: dict[str, Any] = {}
    if fault_map.get("tls115") == "sensor_zero":
        updates["tls_115vac_cmd"] = False
    if fault_map.get("logic1") == "logic_stuck_false":
        updates["logic1_active"] = False
        updates["tls_115vac_cmd"] = False
    if fault_map.get("logic2") == "logic_stuck_false":
        updates["logic2_active"] = False
        updates["etrac_540vdc_cmd"] = False
    if fault_map.get("logic3") == "logic_stuck_false":
        updates["logic3_active"] = False
        updates["eec_deploy_cmd"] = False
        updates["pls_power_cmd"] = False
        updates["pdu_motor_cmd"] = False
    if fault_map.get("logic4") == "logic_stuck_false":
        updates["logic4_active"] = False
        updates["throttle_electronic_lock_release_cmd"] = False
    if fault_map.get("thr_lock") == "cmd_blocked":
        updates["throttle_electronic_lock_release_cmd"] = False
    if not updates:
        return outputs
    return replace(outputs, **updates)


def _outputs_to_dict(outputs: ControllerOutputs) -> dict[str, Any]:
    return {
        "logic1_active": outputs.logic1_active,
        "logic2_active": outputs.logic2_active,
        "logic3_active": outputs.logic3_active,
        "logic4_active": outputs.logic4_active,
        "tls_115vac_cmd": outputs.tls_115vac_cmd,
        "etrac_540vdc_cmd": outputs.etrac_540vdc_cmd,
        "eec_deploy_cmd": outputs.eec_deploy_cmd,
        "pls_power_cmd": outputs.pls_power_cmd,
        "pdu_motor_cmd": outputs.pdu_motor_cmd,
        "throttle_electronic_lock_release_cmd": outputs.throttle_electronic_lock_release_cmd,
    }


def _logic_states_from_outputs_and_explain(
    outputs, explain, fault_map: dict[str, str]
) -> dict[str, str]:
    """Map controller outputs + explain into 'active' / 'blocked' / 'idle'.

    A `logicN:logic_stuck_false` fault forces the node to 'blocked' even
    when the pre-fault `explain.failed_conditions` would be empty (i.e. the
    underlying logic was satisfied but got masked by the output override).
    Without this override the cascade reporter sees the gate as 'idle' and
    misses the fault-induced break (Codex PR-2 MAJOR #1).
    """
    states: dict[str, str] = {}
    for idx, name in enumerate(("logic1", "logic2", "logic3", "logic4"), start=1):
        active = getattr(outputs, f"logic{idx}_active")
        layer_explain = getattr(explain, f"logic{idx}")
        if active:
            states[name] = "active"
        elif fault_map.get(name) == "logic_stuck_false":
            states[name] = "blocked"
        elif layer_explain.failed_conditions:
            states[name] = "blocked"
        else:
            states[name] = "idle"
    return states


def _resolved_inputs_to_dict(resolved: ResolvedInputs, sensors) -> dict[str, Any]:
    return {
        "radio_altitude_ft": resolved.radio_altitude_ft,
        "tra_deg": resolved.tra_deg,
        "sw1": resolved.sw1,
        "sw2": resolved.sw2,
        "engine_running": resolved.engine_running,
        "aircraft_on_ground": resolved.aircraft_on_ground,
        "reverser_inhibited": resolved.reverser_inhibited,
        "eec_enable": resolved.eec_enable,
        "n1k": resolved.n1k,
        "max_n1k_deploy_limit": resolved.max_n1k_deploy_limit,
        "tls_unlocked_ls": resolved.tls_unlocked_ls,
        "all_pls_unlocked_ls": resolved.all_pls_unlocked_ls,
        "reverser_not_deployed_eec": resolved.reverser_not_deployed_eec,
        "reverser_fully_deployed_eec": resolved.reverser_fully_deployed_eec,
        "deploy_90_percent_vdt": resolved.deploy_90_percent_vdt,
        "deploy_position_percent": sensors.deploy_position_percent,
    }
