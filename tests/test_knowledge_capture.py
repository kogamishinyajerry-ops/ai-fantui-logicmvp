import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.document_intake import load_intake_packet
from well_harness.knowledge_capture import build_knowledge_artifact


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"


class KnowledgeCaptureTests(unittest.TestCase):
    def test_build_knowledge_artifact_captures_resolution_and_optimization(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        artifact = build_knowledge_artifact(
            packet,
            scenario_id="ab_pressure_ramp",
            fault_mode_id="pressure_sensor_bias_low",
            evidence_links=("https://example.test/run/123",),
            confirmed_root_cause="Pressure sensor reported a persistent low bias during the ramp.",
            repair_action="Recalibrated the pressure sensor and re-ran the ramp validation.",
            validation_after_fix="The actuator extended again under the same ramp scenario.",
            residual_risk="Low residual risk; keep monitoring for bias drift.",
            sample_period_s=1.0,
        )

        self.assertEqual("resolved", artifact.status)
        self.assertEqual("custom_reverse_control_v1", artifact.system_id)
        self.assertEqual("pressure_sensor_bias_low", artifact.fault_mode_id)
        self.assertEqual(["https://example.test/run/123"], artifact.incident_record["evidence_links"])
        self.assertIn("pressure plausibility checks", artifact.optimization_record["suggested_logic_change"])
        self.assertIn("logic_enable_pressure", artifact.diagnosis_report.blocked_logic_node_ids)

    def test_cli_capture_knowledge_outputs_json_artifact(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(
                [
                    "capture-knowledge",
                    str(SYSTEM_INTAKE_PACKET_PATH),
                    "--scenario",
                    "ab_pressure_ramp",
                    "--fault-mode",
                    "pressure_sensor_bias_low",
                    "--confirmed-root-cause",
                    "Pressure sensor low bias.",
                    "--repair-action",
                    "Recalibrate and retest.",
                    "--validation-after-fix",
                    "Scenario replay and hardware check passed.",
                    "--residual-risk",
                    "Residual drift risk remains low.",
                    "--evidence-link",
                    "https://example.test/run/456",
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(buffer.getvalue())
        self.assertEqual(0, exit_code)
        self.assertEqual("resolved", payload["status"])
        self.assertEqual("pressure_sensor_bias_low", payload["fault_mode_id"])
        self.assertEqual(["https://example.test/run/456"], payload["incident_record"]["evidence_links"])


if __name__ == "__main__":
    unittest.main()
