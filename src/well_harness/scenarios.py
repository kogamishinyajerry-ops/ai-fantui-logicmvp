from __future__ import annotations

from well_harness.models import PilotFrame, Scenario


def nominal_deploy_scenario() -> Scenario:
    return Scenario(
        name="nominal-deploy",
        frames=[
            PilotFrame(
                duration_s=0.5,
                radio_altitude_ft=10.0,
                tra_deg=0.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
            PilotFrame(
                duration_s=0.7,
                radio_altitude_ft=5.0,
                tra_deg=-2.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
            PilotFrame(
                duration_s=0.7,
                radio_altitude_ft=5.0,
                tra_deg=-7.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
            PilotFrame(
                duration_s=4.0,
                radio_altitude_ft=5.0,
                tra_deg=-14.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
        ],
    )


def retract_reset_scenario() -> Scenario:
    return Scenario(
        name="retract-reset",
        frames=[
            PilotFrame(
                duration_s=0.6,
                radio_altitude_ft=5.0,
                tra_deg=-2.5,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
            PilotFrame(
                duration_s=0.8,
                radio_altitude_ft=5.0,
                tra_deg=-7.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
            PilotFrame(
                duration_s=0.8,
                radio_altitude_ft=5.0,
                tra_deg=-13.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
            PilotFrame(
                duration_s=1.2,
                radio_altitude_ft=5.0,
                tra_deg=0.0,
                engine_running=True,
                aircraft_on_ground=True,
                reverser_inhibited=False,
                eec_enable=True,
                n1k=35.0,
                max_n1k_deploy_limit=60.0,
            ),
        ],
    )


BUILT_IN_SCENARIOS = {
    "nominal-deploy": nominal_deploy_scenario,
    "retract-reset": retract_reset_scenario,
}
