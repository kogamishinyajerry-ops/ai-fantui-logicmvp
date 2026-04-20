"""P42-05 · Schema extension + serializer + generator template regression guards.

Covers the W1/W3 surfaces of P42 v2:

- JSON schema (docs/json_schema/controller_truth_adapter_metadata_v1.schema.json):
  new optional `truth_level` and `status` enum properties are present,
  additionalProperties remains false, enum values match docs registry.
- ControllerTruthMetadata serializer:
  * None governance fields are stripped from the payload (v1 shape preserved)
  * Explicit governance fields are serialized with correct values
  * Invalid enum values at runtime still get rejected by jsonschema
- generate_adapter.py template:
  * Emitted source no longer locally redefines ControllerTruthMetadata
    or GenericTruthEvaluation (Codex Counter B)
  * Emitted CONTROLLER_METADATA declares truth_level="demonstrative"
    and status="Upgrade pending" by default
"""
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

# Ensure src/ is on path for direct imports when pytest runs without editable install.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

from well_harness.controller_adapter import (  # noqa: E402
    CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
    CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
    CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION,
    ControllerTruthMetadata,
    controller_truth_metadata_to_dict,
)
from well_harness.tools.generate_adapter import spec_to_adapter_source  # noqa: E402


SCHEMA_PATH = _REPO_ROOT / "docs/json_schema/controller_truth_adapter_metadata_v1.schema.json"

VALID_TRUTH_LEVELS = ("demonstrative", "certified", "placeholder")
VALID_STATUSES = ("In use", "Frozen", "Upgrade pending", "Upgrade in progress")


class JSONSchemaExtensionTests(unittest.TestCase):
    """JSON schema carries the P42 governance extension correctly."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_id_version_unchanged(self) -> None:
        self.assertEqual(
            self.schema["$id"],
            "https://well-harness.local/json_schema/controller_truth_adapter_metadata_v1.schema.json",
        )
        self.assertEqual(self.schema["properties"]["version"]["const"], 1)

    def test_additional_properties_still_false(self) -> None:
        self.assertFalse(self.schema["additionalProperties"])

    def test_truth_level_property_shape(self) -> None:
        prop = self.schema["properties"]["truth_level"]
        self.assertEqual(prop["type"], "string")
        self.assertEqual(tuple(prop["enum"]), VALID_TRUTH_LEVELS)
        self.assertIn("pre-P42/unclassified", prop["description"])

    def test_status_property_shape(self) -> None:
        prop = self.schema["properties"]["status"]
        self.assertEqual(prop["type"], "string")
        self.assertEqual(tuple(prop["enum"]), VALID_STATUSES)
        self.assertIn("pre-P42/unclassified", prop["description"])

    def test_governance_fields_are_optional(self) -> None:
        required = set(self.schema["required"])
        self.assertNotIn("truth_level", required)
        self.assertNotIn("status", required)

    def test_top_level_description_codifies_missing_field_semantic(self) -> None:
        self.assertIn(
            "pre-P42/unclassified",
            self.schema["description"],
            "Schema top-level description must codify 'missing field = pre-P42/unclassified' semantic.",
        )


class SerializerStripNoneTests(unittest.TestCase):
    """controller_truth_metadata_to_dict drops None governance fields."""

    BASE_KWARGS = dict(
        adapter_id="test-adapter",
        system_id="test-system",
        truth_kind="test-kind",
        source_of_truth="test/source.py",
        description="Test metadata for P42 serializer coverage.",
    )

    PRE_P42_PAYLOAD_KEYS = frozenset({
        "$schema",
        "kind",
        "version",
        "adapter_id",
        "system_id",
        "truth_kind",
        "source_of_truth",
        "description",
    })

    def test_none_governance_yields_pre_p42_payload_shape(self) -> None:
        metadata = ControllerTruthMetadata(**self.BASE_KWARGS)
        self.assertIsNone(metadata.truth_level)
        self.assertIsNone(metadata.status)
        payload = controller_truth_metadata_to_dict(metadata)
        self.assertEqual(set(payload.keys()), self.PRE_P42_PAYLOAD_KEYS)
        self.assertNotIn("truth_level", payload)
        self.assertNotIn("status", payload)
        # Envelope constants still present.
        self.assertEqual(payload["$schema"], CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID)
        self.assertEqual(payload["kind"], CONTROLLER_TRUTH_ADAPTER_METADATA_KIND)
        self.assertEqual(payload["version"], CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION)

    def test_explicit_governance_fields_serialized(self) -> None:
        metadata = ControllerTruthMetadata(
            truth_level="certified",
            status="In use",
            **self.BASE_KWARGS,
        )
        payload = metadata.to_dict()
        self.assertEqual(payload["truth_level"], "certified")
        self.assertEqual(payload["status"], "In use")

    def test_partial_governance_strips_only_none_field(self) -> None:
        metadata = ControllerTruthMetadata(
            truth_level="demonstrative",
            status=None,
            **self.BASE_KWARGS,
        )
        payload = metadata.to_dict()
        self.assertEqual(payload["truth_level"], "demonstrative")
        self.assertNotIn("status", payload)


class SchemaEnumRejectionTests(unittest.TestCase):
    """Invalid governance enum values are rejected by jsonschema."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            cls._jsonschema = None
        else:
            cls._jsonschema = jsonschema
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def _skip_if_no_jsonschema(self) -> None:
        if self._jsonschema is None:
            self.skipTest("optional dependency jsonschema is not installed")

    def _base_payload(self) -> dict:
        return {
            "$schema": CONTROLLER_TRUTH_ADAPTER_METADATA_SCHEMA_ID,
            "kind": CONTROLLER_TRUTH_ADAPTER_METADATA_KIND,
            "version": CONTROLLER_TRUTH_ADAPTER_METADATA_VERSION,
            "adapter_id": "test-id",
            "system_id": "test-sys",
            "truth_kind": "k",
            "source_of_truth": "s",
            "description": "d",
        }

    def test_valid_governance_values_pass(self) -> None:
        self._skip_if_no_jsonschema()
        payload = self._base_payload()
        payload["truth_level"] = "certified"
        payload["status"] = "In use"
        self._jsonschema.validate(payload, self.schema)

    def test_bogus_truth_level_rejected(self) -> None:
        self._skip_if_no_jsonschema()
        payload = self._base_payload()
        payload["truth_level"] = "gold"
        with self.assertRaises(self._jsonschema.ValidationError):
            self._jsonschema.validate(payload, self.schema)

    def test_bogus_status_rejected(self) -> None:
        self._skip_if_no_jsonschema()
        payload = self._base_payload()
        payload["status"] = "in-progress"
        with self.assertRaises(self._jsonschema.ValidationError):
            self._jsonschema.validate(payload, self.schema)


