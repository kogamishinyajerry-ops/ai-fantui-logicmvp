#!/usr/bin/env python3
"""Validate the M2 Requirement -> IR demo package and child artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from well_harness.agent_output_contract import (
    run_evidence_agent_checks,
    run_safety_guardian_checks,
    validate_agent_output_contract,
)
from well_harness.agent_requirement_to_ir_demo import (
    DEFAULT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR,
    M2_PACKAGE_NAME,
    M2_SCHEMA_ID,
    validate_m2_requirement_to_ir_demo_package,
)
from well_harness.agent_review_packet import validate_candidate_review_packet_export
from well_harness.agent_task_contract import validate_agent_task_package


DEFAULT_PACKAGE_PATH = DEFAULT_M2_REQUIREMENT_TO_IR_ARTIFACT_DIR / M2_PACKAGE_NAME


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m2_requirement_to_ir_demo_v0_1.json.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m2_requirement_to_ir_demo_v0_1.json.",
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
        validate_m2_requirement_to_ir_demo_package(package)
    except ValueError as exc:
        mismatches.append(str(exc))
        return False
    return True


def _artifact_path(package: dict[str, Any], package_path: Path, key: str) -> Path | None:
    artifact_paths = package.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        return None
    return _resolve_path(artifact_paths.get(key), package_path)


def _child_artifacts_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    valid = True
    candidate_path = _artifact_path(package, package_path, "candidate_agent_output")
    if candidate_path is None or not candidate_path.exists():
        mismatches.append("artifact_paths.candidate_agent_output must exist")
        valid = False
    else:
        try:
            validate_agent_output_contract(_load_json(candidate_path))
        except Exception as exc:  # noqa: BLE001 - checker reports all validation failures.
            mismatches.append(f"candidate_agent_output invalid: {exc}")
            valid = False

    task_package_path = _artifact_path(package, package_path, "task_package")
    if task_package_path is None or not task_package_path.exists():
        mismatches.append("artifact_paths.task_package must exist")
        valid = False
    else:
        try:
            validate_agent_task_package(_load_json(task_package_path))
        except Exception as exc:  # noqa: BLE001
            mismatches.append(f"task_package invalid: {exc}")
            valid = False

    review_export_path = _artifact_path(package, package_path, "candidate_review_packet_export")
    if review_export_path is None or not review_export_path.exists():
        mismatches.append("artifact_paths.candidate_review_packet_export must exist")
        valid = False
    else:
        try:
            validate_candidate_review_packet_export(_load_json(review_export_path))
        except Exception as exc:  # noqa: BLE001
            mismatches.append(f"candidate_review_packet_export invalid: {exc}")
            valid = False

    source_requirement_path = _artifact_path(package, package_path, "source_requirement")
    if source_requirement_path is None or not source_requirement_path.exists():
        mismatches.append("artifact_paths.source_requirement must exist")
        valid = False
    return valid


def _finding_codes(report: dict[str, Any]) -> list[str]:
    return [
        str(item["code"])
        for item in report.get("findings", [])
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    ]


def _traceability_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    valid = True
    aggregate = package.get("aggregate")
    if not isinstance(aggregate, dict):
        mismatches.append("aggregate must be an object")
        return False
    if aggregate.get("open_findings") != []:
        mismatches.append("aggregate.open_findings must be empty")
        valid = False
    if aggregate.get("controller_truth_modified") is not False:
        mismatches.append("aggregate.controller_truth_modified must be false")
        valid = False
    if aggregate.get("ui_layout_modified") is not False:
        mismatches.append("aggregate.ui_layout_modified must be false")
        valid = False
    if aggregate.get("ready_for_m2_review") is not True:
        mismatches.append("aggregate.ready_for_m2_review must be true")
        valid = False

    candidate_path = _artifact_path(package, package_path, "candidate_agent_output")
    if candidate_path is None or not candidate_path.exists():
        return False
    candidate_packet = _load_json(candidate_path)
    safety_report = run_safety_guardian_checks(candidate_packet)
    evidence_report = run_evidence_agent_checks(candidate_packet)
    if _finding_codes(safety_report) != ["CHECK_SAFETY_PRIORITY_001"]:
        mismatches.append("candidate safety findings must contain only CHECK_SAFETY_PRIORITY_001")
        valid = False
    if _finding_codes(evidence_report) != []:
        mismatches.append("candidate evidence findings must be empty")
        valid = False
    coverage = evidence_report.get("coverage", {}).get("requirements", {})
    if coverage.get("total") != 4 or coverage.get("covered_by_ir") != 4:
        mismatches.append("all four requirements must be traced to IR")
        valid = False
    if coverage.get("covered_by_tests") != 4:
        mismatches.append("all four requirements must be covered by tests")
        valid = False
    return valid


def _review_export_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    review_export_path = _artifact_path(package, package_path, "candidate_review_packet_export")
    if review_export_path is None or not review_export_path.exists():
        return False
    review_export = _load_json(review_export_path)
    review_packet = review_export.get("review_packet", {})
    valid = True
    if review_packet.get("reviewer", {}).get("status") != "converged":
        mismatches.append("review_packet.reviewer.status must be converged")
        valid = False
    if review_packet.get("summary", {}).get("open_findings") != []:
        mismatches.append("review_packet.summary.open_findings must be empty")
        valid = False
    chain_statuses = [
        chain.get("status")
        for chain in review_packet.get("finding_chains", [])
        if isinstance(chain, dict)
    ]
    if chain_statuses != ["converged"]:
        mismatches.append("review_packet finding chain must be converged")
        valid = False
    return valid


def verify_m2_requirement_to_ir_demo(package_path: Path = DEFAULT_PACKAGE_PATH) -> dict[str, Any]:
    mismatches: list[str] = []
    package: dict[str, Any] = {}
    try:
        package = _load_json(package_path)
    except (OSError, json.JSONDecodeError) as exc:
        mismatches.append(f"package could not be loaded: {exc}")
        return {
            "status": "fail",
            "package_id": "",
            "schema": M2_SCHEMA_ID,
            "schema_valid": False,
            "child_artifacts_valid": False,
            "traceability_valid": False,
            "review_export_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {"demo_package": str(package_path)},
        }

    schema_mismatches: list[str] = []
    child_mismatches: list[str] = []
    traceability_mismatches: list[str] = []
    review_mismatches: list[str] = []
    schema_valid = _schema_valid(package, schema_mismatches)
    child_artifacts_valid = _child_artifacts_valid(
        package,
        package_path=package_path,
        mismatches=child_mismatches,
    )
    traceability_valid = _traceability_valid(
        package,
        package_path=package_path,
        mismatches=traceability_mismatches,
    )
    review_export_valid = _review_export_valid(
        package,
        package_path=package_path,
        mismatches=review_mismatches,
    )
    mismatches.extend(schema_mismatches)
    mismatches.extend(child_mismatches)
    mismatches.extend(traceability_mismatches)
    mismatches.extend(review_mismatches)
    status = (
        "pass"
        if schema_valid and child_artifacts_valid and traceability_valid and review_export_valid
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": M2_SCHEMA_ID,
        "schema_valid": schema_valid,
        "child_artifacts_valid": child_artifacts_valid,
        "traceability_valid": traceability_valid,
        "review_export_valid": review_export_valid,
        "mismatches": mismatches,
        "artifact_paths": {"demo_package": str(package_path)},
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m2_requirement_to_ir_demo(args.package_path)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"schema_valid: {payload['schema_valid']}")
        print(f"child_artifacts_valid: {payload['child_artifacts_valid']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
