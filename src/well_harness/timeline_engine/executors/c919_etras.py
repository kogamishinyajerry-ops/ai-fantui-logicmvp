"""C919 E-TRAS executor: wraps the frozen-V1.0 C919ReverseThrustSystem.

One tick:
    1. Build fault map (whitelist-checked).
    2. Derive atltla/apwtla from tra_deg window membership (with fault overrides).
    3. Resolve MLG_WOW inputs with fault overrides.
    4. Resolve lock inputs with fault overrides.
    5. Apply over-temp fault override.
    6. Run the full 12-step C919ReverseThrustSystem.tick().
    7. Advance internal TR-position plant based on FADEC deploy/stow commands.
    8. Map SystemState + command outputs into logic_states (5 nodes).
"""

from __future__ import annotations

from typing import Any

from well_harness.adapters.c919_etras_frozen_v1 import (
    C919ReverseThrustSystem,
    FrozenConfig,
    LockInputs,
    RawInputs,
    SystemState,
)
from well_harness.timeline_engine.executors.base import ExecutorTickResult


# SW1 / SW2 throttle microswitch windows (PDF §Step2).
_SW1_WINDOW_MAX_DEG = -1.4
_SW1_WINDOW_MIN_DEG = -6.2
_SW2_WINDOW_MAX_DEG = -5.0
_SW2_WINDOW_MIN_DEG = -9.8

# TR actuator plant rates: deploy 0→100% in ≈2.5s, stow 100→0% in ≈3s (PDF §Step3/§Step8).
_DEPLOY_RATE_PCT_PER_S = 40.0
_STOW_RATE_PCT_PER_S = 33.3


# Whitelist of (node_id, fault_type) pairs the C919 executor applies. Anything
# else raises ValueError so API callers get a 400 instead of silent ignore.
_C919_FAULT_WHITELIST: frozenset[tuple[str, str]] = frozenset(
    {
        ("tr_inhibited", "stuck_on"),
        ("etras_over_temp_fault", "stuck_on"),
        ("engine_running", "stuck_off"),
        ("lgcu1", "disagree"),          # LGCU1 flips to OPPOSITE of LGCU2 (both valid)
        ("lgcu1", "invalid"),           # LGCU1 marked invalid (fallback to LGCU2)
        ("lgcu2", "invalid"),           # LGCU2 marked invalid (fallback to LGCU1)
        ("lgcu_both", "invalid"),       # both invalid → conservative FALSE
        ("atltla", "stuck_off"),        # SW1 never closes
        ("apwtla", "stuck_off"),        # SW2 never closes
        ("tls", "sensor_fail"),         # both TLS unlock sensors stuck locked
        ("pylon_l", "sensor_fail"),     # left pylon sensors stuck locked
        ("pylon_r", "sensor_fail"),     # right pylon sensors stuck locked
        ("pls", "stuck_unlocked"),      # PLS sensors report unlocked while physically stowed
        ("tr_position", "stuck_deployed"),  # actuator jams at current position ≥80%
    }
)


