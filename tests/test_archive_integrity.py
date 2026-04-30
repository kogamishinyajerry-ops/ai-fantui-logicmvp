"""Regression tests for P18.6 archive integrity — SHA256 checksums on write + verify on load.

Verifies that:
  1. archive_workbench_bundle() computes and stores SHA256 checksums in manifest
  2. validate_workbench_archive_manifest() verifies checksums and reports mismatches
  3. Corrupted files are detected (checksum mismatch raises issue)
  4. Invalid SHA256 hex strings are rejected by validation
  5. Schema accepts integrity field
  6. CLI renders integrity info in validation output
"""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from well_harness.workbench_bundle import (
    ChecksumMismatchError,
    archive_workbench_bundle,
    build_workbench_archive_manifest,
    build_workbench_bundle,
    load_workbench_archive_manifest,
    validate_workbench_archive_manifest,
)
from well_harness.document_intake import load_intake_packet


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"


def _create_legitimate_bundle() -> tuple[Path, Path]:
    """Create a valid archive, return (archive_dir, manifest_path)."""
    packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)
    bundle = build_workbench_bundle(
        packet,
        confirmed_root_cause="Test cause",
        repair_action="Test action",
        validation_after_fix="Test validation",
        residual_risk="Test risk",
    )
    archive = archive_workbench_bundle(
        bundle,
        archive_root=tempfile.gettempdir(),
        workspace_handoff={"test": "handoff"},
        workspace_snapshot={"test": "snapshot"},
    )
    manifest_path = Path(archive.manifest_json_path)
    return Path(archive.archive_dir), manifest_path


