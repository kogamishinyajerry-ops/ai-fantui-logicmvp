#!/usr/bin/env python3
"""Generate a resumable cursor state from the multi-agent queue run ledger."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from well_harness.agent_development_slice import DEFAULT_AGENT_OUTPUT_FIXTURE_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURSOR_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-queue-cursor-state-v0-2")
LEDGER_NAME = "multi_agent_queue_run_ledger_v0_2.json"
CURSOR_SCHEMA_ID = (
    "https://well-harness.local/json_schema/multi_agent_queue_cursor_state_v0_2.schema.json"
)
CURSOR_KIND = "ai-fantui-multi-agent-queue-cursor-state"
CURSOR_ID = "multi-agent-queue-cursor-state-v0.2"
CURSOR_GATE_ID = "multi-agent-queue-cursor-state"
CURSOR_NAME = "multi_agent_queue_cursor_state_v0_2.json"
SOURCE_LEDGER_ID = "multi-agent-queue-run-ledger-v0.2"
SOURCE_LEDGER_GATE_ID = "multi-agent-queue-run-ledger"
RESUME_POLICY_ID = "first-approved-open-item-v0.2"
IDLE_REASON = (
    "All approved queue run records are converged; wait for the next append-only queue item."
)
READY_REASON = (
    "An approved open queue run record exists; resume RUN-QUEUE-011 before appending more work."
)
OPEN_RECORD_ID = "RUN-QUEUE-011"
OPEN_QUEUE_ITEM_ID = "queue-safety-output-command-conflict-repair"
OPEN_TASK_ID = "TASK-CE-CHECK-OUTPUT-COMMAND-CONFLICT-001"
OPEN_SOURCE_FINDING_CODE = "CHECK_OUTPUT_COMMAND_CONFLICT_001"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run M11 queue cursor generation from the M10 run ledger.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_CURSOR_ARTIFACT_DIR,
        help="Directory where cursor artifacts will be written.",
    )
    parser.add_argument(
        "--input-packet",
        type=Path,
        default=DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
        help="Candidate agent_output_contract_v0_1 packet to seed ledger generation.",
    )
    parser.add_argument(
        "--resume-mode",
        choices=("idle", "ready-to-resume"),
        default="idle",
        help="Cursor scenario to generate. idle uses the current converged ledger; ready-to-resume appends one approved open record fixture.",
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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _deepcopy_json(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload))


def _run_source_ledger(
    *,
    ledger_artifact_dir: Path,
    input_packet_path: Path,
) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_multi_agent_queue_run_ledger_v0_2.py",
            "--format",
            "json",
            "--artifact-dir",
            str(ledger_artifact_dir),
            "--input-packet",
            str(input_packet_path),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=300,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"source ledger did not emit JSON: {result.stderr}") from exc
    if result.returncode != 0 or payload.get("status") != "pass":
        raise RuntimeError(f"source ledger did not pass: {payload.get('status')}")
    return payload


def _verify_source_ledger(ledger_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/verify_multi_agent_queue_run_ledger_v0_2.py",
            "--ledger",
            str(ledger_path),
            "--format",
            "json",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "mismatches": [result.stderr]}
    payload["returncode"] = result.returncode
    return payload


def _cursor_record(record: dict[str, Any], status: str) -> dict[str, str]:
    task = record.get("task", {})
    return {
        "record_id": str(record.get("record_id", "")),
        "queue_item_id": str(record.get("queue_item_id", "")),
        "task_id": str(task.get("task_id", "")),
        "status": status,
    }


def _record_is_converged(record: dict[str, Any]) -> bool:
    return (
        record.get("approved_task_shell", {}).get("status") == "executed_limited"
        and record.get("approved_task_shell", {}).get("approval_status") == "approved"
        and record.get("repair", {}).get("status") == "pass"
        and record.get("repair", {}).get("reviewer_status") == "converged"
        and record.get("repair", {}).get("finding_chain_statuses") == ["converged"]
        and record.get("boundary", {}).get("controller_truth_modified") is False
        and record.get("boundary", {}).get("ui_layout_modified") is False
    )


def _approved_open_record(sequence: int) -> dict[str, Any]:
    return {
        "record_id": f"RUN-QUEUE-{sequence:03d}",
        "sequence": sequence,
        "queue_item_id": OPEN_QUEUE_ITEM_ID,
        "slice_id": "safety-output-command-conflict-approved-candidate-repair-slice",
        "source_finding_code": OPEN_SOURCE_FINDING_CODE,
        "task": {
            "task_id": OPEN_TASK_ID,
            "target_agent": "LogicIRRepairAgent",
            "task_type": "repair_candidate_logic_ir",
        },
        "preflight": {
            "command": "make multi-agent-fast-construction-gate",
            "gate_id": "multi-agent-m8-fast-construction-gate",
            "returncode": 0,
            "status": "pass",
        },
        "approved_task_shell": {
            "status": "pending_restricted_execution",
            "approval_status": "approved",
            "selected_task_id": OPEN_TASK_ID,
        },
        "repair": {
            "status": "pending",
            "reviewer_status": "approved_open",
            "finding_chain_statuses": ["approved_open"],
        },
        "review_export": {
            "path": "",
            "reviewer_status": "",
            "finding_chain_statuses": [],
        },
        "boundary": {
            "truth_effect": "none",
            "controller_truth_modified": False,
            "ui_layout_modified": False,
        },
    }


def _ledger_with_approved_open_record(
    ledger: dict[str, Any],
    *,
    ledger_path: Path,
) -> dict[str, Any]:
    payload = _deepcopy_json(ledger)
    records = [
        record
        for record in payload.get("run_records", [])
        if isinstance(record, dict)
    ]
    if any(
        record.get("queue_item_id") == OPEN_QUEUE_ITEM_ID and _record_is_approved_open(record)
        for record in records
    ):
        artifact_paths = payload.get("artifact_paths", {})
        if isinstance(artifact_paths, dict):
            artifact_paths["ledger"] = str(ledger_path)
        return payload
    replaced_existing_record = False
    for index, record in enumerate(records):
        if record.get("queue_item_id") == OPEN_QUEUE_ITEM_ID:
            records[index] = _approved_open_record(int(record.get("sequence", index + 1)))
            open_record = records[index]
            replaced_existing_record = True
            break
    else:
        open_record = _approved_open_record(len(records) + 1)
        records.append(open_record)
    payload["run_records"] = records
    payload["run_count"] = len(records)
    payload["selected_queue_item_id"] = OPEN_QUEUE_ITEM_ID
    payload["selected_task_id"] = OPEN_TASK_ID
    payload["scheduler_decision"] = {
        "policy_id": "latest-approved-append-only-item-v0.2",
        "decision_status": "selected_approved_candidate",
        "selected_queue_item_id": OPEN_QUEUE_ITEM_ID,
        "selected_record_id": open_record["record_id"],
        "reason": "Use the first approved open queue item as the resume cursor target.",
    }
    append_only = payload.get("append_only", {})
    if isinstance(append_only, dict):
        source_order = [
            str(item)
            for item in append_only.get("source_queue_order", [])
            if isinstance(item, str)
        ]
        if not replaced_existing_record:
            source_order.append(OPEN_QUEUE_ITEM_ID)
        append_only["source_queue_order"] = source_order
        append_only["record_sequence_preserves_queue_order"] = True
    aggregate = payload.get("aggregate", {})
    if isinstance(aggregate, dict):
        aggregate["record_count"] = len(records)
        aggregate["source_queue_task_count"] = len(records)
        aggregate["executed_limited"] = len(records) - 1
        aggregate["converged"] = len(records) - 1
        aggregate["child_review_exports_valid"] = True
        aggregate["controller_truth_modified"] = False
        aggregate["ui_layout_modified"] = False
        aggregate["open_findings"] = [OPEN_SOURCE_FINDING_CODE]
        aggregate["ledger_append_only"] = True
    deterministic_gates = payload.get("deterministic_gates", {})
    if isinstance(deterministic_gates, dict):
        for key in deterministic_gates:
            deterministic_gates[key] = "pass"
    artifact_paths = payload.get("artifact_paths", {})
    if isinstance(artifact_paths, dict):
        artifact_paths["ledger"] = str(ledger_path)
    payload["status"] = "pass"
    return payload


def _record_is_approved_open(record: dict[str, Any]) -> bool:
    return (
        record.get("approved_task_shell", {}).get("approval_status") == "approved"
        and not _record_is_converged(record)
    )


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def run_multi_agent_queue_cursor_state(
    *,
    artifact_dir: Path = DEFAULT_CURSOR_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
    resume_mode: str = "idle",
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    input_packet_path = input_packet_path.resolve()
    ledger = _run_source_ledger(
        ledger_artifact_dir=artifact_dir / "source-multi-agent-queue-run-ledger",
        input_packet_path=input_packet_path,
    )
    ledger_path = Path(str(ledger.get("artifact_paths", {}).get("ledger", "")))
    ledger_check = _verify_source_ledger(ledger_path)
    if resume_mode == "ready-to-resume":
        ledger_path = (
            artifact_dir
            / "source-multi-agent-queue-run-ledger-ready-to-resume"
            / LEDGER_NAME
        )
        ledger = _ledger_with_approved_open_record(ledger, ledger_path=ledger_path)
        _write_json(ledger_path, ledger)
    records = [
        record
        for record in ledger.get("run_records", [])
        if isinstance(record, dict)
    ]
    completed_records = [
        _cursor_record(record, "converged")
        for record in records
        if _record_is_converged(record)
    ]
    open_records = [
        _cursor_record(record, "approved_open")
        for record in records
        if _record_is_approved_open(record)
    ]
    blocked_records = [
        _cursor_record(record, "blocked")
        for record in records
        if not _record_is_converged(record) and not _record_is_approved_open(record)
    ]
    selected_next = open_records[0] if open_records else {}
    last_completed = completed_records[-1] if completed_records else {}
    state_status = "ready_to_resume" if selected_next else "idle_no_open_approved_items"
    next_action = "resume_next_open_record" if selected_next else "wait_for_append_only_queue_growth"
    boundary_valid = ledger.get("aggregate", {}).get("controller_truth_modified") is False and ledger.get(
        "aggregate", {}
    ).get("ui_layout_modified") is False
    source_ledger_valid = ledger_check.get("returncode") == 0 and ledger_check.get("status") == "pass"
    cursor_monotonic = len(completed_records) + len(open_records) + len(blocked_records) == len(records)
    completed_valid = all(record.get("status") == "converged" for record in completed_records)
    resume_selection_valid = (
        (not selected_next and state_status == "idle_no_open_approved_items")
        or (bool(selected_next) and state_status == "ready_to_resume")
    )

    deterministic_gates = {
        "source_ledger_checker": _gate_status(source_ledger_valid),
        "cursor_monotonicity": _gate_status(cursor_monotonic),
        "completed_records": _gate_status(completed_valid),
        "resume_selection": _gate_status(resume_selection_valid),
        "boundary": _gate_status(boundary_valid),
        "local_gate": "fail",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in deterministic_gates.items() if key != "local_gate")
        else "fail"
    )
    deterministic_gates["local_gate"] = status

    cursor_path = artifact_dir / CURSOR_NAME
    payload = {
        "$schema": CURSOR_SCHEMA_ID,
        "kind": CURSOR_KIND,
        "status": status,
        "gate_id": CURSOR_GATE_ID,
        "cursor_id": CURSOR_ID,
        "source_ledger_id": SOURCE_LEDGER_ID,
        "source_ledger_gate_id": SOURCE_LEDGER_GATE_ID,
        "state_status": state_status,
        "resume_policy": {
            "policy_id": RESUME_POLICY_ID,
            "next_action": next_action,
            "reason": IDLE_REASON if not selected_next else READY_REASON,
        },
        "cursor_position": {
            "last_completed_record_id": str(last_completed.get("record_id", "")),
            "last_completed_queue_item_id": str(last_completed.get("queue_item_id", "")),
            "next_record_id": str(selected_next.get("record_id", "")),
            "next_queue_item_id": str(selected_next.get("queue_item_id", "")),
        },
        "selected_next_record": {
            "record_id": str(selected_next.get("record_id", "")),
            "queue_item_id": str(selected_next.get("queue_item_id", "")),
            "task_id": str(selected_next.get("task_id", "")),
            "status": "ready_to_resume" if selected_next else "none",
        },
        "completed_records": completed_records,
        "open_records": open_records,
        "deterministic_gates": deterministic_gates,
        "aggregate": {
            "source_ledger_record_count": len(records),
            "completed_count": len(completed_records),
            "open_approved_count": len(open_records),
            "blocked_count": len(blocked_records),
            "ready_for_resume": bool(selected_next),
            "idle": not bool(selected_next),
            "controller_truth_modified": not boundary_valid,
            "ui_layout_modified": ledger.get("aggregate", {}).get("ui_layout_modified") is not False,
        },
        "artifact_paths": {
            "cursor_state": str(cursor_path),
            "source_ledger": str(ledger_path),
        },
    }
    _write_json(cursor_path, payload)
    return payload


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_queue_cursor_state(
        artifact_dir=args.artifact_dir,
        input_packet_path=args.input_packet,
        resume_mode=args.resume_mode,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"cursor_id: {payload['cursor_id']}")
        print(f"status: {payload['status']}")
        print(f"state_status: {payload['state_status']}")
        print(f"cursor_state: {payload['artifact_paths']['cursor_state']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
