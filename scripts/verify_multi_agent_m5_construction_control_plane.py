#!/usr/bin/env python3
"""Validate the M5 construction control-plane package and child artifacts."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.agent_construction_control_plane import (
    DEFAULT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR,
    M5_PACKAGE_NAME,
    M5_SCHEMA_ID,
    validate_m5_construction_control_plane,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = DEFAULT_M5_CONSTRUCTION_CONTROL_PLANE_ARTIFACT_DIR / M5_PACKAGE_NAME
EXPECTED_FAILURE_RECOVERY_IDS = [
    "FR-GATE-001",
    "FR-QUEUE-001",
    "FR-BOUNDARY-001",
    "FR-CHILD-001",
]
EXPECTED_STOP_CONDITION_IDS = [
    "STOP-APPROVAL-MISSING",
    "STOP-CONTROLLER-TRUTH-DIFF",
    "STOP-UI-LAYOUT-DIFF",
    "STOP-CERTIFICATION-CLAIM",
    "STOP-DETERMINISTIC-GATE-FAIL",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m5_construction_control_plane_v0_1.json.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m5_construction_control_plane_v0_1.json.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def _env() -> dict[str, str]:
    env = dict(os.environ)
    pythonpath = f"{PROJECT_ROOT / 'src'}:{PROJECT_ROOT}"
    env["PYTHONPATH"] = f"{pythonpath}:{env['PYTHONPATH']}" if env.get("PYTHONPATH") else pythonpath
    return env


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


def _run_json_command(args: list[str], *, timeout: int = 180) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {}
    return {"returncode": result.returncode, "payload": payload, "stderr": result.stderr}


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    try:
        validate_m5_construction_control_plane(package)
    except ValueError as exc:
        mismatches.append(str(exc))
        return False
    return True


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


def _child_packages_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    child_packages = package.get("child_packages")
    if not isinstance(child_packages, dict):
        mismatches.append("child_packages must be an object")
        return False
    expected = {
        "m4_external_review_handoff": (
            "multi-agent-m4-external-review-handoff-v0.1",
            "scripts/verify_multi_agent_m4_external_review_handoff.py",
        ),
        "approved_candidate_task_queue": (
            "approved-candidate-task-queue-v0.1",
            "scripts/verify_approved_candidate_task_queue_artifact.py",
        ),
        "construction_readiness": (
            "multi-agent-construction-readiness-v0.1",
            "",
        ),
    }
    valid = True
    for key, (package_id, checker_script) in expected.items():
        child = child_packages.get(key)
        if not isinstance(child, dict):
            mismatches.append(f"child_packages.{key} must be an object")
            valid = False
            continue
        if child.get("package_id") != package_id:
            mismatches.append(f"child_packages.{key}.package_id must be {package_id}")
            valid = False
        if child.get("status") != "pass" or child.get("checker_status") != "pass":
            mismatches.append(f"child_packages.{key} statuses must be pass")
            valid = False
        path = _resolve_path(child.get("path"), package_path)
        if path is None or not path.exists():
            mismatches.append(f"child_packages.{key}.path must exist")
            valid = False
            continue
        if key == "construction_readiness":
            try:
                readiness = _load_json(path)
            except (OSError, json.JSONDecodeError) as exc:
                mismatches.append(f"construction_readiness payload invalid: {exc}")
                valid = False
                continue
            if readiness.get("status") != "pass":
                mismatches.append("construction_readiness.status must be pass")
                valid = False
            if readiness.get("ready_for_long_running_development") is not True:
                mismatches.append("construction_readiness.ready_for_long_running_development must be true")
                valid = False
            continue
        args = [
            sys.executable,
            checker_script,
            "--format",
            "json",
        ]
        if key == "approved_candidate_task_queue":
            args.extend(["--summary", str(path)])
        else:
            args.extend(["--package", str(path)])
        result = _run_json_command(args, timeout=240)
        if result["returncode"] != 0 or result["payload"].get("status") != "pass":
            mismatches.append(f"child_packages.{key} must verify with {checker_script}")
            valid = False
    return valid


def _queue_snapshot_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    snapshot = package.get("queue_snapshot")
    if not isinstance(snapshot, dict):
        mismatches.append("queue_snapshot must be an object")
        return False
    expected = {
        "queue_id": "approved-candidate-task-queue-v0.1",
        "task_count": 3,
        "passed": 3,
        "preflight_passed": 3,
        "executed_limited": 3,
        "converged": 3,
        "open_findings": [],
        "ready_for_long_running_development": True,
    }
    valid = True
    for key, value in expected.items():
        if snapshot.get(key) != value:
            mismatches.append(f"queue_snapshot.{key} must be {value!r}")
            valid = False
    aggregate = package.get("aggregate", {})
    if not isinstance(aggregate, dict):
        mismatches.append("aggregate must be an object")
        return False
    if aggregate.get("queue_task_count") != snapshot.get("task_count"):
        mismatches.append("aggregate.queue_task_count must match queue_snapshot.task_count")
        valid = False
    if aggregate.get("approved_task_count") != snapshot.get("executed_limited"):
        mismatches.append("aggregate.approved_task_count must match queue_snapshot.executed_limited")
        valid = False
    return valid


def _failure_recovery_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    recovery = package.get("failure_recovery")
    if not isinstance(recovery, list):
        mismatches.append("failure_recovery must be an array")
        return False
    valid = True
    ids = [item.get("id") for item in recovery if isinstance(item, dict)]
    for expected_id in EXPECTED_FAILURE_RECOVERY_IDS:
        if expected_id not in ids:
            mismatches.append(f"failure_recovery must include {expected_id}")
            valid = False
    artifact_paths = package.get("artifact_paths")
    runbook_path = None
    if isinstance(artifact_paths, dict):
        runbook_path = _resolve_path(artifact_paths.get("operator_runbook"), package_path)
    if runbook_path is None or not runbook_path.exists():
        mismatches.append("artifact_paths.operator_runbook must exist")
        valid = False
    else:
        text = runbook_path.read_text(encoding="utf-8")
        for token in ("M5 Construction Control Plane", "make multi-agent-construction-control-plane"):
            if token not in text:
                mismatches.append(f"operator_runbook must include {token}")
                valid = False
    return valid


def _phase_stop_conditions_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    stop_conditions = package.get("phase_review_stop_conditions")
    if not isinstance(stop_conditions, list):
        mismatches.append("phase_review_stop_conditions must be an array")
        return False
    valid = True
    ids = [item.get("id") for item in stop_conditions if isinstance(item, dict)]
    for expected_id in EXPECTED_STOP_CONDITION_IDS:
        if expected_id not in ids:
            mismatches.append(f"phase_review_stop_conditions must include {expected_id}")
            valid = False
    for item in stop_conditions:
        if not isinstance(item, dict):
            mismatches.append("phase_review_stop_conditions items must be objects")
            valid = False
            continue
        if item.get("blocking") is not True:
            mismatches.append(f"{item.get('id', '<unknown>')}.blocking must be true")
            valid = False
    return valid


def _aggregate_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    aggregate = package.get("aggregate")
    summary = package.get("control_plane_summary")
    gates = package.get("deterministic_gates")
    if not isinstance(aggregate, dict) or not isinstance(summary, dict) or not isinstance(gates, dict):
        mismatches.append("aggregate, control_plane_summary, and deterministic_gates must be objects")
        return False
    valid = True
    expected_aggregate = {
        "milestone_count": 4,
        "child_package_count": 3,
        "queue_task_count": 3,
        "approved_task_count": 3,
        "active_stop_conditions": [],
        "open_findings": [],
        "controller_truth_modified": False,
        "ui_layout_modified": False,
        "ready_for_long_running_construction": True,
    }
    for key, value in expected_aggregate.items():
        if aggregate.get(key) != value:
            mismatches.append(f"aggregate.{key} must be {value!r}")
            valid = False
    if summary.get("readiness_status") != "ready_for_long_running_construction":
        mismatches.append("control_plane_summary.readiness_status must be ready_for_long_running_construction")
        valid = False
    if summary.get("entrypoint") != "make multi-agent-construction-control-plane":
        mismatches.append("control_plane_summary.entrypoint must be make multi-agent-construction-control-plane")
        valid = False
    for gate_name, gate_status in gates.items():
        if gate_status != "pass":
            mismatches.append(f"deterministic_gates.{gate_name} must be pass")
            valid = False
    return valid


def verify_m5_construction_control_plane(
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
            "schema": M5_SCHEMA_ID,
            "schema_valid": False,
            "child_packages_valid": False,
            "queue_snapshot_valid": False,
            "failure_recovery_valid": False,
            "phase_stop_conditions_valid": False,
            "boundary_valid": False,
            "aggregate_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {"control_plane_package": str(package_path)},
        }

    schema_mismatches: list[str] = []
    child_mismatches: list[str] = []
    queue_mismatches: list[str] = []
    recovery_mismatches: list[str] = []
    stop_mismatches: list[str] = []
    boundary_mismatches: list[str] = []
    aggregate_mismatches: list[str] = []
    schema_valid = _schema_valid(package, schema_mismatches)
    child_packages_valid = _child_packages_valid(
        package,
        package_path=package_path,
        mismatches=child_mismatches,
    )
    queue_snapshot_valid = _queue_snapshot_valid(package, queue_mismatches)
    failure_recovery_valid = _failure_recovery_valid(
        package,
        package_path=package_path,
        mismatches=recovery_mismatches,
    )
    phase_stop_conditions_valid = _phase_stop_conditions_valid(package, stop_mismatches)
    boundary_valid = _boundary_valid(package, boundary_mismatches)
    aggregate_valid = _aggregate_valid(package, aggregate_mismatches)
    mismatches.extend(schema_mismatches)
    mismatches.extend(child_mismatches)
    mismatches.extend(queue_mismatches)
    mismatches.extend(recovery_mismatches)
    mismatches.extend(stop_mismatches)
    mismatches.extend(boundary_mismatches)
    mismatches.extend(aggregate_mismatches)
    status = (
        "pass"
        if (
            schema_valid
            and child_packages_valid
            and queue_snapshot_valid
            and failure_recovery_valid
            and phase_stop_conditions_valid
            and boundary_valid
            and aggregate_valid
        )
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": M5_SCHEMA_ID,
        "schema_valid": schema_valid,
        "child_packages_valid": child_packages_valid,
        "queue_snapshot_valid": queue_snapshot_valid,
        "failure_recovery_valid": failure_recovery_valid,
        "phase_stop_conditions_valid": phase_stop_conditions_valid,
        "boundary_valid": boundary_valid,
        "aggregate_valid": aggregate_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "control_plane_package": str(package_path),
            "operator_runbook": str(package.get("artifact_paths", {}).get("operator_runbook", "")),
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m5_construction_control_plane(args.package_path)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"schema_valid: {payload['schema_valid']}")
        print(f"child_packages_valid: {payload['child_packages_valid']}")
        print(f"queue_snapshot_valid: {payload['queue_snapshot_valid']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
