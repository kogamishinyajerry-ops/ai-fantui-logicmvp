import unittest

from well_harness.controller import DeployController
from well_harness.models import ControllerOutputs, HarnessConfig, ResolvedInputs
from well_harness.plant import PlantState, SimplifiedDeployPlant
from well_harness.runner import SimulationRunner
from well_harness.scenarios import nominal_deploy_scenario, retract_reset_scenario
from well_harness.switches import LatchedThrottleSwitches, SwitchState


def make_inputs(**overrides):
    base = dict(
        radio_altitude_ft=5.0,
        tra_deg=-14.0,
        sw1=True,
        sw2=True,
        engine_running=True,
        aircraft_on_ground=True,
        reverser_inhibited=False,
        eec_enable=True,
        n1k=35.0,
        max_n1k_deploy_limit=60.0,
        tls_unlocked_ls=True,
        all_pls_unlocked_ls=True,
        reverser_not_deployed_eec=True,
        reverser_fully_deployed_eec=False,
        deploy_90_percent_vdt=False,
    )
    base.update(overrides)
    return ResolvedInputs(**base)


def make_outputs(**overrides):
    base = dict(
        logic1_active=True,
        logic2_active=True,
        logic3_active=True,
        logic4_active=False,
        tls_115vac_cmd=True,
        etrac_540vdc_cmd=True,
        eec_deploy_cmd=True,
        pls_power_cmd=True,
        pdu_motor_cmd=True,
        throttle_electronic_lock_release_cmd=False,
    )
    base.update(overrides)
    return ControllerOutputs(**base)


class DeployControllerTests(unittest.TestCase):
    def test_logic1_requires_all_confirmed_conditions(self):
        controller = DeployController(HarnessConfig())
        outputs = controller.evaluate(make_inputs(sw1=False))
        self.assertFalse(outputs.logic1_active)
        outputs = controller.evaluate(make_inputs(radio_altitude_ft=7.0))
        self.assertFalse(outputs.logic1_active)
        outputs = controller.evaluate(make_inputs(reverser_not_deployed_eec=False))
        self.assertFalse(outputs.logic1_active)

    def test_logic3_uses_tls_unlock_and_tra_threshold(self):
        controller = DeployController(HarnessConfig())
        outputs = controller.evaluate(make_inputs(tls_unlocked_ls=False))
        self.assertFalse(outputs.logic3_active)
        outputs = controller.evaluate(make_inputs(tra_deg=-10.0))
        self.assertFalse(outputs.logic3_active)
        outputs = controller.evaluate(make_inputs())
        self.assertTrue(outputs.logic3_active)

    def test_logic3_explain_includes_threshold_details(self):
        config = HarnessConfig()
        controller = DeployController(config)
        explain = controller.explain(make_inputs(tra_deg=-10.0)).logic3
        conditions = {condition.name: condition for condition in explain.conditions}

        self.assertFalse(explain.active)
        self.assertEqual(conditions["tra_deg"].current_value, -10.0)
        self.assertEqual(conditions["tra_deg"].comparison, "<=")
        self.assertEqual(conditions["tra_deg"].threshold_value, config.logic3_tra_deg_threshold)
        self.assertFalse(conditions["tra_deg"].passed)
        self.assertEqual(conditions["n1k"].threshold_value, 60.0)

    def test_logic1_ra_threshold_is_strictly_below_six_feet(self):
        controller = DeployController(HarnessConfig())

        outputs = controller.evaluate(make_inputs(radio_altitude_ft=6.0))

        self.assertFalse(outputs.logic1_active)
        self.assertFalse(outputs.tls_115vac_cmd)

    def test_logic3_blocks_commands_when_tra_has_not_reached_threshold(self):
        controller = DeployController(HarnessConfig())

        outputs = controller.evaluate(make_inputs(tra_deg=-11.0))

        self.assertFalse(outputs.logic3_active)
        self.assertFalse(outputs.eec_deploy_cmd)
        self.assertFalse(outputs.pls_power_cmd)
        self.assertFalse(outputs.pdu_motor_cmd)

    def test_logic3_requires_n1k_below_deploy_limit(self):
        controller = DeployController(HarnessConfig())

        outputs = controller.evaluate(make_inputs(n1k=60.0, max_n1k_deploy_limit=60.0))

        self.assertFalse(outputs.logic3_active)
        self.assertFalse(outputs.eec_deploy_cmd)
        self.assertFalse(outputs.pls_power_cmd)
        self.assertFalse(outputs.pdu_motor_cmd)

    def test_logic4_requires_deploy_90_percent_vdt(self):
        controller = DeployController(HarnessConfig())

        outputs = controller.evaluate(make_inputs(deploy_90_percent_vdt=False))

        self.assertFalse(outputs.logic4_active)
        self.assertFalse(outputs.throttle_electronic_lock_release_cmd)


