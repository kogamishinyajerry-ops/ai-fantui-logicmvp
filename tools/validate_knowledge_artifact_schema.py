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


SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "knowledge_artifact_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate knowledge-artifact payloads."
)
DEFAULT_CONFIRMED_ROOT_CAUSE = "Pressure sensor bias was confirmed against playback evidence."
DEFAULT_REPAIR_ACTION = "Recalibrated the pressure sensor and replayed the acceptance scenario."
DEFAULT_VALIDATION_AFTER_FIX = "Scenario replay completed with the actuator command restored."
DEFAULT_RESIDUAL_RISK = "Residual drift risk remains low under normal monitoring."
CASES = (
    {
        "name": "fixture_packet",
        "packet_path": PROJECT_ROOT / "tests" / "fixtures" / "system_intake_packet_v1.json",
        "scenario_id": "ab_pressure_ramp",
        "fault_mode_id": "pressure_sensor_bias_low",
        "sample_period_s": 1.0,
        "expected_system_id": "custom_reverse_control_v1",
    },
    {
        "name": "reference_packet",
        "packet_path": PROJECT_ROOT / "src" / "well_harness" / "reference_packets" / "custom_reverse_control_v1.json",
        "scenario_id": "ab_pressure_ramp",
        "fault_mode_id": "pressure_sensor_bias_low",
        "sample_period_s": 1.0,
        "expected_system_id": "custom_reverse_control_v1",
    },
)


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def relative_path(path: Path) -> Path | str:
    try:
        return path.relative_to(PROJECT_ROOT)
    except ValueError:
        return path


def format_validation_error(error) -> str:
    path = "$"
    for path_part in error.absolute_path:
        if isinstance(path_part, int):
            path += f"[{path_part}]"
        else:
            path += f".{path_part}"
    return f"{path}: {error.message}"


def run_knowledge_json(case: dict) -> tuple[int, dict]:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exit_code = well_harness_main(
            [
                "capture-knowledge",
                str(case["packet_path"]),
                "--scenario",
                str(case["scenario_id"]),
                "--fault-mode",
                str(case["fault_mode_id"]),
                "--confirmed-root-cause",
                DEFAULT_CONFIRMED_ROOT_CAUSE,
                "--repair-action",
                DEFAULT_REPAIR_ACTION,
                "--validation-after-fix",
                DEFAULT_VALIDATION_AFTER_FIX,
                "--residual-risk",
                DEFAULT_RESIDUAL_RISK,
                "--evidence-link",
                f"well-harness://validation/{case['name']}",
                "--sample-period",
                str(case["sample_period_s"]),
                "--format",
                "json",
            ]
        )
    try:
        payload = json.loads(buffer.getvalue())
    except json.JSONDecodeError as exc:
        raise ValueError(f"unable to parse knowledge JSON for case {case['name']!r}: {exc}") from exc
    return exit_code, payload


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": str(relative_path(SCHEMA_PATH)),
        "status": status,
    }


def make_result(case: dict, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case["name"],
        "packet_path": str(relative_path(case["packet_path"])),
        "scenario_id": case["scenario_id"],
        "fault_mode_id": case["fault_mode_id"],
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_knowledge_artifact_payloads() -> tuple[int, dict, list[str]]:
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
            exit_code, payload = run_knowledge_json(case)
        except ValueError as exc:
            report["failure_kind"] = "payload_parse"
            report["results"].append(make_result(case, "fail", error_count=1, errors=[str(exc)]))
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: {exc}"]

        if exit_code != 0:
            report["failure_kind"] = "cli_exit"
            report["results"].append(
                make_result(
                    case,
                    "fail",
                    error_count=1,
                    errors=[f"capture-knowledge CLI exited with status {exit_code}"],
                )
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: capture-knowledge CLI exited with status {exit_code}"]

        errors = sorted(
            validator.iter_errors(payload),
            key=lambda error: tuple(error.absolute_path),
        )
        if errors:
            formatted_errors = [format_validation_error(error) for error in errors[:10]]
            report["failure_kind"] = "schema_validation"
            report["results"].append(make_result(case, "fail", error_count=len(errors), errors=formatted_errors))
            report["status"] = "fail"
            text_lines.append(f"FAIL {case['name']}: knowledge artifact schema validation errors")
            for formatted_error in formatted_errors:
                text_lines.append(f"  - {formatted_error}")
            return 1, report, text_lines

        if payload.get("system_id") != case["expected_system_id"]:
            report["failure_kind"] = "system_id_mismatch"
            report["results"].append(
                make_result(
                    case,
                    "fail",
                    error_count=1,
                    errors=[f"expected system_id {case['expected_system_id']} but got {payload.get('system_id')}"],
                )
            )
            report["status"] = "fail"
            return 1, report, [
                f"FAIL {case['name']}: expected system_id {case['expected_system_id']} but got {payload.get('system_id')}"
            ]

        if payload.get("status") != "resolved":
            report["failure_kind"] = "artifact_status_mismatch"
            report["results"].append(
                make_result(
                    case,
                    "fail",
                    error_count=1,
                    errors=[f"expected resolved status but got {payload.get('status')}"],
                )
            )
            report["status"] = "fail"
            return 1, report, [f"FAIL {case['name']}: expected resolved status but got {payload.get('status')}"]

        report["results"].append(make_result(case, "pass", error_count=0, errors=[]))
        text_lines.append(
            f"OK {case['name']}: validated knowledge artifact packet={relative_path(case['packet_path'])}"
        )

    text_lines.append(
        f"PASS: validated {len(CASES)} knowledge artifact payloads against {relative_path(SCHEMA_PATH)}"
    )
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_knowledge_artifact_schema.py [--format text|json]")


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

    exit_code, report, text_lines = validate_knowledge_artifact_payloads()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