class C919ETRASExecutor:
    """Stateful C919 E-TRAS tick runner conforming to the Executor protocol."""

    system_id = "c919-etras"
    logic_node_ids = (
        "ln_eicu_cmd2",
        "ln_eicu_cmd3",
        "ln_tr_command3_enable",
        "ln_fadec_deploy_command",
        "ln_fadec_stow_command",
    )

    def __init__(self, config: FrozenConfig | None = None) -> None:
        self._config = config or FrozenConfig()
        self._system = C919ReverseThrustSystem(config=self._config)
        # TR actuator plant position (separate from the C919 controller itself,
        # which treats tr_position_pct as an external sensor reading).
        self._tr_position_pct: float = 0.0
        self._tr_position_pinned: float | None = None  # set when stuck_deployed active
        # Lock plant: once CMD2 fires, actuators physically unlock. This flag
        # is read by the lock builder on the NEXT tick to emit unlocked lock
        # inputs so the stowed-and-locked dwell accumulator resets and
        # tr_command3_enable can go True.
        self._unlock_engaged: bool = False

    def reset(self, initial_inputs: dict[str, Any]) -> None:
        self._system = C919ReverseThrustSystem(config=self._config)
        self._tr_position_pct = float(initial_inputs.get("tr_position_pct", 0.0))
        self._tr_position_pinned = None
        self._unlock_engaged = False

    def tick(
        self,
        t_s: float,
        dt_s: float,
        inputs: dict[str, Any],
        active_faults: list[str],
    ) -> ExecutorTickResult:
        fault_map = _build_fault_map(active_faults)

        # --- Pin TR position when stuck_deployed first activates ---
        if "tr_position" in fault_map and fault_map["tr_position"] == "stuck_deployed":
            if self._tr_position_pinned is None:
                # Latch at current position (or at least 80% if not yet there).
                self._tr_position_pinned = max(self._tr_position_pct, 80.0)
        else:
            self._tr_position_pinned = None

        raw_inputs = _build_raw_inputs(
            inputs=inputs,
            fault_map=fault_map,
            tr_position_pct=self._tr_position_pct,
            unlock_engaged=self._unlock_engaged,
        )

        outputs = self._system.tick(raw_inputs, dt_s=dt_s)

        # --- Advance TR-position plant AFTER the controller saw pre-advance state ---
        if self._tr_position_pinned is not None:
            self._tr_position_pct = self._tr_position_pinned
        else:
            if outputs.fadec_deploy_command and raw_inputs.tr_inhibited is False:
                self._tr_position_pct = min(
                    100.0, self._tr_position_pct + _DEPLOY_RATE_PCT_PER_S * dt_s
                )
            elif outputs.fadec_stow_command:
                self._tr_position_pct = max(
                    0.0, self._tr_position_pct - _STOW_RATE_PCT_PER_S * dt_s
                )

        # --- Lock plant: CMD2 drives the unlock mechanism. Once CMD2 has
        # fired, treat the actuators as physically unlocked for the rest of
        # the run — CMD2 can toggle during TRA sweep (SW1 window transit),
        # but mechanically the unlocks stay engaged until a full stow cycle
        # re-lands. Auto-releasing unlock_engaged mid-sweep would force
        # stowed_and_locked_latched back True and reset the CMD3 latch.
        # Re-lock happens at reset() (i.e. the start of the next run).
        if outputs.single_phase_unlock_power_on:
            self._unlock_engaged = True

        output_dict = _outputs_to_dict(outputs, self._tr_position_pct)
        logic_states = _logic_states_from_outputs(outputs, raw_inputs)
        resolved_dict = _resolved_inputs_to_dict(raw_inputs, self._tr_position_pct)

        return ExecutorTickResult(
            outputs=output_dict,
            logic_states=logic_states,
            resolved_inputs=resolved_dict,
        )


# ---- Helpers ---------------------------------------------------------------


def _build_fault_map(active_faults: list[str]) -> dict[str, str]:
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
        if (node_id, fault_type) not in _C919_FAULT_WHITELIST:
            raise ValueError(
                f"unknown C919 E-TRAS fault {node_id!r}:{fault_type!r} — not in executor whitelist"
            )
        fault_map[node_id] = fault_type
    return fault_map


def _derive_microswitches(tra_deg: float) -> tuple[bool, bool]:
    """Instantaneous window-membership microswitches (PDF §Step2)."""
    atltla = _SW1_WINDOW_MIN_DEG <= tra_deg <= _SW1_WINDOW_MAX_DEG
    apwtla = _SW2_WINDOW_MIN_DEG <= tra_deg <= _SW2_WINDOW_MAX_DEG
    return atltla, apwtla


