import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
from well_harness.document_intake import load_intake_packet
from well_harness.fault_diagnosis import (
    FAULT_DIAGNOSIS_KIND,
    FAULT_DIAGNOSIS_SCHEMA_ID,
    FAULT_DIAGNOSIS_VERSION,
    build_fault_diagnosis_report_from_truth_adapter,
    build_fault_diagnosis_report_from_intake_packet,
)
from well_harness.scenario_playback import PLAYBACK_TRACE_KIND


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"
PROJECT_ROOT = Path(__file__).parents[1]
FAULT_DIAGNOSIS_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "fault_diagnosis_v1.schema.json"


def load_fault_diagnosis_schema() -> dict:
    return json.loads(FAULT_DIAGNOSIS_SCHEMA_PATH.read_text(encoding="utf-8"))


class FaultDiagnosisTests(unittest.TestCase):
    def test_fault_diagnosis_reports_blocked_logic_chain(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        report = build_fault_diagnosis_report_from_intake_packet(
            packet,
            scenario_id="ab_pressure_ramp",
            fault_mode_id="pressure_sensor_bias_low",
            sample_period_s=1.0,
        )

        self.assertEqual("pressure_sensor_bias_low", report.fault_mode_id)
        self.assertTrue(report.baseline_completion_reached)
        self.assertFalse(report.fault_completion_reached)
        self.assertIn("hyd_pressure", report.affected_signal_ids)
        self.assertIn("actuator_extend", report.affected_signal_ids)
        self.assertIn("logic_enable_pressure", report.blocked_logic_node_ids)
        self.assertIn("hyd_pressure", report.suspected_root_cause)
        self.assertGreaterEqual(len(report.scope_observations), 4)
        self.assertEqual("logic_enable_pressure", report.scope_observations[2].id)
        hyd_pressure_scope = next(item for item in report.scope_observations if item.id == "hyd_pressure")
        self.assertEqual(3200.0, hyd_pressure_scope.baseline_end)
        self.assertEqual(1950.0, hyd_pressure_scope.fault_end)

    def test_cli_fault_diagnosis_outputs_machine_readable_json(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "diagnose-fault",
                    str(SYSTEM_INTAKE_PACKET_PATH),
                    "--scenario",
                    "ab_pressure_ramp",
                    "--fault-mode",
                    "pressure_sensor_bias_low",
                    "--sample-period",
                    "1.0",
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(buffer.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual(FAULT_DIAGNOSIS_SCHEMA_ID, payload["$schema"])
        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["kind"])
        self.assertEqual(FAULT_DIAGNOSIS_VERSION, payload["version"])
        self.assertEqual("pressure_sensor_bias_low", payload["fault_mode_id"])
        self.assertFalse(payload["fault_completion_reached"])
        self.assertIn("logic_enable_pressure", payload["blocked_logic_node_ids"])
        self.assertEqual(PLAYBACK_TRACE_KIND, payload["baseline_report"]["kind"])
        self.assertEqual(PLAYBACK_TRACE_KIND, payload["fault_report"]["kind"])

    def test_fault_diagnosis_report_serializes_to_schema_aware_payload(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        payload = build_fault_diagnosis_report_from_intake_packet(
            packet,
            scenario_id="ab_pressure_ramp",
            fault_mode_id="pressure_sensor_bias_low",
            sample_period_s=1.0,
        ).to_dict()
        encoded = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(FAULT_DIAGNOSIS_SCHEMA_ID, payload["$schema"])
        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["kind"])
        self.assertEqual(FAULT_DIAGNOSIS_VERSION, payload["version"])
        self.assertEqual("ab_pressure_ramp", payload["baseline_report"]["scenario_id"])
        self.assertEqual("ab_pressure_ramp", payload["fault_report"]["scenario_id"])
        self.assertIsInstance(payload["scope_observations"], list)
        self.assertIn("pressure_sensor_bias_low", encoded)
        self.assertIn("logic_enable_pressure", encoded)

    def test_adapter_backed_fault_diagnosis_reports_landing_gear_divergence(self):
        report = build_fault_diagnosis_report_from_truth_adapter(
            build_landing_gear_controller_adapter(),
            scenario_id="handle_down_nominal_extension",
            fault_mode_id="hydraulic_pressure_bias_low",
            sample_period_s=0.5,
        )

        self.assertEqual("minimal_landing_gear_extension", report.system_id)
        self.assertTrue(report.baseline_completion_reached)
        self.assertFalse(report.fault_completion_reached)
        self.assertIn("hydraulic_pressure_psi", report.affected_signal_ids)
        self.assertIn("lg_l1_handle_and_pressure", report.blocked_logic_node_ids)
        self.assertIn("hydraulic_pressure_psi", report.suspected_root_cause)

    def test_fault_diagnosis_schema_documents_generated_payload_shape(self):
        schema = load_fault_diagnosis_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(FAULT_DIAGNOSIS_SCHEMA_ID, schema["$id"])
        self.assertEqual(FAULT_DIAGNOSIS_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(FAULT_DIAGNOSIS_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(FAULT_DIAGNOSIS_SCHEMA_ID, schema["properties"]["$schema"]["const"])
        self.assertEqual("well-harness-playback-trace", schema["$defs"]["playbackTrace"]["properties"]["kind"]["const"])

    def test_optional_jsonschema_validates_generated_fault_diagnosis_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_fault_diagnosis_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)
        payload = build_fault_diagnosis_report_from_intake_packet(
            packet,
            scenario_id="ab_pressure_ramp",
            fault_mode_id="pressure_sensor_bias_low",
            sample_period_s=1.0,
        ).to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_optional_jsonschema_validates_adapter_backed_fault_diagnosis_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_fault_diagnosis_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = build_fault_diagnosis_report_from_truth_adapter(
            build_landing_gear_controller_adapter(),
            scenario_id="handle_down_nominal_extension",
            fault_mode_id="hydraulic_pressure_bias_low",
            sample_period_s=0.5,
        ).to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))


if __name__ == "__main__":
    unittest.main()
