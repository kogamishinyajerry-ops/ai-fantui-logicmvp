import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
from well_harness.document_intake import load_intake_packet
from well_harness.fault_diagnosis import FAULT_DIAGNOSIS_KIND
from well_harness.knowledge_capture import (
    KNOWLEDGE_ARTIFACT_KIND,
    KNOWLEDGE_ARTIFACT_SCHEMA_ID,
    KNOWLEDGE_ARTIFACT_VERSION,
    build_knowledge_artifact_from_truth_adapter,
    build_knowledge_artifact,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"
PROJECT_ROOT = Path(__file__).parents[1]
KNOWLEDGE_ARTIFACT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "knowledge_artifact_v1.schema.json"


def load_knowledge_artifact_schema() -> dict:
    return json.loads(KNOWLEDGE_ARTIFACT_SCHEMA_PATH.read_text(encoding="utf-8"))


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
        self.assertEqual(KNOWLEDGE_ARTIFACT_SCHEMA_ID, payload["$schema"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, payload["kind"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_VERSION, payload["version"])
        self.assertEqual("resolved", payload["status"])
        self.assertEqual("pressure_sensor_bias_low", payload["fault_mode_id"])
        self.assertEqual(["https://example.test/run/456"], payload["incident_record"]["evidence_links"])
        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["diagnosis_report"]["kind"])

    def test_knowledge_artifact_serializes_to_schema_aware_payload(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        payload = build_knowledge_artifact(
            packet,
            scenario_id="ab_pressure_ramp",
            fault_mode_id="pressure_sensor_bias_low",
            evidence_links=("https://example.test/run/123",),
            confirmed_root_cause="Pressure sensor reported a persistent low bias during the ramp.",
            repair_action="Recalibrated the pressure sensor and re-ran the ramp validation.",
            validation_after_fix="The actuator extended again under the same ramp scenario.",
            residual_risk="Low residual risk; keep monitoring for bias drift.",
            sample_period_s=1.0,
        ).to_dict()
        encoded = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(KNOWLEDGE_ARTIFACT_SCHEMA_ID, payload["$schema"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, payload["kind"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_VERSION, payload["version"])
        self.assertEqual("resolved", payload["status"])
        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["diagnosis_report"]["kind"])
        self.assertEqual(["https://example.test/run/123"], payload["incident_record"]["evidence_links"])
        self.assertIn("pressure_sensor_bias_low", encoded)
        self.assertIn("logic_enable_pressure", encoded)

    def test_adapter_backed_knowledge_artifact_preserves_landing_gear_diagnosis_chain(self):
        artifact = build_knowledge_artifact_from_truth_adapter(
            build_landing_gear_controller_adapter(),
            scenario_id="handle_down_nominal_extension",
            fault_mode_id="hydraulic_pressure_bias_low",
            evidence_links=("https://example.test/landing-gear/knowledge",),
            confirmed_root_cause="Hydraulic pressure sensing drift masked the extension-ready threshold.",
            repair_action="Recalibrated the hydraulic pressure sensing path and reran the extension proof.",
            validation_after_fix="Landing-gear extension completed again after recalibration.",
            residual_risk="Residual risk remains limited to future pressure-sensor drift checks.",
            sample_period_s=0.5,
        )

        self.assertEqual("resolved", artifact.status)
        self.assertEqual("minimal_landing_gear_extension", artifact.system_id)
        self.assertEqual(["https://example.test/landing-gear/knowledge"], artifact.incident_record["evidence_links"])
        self.assertIn("lg_l1_handle_and_pressure", artifact.diagnosis_report.blocked_logic_node_ids)

    def test_knowledge_artifact_schema_documents_generated_payload_shape(self):
        schema = load_knowledge_artifact_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_SCHEMA_ID, schema["$id"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_SCHEMA_ID, schema["properties"]["$schema"]["const"])
        self.assertEqual("well-harness-fault-diagnosis", schema["$defs"]["faultDiagnosis"]["properties"]["kind"]["const"])

    def test_optional_jsonschema_validates_generated_knowledge_artifact_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_knowledge_artifact_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)
        payload = build_knowledge_artifact(
            packet,
            scenario_id="ab_pressure_ramp",
            fault_mode_id="pressure_sensor_bias_low",
            evidence_links=("https://example.test/run/123",),
            confirmed_root_cause="Pressure sensor reported a persistent low bias during the ramp.",
            repair_action="Recalibrated the pressure sensor and re-ran the ramp validation.",
            validation_after_fix="The actuator extended again under the same ramp scenario.",
            residual_risk="Low residual risk; keep monitoring for bias drift.",
            sample_period_s=1.0,
        ).to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_optional_jsonschema_validates_adapter_backed_knowledge_artifact_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_knowledge_artifact_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = build_knowledge_artifact_from_truth_adapter(
            build_landing_gear_controller_adapter(),
            scenario_id="handle_down_nominal_extension",
            fault_mode_id="hydraulic_pressure_bias_low",
            evidence_links=("https://example.test/landing-gear/knowledge",),
            confirmed_root_cause="Hydraulic pressure sensing drift masked the extension-ready threshold.",
            repair_action="Recalibrated the hydraulic pressure sensing path and reran the extension proof.",
            validation_after_fix="Landing-gear extension completed again after recalibration.",
            residual_risk="Residual risk remains limited to future pressure-sensor drift checks.",
            sample_period_s=0.5,
        ).to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))


if __name__ == "__main__":
    unittest.main()