def _build_raw_inputs(
    inputs: dict[str, Any],
    fault_map: dict[str, str],
    tr_position_pct: float,
    unlock_engaged: bool,
) -> RawInputs:
    tra_deg = float(inputs.get("tra_deg", 0.0))

    # Microswitches: derive from TRA, then apply stuck_off faults.
    atltla, apwtla = _derive_microswitches(tra_deg)
    if fault_map.get("atltla") == "stuck_off":
        atltla = False
    if fault_map.get("apwtla") == "stuck_off":
        apwtla = False

    # MLG_WOW redundancy:
    lgcu1_raw = bool(inputs.get("lgcu1_mlg_wow", inputs.get("mlg_wow", True)))
    lgcu2_raw = bool(inputs.get("lgcu2_mlg_wow", inputs.get("mlg_wow", True)))
    lgcu1_valid = bool(inputs.get("lgcu1_valid", True))
    lgcu2_valid = bool(inputs.get("lgcu2_valid", True))
    lgcu_fault = fault_map.get("lgcu1") or fault_map.get("lgcu2") or fault_map.get("lgcu_both")
    if fault_map.get("lgcu1") == "disagree":
        # LGCU1 flips to opposite of LGCU2 (both still valid → triggers conservative FALSE).
        lgcu1_raw = not lgcu2_raw
    if fault_map.get("lgcu1") == "invalid":
        lgcu1_valid = False
    if fault_map.get("lgcu2") == "invalid":
        lgcu2_valid = False
    if fault_map.get("lgcu_both") == "invalid":
        lgcu1_valid = False
        lgcu2_valid = False

    # Engine / mode
    engine_running = bool(inputs.get("engine_running", True))
    if fault_map.get("engine_running") == "stuck_off":
        engine_running = False
    tr_inhibited = bool(inputs.get("tr_inhibited", False))
    if fault_map.get("tr_inhibited") == "stuck_on":
        tr_inhibited = True
    trcu_menu_mode = bool(inputs.get("trcu_menu_mode", False))
    maintenance_cycle = bool(inputs.get("maintenance_cycle_on_going", False))

    # N1k
    n1k_pct = float(inputs.get("n1k_pct", 50.0))
    max_n1k_deploy = float(inputs.get("max_n1k_deploy_limit_pct", 84.0))
    max_n1k_stow = float(inputs.get("max_n1k_stow_limit_pct", 30.0))

    # Over-temp
    over_temp = bool(inputs.get("etras_over_temp_fault", False))
    if fault_map.get("etras_over_temp_fault") == "stuck_on":
        over_temp = True

    locks = _build_lock_inputs(inputs, fault_map, tr_position_pct, unlock_engaged)

    return RawInputs(
        lgcu1_mlg_wow=lgcu1_raw,
        lgcu2_mlg_wow=lgcu2_raw,
        lgcu1_valid=lgcu1_valid,
        lgcu2_valid=lgcu2_valid,
        tra_deg=tra_deg,
        atltla=atltla,
        apwtla=apwtla,
        tr_inhibited=tr_inhibited,
        engine_running=engine_running,
        trcu_menu_mode=trcu_menu_mode,
        maintenance_cycle_on_going=maintenance_cycle,
        tr_position_pct=tr_position_pct,
        n1k_pct=n1k_pct,
        max_n1k_deploy_limit_pct=max_n1k_deploy,
        max_n1k_stow_limit_pct=max_n1k_stow,
        etras_over_temp_fault=over_temp,
        locks=locks,
    )


