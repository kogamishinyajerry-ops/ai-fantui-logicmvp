from dataclasses import asdict
import json
import unittest
from pathlib import Path

from well_harness.controller import DeployController
from well_harness.controller_adapter import (
    CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
    CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
    CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION,
    REFERENCE_DEPLOY_CONTROLLER_METADATA,
    build_reference_controller_adapter,
)
from well_harness.models import HarnessConfig, ResolvedInputs


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
        deploy_90_percent_vdt=True,
    )
    base.update(overrides)
    return ResolvedInputs(**base)


PROJECT_ROOT = Path(__file__).parents[1]
CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "controller_truth_adapter_metadata_v1.schema.json"
)


def load_controller_truth_adapter_metadata_schema() -> dict:
    return json.loads(CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_PATH.read_text(encoding="utf-8"))


class ControllerAdapterTests(unittest.TestCase):
    def test_reference_adapter_exposes_reference_truth_metadata(self):
        adapter = build_reference_controller_adapter()

        self.assertEqual(adapter.metadata, REFERENCE_DEPLOY_CONTROLLER_METADATA)
        self.assertEqual(adapter.metadata.adapter_id, "reference-deploy-controller")
        self.assertEqual(adapter.metadata.truth_kind, "python-controller-adapter")
        self.assertEqual(adapter.metadata.source_of_truth, "src/well_harness/controller.py")

    def test_reference_adapter_metadata_serializes_to_schema_aware_payload(self):
        adapter = build_reference_controller_adapter()

        payload = adapter.metadata.to_dict()

        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID, payload["$schema"])
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_KIND, payload["kind"])
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION, payload["version"])
        self.assertEqual("reference-deploy-controller", payload["adapter_id"])
        self.assertEqual("reference_thrust_reverser_deploy", payload["system_id"])
        self.assertEqual("src/well_harness/controller.py", payload["source_of_truth"])

    def test_controller_truth_adapter_metadata_schema_documents_generated_payload_shape(self):
        schema = load_controller_truth_adapter_metadata_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID, schema["$id"])
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID, schema["properties"]["$schema"]["const"])

    def test_optional_jsonschema_validates_reference_adapter_metadata_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_controller_truth_adapter_metadata_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = build_reference_controller_adapter().metadata.to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_reference_adapter_matches_deploy_controller_outputs_and_explain(self):
        config = HarnessConfig()
        inputs = make_inputs()
        adapter = build_reference_controller_adapter(config)
        controller = DeployController(config)

        adapter_outputs, adapter_explain = adapter.evaluate_with_explain(inputs)
        controller_outputs, controller_explain = controller.evaluate_with_explain(inputs)

        self.assertEqual(adapter_outputs, controller_outputs)
        self.assertEqual(adapter_explain, controller_explain)

    def test_reference_adapter_load_spec_exposes_reference_workbench_spec(self):
        payload = build_reference_controller_adapter().load_spec()

        self.assertEqual("reference_thrust_reverser_deploy", payload["system_id"])
        self.assertEqual("src/well_harness/controller.py", payload["source_of_truth"])
        self.assertTrue(payload["logic_nodes"])
        self.assertTrue(payload["acceptance_scenarios"])

    def test_reference_adapter_evaluate_snapshot_emits_generic_truth_evaluation(self):
        payload = build_reference_controller_adapter().evaluate_snapshot(asdict(make_inputs()))

        self.assertEqual("reference_thrust_reverser_deploy", payload.system_id)
        self.assertEqual(("logic1", "logic2", "logic3", "logic4"), payload.active_logic_node_ids)
        self.assertTrue(payload.asserted_component_values["throttle_electronic_lock_release_cmd"])
        self.assertTrue(payload.completion_reached)
        self.assertEqual((), payload.blocked_reasons)


if __name__ == "__main__":
    unittest.main()
