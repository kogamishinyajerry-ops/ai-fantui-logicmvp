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
    changerequest_handoff_hash,
    load_changerequest_handoff_schema,
    validate_changerequest_handoff_packet,
)


PROJECT_ROOT = Path(__file__).parents[1]
VALIDATOR_SCRIPT = PROJECT_ROOT / "tools" / "validate_workbench_changerequest_handoff_schema.py"


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