def _build_lock_inputs(
    inputs: dict[str, Any],
    fault_map: dict[str, str],
    tr_position_pct: float,
    unlock_engaged: bool,
) -> LockInputs:
    """Derive the 10 lock sensor bits.

    Default policy: locks report UNLOCKED when the unlock plant has engaged
    (CMD2 has fired at least once in this deploy cycle) OR when position
    has moved away from stow (> 2%). Otherwise locks report LOCKED. Users
    can still override individual fields via `inputs['locks']`, and faults
    then mask specific groups.
    """
    stowed_zone = tr_position_pct < 2.0 and not unlock_engaged
    default_locked = stowed_zone
    default_unlocked = not stowed_zone

    locks_override = inputs.get("locks") or {}

    def lk(key: str, default: bool) -> bool:
        if key in locks_override:
            return bool(locks_override[key])
        return default

    tls_locked = lk("tls_locked", default_locked)
    tls_unlocked = lk("tls_unlocked", default_unlocked)
    pyl_l_locked = lk("pylon_lock_l_locked", default_locked)
    pyl_l_unlocked = lk("pylon_lock_l_unlocked", default_unlocked)
    pyl_r_locked = lk("pylon_lock_r_locked", default_locked)
    pyl_r_unlocked = lk("pylon_lock_r_unlocked", default_unlocked)
    pls_l_locked = lk("pls_l_locked", default_locked)
    pls_l_unlocked = lk("pls_l_unlocked", default_unlocked)
    pls_r_locked = lk("pls_r_locked", default_locked)
    pls_r_unlocked = lk("pls_r_unlocked", default_unlocked)

    # tls:sensor_fail → force BOTH tls locked=True AND tls_unlocked=False so
    # unlock_confirmed can never be established via TLS.
    if fault_map.get("tls") == "sensor_fail":
        tls_locked = True
        tls_unlocked = False
    if fault_map.get("pylon_l") == "sensor_fail":
        pyl_l_locked = True
        pyl_l_unlocked = False
    if fault_map.get("pylon_r") == "sensor_fail":
        pyl_r_locked = True
        pyl_r_unlocked = False
    # pls:stuck_unlocked → PLS sensors report unlocked (regardless of stow position)
    if fault_map.get("pls") == "stuck_unlocked":
        pls_l_locked = False
        pls_l_unlocked = True
        pls_r_locked = False
        pls_r_unlocked = True

    return LockInputs(
        tls_locked=tls_locked,
        tls_unlocked=tls_unlocked,
        pylon_lock_l_locked=pyl_l_locked,
        pylon_lock_l_unlocked=pyl_l_unlocked,
        pylon_lock_r_locked=pyl_r_locked,
        pylon_lock_r_unlocked=pyl_r_unlocked,
        pls_l_locked=pls_l_locked,
        pls_l_unlocked=pls_l_unlocked,
        pls_r_locked=pls_r_locked,
        pls_r_unlocked=pls_r_unlocked,
    )


def _outputs_to_dict(outputs, tr_position_pct: float) -> dict[str, Any]:
    return {
        "state": outputs.state.value,
        "selected_mlg_wow": outputs.selected_mlg_wow,
        "tr_wow": outputs.tr_wow,
        "single_phase_unlock_power_on": outputs.single_phase_unlock_power_on,
        "three_phase_trcu_power_on": outputs.three_phase_trcu_power_on,
        "unlock_confirmed": outputs.unlock_confirmed,
        "fadec_deploy_command": outputs.fadec_deploy_command,
        "fadec_stow_command": outputs.fadec_stow_command,
        "tr_stowed_and_locked": outputs.tr_stowed_and_locked,
        "tr_position_pct": tr_position_pct,
    }


