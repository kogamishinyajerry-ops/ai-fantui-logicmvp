import json
import unittest
from pathlib import Path

from well_harness.controller_adapter import REFERENCE_DEPLOY_CONTROLLER_METADATA
from well_harness.models import HarnessConfig
from well_harness.system_spec import (
    CONTROL_SYSTEM_SPEC_KIND,
    CONTROL_SYSTEM_SPEC_SCHEMA_ID,
    CONTROL_SYSTEM_SPEC_VERSION,
    current_reference_workbench_spec,
    workbench_spec_from_dict,
    workbench_spec_to_dict,
)


PROJECT_ROOT = Path(__file__).parents[1]
CONTROL_SYSTEM_SPEC_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"


def load_control_system_spec_schema() -> dict:
    return json.loads(CONTROL_SYSTEM_SPEC_SCHEMA_PATH.read_text(encoding="utf-8"))


class ControlSystemWorkbenchSpecTests(unittest.TestCase):
    def test_current_reference_spec_captures_required_components(self):
        spec = current_reference_workbench_spec()
        components = {component.id: component for component in spec.components}

        self.assertEqual(spec.system_id, "reference_thrust_reverser_deploy")
        self.assertEqual(spec.source_of_truth, REFERENCE_DEPLOY_CONTROLLER_METADATA.source_of_truth)
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
        self.assertEqual(len(baseline.transitions), 5)
        self.assertEqual(6, len(baseline.steady_signals))
        self.assertIn("thr_lock == 1", baseline.completion_condition)

        self.assertIn("thr_lock_never_releases", fault_modes)
        self.assertIn("repair_hint", fault_modes["thr_lock_never_releases"].expected_diagnostic_sections)
        self.assertIn("fault_taxonomy", questions)
        self.assertIn("严格验收", questions["source_documents"].required_for)

    def test_workbench_spec_serializes_to_json_safe_payload(self):
        spec = current_reference_workbench_spec()
        payload = workbench_spec_to_dict(spec)
        encoded = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(payload["$schema"], CONTROL_SYSTEM_SPEC_SCHEMA_ID)
        self.assertEqual(payload["kind"], CONTROL_SYSTEM_SPEC_KIND)
        self.assertEqual(payload["version"], CONTROL_SYSTEM_SPEC_VERSION)
        self.assertIn("Reference Thrust Reverser Control Workbench Spec", encoded)
        self.assertIn("compressed_ra_tra_vdt_monitor", encoded)
        self.assertIn("thr_lock_never_releases", encoded)
        self.assertIn("suggested_logic_change", encoded)

    def test_workbench_spec_from_dict_round_trips_reference_payload(self):
        original = current_reference_workbench_spec()
        payload = workbench_spec_to_dict(original)
        restored = workbench_spec_from_dict(payload)

        self.assertEqual(original.system_id, restored.system_id)
        self.assertEqual(original.source_of_truth, restored.source_of_truth)
        self.assertEqual(original.logic_nodes[0].id, restored.logic_nodes[0].id)
        self.assertEqual(original.acceptance_scenarios[0].id, restored.acceptance_scenarios[0].id)
        self.assertEqual(original.fault_modes[0].id, restored.fault_modes[0].id)

    def test_control_system_spec_schema_documents_generated_payload_shape(self):
        schema = load_control_system_spec_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(CONTROL_SYSTEM_SPEC_SCHEMA_ID, schema["$id"])
        self.assertEqual(CONTROL_SYSTEM_SPEC_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(CONTROL_SYSTEM_SPEC_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(CONTROL_SYSTEM_SPEC_SCHEMA_ID, schema["properties"]["$schema"]["const"])

    def test_optional_jsonschema_validates_generated_control_system_spec_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_control_system_spec_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = workbench_spec_to_dict(current_reference_workbench_spec())
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))


if __name__ == "__main__":
    unittest.main()
