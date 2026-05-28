#!/usr/bin/env python3
"""Validate the M6 approved queue extension template package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from well_harness.agent_queue_extension_template import (
    DEFAULT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR,
    M6_PACKAGE_NAME,
    M6_SCHEMA_ID,
    validate_m6_queue_extension_template,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = DEFAULT_M6_QUEUE_EXTENSION_TEMPLATE_ARTIFACT_DIR / M6_PACKAGE_NAME
EXPECTED_TASK_CLASSES = [
    "SafetyRepairTask",
    "EvidenceRepairTask",
    "RequirementRepairTask",
]
REQUIRED_TEMPLATE_FIELDS = [
    "queue_item_id",
    "source_finding_code",
    "task_class",
    "target_agent",
    "task_type",
    "approval_id",
    "readiness_command",
    "runner_contract",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m6_queue_extension_template_v0_1.json.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m6_queue_extension_template_v0_1.json.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(path_value: Any, package_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    project_path = PROJECT_ROOT / path
    if project_path.exists():
        return project_path
    return package_path.parent / path


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    try:
        validate_m6_queue_extension_template(package)
    except ValueError as exc:
        mismatches.append(str(exc))
        return False
    return True


def _append_only_controls_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    controls = package.get("append_only_controls")
    if not isinstance(controls, dict):
        mismatches.append("append_only_controls must be an object")
        return False
    expected = {
        "current_queue_id": "approved-candidate-task-queue-v0.1",
        "next_queue_id": "approved-candidate-task-queue-v0.2",
        "preserve_existing_queue_order": True,
        "requires_new_summary_schema": True,
        "requires_fixture_migration": True,
        "requires_checker_update": True,
        "requires_child_review_export": True,
    }
    valid = True
    for key, value in expected.items():
        if controls.get(key) != value:
            mismatches.append(f"append_only_controls.{key} must be {value!r}")
            valid = False
    return valid


def _task_class_matrix_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    matrix = package.get("task_class_matrix")
    summary = package.get("template_summary")
    template = package.get("queue_item_template")
    if not isinstance(matrix, list) or not isinstance(summary, dict) or not isinstance(template, dict):
        mismatches.append("task_class_matrix, template_summary, and queue_item_template must be present")
        return False
    valid = True
    classes = [item.get("task_class") for item in matrix if isinstance(item, dict)]
    for task_class in EXPECTED_TASK_CLASSES:
        if task_class not in classes:
            mismatches.append(f"task_class_matrix must include {task_class}")
            valid = False
    if summary.get("supported_task_classes") != EXPECTED_TASK_CLASSES:
        mismatches.append("template_summary.supported_task_classes must list Safety, Evidence, and Requirement tasks")
        valid = False
    required_fields = template.get("required_fields")
    if not isinstance(required_fields, list):
        mismatches.append("queue_item_template.required_fields must be an array")
        return False
    for field in REQUIRED_TEMPLATE_FIELDS:
        if field not in required_fields:
            mismatches.append(f"queue_item_template.required_fields must include {field}")
            valid = False
    for item in matrix:
        if not isinstance(item, dict):
            mismatches.append("task_class_matrix entries must be objects")
            valid = False
            continue
        if item.get("required_review_export") != "candidate_review_packet_export_v0_1":
            mismatches.append(f"{item.get('task_class', '<unknown>')} must require candidate_review_packet_export_v0_1")
            valid = False
    return valid


def _template_guide_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    artifact_paths = package.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        mismatches.append("artifact_paths must be an object")
        return False
    guide_path = _resolve_path(artifact_paths.get("operator_template_guide"), package_path)
    if guide_path is None or not guide_path.exists():
        mismatches.append("artifact_paths.operator_template_guide must exist")
        return False
    text = guide_path.read_text(encoding="utf-8")
    valid = True
    for token in ("M6 Queue Extension Template", "SafetyRepairTask", "EvidenceRepairTask", "RequirementRepairTask"):
        if token not in text:
            mismatches.append(f"operator_template_guide must include {token}")
            valid = False
    return valid


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    boundaries = package.get("review_boundaries")
    if not isinstance(boundaries, dict):
        mismatches.append("review_boundaries must be an object")
        return False
    valid = True
    expected = {
        "truth_effect": "none",
        "certification_claim": "none",
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    for key, value in expected.items():
        if boundaries.get(key) != value:
            mismatches.append(f"review_boundaries.{key} must be {value!r}")
            valid = False
    restricted_paths = boundaries.get("restricted_paths")
    for path in (
        "src/well_harness/controller.py",
        "src/well_harness/editable_control_model.py",
        "src/well_harness/static/requirements_intake/",
    ):
        if not isinstance(restricted_paths, list) or path not in restricted_paths:
            mismatches.append(f"review_boundaries.restricted_paths must include {path}")
            valid = False
    return valid


def _aggregate_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    aggregate = package.get("aggregate")
    gates = package.get("deterministic_gates")
    preconditions = package.get("preconditions")
    if not isinstance(aggregate, dict) or not isinstance(gates, dict) or not isinstance(preconditions, dict):
        mismatches.append("aggregate, deterministic_gates, and preconditions must be objects")
        return False
    valid = True
    expected_aggregate = {
        "template_count": 1,
        "supported_task_class_count": 3,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_queue_expansion": True,
    }
    for key, value in expected_aggregate.items():
        if aggregate.get(key) != value:
            mismatches.append(f"aggregate.{key} must be {value!r}")
            valid = False
    if preconditions.get("required_entrypoint") != "make multi-agent-construction-control-plane":
        mismatches.append("preconditions.required_entrypoint must be make multi-agent-construction-control-plane")
        valid = False
    for gate_name, gate_status in gates.items():
        if gate_status != "pass":
            mismatches.append(f"deterministic_gates.{gate_name} must be pass")
            valid = False
    return valid


def verify_m6_queue_extension_template(
    package_path: Path = DEFAULT_PACKAGE_PATH,
) -> dict[str, Any]:
    mismatches: list[str] = []
    package: dict[str, Any] = {}
    try:
        package = _load_json(package_path)
    except (OSError, json.JSONDecodeError) as exc:
        mismatches.append(f"package could not be loaded: {exc}")
        return {
            "status": "fail",
            "package_id": "",
            "schema": M6_SCHEMA_ID,
            "schema_valid": False,
            "append_only_controls_valid": False,
            "task_class_matrix_valid": False,
            "template_guide_valid": False,
            "boundary_valid": False,
            "aggregate_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {"template_package": str(package_path)},
        }

    schema_mismatches: list[str] = []
    controls_mismatches: list[str] = []
    matrix_mismatches: list[str] = []
    guide_mismatches: list[str] = []
    boundary_mismatches: list[str] = []
    aggregate_mismatches: list[str] = []
    schema_valid = _schema_valid(package, schema_mismatches)
    append_only_controls_valid = _append_only_controls_valid(package, controls_mismatches)
    task_class_matrix_valid = _task_class_matrix_valid(package, matrix_mismatches)
    template_guide_valid = _template_guide_valid(
        package,
        package_path=package_path,
        mismatches=guide_mismatches,
    )
    boundary_valid = _boundary_valid(package, boundary_mismatches)
    aggregate_valid = _aggregate_valid(package, aggregate_mismatches)
    mismatches.extend(schema_mismatches)
    mismatches.extend(controls_mismatches)
    mismatches.extend(matrix_mismatches)
    mismatches.extend(guide_mismatches)
    mismatches.extend(boundary_mismatches)
    mismatches.extend(aggregate_mismatches)
    status = (
        "pass"
        if (
            schema_valid
            and append_only_controls_valid
            and task_class_matrix_valid
            and template_guide_valid
            and boundary_valid
            and aggregate_valid
        )
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": M6_SCHEMA_ID,
        "schema_valid": schema_valid,
        "append_only_controls_valid": append_only_controls_valid,
        "task_class_matrix_valid": task_class_matrix_valid,
        "template_guide_valid": template_guide_valid,
        "boundary_valid": boundary_valid,
        "aggregate_valid": aggregate_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "template_package": str(package_path),
            "operator_template_guide": str(package.get("artifact_paths", {}).get("operator_template_guide", "")),
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m6_queue_extension_template(args.package_path)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"schema_valid: {payload['schema_valid']}")
        print(f"task_class_matrix_valid: {payload['task_class_matrix_valid']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
