#!/usr/bin/env python3
"""Validate the M3 Safety/Evidence value package and child review exports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from well_harness.agent_review_packet import validate_candidate_review_packet_export
from well_harness.agent_safety_evidence_value_pack import (
    DEFAULT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR,
    M3_PACKAGE_NAME,
    M3_SCHEMA_ID,
    M3_SLICE_ORDER,
    validate_m3_safety_evidence_value_pack,
)


DEFAULT_PACKAGE_PATH = DEFAULT_M3_SAFETY_EVIDENCE_VALUE_PACK_ARTIFACT_DIR / M3_PACKAGE_NAME


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m3_safety_evidence_value_pack_v0_1.json.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m3_safety_evidence_value_pack_v0_1.json.",
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
    return package_path.parent / path


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    try:
        validate_m3_safety_evidence_value_pack(package)
    except ValueError as exc:
        mismatches.append(str(exc))
        return False
    return True


def _child_review_exports_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    slices = package.get("slices")
    if not isinstance(slices, list):
        mismatches.append("slices must be an array")
        return False
    valid = True
    for item in slices:
        if not isinstance(item, dict):
            mismatches.append("slice summary must be an object")
            valid = False
            continue
        slice_id = str(item.get("slice_id", ""))
        artifact_paths = item.get("artifact_paths")
        if not isinstance(artifact_paths, dict):
            mismatches.append(f"{slice_id}.artifact_paths must be an object")
            valid = False
            continue
        review_export_path = _resolve_path(
            artifact_paths.get("candidate_review_packet_export"),
            package_path,
        )
        if review_export_path is None or not review_export_path.exists():
            mismatches.append(f"{slice_id}.candidate_review_packet_export must exist")
            valid = False
            continue
        try:
            review_export = _load_json(review_export_path)
            validate_candidate_review_packet_export(review_export)
        except Exception as exc:  # noqa: BLE001 - report every checker mismatch.
            mismatches.append(f"{slice_id}.candidate_review_packet_export invalid: {exc}")
            valid = False
            continue
        review_packet = review_export.get("review_packet", {})
        if not isinstance(review_packet, dict):
            mismatches.append(f"{slice_id}.review_packet must be an object")
            valid = False
        elif review_packet.get("reviewer", {}).get("status") != "converged":
            mismatches.append(f"{slice_id}.review_packet.reviewer.status must be converged")
            valid = False
    return valid


def _convergence_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    if package.get("slice_order") != M3_SLICE_ORDER:
        mismatches.append("slice_order must list the four M3 slices in deterministic order")
        valid = False

    aggregate = package.get("aggregate")
    if not isinstance(aggregate, dict):
        mismatches.append("aggregate must be an object")
        return False
    expected_aggregate = {
        "slice_count": 4,
        "passed": 4,
        "converged": 4,
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
    }
    for key, expected in expected_aggregate.items():
        if aggregate.get(key) != expected:
            if key == "open_findings":
                mismatches.append("aggregate.open_findings must be empty")
            else:
                mismatches.append(f"aggregate.{key} must be {expected!r}")
            valid = False

    gates = package.get("deterministic_gates")
    if not isinstance(gates, dict):
        mismatches.append("deterministic_gates must be an object")
        valid = False
    else:
        for gate_name, gate_status in gates.items():
            if gate_status != "pass":
                mismatches.append(f"deterministic_gates.{gate_name} must be pass")
                valid = False

    slices = package.get("slices")
    if not isinstance(slices, list):
        mismatches.append("slices must be an array")
        return False
    if len(slices) != 4:
        mismatches.append("slices must contain exactly four child summaries")
        valid = False
    for item in slices:
        if not isinstance(item, dict):
            mismatches.append("slice summary must be an object")
            valid = False
            continue
        slice_id = str(item.get("slice_id", ""))
        if item.get("status") != "pass":
            mismatches.append(f"{slice_id}.status must be pass")
            valid = False
        if item.get("reviewer_status") != "converged":
            mismatches.append(f"{slice_id}.reviewer_status must be converged")
            valid = False
        if item.get("finding_chain_statuses") != ["converged"]:
            mismatches.append(f"{slice_id}.finding_chain_statuses must be ['converged']")
            valid = False
        convergence = item.get("convergence")
        if not isinstance(convergence, dict):
            mismatches.append(f"{slice_id}.convergence must be an object")
            valid = False
            continue
        if convergence.get("after_findings") != []:
            mismatches.append(f"{slice_id}.convergence.after_findings must be empty")
            valid = False
        if convergence.get("task_package_status") != "no_tasks_required":
            mismatches.append(f"{slice_id}.task_package_status must be no_tasks_required")
            valid = False
        if convergence.get("execution_plan_status") != "no_task_available":
            mismatches.append(f"{slice_id}.execution_plan_status must be no_task_available")
            valid = False
        if convergence.get("execution_evidence_status") != "no_task_available":
            mismatches.append(f"{slice_id}.execution_evidence_status must be no_task_available")
            valid = False
        if convergence.get("controller_truth_modified") is not False:
            mismatches.append(f"{slice_id}.controller_truth_modified must be false")
            valid = False
        if convergence.get("ui_layout_modified") is not False:
            mismatches.append(f"{slice_id}.ui_layout_modified must be false")
            valid = False
    return valid


def verify_m3_safety_evidence_value_pack(
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
            "schema": M3_SCHEMA_ID,
            "schema_valid": False,
            "child_review_exports_valid": False,
            "convergence_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {"package": str(package_path)},
        }

    schema_mismatches: list[str] = []
    child_mismatches: list[str] = []
    convergence_mismatches: list[str] = []
    schema_valid = _schema_valid(package, schema_mismatches)
    child_review_exports_valid = _child_review_exports_valid(
        package,
        package_path=package_path,
        mismatches=child_mismatches,
    )
    convergence_valid = _convergence_valid(package, convergence_mismatches)
    mismatches.extend(schema_mismatches)
    mismatches.extend(child_mismatches)
    mismatches.extend(convergence_mismatches)
    status = (
        "pass"
        if schema_valid and child_review_exports_valid and convergence_valid
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": M3_SCHEMA_ID,
        "schema_valid": schema_valid,
        "child_review_exports_valid": child_review_exports_valid,
        "convergence_valid": convergence_valid,
        "mismatches": mismatches,
        "artifact_paths": {"package": str(package_path)},
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m3_safety_evidence_value_pack(args.package_path)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"schema_valid: {payload['schema_valid']}")
        print(f"child_review_exports_valid: {payload['child_review_exports_valid']}")
        print(f"convergence_valid: {payload['convergence_valid']}")
        print(f"package: {payload['artifact_paths']['package']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
