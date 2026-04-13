from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.adapters.landing_gear_adapter import (
    LANDING_GEAR_SYSTEM_ID,
    build_landing_gear_controller_adapter,
)


CONTROL_SYSTEM_SPEC_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json"
ADAPTER_METADATA_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "controller_truth_adapter_metadata_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate landing-gear adapter payloads."
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
        "schema_paths": {
            "adapter_metadata": relative_path(ADAPTER_METADATA_SCHEMA_PATH),
            "control_system_spec": relative_path(CONTROL_SYSTEM_SPEC_SCHEMA_PATH),
        },
        "status": status,
    }


def make_result(case: str, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_landing_gear_adapter() -> tuple[int, dict, list[str]]:
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
        metadata_schema = load_json(ADAPTER_METADATA_SCHEMA_PATH)
        spec_schema = load_json(CONTROL_SYSTEM_SPEC_SCHEMA_PATH)
        Draft202012Validator.check_schema(metadata_schema)
        Draft202012Validator.check_schema(spec_schema)
    except Exception as exc:
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL schema: unable to load landing-gear validation schemas: {exc}"]

    adapter = build_landing_gear_controller_adapter()
    metadata_payload = adapter.metadata.to_dict()
    spec_payload = adapter.load_spec()

    metadata_validator = Draft202012Validator(metadata_schema)
    metadata_errors = sorted(
        metadata_validator.iter_errors(metadata_payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if metadata_errors:
        formatted_errors = [format_validation_error(error) for error in metadata_errors[:10]]
        report["failure_kind"] = "metadata_schema_validation"
        report["results"].append(
            make_result("landing_gear_adapter_metadata", "fail", error_count=len(metadata_errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        return 1, report, ["FAIL landing_gear_adapter_metadata:"] + [f"  - {error}" for error in formatted_errors]

    report["results"].append(
        make_result(
            "landing_gear_adapter_metadata",
            "pass",
            adapter_id=metadata_payload["adapter_id"],
            error_count=0,
            errors=[],
            system_id=metadata_payload["system_id"],
        )
    )

    spec_validator = Draft202012Validator(spec_schema)
    spec_errors = sorted(
        spec_validator.iter_errors(spec_payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if spec_errors:
        formatted_errors = [format_validation_error(error) for error in spec_errors[:10]]
        report["failure_kind"] = "spec_schema_validation"
        report["results"].append(
            make_result("landing_gear_control_system_spec", "fail", error_count=len(spec_errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        return 1, report, ["FAIL landing_gear_control_system_spec:"] + [f"  - {error}" for error in formatted_errors]

    report["results"].append(
        make_result(
            "landing_gear_control_system_spec",
            "pass",
            error_count=0,
            errors=[],
            logic_node_count=len(spec_payload["logic_nodes"]),
            system_id=spec_payload["system_id"],
        )
    )

    nominal_evaluation = adapter.evaluate_snapshot(
        {
            "gear_handle_position": "DOWN",
            "hydraulic_pressure_psi": 2850.0,
            "uplock_released": True,
            "gear_position_percent": 100.0,
            "downlock_engaged": True,
        }
    )
    if (
        nominal_evaluation.system_id != LANDING_GEAR_SYSTEM_ID
        or nominal_evaluation.active_logic_node_ids
        != ("lg_l1_handle_and_pressure", "lg_l2_extend_after_uplock_release")
        or not nominal_evaluation.completion_reached
    ):
        report["failure_kind"] = "nominal_runtime_contract"
        report["results"].append(
            make_result(
                "landing_gear_nominal_runtime",
                "fail",
                error_count=1,
                errors=["nominal snapshot did not reach the expected completion state"],
            )
        )
        report["status"] = "fail"
        return 1, report, ["FAIL landing_gear_nominal_runtime: nominal snapshot did not reach expected completion state"]

    report["results"].append(
        make_result(
            "landing_gear_nominal_runtime",
            "pass",
            active_logic_node_ids=list(nominal_evaluation.active_logic_node_ids),
            completion_reached=nominal_evaluation.completion_reached,
            error_count=0,
            errors=[],
        )
    )

    blocked_evaluation = adapter.evaluate_snapshot(
        {
            "gear_handle_position": "DOWN",
            "hydraulic_pressure_psi": 1500.0,
            "uplock_released": False,
            "gear_position_percent": 0.0,
            "downlock_engaged": False,
        }
    )
    if blocked_evaluation.completion_reached or "hydraulic_pressure_psi below 2200.0" not in blocked_evaluation.blocked_reasons:
        report["failure_kind"] = "blocked_runtime_contract"
        report["results"].append(
            make_result(
                "landing_gear_blocked_runtime",
                "fail",
                error_count=1,
                errors=["blocked snapshot did not preserve the expected hydraulic-pressure blocker"],
            )
        )
        report["status"] = "fail"
        return 1, report, [
            "FAIL landing_gear_blocked_runtime: blocked snapshot did not preserve the expected hydraulic-pressure blocker"
        ]

    report["results"].append(
        make_result(
            "landing_gear_blocked_runtime",
            "pass",
            blocked_reasons=list(blocked_evaluation.blocked_reasons),
            completion_reached=blocked_evaluation.completion_reached,
            error_count=0,
            errors=[],
        )
    )

    text_lines = [
        "OK landing_gear_adapter_metadata: validated landing-gear adapter metadata payload",
        "OK landing_gear_control_system_spec: validated landing-gear control-system spec payload",
        "OK landing_gear_nominal_runtime: nominal snapshot reaches completed extension truth",
        "OK landing_gear_blocked_runtime: low-pressure snapshot preserves the expected blocker",
        "PASS: validated landing-gear adapter metadata, spec, and runtime truth contract",
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_landing_gear_adapter.py [--format text|json]")


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

    exit_code, report, text_lines = validate_landing_gear_adapter()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
