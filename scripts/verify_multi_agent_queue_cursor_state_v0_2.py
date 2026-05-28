#!/usr/bin/env python3
"""Validate the M11 queue cursor/resume state artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema

from scripts.verify_multi_agent_queue_run_ledger_v0_2 import verify_multi_agent_queue_run_ledger


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURSOR_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-queue-cursor-state-v0-2")
CURSOR_NAME = "multi_agent_queue_cursor_state_v0_2.json"
LEDGER_SCHEMA_NAME = "multi_agent_queue_run_ledger_v0_2.schema.json"
CURSOR_SCHEMA_ID = (
    "https://well-harness.local/json_schema/multi_agent_queue_cursor_state_v0_2.schema.json"
)
CURSOR_SCHEMA_NAME = "multi_agent_queue_cursor_state_v0_2.schema.json"
CURSOR_KIND = "ai-fantui-multi-agent-queue-cursor-state"
CURSOR_ID = "multi-agent-queue-cursor-state-v0.2"
CURSOR_GATE_ID = "multi-agent-queue-cursor-state"
SOURCE_LEDGER_ID = "multi-agent-queue-run-ledger-v0.2"
SOURCE_LEDGER_GATE_ID = "multi-agent-queue-run-ledger"
EXPECTED_IDLE_COMPLETED_RECORD_IDS = [
    "RUN-QUEUE-001",
    "RUN-QUEUE-002",
    "RUN-QUEUE-003",
    "RUN-QUEUE-004",
    "RUN-QUEUE-005",
    "RUN-QUEUE-006",
    "RUN-QUEUE-007",
    "RUN-QUEUE-008",
    "RUN-QUEUE-009",
    "RUN-QUEUE-010",
    "RUN-QUEUE-011",
]
EXPECTED_READY_COMPLETED_RECORD_IDS = EXPECTED_IDLE_COMPLETED_RECORD_IDS[:10]
OPEN_RECORD_ID = "RUN-QUEUE-011"
OPEN_QUEUE_ITEM_ID = "queue-safety-output-command-conflict-repair"
OPEN_TASK_ID = "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001"
EXPECTED_OPEN_CURSOR_RECORD = {
    "record_id": OPEN_RECORD_ID,
    "queue_item_id": OPEN_QUEUE_ITEM_ID,
    "task_id": OPEN_TASK_ID,
    "status": "approved_open",
}
EXPECTED_SELECTED_OPEN_RECORD = {
    "record_id": OPEN_RECORD_ID,
    "queue_item_id": OPEN_QUEUE_ITEM_ID,
    "task_id": OPEN_TASK_ID,
    "status": "ready_to_resume",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify the M11 queue cursor state artifact.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_CURSOR_ARTIFACT_DIR,
        help="Directory containing multi_agent_queue_cursor_state_v0_2.json.",
    )
    parser.add_argument(
        "--cursor",
        type=Path,
        default=None,
        help="Explicit cursor path. Overrides --artifact-dir.",
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


def _cursor_path(*, artifact_dir: Path, cursor_path: Path | None = None) -> Path:
    if cursor_path is not None:
        return cursor_path
    return artifact_dir / CURSOR_NAME


def _load_schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / CURSOR_SCHEMA_NAME)


def _load_ledger_schema() -> dict[str, Any]:
    return _load_json(PROJECT_ROOT / "docs" / "json_schema" / LEDGER_SCHEMA_NAME)


def _schema_mismatches(cursor: dict[str, Any]) -> list[str]:
    errors = sorted(
        jsonschema.Draft202012Validator(_load_schema()).iter_errors(cursor),
        key=lambda error: list(error.absolute_path),
    )
    mismatches: list[str] = []
    for error in errors:
        path = ".".join(str(part) for part in error.absolute_path)
        location = f" at {path}" if path else ""
        mismatches.append(f"queue cursor state schema validation failed{location}: {error.message}")
    return mismatches


def _resolve_path(path_value: Any, cursor_path: Path) -> Path | None:
    if not isinstance(path_value, str) or not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return cursor_path.parent / path


def _check_basic_fields(cursor: dict[str, Any], mismatches: list[str]) -> None:
    expected = {
        "$schema": CURSOR_SCHEMA_ID,
        "kind": CURSOR_KIND,
        "gate_id": CURSOR_GATE_ID,
        "cursor_id": CURSOR_ID,
        "source_ledger_id": SOURCE_LEDGER_ID,
        "source_ledger_gate_id": SOURCE_LEDGER_GATE_ID,
        "status": "pass",
    }
    for key, expected_value in expected.items():
        if cursor.get(key) != expected_value:
            mismatches.append(f"{key} must be {expected_value!r}")


def _record_is_converged(record: dict[str, Any]) -> bool:
    return (
        record.get("approved_task_shell", {}).get("approval_status") == "approved"
        and record.get("approved_task_shell", {}).get("status") == "executed_limited"
        and record.get("repair", {}).get("status") == "pass"
        and record.get("repair", {}).get("reviewer_status") == "converged"
        and record.get("repair", {}).get("finding_chain_statuses") == ["converged"]
        and record.get("boundary", {}).get("controller_truth_modified") is False
        and record.get("boundary", {}).get("ui_layout_modified") is False
    )


def _record_is_approved_open(record: dict[str, Any]) -> bool:
    task = record.get("task", {})
    shell = record.get("approved_task_shell", {})
    repair = record.get("repair", {})
    boundary = record.get("boundary", {})
    return (
        record.get("record_id") == OPEN_RECORD_ID
        and record.get("queue_item_id") == OPEN_QUEUE_ITEM_ID
        and isinstance(task, dict)
        and task.get("task_id") == OPEN_TASK_ID
        and isinstance(shell, dict)
        and shell.get("approval_status") == "approved"
        and shell.get("selected_task_id") == OPEN_TASK_ID
        and shell.get("status") == "pending_restricted_execution"
        and isinstance(repair, dict)
        and repair.get("status") == "pending"
        and repair.get("reviewer_status") == "approved_open"
        and repair.get("finding_chain_statuses") == ["approved_open"]
        and isinstance(boundary, dict)
        and boundary.get("controller_truth_modified") is False
        and boundary.get("ui_layout_modified") is False
    )


def _check_ready_source_ledger(
    cursor: dict[str, Any],
    ledger_path: Path,
    mismatches: list[str],
) -> bool:
    try:
        ledger = _load_json(ledger_path)
    except (OSError, json.JSONDecodeError) as exc:
        mismatches.append(f"source ledger could not be loaded: {exc}")
        return False
    schema_errors = sorted(
        jsonschema.Draft202012Validator(_load_ledger_schema()).iter_errors(ledger),
        key=lambda error: list(error.absolute_path),
    )
    if schema_errors:
        for error in schema_errors:
            path = ".".join(str(part) for part in error.absolute_path)
            location = f" at {path}" if path else ""
            mismatches.append(f"source ledger schema validation failed{location}: {error.message}")
        return False

    records = ledger.get("run_records")
    if not isinstance(records, list):
        mismatches.append("source ledger run_records must be an array")
        return False
    valid = True
    if len(records) != 11:
        mismatches.append("ready source ledger must contain ten completed records plus one approved open record")
        valid = False
    completed = records[:10]
    open_records = records[10:]
    if [record.get("record_id") for record in completed if isinstance(record, dict)] != (
        EXPECTED_READY_COMPLETED_RECORD_IDS
    ):
        mismatches.append("ready source ledger completed prefix must preserve RUN-QUEUE-001 through RUN-QUEUE-010")
        valid = False
    for record in completed:
        if not isinstance(record, dict) or not _record_is_converged(record):
            record_id = record.get("record_id", "") if isinstance(record, dict) else ""
            mismatches.append(f"{record_id}.source_ledger.completed_record must be converged")
            valid = False
    if len(open_records) != 1 or not isinstance(open_records[0], dict):
        mismatches.append("ready source ledger must contain exactly one approved open record")
        valid = False
    elif not _record_is_approved_open(open_records[0]):
        mismatches.append(f"{OPEN_RECORD_ID}.source_ledger.open_record must be approved_open")
        valid = False

    aggregate = ledger.get("aggregate")
    if not isinstance(aggregate, dict):
        mismatches.append("source ledger aggregate must be an object")
        valid = False
    else:
        expected = {
            "record_count": 11,
            "source_queue_task_count": 11,
            "executed_limited": 10,
            "converged": 10,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
            "ledger_append_only": True,
        }
        for key, expected_value in expected.items():
            if aggregate.get(key) != expected_value:
                mismatches.append(f"source ledger aggregate.{key} must be {expected_value!r}")
                valid = False

    append_only = ledger.get("append_only")
    if not isinstance(append_only, dict):
        mismatches.append("source ledger append_only must be an object")
        valid = False
    else:
        source_order = append_only.get("source_queue_order")
        if not isinstance(source_order, list) or source_order[-1:] != [OPEN_QUEUE_ITEM_ID]:
            mismatches.append("source ledger append_only.source_queue_order must append the open queue item")
            valid = False
        if append_only.get("record_sequence_preserves_queue_order") is not True:
            mismatches.append("source ledger append_only must preserve queue order")
            valid = False

    if cursor.get("open_records") != [EXPECTED_OPEN_CURSOR_RECORD]:
        mismatches.append("cursor open_records must mirror the approved open source ledger record")
        valid = False
    return valid


def _check_source_ledger(cursor: dict[str, Any], cursor_path: Path, mismatches: list[str]) -> bool:
    ledger_path = _resolve_path(
        cursor.get("artifact_paths", {}).get("source_ledger"),
        cursor_path,
    )
    if ledger_path is None:
        mismatches.append("artifact_paths.source_ledger is required")
        return False
    if cursor.get("state_status") == "ready_to_resume":
        return _check_ready_source_ledger(cursor, ledger_path, mismatches)
    result = verify_multi_agent_queue_run_ledger(ledger_path=ledger_path)
    if result.get("status") != "pass":
        mismatches.append("source ledger checker must pass")
        mismatches.extend(str(item) for item in result.get("mismatches", []))
        return False
    return True


def _check_completed_records(cursor: dict[str, Any], mismatches: list[str]) -> bool:
    records = cursor.get("completed_records")
    if not isinstance(records, list):
        mismatches.append("completed_records must be an array")
        return False
    valid = True
    record_ids = [record.get("record_id") for record in records if isinstance(record, dict)]
    expected_record_ids = (
        EXPECTED_READY_COMPLETED_RECORD_IDS
        if cursor.get("state_status") == "ready_to_resume"
        else EXPECTED_IDLE_COMPLETED_RECORD_IDS
    )
    if record_ids != expected_record_ids:
        mismatches.append("completed_records must preserve converged ledger order")
        valid = False
    for record in records:
        if not isinstance(record, dict):
            mismatches.append("completed_records entries must be objects")
            valid = False
            continue
        record_id = str(record.get("record_id", ""))
        if record.get("status") != "converged":
            mismatches.append(f"{record_id}.completed_records.status must be converged")
            valid = False
        if not record.get("task_id"):
            mismatches.append(f"{record_id}.completed_records.task_id is required")
            valid = False
    return valid


def _check_resume_selection(cursor: dict[str, Any], mismatches: list[str]) -> bool:
    valid = True
    state_status = cursor.get("state_status")
    open_records = cursor.get("open_records")
    selected = cursor.get("selected_next_record")
    position = cursor.get("cursor_position")
    if state_status == "ready_to_resume":
        expected_selected = EXPECTED_SELECTED_OPEN_RECORD
        expected_position = {
            "last_completed_record_id": "RUN-QUEUE-010",
            "last_completed_queue_item_id": "queue-safety-unreachable-state-repair",
            "next_record_id": OPEN_RECORD_ID,
            "next_queue_item_id": OPEN_QUEUE_ITEM_ID,
        }
        if open_records != [EXPECTED_OPEN_CURSOR_RECORD]:
            mismatches.append("open_records must contain the approved open resume record")
            valid = False
        if selected != expected_selected:
            mismatches.append("selected_next_record must select first approved open record")
            valid = False
        expected_next_action = "resume_next_open_record"
    else:
        expected_position = {
            "last_completed_record_id": "RUN-QUEUE-011",
            "last_completed_queue_item_id": "queue-safety-output-command-conflict-repair",
            "next_record_id": "",
            "next_queue_item_id": "",
        }
        if open_records != []:
            mismatches.append("open_records must be empty while all ledger records are converged")
            valid = False
        if selected != {"record_id": "", "queue_item_id": "", "task_id": "", "status": "none"}:
            mismatches.append("selected_next_record must be empty when no approved open record exists")
            valid = False
        expected_next_action = "wait_for_append_only_queue_growth"
    if position != expected_position:
        mismatches.append("cursor_position must match completed and selected resume records")
        valid = False
    policy = cursor.get("resume_policy")
    if not isinstance(policy, dict):
        mismatches.append("resume_policy must be an object")
        valid = False
    else:
        if policy.get("policy_id") != "first-approved-open-item-v0.2":
            mismatches.append("resume_policy.policy_id must be first-approved-open-item-v0.2")
            valid = False
        if policy.get("next_action") != expected_next_action:
            mismatches.append(f"resume_policy.next_action must be {expected_next_action}")
            valid = False
    return valid


def _check_aggregate(cursor: dict[str, Any], mismatches: list[str]) -> bool:
    if cursor.get("state_status") == "ready_to_resume":
        expected = {
            "source_ledger_record_count": 11,
            "completed_count": 10,
            "open_approved_count": 1,
            "blocked_count": 0,
            "ready_for_resume": True,
            "idle": False,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        }
    else:
        expected = {
            "source_ledger_record_count": 11,
            "completed_count": 11,
            "open_approved_count": 0,
            "blocked_count": 0,
            "ready_for_resume": False,
            "idle": True,
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        }
    aggregate = cursor.get("aggregate")
    if not isinstance(aggregate, dict):
        mismatches.append("aggregate must be an object")
        return False
    valid = True
    for key, expected_value in expected.items():
        if aggregate.get(key) != expected_value:
            mismatches.append(f"aggregate.{key} must be {expected_value!r}")
            valid = False
    return valid


def _check_gates(cursor: dict[str, Any], mismatches: list[str]) -> bool:
    gates = cursor.get("deterministic_gates")
    if not isinstance(gates, dict):
        mismatches.append("deterministic_gates must be an object")
        return False
    valid = True
    for gate_name, status in gates.items():
        if status != "pass":
            mismatches.append(f"deterministic_gates.{gate_name} must be pass")
            valid = False
    return valid


def verify_multi_agent_queue_cursor_state(
    *,
    artifact_dir: Path = DEFAULT_CURSOR_ARTIFACT_DIR,
    cursor_path: Path | None = None,
) -> dict[str, Any]:
    resolved_cursor_path = _cursor_path(
        artifact_dir=artifact_dir,
        cursor_path=cursor_path,
    )
    try:
        cursor = _load_json(resolved_cursor_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "gate_id": "",
            "cursor_id": "",
            "cursor_schema": CURSOR_SCHEMA_ID,
            "cursor_schema_valid": False,
            "source_ledger_valid": False,
            "cursor_monotonicity_valid": False,
            "completed_records_valid": False,
            "resume_selection_valid": False,
            "aggregate_valid": False,
            "mismatches": [f"cursor could not be loaded: {exc}"],
            "artifact_paths": {
                "cursor_state": str(resolved_cursor_path),
                "source_ledger": "",
            },
        }

    mismatches = _schema_mismatches(cursor)
    cursor_schema_valid = not mismatches
    _check_basic_fields(cursor, mismatches)
    source_ledger_valid = _check_source_ledger(cursor, resolved_cursor_path, mismatches)
    completed_records_valid = _check_completed_records(cursor, mismatches)
    resume_selection_valid = _check_resume_selection(cursor, mismatches)
    aggregate_valid = _check_aggregate(cursor, mismatches)
    gates_valid = _check_gates(cursor, mismatches)
    cursor_monotonicity_valid = (
        completed_records_valid and resume_selection_valid and aggregate_valid
    )
    status = "pass" if not mismatches and gates_valid else "fail"
    source_ledger_path = ""
    if isinstance(cursor.get("artifact_paths"), dict):
        source_ledger_path = str(cursor["artifact_paths"].get("source_ledger", ""))
    return {
        "status": status,
        "gate_id": str(cursor.get("gate_id", "")),
        "cursor_id": str(cursor.get("cursor_id", "")),
        "cursor_schema": CURSOR_SCHEMA_ID,
        "cursor_schema_valid": cursor_schema_valid,
        "source_ledger_valid": source_ledger_valid,
        "cursor_monotonicity_valid": cursor_monotonicity_valid,
        "completed_records_valid": completed_records_valid,
        "resume_selection_valid": resume_selection_valid,
        "aggregate_valid": aggregate_valid,
        "mismatches": mismatches,
        "artifact_paths": {
            "cursor_state": str(resolved_cursor_path),
            "source_ledger": source_ledger_path,
        },
    }


def main() -> int:
    args = _parse_args()
    payload = verify_multi_agent_queue_cursor_state(
        artifact_dir=args.artifact_dir,
        cursor_path=args.cursor,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"gate_id: {payload['gate_id']}")
        print(f"status: {payload['status']}")
        print(f"cursor_schema_valid: {payload['cursor_schema_valid']}")
        print(f"source_ledger_valid: {payload['source_ledger_valid']}")
        print(f"cursor_monotonicity_valid: {payload['cursor_monotonicity_valid']}")
        print(f"resume_selection_valid: {payload['resume_selection_valid']}")
        print(f"cursor_state: {payload['artifact_paths']['cursor_state']}")
        for mismatch in payload["mismatches"]:
            print(f"mismatch: {mismatch}")
    return 0 if payload.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
