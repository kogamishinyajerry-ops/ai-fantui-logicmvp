import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.document_intake import load_intake_packet
from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"


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
        self.assertEqual("pressure_sensor_bias_low", payload["fault_mode_id"])
        self.assertFalse(payload["fault_completion_reached"])
        self.assertIn("logic_enable_pressure", payload["blocked_logic_node_ids"])


if __name__ == "__main__":
    unittest.main()
