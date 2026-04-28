"""C919 E-TRAS tick / reset API helpers.

Single source of truth for the JSON shape exchanged with the C919
sim panel (c919_etras_panel/index.html). Both the unified workbench
demo_server (port 8002, P56-04) and the standalone panel server
(port 9191, scripts/c919_etras_panel_server.py) import these
helpers so the panel works identically on either port.

Before P56-04 (2026-04-28): these functions were inline in
scripts/c919_etras_panel_server.py and the unified demo_server
returned 404 on /api/tick. Moving them here lets demo_server.py
mount the same simulation engine.
"""

from __future__ import annotations

from threading import Lock
from typing import Any, Dict, Tuple

from well_harness.adapters.c919_etras_frozen_v1 import (
    C919ReverseThrustSystem,
    FrozenConfig,
    LockInputs,
    RawInputs,
    SystemState,
    TelemetryLogger,
)
from well_harness.adapters.c919_etras_frozen_v1.cmd3_latch_controller import (
    derive_tr_command3_enable,
)


__all__ = [
    "parse_c919_raw_inputs",
    "build_c919_tick_response",
    "handle_c919_tick",
    "reset_c919_system",
    "get_c919_log_records",
    "C919SimState",
]


def parse_c919_raw_inputs(payload: Dict[str, Any]) -> RawInputs:
    """Parse the panel's POST body (or any matching dict) into a
    `RawInputs` dataclass. Missing fields fall back to defaults
    (booleans=False except _valid + locks which default to True;
    numerics=0 except n1k_pct=50 / max_*_limit_pct as in the
    standalone server)."""
    def b(key: str, default: bool = False) -> bool:
        return bool(payload.get(key, default))

    def f(key: str, default: float = 0.0) -> float:
        return float(payload.get(key, default))

    locks_raw = payload.get("locks", {}) or {}
    locks = LockInputs(
        tls_locked=bool(locks_raw.get("tls_locked", True)),
        tls_unlocked=bool(locks_raw.get("tls_unlocked", False)),
        pylon_lock_l_locked=bool(locks_raw.get("pylon_lock_l_locked", True)),
        pylon_lock_l_unlocked=bool(locks_raw.get("pylon_lock_l_unlocked", False)),
        pylon_lock_r_locked=bool(locks_raw.get("pylon_lock_r_locked", True)),
        pylon_lock_r_unlocked=bool(locks_raw.get("pylon_lock_r_unlocked", False)),
        pls_l_locked=bool(locks_raw.get("pls_l_locked", True)),
        pls_l_unlocked=bool(locks_raw.get("pls_l_unlocked", False)),
        pls_r_locked=bool(locks_raw.get("pls_r_locked", True)),
        pls_r_unlocked=bool(locks_raw.get("pls_r_unlocked", False)),
    )
    return RawInputs(
        lgcu1_mlg_wow=b("lgcu1_mlg_wow"),
        lgcu2_mlg_wow=b("lgcu2_mlg_wow"),
        lgcu1_valid=b("lgcu1_valid", True),
        lgcu2_valid=b("lgcu2_valid", True),
        tra_deg=f("tra_deg"),
        atltla=b("atltla"),
        apwtla=b("apwtla"),
        tr_inhibited=b("tr_inhibited"),
        engine_running=b("engine_running"),
        trcu_menu_mode=b("trcu_menu_mode"),
        maintenance_cycle_on_going=b("maintenance_cycle_on_going"),
        tr_position_pct=f("tr_position_pct"),
        n1k_pct=f("n1k_pct", 50.0),
        max_n1k_deploy_limit_pct=f("max_n1k_deploy_limit_pct", 84.0),
        max_n1k_stow_limit_pct=f("max_n1k_stow_limit_pct", 72.0),
        etras_over_temp_fault=b("etras_over_temp_fault"),
        locks=locks,
    )


