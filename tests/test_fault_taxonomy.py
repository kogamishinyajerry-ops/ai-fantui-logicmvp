import json
import unittest
from pathlib import Path

from well_harness.fault_taxonomy import (
    FAULT_TAXONOMY_KIND,
    FAULT_TAXONOMY_SCHEMA_ID,
    FAULT_TAXONOMY_VERSION,
    SUPPORTED_FAULT_KINDS,
    fault_taxonomy_to_dict,
    validate_fault_kind,
)


PROJECT_ROOT = Path(__file__).parents[1]
FAULT_TAXONOMY_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "fault_taxonomy_v1.schema.json"


def load_fault_taxonomy_schema() -> dict:
    return json.loads(FAULT_TAXONOMY_SCHEMA_PATH.read_text(encoding="utf-8"))


class FaultTaxonomyTests(unittest.TestCase):
    def test_fault_taxonomy_lists_supported_fault_kinds(self):
        self.assertIn("bias_low", SUPPORTED_FAULT_KINDS)
        self.assertIn("command_path_failure", SUPPORTED_FAULT_KINDS)
        self.assertEqual("stuck_low", validate_fault_kind("stuck_low"))

    def test_fault_taxonomy_schema_documents_generated_payload_shape(self):
        schema = load_fault_taxonomy_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(FAULT_TAXONOMY_SCHEMA_ID, schema["$id"])
        self.assertEqual(FAULT_TAXONOMY_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(FAULT_TAXONOMY_VERSION, schema["properties"]["version"]["const"])

    def test_optional_jsonschema_validates_generated_fault_taxonomy_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_fault_taxonomy_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        payload = fault_taxonomy_to_dict()
        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_unknown_fault_kind_raises_helpful_error(self):
        with self.assertRaisesRegex(ValueError, "fault_kind must be one of"):
            validate_fault_kind("mystery_fault")


if __name__ == "__main__":
    unittest.main()
