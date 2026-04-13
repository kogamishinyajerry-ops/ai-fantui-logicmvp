from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.controller_adapter import build_reference_controller_adapter
from well_harness.system_spec import current_reference_workbench_spec


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "controller_truth_adapter_metadata_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate controller-truth-adapter metadata payloads."
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


def validate_controller_truth_adapter_metadata_payloads() -> tuple[int, dict, list[str]]:
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

    adapter = build_reference_controller_adapter()
    metadata_payload = adapter.metadata.to_dict()
    validator = Draft202012Validator(schema_document)
    errors = sorted(
        validator.iter_errors(metadata_payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if errors:
        formatted_errors = [format_validation_error(error) for error in errors[:10]]
        report["failure_kind"] = "schema_validation"
        report["results"].append(
            make_result("reference_adapter_metadata", "fail", error_count=len(errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        text_lines = ["FAIL reference_adapter_metadata: controller truth adapter metadata schema validation errors"]
        for formatted_error in formatted_errors:
            text_lines.append(f"  - {formatted_error}")
        return 1, report, text_lines

    report["results"].append(
        make_result(
            "reference_adapter_metadata",
            "pass",
            adapter_id=metadata_payload["adapter_id"],
            error_count=0,
            errors=[],
            source_of_truth=metadata_payload["source_of_truth"],
            system_id=metadata_payload["system_id"],
        )
    )

    reference_spec = current_reference_workbench_spec()
    if reference_spec.source_of_truth != metadata_payload["source_of_truth"]:
        report["failure_kind"] = "reference_spec_source_of_truth_mismatch"
        report["results"].append(
            make_result(
                "reference_spec_source_of_truth",
                "fail",
                error_count=1,
                errors=[
                    "current_reference_workbench_spec source_of_truth does not match reference adapter metadata"
                ],
                adapter_source_of_truth=metadata_payload["source_of_truth"],
                spec_source_of_truth=reference_spec.source_of_truth,
            )
        )
        report["status"] = "fail"
        return 1, report, [
            "FAIL reference_spec_source_of_truth: reference spec source_of_truth does not match adapter metadata"
        ]

    report["results"].append(
        make_result(
            "reference_spec_source_of_truth",
            "pass",
            adapter_source_of_truth=metadata_payload["source_of_truth"],
            error_count=0,
            errors=[],
            spec_source_of_truth=reference_spec.source_of_truth,
        )
    )

    text_lines = [
        (
            "OK reference_adapter_metadata: "
            f"validated adapter={metadata_payload['adapter_id']} system={metadata_payload['system_id']}"
        ),
        "OK reference_spec_source_of_truth: reference spec remains aligned with adapter metadata",
        (
            "PASS: validated controller truth adapter metadata payload "
            f"against {relative_path(SCHEMA_PATH)}"
        ),
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_controller_truth_adapter_metadata_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_controller_truth_adapter_metadata_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
