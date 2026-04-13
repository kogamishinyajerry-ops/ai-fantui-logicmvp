import json
import unittest
from pathlib import Path

from well_harness.adapters.landing_gear_adapter import (
    LANDING_GEAR_CONTROLLER_METADATA,
    LANDING_GEAR_PRESSURE_THRESHOLD_PSI,
    LANDING_GEAR_SYSTEM_ID,
    build_landing_gear_controller_adapter,
)
from well_harness.controller_adapter import (
    CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
)
from well_harness.system_spec import CONTROL_SYSTEM_SPEC_SCHEMA_ID


PROJECT_ROOT = Path(__file__).parents[1]
METADATA_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "controller_truth_adapter_metadata_v1.schema.json"
SPEC_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class LandingGearAdapterTests(unittest.TestCase):
    def test_landing_gear_adapter_exposes_expected_metadata(self):
        adapter = build_landing_gear_controller_adapter()

        self.assertEqual(LANDING_GEAR_CONTROLLER_METADATA, adapter.metadata)
        self.assertEqual("landing-gear-controller-adapter", adapter.metadata.adapter_id)
        self.assertEqual(LANDING_GEAR_SYSTEM_ID, adapter.metadata.system_id)

    def test_landing_gear_adapter_metadata_serializes_to_schema_aware_payload(self):
        payload = build_landing_gear_controller_adapter().metadata.to_dict()

        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID, payload["$schema"])
        self.assertEqual("landing-gear-controller-adapter", payload["adapter_id"])
        self.assertEqual(LANDING_GEAR_SYSTEM_ID, payload["system_id"])
        self.assertEqual("src/well_harness/adapters/landing_gear_adapter.py", payload["source_of_truth"])

    def test_landing_gear_adapter_load_spec_exposes_schema_aware_second_system_spec(self):
        payload = build_landing_gear_controller_adapter().load_spec()

        self.assertEqual(CONTROL_SYSTEM_SPEC_SCHEMA_ID, payload["$schema"])
        self.assertEqual(LANDING_GEAR_SYSTEM_ID, payload["system_id"])
        self.assertEqual("src/well_harness/adapters/landing_gear_adapter.py", payload["source_of_truth"])
        self.assertEqual(2, len(payload["logic_nodes"]))
        self.assertEqual(2, len(payload["fault_modes"]))

    def test_optional_jsonschema_validates_landing_gear_adapter_payloads_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        metadata_schema = load_json(METADATA_SCHEMA_PATH)
        spec_schema = load_json(SPEC_SCHEMA_PATH)
        Draft202012Validator.check_schema(metadata_schema)
        Draft202012Validator.check_schema(spec_schema)

        metadata_validator = Draft202012Validator(metadata_schema)
        metadata_errors = sorted(
            metadata_validator.iter_errors(build_landing_gear_controller_adapter().metadata.to_dict()),
            key=lambda error: tuple(error.absolute_path),
        )
        self.assertEqual([], metadata_errors, "\n".join(error.message for error in metadata_errors[:10]))

        spec_validator = Draft202012Validator(spec_schema)
        spec_errors = sorted(
            spec_validator.iter_errors(build_landing_gear_controller_adapter().load_spec()),
            key=lambda error: tuple(error.absolute_path),
        )
        self.assertEqual([], spec_errors, "\n".join(error.message for error in spec_errors[:10]))

    def test_landing_gear_adapter_evaluates_nominal_snapshot(self):
        evaluation = build_landing_gear_controller_adapter().evaluate_snapshot(
            {
                "gear_handle_position": "DOWN",
                "hydraulic_pressure_psi": 2850.0,
                "uplock_released": True,
                "gear_position_percent": 100.0,
                "downlock_engaged": True,
            }
        )

        self.assertEqual(LANDING_GEAR_SYSTEM_ID, evaluation.system_id)
        self.assertEqual(
            ("lg_l1_handle_and_pressure", "lg_l2_extend_after_uplock_release"),
            evaluation.active_logic_node_ids,
        )
        self.assertTrue(evaluation.asserted_component_values["selector_valve_cmd"])
        self.assertTrue(evaluation.asserted_component_values["extend_actuator_cmd"])
        self.assertTrue(evaluation.completion_reached)
        self.assertEqual((), evaluation.blocked_reasons)

    def test_landing_gear_adapter_blocks_low_pressure_snapshot(self):
        evaluation = build_landing_gear_controller_adapter().evaluate_snapshot(
            {
                "gear_handle_position": "DOWN",
                "hydraulic_pressure_psi": 1500.0,
                "uplock_released": False,
                "gear_position_percent": 0.0,
                "downlock_engaged": False,
            }
        )

        self.assertEqual((), evaluation.active_logic_node_ids)
        self.assertFalse(evaluation.asserted_component_values["selector_valve_cmd"])
        self.assertFalse(evaluation.asserted_component_values["extend_actuator_cmd"])
        self.assertFalse(evaluation.completion_reached)
        self.assertIn(
            f"hydraulic_pressure_psi below {LANDING_GEAR_PRESSURE_THRESHOLD_PSI:.1f}",
            evaluation.blocked_reasons,
        )

    def test_landing_gear_adapter_blocks_when_uplock_is_not_released(self):
        evaluation = build_landing_gear_controller_adapter().evaluate_snapshot(
            {
                "gear_handle_position": "DOWN",
                "hydraulic_pressure_psi": 2850.0,
                "uplock_released": False,
                "gear_position_percent": 0.0,
                "downlock_engaged": False,
            }
        )

        self.assertEqual(("lg_l1_handle_and_pressure",), evaluation.active_logic_node_ids)
        self.assertTrue(evaluation.asserted_component_values["selector_valve_cmd"])
        self.assertFalse(evaluation.asserted_component_values["extend_actuator_cmd"])
        self.assertFalse(evaluation.completion_reached)
        self.assertIn("uplock_released is still false", evaluation.blocked_reasons)


if __name__ == "__main__":
    unittest.main()
