#!/usr/bin/env python3
"""Validate the M8 fast construction gate package."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.agent_fast_construction_gate import (
    DEFAULT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR,
    FORBIDDEN_FAST_COMMAND_TOKENS,
    M8_PACKAGE_NAME,
    M8_SCHEMA_ID,
    validate_m8_fast_construction_gate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE_PATH = DEFAULT_M8_FAST_CONSTRUCTION_GATE_ARTIFACT_DIR / M8_PACKAGE_NAME
EXPECTED_GATES = {
    "candidate_review_packet_export": "pass",
    "queue_v0_2_fixture_preflight": "pass",
    "queue_v0_2_artifact_checker": "pass",
    "queue_expansion_contract": "pass",
    "m6_template_contract": "pass",
    "boundary": "pass",
    "local_gate": "pass",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify multi_agent_m8_fast_construction_gate_v0_1.json.",
    )
    parser.add_argument(
        "--package",
        dest="package_path",
        type=Path,
        default=DEFAULT_PACKAGE_PATH,
        help="Path to multi_agent_m8_fast_construction_gate_v0_1.json.",
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


def _run_json_command(args: list[str]) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=90,
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


def _schema_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    try:
        validate_m8_fast_construction_gate(package)
    except ValueError as exc:
        mismatches.append(str(exc))
        return False
    return True


def _fast_policy_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    policy = package.get("gate_policy")
    aggregate = package.get("aggregate")
    validation_budget = package.get("validation_budget")
    fast_checks = package.get("fast_checks")
    if not isinstance(policy, dict) or not isinstance(aggregate, dict) or not isinstance(validation_budget, dict):
        mismatches.append("gate_policy, aggregate, and validation_budget must be objects")
        return False
    if not isinstance(fast_checks, list):
        mismatches.append("fast_checks must be an array")
        return False

    valid = True
    expected_policy = {
        "entrypoint": "make multi-agent-fast-construction-gate",
        "full_pytest_excluded": True,
        "not_a_release_gate": True,
        "max_expected_runtime_seconds": 60,
    }
    for key, value in expected_policy.items():
        if policy.get(key) != value:
            mismatches.append(f"gate_policy.{key} must be {value!r}")
            valid = False
    if validation_budget.get("full_pytest_is_per_milestone_gate") is not True:
        mismatches.append("validation_budget.full_pytest_is_per_milestone_gate must be true")
        valid = False
    if aggregate.get("full_pytest_excluded_from_fast_gate") is not True:
        mismatches.append("aggregate.full_pytest_excluded_from_fast_gate must be true")
        valid = False
    commands = [
        str(check.get("command", ""))
        for check in fast_checks
        if isinstance(check, dict)
    ]
    if any(
        any(token in command for token in FORBIDDEN_FAST_COMMAND_TOKENS)
        for command in commands
    ):
        mismatches.append("fast_checks must not include full pytest or GSD validation commands")
        valid = False
    if len(fast_checks) != 5:
        mismatches.append("fast_checks must contain exactly five lightweight checks")
        valid = False
    return valid


def _gates_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    gates = package.get("deterministic_gates")
    if not isinstance(gates, dict):
        mismatches.append("deterministic_gates must be an object")
        return False
    valid = True
    if gates != EXPECTED_GATES:
        mismatches.append("deterministic_gates must list all M8 gates as pass")
        valid = False
    fast_checks = package.get("fast_checks", [])
    if isinstance(fast_checks, list):
        for check in fast_checks:
            if not isinstance(check, dict):
                mismatches.append("fast_checks entries must be objects")
                valid = False
                continue
            if check.get("status") != "pass":
                mismatches.append(f"fast_checks.{check.get('name', '<unknown>')}.status must be pass")
                valid = False
            if check.get("returncode") != 0:
                mismatches.append(
                    f"fast_checks.{check.get('name', '<unknown>')}.returncode must be 0"
                )
                valid = False
    return valid


def _queue_v0_2_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    artifact_paths = package.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        mismatches.append("artifact_paths must be an object")
        return False
    queue_summary_path = _resolve_path(artifact_paths.get("queue_v0_2_summary"), package_path)
    if queue_summary_path is None or not queue_summary_path.exists():
        mismatches.append("artifact_paths.queue_v0_2_summary must exist")
        return False
    result = _run_json_command(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_v0_2_artifact.py",
            "--format",
            "json",
            "--summary",
            str(queue_summary_path),
        ],
    )
    payload = result["payload"]
    valid = (
        result["returncode"] == 0
        and payload.get("status") == "pass"
        and payload.get("child_review_exports_valid") is True
        and payload.get("aggregate", {}).get("task_count") == 4
        and payload.get("aggregate", {}).get("converged") == 4
    )
    if not valid:
        mismatches.append("queue_v0_2_summary must validate with four converged child exports")
        for item in payload.get("mismatches", []):
            mismatches.append(str(item))
    return valid


def _m6_template_valid(
    package: dict[str, Any],
    *,
    package_path: Path,
    mismatches: list[str],
) -> bool:
    artifact_paths = package.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        mismatches.append("artifact_paths must be an object")
        return False
    m6_package_path = _resolve_path(artifact_paths.get("m6_template_package"), package_path)
    if m6_package_path is None or not m6_package_path.exists():
        mismatches.append("artifact_paths.m6_template_package must exist")
        return False
    result = _run_json_command(
        [
            sys.executable,
            "scripts/verify_multi_agent_m6_queue_extension_template.py",
            "--format",
            "json",
            "--package",
            str(m6_package_path),
        ],
    )
    payload = result["payload"]
    valid = (
        result["returncode"] == 0
        and payload.get("status") == "pass"
        and payload.get("boundary_valid") is True
        and payload.get("task_class_matrix_valid") is True
    )
    if not valid:
        mismatches.append("m6_template_package must validate before the M8 fast gate can pass")
        for item in payload.get("mismatches", []):
            mismatches.append(str(item))
    return valid


def _boundary_valid(package: dict[str, Any], mismatches: list[str]) -> bool:
    boundaries = package.get("review_boundaries")
    aggregate = package.get("aggregate")
    if not isinstance(boundaries, dict) or not isinstance(aggregate, dict):
        mismatches.append("review_boundaries and aggregate must be objects")
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
        if key in aggregate and aggregate.get(key) != value:
            mismatches.append(f"aggregate.{key} must be {value!r}")
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
    if aggregate.get("open_findings") != []:
        mismatches.append("aggregate.open_findings must be empty")
        valid = False
    if aggregate.get("ready_for_slice_preflight") is not True:
        mismatches.append("aggregate.ready_for_slice_preflight must be true")
        valid = False
    return valid


def verify_m8_fast_construction_gate(
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
            "schema": M8_SCHEMA_ID,
            "schema_valid": False,
            "fast_policy_valid": False,
            "gates_valid": False,
            "queue_v0_2_valid": False,
            "m6_template_valid": False,
            "boundary_valid": False,
            "mismatches": mismatches,
            "artifact_paths": {"fast_gate_package": str(package_path)},
        }

    schema_mismatches: list[str] = []
    policy_mismatches: list[str] = []
    gate_mismatches: list[str] = []
    queue_mismatches: list[str] = []
    m6_mismatches: list[str] = []
    boundary_mismatches: list[str] = []
    schema_valid = _schema_valid(package, schema_mismatches)
    fast_policy_valid = _fast_policy_valid(package, policy_mismatches)
    gates_valid = _gates_valid(package, gate_mismatches)
    queue_v0_2_valid = _queue_v0_2_valid(
        package,
        package_path=package_path,
        mismatches=queue_mismatches,
    )
    m6_template_valid = _m6_template_valid(
        package,
        package_path=package_path,
        mismatches=m6_mismatches,
    )
    boundary_valid = _boundary_valid(package, boundary_mismatches)
    mismatches.extend(schema_mismatches)
    mismatches.extend(policy_mismatches)
    mismatches.extend(gate_mismatches)
    mismatches.extend(queue_mismatches)
    mismatches.extend(m6_mismatches)
    mismatches.extend(boundary_mismatches)
    status = (
        "pass"
        if (
            schema_valid
            and fast_policy_valid
            and gates_valid
            and queue_v0_2_valid
            and m6_template_valid
            and boundary_valid
        )
        else "fail"
    )
    return {
        "status": status,
        "package_id": str(package.get("package_id", "")),
        "schema": M8_SCHEMA_ID,
        "schema_valid": schema_valid,
        "fast_policy_valid": fast_policy_valid,
        "gates_valid": gates_valid,
        "queue_v0_2_valid": queue_v0_2_valid,
        "m6_template_valid": m6_template_valid,
        "boundary_valid": boundary_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "fast_gate_package": str(package_path),
            "queue_v0_2_summary": str(
                package.get("artifact_paths", {}).get("queue_v0_2_summary", "")
            ),
            "m6_template_package": str(
                package.get("artifact_paths", {}).get("m6_template_package", "")
            ),
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_m8_fast_construction_gate(args.package_path)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"package_id: {payload['package_id']}")
        print(f"status: {payload['status']}")
        print(f"schema_valid: {payload['schema_valid']}")
        print(f"fast_policy_valid: {payload['fast_policy_valid']}")
        print(f"queue_v0_2_valid: {payload['queue_v0_2_valid']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
