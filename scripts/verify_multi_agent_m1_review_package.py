#!/usr/bin/env python3
"""Validate the M1 review package and its referenced child artifacts."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = (
    Path("/tmp/ai-fantui-multi-agent-m1-review-package")
    / "multi_agent_m1_review_package_v0_1.json"
)
PACKAGE_SCHEMA_ID = (
    "https://well-harness.local/json_schema/multi_agent_m1_review_package_v0_1.schema.json"
)
PACKAGE_SCHEMA_PATH = (
    PROJECT_ROOT / "docs" / "json_schema" / "multi_agent_m1_review_package_v0_1.schema.json"
)
PACKAGE_ID = "multi-agent-m1-review-package-v0.1"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a generated multi_agent_m1_review_package_v0_1.json artifact.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m1_review_package_v0_1.json.",
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


def _run_json_command(args: list[str], *, timeout: int = 60) -> dict[str, Any]:
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
    return {
        "returncode": result.returncode,
        "payload": payload,
        "stderr": result.stderr,
    }


def _schema_mismatches(package: dict[str, Any]) -> list[str]:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_json(PACKAGE_SCHEMA_PATH)).iter_errors(package),
        key=lambda error: list(error.absolute_path),
    )
    mismatches: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"M1 review package schema validation failed{location}: {error.message}")
    return mismatches


def _all_deliverables_pass(package: dict[str, Any], mismatches: list[str]) -> bool:
    deliverables = package.get("deliverables")
    expected_ids = ["S1", "S2", "S3", "S4", "S5"]
    if not isinstance(deliverables, list):
        mismatches.append("deliverables must be an array")
        return False
    ids = [
        item.get("id")
        for item in deliverables
        if isinstance(item, dict)
    ]
    if ids != expected_ids:
        mismatches.append("deliverables must list S1 through S5 in order")
        return False
    valid = True
    for item in deliverables:
        if not isinstance(item, dict):
            valid = False
            continue
        deliverable_id = str(item.get("id", ""))
        if item.get("status") != "pass":
            mismatches.append(f"{deliverable_id}.status must be pass")
            valid = False
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            mismatches.append(f"{deliverable_id}.evidence must be a non-empty array")
            valid = False
    return valid


def _milestone_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    milestone = package.get("milestone")
    if not isinstance(milestone, dict):
        mismatches.append("milestone must be an object")
        return False
    valid = True
    expected = {
        "id": "M1",
        "name": "可审查自动开发闭环样板",
        "budget": 18,
        "effort_unit": "施工队工时",
        "claim": "candidate-only engineering-chain milestone",
    }
    for key, value in expected.items():
        if milestone.get(key) != value:
            mismatches.append(f"milestone.{key} must be {value!r}")
            valid = False
    if "天" in json.dumps(milestone, ensure_ascii=False):
        mismatches.append("milestone must not use calendar-day estimates")
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
            mismatches.append(f"review_boundaries.{key} must be {str(value).lower()}")
            valid = False
    restricted_paths = boundaries.get("restricted_paths")
    required_paths = [
        "src/well_harness/controller.py",
        "src/well_harness/editable_control_model.py",
        "src/well_harness/static/requirements_intake/",
    ]
    if not isinstance(restricted_paths, list):
        mismatches.append("review_boundaries.restricted_paths must be an array")
        return False
    for path in required_paths:
        if path not in restricted_paths:
            mismatches.append(f"review_boundaries.restricted_paths must include {path}")
            valid = False
    return valid


def _gates_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    gates = package.get("deterministic_gates")
    if not isinstance(gates, dict):
        mismatches.append("deterministic_gates must be an object")
        return False
    valid = True
    expected_names = [
        "approved_repair_slices_artifact",
        "approved_candidate_task_queue_artifact",
        "queue_expansion_contract",
        "construction_readiness",
        "local_gate_entrypoint",
    ]
    for name in expected_names:
        if gates.get(name) != "pass":
            mismatches.append(f"deterministic_gates.{name} must be pass")
            valid = False
    return valid


def _child_artifacts_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    child_artifacts = package.get("child_artifacts")
    if not isinstance(child_artifacts, dict):
        mismatches.append("child_artifacts must be an object")
        return False

    valid = True
    repair_summary = _resolve_path(child_artifacts.get("approved_repair_slices_summary"), package_path)
    if repair_summary is None or not repair_summary.exists():
        mismatches.append("child_artifacts.approved_repair_slices_summary must exist")
        valid = False
    else:
        result = _run_json_command(
            [
                sys.executable,
                "scripts/verify_approved_repair_slices_artifact.py",
                "--summary",
                str(repair_summary),
                "--format",
                "json",
            ],
        )
        if result["returncode"] != 0 or result["payload"].get("status") != "pass":
            mismatches.append("approved_repair_slices_summary child artifact must verify")
            valid = False

    queue_summary = _resolve_path(
        child_artifacts.get("approved_candidate_task_queue_summary"),
        package_path,
    )
    if queue_summary is None or not queue_summary.exists():
        mismatches.append("child_artifacts.approved_candidate_task_queue_summary must exist")
        valid = False
    else:
        result = _run_json_command(
            [
                sys.executable,
                "scripts/verify_approved_candidate_task_queue_artifact.py",
                "--summary",
                str(queue_summary),
                "--format",
                "json",
            ],
        )
        if result["returncode"] != 0 or result["payload"].get("status") != "pass":
            mismatches.append("approved_candidate_task_queue_summary child artifact must verify")
            valid = False

    expansion_contract = _resolve_path(child_artifacts.get("queue_expansion_contract"), package_path)
    if expansion_contract is None or not expansion_contract.exists():
        mismatches.append("child_artifacts.queue_expansion_contract must exist")
        valid = False
    else:
        result = _run_json_command(
            [
                sys.executable,
                "scripts/verify_approved_candidate_task_queue_expansion_contract.py",
                "--contract",
                str(expansion_contract),
                "--format",
                "json",
            ],
        )
        if result["returncode"] != 0 or result["payload"].get("status") != "pass":
            mismatches.append("queue_expansion_contract child artifact must verify")
            valid = False

    readiness_packet = _resolve_path(child_artifacts.get("construction_readiness_packet"), package_path)
    if readiness_packet is None or not readiness_packet.exists():
        mismatches.append("child_artifacts.construction_readiness_packet must exist")
        valid = False
    else:
        try:
            readiness = _load_json(readiness_packet)
        except (OSError, json.JSONDecodeError) as exc:
            mismatches.append(f"construction_readiness_packet could not be loaded: {exc}")
            valid = False
        else:
            if readiness.get("status") != "pass":
                mismatches.append("construction_readiness_packet.status must be pass")
                valid = False
            if readiness.get("ready_for_long_running_development") is not True:
                mismatches.append(
                    "construction_readiness_packet.ready_for_long_running_development must be true"
                )
                valid = False

    project_manager_plan = _resolve_path(child_artifacts.get("project_manager_plan"), package_path)
    if project_manager_plan is None or not project_manager_plan.exists():
        mismatches.append("child_artifacts.project_manager_plan must exist")
        valid = False
    else:
        text = project_manager_plan.read_text(encoding="utf-8")
        if "施工队工时" not in text or "M1" not in text:
            mismatches.append("project_manager_plan must include M1 crew-hour planning")
            valid = False
    return valid


def verify_m1_review_package(package_path: Path = DEFAULT_PACKAGE_PATH) -> dict[str, Any]:
    mismatches: list[str] = []
    package: dict[str, Any] = {}
    try:
        package = _load_json(package_path)
    except (OSError, json.JSONDecodeError) as exc:
        mismatches.append(f"package could not be loaded: {exc}")
        return {
            "status": "fail",
            "package_id": "",
            "schema": PACKAGE_SCHEMA_ID,
            "schema_valid": False,
            "child_artifacts_valid": False,
            "boundary_valid": False,
            "milestone_valid": False,
            "deterministic_gates_valid": False,
            "deliverables_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {
                "review_package": str(package_path),
            },
        }

    schema_mismatches = _schema_mismatches(package)
    mismatches.extend(schema_mismatches)
    schema_valid = not schema_mismatches
    milestone_mismatches: list[str] = []
    boundary_mismatches: list[str] = []
    gates_mismatches: list[str] = []
    deliverables_mismatches: list[str] = []
    child_mismatches: list[str] = []
    milestone_valid = _milestone_valid(package, milestone_mismatches)
    boundary_valid = _boundary_valid(package, boundary_mismatches)
    deterministic_gates_valid = _gates_valid(package, gates_mismatches)
    deliverables_valid = _all_deliverables_pass(package, deliverables_mismatches)
    child_artifacts_valid = _child_artifacts_valid(
        package,
        package_path=package_path,
        mismatches=child_mismatches,
    )
    mismatches.extend(milestone_mismatches)
    mismatches.extend(boundary_mismatches)
    mismatches.extend(gates_mismatches)
    mismatches.extend(deliverables_mismatches)
    mismatches.extend(child_mismatches)

    package_id_valid = package.get("package_id") == PACKAGE_ID
    if not package_id_valid:
        mismatches.append(f"package_id must be {PACKAGE_ID}")

    status = (
        "pass"
        if (
            package.get("status") == "pass"
            and package_id_valid
            and schema_valid
            and child_artifacts_valid
            and boundary_valid
            and milestone_valid
            and deterministic_gates_valid
            and deliverables_valid
        )
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": PACKAGE_SCHEMA_ID,
        "schema_valid": schema_valid,
        "child_artifacts_valid": child_artifacts_valid,
        "boundary_valid": boundary_valid,
        "milestone_valid": milestone_valid,
        "deterministic_gates_valid": deterministic_gates_valid,
        "deliverables_valid": deliverables_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "review_package": str(package_path),
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m1_review_package(args.package_path)
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
