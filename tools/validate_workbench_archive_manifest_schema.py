from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.document_intake import intake_packet_from_dict, intake_template_payload, load_intake_packet
from well_harness.workbench_bundle import (
    archive_workbench_bundle,
    build_workbench_bundle,
    load_workbench_archive_manifest,
    validate_workbench_archive_manifest,
)


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "workbench_archive_manifest_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate workbench-archive-manifest payloads."
)
READY_BUNDLE_KWARGS = {
    "confirmed_root_cause": "Pressure sensor bias was confirmed against playback evidence.",
    "repair_action": "Recalibrated the pressure sensor and replayed the acceptance scenario.",
    "validation_after_fix": "Scenario replay completed with the actuator command restored.",
    "residual_risk": "Residual drift risk remains low under normal monitoring.",
}
CASES = (
    {
        "name": "ready_archive_manifest",
        "packet_path": PROJECT_ROOT / "tests" / "fixtures" / "system_intake_packet_v1.json",
        "expected_bundle_kind": "full_workbench_bundle",
        "expected_ready_for_spec_build": True,
        "workspace_handoff": {"note": "ready archive handoff"},
        "workspace_snapshot": {"current_view": "ready"},
    },
    {
        "name": "blocked_archive_manifest",
        "packet_path": None,
        "expected_bundle_kind": "clarification_follow_up",
        "expected_ready_for_spec_build": False,
        "workspace_handoff": None,
        "workspace_snapshot": None,
    },
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def build_case_bundle(case: dict[str, Any]):
    if case["packet_path"] is None:
        packet = intake_packet_from_dict(intake_template_payload())
        return build_workbench_bundle(packet)
    packet = load_intake_packet(case["packet_path"])
    return build_workbench_bundle(packet, **READY_BUNDLE_KWARGS)


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": relative_path(SCHEMA_PATH),
        "status": status,
    }


def make_result(case: dict[str, Any], manifest: dict | None, validation_status: str, **extra_fields) -> dict:
    bundle = manifest.get("bundle") if isinstance(manifest, dict) and isinstance(manifest.get("bundle"), dict) else {}
    result = {
        "bundle_kind": bundle.get("bundle_kind"),
        "case": case["name"],
        "ready_for_spec_build": bundle.get("ready_for_spec_build"),
        "system_id": bundle.get("system_id"),
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_case_contract(case: dict[str, Any], manifest: dict) -> tuple[str, ...]:
    issues: list[str] = []
    bundle = manifest.get("bundle") if isinstance(manifest.get("bundle"), dict) else {}
    if bundle.get("bundle_kind") != case["expected_bundle_kind"]:
        issues.append(f"expected bundle_kind {case['expected_bundle_kind']!r} but got {bundle.get('bundle_kind')!r}")
    if bundle.get("ready_for_spec_build") != case["expected_ready_for_spec_build"]:
        issues.append(
            "expected ready_for_spec_build "
            f"{case['expected_ready_for_spec_build']!r} but got {bundle.get('ready_for_spec_build')!r}"
        )
    files = manifest.get("files") if isinstance(manifest.get("files"), dict) else {}
    if files.get("bundle_json") != "bundle.json":
        issues.append(f"expected files.bundle_json to be 'bundle.json' but got {files.get('bundle_json')!r}")
    if files.get("summary_markdown") != "README.md":
        issues.append(f"expected files.summary_markdown to be 'README.md' but got {files.get('summary_markdown')!r}")
    if case["workspace_handoff"] is not None and files.get("workspace_handoff_json") != "workspace_handoff.json":
        issues.append("ready archive with handoff must include workspace_handoff.json")
    if case["workspace_snapshot"] is not None and files.get("workspace_snapshot_json") != "workspace_snapshot.json":
        issues.append("ready archive with snapshot must include workspace_snapshot.json")
    return tuple(issues)


def validate_workbench_archive_manifest_payloads() -> tuple[int, dict, list[str]]:
    report = make_report()

    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        report["status"] = "skip"
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        report["status"] = "skip"
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        schema_document = load_json(SCHEMA_PATH)
        Draft202012Validator.check_schema(schema_document)
    except Exception as exc:
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL schema: unable to use {relative_path(SCHEMA_PATH)}: {exc}"]

    validator = Draft202012Validator(schema_document)
    text_lines: list[str] = []

    for case in CASES:
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                bundle = build_case_bundle(case)
                archive = archive_workbench_bundle(
                    bundle,
                    temp_dir,
                    workspace_handoff=case["workspace_handoff"],
                    workspace_snapshot=case["workspace_snapshot"],
                )
                manifest = load_workbench_archive_manifest(archive.manifest_json_path)
            except Exception as exc:
                report["failure_kind"] = "payload_build"
                report["results"].append(make_result(case, None, "fail", error_count=1, errors=[str(exc)]))
                report["status"] = "fail"
                return 1, report, [f"FAIL {case['name']}: unable to build archive manifest payload: {exc}"]

            internal_issues = validate_workbench_archive_manifest(
                manifest,
                manifest_path=archive.manifest_json_path,
            )
            if internal_issues:
                report["failure_kind"] = "internal_manifest_validation"
                report["results"].append(
                    make_result(case, manifest, "fail", error_count=len(internal_issues), errors=list(internal_issues))
                )
                report["status"] = "fail"
                return 1, report, [f"FAIL {case['name']}: {'; '.join(internal_issues)}"]

            errors = sorted(
                validator.iter_errors(manifest),
                key=lambda error: tuple(error.absolute_path),
            )
            if errors:
                formatted_errors = [format_validation_error(error) for error in errors[:10]]
                report["failure_kind"] = "schema_validation"
                report["results"].append(
                    make_result(case, manifest, "fail", error_count=len(errors), errors=formatted_errors)
                )
                report["status"] = "fail"
                text_lines.append(f"FAIL {case['name']}: workbench archive manifest schema validation errors")
                for formatted_error in formatted_errors:
                    text_lines.append(f"  - {formatted_error}")
                return 1, report, text_lines

            contract_issues = validate_case_contract(case, manifest)
            if contract_issues:
                report["failure_kind"] = "manifest_contract_mismatch"
                report["results"].append(
                    make_result(case, manifest, "fail", error_count=len(contract_issues), errors=list(contract_issues))
                )
                report["status"] = "fail"
                return 1, report, [f"FAIL {case['name']}: {'; '.join(contract_issues)}"]

            report["results"].append(make_result(case, manifest, "pass", error_count=0, errors=[]))
            text_lines.append(
                "OK "
                f"{case['name']}: validated archive manifest "
                f"bundle_kind={manifest['bundle']['bundle_kind']}"
            )

    text_lines.append(
        f"PASS: validated {len(CASES)} workbench archive manifest payloads against {relative_path(SCHEMA_PATH)}"
    )
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_workbench_archive_manifest_schema.py [--format text|json]")


def emit_report(report: dict, text_lines: list[str], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    for line in text_lines:
        print(line)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        output_format = parse_output_format(argv)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    exit_code, report, text_lines = validate_workbench_archive_manifest_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
