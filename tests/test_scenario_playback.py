import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
from well_harness.document_intake import load_intake_packet
from well_harness.scenario_playback import (
    PLAYBACK_TRACE_KIND,
    PLAYBACK_TRACE_SCHEMA_ID,
    PLAYBACK_TRACE_VERSION,
    build_playback_report_from_truth_adapter,
    build_playback_report_from_intake_packet,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"
REPO_ROOT = FIXTURES_DIR.parent.parent
PLAYBACK_TRACE_SCHEMA_PATH = REPO_ROOT / "docs" / "json_schema" / "playback_trace_v1.schema.json"


def load_playback_trace_schema() -> dict:
    return json.loads(PLAYBACK_TRACE_SCHEMA_PATH.read_text(encoding="utf-8"))


class ScenarioPlaybackTests(unittest.TestCase):
    def test_build_playback_report_compiles_signal_and_logic_series(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        report = build_playback_report_from_intake_packet(
            packet,
            scenario_id="ab_pressure_ramp",
            sample_period_s=1.0,
        )

        signal_series = {series.id: series for series in report.signal_series}
        logic_series = {series.id: series for series in report.logic_series}

        self.assertEqual("custom_reverse_control_v1", report.system_id)
        self.assertEqual("ab_pressure_ramp", report.scenario_id)
        self.assertTrue(report.completion_reached)
        self.assertEqual(13, len(signal_series["hyd_pressure"].points))
        self.assertEqual(0.0, signal_series["hyd_pressure"].points[0].value)
        self.assertEqual(1600.0, signal_series["hyd_pressure"].points[4].value)
        self.assertEqual(3200.0, signal_series["hyd_pressure"].points[8].value)
        self.assertEqual(1.0, signal_series["cmd_enable"].points[0].value)
        self.assertEqual(0.0, signal_series["actuator_extend"].points[6].value)
        self.assertEqual(1.0, signal_series["actuator_extend"].points[7].value)
        self.assertEqual(1.0, logic_series["logic_enable_pressure"].points[7].value)
        self.assertEqual((), report.assumptions)

    def test_cli_playback_outputs_machine_readable_json(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "playback",
                    str(SYSTEM_INTAKE_PACKET_PATH),
                    "--scenario",
                    "ab_pressure_ramp",
                    "--sample-period",
                    "1.0",
                    "--format",
                    "json",
                ]
            )
        payload = json.loads(buffer.getvalue())

        self.assertEqual(0, exit_code)
        self.assertEqual(PLAYBACK_TRACE_SCHEMA_ID, payload["$schema"])
        self.assertEqual(PLAYBACK_TRACE_KIND, payload["kind"])
        self.assertEqual(PLAYBACK_TRACE_VERSION, payload["version"])
        self.assertEqual("ab_pressure_ramp", payload["scenario_id"])
        self.assertTrue(payload["completion_reached"])
        self.assertEqual("actuator_extend", payload["signal_series"][2]["id"])

    def test_adapter_backed_playback_supports_discrete_landing_gear_states(self):
        report = build_playback_report_from_truth_adapter(
            build_landing_gear_controller_adapter(),
            scenario_id="handle_down_nominal_extension",
            sample_period_s=0.5,
        )

        signal_series = {series.id: series for series in report.signal_series}
        logic_series = {series.id: series for series in report.logic_series}

        self.assertEqual("minimal_landing_gear_extension", report.system_id)
        self.assertEqual("handle_down_nominal_extension", report.scenario_id)
        self.assertTrue(report.completion_reached)
        self.assertEqual(1.0, signal_series["selector_valve_cmd"].points[0].value)
        self.assertEqual(0.0, signal_series["uplock_released"].points[0].value)
        self.assertEqual(1.0, logic_series["lg_l1_handle_and_pressure"].points[0].value)
        self.assertEqual(0.0, logic_series["lg_l2_extend_after_uplock_release"].points[0].value)
        self.assertEqual(1.0, logic_series["lg_l2_extend_after_uplock_release"].points[2].value)

    def test_reference_adapter_backed_playback_accepts_percent_completion_conditions(self):
        from well_harness.controller_adapter import build_reference_controller_adapter

        report = build_playback_report_from_truth_adapter(
            build_reference_controller_adapter(),
            scenario_id="compressed_ra_tra_vdt_monitor",
            sample_period_s=0.5,
        )

        self.assertEqual("reference_thrust_reverser_deploy", report.system_id)
        self.assertTrue(report.completion_reached)

    def test_playback_report_serializes_to_schema_aware_payload(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        payload = build_playback_report_from_intake_packet(
            packet,
            scenario_id="ab_pressure_ramp",
            sample_period_s=1.0,
        ).to_dict()
        encoded = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(PLAYBACK_TRACE_SCHEMA_ID, payload["$schema"])
        self.assertEqual(PLAYBACK_TRACE_KIND, payload["kind"])
        self.assertEqual(PLAYBACK_TRACE_VERSION, payload["version"])
        self.assertIsInstance(payload["signal_series"], list)
        self.assertIsInstance(payload["signal_series"][0]["points"], list)
        self.assertIn("ab_pressure_ramp", encoded)
        self.assertIn("logic_enable_pressure", encoded)

    def test_playback_trace_schema_documents_generated_payload_shape(self):
        schema = load_playback_trace_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(PLAYBACK_TRACE_SCHEMA_ID, schema["$id"])
        self.assertEqual(PLAYBACK_TRACE_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(PLAYBACK_TRACE_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(PLAYBACK_TRACE_SCHEMA_ID, schema["properties"]["$schema"]["const"])

    def test_optional_jsonschema_validates_generated_playback_trace_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_playback_trace_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)
        payload = build_playback_report_from_intake_packet(
            packet,
            scenario_id="ab_pressure_ramp",
            sample_period_s=1.0,
        ).to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_optional_jsonschema_validates_adapter_backed_landing_gear_playback_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_playback_trace_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = build_playback_report_from_truth_adapter(
            build_landing_gear_controller_adapter(),
            scenario_id="handle_down_nominal_extension",
            sample_period_s=0.5,
        ).to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_module_entrypoint_emits_playback_text(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "well_harness.cli",
                "playback",
                str(SYSTEM_INTAKE_PACKET_PATH),
                "--scenario",
                "ab_pressure_ramp",
                "--sample-period",
                "1.0",
                "--format",
                "text",
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode)
        self.assertIn("scenario: ab_pressure_ramp", result.stdout)
        self.assertIn("signal snapshots:", result.stdout)


if __name__ == "__main__":
    unittest.main()
