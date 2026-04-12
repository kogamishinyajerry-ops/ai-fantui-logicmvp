import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from well_harness.cli import main
from well_harness.document_intake import (
    apply_safe_schema_repairs,
    assess_intake_packet,
    build_clarification_brief,
    intake_packet_from_dict,
    intake_template_payload,
    load_intake_packet,
)


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"


class MixedDocumentIntakeTests(unittest.TestCase):
    def test_load_intake_packet_supports_mixed_docs_and_custom_signal_semantics(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        self.assertEqual(packet.system_id, "custom_reverse_control_v1")
        self.assertEqual(len(packet.source_documents), 2)
        self.assertEqual({document.kind for document in packet.source_documents}, {"pdf", "markdown"})
        self.assertEqual(packet.components[1].unit, "psi")
        self.assertEqual(packet.components[1].state_shape, "analog")
        self.assertEqual(packet.components[0].allowed_states, ("0", "1"))

    def test_assess_intake_packet_reports_ready_when_answers_are_complete(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)
        report = assess_intake_packet(packet)

        self.assertTrue(report["includes_pdf_sources"])
        self.assertTrue(report["mixed_source_packet"])
        self.assertTrue(report["ready_for_spec_build"])
        self.assertEqual(report["blocking_reasons"], [])
        self.assertEqual(report["unanswered_clarifications"], [])
        self.assertIn("generated_workbench_spec", report)
        self.assertEqual(report["generated_workbench_spec"]["system_id"], "custom_reverse_control_v1")
        brief = build_clarification_brief(packet)
        self.assertEqual("ready", brief["gate_status"])
        self.assertEqual([], [item for item in brief["follow_up_items"] if item["status"] != "answered"])
        self.assertIn("scenario_playback", brief["unlocks_after_completion"])

    def test_assess_intake_packet_surfaces_missing_clarifications_as_blocking_follow_up(self):
        payload = intake_template_payload()
        payload["system_id"] = "incomplete_packet"
        payload["title"] = "Incomplete Packet"
        payload["objective"] = "Show unanswered clarification handling."
        payload["source_documents"][0]["location"] = "docs/source.pdf"
        payload["components"] = [
            {
                "id": "sensor_x",
                "label": "SENSOR_X",
                "kind": "sensor",
                "state_shape": "analog",
                "unit": "bar",
                "description": "System-defined sensor.",
                "allowed_range": [0.0, 5.0],
            }
        ]
        payload["logic_nodes"] = [
            {
                "id": "logic_x",
                "label": "L_X",
                "description": "Simple gate.",
                "conditions": [
                    {
                        "name": "sensor_x",
                        "source_component_id": "sensor_x",
                        "comparison": ">=",
                        "threshold_value": 2.0,
                        "note": "Threshold gate.",
                    }
                ],
                "downstream_component_ids": ["sensor_x"],
            }
        ]
        payload["acceptance_scenarios"] = [
            {
                "id": "scenario_x",
                "label": "Scenario X",
                "description": "Simple ramp.",
                "time_scale_factor": 1.0,
                "total_duration_s": 2.0,
                "monitored_signal_ids": ["sensor_x"],
                "transitions": [
                    {
                        "signal_id": "sensor_x",
                        "start_s": 0.0,
                        "end_s": 2.0,
                        "start_value": 0.0,
                        "end_value": 3.0,
                        "unit": "bar",
                        "note": "Ramp",
                    }
                ],
                "completion_condition": "sensor_x >= 2.0",
            }
        ]
        payload["fault_modes"] = [
            {
                "id": "fault_x",
                "target_component_id": "sensor_x",
                "fault_kind": "stuck_low",
                "symptom": "Signal never rises.",
                "reasoning_scope_component_ids": ["sensor_x"],
                "expected_diagnostic_sections": ["symptoms", "repair_hint"],
                "optimization_prompt": "Add redundancy if needed.",
            }
        ]
        payload["clarification_answers"] = [
            {
                "question_id": "source_documents",
                "answer": "Mixed docs/PDF",
            }
        ]
        packet = intake_packet_from_dict(payload)
        report = assess_intake_packet(packet)

        self.assertFalse(report["ready_for_spec_build"])
        self.assertIsNone(report["generated_workbench_spec"])
        self.assertGreaterEqual(len(report["unanswered_clarifications"]), 1)
        self.assertIn("component_state_domains", {item["id"] for item in report["unanswered_clarifications"]})
        brief = build_clarification_brief(packet)
        self.assertEqual("blocked_by_clarifications", brief["gate_status"])
        self.assertEqual(3, brief["open_question_count"])
        self.assertIn("spec build is blocked", brief["gating_statement"].lower())
        self.assertIn(
            "Answer clarification component_state_domains",
            " ".join(brief["next_actions"]),
        )

    def test_cli_can_render_intake_template_and_json_assessment(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["intake", "--template", "--format", "json"])
        template_payload = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(template_payload["source_documents"][0]["kind"], "pdf")
        self.assertEqual(template_payload["clarification_answers"][0]["question_id"], "source_documents")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["intake", str(SYSTEM_INTAKE_PACKET_PATH), "--format", "json"])
        report = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertTrue(report["ready_for_spec_build"])
        self.assertTrue(report["includes_pdf_sources"])
        self.assertEqual(report["custom_signal_semantics"][1]["unit"], "psi")

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["intake", str(SYSTEM_INTAKE_PACKET_PATH), "--follow-up", "--format", "json"])
        follow_up = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual("ready", follow_up["gate_status"])
        self.assertEqual(0, follow_up["open_question_count"])
        self.assertIn("knowledge_capture", follow_up["unlocks_after_completion"])

    def test_assess_intake_packet_includes_safe_schema_repair_suggestions_for_template_gaps(self):
        packet = intake_packet_from_dict(intake_template_payload())

        report = assess_intake_packet(packet)

        self.assertFalse(report["ready_for_spec_build"])
        suggestion_ids = {item["id"] for item in report["repair_suggestions"]}
        self.assertIn("add_logic_node_stub", suggestion_ids)
        self.assertIn("add_fault_mode_stub", suggestion_ids)
        self.assertTrue(
            any(item["autofix_available"] for item in report["repair_suggestions"])
        )

    def test_apply_safe_schema_repairs_converts_template_to_clarification_only_block(self):
        packet = intake_packet_from_dict(intake_template_payload())

        repaired_packet, applied_suggestion_ids = apply_safe_schema_repairs(packet)
        report = assess_intake_packet(repaired_packet)
        brief = build_clarification_brief(repaired_packet)

        self.assertIn("add_logic_node_stub", applied_suggestion_ids)
        self.assertIn("add_fault_mode_stub", applied_suggestion_ids)
        self.assertEqual([], report["blocking_reasons"])
        self.assertFalse(report["ready_for_spec_build"])
        self.assertEqual("blocked_by_clarifications", brief["gate_status"])
        self.assertEqual(2, brief["open_question_count"])

    def test_cli_can_export_reference_spec_json(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = main(["spec", "--format", "json"])
        payload = json.loads(buffer.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["system_id"], "reference_thrust_reverser_deploy")
        self.assertEqual(payload["source_of_truth"], "src/well_harness/controller.py")


if __name__ == "__main__":
    unittest.main()
