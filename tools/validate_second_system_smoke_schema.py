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


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "second_system_smoke_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate second-system-smoke payloads."
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


def run_second_system_smoke_json(extra_args: list[str] | None = None) -> tuple[int, dict]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = well_harness_main(["second-system-smoke", *(extra_args or []), "--format", "json"])
    try:
        payload = json.loads(buffer.getvalue())
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse second-system smoke JSON: {exc}") from exc
    return exit_code, payload


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": relative_path(SCHEMA_PATH),
        "status": status,
    }


def make_result(payload: dict | None, validation_status: str, **extra_fields) -> dict:
    result = {
        "adapter_id": payload.get("adapter_id") if isinstance(payload, dict) else None,
        "bundle_kind": payload.get("bundle_kind") if isinstance(payload, dict) else None,
        "case": "default_cli_second_system_smoke",
        "proof_mode": payload.get("proof_mode") if isinstance(payload, dict) else None,
        "smoke_passed": payload.get("smoke_passed") if isinstance(payload, dict) else None,
        "system_id": payload.get("system_id") if isinstance(payload, dict) else None,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_smoke_contract(
    payload: dict,
    *,
    expected_values: dict[str, object],
    required_evidence_steps: tuple[str, ...],
) -> tuple[str, ...]:
    issues: list[str] = []
    for field_name, expected_value in expected_values.items():
        if payload.get(field_name) != expected_value:
            issues.append(f"expected {field_name} {expected_value!r} but got {payload.get(field_name)!r}")
    for evidence_step in required_evidence_steps:
        if evidence_step not in payload.get("evidence_steps", []):
            issues.append(f"expected evidence_steps to include {evidence_step!r}")
    return tuple(issues)


def validate_second_system_smoke_payloads() -> tuple[int, dict, list[str]]:
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
    cases = (
        (
            "default_cli_second_system_smoke",
            [],
            {
                "adapter_id": "landing-gear-controller-adapter",
                "bundle_kind": "adapter_runtime_proof",
                "knowledge_status": "resolved",
                "packet_path": None,
                "proof_mode": "truth_adapter",
                "selected_fault_mode_id": "hydraulic_pressure_bias_low",
                "selected_scenario_id": "handle_down_nominal_extension",
                "smoke_passed": True,
                "system_id": "minimal_landing_gear_extension",
            },
            (
                "adapter_metadata",
                "control_system_spec",
                "runtime_truth_alignment",
                "playback_report",
                "fault_diagnosis_report",
                "knowledge_artifact",
            ),
        ),
        (
            "legacy_intake_packet_second_system_smoke",
            ["--proof-mode", "intake-packet"],
            {
                "adapter_id": None,
                "bundle_kind": "full_workbench_bundle",
                "knowledge_status": "resolved",
                "proof_mode": "intake_packet",
                "selected_fault_mode_id": "pressure_sensor_bias_low",
                "selected_scenario_id": "ab_pressure_ramp",
                "smoke_passed": True,
                "system_id": "custom_reverse_control_v1",
            },
            (
                "intake_assessment",
                "clarification_brief",
                "playback_report",
                "fault_diagnosis_report",
                "knowledge_artifact",
            ),
        ),
    )

    for case_name, extra_args, expected_values, required_evidence_steps in cases:
        try:
            exit_code, payload = run_second_system_smoke_json(extra_args)
        except ValueError as exc:
            report["failure_kind"] = "payload_parse"
            report["results"].append(make_result(None, "fail", case=case_name, error_count=1, errors=[str(exc)]))
            report["status"] = "fail"
            return 1, report, [f"FAIL {case_name}: {exc}"]

        if exit_code != 0:
            report["failure_kind"] = "cli_exit"
            report["results"].append(
                make_result(
                    payload,
                    "fail",
                    case=case_name,
                    error_count=1,
                    errors=[f"second-system-smoke CLI exited with status {exit_code}"],
                )
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case_name}: CLI exited with status {exit_code}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            formatted_errors = [format_validation_error(error) for error in errors[:10]]
            report["failure_kind"] = "schema_validation"
            report["results"].append(
                make_result(payload, "fail", case=case_name, error_count=len(errors), errors=formatted_errors)
            )
            report["status"] = "fail"
            text_lines = [f"FAIL {case_name}: second-system smoke schema validation errors"]
            for formatted_error in formatted_errors:
                text_lines.append(f"  - {formatted_error}")
            return 1, report, text_lines

        contract_issues = validate_smoke_contract(
            payload,
            expected_values=expected_values,
            required_evidence_steps=required_evidence_steps,
        )
        if contract_issues:
            report["failure_kind"] = "smoke_contract_mismatch"
            report["results"].append(
                make_result(payload, "fail", case=case_name, error_count=len(contract_issues), errors=list(contract_issues))
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case_name}: {'; '.join(contract_issues)}"]

        report["results"].append(make_result(payload, "pass", case=case_name, error_count=0, errors=[]))

    text_lines = [
        "OK default_cli_second_system_smoke: validated system=minimal_landing_gear_extension bundle=adapter_runtime_proof",
        "OK legacy_intake_packet_second_system_smoke: validated system=custom_reverse_control_v1 bundle=full_workbench_bundle",
        f"PASS: validated {len(cases)} second-system smoke payloads against {relative_path(SCHEMA_PATH)}",
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_second_system_smoke_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_second_system_smoke_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