class SwitchModelTests(unittest.TestCase):
    def test_sw1_sw2_latches_hold_until_reverse_selection_returns_near_zero(self):
        switches = LatchedThrottleSwitches(HarnessConfig())
        state = SwitchState(previous_tra_deg=0.0)

        state = switches.update(state, -3.0)
        self.assertTrue(state.sw1)
        self.assertFalse(state.sw2)

        state = switches.update(state, -8.0)
        self.assertTrue(state.sw1)
        self.assertTrue(state.sw2)

        state = switches.update(state, -6.0)
        self.assertTrue(state.sw1)
        self.assertTrue(state.sw2)

        state = switches.update(state, -4.0)
        self.assertTrue(state.sw1)
        self.assertFalse(state.sw2)

        state = switches.update(state, -1.0)
        self.assertFalse(state.sw1)
        self.assertFalse(state.sw2)


class SimplifiedPlantTests(unittest.TestCase):
    def test_deploy_motion_waits_for_all_pls_unlocks_in_first_cut_plant(self):
        plant = SimplifiedDeployPlant(HarnessConfig())
        outputs = make_outputs()
        state = PlantState(
            tls_unlocked_ls=True,
            pls_unlocked_ls=(False, False, False, False),
            deploy_position_percent=0.0,
        )

        blocked = plant.advance(state, outputs, dt_s=0.1)
        self.assertEqual(blocked.deploy_position_percent, 0.0)
        self.assertFalse(all(blocked.pls_unlocked_ls))

        unlocked_state = PlantState(
            tls_unlocked_ls=True,
            pls_unlocked_ls=(True, True, True, True),
            deploy_position_percent=0.0,
        )
        moving = plant.advance(unlocked_state, outputs, dt_s=0.1)
        self.assertGreater(moving.deploy_position_percent, 0.0)

    def test_reverser_not_deployed_eec_is_first_cut_position_simplification(self):
        config = HarnessConfig()

        parked = PlantState(deploy_position_percent=0.0).sensors(config)
        moved = PlantState(deploy_position_percent=0.1).sensors(config)

        self.assertTrue(parked.reverser_not_deployed_eec)
        self.assertFalse(moved.reverser_not_deployed_eec)


class RunnerTests(unittest.TestCase):
    def test_nominal_deploy_reaches_logic4(self):
        scenario = nominal_deploy_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))
        self.assertTrue(any(row.logic4_active for row in result.rows))
        self.assertGreaterEqual(result.rows[-1].deploy_position_percent, 90.0)

    def test_retract_reset_clears_switches_and_logic(self):
        scenario = retract_reset_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))
        tail = result.rows[-1]
        self.assertFalse(tail.sw1)
        self.assertFalse(tail.sw2)
        self.assertFalse(tail.logic1_active)
        self.assertFalse(tail.logic2_active)

    def test_logic_transition_diagnostics_capture_failed_and_changed_conditions(self):
        scenario = nominal_deploy_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))

        logic3_diagnosis = result.logic_transition_diagnostics(logic_name="logic3")[0]

        self.assertEqual(logic3_diagnosis.logic_name, "logic3")
        self.assertEqual(logic3_diagnosis.before_time_s, 1.8)
        self.assertEqual(logic3_diagnosis.after_time_s, 1.9)
        self.assertFalse(logic3_diagnosis.before_active)
        self.assertTrue(logic3_diagnosis.after_active)
        self.assertEqual(logic3_diagnosis.before_failed_conditions, ("tra_deg",))
        self.assertEqual(logic3_diagnosis.after_failed_conditions, ())
        self.assertEqual(logic3_diagnosis.changed_conditions[0].name, "tra_deg")
        self.assertEqual(logic3_diagnosis.changed_conditions[0].before_current_value, -7.0)
        self.assertEqual(logic3_diagnosis.changed_conditions[0].after_current_value, -14.0)
        self.assertEqual(logic3_diagnosis.changed_conditions[0].threshold_value, -11.74)

    def test_logic_transition_diagnostics_include_context_changes(self):
        scenario = nominal_deploy_scenario()
        result = SimulationRunner().run(scenario.name, list(scenario.frames))

        logic4_diagnosis = result.logic_transition_diagnostics(logic_name="logic4")[0]
        context_changes = {
            (change.field_group, change.field_name): change
            for change in logic4_diagnosis.context_changes
        }

        throttle_lock_change = context_changes[("controller_outputs", "throttle_lock_release_cmd")]
        self.assertFalse(throttle_lock_change.before_value)
        self.assertTrue(throttle_lock_change.after_value)

        vdt_change = context_changes[("plant_sensors", "deploy_90_percent_vdt")]
        self.assertFalse(vdt_change.before_value)
        self.assertTrue(vdt_change.after_value)

        deploy_position_change = context_changes[("plant_sensors", "deploy_position_percent")]
        self.assertEqual(deploy_position_change.before_value, 87.0)
        self.assertEqual(deploy_position_change.after_value, 90.0)

        pls_timer_change = context_changes[("plant_state", "pls_powered_s")]
        self.assertGreater(pls_timer_change.after_value, pls_timer_change.before_value)


if __name__ == "__main__":
    unittest.main()
