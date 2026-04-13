from __future__ import annotations

from well_harness.controller_adapter import ControllerTruthAdapter, build_reference_controller_adapter
from well_harness.models import (
    HarnessConfig,
    PilotFrame,
    PilotInputs,
    ResolvedInputs,
    SimulationResult,
    TraceRow,
)
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.switches import LatchedThrottleSwitches, SwitchState


class SimulationRunner:
    def __init__(
        self,
        config: HarnessConfig | None = None,
        controller_adapter: ControllerTruthAdapter | None = None,
    ) -> None:
        self.config = config or HarnessConfig()
        self.controller_adapter = controller_adapter or build_reference_controller_adapter(self.config)
        self.switches = LatchedThrottleSwitches(self.config)
        self.plant = SimplifiedDeployPlant(self.config)

    def run(self, scenario_name: str, frames: list[PilotFrame]) -> SimulationResult:
        rows = []
        time_s = 0.0
        plant_state = PlantState()
        initial_tra = frames[0].tra_deg if frames else 0.0
        switch_state = SwitchState(previous_tra_deg=initial_tra)

        for frame in frames:
            steps = max(1, round(frame.duration_s / self.config.step_s))
            for _ in range(steps):
                switch_state = self.switches.update(switch_state, frame.tra_deg)
                sensors = plant_state.sensors(self.config)
                pilot_inputs = PilotInputs(
                    radio_altitude_ft=frame.radio_altitude_ft,
                    tra_deg=frame.tra_deg,
                    engine_running=frame.engine_running,
                    aircraft_on_ground=frame.aircraft_on_ground,
                    reverser_inhibited=frame.reverser_inhibited,
                    eec_enable=frame.eec_enable,
                    n1k=frame.n1k,
                    max_n1k_deploy_limit=frame.max_n1k_deploy_limit,
                )
                inputs = ResolvedInputs(
                    radio_altitude_ft=pilot_inputs.radio_altitude_ft,
                    tra_deg=pilot_inputs.tra_deg,
                    sw1=switch_state.sw1,
                    sw2=switch_state.sw2,
                    engine_running=pilot_inputs.engine_running,
                    aircraft_on_ground=pilot_inputs.aircraft_on_ground,
                    reverser_inhibited=pilot_inputs.reverser_inhibited,
                    eec_enable=pilot_inputs.eec_enable,
                    n1k=pilot_inputs.n1k,
                    max_n1k_deploy_limit=pilot_inputs.max_n1k_deploy_limit,
                    tls_unlocked_ls=sensors.tls_unlocked_ls,
                    all_pls_unlocked_ls=sensors.all_pls_unlocked,
                    reverser_not_deployed_eec=sensors.reverser_not_deployed_eec,
                    reverser_fully_deployed_eec=sensors.reverser_fully_deployed_eec,
                    deploy_90_percent_vdt=sensors.deploy_90_percent_vdt,
                )
                outputs, explain = self.controller_adapter.evaluate_with_explain(inputs)
                rows.append(
                    TraceRow(
                        time_s=round(time_s, 3),
                        pilot=pilot_inputs,
                        resolved_inputs=inputs,
                        plant_sensors=sensors,
                        plant_state=plant_state.debug_state(),
                        controller_outputs=outputs,
                        controller_explain=explain,
                    )
                )
                plant_state = self.plant.advance(plant_state, outputs, self.config.step_s)
                time_s += self.config.step_s

        return SimulationResult(scenario_name=scenario_name, rows=rows)
