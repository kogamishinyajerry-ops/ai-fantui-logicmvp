#!/usr/bin/env python3
"""
Validate the landing-gear full intake --> playback --> diagnosis --> knowledge pipeline.

Each stage's output is validated against its v1 JSON schema:
  Stage 1: ControlSystemIntakePacket --> ControlSystemWorkbenchSpec
           validated against control_system_spec_v1.schema.json
  Stage 2: ControlSystemIntakePacket --> ScenarioPlaybackReport
           validated against playback_trace_v1.schema.json
  Stage 3: ControlSystemIntakePacket --> FaultDiagnosisReport
           validated against fault_diagnosis_v1.schema.json
  Stage 4: ControlSystemIntakePacket --> KnowledgeArtifact
           validated against knowledge_artifact_v1.schema.json

Exit codes:
  0  all schemas pass
  1  one or more schema failures
  2  bad arguments
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.adapters.landing_gear_intake_packet import build_landing_gear_intake_packet
from well_harness.document_intake import intake_packet_to_workbench_spec
from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet
from well_harness.knowledge_capture import build_knowledge_artifact
from well_harness.scenario_playback import build_playback_report_from_intake_packet
from well_harness.system_spec import workbench_spec_to_dict

FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OUTPUT_FORMATS = {"text", "json"}
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed. "
    "Install it to validate the landing-gear full pipeline."
)

SCHEMA_PATHS = {
    "spec": PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json",
    "playback": PROJECT_ROOT / "docs" / "json_schema" / "playback_trace_v1.schema.json",
    "diagnosis": PROJECT_ROOT / "docs" / "json_schema" / "fault_diagnosis_v1.schema.json",
    "knowledge": PROJECT_ROOT / "docs" / "json_schema" / "knowledge_artifact_v1.schema.json",
}

LANDING_GEAR_SCENARIO_ID = "handle_down_nominal_extension"
LANDING_GEAR_FAULT_MODE_ID = "uplock_stuck_locked"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def relative_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def format_validation_error(error) -> str:
    path = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return f"{path}: {error.message}"


def make_result(case: str, validation_status: str, **extra_fields) -> dict:
    result = {
        "case": case,
        "validation_status": validation_status,
    }
    result.update(extra_fields)
    return result


def validate_landing_gear_full_pipeline() -> tuple[int, dict, list[str]]:
    report: dict = {
        "results": [],
        "status": "pass",
    }

    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        report["status"] = "skip"
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        report["status"] = "skip"
        report["reason"] = OPTIONAL_JSONSCHEMA_SKIP_MESSAGE
        return 0, report, [OPTIONAL_JSONSCHEMA_SKIP_MESSAGE]

    # Load all schemas once
    schemas: dict[str, dict] = {}
    for key, schema_path in SCHEMA_PATHS.items():
        try:
            schemas[key] = load_json(schema_path)
            Draft202012Validator.check_schema(schemas[key])
        except Exception as exc:
            report["failure_kind"] = "schema_unavailable"
            report["reason"] = f"unable to load {relative_path(schema_path)}: {exc}"
            report["status"] = "fail"
            return 1, report, [f"FAIL schema: {relative_path(schema_path)}: {exc}"]

    # ---- Stage 1: Intake packet --> spec --> validate ----
    packet = build_landing_gear_intake_packet()
    spec = intake_packet_to_workbench_spec(packet)
    spec_dict = workbench_spec_to_dict(spec)

    validator_spec = Draft202012Validator(schemas["spec"])
    spec_errors = sorted(
        validator_spec.iter_errors(spec_dict),
        key=lambda e: tuple(e.absolute_path),
    )
    if spec_errors:
        formatted = [format_validation_error(e) for e in spec_errors[:10]]
        report["results"].append(
            make_result(
                "intake_to_spec_schema",
                "fail",
                error_count=len(spec_errors),
                errors=formatted,
            )
        )
        report["status"] = "fail"
        report_lines = [f"FAIL intake_to_spec_schema ({len(spec_errors)} error(s)):"]
        report_lines += [f"  - {e}" for e in formatted]
        return 1, report, report_lines

    report["results"].append(
        make_result(
            "intake_to_spec_schema",
            "pass",
            system_id=spec.system_id,
            component_count=len(spec.components),
            logic_node_count=len(spec.logic_nodes),
            error_count=0,
            errors=[],
        )
    )

    # ---- Stage 2: Intake packet --> playback --> validate ----
    playback = build_playback_report_from_intake_packet(
        packet,
        scenario_id=LANDING_GEAR_SCENARIO_ID,
        sample_period_s=0.5,
    )
    playback_dict = playback.to_dict()

    validator_playback = Draft202012Validator(schemas["playback"])
    playback_errors = sorted(
        validator_playback.iter_errors(playback_dict),
        key=lambda e: tuple(e.absolute_path),
    )
    if playback_errors:
        formatted = [format_validation_error(e) for e in playback_errors[:10]]
        report["results"].append(
            make_result(
                "intake_to_playback_schema",
                "fail",
                error_count=len(playback_errors),
                errors=formatted,
            )
        )
        report["status"] = "fail"
        report_lines = [f"FAIL intake_to_playback_schema ({len(playback_errors)} error(s)):"]
        report_lines += [f"  - {e}" for e in formatted]
        return 1, report, report_lines

    report["results"].append(
        make_result(
            "intake_to_playback_schema",
            "pass",
            scenario_id=playback.scenario_id,
            completion_reached=playback.completion_reached,
            error_count=0,
            errors=[],
        )
    )

    # ---- Stage 3: Intake packet --> diagnosis --> validate ----
    diagnosis = build_fault_diagnosis_report_from_intake_packet(
        packet,
        scenario_id=LANDING_GEAR_SCENARIO_ID,
        fault_mode_id=LANDING_GEAR_FAULT_MODE_ID,
        sample_period_s=0.5,
    )
    diagnosis_dict = diagnosis.to_dict()

    validator_diagnosis = Draft202012Validator(schemas["diagnosis"])
    diagnosis_errors = sorted(
        validator_diagnosis.iter_errors(diagnosis_dict),
        key=lambda e: tuple(e.absolute_path),
    )
    if diagnosis_errors:
        formatted = [format_validation_error(e) for e in diagnosis_errors[:10]]
        report["results"].append(
            make_result(
                "intake_to_diagnosis_schema",
                "fail",
                error_count=len(diagnosis_errors),
                errors=formatted,
            )
        )
        report["status"] = "fail"
        report_lines = [f"FAIL intake_to_diagnosis_schema ({len(diagnosis_errors)} error(s)):"]
        report_lines += [f"  - {e}" for e in formatted]
        return 1, report, report_lines

    report["results"].append(
        make_result(
            "intake_to_diagnosis_schema",
            "pass",
            fault_mode_id=diagnosis.fault_mode_id,
            baseline_completion=diagnosis.baseline_completion_reached,
            fault_completion=diagnosis.fault_completion_reached,
            error_count=0,
            errors=[],
        )
    )

    # ---- Stage 4: Intake packet --> knowledge --> validate ----
    knowledge = build_knowledge_artifact(
        packet,
        scenario_id=LANDING_GEAR_SCENARIO_ID,
        fault_mode_id=LANDING_GEAR_FAULT_MODE_ID,
        sample_period_s=0.5,
    )
    knowledge_dict = knowledge.to_dict()

    validator_knowledge = Draft202012Validator(schemas["knowledge"])
    knowledge_errors = sorted(
        validator_knowledge.iter_errors(knowledge_dict),
        key=lambda e: tuple(e.absolute_path),
    )
    if knowledge_errors:
        formatted = [format_validation_error(e) for e in knowledge_errors[:10]]
        report["results"].append(
            make_result(
                "intake_to_knowledge_schema",
                "fail",
                error_count=len(knowledge_errors),
                errors=formatted,
            )
        )
        report["status"] = "fail"
        report_lines = [f"FAIL intake_to_knowledge_schema ({len(knowledge_errors)} error(s)):"]
        report_lines += [f"  - {e}" for e in formatted]
        return 1, report, report_lines

    report["results"].append(
        make_result(
            "intake_to_knowledge_schema",
            "pass",
            artifact_status=knowledge.status,
            generated_at_utc=knowledge.generated_at_utc,
            error_count=0,
            errors=[],
        )
    )

    report_lines = [
        "PASS intake_to_spec_schema:       ControlSystemWorkbenchSpec is schema-valid",
        "PASS intake_to_playback_schema:   ScenarioPlaybackReport is schema-valid",
        "PASS intake_to_diagnosis_schema:  FaultDiagnosisReport is schema-valid",
        "PASS intake_to_knowledge_schema:  KnowledgeArtifact is schema-valid",
        "PASS: landing-gear full intake pipeline validated end-to-end",
    ]
    return 0, report, report_lines


def parse_output_format(argv: list[str]) -> str:
    if not argv:
        return "text"
    if len(argv) == 2 and argv[0] == "--format" and argv[1] in OUTPUT_FORMATS:
        return argv[1]
    raise ValueError("usage: validate_landing_gear_full_pipeline.py [--format text|json]")


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

    exit_code, report, text_lines = validate_landing_gear_full_pipeline()
    emit_report(report, text_lines, output_format)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
