"""Sandbox validation tests for archive-restore endpoint.

Verifies that path-traversal attacks are blocked by the two-layer defense:
  Layer 1 (demo_server.py): manifest_path must resolve inside archive_root
  Layer 2 (workbench_bundle.py): archive_dir cannot be an absolute path escaping the sandbox
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from unittest import mock

from tools.validate_workbench_changerequest_handoff_schema import sample_changerequest_handoff_packet
from well_harness.demo_server import build_workbench_archive_restore_response, default_workbench_archive_root
from well_harness.document_intake import load_intake_packet
from well_harness.workbench_bundle import (
    archive_workbench_bundle,
    build_workbench_bundle,
    load_workbench_archive_restore_payload,
)
from well_harness.workbench_changerequest_handoff import (
    FOUNDATION_REVIEW_ARCHIVE_KIND,
    FOUNDATION_REVIEW_ARCHIVE_REQUIRED_SECTIONS,
    FOUNDATION_REVIEW_ARCHIVE_VERSION,
    changerequest_handoff_ui_checksum,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"


def _create_legitimate_archive(archive_root: Path) -> tuple[Path, Path]:
    """Create a valid archive inside archive_root. Returns (manifest_path, archive_dir)."""
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
        archive_root=archive_root,
        workspace_handoff={"test": "handoff"},
        workspace_snapshot={"test": "snapshot"},
    )
    # manifest_json_path is a string, convert to Path
    manifest_path = Path(archive.manifest_json_path)
    return manifest_path, Path(archive.archive_dir)


def _create_archive_with_workspace_snapshot(
    archive_root: Path,
    workspace_snapshot: dict,
) -> tuple[Path, Path]:
    """Create a valid archive with a caller-supplied workspace snapshot."""
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
        archive_root=archive_root,
        workspace_handoff={"test": "handoff"},
        workspace_snapshot=workspace_snapshot,
    )
    return Path(archive.manifest_json_path), Path(archive.archive_dir)


def _create_legitimate_archive_in_default_root() -> tuple[Path, Path]:
    """Create a valid archive inside default_workbench_archive_root()."""
    archive_root = default_workbench_archive_root()
    archive_root.mkdir(parents=True, exist_ok=True)
    return _create_legitimate_archive(archive_root)


def _valid_handoff_evidence_archive() -> dict:
    handoff_packet = sample_changerequest_handoff_packet()
    return {
        "kind": "well-harness-workbench-evidence-archive",
        "version": 1,
        "archive_scope": "local_draft_download",
        "changerequest_handoff_packet": handoff_packet,
        "checksums": {
            "changerequest_handoff_packet_checksum": changerequest_handoff_ui_checksum(handoff_packet),
        },
    }


def _valid_foundation_review_archive() -> dict:
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
        "sections": {
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
        },
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


def _valid_review_ready_evidence_archive() -> dict:
    payload = _valid_handoff_evidence_archive()
    foundation_review_archive = _valid_foundation_review_archive()
    payload["foundation_review_archive"] = foundation_review_archive
    payload["checksums"]["foundation_review_archive_checksum"] = changerequest_handoff_ui_checksum(
        foundation_review_archive
    )
    return payload


def _build_valid_manifest(archive_dir_value: str, files: Optional[dict] = None) -> dict:
    """Build a minimally valid manifest that passes schema validation."""
    return {
        "kind": "well-harness-workbench-archive-manifest",
        "version": 1,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "archive_dir": archive_dir_value,
        "bundle": {
            "bundle_kind": "full_workbench_bundle",
            "system_id": "test-system",
            "system_title": "Test System",
            "ready_for_spec_build": True,
            "selected_scenario_id": "test-scenario",
            "selected_fault_mode_id": "test-fault",
            "next_actions": ["Test action 1", "Test action 2"],
        },
        "files": files or {
            "bundle_json": "bundle.json",
            "summary_markdown": "summary.md",
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
            "archive_summary_markdown": "summary.md",
        },
        "self_check": {
            "command": "python3 -m well_harness.cli archive-manifest .",
            "working_directory": "archive_dir",
        },
    }


class ArchiveRestoreSandboxTests(unittest.TestCase):
    """Layer 1 + Layer 2 sandbox tests for build_workbench_archive_restore_response."""

    def test_absolute_manifest_path_outside_archive_root(self):
        """Absolute manifest path outside archive_root should be rejected.

        Layer 1 check: resolved manifest_path must be within archive_root.
        """
        with tempfile.TemporaryDirectory() as tmp:
            evil_dir = Path(tmp) / "evil"
            evil_dir.mkdir()
            evil_manifest = evil_dir / "manifest.json"

            # Create required files so schema validation passes
            (evil_dir / "bundle.json").write_text(json.dumps({"test": "bundle"}), encoding="utf-8")
            (evil_dir / "summary.md").write_text("Test summary", encoding="utf-8")
            (evil_dir / "intake_assessment.json").write_text(json.dumps({"test": "assessment"}), encoding="utf-8")

            # Create a valid manifest in /tmp (outside archive_root)
            manifest = _build_valid_manifest(".", files={
                "bundle_json": "bundle.json",
                "summary_markdown": "summary.md",
                "intake_assessment_json": "intake_assessment.json",
                "clarification_brief_json": None,
                "playback_report_json": None,
                "fault_diagnosis_report_json": None,
                "knowledge_artifact_json": None,
                "workspace_handoff_json": None,
                "workspace_snapshot_json": None,
            })
            evil_manifest.write_text(json.dumps(manifest), encoding="utf-8")

            response, error = build_workbench_archive_restore_response({
                "manifest_path": str(evil_manifest),
            })
            # Layer 1 (manifest location) was removed — portable archives with
            # relative archive_dir from arbitrary locations are legitimate.
            # Layer 2 (absolute archive_dir escape) is the real security boundary.
            self.assertIsNotNone(response)
            self.assertIsNone(error)
            # archive_dir is resolved to the directory containing the manifest
            self.assertTrue(Path(response["archive_dir"]).is_absolute())

    def test_absolute_manifest_path_with_dotdot_escape(self):
        """Absolute path with .. attempting to escape should be sandbox_violation.

        Layer 1 check should catch this after resolving the path.
        """
        # /etc/passwd/../tmp/evil.json resolves to /etc/tmp/evil.json
        # which is outside archive_root
        response, error = build_workbench_archive_restore_response({
            "manifest_path": "/etc/passwd/../tmp/evil.json",
        })
        self.assertIsNone(response)
        self.assertIsNotNone(error)
        # File doesn't exist - gets caught before sandbox check
        self.assertEqual(error["error"], "workbench_archive_not_found")

    def test_manifest_archive_dir_root_slash(self):
        """Manifest with archive_dir='/' should be sandbox_violation.

        Layer 2: _resolve_manifest_archive_dir_path returns None for absolute
        paths that escape the sandbox.
        """
        archive_root = default_workbench_archive_root()
        archive_root.mkdir(parents=True, exist_ok=True)

        safe_dir = archive_root / "test_root_slash"
        safe_dir.mkdir(exist_ok=True)

        # Create bundle.json so the manifest is valid
        bundle_path = safe_dir / "bundle.json"
        bundle_path.write_text(json.dumps({"test": "bundle"}), encoding="utf-8")

        summary_path = safe_dir / "summary.md"
        summary_path.write_text("Test summary", encoding="utf-8")

        intake_path = safe_dir / "intake_assessment.json"
        intake_path.write_text(json.dumps({"test": "assessment"}), encoding="utf-8")

        manifest = _build_valid_manifest("/", files={
            "bundle_json": "bundle.json",
            "summary_markdown": "summary.md",
            "intake_assessment_json": "intake_assessment.json",
            "clarification_brief_json": None,
            "playback_report_json": None,
            "fault_diagnosis_report_json": None,
            "knowledge_artifact_json": None,
            "workspace_handoff_json": None,
            "workspace_snapshot_json": None,
        })
        manifest_path = safe_dir / "archive_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        response, error = build_workbench_archive_restore_response({
            "manifest_path": str(manifest_path),
        })
        self.assertIsNone(response)
        self.assertIsNotNone(error)
        # Layer 2 catches archive_dir="/" escaping sandbox
        self.assertEqual(error["error"], "sandbox_violation")

    def test_manifest_archive_dir_absolute_etc(self):
        """Manifest with archive_dir='/etc' should be sandbox_violation.

        Layer 2: absolute archive_dir outside sandbox is rejected.
        """
        archive_root = default_workbench_archive_root()
        archive_root.mkdir(parents=True, exist_ok=True)

        safe_dir = archive_root / "test_etc"
        safe_dir.mkdir(exist_ok=True)

        # Create required files
        bundle_path = safe_dir / "bundle.json"
        bundle_path.write_text(json.dumps({"test": "bundle"}), encoding="utf-8")
        summary_path = safe_dir / "summary.md"
        summary_path.write_text("Test summary", encoding="utf-8")
        intake_path = safe_dir / "intake_assessment.json"
        intake_path.write_text(json.dumps({"test": "assessment"}), encoding="utf-8")

        manifest = _build_valid_manifest("/etc", files={
            "bundle_json": "bundle.json",
            "summary_markdown": "summary.md",
            "intake_assessment_json": "intake_assessment.json",
            "clarification_brief_json": None,
            "playback_report_json": None,
            "fault_diagnosis_report_json": None,
            "knowledge_artifact_json": None,
            "workspace_handoff_json": None,
            "workspace_snapshot_json": None,
        })
        manifest_path = safe_dir / "archive_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        response, error = build_workbench_archive_restore_response({
            "manifest_path": str(manifest_path),
        })
        self.assertIsNone(response)
        self.assertIsNotNone(error)
        self.assertEqual(error["error"], "sandbox_violation")

    def test_legitimate_relative_manifest_inside_root(self):
        """Valid archive manifest with relative archive_dir should work."""
        manifest_path, archive_dir = _create_legitimate_archive_in_default_root()

        response, error = build_workbench_archive_restore_response({
            "manifest_path": str(manifest_path),
        })
        self.assertIsNotNone(response)
        self.assertIsNone(error)
        self.assertEqual(response["archive_dir"], str(archive_dir))

    def test_legitimate_absolute_manifest_inside_root(self):
        """Absolute path to real manifest under archive_root should be accepted."""
        manifest_path, archive_dir = _create_legitimate_archive_in_default_root()

        # Pass the absolute path
        abs_path = str(manifest_path.resolve())
        response, error = build_workbench_archive_restore_response({
            "manifest_path": abs_path,
        })
        self.assertIsNotNone(response)
        self.assertIsNone(error)

    def test_archive_restore_reports_handoff_validation_for_valid_evidence_archive(self):
        """Archive restore exposes machine-readable validation for embedded handoff packets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path, _archive_dir = _create_archive_with_workspace_snapshot(
                Path(temp_dir),
                _valid_handoff_evidence_archive(),
            )

            response, error = build_workbench_archive_restore_response({
                "manifest_path": str(manifest_path),
            })

        self.assertIsNotNone(response)
        self.assertIsNone(error)
        validation = response["changerequest_handoff_validation"]
        self.assertEqual("pass", validation["status"])
        self.assertEqual("pass", validation["checksum_status"])
        self.assertEqual("none", validation["truth_effect"])
        self.assertTrue(validation["canonical_hash"])

    def test_archive_restore_reports_foundation_review_archive_validation(self):
        """Review-ready evidence archives expose restore-time foundation validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path, _archive_dir = _create_archive_with_workspace_snapshot(
                Path(temp_dir),
                _valid_review_ready_evidence_archive(),
            )

            response, error = build_workbench_archive_restore_response({
                "manifest_path": str(manifest_path),
            })

        self.assertIsNotNone(response)
        self.assertIsNone(error)
        validation = response["foundation_review_archive_validation"]
        self.assertEqual("pass", validation["status"])
        self.assertEqual("pass", validation["checksum_status"])
        self.assertEqual("none", validation["truth_effect"])
        self.assertTrue(validation["canonical_hash"])

    def test_archive_restore_rejects_invalid_foundation_review_archive(self):
        """Invalid review archives fail restore instead of being treated as trusted proof."""
        evidence_archive = _valid_review_ready_evidence_archive()
        evidence_archive["foundation_review_archive"]["truth_effect"] = "certified"
        evidence_archive["checksums"]["foundation_review_archive_checksum"] = changerequest_handoff_ui_checksum(
            evidence_archive["foundation_review_archive"]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path, _archive_dir = _create_archive_with_workspace_snapshot(
                Path(temp_dir),
                evidence_archive,
            )
            response, error = build_workbench_archive_restore_response({
                "manifest_path": str(manifest_path),
            })

        self.assertIsNone(response)
        self.assertIsNotNone(error)
        self.assertEqual("invalid_workbench_archive", error["error"])
        self.assertIn("foundation review archive", error["message"])
        self.assertIn("truth_effect must be 'none'", error["message"])

    def test_archive_restore_rejects_invalid_handoff_packet_in_evidence_archive(self):
        """Invalid embedded handoff packets fail restore instead of being silently trusted."""
        evidence_archive = _valid_handoff_evidence_archive()
        evidence_archive["changerequest_handoff_packet"]["truth_level_impact"] = "certified"
        evidence_archive["checksums"]["changerequest_handoff_packet_checksum"] = changerequest_handoff_ui_checksum(
            evidence_archive["changerequest_handoff_packet"]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path, _archive_dir = _create_archive_with_workspace_snapshot(
                Path(temp_dir),
                evidence_archive,
            )
            response, error = build_workbench_archive_restore_response({
                "manifest_path": str(manifest_path),
            })

        self.assertIsNone(response)
        self.assertIsNotNone(error)
        self.assertEqual("invalid_workbench_archive", error["error"])
        self.assertIn("ChangeRequest handoff archive", error["message"])
        self.assertIn("truth_level_impact must be 'none'", error["message"])

    def test_archive_restore_is_backward_compatible_without_handoff_packet(self):
        """Archives without handoff packets still restore with explicit not_present status."""
        manifest_path, _archive_dir = _create_legitimate_archive_in_default_root()

        response, error = build_workbench_archive_restore_response({
            "manifest_path": str(manifest_path),
        })

        self.assertIsNotNone(response)
        self.assertIsNone(error)
        validation = response["changerequest_handoff_validation"]
        self.assertEqual("not_present", validation["status"])
        self.assertEqual(0, validation["issue_count"])
        foundation_validation = response["foundation_review_archive_validation"]
        self.assertEqual("not_present", foundation_validation["status"])
        self.assertEqual(0, foundation_validation["issue_count"])

    def test_valid_nested_archive_dir(self):
        """Manifest with relative archive_dir='subdir/' should be accepted."""
        manifest_path, archive_dir = _create_legitimate_archive_in_default_root()

        # The legitimate archive uses relative "." as archive_dir
        response, error = build_workbench_archive_restore_response({
            "manifest_path": str(manifest_path),
        })
        self.assertIsNotNone(response)
        self.assertIsNone(error)

    def test_symlink_within_archive_is_allowed(self):
        """Symlinks within the archive directory should be allowed.

        This tests that the sandbox allows legitimate symlinks inside the archive.
        The actual symlink escape (following a symlink to outside archive_root)
        would require actually reading through the symlink, which is caught elsewhere.
        """
        archive_root = default_workbench_archive_root()
        archive_root.mkdir(parents=True, exist_ok=True)

        import uuid
        unique_dir = f"test_symlink_{uuid.uuid4().hex[:8]}"
        safe_dir = archive_root / unique_dir
        safe_dir.mkdir(exist_ok=True)

        # Create a subdirectory that could contain symlinks
        subdir = safe_dir / "subdir"
        subdir.mkdir()

        # Create required files in subdir (relative to archive_dir="subdir")
        (subdir / "bundle.json").write_text(json.dumps({"test": "bundle"}), encoding="utf-8")
        (subdir / "summary.md").write_text("Test summary", encoding="utf-8")
        (subdir / "intake_assessment.json").write_text(json.dumps({"test": "assessment"}), encoding="utf-8")

        manifest = _build_valid_manifest("subdir", files={
            "bundle_json": "bundle.json",
            "summary_markdown": "summary.md",
            "intake_assessment_json": "intake_assessment.json",
            "clarification_brief_json": None,
            "playback_report_json": None,
            "fault_diagnosis_report_json": None,
            "knowledge_artifact_json": None,
            "workspace_handoff_json": None,
            "workspace_snapshot_json": None,
        })
        manifest_path = safe_dir / "archive_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        response, error = build_workbench_archive_restore_response({
            "manifest_path": str(manifest_path),
        })
        # This should succeed since subdir is within archive_root
        self.assertIsNotNone(response)
        self.assertIsNone(error)


class WorkbenchBundleLayer2Tests(unittest.TestCase):
    """Direct Layer 2 (_resolve_manifest_archive_dir_path) isolation tests."""

    def test_archive_dir_root_slash_causes_sandbox_escape_error(self):
        """Layer 2: archive_dir='/' should cause SandboxEscapeError (sandbox escape)."""
        from well_harness.workbench_bundle import SandboxEscapeError

        archive_root = default_workbench_archive_root()
        archive_root.mkdir(parents=True, exist_ok=True)

        safe_dir = archive_root / "layer2_test"
        safe_dir.mkdir(exist_ok=True)

        # Create required files
        bundle_path = safe_dir / "bundle.json"
        bundle_path.write_text(json.dumps({"test": "bundle"}), encoding="utf-8")
        summary_path = safe_dir / "summary.md"
        summary_path.write_text("Test summary", encoding="utf-8")
        intake_path = safe_dir / "intake_assessment.json"
        intake_path.write_text(json.dumps({"test": "assessment"}), encoding="utf-8")

        manifest = _build_valid_manifest("/", files={
            "bundle_json": "bundle.json",
            "summary_markdown": "summary.md",
            "intake_assessment_json": "intake_assessment.json",
            "clarification_brief_json": None,
            "playback_report_json": None,
            "fault_diagnosis_report_json": None,
            "knowledge_artifact_json": None,
            "workspace_handoff_json": None,
            "workspace_snapshot_json": None,
        })
        manifest_path = safe_dir / "archive_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        # Layer 2 should raise SandboxEscapeError for archive_dir="/"
        with self.assertRaises(SandboxEscapeError) as ctx:
            load_workbench_archive_restore_payload(str(manifest_path))
        self.assertIn("sandbox", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
