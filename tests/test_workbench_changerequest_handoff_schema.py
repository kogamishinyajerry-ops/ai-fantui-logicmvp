import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from tools.validate_workbench_changerequest_handoff_schema import (
    FORCE_JSONSCHEMA_MISSING_ENV,
    OPTIONAL_JSONSCHEMA_SKIP_MESSAGE,
    sample_changerequest_handoff_packet,
)
from well_harness.workbench_changerequest_handoff import (  # type: ignore[import-untyped]
    CHANGE_REQUEST_HANDOFF_CANONICALIZATION,
    CHANGE_REQUEST_HANDOFF_KIND,
    CHANGE_REQUEST_HANDOFF_SCHEMA_ID,
    CHANGE_REQUEST_HANDOFF_SCHEMA_PATH,
    CHANGE_REQUEST_HANDOFF_VERSION,
    FOUNDATION_REVIEW_ARCHIVE_KIND,
    FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS,
    FOUNDATION_REVIEW_ARCHIVE_VERSION,
    changerequest_handoff_ui_checksum,
    changerequest_handoff_hash,
    load_changerequest_handoff_schema,
    validate_changerequest_handoff_archive_payload,
    validate_changerequest_handoff_packet,
    validate_foundation_review_archive_bundle,
    validate_foundation_review_archive_payload,
)


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATOR_SCRIPT = PROJECT_ROOT / "tools" / "validate_workbench_changerequest_handoff_schema.py"


def sample_foundation_review_archive() -> dict:
    sections = {
        section_name: {
            "key": section_name,
            "status": "present",
            "kind": "untyped",
            "version": "unversioned",
            "checksum_key": f"{section_name}_checksum",
            "checksum": "ui_draft_11111111",
            "truth_effect": "none",
        }
        for section_name in FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS
    }
    return {
        "kind": FOUNDATION_REVIEW_ARCHIVE_KIND,
        "version": FOUNDATION_REVIEW_ARCHIVE_VERSION,
        "review_scope": "workbench_v4_single_user_foundation",
        "archive_kind": "well-harness-workbench-evidence-archive",
        "archive_version": 1,
        "candidate_state": "sandbox_candidate",
        "certification_claim": "none",
        "truth_level_impact": "none",
        "dal_pssa_impact": "none",
        "controller_truth_modified": False,
        "frozen_assets_modified": False,
        "live_linear_mutation": False,
        "runtime_truth_effect": "none",
        "truth_effect": "none",
        "required_sections": list(FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS),
        "missing_sections": [],
        "section_count": len(FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS),
        "sections": sections,
        "review_readiness": "ready",
        "preflight_summary": {
            "classification": "ready",
            "finding_count": 0,
            "candidate_model_hash": "ui_draft_11111111",
            "truth_effect": "none",
        },
        "review_packet": {
            "graph_checksum": "ui_draft_11111111",
            "test_bench_checksum": "ui_draft_11111111",
            "run_report_checksum": "ui_draft_11111111",
            "debugger_checksum": "ui_draft_11111111",
            "preflight_checksum": "ui_draft_11111111",
            "hardware_evidence_checksum": "ui_draft_11111111",
            "changerequest_handoff_checksum": "ui_draft_11111111",
            "linear_issue_body_checksum": "ui_draft_11111111",
            "pr_proof_packet_checksum": "ui_draft_11111111",
            "truth_effect": "none",
        },
        "linear_ready": {
            "issue_body_available": True,
            "pr_proof_available": True,
            "handoff_packet_available": True,
            "live_linear_mutation": False,
            "browser_mutates_linear": False,
            "truth_effect": "none",
        },
        "restore_contract": {
            "validation_report_key": "foundation_review_archive_validation",
            "restore_payload_key": "foundation_review_archive_validation",
            "requires_handoff_packet_validation": True,
            "browser_archive_only": True,
            "truth_effect": "none",
        },
        "checksum_manifest": {},
    }


