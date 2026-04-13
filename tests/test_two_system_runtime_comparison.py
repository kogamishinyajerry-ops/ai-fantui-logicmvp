import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.two_system_runtime_comparison import (
    TWO_SYSTEM_RUNTIME_COMPARISON_KIND,
    TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID,
    TWO_SYSTEM_RUNTIME_COMPARISON_VERSION,
    build_two_system_runtime_comparison_report,
)


PROJECT_ROOT = Path(__file__).parents[1]
SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "two_system_runtime_comparison_v1.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


class TwoSystemRuntimeComparisonTests(unittest.TestCase):
    def test_build_two_system_runtime_comparison_report_proves_both_systems_share_runtime_chain(self):
        report = build_two_system_runtime_comparison_report()

        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_KIND, report.kind)
        self.assertEqual("reference_thrust_reverser_deploy", report.primary_system.system_id)
        self.assertEqual("minimal_landing_gear_extension", report.comparison_system.system_id)
        self.assertTrue(report.both_support_adapter_truth)
        self.assertTrue(report.both_reach_playback_completion)
        self.assertTrue(report.both_block_fault_path)
        self.assertTrue(report.both_emit_resolved_knowledge)
        self.assertIn("knowledge_artifact", report.shared_contracts)

    def test_runtime_comparison_report_serializes_to_schema_aware_payload(self):
        payload = build_two_system_runtime_comparison_report().to_dict()

        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID, payload["$schema"])
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_KIND, payload["kind"])
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_VERSION, payload["version"])
        self.assertEqual("reference_thrust_reverser_deploy", payload["primary_system"]["system_id"])
        self.assertEqual("minimal_landing_gear_extension", payload["comparison_system"]["system_id"])
        self.assertTrue(payload["both_reach_playback_completion"])

    def test_runtime_comparison_schema_documents_generated_payload_shape(self):
        schema = load_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID, schema["$id"])
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID, schema["properties"]["$schema"]["const"])
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_VERSION, schema["properties"]["version"]["const"])

    def test_optional_jsonschema_validates_runtime_comparison_payload_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = build_two_system_runtime_comparison_report().to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_cli_two_system_runtime_comparison_outputs_machine_readable_json(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["two-system-runtime-comparison", "--format", "json"])
        payload = json.loads(buffer.getvalue())

        self.assertEqual(0, exit_code)
        self.assertEqual(TWO_SYSTEM_RUNTIME_COMPARISON_SCHEMA_ID, payload["$schema"])
        self.assertEqual("reference_thrust_reverser_deploy", payload["primary_system"]["system_id"])
        self.assertEqual("minimal_landing_gear_extension", payload["comparison_system"]["system_id"])
        self.assertTrue(payload["both_emit_resolved_knowledge"])


if __name__ == "__main__":
    unittest.main()