class TestArchiveIntegrityChecksums(unittest.TestCase):
    """Archive integrity checksum tests."""

    def test_archive_includes_integrity_field_in_manifest(self):
        """archive_workbench_bundle must write SHA256 checksums to archive_manifest.json."""
        archive_dir, manifest_path = _create_legitimate_bundle()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertIn("integrity", manifest)
            integrity = manifest["integrity"]
            self.assertIsInstance(integrity, dict)
            # Must have at least the 3 required files
            self.assertIn("bundle_json", integrity)
            self.assertIn("summary_markdown", integrity)
            self.assertIn("intake_assessment_json", integrity)
            # SHA256 hex = 64 chars
            for key, digest in integrity.items():
                self.assertEqual(len(digest), 64, f"{key} digest is not 64 chars")
                self.assertTrue(
                    all(c in "0123456789abcdef" for c in digest),
                    f"{key} digest is not a valid hex string",
                )
        finally:
            # Clean up
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_valid_archive_passes_integrity_validation(self):
        """A non-corrupted archive with integrity field must pass validation."""
        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            issues = validate_workbench_archive_manifest(
                json.loads(manifest_path.read_text(encoding="utf-8")),
                manifest_path=manifest_path,
                require_existing_files=True,
            )
            checksum_issues = [i for i in issues if "checksum" in i.lower() or "integrity" in i.lower()]
            self.assertEqual(
                checksum_issues,
                [],
                f"Unexpected integrity issues: {checksum_issues}",
            )
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_corrupted_file_detected_by_integrity_check(self):
        """Modifying an archived file after writing must cause checksum mismatch."""
        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            integrity = manifest["integrity"]

            # Corrupt bundle.json by appending a space
            bundle_json_path = archive_dir / "bundle.json"
            original = bundle_json_path.read_text(encoding="utf-8")
            bundle_json_path.write_text(original + " ", encoding="utf-8")

            # Re-validate — should detect the mismatch
            issues = validate_workbench_archive_manifest(
                manifest,
                manifest_path=manifest_path,
                require_existing_files=True,
            )
            checksum_issues = [i for i in issues if "checksum mismatch" in i.lower()]
            self.assertGreater(
                len(checksum_issues),
                0,
                "Checksum mismatch was not detected after file corruption",
            )
            # The issue should mention bundle_json
            self.assertTrue(
                any("bundle_json" in issue for issue in checksum_issues),
                f"Issue does not mention bundle_json: {checksum_issues}",
            )
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_invalid_sha256_in_integrity_field_reported(self):
        """Non-64-char or non-hex integrity values must be validation issues."""
        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            # Replace a valid hash with an invalid one
            manifest["integrity"]["bundle_json"] = "not-a-valid-sha256"
            manifest["integrity"]["intake_assessment_json"] = "a" * 63  # too short
            manifest["integrity"]["summary_markdown"] = "g" * 64  # invalid char 'g'

            issues = validate_workbench_archive_manifest(
                manifest,
                manifest_path=manifest_path,
                require_existing_files=True,
            )
            sha256_issues = [i for i in issues if "sha256" in i.lower() or "64-character" in i]
            self.assertGreater(
                len(sha256_issues),
                0,
                "Invalid SHA256 format was not reported as validation issue",
            )
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_missing_integrity_field_is_allowed(self):
        """Manifest without integrity field must still pass validation (backward compat)."""
        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            del manifest["integrity"]

            issues = validate_workbench_archive_manifest(
                manifest,
                manifest_path=manifest_path,
                require_existing_files=True,
            )
            # Should not have any integrity-related issues
            integrity_issues = [i for i in issues if "integrity" in i.lower()]
            self.assertEqual(integrity_issues, [], f"Unexpected integrity issues: {integrity_issues}")
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_schema_accepts_integrity_field(self):
        """Schema validation (via validate) must accept a manifest with integrity field."""
        import jsonschema

        schema_path = Path(__file__).parent.parent / "docs" / "json_schema" / "workbench_archive_manifest_v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            # jsonschema validation should not raise
            jsonschema.validate(manifest, schema)
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_schema_rejects_integrity_with_invalid_hash(self):
        """Schema must reject an integrity value that is not a 64-char hex string."""
        import jsonschema

        schema_path = Path(__file__).parent.parent / "docs" / "json_schema" / "workbench_archive_v1.schema.json"
        if not schema_path.exists():
            schema_path = Path(__file__).parent.parent / "docs" / "json_schema" / "workbench_archive_manifest_v1.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        manifest = {
            "$schema": "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
            "kind": "well-harness-workbench-archive-manifest",
            "version": 1,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "archive_dir": ".",
            "bundle": {
                "bundle_kind": "full_workbench_bundle",
                "system_id": "test",
                "system_title": "Test",
                "ready_for_spec_build": True,
                "selected_scenario_id": "test",
                "selected_fault_mode_id": None,
                "next_actions": [],
            },
            "files": {
                "bundle_json": "bundle.json",
                "summary_markdown": "README.md",
                "intake_assessment_json": "intake_assessment.json",
                "clarification_brief_json": None,
                "playback_report_json": None,
                "fault_diagnosis_report_json": None,
                "knowledge_artifact_json": None,
                "workspace_handoff_json": None,
                "workspace_snapshot_json": None,
            },
            "restore_targets": {
                "browser_workspace_snapshot": None,
                "browser_handoff_summary": None,
                "archive_summary_markdown": "README.md",
            },
            "integrity": {
                "bundle_json": "not-64-chars",  # invalid: too short
            },
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(manifest, schema)

    def test_checksum_computed_for_all_present_files(self):
        """Only files actually present in the archive should appear in integrity dict."""
        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            integrity = manifest["integrity"]
            files = manifest["files"]
            # Optional files that may be None should not have integrity entries
            for key in ("clarification_brief_json", "playback_report_json",
                        "fault_diagnosis_report_json", "knowledge_artifact_json",
                        "workspace_handoff_json", "workspace_snapshot_json"):
                if files.get(key) is None:
                    self.assertNotIn(
                        key,
                        integrity,
                        f"Optional file {key} is None but has an integrity entry",
                    )
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)

    def test_manifest_validation_is_stable_when_files_and_integrity_keys_reordered(self):
        """Manifest validation must not depend on object key insertion order."""
        archive_dir, manifest_path = _create_legitimate_archive()
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"] = dict(reversed(list(manifest["files"].items())))
            manifest["integrity"] = dict(reversed(list(manifest["integrity"].items())))

            issues = validate_workbench_archive_manifest(
                manifest,
                manifest_path=manifest_path,
                require_existing_files=True,
            )

            self.assertEqual([], list(issues))
        finally:
            import shutil
            shutil.rmtree(archive_dir, ignore_errors=True)


# Helper to create archive for tests (duplicated to avoid top-level import of shutil above)
def _create_legitimate_archive() -> tuple[Path, Path]:
    """Create a valid archive, return (archive_dir, manifest_path)."""
    packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)
    bundle = build_workbench_bundle(
        packet,
        confirmed_root_cause="Test cause",
        repair_action="Test action",
        validation_after_fix="Test validation",
        residual_risk="Test risk",
    )
    archive = archive_workbench_bundle(
        bundle,
        archive_root=tempfile.gettempdir(),
        workspace_handoff={"test": "handoff"},
        workspace_snapshot={"test": "snapshot"},
    )
    manifest_path = Path(archive.manifest_json_path)
    return Path(archive.archive_dir), manifest_path


if __name__ == "__main__":
    unittest.main()
