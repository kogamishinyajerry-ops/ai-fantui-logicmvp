import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.second_system_smoke import (
    SECOND_SYSTEM_SMOKE_KIND,
    SECOND_SYSTEM_SMOKE_SCHEMA_ID,
    SECOND_SYSTEM_SMOKE_VERSION,
    build_second_system_smoke_report,
)


PROJECT_ROOT = Path(__file__).parents[1]
SECOND_SYSTEM_SMOKE_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "second_system_smoke_v1.schema.json"


def load_second_system_smoke_schema() -> dict:
    return json.loads(SECOND_SYSTEM_SMOKE_SCHEMA_PATH.read_text(encoding="utf-8"))


class SecondSystemSmokeTests(unittest.TestCase):
    def test_second_system_smoke_report_defaults_to_adapter_backed_runtime_chain(self):
        report = build_second_system_smoke_report()

        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, report.kind)
        self.assertEqual("truth_adapter", report.proof_mode)
        self.assertEqual("landing-gear-controller-adapter", report.adapter_id)
        self.assertEqual("minimal_landing_gear_extension", report.system_id)
        self.assertIsNone(report.packet_path)
        self.assertEqual("handle_down_nominal_extension", report.selected_scenario_id)
        self.assertEqual("hydraulic_pressure_bias_low", report.selected_fault_mode_id)
        self.assertEqual("adapter_runtime_proof", report.bundle_kind)
        self.assertTrue(report.ready_for_spec_build)
        self.assertTrue(report.playback_completion_reached)
        self.assertFalse(report.fault_completion_reached)
        self.assertEqual("resolved", report.knowledge_status)
        self.assertTrue(report.smoke_passed)
        self.assertIn("runtime_truth_alignment", report.evidence_steps)
        self.assertIn("knowledge_artifact", report.evidence_steps)

    def test_second_system_smoke_report_can_still_run_legacy_intake_packet_path(self):
        report = build_second_system_smoke_report(proof_mode="intake-packet")

        self.assertEqual("intake_packet", report.proof_mode)
        self.assertIsNone(report.adapter_id)
        self.assertEqual("custom_reverse_control_v1", report.system_id)
        self.assertEqual("ab_pressure_ramp", report.selected_scenario_id)
        self.assertEqual("pressure_sensor_bias_low", report.selected_fault_mode_id)
        self.assertEqual("full_workbench_bundle", report.bundle_kind)
        self.assertTrue(report.smoke_passed)
        self.assertIn("clarification_brief", report.evidence_steps)

    def test_second_system_smoke_report_serializes_default_payload_to_schema_aware_json(self):
        payload = build_second_system_smoke_report().to_dict()

        self.assertEqual(SECOND_SYSTEM_SMOKE_SCHEMA_ID, payload["$schema"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, payload["kind"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_VERSION, payload["version"])
        self.assertEqual("truth_adapter", payload["proof_mode"])
        self.assertEqual("landing-gear-controller-adapter", payload["adapter_id"])
        self.assertEqual("minimal_landing_gear_extension", payload["system_id"])
        self.assertIsNone(payload["packet_path"])
        self.assertEqual("adapter_runtime_proof", payload["bundle_kind"])
        self.assertTrue(payload["smoke_passed"])
        self.assertIn("knowledge_artifact", payload["evidence_steps"])

    def test_second_system_smoke_schema_documents_generated_payload_shape(self):
        schema = load_second_system_smoke_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_SCHEMA_ID, schema["$id"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_SCHEMA_ID, schema["properties"]["$schema"]["const"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_VERSION, schema["properties"]["version"]["const"])

    def test_optional_jsonschema_validates_generated_second_system_smoke_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_second_system_smoke_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = build_second_system_smoke_report().to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_cli_second_system_smoke_outputs_machine_readable_json(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["second-system-smoke", "--format", "json"])
        payload = json.loads(buffer.getvalue())

        self.assertEqual(0, exit_code)
        self.assertEqual(SECOND_SYSTEM_SMOKE_SCHEMA_ID, payload["$schema"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_KIND, payload["kind"])
        self.assertEqual(SECOND_SYSTEM_SMOKE_VERSION, payload["version"])
        self.assertEqual("truth_adapter", payload["proof_mode"])
        self.assertEqual("landing-gear-controller-adapter", payload["adapter_id"])
        self.assertEqual("minimal_landing_gear_extension", payload["system_id"])
        self.assertTrue(payload["smoke_passed"])
        self.assertEqual("resolved", payload["knowledge_status"])


if __name__ == "__main__":
    unittest.main()
