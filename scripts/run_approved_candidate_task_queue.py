#!/usr/bin/env python3
"""Run a small approved candidate task queue behind the readiness gate."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from well_harness.agent_development_slice import (
    DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
    run_evidence_candidate_repair_slice,
    run_first_candidate_repair_slice,
    run_missing_test_result_candidate_repair_slice,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE_ARTIFACT_DIR = Path("/tmp/ai-fantui-approved-candidate-task-queue")
QUEUE_ID = "approved-candidate-task-queue-v0.1"
QUEUE_GATE_ID = "approved-candidate-task-queue"
QUEUE_SUMMARY_KIND = "ai-fantui-approved-candidate-task-queue-summary"
QUEUE_SUMMARY_SCHEMA_ID = (
    "https://well-harness.local/json_schema/approved_candidate_task_queue_summary_v0_1.schema.json"
)
READINESS_COMMAND = "make multi-agent-construction-readiness"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run approved candidate repair tasks after per-task readiness preflight.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=DEFAULT_QUEUE_ARTIFACT_DIR,
        help="Directory where queue artifacts will be written.",
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


def _run_readiness_preflight(readiness_dir: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "make",
            "multi-agent-construction-readiness",
            f"MULTI_AGENT_CONSTRUCTION_READINESS_ARTIFACT_DIR={readiness_dir}",
        ],
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
    status = (
        "pass"
        if result.returncode == 0
        and payload.get("status") == "pass"
        and payload.get("ready_for_long_running_development") is True
        else "fail"
    )
    return {
        "command": READINESS_COMMAND,
        "status": status,
        "returncode": result.returncode,
        "readiness_id": payload.get("readiness_id", ""),
        "ready_for_long_running_development": payload.get(
            "ready_for_long_running_development",
            False,
        ),
        "artifact_paths": payload.get("artifact_paths", {}),
        "stderr": result.stderr,
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _approved_shell_status(slice_payload: dict[str, Any]) -> dict[str, Any]:
    try:
        artifact_paths = slice_payload.get("artifact_paths", {})
        if not isinstance(artifact_paths, dict):
            raise ValueError("artifact_paths is not an object")
        loop_path_value = artifact_paths.get("repair_loop_result")
        if not loop_path_value:
            raise ValueError("missing repair_loop_result artifact path")
        loop_result = _load_json(Path(str(loop_path_value)))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {
            "status": "invalid_payload",
            "approval_status": "",
            "selected_task_id": "",
        }
    evidence = loop_result.get("before", {}).get("execution_evidence_package", {})
    return {
        "status": str(evidence.get("executor", {}).get("status", "")),
        "approval_status": str(evidence.get("approval", {}).get("status", "")),
        "selected_task_id": str(evidence.get("executor", {}).get("selected_task_id", "")),
    }


def _boundary(slice_payload: dict[str, Any]) -> dict[str, bool | str]:
    candidate_delta = slice_payload.get("candidate_delta", {})
    return {
        "truth_effect": "none",
        "controller_truth_modified": candidate_delta.get("controller_truth_modified") is not False,
        "ui_layout_modified": candidate_delta.get("ui_layout_modified") is not False,
    }


def _queue_items() -> list[dict[str, Any]]:
    return [
        {
            "queue_item_id": "queue-safety-priority-repair",
            "slice_id": "first-approved-candidate-repair-slice",
            "runner": run_first_candidate_repair_slice,
        },
        {
            "queue_item_id": "queue-evidence-simulation-result-repair",
            "slice_id": "evidence-approved-candidate-repair-slice",
            "runner": run_evidence_candidate_repair_slice,
        },
        {
            "queue_item_id": "queue-evidence-test-result-missing-repair",
            "slice_id": "missing-test-result-approved-candidate-repair-slice",
            "runner": run_missing_test_result_candidate_repair_slice,
        },
    ]


def _run_queue_item(
    item: dict[str, Any],
    *,
    artifact_dir: Path,
    input_packet_path: Path,
) -> dict[str, Any]:
    queue_item_id = str(item["queue_item_id"])
    preflight = _run_readiness_preflight(artifact_dir / queue_item_id / "readiness")
    if preflight["status"] != "pass":
        return {
            "queue_item_id": queue_item_id,
            "slice_id": str(item["slice_id"]),
            "status": "blocked_preflight",
            "preflight": preflight,
            "execution": {
                "status": "not_run",
                "reason": "readiness preflight did not pass",
            },
            "approved_task_shell": {
                "status": "not_run",
                "approval_status": "not_run",
                "selected_task_id": "",
            },
            "selected_task": {},
            "boundary": {
                "truth_effect": "none",
                "controller_truth_modified": False,
                "ui_layout_modified": False,
            },
            "artifact_paths": {},
        }

    runner: Callable[..., dict[str, Any]] = item["runner"]
    try:
        slice_payload = runner(
            artifact_dir=artifact_dir / queue_item_id / "slice",
            input_packet_path=input_packet_path,
        )
    except Exception:
        slice_payload = {
            "status": "fail",
            "reviewer_status": "",
            "finding_chain_statuses": [],
            "selected_task": {},
            "candidate_delta": {
                "controller_truth_modified": False,
                "ui_layout_modified": False,
            },
            "artifact_paths": {},
        }
    shell_status = _approved_shell_status(slice_payload)
    boundary = _boundary(slice_payload)
    execution_status = (
        "pass"
        if slice_payload.get("status") == "pass"
        and shell_status["status"] == "executed_limited"
        and boundary["controller_truth_modified"] is False
        and boundary["ui_layout_modified"] is False
        else "fail"
    )
    return {
        "queue_item_id": queue_item_id,
        "slice_id": str(item["slice_id"]),
        "status": execution_status,
        "preflight": preflight,
        "execution": {
            "status": execution_status,
            "slice_status": slice_payload.get("status"),
            "reviewer_status": slice_payload.get("reviewer_status"),
            "finding_chain_statuses": slice_payload.get("finding_chain_statuses", []),
            **(
                {"reason": "invalid slice payload"}
                if shell_status["status"] == "invalid_payload"
                else {}
            ),
        },
        "approved_task_shell": shell_status,
        "selected_task": slice_payload.get("selected_task", {}),
        "boundary": boundary,
        "artifact_paths": slice_payload.get("artifact_paths", {}),
    }


def run_approved_candidate_task_queue(
    *,
    artifact_dir: Path = DEFAULT_QUEUE_ARTIFACT_DIR,
    input_packet_path: Path = DEFAULT_AGENT_OUTPUT_FIXTURE_PATH,
) -> dict[str, Any]:
    items = [
        _run_queue_item(
            item,
            artifact_dir=artifact_dir,
            input_packet_path=input_packet_path,
        )
        for item in _queue_items()
    ]
    status = "pass" if all(item["status"] == "pass" for item in items) else "fail"
    preflight_passed = sum(1 for item in items if item["preflight"].get("status") == "pass")
    executed_limited = sum(
        1
        for item in items
        if item["approved_task_shell"].get("status") == "executed_limited"
    )
    converged = sum(
        1
        for item in items
        if item["execution"].get("reviewer_status") == "converged"
        and item["execution"].get("finding_chain_statuses") == ["converged"]
    )
    open_findings: list[str] = []
    controller_truth_modified = any(
        item["boundary"].get("controller_truth_modified") is not False
        for item in items
    )
    ui_layout_modified = any(
        item["boundary"].get("ui_layout_modified") is not False
        for item in items
    )
    queue_summary_path = artifact_dir / "approved_candidate_task_queue_summary.json"
    payload = {
        "$schema": QUEUE_SUMMARY_SCHEMA_ID,
        "kind": QUEUE_SUMMARY_KIND,
        "status": status,
        "gate_id": QUEUE_GATE_ID,
        "queue_id": QUEUE_ID,
        "task_count": len(items),
        "ready_for_long_running_development": status == "pass",
        "queue_order": [item["queue_item_id"] for item in items],
        "items": items,
        "deterministic_gates": {
            "preflight_readiness": "pass" if preflight_passed == len(items) else "fail",
            "approved_task_shell": "pass" if executed_limited == len(items) else "fail",
            "child_review_exports": "pass" if converged == len(items) else "fail",
            "local_gate": status,
        },
        "aggregate": {
            "task_count": len(items),
            "passed": sum(1 for item in items if item["status"] == "pass"),
            "preflight_passed": preflight_passed,
            "executed_limited": executed_limited,
            "converged": converged,
            "open_findings": open_findings,
            "controller_truth_modified": controller_truth_modified,
            "ui_layout_modified": ui_layout_modified,
        },
        "artifact_paths": {
            "queue_summary": str(queue_summary_path),
        },
    }
    queue_summary_path.parent.mkdir(parents=True, exist_ok=True)
    queue_summary_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return payload


def main() -> int:
    args = _parse_args()
    payload = run_approved_candidate_task_queue(
        artifact_dir=args.artifact_dir,
        input_packet_path=args.input_packet,
    )
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"queue_id: {payload['queue_id']}")
        print(f"status: {payload['status']}")
        print(f"task_count: {payload['task_count']}")
        print(f"ready_for_long_running_development: {payload['ready_for_long_running_development']}")
        print(f"summary: {payload['artifact_paths']['queue_summary']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
