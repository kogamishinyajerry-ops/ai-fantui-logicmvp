"""FANTUI stateful tick runtime.

Wraps the pure DeployController with the state-bearing plant model
(SimplifiedDeployPlant) and the latched TRA switches (LatchedThrottleSwitches)
so that a browser client can drive the reverser logic one discrete step at
a time, accumulating VDT / lock indications across ticks.

Used by demo_server's ``/api/fantui/tick`` endpoint as a live counterpart to
the C919 panel's stateful console. The stateless ``/api/lever-snapshot``
endpoint intentionally remains untouched — it fills a different UX slot
(single-shot evaluation) and feeds ``/api/timeline-simulate``.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List

from well_harness.controller import DeployController
from well_harness.models import (
    ControllerOutputs,
    HarnessConfig,
    PilotInputs,
    ResolvedInputs,
)
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.switches import LatchedThrottleSwitches, SwitchState


@dataclass
class FantuiTickRecord:
    """One row in the ring buffer. Mirrors the C919 TelemetryLogger contract
    closely enough that both can feed the same shared front-end chart module.
    """

    t_s: float
    # Pilot-visible inputs (echoed so the timeline view can show them)
    radio_altitude_ft: float
    tra_deg: float
    engine_running: bool
    aircraft_on_ground: bool
    reverser_inhibited: bool
    eec_enable: bool
    n1k: float
    max_n1k_deploy_limit: float
    # Derived
    sw1: bool
    sw2: bool
    deploy_position_percent: float
    tls_unlocked_ls: bool
    all_pls_unlocked_ls: bool
    deploy_90_percent_vdt: bool
    # Controller outputs (active gates + commands)
    logic1_active: bool
    logic2_active: bool
    logic3_active: bool
    logic4_active: bool
    tls_115vac_cmd: bool
    etrac_540vdc_cmd: bool
    eec_deploy_cmd: bool
    pls_power_cmd: bool
    pdu_motor_cmd: bool
    throttle_electronic_lock_release_cmd: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "t_s": round(self.t_s, 6),
            "radio_altitude_ft": self.radio_altitude_ft,
            "tra_deg": self.tra_deg,
            "engine_running": self.engine_running,
            "aircraft_on_ground": self.aircraft_on_ground,
            "reverser_inhibited": self.reverser_inhibited,
            "eec_enable": self.eec_enable,
            "n1k": self.n1k,
            "max_n1k_deploy_limit": self.max_n1k_deploy_limit,
            "sw1": self.sw1,
            "sw2": self.sw2,
            "deploy_position_percent": round(self.deploy_position_percent, 3),
            "tls_unlocked_ls": self.tls_unlocked_ls,
            "all_pls_unlocked_ls": self.all_pls_unlocked_ls,
            "deploy_90_percent_vdt": self.deploy_90_percent_vdt,
            "logic1_active": self.logic1_active,
            "logic2_active": self.logic2_active,
            "logic3_active": self.logic3_active,
            "logic4_active": self.logic4_active,
            "tls_115vac_cmd": self.tls_115vac_cmd,
            "etrac_540vdc_cmd": self.etrac_540vdc_cmd,
            "eec_deploy_cmd": self.eec_deploy_cmd,
            "pls_power_cmd": self.pls_power_cmd,
            "pdu_motor_cmd": self.pdu_motor_cmd,
            "throttle_electronic_lock_release_cmd": self.throttle_electronic_lock_release_cmd,
        }


class FantuiTickSystem:
    """Accumulates controller/plant state across ticks.

    The controller itself is pure — ``DeployController.evaluate`` always
    returns the same outputs for the same inputs — so the state that matters
    lives in the plant (lock indications, deploy percentage, powered-seconds
    integrators) and in the latched TRA switches.
    """

    LOG_CAP = 400

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()
        self.controller = DeployController(self.config)
        self.plant = SimplifiedDeployPlant(self.config)
        self.switches = LatchedThrottleSwitches(self.config)
        self._t_s: float = 0.0
        self._plant_state: PlantState = PlantState()
        self._switch_state: SwitchState = SwitchState(previous_tra_deg=0.0)
        self._log: Deque[FantuiTickRecord] = deque(maxlen=self.LOG_CAP)

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def t_s(self) -> float:
        return self._t_s

    @property
    def plant_state(self) -> PlantState:
        return self._plant_state

    @property
    def switch_state(self) -> SwitchState:
        return self._switch_state

    def reset(self) -> None:
        self._t_s = 0.0
        self._plant_state = PlantState()
        self._switch_state = SwitchState(previous_tra_deg=0.0)
        self._log.clear()

    def records(self) -> List[Dict[str, Any]]:
        return [r.as_dict() for r in self._log]

    def tick(self, pilot: PilotInputs, dt_s: float) -> FantuiTickRecord:
        """Advance one discrete step.

        Plant and switches use the pilot inputs + previous outputs to update
        sensors before the controller re-evaluates — matching the pattern
        used by ``runner.py`` in non-streaming traces.
        """
        if dt_s <= 0:
            raise ValueError("dt_s must be > 0")

        # Update latched switches from TRA motion
        self._switch_state = self.switches.update(self._switch_state, pilot.tra_deg)

        # Build resolved inputs using current plant sensors
        sensors = self._plant_state.sensors(self.config)
        resolved = ResolvedInputs(
            radio_altitude_ft=pilot.radio_altitude_ft,
            tra_deg=pilot.tra_deg,
            sw1=self._switch_state.sw1,
            sw2=self._switch_state.sw2,
            engine_running=pilot.engine_running,
            aircraft_on_ground=pilot.aircraft_on_ground,
            reverser_inhibited=pilot.reverser_inhibited,
            eec_enable=pilot.eec_enable,
            n1k=pilot.n1k,
            max_n1k_deploy_limit=pilot.max_n1k_deploy_limit,
            tls_unlocked_ls=sensors.tls_unlocked_ls,
            all_pls_unlocked_ls=all(sensors.pls_unlocked_ls),
            reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
            reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
            deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
        )

        outputs: ControllerOutputs = self.controller.evaluate(resolved)

        # Advance plant with the commands we just issued
        self._plant_state = self.plant.advance(self._plant_state, outputs, dt_s)
        self._t_s += dt_s

        rec = FantuiTickRecord(
            t_s=self._t_s,
            radio_altitude_ft=pilot.radio_altitude_ft,
            tra_deg=pilot.tra_deg,
            engine_running=pilot.engine_running,
            aircraft_on_ground=pilot.aircraft_on_ground,
            reverser_inhibited=pilot.reverser_inhibited,
            eec_enable=pilot.eec_enable,
            n1k=pilot.n1k,
            max_n1k_deploy_limit=pilot.max_n1k_deploy_limit,
            sw1=self._switch_state.sw1,
            sw2=self._switch_state.sw2,
            deploy_position_percent=self._plant_state.deploy_position_percent,
            tls_unlocked_ls=self._plant_state.tls_unlocked_ls,
            all_pls_unlocked_ls=all(self._plant_state.pls_unlocked_ls),
            deploy_90_percent_vdt=self._plant_state.sensors(self.config).deploy_90_percent_vdt,
            logic1_active=outputs.logic1_active,
            logic2_active=outputs.logic2_active,
            logic3_active=outputs.logic3_active,
            logic4_active=outputs.logic4_active,
            tls_115vac_cmd=outputs.tls_115vac_cmd,
            etrac_540vdc_cmd=outputs.etrac_540vdc_cmd,
            eec_deploy_cmd=outputs.eec_deploy_cmd,
            pls_power_cmd=outputs.pls_power_cmd,
            pdu_motor_cmd=outputs.pdu_motor_cmd,
            throttle_electronic_lock_release_cmd=outputs.throttle_electronic_lock_release_cmd,
        )
        self._log.append(rec)
        return rec


def parse_pilot_inputs(body: Dict[str, Any]) -> PilotInputs:
    """Validate and coerce a JSON POST body into ``PilotInputs``.

    Defaults match the demo.html initial state so a minimal request body
    still tick-runs. Raises ``ValueError`` on type errors.
    """
    def f(key: str, default: float) -> float:
        v = body.get(key, default)
        try:
            return float(v)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"field {key!r} must be a number") from exc

    def b(key: str, default: bool) -> bool:
        v = body.get(key, default)
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        raise ValueError(f"field {key!r} must be a boolean")

    return PilotInputs(
        radio_altitude_ft=f("radio_altitude_ft", 0.0),
        tra_deg=f("tra_deg", 0.0),
        engine_running=b("engine_running", False),
        aircraft_on_ground=b("aircraft_on_ground", True),
        reverser_inhibited=b("reverser_inhibited", False),
        eec_enable=b("eec_enable", True),
        n1k=f("n1k", 50.0),
        max_n1k_deploy_limit=f("max_n1k_deploy_limit", 85.0),
    )