class WorkbenchChangeRequestHandoffSchemaTests(unittest.TestCase):
    def test_schema_document_matches_handoff_constants(self) -> None:
        schema = load_changerequest_handoff_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(CHANGE_REQUEST_HANDOFF_SCHEMA_ID, schema["$id"])
        self.assertEqual(CHANGE_REQUEST_HANDOFF_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(CHANGE_REQUEST_HANDOFF_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(
            CHANGE_REQUEST_HANDOFF_CANONICALIZATION,
            schema["$defs"]["serialization"]["properties"]["canonicalization"]["const"],
        )
        self.assertTrue(CHANGE_REQUEST_HANDOFF_SCHEMA_PATH.exists())

    def test_valid_packet_passes_structural_and_json_schema_validation(self) -> None:
        try:
            from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        payload = sample_changerequest_handoff_packet()
        schema = load_changerequest_handoff_schema()
        Draft202012Validator.check_schema(schema)
        errors = sorted(
            Draft202012Validator(schema).iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual((), validate_changerequest_handoff_packet(payload))
        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_packet_rejects_live_mutation_and_certified_truth_claims(self) -> None:
        payload = sample_changerequest_handoff_packet()
        payload["live_linear_mutation"] = True
        payload["certification_claim"] = "certified"
        payload["truth_level_impact"] = "certified"
        payload["red_line_metadata"]["live_linear_mutation"] = True
        payload["changerequest_proof_packet"]["certification_claim"] = "certified"

        issues = validate_changerequest_handoff_packet(payload)

        self.assertIn("live_linear_mutation must be False.", " ".join(issues))
        self.assertIn("certification_claim must be 'none'.", " ".join(issues))
        self.assertIn("truth_level_impact must be 'none'.", " ".join(issues))

    def test_structural_validator_rejects_schema_only_contract_drift(self) -> None:
        payload = sample_changerequest_handoff_packet()
        payload["unexpected"] = "not allowed"
        payload["serialization"]["checksum_algorithm"] = "raw_json_hash"
        payload["metadata"]["unexpected"] = "not allowed"
        del payload["metadata"]["diff_review_v2"]

        issues = validate_changerequest_handoff_packet(payload)
        issue_text = " ".join(issues)

        self.assertIn("unexpected is not part of ChangeRequest handoff packet version 1.", issue_text)
        self.assertIn("serialization.checksum_algorithm must be", issue_text)
        self.assertIn("metadata.unexpected is not part of ChangeRequest handoff packet version 1.", issue_text)
        self.assertIn("metadata.diff_review_v2 must be a JSON object.", issue_text)

    def test_canonical_hash_is_stable_across_key_ordering(self) -> None:
        payload = sample_changerequest_handoff_packet()
        scrambled = copy.deepcopy(payload)
        scrambled["metadata"] = {
            "test_delta": scrambled["metadata"]["test_delta"],
            "agent_eligible": scrambled["metadata"]["agent_eligible"],
            **{
                key: value
                for key, value in scrambled["metadata"].items()
                if key not in {"test_delta", "agent_eligible"}
            },
        }
        scrambled = {
            "pr_proof_packet": scrambled["pr_proof_packet"],
            "linear_issue_body": scrambled["linear_issue_body"],
            **{
                key: value
                for key, value in scrambled.items()
                if key not in {"pr_proof_packet", "linear_issue_body"}
            },
        }

        self.assertEqual(changerequest_handoff_hash(payload), changerequest_handoff_hash(scrambled))

    def test_archive_payload_validates_handoff_packet_and_ui_checksum(self) -> None:
        payload = sample_changerequest_handoff_packet()
        archive = {
            "kind": "well-harness-workbench-evidence-archive",
            "version": 1,
            "changerequest_handoff_packet": payload,
            "checksums": {
                "changerequest_handoff_packet_checksum": changerequest_handoff_ui_checksum(payload),
            },
        }

        report = validate_changerequest_handoff_archive_payload(archive)

        self.assertEqual("pass", report["status"])
        self.assertEqual("pass", report["checksum_status"])
        self.assertEqual("changerequest_handoff_packet", report["source_path"])
        self.assertEqual(changerequest_handoff_hash(payload), report["canonical_hash"])
        self.assertEqual(changerequest_handoff_ui_checksum(payload), report["ui_checksum"])
        self.assertEqual([], report["issues"])
        self.assertEqual("none", report["truth_effect"])

    def test_archive_payload_without_handoff_packet_is_backward_compatible(self) -> None:
        report = validate_changerequest_handoff_archive_payload(
            {
                "kind": "well-harness-workbench-evidence-archive",
                "version": 1,
                "model_json": {"kind": "well-harness-workbench-ui-draft"},
            }
        )

        self.assertEqual("not_present", report["status"])
        self.assertEqual(0, report["issue_count"])
        self.assertIsNone(report["canonical_hash"])

    def test_archive_payload_rejects_invalid_handoff_packet(self) -> None:
        payload = sample_changerequest_handoff_packet()
        payload["live_linear_mutation"] = True
        archive = {
            "kind": "well-harness-workbench-evidence-archive",
            "version": 1,
            "changerequest_handoff_packet": payload,
            "checksums": {
                "changerequest_handoff_packet_checksum": changerequest_handoff_ui_checksum(payload),
            },
        }

        report = validate_changerequest_handoff_archive_payload(archive)

        self.assertEqual("fail", report["status"])
        self.assertIn("live_linear_mutation must be False.", " ".join(report["issues"]))

    def test_archive_payload_rejects_handoff_checksum_mismatch(self) -> None:
        payload = sample_changerequest_handoff_packet()
        archive = {
            "kind": "well-harness-workbench-evidence-archive",
            "version": 1,
            "model_json": {
                "kind": "well-harness-workbench-ui-draft",
                "changerequest_handoff_packet": payload,
            },
            "checksums": {
                "changerequest_handoff_packet_checksum": "ui_draft_00000000",
            },
        }

        report = validate_changerequest_handoff_archive_payload(archive)

        self.assertEqual("fail", report["status"])
        self.assertEqual("mismatch", report["checksum_status"])
        self.assertIn("checksum mismatch", " ".join(report["issues"]))

    def test_foundation_review_archive_bundle_validates_review_ready_sections(self) -> None:
        payload = sample_foundation_review_archive()

        self.assertIn("scenario_test_case_library", FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS)
        self.assertIn("scenario_test_case_library", payload["sections"])
        self.assertIn("sandbox_runner_trace_kernel", FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS)
        self.assertIn("sandbox_runner_trace_kernel", payload["sections"])
        self.assertIn("debug_probe_timeline", FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS)
        self.assertIn("debug_probe_timeline", payload["sections"])
        self.assertIn("hardware_evidence_attachment_v2", FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS)
        self.assertIn("hardware_evidence_attachment_v2", payload["sections"])
        self.assertEqual((), validate_foundation_review_archive_bundle(payload))

    def test_foundation_review_archive_payload_validates_checksum(self) -> None:
        payload = sample_foundation_review_archive()
        archive = {
            "kind": "well-harness-workbench-evidence-archive",
            "version": 1,
            "foundation_review_archive": payload,
            "checksums": {
                "foundation_review_archive_checksum": changerequest_handoff_ui_checksum(payload),
            },
        }

        report = validate_foundation_review_archive_payload(archive)

        self.assertEqual("pass", report["status"])
        self.assertEqual("pass", report["checksum_status"])
        self.assertEqual("foundation_review_archive", report["source_path"])
        self.assertEqual(changerequest_handoff_hash(payload), report["canonical_hash"])
        self.assertEqual(changerequest_handoff_ui_checksum(payload), report["ui_checksum"])
        self.assertEqual("none", report["truth_effect"])

    def test_foundation_review_archive_payload_rejects_truth_and_linear_mutation_claims(self) -> None:
        payload = sample_foundation_review_archive()
        payload["truth_effect"] = "certified"
        payload["certification_claim"] = "certified"
        payload["live_linear_mutation"] = True
        archive = {
            "kind": "well-harness-workbench-evidence-archive",
            "version": 1,
            "foundation_review_archive": payload,
            "checksums": {
                "foundation_review_archive_checksum": changerequest_handoff_ui_checksum(payload),
            },
        }

        report = validate_foundation_review_archive_payload(archive)
        issue_text = " ".join(report["issues"])

        self.assertEqual("fail", report["status"])
        self.assertIn("foundation_review_archive.truth_effect must be 'none'.", issue_text)
        self.assertIn("foundation_review_archive.certification_claim must be 'none'.", issue_text)
        self.assertIn("foundation_review_archive.live_linear_mutation must be False.", issue_text)

    def test_foundation_review_archive_payload_rejects_missing_checksum(self) -> None:
        payload = sample_foundation_review_archive()

        report = validate_foundation_review_archive_payload(
            {
                "kind": "well-harness-workbench-evidence-archive",
                "version": 1,
                "foundation_review_archive": payload,
                "checksums": {},
            }
        )

        self.assertEqual("fail", report["status"])
        self.assertEqual("missing", report["checksum_status"])
        self.assertIn("foundation_review_archive_checksum is required", " ".join(report["issues"]))

    def test_standalone_script_json_pass_output(self) -> None:
        env = dict(os.environ)
        src_path = str(PROJECT_ROOT / "src")
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(
            "docs/json_schema/workbench_changerequest_handoff_v1.schema.json",
            payload["schema_path"],
        )
        self.assertIn("valid_handoff_packet", {result["case"] for result in payload["results"]})

    def test_standalone_script_forced_jsonschema_missing_skip(self) -> None:
        env = dict(os.environ)
        env[FORCE_JSONSCHEMA_MISSING_ENV] = "1"
        src_path = str(PROJECT_ROOT / "src")
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT), "--format", "json"],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("skip", payload["status"])
        self.assertEqual(OPTIONAL_JSONSCHEMA_SKIP_MESSAGE, payload["reason"])


if __name__ == "__main__":
    unittest.main()
