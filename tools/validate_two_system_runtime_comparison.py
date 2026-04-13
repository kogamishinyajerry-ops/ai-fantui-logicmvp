from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.cli import main as well_harness_main


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "two_system_runtime_comparison_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate two-system runtime comparison payloads."
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


def run_two_system_runtime_comparison_json() -> tuple[int, dict]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = well_harness_main(["two-system-runtime-comparison", "--format", "json"])
    try:
        payload = json.loads(buffer.getvalue())
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse two-system runtime comparison JSON: {exc}") from exc
    return exit_code, payload


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": relative_path(SCHEMA_PATH),
        "status": status,
    }


def make_result(validation_status: str, **extra_fields) -> dict:
    result = {
        "case": "reference_vs_landing_gear_runtime_comparison",
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_contract(payload: dict) -> tuple[str, ...]:
    issues: list[str] = []
    expected_values = {
        "both_support_adapter_truth": True,
        "both_reach_playback_completion": True,
        "both_block_fault_path": True,
        "both_emit_resolved_knowledge": True,
    }
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            issues.append(f"expected {field_name} {expected_value!r} but got {payload.get(field_name)!r}")
    primary = payload.get("primary_system", {})
    comparison = payload.get("comparison_system", {})
    if primary.get("system_id") != "reference_thrust_reverser_deploy":
        issues.append(f"expected primary_system.system_id 'reference_thrust_reverser_deploy' but got {primary.get('system_id')!r}")
    if comparison.get("system_id") != "minimal_landing_gear_extension":
        issues.append(f"expected comparison_system.system_id 'minimal_landing_gear_extension' but got {comparison.get('system_id')!r}")
    if primary.get("knowledge_status") != "resolved":
        issues.append(f"expected primary_system.knowledge_status 'resolved' but got {primary.get('knowledge_status')!r}")
    if comparison.get("knowledge_status") != "resolved":
        issues.append(f"expected comparison_system.knowledge_status 'resolved' but got {comparison.get('knowledge_status')!r}")
    shared_contracts = payload.get("shared_contracts", [])
    for contract_name in (
        "controller_truth_metadata",
        "control_system_spec",
        "playback_report",
        "fault_diagnosis_report",
        "knowledge_artifact",
    ):
        if contract_name not in shared_contracts:
            issues.append(f"expected shared_contracts to include {contract_name!r}")
    return tuple(issues)


def validate_two_system_runtime_comparison() -> tuple[int, dict, list[str]]:
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
        return 1, report, [f"FAIL schema: unable to load {relative_path(SCHEMA_PATH)}: {exc}"]

    try:
        exit_code, payload = run_two_system_runtime_comparison_json()
    except ValueError as exc:
        report["failure_kind"] = "payload_parse"
        report["results"].append(make_result("fail", error_count=1, errors=[str(exc)]))
        report["status"] = "fail"
        return 1, report, [f"FAIL reference_vs_landing_gear_runtime_comparison: {exc}"]

    if exit_code != 0:
        report["failure_kind"] = "cli_exit"
        report["results"].append(
            make_result(
                "fail",
                error_count=1,
                errors=[f"two-system-runtime-comparison CLI exited with status {exit_code}"],
            )
        )
        report["status"] = "fail"
        return 1, report, [f"FAIL reference_vs_landing_gear_runtime_comparison: CLI exited with status {exit_code}"]

    validator = Draft202012Validator(schema_document)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if errors:
        formatted_errors = [format_validation_error(error) for error in errors[:10]]
        report["failure_kind"] = "schema_validation"
        report["results"].append(
            make_result("fail", error_count=len(errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        text_lines = ["FAIL reference_vs_landing_gear_runtime_comparison: schema validation errors"]
        for formatted_error in formatted_errors:
            text_lines.append(f"  - {formatted_error}")
        return 1, report, text_lines

    contract_issues = validate_contract(payload)
    if contract_issues:
        report["failure_kind"] = "comparison_contract_mismatch"
        report["results"].append(
            make_result("fail", error_count=len(contract_issues), errors=list(contract_issues))
        )
        report["status"] = "fail"
        return 1, report, [f"FAIL reference_vs_landing_gear_runtime_comparison: {'; '.join(contract_issues)}"]

    report["results"].append(
        make_result(
            "pass",
            error_count=0,
            errors=[],
            primary_system_id=payload["primary_system"]["system_id"],
            comparison_system_id=payload["comparison_system"]["system_id"],
        )
    )
    text_lines = [
        "OK reference_vs_landing_gear_runtime_comparison: validated adapter-backed runtime comparison for reference thrust-reverser and landing gear",
        f"PASS: validated 1 two-system runtime comparison payload against {relative_path(SCHEMA_PATH)}",
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_two_system_runtime_comparison.py [--format text|json]")


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

    exit_code, report, text_lines = validate_two_system_runtime_comparison()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
