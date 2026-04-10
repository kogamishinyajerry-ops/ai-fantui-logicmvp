import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.document_intake import load_intake_packet
from well_harness.scenario_playback import build_playback_report_from_intake_packet


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"
REPO_ROOT = FIXTURES_DIR.parent.parent


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
        self.assertEqual("ab_pressure_ramp", payload["scenario_id"])
        self.assertTrue(payload["completion_reached"])
        self.assertEqual("actuator_extend", payload["signal_series"][2]["id"])

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
