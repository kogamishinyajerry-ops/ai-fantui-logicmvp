#!/usr/bin/env python3
"""Validate the append-only expansion contract for approved candidate queues."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_SCHEMA_ID = (
    "https://well-harness.local/json_schema/"
    "approved_candidate_task_queue_expansion_contract_v0_1.schema.json"
)
CONTRACT_SCHEMA_PATH = (
    PROJECT_ROOT
    / "docs"
    / "json_schema"
    / "approved_candidate_task_queue_expansion_contract_v0_1.schema.json"
)
DEFAULT_CONTRACT_PATH = (
    PROJECT_ROOT
    / "tests"
    / "fixtures"
    / "approved_candidate_task_queue_expansion_contract_v0_1.json"
)
CURRENT_QUEUE_ID = "approved-candidate-task-queue-v0.1"
NEXT_QUEUE_ID = "approved-candidate-task-queue-v0.2"
REQUIRED_NEW_TASK_FIELDS = [
    "schema_update",
    "fixture_update",
    "checker_update",
    "focused_test",
    "make_target",
    "ci_checker_step",
    "child_review_packet_export",
    "readiness_preflight",
    "approved_task_shell",
    "boundary_check",
]
REQUIRED_FORBIDDEN_FILES = [
    "src/well_harness/controller.py",
    "src/well_harness/editable_control_model.py",
    "src/well_harness/static/requirements_intake/requirements_intake.css",
    "src/well_harness/static/requirements_intake/requirements_intake.js",
    "src/well_harness/static/requirements_intake/index.html",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify approved candidate task queue expansion contract.",
    )
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT_PATH,
        help="Path to approved_candidate_task_queue_expansion_contract_v0_1.json.",
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


def _schema_mismatches(contract: dict[str, Any]) -> list[str]:
    schema = _load_json(CONTRACT_SCHEMA_PATH)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(contract),
        key=lambda error: list(error.absolute_path),
    )
    mismatches: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(
            f"approved candidate task queue expansion contract schema validation failed{location}: {error.message}"
        )
    return mismatches


def verify_expansion_contract(contract_path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    mismatches: list[str] = []
    contract: dict[str, Any] = {}
    try:
        contract = _load_json(contract_path)
    except (OSError, json.JSONDecodeError) as exc:
        mismatches.append(f"contract could not be loaded: {exc}")
        return {
            "status": "fail",
            "contract_schema": CONTRACT_SCHEMA_ID,
            "contract_schema_valid": False,
            "contract_valid": False,
            "current_queue_contract_fixed": False,
            "append_only_ready": False,
            "next_queue_id": "",
            "mismatches": mismatches,
            "artifact_paths": {
                "contract": str(contract_path),
                "schema": str(CONTRACT_SCHEMA_PATH),
            },
        }

    schema_mismatches = _schema_mismatches(contract)
    mismatches.extend(schema_mismatches)
    contract_schema_valid = not schema_mismatches

    current = contract.get("current_queue_contract")
    current_queue_contract_fixed = False
    if not isinstance(current, dict):
        mismatches.append("current_queue_contract must be an object")
    else:
        current_queue_contract_fixed = (
            current.get("queue_id") == CURRENT_QUEUE_ID
            and current.get("fixed_item_count") == 3
            and current.get("mutable") is False
        )
        if not current_queue_contract_fixed:
            mismatches.append("current_queue_contract must keep v0.1 fixed and immutable")

    expansion = contract.get("expansion_policy")
    append_only_ready = False
    next_queue_id = ""
    if not isinstance(expansion, dict):
        mismatches.append("expansion_policy must be an object")
    else:
        next_queue_id = str(expansion.get("next_queue_id", ""))
        append_only_ready = (
            expansion.get("append_only") is True
            and next_queue_id == NEXT_QUEUE_ID
            and expansion.get("new_task_requires") == REQUIRED_NEW_TASK_FIELDS
        )
        if not append_only_ready:
            mismatches.append("expansion_policy must be append-only and list all required controls")

    forbidden_files = contract.get("forbidden_files")
    if not isinstance(forbidden_files, list):
        mismatches.append("forbidden_files must be an array")
    else:
        for file_path in REQUIRED_FORBIDDEN_FILES:
            if file_path not in forbidden_files:
                mismatches.append(f"forbidden_files must include {file_path}")

    status = (
        "pass"
        if contract_schema_valid and current_queue_contract_fixed and append_only_ready and not mismatches
        else "fail"
    )
    return {
        "status": status,
        "contract_schema": CONTRACT_SCHEMA_ID,
        "contract_schema_valid": contract_schema_valid,
        "contract_valid": not mismatches,
        "current_queue_contract_fixed": current_queue_contract_fixed,
        "append_only_ready": append_only_ready,
        "next_queue_id": next_queue_id,
        "mismatches": mismatches,
        "artifact_paths": {
            "contract": str(contract_path),
            "schema": str(CONTRACT_SCHEMA_PATH),
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_expansion_contract(args.contract)
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"status: {payload['status']}")
        print(f"contract_schema_valid: {payload['contract_schema_valid']}")
        print(f"current_queue_contract_fixed: {payload['current_queue_contract_fixed']}")
        print(f"append_only_ready: {payload['append_only_ready']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
