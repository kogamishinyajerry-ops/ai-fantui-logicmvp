import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from well_harness.cli import main
from well_harness.document_intake import intake_packet_from_dict, intake_template_payload, load_intake_packet
from well_harness.fault_diagnosis import FAULT_DIAGNOSIS_KIND
from well_harness.knowledge_capture import KNOWLEDGE_ARTIFACT_KIND
from well_harness.scenario_playback import PLAYBACK_TRACE_KIND
from well_harness.workbench_bundle import (
    WORKBENCH_BUNDLE_KIND,
    WORKBENCH_BUNDLE_SCHEMA_ID,
    WORKBENCH_BUNDLE_VERSION,
    archive_workbench_bundle,
    build_workbench_bundle,
    load_workbench_archive_bundle_payload,
    load_workbench_archive_manifest,
    load_workbench_archive_restore_payload,
    load_workbench_archive_workspace_handoff,
    load_workbench_archive_workspace_snapshot,
    render_workbench_bundle_markdown,
    render_workbench_bundle_text,
    resolve_workbench_archive_manifest_files,
    validate_workbench_archive_manifest,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
PROJECT_ROOT = Path(__file__).parents[1]
ARCHIVE_MANIFEST_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "workbench_archive_manifest_v1.schema.json"
WORKBENCH_BUNDLE_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "workbench_bundle_v1.schema.json"
SYSTEM_INTAKE_PACKET_PATH = FIXTURES_DIR / "system_intake_packet_v1.json"


def run_json_cli(args: list[str]) -> tuple[int, dict]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(args)
    return exit_code, json.loads(buffer.getvalue())


def run_text_cli(args: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = main(args)
    return exit_code, buffer.getvalue()


def load_archive_manifest_schema() -> dict:
    return json.loads(ARCHIVE_MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))


def load_workbench_bundle_schema() -> dict:
    return json.loads(WORKBENCH_BUNDLE_SCHEMA_PATH.read_text(encoding="utf-8"))


class WorkbenchBundleTests(unittest.TestCase):
    def test_build_workbench_bundle_returns_clarification_follow_up_for_blocked_packet(self):
        packet = intake_packet_from_dict(intake_template_payload())

        bundle = build_workbench_bundle(packet)

        self.assertFalse(bundle.ready_for_spec_build)
        self.assertEqual("clarification_follow_up", bundle.bundle_kind)
        self.assertIsNotNone(bundle.clarification_brief)
        self.assertIsNone(bundle.playback_report)
        self.assertIsNone(bundle.fault_diagnosis_report)
        self.assertIsNone(bundle.knowledge_artifact)
        self.assertGreaterEqual(len(bundle.next_actions), 1)
        self.assertIn("Answer clarification", " ".join(bundle.next_actions))

    def test_build_workbench_bundle_stitches_ready_chain_into_single_bundle(self):
        packet = load_intake_packet(SYSTEM_INTAKE_PACKET_PATH)

        bundle = build_workbench_bundle(
            packet,
            confirmed_root_cause="Pressure sensor bias was pulling the reported value below the unlock threshold.",
            repair_action="Recalibrated the pressure sensing path and confirmed the unlock threshold returned to nominal.",
            validation_after_fix="Replayed the acceptance scenario and the monitored command path completed again.",
            residual_risk="Continue monitoring for future pressure-sensor drift under maintenance checks.",
        )

        self.assertTrue(bundle.ready_for_spec_build)
        self.assertEqual("full_workbench_bundle", bundle.bundle_kind)
        self.assertEqual("ab_pressure_ramp", bundle.selected_scenario_id)
        self.assertEqual("pressure_sensor_bias_low", bundle.selected_fault_mode_id)
        self.assertIsNotNone(bundle.clarification_brief)
        self.assertIsNotNone(bundle.playback_report)
        self.assertIsNotNone(bundle.fault_diagnosis_report)
        self.assertIsNotNone(bundle.knowledge_artifact)
        self.assertEqual("resolved", bundle.knowledge_artifact.status)
        self.assertIn("capture or archive the bundle artifact", " ".join(bundle.next_actions).lower())

    def test_workbench_bundle_serializes_to_schema_aware_payload(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        payload = bundle.to_dict()
        encoded = json.dumps(payload, ensure_ascii=False)

        self.assertEqual(WORKBENCH_BUNDLE_SCHEMA_ID, payload["$schema"])
        self.assertEqual(WORKBENCH_BUNDLE_KIND, payload["kind"])
        self.assertEqual(WORKBENCH_BUNDLE_VERSION, payload["version"])
        self.assertEqual("full_workbench_bundle", payload["bundle_kind"])
        self.assertEqual(PLAYBACK_TRACE_KIND, payload["playback_report"]["kind"])
        self.assertEqual(FAULT_DIAGNOSIS_KIND, payload["fault_diagnosis_report"]["kind"])
        self.assertEqual(KNOWLEDGE_ARTIFACT_KIND, payload["knowledge_artifact"]["kind"])
        self.assertIn("pressure_sensor_bias_low", encoded)

    def test_blocked_workbench_bundle_serializes_to_schema_aware_payload(self):
        bundle = build_workbench_bundle(intake_packet_from_dict(intake_template_payload()))

        payload = bundle.to_dict()

        self.assertEqual(WORKBENCH_BUNDLE_SCHEMA_ID, payload["$schema"])
        self.assertEqual(WORKBENCH_BUNDLE_KIND, payload["kind"])
        self.assertEqual(WORKBENCH_BUNDLE_VERSION, payload["version"])
        self.assertEqual("clarification_follow_up", payload["bundle_kind"])
        self.assertFalse(payload["ready_for_spec_build"])
        self.assertIsNone(payload["playback_report"])
        self.assertIsNone(payload["fault_diagnosis_report"])
        self.assertIsNone(payload["knowledge_artifact"])

    def test_workbench_bundle_schema_documents_generated_payload_shape(self):
        schema = load_workbench_bundle_schema()

        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual(WORKBENCH_BUNDLE_SCHEMA_ID, schema["$id"])
        self.assertEqual(WORKBENCH_BUNDLE_KIND, schema["properties"]["kind"]["const"])
        self.assertEqual(WORKBENCH_BUNDLE_VERSION, schema["properties"]["version"]["const"])
        self.assertEqual(WORKBENCH_BUNDLE_SCHEMA_ID, schema["properties"]["$schema"]["const"])
        self.assertEqual(PLAYBACK_TRACE_KIND, schema["$defs"]["playbackTraceEnvelope"]["properties"]["kind"]["const"])

    def test_optional_jsonschema_validates_generated_workbench_bundles_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        schema = load_workbench_bundle_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        ready_payload = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        ).to_dict()
        blocked_payload = build_workbench_bundle(intake_packet_from_dict(intake_template_payload())).to_dict()
        errors = sorted(
            [*validator.iter_errors(ready_payload), *validator.iter_errors(blocked_payload)],
            key=lambda error: tuple(error.absolute_path),
        )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_render_workbench_bundle_text_summarizes_blocked_and_ready_states(self):
        blocked_bundle = build_workbench_bundle(intake_packet_from_dict(intake_template_payload()))
        blocked_text = render_workbench_bundle_text(blocked_bundle)
        self.assertIn("bundle_kind: clarification_follow_up", blocked_text)
        self.assertIn("clarification_brief:", blocked_text)

        ready_bundle = build_workbench_bundle(load_intake_packet(SYSTEM_INTAKE_PACKET_PATH))
        ready_text = render_workbench_bundle_text(ready_bundle)
        self.assertIn("bundle_kind: full_workbench_bundle", ready_text)
        self.assertIn("playback:", ready_text)
        self.assertIn("knowledge_artifact:", ready_text)

    def test_render_workbench_bundle_markdown_and_archive_capture_ready_bundle(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        markdown = render_workbench_bundle_markdown(bundle)

        self.assertIn("# Workbench Bundle Archive", markdown)
        self.assertIn("## Playback Report", markdown)
        self.assertIn("## Knowledge Artifact", markdown)

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            archive_dir = Path(archive.archive_dir)

            self.assertTrue(archive_dir.exists())
            self.assertTrue(Path(archive.manifest_json_path).exists())
            self.assertTrue(Path(archive.bundle_json_path).exists())
            self.assertTrue(Path(archive.summary_markdown_path).exists())
            self.assertTrue(Path(archive.intake_assessment_json_path).exists())
            self.assertTrue(Path(archive.clarification_brief_json_path).exists())
            self.assertTrue(Path(archive.playback_report_json_path).exists())
            self.assertTrue(Path(archive.fault_diagnosis_report_json_path).exists())
            self.assertTrue(Path(archive.knowledge_artifact_json_path).exists())
            saved_bundle = json.loads(Path(archive.bundle_json_path).read_text(encoding="utf-8"))
            self.assertEqual("full_workbench_bundle", saved_bundle["bundle_kind"])
            saved_manifest = json.loads(Path(archive.manifest_json_path).read_text(encoding="utf-8"))
            self.assertEqual("well-harness-workbench-archive-manifest", saved_manifest["kind"])
            self.assertEqual(
                "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
                saved_manifest["$schema"],
            )
            self.assertEqual(".", saved_manifest["archive_dir"])
            self.assertEqual("bundle.json", saved_manifest["files"]["bundle_json"])
            self.assertEqual("README.md", saved_manifest["files"]["summary_markdown"])
            self.assertEqual("full_workbench_bundle", saved_manifest["bundle"]["bundle_kind"])
            self.assertEqual(
                "python3 -m well_harness.cli archive-manifest .",
                saved_manifest["self_check"]["command"],
            )
            self.assertEqual("archive_dir", saved_manifest["self_check"]["working_directory"])
            self.assertEqual((), validate_workbench_archive_manifest(saved_manifest, manifest_path=archive.manifest_json_path))
            loaded_manifest = load_workbench_archive_manifest(archive.manifest_json_path)
            self.assertEqual(saved_manifest, loaded_manifest)
            saved_summary = Path(archive.summary_markdown_path).read_text(encoding="utf-8")
            self.assertIn("## Knowledge Artifact", saved_summary)
            self.assertIn("## Archive Manifest", saved_summary)
            self.assertIn("https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json", saved_summary)
            self.assertIn("python3 -m well_harness.cli archive-manifest .", saved_summary)

    def test_archive_manifest_validation_reports_missing_core_file(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            manifest = load_workbench_archive_manifest(archive.manifest_json_path)
            Path(archive.bundle_json_path).unlink()

            issues = validate_workbench_archive_manifest(manifest, manifest_path=archive.manifest_json_path)

        self.assertIn("files.bundle_json does not point to an existing file", " ".join(issues))

    def test_load_workbench_archive_manifest_rejects_malformed_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "archive_manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "kind": "wrong-kind",
                        "version": 1,
                        "created_at_utc": "2026-04-12T00:00:00+00:00",
                        "archive_dir": temp_dir,
                        "bundle": {
                            "bundle_kind": "full_workbench_bundle",
                            "system_id": "custom_reverse_control_v1",
                            "system_title": "Custom reverse control",
                            "ready_for_spec_build": True,
                            "selected_scenario_id": "ab_pressure_ramp",
                            "selected_fault_mode_id": "pressure_sensor_bias_low",
                            "next_actions": [],
                        },
                        "files": {
                            "bundle_json": None,
                            "summary_markdown": None,
                            "intake_assessment_json": None,
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
                            "archive_summary_markdown": None,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "invalid workbench archive manifest"):
                load_workbench_archive_manifest(manifest_path)

    def test_archive_manifest_validation_reports_invalid_self_check_metadata(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            manifest = load_workbench_archive_manifest(archive.manifest_json_path)
            manifest["$schema"] = "https://well-harness.local/json_schema/wrong.schema.json"
            manifest["self_check"] = {
                "command": "",
                "working_directory": "repository_root",
            }

            issues = validate_workbench_archive_manifest(manifest, manifest_path=archive.manifest_json_path)

        self.assertIn("$schema must be", " ".join(issues))
        self.assertIn("self_check.command must be a non-empty string", " ".join(issues))
        self.assertIn("self_check.working_directory must be 'archive_dir'", " ".join(issues))

    def test_archive_manifest_schema_documents_generated_manifest_shape(self):
        schema = load_archive_manifest_schema()

        self.assertEqual(
            "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
            schema["properties"]["$schema"]["const"],
        )
        self.assertEqual("well-harness-workbench-archive-manifest", schema["properties"]["kind"]["const"])
        self.assertEqual(1, schema["properties"]["version"]["const"])
        self.assertEqual(
            "python3 -m well_harness.cli archive-manifest .",
            schema["$defs"]["selfCheck"]["properties"]["command"]["const"],
        )
        self.assertEqual(
            "archive_dir",
            schema["$defs"]["selfCheck"]["properties"]["working_directory"]["const"],
        )

    def test_optional_jsonschema_validates_generated_archive_manifest_when_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional dependency jsonschema is not installed")

        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        schema = load_archive_manifest_schema()
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            manifest = load_workbench_archive_manifest(archive.manifest_json_path)
            errors = sorted(
                validator.iter_errors(manifest),
                key=lambda error: tuple(error.absolute_path),
            )

        self.assertEqual([], errors, "\n".join(error.message for error in errors[:10]))

    def test_cli_archive_manifest_validates_generated_archive(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)

            exit_code, payload = run_json_cli(
                [
                    "archive-manifest",
                    archive.manifest_json_path,
                    "--format",
                    "json",
                ]
            )

        self.assertEqual(0, exit_code)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["issues"])
        self.assertEqual(
            "https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json",
            payload["schema"],
        )
        self.assertEqual("well-harness-workbench-archive-manifest", payload["kind"])
        self.assertEqual(".", payload["archive_dir"])
        self.assertEqual("custom_reverse_control_v1", payload["bundle"]["system_id"])
        self.assertEqual("python3 -m well_harness.cli archive-manifest .", payload["self_check"]["command"])
        self.assertEqual("bundle.json", payload["files"]["bundle_json"])
        self.assertEqual("README.md", payload["files"]["summary_markdown"])
        self.assertEqual(str(Path(archive.bundle_json_path)), payload["resolved_files"]["bundle_json"])
        self.assertEqual(str(Path(archive.summary_markdown_path)), payload["resolved_files"]["summary_markdown"])
        self.assertGreaterEqual(payload["file_count"], 5)

    def test_cli_archive_manifest_accepts_archive_directory_and_prints_restore_targets(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)

            json_exit_code, payload = run_json_cli(
                [
                    "archive-manifest",
                    archive.archive_dir,
                    "--format",
                    "json",
                ]
            )
            text_exit_code, text = run_text_cli(["archive-manifest", archive.archive_dir])

        self.assertEqual(0, json_exit_code)
        self.assertTrue(payload["valid"])
        self.assertEqual(str(Path(archive.manifest_json_path)), payload["manifest_path"])
        self.assertEqual(0, text_exit_code)
        self.assertIn("restore_targets:", text)
        self.assertIn("schema: https://well-harness.local/json_schema/workbench_archive_manifest_v1.schema.json", text)
        self.assertIn("archive_summary_markdown:", text)
        self.assertIn("self_check: python3 -m well_harness.cli archive-manifest .", text)

    def test_archive_readme_self_check_command_runs_from_archive_directory(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        env = dict(os.environ)
        src_path = str(PROJECT_ROOT / "src")
        existing_pythonpath = env.get("PYTHONPATH")
        env["PYTHONPATH"] = src_path if not existing_pythonpath else f"{src_path}{os.pathsep}{existing_pythonpath}"

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            archive_dir = Path(archive.archive_dir)
            moved_archive_dir = Path(temp_dir) / "moved-archive"
            archive_dir.rename(moved_archive_dir)

            result = subprocess.run(
                [sys.executable, "-m", "well_harness.cli", "archive-manifest", "."],
                cwd=moved_archive_dir,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(0, result.returncode)
        self.assertIn("archive_manifest: OK", result.stdout)
        self.assertIn("self_check: python3 -m well_harness.cli archive-manifest .", result.stdout)

    def test_cli_archive_manifest_reports_invalid_generated_archive(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            Path(archive.bundle_json_path).unlink()

            exit_code, payload = run_json_cli(
                [
                    "archive-manifest",
                    archive.manifest_json_path,
                    "--format",
                    "json",
                ]
            )

        self.assertEqual(1, exit_code)
        self.assertFalse(payload["valid"])
        self.assertIn("files.bundle_json does not point to an existing file", " ".join(payload["issues"]))

    def test_archive_workbench_bundle_can_capture_browser_handoff_snapshot(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        handoff = {
            "badgeText": "可交接",
            "system": "custom_reverse_control_v1",
            "packet": "2 docs / 4 logic / 1 faults",
            "result": "通过 / ab_pressure_ramp",
            "archive": "已留档",
            "workspace": "3 个 packet 版本 / 2 个结果",
            "note": "Archive this ready result and hand it to the next engineer.",
        }

        markdown = render_workbench_bundle_markdown(bundle, workspace_handoff=handoff)
        self.assertIn("## Browser Workspace Handoff", markdown)
        self.assertIn("Archive this ready result", markdown)

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir, workspace_handoff=handoff)

            self.assertTrue(Path(archive.manifest_json_path).exists())
            self.assertTrue(Path(archive.workspace_handoff_json_path).exists())
            saved_handoff = json.loads(Path(archive.workspace_handoff_json_path).read_text(encoding="utf-8"))
            self.assertEqual("可交接", saved_handoff["badgeText"])
            saved_summary = Path(archive.summary_markdown_path).read_text(encoding="utf-8")
            self.assertIn("## Browser Workspace Handoff", saved_summary)
            self.assertIn("Archive this ready result", saved_summary)
            saved_manifest = json.loads(Path(archive.manifest_json_path).read_text(encoding="utf-8"))
            self.assertEqual("workspace_handoff.json", saved_manifest["files"]["workspace_handoff_json"])

    def test_archive_workbench_bundle_can_capture_browser_workspace_snapshot(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        workspace_snapshot = {
            "kind": "well-harness-workbench-browser-workspace",
            "version": 2,
            "packetRevisionHistory": [{"id": "workbench-packet-revision-1", "title": "载入参考样例"}],
            "runHistory": [{"id": "workbench-history-1", "title": "一键通过验收"}],
            "handoff": {
                "badgeText": "可交接",
                "note": "Preserve this exact ready workspace for replay and handoff.",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir, workspace_snapshot=workspace_snapshot)

            self.assertTrue(Path(archive.manifest_json_path).exists())
            self.assertTrue(Path(archive.workspace_snapshot_json_path).exists())
            saved_snapshot = json.loads(Path(archive.workspace_snapshot_json_path).read_text(encoding="utf-8"))
            self.assertEqual(2, saved_snapshot["version"])
            self.assertEqual("可交接", saved_snapshot["handoff"]["badgeText"])
            saved_manifest = json.loads(Path(archive.manifest_json_path).read_text(encoding="utf-8"))
            self.assertEqual("workspace_snapshot.json", saved_manifest["files"]["workspace_snapshot_json"])

    def test_archive_manifest_remains_valid_after_archive_directory_is_moved(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)
            archive_dir = Path(archive.archive_dir)
            moved_archive_dir = Path(temp_dir) / "portable-archive"
            archive_dir.rename(moved_archive_dir)
            moved_manifest_path = moved_archive_dir / "archive_manifest.json"

            manifest = load_workbench_archive_manifest(moved_manifest_path)

        self.assertEqual(".", manifest["archive_dir"])
        self.assertEqual("bundle.json", manifest["files"]["bundle_json"])

    def test_archive_manifest_resolves_files_and_workspace_metadata_after_move(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        handoff = {
            "badgeText": "可交接",
            "system": "custom_reverse_control_v1",
            "packet": "2 docs / 4 logic / 1 faults",
            "result": "通过 / ab_pressure_ramp",
            "archive": "已留档",
            "workspace": "3 个 packet 版本 / 2 个结果",
            "note": "Portable archive handoff note.",
        }
        workspace_snapshot = {
            "kind": "well-harness-workbench-browser-workspace",
            "version": 2,
            "packetRevisionHistory": [{"id": "workbench-packet-revision-1", "title": "载入参考样例"}],
            "runHistory": [{"id": "workbench-history-1", "title": "一键通过验收"}],
            "handoff": {
                "badgeText": "可交接",
                "note": "Portable archive handoff note.",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(
                bundle,
                temp_dir,
                workspace_handoff=handoff,
                workspace_snapshot=workspace_snapshot,
            )
            archive_dir = Path(archive.archive_dir)
            moved_archive_dir = Path(temp_dir) / "portable-archive"
            archive_dir.rename(moved_archive_dir)
            moved_manifest_path = moved_archive_dir / "archive_manifest.json"

            manifest = load_workbench_archive_manifest(moved_manifest_path)
            resolved_files = resolve_workbench_archive_manifest_files(manifest, manifest_path=moved_manifest_path)
            restored_handoff = load_workbench_archive_workspace_handoff(moved_manifest_path)
            restored_snapshot = load_workbench_archive_workspace_snapshot(moved_manifest_path)

        self.assertEqual(str((moved_archive_dir / "bundle.json").resolve()), resolved_files["bundle_json"])
        self.assertEqual(
            str((moved_archive_dir / "workspace_handoff.json").resolve()),
            resolved_files["workspace_handoff_json"],
        )
        self.assertEqual("Portable archive handoff note.", restored_handoff["note"])
        self.assertEqual(2, restored_snapshot["version"])

    def test_load_workbench_archive_restore_payload_reopens_moved_archive(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )
        handoff = {
            "badgeText": "可交接",
            "system": "custom_reverse_control_v1",
            "packet": "2 docs / 4 logic / 1 faults",
            "result": "通过 / ab_pressure_ramp",
            "archive": "已留档",
            "workspace": "3 个 packet 版本 / 2 个结果",
            "note": "Portable archive handoff note.",
        }
        workspace_snapshot = {
            "kind": "well-harness-workbench-browser-workspace",
            "version": 2,
            "packetRevisionHistory": [{"id": "workbench-packet-revision-1", "title": "载入参考样例"}],
            "runHistory": [{"id": "workbench-history-1", "title": "一键通过验收"}],
            "handoff": {
                "badgeText": "可交接",
                "note": "Portable archive handoff note.",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(
                bundle,
                temp_dir,
                workspace_handoff=handoff,
                workspace_snapshot=workspace_snapshot,
            )
            archive_dir = Path(archive.archive_dir)
            moved_archive_dir = Path(temp_dir) / "portable-archive"
            archive_dir.rename(moved_archive_dir)
            moved_manifest_path = moved_archive_dir / "archive_manifest.json"

            restore_payload = load_workbench_archive_restore_payload(moved_archive_dir)

        self.assertEqual(str(moved_manifest_path.resolve()), restore_payload["manifest_path"])
        self.assertEqual(str(moved_archive_dir.resolve()), restore_payload["archive_dir"])
        self.assertEqual("well-harness-workbench-archive-manifest", restore_payload["manifest"]["kind"])
        self.assertEqual("full_workbench_bundle", restore_payload["bundle"]["bundle_kind"])
        self.assertEqual(
            str((moved_archive_dir / "bundle.json").resolve()),
            restore_payload["resolved_files"]["bundle_json"],
        )
        self.assertEqual("Portable archive handoff note.", restore_payload["workspace_handoff"]["note"])
        self.assertEqual(2, restore_payload["workspace_snapshot"]["version"])

    def test_load_workbench_archive_bundle_payload_returns_bundle_json_object(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            archive = archive_workbench_bundle(bundle, temp_dir)

            bundle_payload = load_workbench_archive_bundle_payload(archive.manifest_json_path)

        self.assertEqual("full_workbench_bundle", bundle_payload["bundle_kind"])
        self.assertTrue(bundle_payload["ready_for_spec_build"])

    def test_archive_workbench_bundle_avoids_name_collisions_within_same_second(self):
        bundle = build_workbench_bundle(
            load_intake_packet(SYSTEM_INTAKE_PACKET_PATH),
            confirmed_root_cause="Pressure sensor bias was confirmed during troubleshooting.",
            repair_action="Recalibrated the sensor path.",
            validation_after_fix="Acceptance replay completed after the repair.",
            residual_risk="Watch for future sensor drift.",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch("well_harness.workbench_bundle._archive_timestamp", return_value="20260411T080000Z"):
                archive_one = archive_workbench_bundle(bundle, temp_dir)
                archive_two = archive_workbench_bundle(bundle, temp_dir)

            self.assertTrue(Path(archive_one.archive_dir).exists())
            self.assertTrue(Path(archive_two.archive_dir).exists())
            self.assertNotEqual(archive_one.archive_dir, archive_two.archive_dir)
            self.assertTrue(Path(archive_two.archive_dir).name.endswith("-2"))

    def test_cli_bundle_outputs_json_for_ready_packet(self):
        exit_code, payload = run_json_cli(
            [
                "bundle",
                str(SYSTEM_INTAKE_PACKET_PATH),
                "--format",
                "json",
                "--confirmed-root-cause",
                "Pressure sensor bias was confirmed during troubleshooting.",
                "--repair-action",
                "Recalibrated the sensor path.",
                "--validation-after-fix",
                "Acceptance replay completed after the repair.",
                "--residual-risk",
                "Watch for future sensor drift.",
            ]
        )

        self.assertEqual(0, exit_code)
        self.assertEqual("full_workbench_bundle", payload["bundle_kind"])
        self.assertTrue(payload["ready_for_spec_build"])
        self.assertEqual("ab_pressure_ramp", payload["selected_scenario_id"])
        self.assertEqual("pressure_sensor_bias_low", payload["selected_fault_mode_id"])
        self.assertEqual("resolved", payload["knowledge_artifact"]["status"])

    def test_cli_bundle_outputs_follow_up_for_blocked_packet(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_path = Path(temp_dir) / "blocked_packet.json"
            packet_path.write_text(json.dumps(intake_template_payload(), ensure_ascii=False, indent=2), encoding="utf-8")

            exit_code, payload = run_json_cli(["bundle", str(packet_path), "--format", "json"])

        self.assertEqual(1, exit_code)
        self.assertEqual("clarification_follow_up", payload["bundle_kind"])
        self.assertFalse(payload["ready_for_spec_build"])
        self.assertEqual("blocked_by_schema_and_clarifications", payload["clarification_brief"]["gate_status"])

    def test_cli_bundle_can_archive_blocked_follow_up_bundle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_path = Path(temp_dir) / "blocked_packet.json"
            packet_path.write_text(json.dumps(intake_template_payload(), ensure_ascii=False, indent=2), encoding="utf-8")

            exit_code, payload = run_json_cli(
                [
                    "bundle",
                    str(packet_path),
                    "--format",
                    "json",
                    "--archive-dir",
                    temp_dir,
                ]
            )

            self.assertEqual(1, exit_code)
            self.assertEqual("clarification_follow_up", payload["bundle_kind"])
            archive = payload["archive"]
            self.assertTrue(Path(archive["archive_dir"]).exists())
            self.assertTrue(Path(archive["bundle_json_path"]).exists())
            self.assertTrue(Path(archive["summary_markdown_path"]).exists())
            self.assertIsNone(archive["playback_report_json_path"])
            summary_text = Path(archive["summary_markdown_path"]).read_text(encoding="utf-8")
            self.assertIn("## Clarification Gate", summary_text)