def _logic_states_from_outputs(outputs, raw_inputs: RawInputs) -> dict[str, str]:
    """Map C919 outputs into 'active' / 'blocked' / 'idle' per logic node.

    Semantics:
      ln_eicu_cmd2: active iff single_phase_unlock_power_on. Blocked iff any
        preflight condition would fire it (SW1/SW2 closed) but it did not.
      ln_eicu_cmd3: active iff three_phase_trcu_power_on. Blocked iff SW1
        closed and MLG_WOW but CMD3 did not latch (typically tr_inhibited).
      ln_tr_command3_enable: active iff the derived enable is true (approx
        three_phase AND NOT over_temp AND TRA<-1.4 AND NOT stowed-locked-1s).
        Not perfectly observable from Outputs alone, so we infer from
        three_phase_trcu_power_on AND !over_temp AND !tr_stowed_and_locked.
      ln_fadec_deploy_command: active iff fadec_deploy_command.
      ln_fadec_stow_command: active iff fadec_stow_command.
    """
    states: dict[str, str] = {}

    # "Triggerable" = the forward-path conditions that put this gate in the
    # running to fire. If the gate is NOT active but its triggerable path is
    # lit, something downstream (like tr_inhibited) must be blocking it, so
    # we report 'blocked'. If the triggerable path itself is not lit, the
    # gate is 'idle'.
    # ln_eicu_cmd2 — triggerable when TRA has entered a reverse window and
    # the aircraft is on the ground (selected MLG_WOW is TRUE).
    cmd2_triggerable = (raw_inputs.atltla or raw_inputs.apwtla) and outputs.selected_mlg_wow
    if outputs.single_phase_unlock_power_on:
        states["ln_eicu_cmd2"] = "active"
    elif cmd2_triggerable:
        states["ln_eicu_cmd2"] = "blocked"
    else:
        states["ln_eicu_cmd2"] = "idle"

    # ln_eicu_cmd3 — triggerable when the set-path is lit (APWTLA + ground +
    # engine). A latched tr_inhibited or stowed-locked reset will still flip
    # this to 'blocked' because the controller would otherwise have fired.
    cmd3_triggerable = (
        raw_inputs.apwtla
        and outputs.selected_mlg_wow
        and raw_inputs.engine_running
    )
    if outputs.three_phase_trcu_power_on:
        states["ln_eicu_cmd3"] = "active"
    elif cmd3_triggerable:
        states["ln_eicu_cmd3"] = "blocked"
    else:
        states["ln_eicu_cmd3"] = "idle"

    # ln_tr_command3_enable — approximation
    enable_active = (
        outputs.three_phase_trcu_power_on
        and not raw_inputs.etras_over_temp_fault
        and raw_inputs.tra_deg < _SW1_WINDOW_MAX_DEG
        and not outputs.tr_stowed_and_locked
    )
    enable_triggerable = outputs.three_phase_trcu_power_on
    if enable_active:
        states["ln_tr_command3_enable"] = "active"
    elif enable_triggerable:
        states["ln_tr_command3_enable"] = "blocked"
    else:
        states["ln_tr_command3_enable"] = "idle"

    # ln_fadec_deploy_command
    if outputs.fadec_deploy_command:
        states["ln_fadec_deploy_command"] = "active"
    elif enable_active and outputs.tr_wow:
        states["ln_fadec_deploy_command"] = "blocked"
    else:
        states["ln_fadec_deploy_command"] = "idle"

    # ln_fadec_stow_command
    if outputs.fadec_stow_command:
        states["ln_fadec_stow_command"] = "active"
    elif raw_inputs.tra_deg >= 0.0 and raw_inputs.engine_running:
        states["ln_fadec_stow_command"] = "blocked"
    else:
        states["ln_fadec_stow_command"] = "idle"

    return states


def _resolved_inputs_to_dict(raw: RawInputs, tr_position_pct: float) -> dict[str, Any]:
    return {
        "tra_deg": raw.tra_deg,
        "atltla": raw.atltla,
        "apwtla": raw.apwtla,
        "lgcu1_mlg_wow": raw.lgcu1_mlg_wow,
        "lgcu2_mlg_wow": raw.lgcu2_mlg_wow,
        "lgcu1_valid": raw.lgcu1_valid,
        "lgcu2_valid": raw.lgcu2_valid,
        "tr_inhibited": raw.tr_inhibited,
        "engine_running": raw.engine_running,
        "trcu_menu_mode": raw.trcu_menu_mode,
        "maintenance_cycle_on_going": raw.maintenance_cycle_on_going,
        "n1k_pct": raw.n1k_pct,
        "max_n1k_deploy_limit_pct": raw.max_n1k_deploy_limit_pct,
        "max_n1k_stow_limit_pct": raw.max_n1k_stow_limit_pct,
        "etras_over_temp_fault": raw.etras_over_temp_fault,
        "tr_position_pct": tr_position_pct,
    }
