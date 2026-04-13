from __future__ import annotations

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.adapters.landing_gear_adapter import build_landing_gear_controller_adapter
from well_harness.scenario_playback import build_playback_report_from_truth_adapter


PLAYBACK_TRACE_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "playback_trace_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate landing-gear playback payloads."
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


def series_value_at_time(report, series_id: str, time_s: float) -> float:
    for series in (*report.signal_series, *report.logic_series):
        if series.id != series_id:
            continue
        for point in series.points:
            if abs(point.time_s - time_s) < 1e-9:
                return point.value
    raise KeyError(f"series {series_id!r} does not have a sample at {time_s}")


def make_report(status: str = "pass") -> dict:
    return {
        "results": [],
        "schema_path": relative_path(PLAYBACK_TRACE_SCHEMA_PATH),
        "status": status,
    }


def make_result(case: str, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_landing_gear_playback() -> tuple[int, dict, list[str]]:
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
        schema_document = load_json(PLAYBACK_TRACE_SCHEMA_PATH)
        Draft202012Validator.check_schema(schema_document)
    except Exception as exc:
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL schema: unable to load {relative_path(PLAYBACK_TRACE_SCHEMA_PATH)}: {exc}"]

    adapter = build_landing_gear_controller_adapter()
    playback_report = build_playback_report_from_truth_adapter(
        adapter,
        scenario_id="handle_down_nominal_extension",
        sample_period_s=0.5,
    )
    payload = playback_report.to_dict()

    validator = Draft202012Validator(schema_document)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if errors:
        formatted_errors = [format_validation_error(error) for error in errors[:10]]
        report["failure_kind"] = "schema_validation"
        report["results"].append(
            make_result("landing_gear_adapter_backed_playback_schema", "fail", error_count=len(errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        return 1, report, ["FAIL landing_gear_adapter_backed_playback_schema:"] + [f"  - {error}" for error in formatted_errors]

    report["results"].append(
        make_result(
            "landing_gear_adapter_backed_playback_schema",
            "pass",
            error_count=0,
            errors=[],
            scenario_id=playback_report.scenario_id,
            system_id=playback_report.system_id,
        )
    )

    checkpoints = (
        (
            0.0,
            {
                "gear_handle_position": "DOWN",
                "hydraulic_pressure_psi": series_value_at_time(playback_report, "hydraulic_pressure_psi", 0.0),
                "uplock_released": series_value_at_time(playback_report, "uplock_released", 0.0) >= 0.5,
                "gear_position_percent": series_value_at_time(playback_report, "gear_position_percent", 0.0),
                "downlock_engaged": series_value_at_time(playback_report, "downlock_engaged", 0.0) >= 0.5,
            },
            ("lg_l1_handle_and_pressure",),
            False,
        ),
        (
            1.0,
            {
                "gear_handle_position": "DOWN",
                "hydraulic_pressure_psi": series_value_at_time(playback_report, "hydraulic_pressure_psi", 1.0),
                "uplock_released": series_value_at_time(playback_report, "uplock_released", 1.0) >= 0.5,
                "gear_position_percent": series_value_at_time(playback_report, "gear_position_percent", 1.0),
                "downlock_engaged": series_value_at_time(playback_report, "downlock_engaged", 1.0) >= 0.5,
            },
            ("lg_l1_handle_and_pressure", "lg_l2_extend_after_uplock_release"),
            False,
        ),
        (
            6.0,
            {
                "gear_handle_position": "DOWN",
                "hydraulic_pressure_psi": series_value_at_time(playback_report, "hydraulic_pressure_psi", 6.0),
                "uplock_released": series_value_at_time(playback_report, "uplock_released", 6.0) >= 0.5,
                "gear_position_percent": series_value_at_time(playback_report, "gear_position_percent", 6.0),
                "downlock_engaged": series_value_at_time(playback_report, "downlock_engaged", 6.0) >= 0.5,
            },
            ("lg_l1_handle_and_pressure", "lg_l2_extend_after_uplock_release"),
            True,
        ),
    )

    for checkpoint_time, snapshot, expected_logic_ids, expected_completion in checkpoints:
        evaluation = adapter.evaluate_snapshot(snapshot)
        if evaluation.active_logic_node_ids != expected_logic_ids or evaluation.completion_reached != expected_completion:
            report["failure_kind"] = "checkpoint_alignment"
            report["results"].append(
                make_result(
                    "landing_gear_adapter_backed_playback_alignment",
                    "fail",
                    checkpoint_time_s=checkpoint_time,
                    error_count=1,
                    errors=[
                        "adapter truth did not match the expected playback checkpoint"
                    ],
                )
            )
            report["status"] = "fail"
            return 1, report, [
                f"FAIL landing_gear_adapter_backed_playback_alignment: adapter truth did not match checkpoint {checkpoint_time:g}s"
            ]

    report["results"].append(
        make_result(
            "landing_gear_adapter_backed_playback_alignment",
            "pass",
            checkpoint_times=[0.0, 1.0, 6.0],
            completion_reached=playback_report.completion_reached,
            error_count=0,
            errors=[],
        )
    )

    text_lines = [
        "OK landing_gear_adapter_backed_playback_schema: adapter-backed landing-gear playback is schema-valid",
        "OK landing_gear_adapter_backed_playback_alignment: playback checkpoints align with adapter truth",
        "PASS: validated landing-gear adapter-backed playback proof",
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_landing_gear_playback.py [--format text|json]")


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

    exit_code, report, text_lines = validate_landing_gear_playback()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
