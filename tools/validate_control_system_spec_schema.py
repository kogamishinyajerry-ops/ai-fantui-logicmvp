from __future__ import annotations

import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.cli import main as well_harness_main
from well_harness.document_intake import assess_intake_packet, load_intake_packet


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate control-system-spec payloads."
)
CASES = (
    {
        "name": "reference_cli_spec",
        "source": "cli_spec",
        "packet_path": None,
        "expected_system_id": "reference_thrust_reverser_deploy",
    },
    {
        "name": "fixture_generated_spec",
        "source": "intake_generated_spec",
        "packet_path": PROJECT_ROOT / "tests" / "fixtures" / "system_intake_packet_v1.json",
        "expected_system_id": "custom_reverse_control_v1",
    },
    {
        "name": "reference_packet_generated_spec",
        "source": "intake_generated_spec",
        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
        "expected_system_id": "custom_reverse_control_v1",
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


def run_reference_spec_json() -> tuple[int, dict]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = well_harness_main(["spec", "--format", "json"])
    try:
        payload = json.loads(buffer.getvalue())
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse reference spec JSON: {exc}") from exc
    return exit_code, payload


def run_intake_generated_spec_json(packet_path: Path) -> dict:
    packet = load_intake_packet(packet_path)
    report = assess_intake_packet(packet)
    if not report["ready_for_spec_build"]:
        blockers = report.get("blocking_reasons", [])
        unanswered = report.get("unanswered_clarifications", [])
        raise ValueError(f"packet is not ready for spec build: blockers={blockers} unanswered={unanswered}")
    generated_spec = report.get("generated_workbench_spec")
    if not isinstance(generated_spec, dict):
        raise ValueError("ready intake report did not include generated_workbench_spec")
    return generated_spec


def build_case_payload(case: dict[str, Any]) -> tuple[int, dict]:
    if case["source"] == "cli_spec":
        return run_reference_spec_json()
    return 0, run_intake_generated_spec_json(case["packet_path"])


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": str(relative_path(SCHEMA_PATH)),
        "status": status,
    }


def make_result(case: dict[str, Any], payload: dict | None, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case["name"],
        "packet_path": relative_path(case["packet_path"]),
        "source": case["source"],
        "system_id": payload.get("system_id") if isinstance(payload, dict) else None,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_case_contract(case: dict[str, Any], payload: dict) -> tuple[str, ...]:
    issues: list[str] = []
    if payload.get("system_id") != case["expected_system_id"]:
        issues.append(f"expected system_id {case['expected_system_id']!r} but got {payload.get('system_id')!r}")
    if not payload.get("components"):
        issues.append("control-system spec must include at least one component")
    if not payload.get("logic_nodes"):
        issues.append("control-system spec must include at least one logic node")
    if not payload.get("acceptance_scenarios"):
        issues.append("control-system spec must include at least one acceptance scenario")
    if not payload.get("fault_modes"):
        issues.append("control-system spec must include at least one fault mode")
    return tuple(issues)


def validate_control_system_spec_payloads() -> tuple[int, dict, list[str]]:
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
            exit_code, payload = build_case_payload(case)
        except ValueError as exc:
            report["failure_kind"] = "payload_build"
            report["results"].append(make_result(case, None, "fail", error_count=1, errors=[str(exc)]))
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: {exc}"]

        if exit_code != 0:
            report["failure_kind"] = "cli_exit"
            report["results"].append(
                make_result(case, payload, "fail", error_count=1, errors=[f"spec CLI exited with status {exit_code}"])
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: spec CLI exited with status {exit_code}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            formatted_errors = [format_validation_error(error) for error in errors[:10]]
            report["failure_kind"] = "schema_validation"
            report["results"].append(make_result(case, payload, "fail", error_count=len(errors), errors=formatted_errors))
            report["status"] = "fail"
            text_lines.append(f"FAIL {case['name']}: control-system spec schema validation errors")
            for formatted_error in formatted_errors:
                text_lines.append(f"  - {formatted_error}")
            return 1, report, text_lines

        contract_issues = validate_case_contract(case, payload)
        if contract_issues:
            report["failure_kind"] = "spec_contract_mismatch"
            report["results"].append(
                make_result(case, payload, "fail", error_count=len(contract_issues), errors=list(contract_issues))
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: {'; '.join(contract_issues)}"]

        report["results"].append(make_result(case, payload, "pass", error_count=0, errors=[]))
        text_lines.append(
            "OK "
            f"{case['name']}: validated control-system spec "
            f"system_id={payload['system_id']} packet={relative_path(case['packet_path']) or 'cli'}"
        )

    text_lines.append(
        f"PASS: validated {len(CASES)} control-system spec payloads against {relative_path(SCHEMA_PATH)}"
    )
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_control_system_spec_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_control_system_spec_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
