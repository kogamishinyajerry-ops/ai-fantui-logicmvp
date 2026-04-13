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
from well_harness.knowledge_capture import build_knowledge_artifact_from_truth_adapter


KNOWLEDGE_ARTIFACT_SCHEMA_PATH = PROJECT_ROOT / "docs" / "json_schema" / "knowledge_artifact_v1.schema.json"
FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate landing-gear knowledge payloads."
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
        "schema_path": relative_path(KNOWLEDGE_ARTIFACT_SCHEMA_PATH),
        "status": status,
    }


def make_result(case: str, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_landing_gear_knowledge() -> tuple[int, dict, list[str]]:
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
        schema_document = load_json(KNOWLEDGE_ARTIFACT_SCHEMA_PATH)
        Draft202012Validator.check_schema(schema_document)
    except Exception as exc:
        report["failure_kind"] = "schema_unavailable"
        report["reason"] = str(exc)
        report["status"] = "fail"
        return 1, report, [f"FAIL schema: unable to load {relative_path(KNOWLEDGE_ARTIFACT_SCHEMA_PATH)}: {exc}"]

    artifact = build_knowledge_artifact_from_truth_adapter(
        build_landing_gear_controller_adapter(),
        scenario_id="handle_down_nominal_extension",
        fault_mode_id="hydraulic_pressure_bias_low",
        evidence_links=("https://example.test/landing-gear/diagnosis-proof",),
        confirmed_root_cause="Hydraulic pressure sensing drift masked the extension-ready threshold.",
        repair_action="Recalibrated the hydraulic pressure sensing path and reran the extension proof.",
        validation_after_fix="Replayed the landing-gear extension and confirmed the command path completed again.",
        residual_risk="Continue monitoring for future pressure-sensor drift during maintenance checks.",
        sample_period_s=0.5,
    )
    payload = artifact.to_dict()

    validator = Draft202012Validator(schema_document)
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(error.absolute_path),
    )
    if errors:
        formatted_errors = [format_validation_error(error) for error in errors[:10]]
        report["failure_kind"] = "schema_validation"
        report["results"].append(
            make_result("landing_gear_adapter_backed_knowledge_schema", "fail", error_count=len(errors), errors=formatted_errors)
        )
        report["status"] = "fail"
        return 1, report, ["FAIL landing_gear_adapter_backed_knowledge_schema:"] + [f"  - {error}" for error in formatted_errors]

    report["results"].append(
        make_result(
            "landing_gear_adapter_backed_knowledge_schema",
            "pass",
            error_count=0,
            errors=[],
            fault_mode_id=artifact.fault_mode_id,
            status_value=artifact.status,
            system_id=artifact.system_id,
        )
    )

    if (
        artifact.status != "resolved"
        or artifact.diagnosis_report.fault_completion_reached
        or "lg_l1_handle_and_pressure" not in artifact.diagnosis_report.blocked_logic_node_ids
    ):
        report["failure_kind"] = "knowledge_contract"
        report["results"].append(
            make_result(
                "landing_gear_adapter_backed_knowledge_contract",
                "fail",
                error_count=1,
                errors=["adapter-backed knowledge artifact did not preserve the expected resolved diagnosis chain"],
            )
        )
        report["status"] = "fail"
        return 1, report, [
            "FAIL landing_gear_adapter_backed_knowledge_contract: adapter-backed knowledge artifact did not preserve the expected resolved diagnosis chain"
        ]

    report["results"].append(
        make_result(
            "landing_gear_adapter_backed_knowledge_contract",
            "pass",
            blocked_logic_node_ids=list(artifact.diagnosis_report.blocked_logic_node_ids),
            evidence_links=artifact.incident_record["evidence_links"],
            error_count=0,
            errors=[],
        )
    )

    text_lines = [
        "OK landing_gear_adapter_backed_knowledge_schema: adapter-backed landing-gear knowledge artifact is schema-valid",
        "OK landing_gear_adapter_backed_knowledge_contract: resolved knowledge artifact preserves the expected diagnosis chain",
        "PASS: validated landing-gear adapter-backed knowledge proof",
    ]
    return 0, report, text_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_landing_gear_knowledge.py [--format text|json]")


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

    exit_code, report, text_lines = validate_landing_gear_knowledge()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
