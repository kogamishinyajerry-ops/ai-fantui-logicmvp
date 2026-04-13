from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.fault_taxonomy import SUPPORTED_FAULT_KINDS, fault_taxonomy_to_dict


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "fault_taxonomy_v1.schema.json"
CONTROL_SYSTEM_SPEC_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate fault-taxonomy payloads."
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


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": relative_path(SCHEMA_PATH),
        "status": status,
    }


def make_result(case: str, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def control_system_spec_fault_kind_enum() -> tuple[str, ...]:
    schema_document = load_json(CONTROL_SYSTEM_SPEC_SCHEMA_PATH)
    enum_values = schema_document["$defs"]["faultKindValue"]["enum"]
    return tuple(enum_values)


def validate_fault_taxonomy_payloads() -> tuple[int, dict, list[str]]:
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
    taxonomy_payload = fault_taxonomy_to_dict()
    errors = sorted(
        validator.iter_errors(taxonomy_payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if errors:
        formatted_errors = [format_validation_error(error) for error in errors[:10]]
        report["failure_kind"] = "schema_validation"
        report["results"].append(
            make_result("fault_taxonomy_payload", "fail", error_count=len(errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        text_lines = ["FAIL fault_taxonomy_payload: fault taxonomy schema validation errors"]
        for formatted_error in formatted_errors:
            text_lines.append(f"  - {formatted_error}")
        return 1, report, text_lines

    payload_fault_kinds = tuple(item["fault_kind"] for item in taxonomy_payload["fault_kinds"])
    if payload_fault_kinds != SUPPORTED_FAULT_KINDS:
        report["failure_kind"] = "taxonomy_payload_mismatch"
        report["results"].append(
            make_result(
                "fault_taxonomy_payload",
                "fail",
                error_count=1,
                errors=[
                    "fault_taxonomy_to_dict fault_kinds do not match SUPPORTED_FAULT_KINDS"
                ],
            )
        )
        report["status"] = "fail"
        return 1, report, ["FAIL fault_taxonomy_payload: payload kinds do not match SUPPORTED_FAULT_KINDS"]

    report["results"].append(
        make_result(
            "fault_taxonomy_payload",
            "pass",
            error_count=0,
            errors=[],
            fault_kind_count=len(payload_fault_kinds),
        )
    )

    try:
        control_schema_enum = control_system_spec_fault_kind_enum()
    except Exception as exc:
        report["failure_kind"] = "control_system_spec_schema_unavailable"
        report["results"].append(
            make_result("control_system_spec_fault_kind_enum", "fail", error_count=1, errors=[str(exc)])
        )
        report["status"] = "fail"
        return 1, report, [f"FAIL control_system_spec_fault_kind_enum: {exc}"]

    if control_schema_enum != SUPPORTED_FAULT_KINDS:
        report["failure_kind"] = "control_system_spec_enum_mismatch"
        report["results"].append(
            make_result(
                "control_system_spec_fault_kind_enum",
                "fail",
                error_count=1,
                errors=[
                    "control_system_spec_v1 faultKindValue enum does not match SUPPORTED_FAULT_KINDS"
                ],
                control_schema_enum=list(control_schema_enum),
                supported_fault_kinds=list(SUPPORTED_FAULT_KINDS),
            )
        )
        report["status"] = "fail"
        return 1, report, [
            "FAIL control_system_spec_fault_kind_enum: control_system_spec_v1 enum does not match taxonomy"
        ]

    report["results"].append(
        make_result(
            "control_system_spec_fault_kind_enum",
            "pass",
            error_count=0,
            errors=[],
            fault_kind_count=len(control_schema_enum),
        )
    )
    text_lines = [
        f"OK fault_taxonomy_payload: validated {len(payload_fault_kinds)} fault kinds",
        (
            "OK control_system_spec_fault_kind_enum: "
            f"{relative_path(CONTROL_SYSTEM_SPEC_SCHEMA_PATH)} matches the published taxonomy"
        ),
        (
            "PASS: validated fault taxonomy payload and control-system fault_kind enum "
            f"against {relative_path(SCHEMA_PATH)}"
        ),
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_fault_taxonomy_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_fault_taxonomy_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
