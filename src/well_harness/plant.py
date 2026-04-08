from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from well_harness.models import ControllerOutputs, HarnessConfig, PlantDebugState, PlantSensors


@dataclass(frozen=True)
class PlantState:
    tls_powered_s: float = 0.0
    pls_powered_s: float = 0.0
    tls_unlocked_ls: bool = False
    pls_unlocked_ls: Tuple[bool, bool, bool, bool] = (False, False, False, False)
    deploy_position_percent: float = 0.0

    def sensors(self, config: HarnessConfig) -> PlantSensors:
        return PlantSensors(
            tls_unlocked_ls=self.tls_unlocked_ls,
            pls_unlocked_ls=self.pls_unlocked_ls,
            # First-cut feedback simplification: treat any positive modeled
            # deploy travel as "not deployed" no longer being true. This is
            # not a confirmed real EEC signal model.
            reverser_not_deployed_eec=self.deploy_position_percent <= 0.0,
            reverser_fully_deployed_eec=self.deploy_position_percent >= 100.0,
            deploy_90_percent_vdt=self.deploy_position_percent >= config.deploy_90_threshold_percent,
            deploy_position_percent=self.deploy_position_percent,
        )

    def debug_state(self) -> PlantDebugState:
        return PlantDebugState(
            tls_powered_s=self.tls_powered_s,
            pls_powered_s=self.pls_powered_s,
            tls_unlocked_ls=self.tls_unlocked_ls,
            pls_unlocked_ls=self.pls_unlocked_ls,
            deploy_position_percent=self.deploy_position_percent,
        )


class SimplifiedDeployPlant:
    """A replaceable simplified plant model for deploy-side feedback."""

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self.config = config or HarnessConfig()

    def advance(self, state: PlantState, outputs: ControllerOutputs, dt_s: float) -> PlantState:
        tls_powered_s = state.tls_powered_s + dt_s if outputs.tls_115vac_cmd else 0.0
        tls_unlocked_ls = state.tls_unlocked_ls or (
            outputs.tls_115vac_cmd and tls_powered_s >= self.config.tls_unlock_delay_s
        )

        pls_powered_s = state.pls_powered_s + dt_s if outputs.pls_power_cmd else 0.0
        pls_ready = outputs.pls_power_cmd and pls_powered_s >= self.config.pls_unlock_delay_s
        previously_unlocked = all(state.pls_unlocked_ls)
        pls_unlocked = previously_unlocked or pls_ready
        pls_unlocked_ls = (pls_unlocked, pls_unlocked, pls_unlocked, pls_unlocked)

        effective_motor_drive = (
            outputs.etrac_540vdc_cmd
            and outputs.pdu_motor_cmd
            and outputs.pls_power_cmd
            and tls_unlocked_ls
            # First-cut plant simplification: motion is held until all modeled
            # PLS unlock indications are true. This is not a controller
            # logic3 gate; controller truth stays in DeployController.
            and all(pls_unlocked_ls)
        )

        deploy_position_percent = state.deploy_position_percent
        if effective_motor_drive:
            deploy_position_percent = min(
                100.0,
                deploy_position_percent + self.config.deploy_rate_percent_per_s * dt_s,
            )

        # This first-cut plant keeps unlock indications during deploy-side
        # operation and clears them only when reverse selection is fully removed.
        if not (
            outputs.tls_115vac_cmd
            or outputs.etrac_540vdc_cmd
            or outputs.pls_power_cmd
            or outputs.pdu_motor_cmd
        ):
            tls_unlocked_ls = False
            pls_unlocked_ls = (False, False, False, False)

        return PlantState(
            tls_powered_s=tls_powered_s,
            pls_powered_s=pls_powered_s,
            tls_unlocked_ls=tls_unlocked_ls,
            pls_unlocked_ls=pls_unlocked_ls,
            deploy_position_percent=deploy_position_percent,
        )