class GeneratorTemplateP42DefaultsTests(unittest.TestCase):
    """generate_adapter.py no longer shadows central dataclasses and emits P42 defaults."""

    @classmethod
    def setUpClass(cls) -> None:
        spec_path = _REPO_ROOT / "src/well_harness/tools/specs/reference_thrust_reverser.spec.json"
        cls.spec = json.loads(spec_path.read_text(encoding="utf-8"))
        cls.source = spec_to_adapter_source(cls.spec, source_path=str(spec_path))

    def test_no_shadow_ControllerTruthMetadata(self) -> None:
        # The specific multi-line signature of the old shadow redefinition.
        forbidden = "@dataclass(frozen=True)\nclass ControllerTruthMetadata"
        self.assertNotIn(
            forbidden, self.source,
            "Generated adapter must not locally redefine ControllerTruthMetadata (Codex Counter B).",
        )

    def test_no_shadow_GenericTruthEvaluation(self) -> None:
        forbidden = "@dataclass(frozen=True, eq=False)\nclass GenericTruthEvaluation"
        self.assertNotIn(
            forbidden, self.source,
            "Generated adapter must not locally redefine GenericTruthEvaluation.",
        )

    def test_central_import_preserved(self) -> None:
        self.assertIn(
            "from well_harness.controller_adapter import (\n    ControllerTruthMetadata,\n    GenericTruthEvaluation,\n)",
            self.source,
            "Generated adapter must import dataclasses from the central module.",
        )

    def test_emitted_metadata_declares_P42_defaults(self) -> None:
        self.assertIn('truth_level="demonstrative"', self.source)
        self.assertIn('status="Upgrade pending"', self.source)

    def test_emitted_metadata_is_not_In_use_by_default(self) -> None:
        # Defensive: catches accidental regression to "In use" default.
        # Restrict the check to the CONTROLLER_METADATA assignment block so the
        # docstring's promotion protocol (which mentions "status='In use'" as
        # the target of a manual upgrade) does not false-positive.
        start = self.source.index("CONTROLLER_METADATA = ControllerTruthMetadata(")
        end = self.source.index(")", start) + 1
        metadata_block = self.source[start:end]
        self.assertIn('status="Upgrade pending"', metadata_block)
        self.assertNotIn(
            'status="In use"', metadata_block,
            "CONTROLLER_METADATA block must start as 'Upgrade pending', never 'In use' (P42 Q5=A).",
        )


if __name__ == "__main__":
    unittest.main()
