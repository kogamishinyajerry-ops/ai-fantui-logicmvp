import json
import unittest

from well_harness.models import HarnessConfig
from well_harness.system_spec import current_reference_workbench_spec, workbench_spec_to_dict


class ControlSystemWorkbenchSpecTests(unittest.TestCase):
    def test_current_reference_spec_captures_required_components(self):
        spec = current_reference_workbench_spec()
        components = {component.id: component for component in spec.components}

        self.assertEqual(spec.system_id, "reference_thrust_reverser_deploy")
        self.assertEqual(spec.source_of_truth, "src/well_harness/controller.py")
        self.assertIn("strict acceptance playback", spec.objective)

        self.assertEqual(components["sw1"].state_shape, "binary")
        self.assertEqual(components["sw2"].state_shape, "binary")
        self.assertEqual(components["tls_voltage_v"].allowed_range, (0.0, 115.0))
        self.assertEqual(components["etrac_voltage_v"].allowed_range, (0.0, 540.0))
        self.assertEqual(
            components["tra_deg"].allowed_range,
            (HarnessConfig().reverse_travel_min_deg, HarnessConfig().reverse_travel_max_deg),
        )
        self.assertEqual(components["thr_lock"].allowed_states, ("0", "1"))

    def test_current_reference_spec_exposes_logic_fault_and_acceptance_layers(self):
        spec = current_reference_workbench_spec()
        logic_nodes = {node.id: node for node in spec.logic_nodes}
        scenarios = {scenario.id: scenario for scenario in spec.acceptance_scenarios}
        fault_modes = {fault.id: fault for fault in spec.fault_modes}
        questions = {item.id: item for item in spec.onboarding_questions}

        self.assertIn("logic4", logic_nodes)
        self.assertEqual(logic_nodes["logic4"].downstream_component_ids, ("thr_lock",))
        self.assertIn("deploy_feedback_percent", {condition.source_component_id for condition in logic_nodes["logic4"].conditions})

        baseline = scenarios["compressed_ra_tra_vdt_monitor"]
        self.assertEqual(baseline.time_scale_factor, 0.1)
        self.assertEqual(baseline.total_duration_s, 7.0)
        self.assertEqual(len(baseline.transitions), 3)
        self.assertIn("thr_lock == 1", baseline.completion_condition)

        self.assertIn("thr_lock_never_releases", fault_modes)
        self.assertIn("repair_hint", fault_modes["thr_lock_never_releases"].expected_diagnostic_sections)
        self.assertIn("fault_taxonomy", questions)
        self.assertIn("严格验收", questions["source_documents"].required_for)

    def test_workbench_spec_serializes_to_json_safe_payload(self):
        spec = current_reference_workbench_spec()
        payload = workbench_spec_to_dict(spec)
        encoded = json.dumps(payload, ensure_ascii=False)

        self.assertIn("Reference Thrust Reverser Control Workbench Spec", encoded)
        self.assertIn("compressed_ra_tra_vdt_monitor", encoded)
        self.assertIn("thr_lock_never_releases", encoded)
        self.assertIn("suggested_logic_change", encoded)


if __name__ == "__main__":
    unittest.main()
