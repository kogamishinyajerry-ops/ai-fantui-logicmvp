from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.document_intake import intake_packet_from_dict, intake_template_payload, load_intake_packet
from well_harness.workbench_bundle import build_workbench_bundle


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "workbench_bundle_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate workbench-bundle payloads."
)
READY_BUNDLE_KWARGS = {
    "confirmed_root_cause": "Pressure sensor bias was confirmed against playback evidence.",
    "repair_action": "Recalibrated the pressure sensor and replayed the acceptance scenario.",
    "validation_after_fix": "Scenario replay completed with the actuator command restored.",
    "residual_risk": "Residual drift risk remains low under normal monitoring.",
}
CASES = (
    {
        "name": "fixture_ready_packet",
        "packet_path": PROJECT_ROOT / "tests" / "fixtures" / "system_intake_packet_v1.json",
        "expected_system_id": "custom_reverse_control_v1",
        "expected_bundle_kind": "full_workbench_bundle",
        "expected_ready_for_spec_build": True,
    },
    {
        "name": "reference_ready_packet",
        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
        "expected_system_id": "custom_reverse_control_v1",
        "expected_bundle_kind": "full_workbench_bundle",
        "expected_ready_for_spec_build": True,
    },
    {
        "name": "template_blocked_packet",
        "packet_path": None,
        "expected_system_id": "new_control_system_id",
        "expected_bundle_kind": "clarification_follow_up",
        "expected_ready_for_spec_build": False,
    },
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def relative_path(path: Path | None) -> str | None:
    if path is None:
        return None
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


def build_case_payload(case: dict[str, Any]) -> dict:
    packet_path = case["packet_path"]
    if packet_path is None:
        packet = intake_packet_from_dict(intake_template_payload())
        return build_workbench_bundle(packet).to_dict()

    packet = load_intake_packet(packet_path)
    return build_workbench_bundle(packet, **READY_BUNDLE_KWARGS).to_dict()


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": str(relative_path(SCHEMA_PATH)),
        "status": status,
    }


def make_result(case: dict[str, Any], payload: dict | None, validation_status: str, **extra_fields) -> dict:
    result = {
        "bundle_kind": payload.get("bundle_kind") if isinstance(payload, dict) else None,
        "case": case["name"],
        "packet_path": relative_path(case["packet_path"]),
        "ready_for_spec_build": payload.get("ready_for_spec_build") if isinstance(payload, dict) else None,
        "system_id": payload.get("system_id") if isinstance(payload, dict) else None,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_case_contract(case: dict[str, Any], payload: dict) -> tuple[str, ...]:
    issues: list[str] = []
    for field_name, expected_value in (
        ("system_id", case["expected_system_id"]),
        ("bundle_kind", case["expected_bundle_kind"]),
        ("ready_for_spec_build", case["expected_ready_for_spec_build"]),
    ):
        if payload.get(field_name) != expected_value:
            issues.append(f"expected {field_name} {expected_value!r} but got {payload.get(field_name)!r}")

    nested_payloads = (
        payload.get("playback_report"),
        payload.get("fault_diagnosis_report"),
        payload.get("knowledge_artifact"),
    )
    if case["expected_ready_for_spec_build"] and any(nested_payload is None for nested_payload in nested_payloads):
        issues.append("ready bundle must include playback, diagnosis, and knowledge payloads")
    if not case["expected_ready_for_spec_build"] and any(nested_payload is not None for nested_payload in nested_payloads):
        issues.append("blocked bundle must not include playback, diagnosis, or knowledge payloads")
    return tuple(issues)


def validate_workbench_bundle_payloads() -> tuple[int, dict, list[str]]:
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
        try:
            payload = build_case_payload(case)
        except Exception as exc:
            report["failure_kind"] = "payload_build"
            report["results"].append(make_result(case, None, "fail", error_count=1, errors=[str(exc)]))
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: unable to build workbench bundle payload: {exc}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            formatted_errors = [format_validation_error(error) for error in errors[:10]]
            report["failure_kind"] = "schema_validation"
            report["results"].append(make_result(case, payload, "fail", error_count=len(errors), errors=formatted_errors))
            report["status"] = "fail"
            text_lines.append(f"FAIL {case['name']}: workbench bundle schema validation errors")
            for formatted_error in formatted_errors:
                text_lines.append(f"  - {formatted_error}")
            return 1, report, text_lines

        contract_issues = validate_case_contract(case, payload)
        if contract_issues:
            report["failure_kind"] = "bundle_contract_mismatch"
            report["results"].append(
                make_result(case, payload, "fail", error_count=len(contract_issues), errors=list(contract_issues))
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: {'; '.join(contract_issues)}"]

        report["results"].append(make_result(case, payload, "pass", error_count=0, errors=[]))
        text_lines.append(
            "OK "
            f"{case['name']}: validated workbench bundle "
            f"bundle_kind={payload['bundle_kind']} packet={relative_path(case['packet_path']) or 'template'}"
        )

    text_lines.append(
        f"PASS: validated {len(CASES)} workbench bundle payloads against {relative_path(SCHEMA_PATH)}"
    )
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_workbench_bundle_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_workbench_bundle_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
