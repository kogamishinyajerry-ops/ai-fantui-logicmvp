#!/usr/bin/env python3
"""Generate an auditable run ledger from the approved candidate task queue."""
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
DEFAULT_LEDGER_ARTIFACT_DIR = Path("/tmp/ai-fantui-multi-agent-queue-run-ledger-v0-2")
LEDGER_SCHEMA_ID = (
    "https://well-harness.local/json_schema/multi_agent_queue_run_ledger_v0_2.schema.json"
)
LEDGER_KIND = "ai-fantui-multi-agent-queue-run-ledger"
LEDGER_ID = "multi-agent-queue-run-ledger-v0.2"
LEDGER_GATE_ID = "multi-agent-queue-run-ledger"
LEDGER_NAME = "multi_agent_queue_run_ledger_v0_2.json"
SOURCE_QUEUE_ID = "approved-candidate-task-queue-v0.9"
SOURCE_QUEUE_GATE_ID = "approved-candidate-task-queue-v0-9"
SELECTED_QUEUE_ITEM_ID = "queue-safety-output-command-conflict-repair"
SCHEDULER_POLICY_ID = "latest-approved-append-only-item-v0.2"
SCHEDULER_REASON = (
    "Use the newest append-only approved queue item after v0.9 checker passes."
)
EXPECTED_QUEUE_ORDER = [
    "queue-safety-priority-repair",
    "queue-evidence-simulation-result-repair",
    "queue-evidence-test-result-missing-repair",
    "queue-requirement-ambiguity-repair",
    "queue-safety-undefined-signal-repair",
    "queue-evidence-boundary-review-repair",
    "queue-evidence-unknown-requirement-repair",
    "queue-evidence-ir-trace-unknown-requirement-repair",
    "queue-safety-transition-endpoint-repair",
    "queue-safety-unreachable-state-repair",
    "queue-safety-output-command-conflict-repair",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the M10 queue scheduler and write a stable run ledger.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_LEDGER_ARTIFACT_DIR,
        help="Directory where ledger artifacts will be written.",
    )
    parser.add_argument(
        "--input-packet",
        type=Path,
        default=DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
        help="Candidate agent_output_contract_v0_1 packet to seed the queue.",
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


def _run_source_queue(
    *,
    queue_artifact_dir: Path,
    input_packet_path: Path,
) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_approved_candidate_task_queue_v0_9.py",
            "--format",
            "json",
            "--artifact-dir",
            str(queue_artifact_dir),
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
        raise RuntimeError(f"source queue did not emit JSON: {result.stderr}") from exc
    if result.returncode != 0 or payload.get("status") != "pass":
        raise RuntimeError(f"source queue did not pass: {payload.get('status')}")
    return payload


def _verify_source_queue(queue_summary_path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/verify_approved_candidate_task_queue_v0_9_artifact.py",
            "--summary",
            str(queue_summary_path),
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


def _review_status(item: dict[str, Any]) -> dict[str, Any]:
    path_value = item.get("artifact_paths", {}).get("candidate_review_packet_export")
    if not isinstance(path_value, str) or not path_value:
        return {
            "path": "",
            "reviewer_status": "",
            "finding_chain_statuses": [],
        }
    try:
        export = _load_json(Path(path_value))
    except (OSError, json.JSONDecodeError):
        return {
            "path": path_value,
            "reviewer_status": "",
            "finding_chain_statuses": [],
        }
    review_packet = export.get("review_packet", {})
    chains = review_packet.get("finding_chains", [])
    statuses = [
        str(chain.get("status", ""))
        for chain in chains
        if isinstance(chain, dict)
    ]
    return {
        "path": path_value,
        "reviewer_status": str(review_packet.get("reviewer", {}).get("status", "")),
        "finding_chain_statuses": statuses,
    }


def _run_record(item: dict[str, Any], index: int) -> dict[str, Any]:
    queue_contract = item.get("queue_contract", {})
    selected_task = item.get("selected_task", {})
    preflight = item.get("preflight", {})
    execution = item.get("execution", {})
    return {
        "record_id": f"RUN-QUEUE-{index:03d}",
        "sequence": index,
        "queue_item_id": str(item.get("queue_item_id", "")),
        "slice_id": str(item.get("slice_id", "")),
        "source_finding_code": str(queue_contract.get("source_finding_code", "")),
        "task": {
            "task_id": str(selected_task.get("task_id", "")),
            "target_agent": str(selected_task.get("target_agent", "")),
            "task_type": str(selected_task.get("task_type", "")),
        },
        "preflight": {
            "command": str(preflight.get("command", "")),
            "gate_id": str(preflight.get("gate_id", "")),
            "returncode": int(preflight.get("returncode", -1)),
            "status": str(preflight.get("status", "")),
        },
        "approved_task_shell": dict(item.get("approved_task_shell", {})),
        "repair": {
            "status": str(execution.get("status", "")),
            "reviewer_status": str(execution.get("reviewer_status", "")),
            "finding_chain_statuses": list(execution.get("finding_chain_statuses", [])),
        },
        "review_export": _review_status(item),
        "boundary": dict(item.get("boundary", {})),
    }


def _build_run_records(source_queue: dict[str, Any]) -> list[dict[str, Any]]:
    items = source_queue.get("items", [])
    return [
        _run_record(item, index)
        for index, item in enumerate(items, start=1)
        if isinstance(item, dict)
    ]


def _selected_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    for record in records:
        if record.get("queue_item_id") == SELECTED_QUEUE_ITEM_ID:
            return record
    return {}


def _gate_status(value: bool) -> str:
    return "pass" if value else "fail"


def run_multi_agent_queue_run_ledger(
    *,
    artifact_dir: Path = DEFAULT_LEDGER_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    artifact_dir = artifact_dir.resolve()
    input_packet_path = input_packet_path.resolve()
    source_queue = _run_source_queue(
        queue_artifact_dir=artifact_dir / "source-approved-candidate-task-queue-v0-9",
        input_packet_path=input_packet_path,
    )
    source_queue_summary_path = Path(
        str(source_queue.get("artifact_paths", {}).get("queue_summary", ""))
    )
    source_queue_check = _verify_source_queue(source_queue_summary_path)
    records = _build_run_records(source_queue)
    selected = _selected_record(records)
    queue_order = [record["queue_item_id"] for record in records]

    source_queue_valid = (
        source_queue_check.get("returncode") == 0
        and source_queue_check.get("status") == "pass"
    )
    scheduler_valid = (
        bool(selected)
        and selected.get("approved_task_shell", {}).get("approval_status") == "approved"
        and selected.get("approved_task_shell", {}).get("status") == "executed_limited"
    )
    approved_shell_valid = all(
        record.get("approved_task_shell", {}).get("status") == "executed_limited"
        and record.get("approved_task_shell", {}).get("approval_status") == "approved"
        for record in records
    )
    child_exports_valid = all(
        record.get("review_export", {}).get("reviewer_status") == "converged"
        and record.get("review_export", {}).get("finding_chain_statuses") == ["converged"]
        for record in records
    )
    boundary_valid = all(
        record.get("boundary", {}).get("controller_truth_modified") is False
        and record.get("boundary", {}).get("ui_layout_modified") is False
        for record in records
    )
    append_only_valid = queue_order == EXPECTED_QUEUE_ORDER
    converged = sum(
        1
        for record in records
        if record.get("repair", {}).get("reviewer_status") == "converged"
        and record.get("repair", {}).get("finding_chain_statuses") == ["converged"]
    )
    executed_limited = sum(
        1
        for record in records
        if record.get("approved_task_shell", {}).get("status") == "executed_limited"
    )

    deterministic_gates = {
        "source_queue_v0_9_checker": _gate_status(source_queue_valid),
        "scheduler_selection": _gate_status(scheduler_valid),
        "approved_task_shell_records": _gate_status(approved_shell_valid),
        "child_review_exports": _gate_status(child_exports_valid),
        "boundary": _gate_status(boundary_valid),
        "local_gate": "fail",
    }
    status = (
        "pass"
        if all(value == "pass" for key, value in deterministic_gates.items() if key != "local_gate")
        and append_only_valid
        else "fail"
    )
    deterministic_gates["local_gate"] = status

    ledger_path = artifact_dir / LEDGER_NAME
    payload = {
        "$schema": LEDGER_SCHEMA_ID,
        "kind": LEDGER_KIND,
        "status": status,
        "gate_id": LEDGER_GATE_ID,
        "ledger_id": LEDGER_ID,
        "source_queue_id": SOURCE_QUEUE_ID,
        "source_queue_gate_id": SOURCE_QUEUE_GATE_ID,
        "selected_queue_item_id": SELECTED_QUEUE_ITEM_ID,
        "selected_task_id": str(selected.get("task", {}).get("task_id", "")),
        "run_count": len(records),
        "scheduler_decision": {
            "policy_id": SCHEDULER_POLICY_ID,
            "decision_status": (
                "selected_approved_candidate" if scheduler_valid else "blocked"
            ),
            "selected_queue_item_id": SELECTED_QUEUE_ITEM_ID,
            "selected_record_id": str(selected.get("record_id", "")),
            "reason": SCHEDULER_REASON,
        },
        "append_only": {
            "source_queue_id": SOURCE_QUEUE_ID,
            "source_queue_order": queue_order,
            "record_sequence_preserves_queue_order": append_only_valid,
            "append_mode": "ledger_records_append_only_v0.2",
        },
        "run_records": records,
        "deterministic_gates": deterministic_gates,
        "aggregate": {
            "record_count": len(records),
            "source_queue_task_count": int(source_queue.get("task_count", 0)),
            "executed_limited": executed_limited,
            "converged": converged,
            "child_review_exports_valid": child_exports_valid,
            "controller_truth_modified": not boundary_valid,
            "ui_layout_modified": any(
                record.get("boundary", {}).get("ui_layout_modified") is not False
                for record in records
            ),
            "open_findings": list(source_queue.get("aggregate", {}).get("open_findings", [])),
            "ledger_append_only": append_only_valid,
        },
        "artifact_paths": {
            "ledger": str(ledger_path),
            "source_queue_summary": str(source_queue_summary_path),
        },
    }
    _write_json(ledger_path, payload)
    return payload


def main() -> int:
    args = _parse_args()
    payload = run_multi_agent_queue_run_ledger(
        artifact_dir=args.artifact_dir,
        input_packet_path=args.input_packet,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"ledger_id: {payload['ledger_id']}")
        print(f"status: {payload['status']}")
        print(f"selected_queue_item_id: {payload['selected_queue_item_id']}")
        print(f"run_count: {payload['run_count']}")
        print(f"ledger: {payload['artifact_paths']['ledger']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
