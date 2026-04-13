#!/usr/bin/env python3
"""
Dry-run script that validates whether a new-system spec can pass through the full pipeline.

Accepts a JSON spec file conforming to control_system_spec_v1.schema.json and runs it
through all 4 pipeline stages:

  Stage 1 – SPEC:      JSON spec  -->  ControlSystemWorkbenchSpec  (via workbench_spec_from_dict)
  Stage 2 – PLAYBACK:  ControlSystemIntakePacket  -->  ScenarioPlaybackReport
  Stage 3 – DIAGNOSIS: ControlSystemIntakePacket  -->  FaultDiagnosisReport
  Stage 4 – KNOWLEDGE: ControlSystemIntakePacket  -->  KnowledgeArtifact

Each stage's output is validated against its v1 JSON schema when jsonschema is available.

Exit codes:
  0  all stages pass
  1  one or more failures
  2  bad arguments
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from well_harness.document_intake import (
    ControlSystemIntakePacket,
    SourceDocumentRef,
    intake_packet_from_dict,
    intake_packet_to_workbench_spec,
)
from well_harness.fault_diagnosis import build_fault_diagnosis_report_from_intake_packet
from well_harness.knowledge_capture import build_knowledge_artifact
from well_harness.scenario_playback import build_playback_report_from_intake_packet
from well_harness.system_spec import workbench_spec_from_dict, workbench_spec_to_dict

FORCE_JSONSCHEMA_MISSING_ENV = "WELL_HARNESS_FORCE_JSONSCHEMA_MISSING"
OPTIONAL_JSONSCHEMA_SKIP_MESSAGE = (
    "SKIP: optional dependency 'jsonschema' is not installed; "
    "schema validation is skipped but pipeline stages are still executed."
)

SCHEMA_PATHS = {
    "spec": PROJECT_ROOT / "docs" / "json_schema" / "control_system_spec_v1.schema.json",
    "playback": PROJECT_ROOT / "docs" / "json_schema" / "playback_trace_v1.schema.json",
    "diagnosis": PROJECT_ROOT / "docs" / "json_schema" / "fault_diagnosis_v1.schema.json",
    "knowledge": PROJECT_ROOT / "docs" / "json_schema" / "knowledge_artifact_v1.schema.json",
}


def _format_validation_error(error) -> str:
    """Format a jsonschema ValidationError into a readable path+message string."""
    path = "$"
    for part in error.absolute_path:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return f"{path}: {error.message}"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _build_intake_packet_from_spec_dict(spec_dict: dict) -> ControlSystemIntakePacket:
    """
    Convert a workbench spec dict (as produced by workbench_spec_to_dict) into a
    ControlSystemIntakePacket so it can flow through the playback / diagnosis /
    knowledge stages.
    """
    # Re-parse the spec so we get typed objects
    spec = workbench_spec_from_dict(spec_dict)

    source_document_refs = (
        SourceDocumentRef(
            id="spec-file-source",
            kind="json-spec",
            title=f"Spec file for {spec.system_id}",
            location="<in-memory from spec file>",
            role="truth_source",
            notes="Built by onboard_new_system_dry_run from JSON spec file",
        ),
    )

    return ControlSystemIntakePacket(
        system_id=spec.system_id,
        title=spec.title,
        objective=spec.objective,
        source_of_truth=spec.source_of_truth,
        source_documents=source_document_refs,
        components=spec.components,
        logic_nodes=spec.logic_nodes,
        acceptance_scenarios=spec.acceptance_scenarios,
        fault_modes=spec.fault_modes,
        knowledge_capture=spec.knowledge_capture,
        clarification_answers=(),
        tags=spec.tags,
    )


def _load_spec_from_python_adapter(spec_path: Path) -> dict:
    """
    Load a Python adapter file and call its build_*_workbench_spec() function
    to obtain the spec dict.  This allows the tool to accept either:
      - a JSON spec file (control_system_spec_v1.schema.json format), or
      - a Python adapter file that exposes build_<system>_workbench_spec().
    """
    import importlib.util

    module_name = f"_temp_adapter_{spec_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, spec_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load Python adapter: {spec_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Look for the adapter's spec builder (landing_gear, throttle_reverser, ...)
    for attr_name in dir(module):
        if attr_name.startswith("_") or attr_name in ("sys", "os", "Path"):
            continue
        attr = getattr(module, attr_name, None)
        if callable(attr) and attr_name.endswith("_workbench_spec") and attr_name != "workbench_spec_from_dict":
            return attr()
    raise ValueError(
        f"Python adapter {spec_path} has no function named "
        "build_*_workbench_spec(). Expected e.g. build_landing_gear_workbench_spec()."
    )


def _load_and_validate_spec(spec_path: Path) -> tuple[dict, dict | None, list[str]]:
    """
    Load a spec file — either a JSON file or a Python adapter file.

    For JSON files: parse and validate against control_system_spec_v1.schema.json.
    For Python adapter files: call their build_<name>_workbench_spec() function.

    Returns (spec_dict, schema_dict_or_none, errors).
    If jsonschema is unavailable, schema_dict_or_none is None and errors is [].
    """
    raw_bytes = spec_path.read_bytes()
    if raw_bytes.strip().startswith(b"{"):
        # Looks like JSON — parse it directly
        spec_dict = _load_json(spec_path)
    else:
        # Treat as Python adapter
        spec_dict = _load_spec_from_python_adapter(spec_path)

    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        return spec_dict, None, []

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return spec_dict, None, []

    try:
        schema_dict = _load_json(SCHEMA_PATHS["spec"])
        Draft202012Validator.check_schema(schema_dict)
    except Exception as exc:
        return spec_dict, None, [f"WARN: could not load spec schema: {exc}"]

    validator = Draft202012Validator(schema_dict)
    errors = sorted(validator.iter_errors(spec_dict), key=lambda e: tuple(e.absolute_path))
    if errors:
        return spec_dict, schema_dict, [_format_validation_error(e) for e in errors[:10]]
    return spec_dict, schema_dict, []


def _validate_output_with_schema(
    data: dict,
    schema_key: str,
) -> tuple[bool, list[str]]:
    """
    Validate a stage output dict against its schema.

    Returns (passed, error_messages).
    Gracefully skips if jsonschema is unavailable.
    """
    if os.environ.get(FORCE_JSONSCHEMA_MISSING_ENV) == "1":
        return True, []

    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return True, []

    schema_path = SCHEMA_PATHS.get(schema_key)
    if schema_path is None:
        return True, []

    try:
        schema_dict = _load_json(schema_path)
        Draft202012Validator.check_schema(schema_dict)
    except Exception as exc:
        return False, [f"could not load {schema_key} schema: {exc}"]

    validator = Draft202012Validator(schema_dict)
    errors = sorted(validator.iter_errors(data), key=lambda e: tuple(e.absolute_path))
    if errors:
        return False, [_format_validation_error(e) for e in errors[:10]]
    return True, []


def validate_new_system_spec(
    spec_path: str | Path,
    output_dir: str | Path,
) -> dict:
    """
    Validate a new-system spec file through all 4 pipeline stages.

    Parameters
    ----------
    spec_path
        Path to a JSON file conforming to control_system_spec_v1.schema.json.
    output_dir
        Directory where dry_run_results.json will be written.

    Returns
    -------
    dict with keys:
        overall_status: "pass" | "fail" | "skip"
        stages: list of per-stage result dicts
        spec_errors: list of top-level spec validation errors
        jsonschema_available: bool
    """
    spec_path = Path(spec_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonschema_available = True
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        jsonschema_available = False

    results: dict = {
        "spec_file": str(spec_path),
        "output_dir": str(output_dir),
        "overall_status": "fail",
        "jsonschema_available": jsonschema_available,
        "spec_validation_errors": [],
        "stages": [],
    }

    # ---- Stage 0: Load & validate spec ----
    spec_dict, _, spec_errors = _load_and_validate_spec(spec_path)
    if spec_errors:
        results["spec_validation_errors"] = spec_errors
        results["overall_status"] = "fail"
        results["stages"] = []
        return results

    # ---- Stage 1: spec dict --> ControlSystemWorkbenchSpec ----
    stage1_status = "fail"
    stage1_errors: list[str] = []
    stage1_output: dict = {}

    try:
        spec = workbench_spec_from_dict(spec_dict)
        stage1_output = workbench_spec_to_dict(spec)
        # Basic sanity checks
        assert isinstance(spec.system_id, str) and spec.system_id
        assert isinstance(spec.title, str) and spec.title
        assert isinstance(spec.components, tuple) and len(spec.components) >= 1
        stage1_status = "pass"
    except Exception as exc:
        stage1_errors.append(f"workbench_spec_from_dict failed: {exc}")

    # Schema-validate stage-1 output
    if stage1_status == "pass" and jsonschema_available:
        passed, schema_errors = _validate_output_with_schema(stage1_output, "spec")
        if not passed:
            stage1_status = "fail"
            stage1_errors.extend(schema_errors)

    results["stages"].append({
        "stage": "spec",
        "stage_name": "Stage 1 – SPEC (JSON → ControlSystemWorkbenchSpec)",
        "status": stage1_status,
        "errors": stage1_errors,
        "output_summary": {
            "system_id": stage1_output.get("system_id"),
            "component_count": len(stage1_output.get("components", [])),
            "logic_node_count": len(stage1_output.get("logic_nodes", [])),
            "acceptance_scenario_count": len(stage1_output.get("acceptance_scenarios", [])),
            "fault_mode_count": len(stage1_output.get("fault_modes", [])),
        } if stage1_output else {},
    })

    if stage1_status != "pass":
        results["overall_status"] = "fail"
        return results

    # ---- Stage 2: spec dict --> intake packet --> playback report ----
    stage2_status = "fail"
    stage2_errors: list[str] = []
    stage2_output: dict = {}

    try:
        packet = _build_intake_packet_from_spec_dict(spec_dict)
        # Pick the first scenario for dry-run playback
        if not packet.acceptance_scenarios:
            stage2_errors.append("No acceptance_scenarios defined; cannot run playback.")
        else:
            scenario_id = packet.acceptance_scenarios[0].id
            playback = build_playback_report_from_intake_packet(
                packet,
                scenario_id=scenario_id,
                sample_period_s=0.5,
            )
            stage2_output = playback.to_dict()
            stage2_status = "pass"
    except Exception as exc:
        stage2_errors.append(f"playback stage failed: {exc}")

    if stage2_status == "pass" and jsonschema_available:
        passed, schema_errors = _validate_output_with_schema(stage2_output, "playback")
        if not passed:
            stage2_status = "fail"
            stage2_errors.extend(schema_errors)

    results["stages"].append({
        "stage": "playback",
        "stage_name": "Stage 2 – PLAYBACK (spec → ScenarioPlaybackReport)",
        "status": stage2_status,
        "errors": stage2_errors,
        "output_summary": {
            "scenario_id": stage2_output.get("scenario_id"),
            "completion_reached": stage2_output.get("completion_reached"),
            "signal_series_count": len(stage2_output.get("signal_series", [])),
        } if stage2_output else {},
    })

    if stage2_status != "pass":
        results["overall_status"] = "fail"
        return results

    # ---- Stage 3: spec dict --> intake packet --> fault diagnosis ----
    stage3_status = "fail"
    stage3_errors: list[str] = []
    stage3_output: dict = {}

    try:
        if not packet.fault_modes:
            stage3_errors.append("No fault_modes defined; cannot run diagnosis.")
        else:
            fault_mode_id = packet.fault_modes[0].id
            scenario_id = packet.acceptance_scenarios[0].id
            diagnosis = build_fault_diagnosis_report_from_intake_packet(
                packet,
                scenario_id=scenario_id,
                fault_mode_id=fault_mode_id,
                sample_period_s=0.5,
            )
            stage3_output = diagnosis.to_dict()
            stage3_status = "pass"
    except Exception as exc:
        stage3_errors.append(f"diagnosis stage failed: {exc}")

    if stage3_status == "pass" and jsonschema_available:
        passed, schema_errors = _validate_output_with_schema(stage3_output, "diagnosis")
        if not passed:
            stage3_status = "fail"
            stage3_errors.extend(schema_errors)

    results["stages"].append({
        "stage": "diagnosis",
        "stage_name": "Stage 3 – DIAGNOSIS (spec → FaultDiagnosisReport)",
        "status": stage3_status,
        "errors": stage3_errors,
        "output_summary": {
            "fault_mode_id": stage3_output.get("fault_mode_id"),
            "baseline_completion": stage3_output.get("baseline_completion_reached"),
            "fault_completion": stage3_output.get("fault_completion_reached"),
        } if stage3_output else {},
    })

    if stage3_status != "pass":
        results["overall_status"] = "fail"
        return results

    # ---- Stage 4: spec dict --> intake packet --> knowledge artifact ----
    stage4_status = "fail"
    stage4_errors: list[str] = []
    stage4_output: dict = {}

    try:
        if not packet.fault_modes:
            stage4_errors.append("No fault_modes defined; cannot run knowledge capture.")
        else:
            fault_mode_id = packet.fault_modes[0].id
            scenario_id = packet.acceptance_scenarios[0].id
            knowledge = build_knowledge_artifact(
                packet,
                scenario_id=scenario_id,
                fault_mode_id=fault_mode_id,
                sample_period_s=0.5,
            )
            stage4_output = knowledge.to_dict()
            stage4_status = "pass"
    except Exception as exc:
        stage4_errors.append(f"knowledge stage failed: {exc}")

    if stage4_status == "pass" and jsonschema_available:
        passed, schema_errors = _validate_output_with_schema(stage4_output, "knowledge")
        if not passed:
            stage4_status = "fail"
            stage4_errors.extend(schema_errors)

    results["stages"].append({
        "stage": "knowledge",
        "stage_name": "Stage 4 – KNOWLEDGE (spec → KnowledgeArtifact)",
        "status": stage4_status,
        "errors": stage4_errors,
        "output_summary": {
            "artifact_status": stage4_output.get("status"),
            "generated_at_utc": stage4_output.get("generated_at_utc"),
        } if stage4_output else {},
    })

    if stage4_status != "pass":
        results["overall_status"] = "fail"
        return results

    # All stages passed
    results["overall_status"] = "pass"

    return results


def _render_text(results: dict) -> list[str]:
    """Render a results dict as human-readable lines."""
    lines: list[str] = []

    status = results["overall_status"].upper()
    lines.append(f"=== Onboarding Dry Run: {status} ===")
    lines.append(f"spec file: {results['spec_file']}")

    if not results["jsonschema_available"]:
        lines.append("NOTE: jsonschema not installed; schema validation skipped.")

    if results["spec_validation_errors"]:
        lines.append("\nSPEC VALIDATION ERRORS:")
        for err in results["spec_validation_errors"]:
            lines.append(f"  - {err}")

    for stage_result in results["stages"]:
        stage_name = stage_result["stage_name"]
        stage_status = stage_result["status"].upper()
        lines.append(f"\n[{stage_status}] {stage_name}")
        if stage_result["errors"]:
            for err in stage_result["errors"]:
                lines.append(f"  ERROR: {err}")
        if stage_result["output_summary"]:
            for k, v in stage_result["output_summary"].items():
                lines.append(f"  {k}={v}")

    lines.append(f"\nOVERALL: {results['overall_status'].upper()}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dry-run validation of a new-system spec through the full pipeline.",
    )
    parser.add_argument(
        "--spec-file",
        required=True,
        type=Path,
        help="Path to a JSON spec file conforming to control_system_spec_v1.schema.json",
    )
    parser.add_argument(
        "--output-dir",
        default=Path("./onboarding验证"),
        type=Path,
        help="Directory where dry_run_results.json will be written (default: ./onboarding验证/)",
    )
    parser.add_argument(
        "--format",
        default="text",
        choices=["json", "text"],
        help="Output format (default: text)",
    )

    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    try:
        results = validate_new_system_spec(args.spec_file, args.output_dir)
    except Exception as exc:
        # Fatal error (bad file, etc.)
        results = {
            "spec_file": str(args.spec_file),
            "output_dir": str(args.output_dir),
            "overall_status": "fail",
            "jsonschema_available": True,
            "fatal_error": str(exc),
            "stages": [],
            "spec_validation_errors": [],
        }

    output_path = args.output_dir / "dry_run_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2, ensure_ascii=False)

    if args.format == "json":
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for line in _render_text(results):
            print(line)

    # Exit 0 only if overall passed
    return 0 if results["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