def build_c919_tick_response(
    outputs,
    sys_ref: C919ReverseThrustSystem,
    inp: RawInputs,
) -> Dict[str, Any]:
    """Shape the C919 system's tick output into the JSON the panel's
    updateUI() consumes. Keys must match c919_etras_panel/index.html
    expectations (`data.state`, `data.derived.*`, `data.outputs.*`,
    `data.locks.*`)."""
    tr_cmd3_enable = derive_tr_command3_enable(
        outputs.tr_stowed_and_locked, inp.etras_over_temp_fault
    )
    return {
        "t_s": round(sys_ref.t_s, 3),
        "state": outputs.state.value,
        "derived": {
            "selected_mlg_wow": outputs.selected_mlg_wow,
            "tr_wow": outputs.tr_wow,
            "tr_wow_acc_s": round(sys_ref.tr_wow_filter._true_acc_s, 3),
            "unlock_confirmed": outputs.unlock_confirmed,
            "tr_stowed_and_locked": outputs.tr_stowed_and_locked,
            "stowed_acc_s": round(sys_ref.locks_agg._stowed_locked_acc_s, 3),
            "tr_command3_enable": tr_cmd3_enable,
            "cmd3_latch": sys_ref.cmd3.latch,
            "cmd2_timer_s": round(sys_ref.cmd2.timer_s, 2),
        },
        "outputs": {
            "single_phase_unlock_power_on": outputs.single_phase_unlock_power_on,
            "three_phase_trcu_power_on": outputs.three_phase_trcu_power_on,
            "fadec_deploy_command": outputs.fadec_deploy_command,
            "fadec_stow_command": outputs.fadec_stow_command,
            "tr_stowed_and_locked": outputs.tr_stowed_and_locked,
            "unlock_confirmed": outputs.unlock_confirmed,
        },
        "locks": {
            "tls_locked": outputs.tls_locked,
            "tls_unlocked": outputs.tls_unlocked,
            "pylon_lock_l_locked": outputs.pylon_lock_l_locked,
            "pylon_lock_l_unlocked": outputs.pylon_lock_l_unlocked,
            "pylon_lock_r_locked": outputs.pylon_lock_r_locked,
            "pylon_lock_r_unlocked": outputs.pylon_lock_r_unlocked,
            "pls_l_locked": outputs.pls_l_locked,
            "pls_l_unlocked": outputs.pls_l_unlocked,
            "pls_r_locked": outputs.pls_r_locked,
            "pls_r_unlocked": outputs.pls_r_unlocked,
        },
    }


class C919SimState:
    """Module-level container for the persistent C919 simulation
    instance. Tick continuity (FSM transitions, timers, accumulators)
    requires the system to survive between HTTP requests."""

    def __init__(self, config: FrozenConfig | None = None) -> None:
        self.config = config or FrozenConfig()
        self.lock = Lock()
        self.logger = TelemetryLogger()
        self.system = C919ReverseThrustSystem(
            config=self.config, logger=self.logger,
        )

    def reset(self) -> Dict[str, Any]:
        """Rebuild the system from scratch — zeroes t_s, FSM back to
        S0_AIR_STOWED_LOCKED, all timers / accumulators clear."""
        with self.lock:
            self.logger = TelemetryLogger()
            self.system = C919ReverseThrustSystem(
                config=self.config, logger=self.logger,
            )
        return {"ok": True, "state": SystemState.S0_AIR_STOWED_LOCKED.value}


def handle_c919_tick(
    state: C919SimState,
    payload: Dict[str, Any],
) -> Tuple[int, Dict[str, Any]]:
    """End-to-end handler: parse → tick → build response. Returns
    (status_code, response_body) so the HTTP server only needs to
    serialize and write."""
    try:
        inp = parse_c919_raw_inputs(payload)
        dt = float(payload.get("dt_s", state.config.step_s))
        with state.lock:
            out = state.system.tick(inp, dt)
            resp = build_c919_tick_response(out, state.system, inp)
        return 200, resp
    except Exception as e:
        return 400, {"error": str(e)}


def reset_c919_system(state: C919SimState) -> Dict[str, Any]:
    """Wrapper kept so demo_server.py and the standalone server use
    the same canonical reset path."""
    return state.reset()


def get_c919_log_records(state: C919SimState, limit: int = 200) -> list:
    """Return the last `limit` telemetry records the C919 system has
    accumulated. Used by the panel's chart/log drawer (`refreshChart`
    fetches /api/log periodically) and by debugging surfaces.

    Codex P56-04 round-1 P2: until this helper landed, the panel
    correctly polled /api/log on the unified server but received
    404, leaving the chart/log drawer dark even though /api/tick
    worked."""
    with state.lock:
        # Snapshot the slice under the lock so JSON serialization
        # can run unlocked (records is a list of dataclass-like
        # entries; slicing is sufficient for thread-safe handoff).
        return list(state.logger.records[-limit:])
